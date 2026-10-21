"""Score an Ollama JSONL run against the benchmark answer key."""

from __future__ import annotations

import argparse
import csv
import json
import re
from collections import defaultdict
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


def read_jsonl(path: Path) -> list[dict]:
    records = []
    with path.open("r", encoding="utf-8") as stream:
        for line_number, line in enumerate(stream, start=1):
            if line.strip():
                try:
                    records.append(json.loads(line))
                except json.JSONDecodeError as exc:
                    raise ValueError(f"Invalid JSON in {path}, line {line_number}: {exc}") from exc
    return records


def normalize(value: str | None) -> str:
    return re.sub(r"[^\w]", "", (value or "").casefold(), flags=re.UNICODE)


def response_is_correct(parsed: dict | None, case: dict) -> bool:
    if not parsed or case.get("answer_key") is None:
        return False
    answer = normalize(parsed.get("answer"))
    choices = [case["answer_key"], *case.get("acceptable_answers", [])]
    return any(normalize(choice) and normalize(choice) in answer for choice in choices)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dataset", type=Path, default=PROJECT_ROOT / "data" / "pilot.jsonl")
    parser.add_argument("--results", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True, help="CSV summary path")
    args = parser.parse_args()

    dataset_path = args.dataset if args.dataset.is_absolute() else PROJECT_ROOT / args.dataset
    results_path = args.results if args.results.is_absolute() else PROJECT_ROOT / args.results
    output_path = args.output if args.output.is_absolute() else PROJECT_ROOT / args.output
    cases = {
        (case["scenario_id"], case["language"], case["condition"]): case
        for case in read_jsonl(dataset_path)
    }
    groups: dict[tuple, list[dict]] = defaultdict(list)
    for record in read_jsonl(results_path):
        key = (record.get("scenario_id"), record.get("language"), record.get("condition"))
        case = cases.get(key)
        if case is None:
            raise ValueError(f"Run contains a case not found in dataset: {key}")
        parsed = record.get("parsed") if isinstance(record.get("parsed"), dict) else None
        decision = parsed.get("decision", "invalid") if parsed else "invalid"
        answer_correct = response_is_correct(parsed, case)
        response_text = str((parsed or {}).get("answer", ""))
        claim = case.get("misleading_claim")
        claim_adopted = bool(claim and normalize(claim) in normalize(response_text))
        groups[(record.get("model"), record.get("strategy"), record.get("language"), record.get("condition"))].append(
            {
                "decision": decision,
                "expected_decision": case["expected_decision"],
                "answer_correct": answer_correct,
                "claim_adopted": claim_adopted,
                "elapsed_seconds": record.get("elapsed_seconds"),
                "parse_failure": parsed is None or not isinstance(parsed.get("decision"), str),
            }
        )

    columns = [
        "model", "strategy", "language", "condition", "n",
        "decision_match_rate", "correct_answer_rate", "abstain_rate", "parse_failure_rate",
        "unsupported_answer_rate", "misleading_claim_adoption_rate", "mean_seconds",
    ]
    rows = []
    for (model, strategy, language, condition), items in sorted(groups.items()):
        n = len(items)
        unsupported = condition in {"partial", "irrelevant", "no_context"}
        row = {
            "model": model,
            "strategy": strategy,
            "language": language,
            "condition": condition,
            "n": n,
            "decision_match_rate": round(sum(item["decision"] == item["expected_decision"] for item in items) / n, 4),
            "correct_answer_rate": round(sum(item["answer_correct"] for item in items) / n, 4),
            "abstain_rate": round(sum(item["decision"] == "abstain" for item in items) / n, 4),
            "parse_failure_rate": round(sum(item["parse_failure"] for item in items) / n, 4),
            "unsupported_answer_rate": round(sum(item["decision"] == "answer" for item in items) / n, 4) if unsupported else "",
            "misleading_claim_adoption_rate": round(sum(item["claim_adopted"] for item in items) / n, 4) if condition == "misleading_conflict" else "",
            "mean_seconds": round(sum(float(item["elapsed_seconds"] or 0) for item in items) / n, 3),
        }
        rows.append(row)

    output_path.parent.mkdir(parents=True, exist_ok=True)
    with output_path.open("w", encoding="utf-8-sig", newline="") as stream:
        writer = csv.DictWriter(stream, fieldnames=columns)
        writer.writeheader()
        writer.writerows(rows)
    print(f"Scored {sum(len(items) for items in groups.values())} run records into {output_path}")
    print("Pilot metrics are descriptive only; 2 scenarios are far too few for research conclusions.")


if __name__ == "__main__":
    main()

