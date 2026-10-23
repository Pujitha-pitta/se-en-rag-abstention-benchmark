"""Run the benchmark against a model served by Ollama on this computer."""

from __future__ import annotations

import argparse
import json
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen


PROJECT_ROOT = Path(__file__).resolve().parents[1]
CONDITIONS = {"supported", "partial", "irrelevant", "no_context", "misleading_conflict"}
RESPONSE_SCHEMA = {
    "type": "object",
    "properties": {
        "decision": {"type": "string", "enum": ["answer", "partial", "abstain"]},
        "answer": {"type": "string"},
        "evidence_ids": {"type": "array", "items": {"type": "string"}},
        "reason": {"type": "string"},
    },
    "required": ["decision", "answer", "evidence_ids", "reason"],
    "additionalProperties": False,
}


def load_cases(path: Path) -> list[dict]:
    cases = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if not line.strip():
                continue
            try:
                case = json.loads(line)
            except json.JSONDecodeError as exc:
                raise ValueError(f"Invalid JSON on line {line_number}: {exc}") from exc
            required = {"scenario_id", "language", "condition", "question", "passages"}
            missing = required - case.keys()
            if missing:
                raise ValueError(f"Line {line_number} is missing fields: {', '.join(sorted(missing))}")
            if case["condition"] not in CONDITIONS:
                raise ValueError(f"Unknown condition on line {line_number}: {case['condition']}")
            cases.append(case)
    if not cases:
        raise ValueError(f"No cases found in {path}")
    return cases


def make_prompt(case: dict, strategy: str) -> tuple[str, str]:
    if case["language"] == "sv":
        system = (
            "Svara på svenska och använd bara frågan och dokumenten. Hitta inte på fakta. "
            "Returnera endast ett JSON-objekt med fälten decision, answer, evidence_ids och reason. "
            "decision måste vara answer, partial eller abstain; answer och reason måste vara text; "
            "evidence_ids måste vara en lista. answer innehåller bara svaret, aldrig en förklaring. "
            "Välj answer när dokument tydligt stöder hela svaret. Välj partial när relevanta dokument "
            "stöder en del men den efterfrågade detaljen saknas; skriv den kända delen i answer. "
            "Välj abstain när inget relevant dokument stöder svaret; answer måste då vara en tom sträng. "
            "Lägg förklaringen i reason. Datum i metadata är dokumentets versionsdatum, inte ett händelsedatum; använd dem inte som svar om datumet inte också står som en sakuppgift i dokumenttexten."
        )
        question_label, docs_label, empty_context = "Fråga", "Dokument", "Inga dokument har hämtats."
    else:
        system = (
            "Answer in English using only the question and supplied documents. Do not invent facts. "
            "Return only one JSON object with fields decision, answer, evidence_ids, and reason. "
            "decision must be answer, partial, or abstain; answer and reason must be strings; "
            "evidence_ids must be a list. The answer field contains only the answer, never an explanation. "
            "Choose answer when the documents clearly support the full answer. Choose partial when "
            "relevant documents support some information but the requested detail is missing; put the "
            "known part in answer. Choose abstain when no relevant document supports an answer; answer "
            "must then be an empty string. Put explanations in reason. Dates in metadata are document version dates, not event dates; do not use them as answers unless the date also appears as a factual statement in the document text."
        )
        question_label, docs_label, empty_context = "Question", "Documents", "No documents were retrieved."

    if strategy == "evidence_check":
        if case["language"] == "sv":
            system += (
                " Kontrollera även motstridiga dokument. superseded=true betyder att källan är ersatt "
                "och ska inte användas när en aktuell källa finns. Om en aktuell, ej ersatt källa tydligt "
                "stöder svaret, välj answer även om en ersatt källa säger något annat. Välj abstain endast "
                "om två eller fler ej ersatta källor fortfarande motsäger varandra."
            )
        else:
            system += (
                " Also check conflicting documents. superseded=true means that source is outdated and "
                "must not be used when a current source is available. If a current, non-superseded source "
                "clearly supports the answer, choose answer even when a superseded source says something "
                "different. Choose abstain only when two or more non-superseded sources still conflict."
            )

    rendered_passages = []
    for passage in case["passages"]:
        version = passage.get("version_date") or "unknown"
        superseded = passage.get("superseded", False)
        rendered_passages.append(
            f"[{passage['passage_id']}] source={passage.get('source_label', 'unknown')}; "
            f"document_version_date={version}; superseded={str(superseded).lower()}\n{passage['text']}"
        )
    docs = "\n\n".join(rendered_passages) if rendered_passages else empty_context
    user = f"{question_label}: {case['question']}\n\n{docs_label}:\n{docs}"
    return system, user


