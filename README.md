# Swedish–English Evidence-Aware RAG Benchmark

A small research project testing whether compact AI models can answer from retrieved documents only when the evidence is sufficient, and whether this changes between Swedish and English.

## The question

When a model receives useful, incomplete, missing, or conflicting/outdated documents, does it answer, qualify its answer, or abstain? Do local models behave differently on matched Swedish and English examples?

## First version

- Start with a small, controlled pilot of fictional facts so answers are known and models cannot rely on memorized real-world facts.
- Give the model a fixed set of retrieved passages. This isolates evidence judgment from retrieval quality.
- Compare five conditions: supported, partial, irrelevant documents, no documents, and conflicting/outdated documents.
- Create matched Swedish and English examples and manually check that the facts and difficulty match. Swedish wording needs review by a fluent speaker before results are treated as research evidence.
- Test a few locally runnable models with the same prompts and settings.
- Compare supported-answer accuracy, appropriate abstention, unsupported-answer rate, copying of contradicted claims, and over-abstention.

## Important benchmark rule

A model cannot infer that a lone, plausible statement is false from that statement alone. “Misleading evidence” in this benchmark therefore means evidence that contains a detectable warning, such as a conflict with a clearly authoritative source or a superseded document whose date/version is shown. We may separately measure whether a model repeats an unsupported claim, but will not label an unknowable fact as a model-detectable error.

## Repository map

- `docs/research_protocol.md` — research question, benchmark design, scoring, and milestones.
- `data/schema.json` — required fields for each benchmark case.
- `data/pilot.jsonl` — 20 draft cases: two scenarios × two languages × five evidence conditions.
- `src/run_ollama.py` — runs the pilot using a local Ollama model.
- `src/score.py` — summarizes saved runs as CSV, including a heuristic answer/decision conflict rate. Review flagged outputs manually; the phrase checks are not a substitute for human evaluation.
- `results/` — generated results; do not commit private user data or model files.

## Run the pilot on Windows

1. Install Python 3.10+ and [Ollama](https://ollama.com/download).
2. In PowerShell, download a small starter model and check its exact name:

   ```powershell
   ollama pull qwen3:1.7b
   ollama list
   ```

3. From this project folder, run both prompt strategies:

   ```powershell
   py -3 src/run_ollama.py --model qwen3:1.7b --strategy baseline --output results/qwen3-1.7b-baseline.jsonl
   py -3 src/run_ollama.py --model qwen3:1.7b --strategy evidence_check --output results/qwen3-1.7b-evidence-check.jsonl
   py -3 src/score.py --results results/qwen3-1.7b-baseline.jsonl --output results/qwen3-1.7b-baseline.csv
   py -3 src/score.py --results results/qwen3-1.7b-evidence-check.jsonl --output results/qwen3-1.7b-evidence-check.csv
   ```

The runner calls Ollama at `http://localhost:11434`; it does not send benchmark prompts to a hosted model API. Results from this 20-case draft pilot only check that the workflow runs; they are not research findings.

## Current status

Project scope, initial protocol, 20-case pilot, local runner, and scorer are in place. Swedish wording has not been reviewed by a fluent speaker. The next step is to review the translations and expand the scenarios before drawing conclusions.

## Research context

Related work already studies evidence sufficiency generally, misleading-context abstention with small models in English, multilingual hallucination detection, and Swedish local RAG including refusal behavior. This project does not claim the general idea is new; its proposed focus is a controlled, matched Swedish–English comparison of small local models across evidence conditions. Treat that as a candidate contribution until a systematic literature review confirms it. See the protocol for initial related-work leads and limits.