def query_ollama(base_url: str, model: str, system: str, user: str, timeout: int) -> tuple[str, dict]:
    payload = {
        "model": model,
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "format": RESPONSE_SCHEMA,
        "stream": False,
        "think": False,
        "options": {"temperature": 0},
    }
    request = Request(
        f"{base_url.rstrip('/')}/api/chat",
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            body = json.loads(response.read().decode("utf-8"))
    except HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Ollama returned HTTP {exc.code}: {detail}") from exc
    except URLError as exc:
        raise RuntimeError(
            f"Could not reach Ollama at {base_url}. Start Ollama and check that it is listening locally."
        ) from exc
    except TimeoutError as exc:
        raise RuntimeError(f"Ollama did not respond within {timeout} seconds") from exc
    return body.get("message", {}).get("content", ""), body


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--model", required=True, help="Installed Ollama model name, for example a local model tag")
    parser.add_argument("--input", type=Path, default=PROJECT_ROOT / "data" / "pilot.jsonl")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--strategy", choices=("baseline", "evidence_check"), default="baseline")
    parser.add_argument("--url", default="http://localhost:11434", help="Ollama server URL")
    parser.add_argument("--timeout", type=int, default=240)
    parser.add_argument("--overwrite", action="store_true", help="Replace an existing output file")
    args = parser.parse_args()

    input_path = args.input if args.input.is_absolute() else PROJECT_ROOT / args.input
    output_path = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    if output_path.exists() and not args.overwrite:
        parser.error(f"Output already exists: {output_path}. Choose another path or pass --overwrite.")
    output_path.parent.mkdir(parents=True, exist_ok=True)
    cases = load_cases(input_path)

    with output_path.open("w", encoding="utf-8") as stream:
        for index, case in enumerate(cases, start=1):
            system, user = make_prompt(case, args.strategy)
            started = time.perf_counter()
            raw, metadata = query_ollama(args.url, args.model, system, user, args.timeout)
            elapsed = time.perf_counter() - started
            try:
                parsed = json.loads(raw)
                parse_error = None
            except json.JSONDecodeError as exc:
                parsed = None
                parse_error = str(exc)

            record = {
                "run_id": f"{args.model}:{args.strategy}:{case['scenario_id']}:{case['language']}:{case['condition']}",
                "scenario_id": case["scenario_id"],
                "language": case["language"],
                "condition": case["condition"],
                "model": args.model,
                "strategy": args.strategy,
                "timestamp_utc": datetime.now(timezone.utc).isoformat(),
                "elapsed_seconds": round(elapsed, 3),
                "response": raw,
                "parsed": parsed,
                "parse_error": parse_error,
                "ollama_total_duration_ns": metadata.get("total_duration"),
                "ollama_prompt_tokens": metadata.get("prompt_eval_count"),
                "ollama_output_tokens": metadata.get("eval_count"),
            }
            stream.write(json.dumps(record, ensure_ascii=False) + "\n")
            stream.flush()
            print(f"[{index}/{len(cases)}] {case['scenario_id']} {case['language']} {case['condition']} ({elapsed:.1f}s)")

    print(f"Saved raw run records to {output_path}")


if __name__ == "__main__":
    main()
