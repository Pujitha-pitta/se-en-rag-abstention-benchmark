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
- `docs/swedish_language_review.md` — AI-assisted consistency review of the expanded Swedish draft; not human validation.
- `data/schema.json` — required fields for each benchmark case.
- `data/pilot.jsonl` — 20 pilot cases: two scenarios × two languages × five evidence conditions.
- `data/expanded_draft.jsonl` — 30 additional draft cases: three new scenarios × two languages × five evidence conditions. These remain draft cases. Prefer fluent human review; if unavailable, use documented independent language-model checks and back-translation, keep the Swedish marked unreviewed, and treat results as exploratory.
- `src/run_ollama.py` — runs the pilot using a local Ollama model and constrains response fields and decision labels with a JSON schema.
- `src/score.py` — summarizes saved runs as CSV. Its `answer_decision_rate` is the share of records in irrelevant/no-context conditions whose parsed decision is `answer`; it does not judge whether the answer text makes an unsupported factual claim. The answer/decision conflict rate is also heuristic. Review output content separately; phrase checks are not a substitute for human evaluation.
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

The runner calls Ollama at `http://localhost:11434`; it does not send benchmark prompts to a hosted model API. Results from the 20-case pilot only check that the workflow runs; they are not research findings. Before running `expanded_draft.jsonl`, check the translations, question-condition pairings, and gold labels. If no fluent Swedish reviewer is available, document independent model checks and back-translation and treat Swedish results as exploratory.

## Current status

Project scope, initial protocol, 20-case pilot, local runner, scorer, and a separate 30-case expansion draft are in place. Swedish wording in both datasets has not received fluent-human review. Check translations, matched questions, and expected labels; if no fluent reviewer is available, document model-assisted checks and keep results exploratory.

## AI-assisted output review

`results/manual_review_v2_completed.csv` contains an AI-assisted review of 24 selected outputs from scenarios C003–C005, covering the `partial` and `irrelevant` conditions for the baseline and evidence-check strategies. It records potential decision/content mismatches, unsupported inferences, metadata used as a factual answer, and outputs with no clear issue from the material reviewed.

This is not a human review, despite `manual_review` in the filename. Swedish-language wording and judgments were not independently checked by a fluent Swedish speaker. Treat the annotations as provisional; the pilot is small and its results are descriptive, not research conclusions.

## Expanded-draft pilot results

The following descriptive results come from Qwen3 1.7B baseline and evidence-check runs on `data/expanded_draft.jsonl`. Each strategy has 30 records: three examples per language and condition. Score summaries are in `results/qwen3-1.7b-expanded-baseline-v2-scores.csv` and `results/qwen3-1.7b-expanded-evidence-check-v2-scores.csv`.

Decision-match rate by condition (baseline / evidence-check):

| Condition | English | Swedish |
|---|---:|---:|
| Supported | 100% / 100% | 100% / 100% |
| Partial | 33% / 0% | 0% / 0% |
| Irrelevant | 33% / 67% | 67% / 0% |
| No context | 100% / 100% | 100% / 100% |
| Misleading conflict | 100% / 100% | 100% / 100% |

Evidence-check did not improve every condition. For irrelevant evidence, its abstention rate rose from 33% to 67% in English but fell from 67% to 0% in Swedish. Decision-match rates do not by themselves indicate answer correctness. The answer key now accepts the concise answer “14” for C004, because the question itself asks for a number of days; before this, the scorer marked that semantically correct response as wrong. With that correction, both strategies had 100% correct-answer rates on supported English examples and on misleading-conflict examples in both languages in this run. The partial-evidence decision match was low for both strategies.

The CSV `answer_decision_rate` counts the `answer` decision label for irrelevant/no-context cases; it is not a factual unsupported-claim rate. In the reviewed examples, some such records have a blank answer or text that says the information is absent, while other records make unsupported claims. The AI-assisted review file records these separately. The rates are based on only three examples per language and condition. Swedish text was not independently checked by a fluent speaker, and the scorer's answer/decision conflict metric is heuristic. Treat the comparison as exploratory; it does not establish that either strategy is better.

## Output-format compliance check

A local 30-record-per-strategy comparison on the same expanded draft found no decision labels outside the runner's allowed set (`answer`, `partial`, `abstain`) in either Qwen3 1.7B run. Gemma3 1B produced out-of-set decision labels in 11/30 baseline records and 14/30 evidence-check records. These runs used JSON mode without a constrained JSON schema. This is a response-format compliance count, not an accuracy score. The Gemma raw runs and score summaries remain local and are not included in this repository, so the count is reported as an exploratory observation from the local run. The small set, draft data, and lack of fluent-human Swedish review limit interpretation; it does not establish comparative model quality.

The runner now sends an explicit JSON schema to Ollama, constraining the response fields and the `decision` enum. New schema-constrained runs use a changed output-format setting, so rerun each model and strategy before comparing new results with one another; do not combine them as if they were generated under the earlier JSON-only setting. Ollama supports JSON schemas through its chat API's `format` field ([structured outputs documentation](https://docs.ollama.com/capabilities/structured-outputs)).

## Schema-constrained exploratory comparison

The table shows decision-match rates from 30-record runs per model and strategy on the draft dataset. There are only three examples per language and condition, so each record changes a rate by about 33 percentage points.

| Language | Condition | Qwen3 baseline | Qwen3 evidence-check | Gemma3 baseline | Gemma3 evidence-check |
|---|---|---:|---:|---:|---:|
| English | Supported | 100% | 100% | 67% | 67% |
| English | Partial | 33% | 0% | 0% | 0% |
| English | Irrelevant | 33% | 67% | 67% | 67% |
| English | No context | 100% | 100% | 100% | 100% |
| English | Misleading conflict | 100% | 100% | 33% | 33% |
| Swedish | Supported | 100% | 100% | 0% | 0% |
| Swedish | Partial | 0% | 0% | 0% | 0% |
| Swedish | Irrelevant | 67% | 0% | 67% | 67% |
| Swedish | No context | 100% | 100% | 100% | 100% |
| Swedish | Misleading conflict | 100% | 100% | 0% | 0% |

These are exploratory descriptive results, not evidence that one model or strategy is generally superior. The answer/decision conflict metric remains heuristic, and the Swedish text has not received fluent-human review. In a targeted AI-assisted inspection of the raw outputs, Qwen3 evidence-check labeled two Swedish irrelevant-evidence cases `answer` while leaving the answer blank and explaining that the requested information was absent; its third case inferred a signed budget form from unrelated eligibility information. Gemma3 labeled the three Swedish supported cases `abstain` even though its answer field contained the supported fact. These examples illustrate why a valid JSON schema does not guarantee that decision, answer, and rationale agree or that claims are supported. This review is provisional and is not a fluent-human Swedish review.

## Research context

Related work already studies evidence sufficiency generally, misleading-context abstention with small models in English, multilingual hallucination detection, and Swedish local RAG including refusal behavior. This project does not claim the general idea is new; its proposed focus is a controlled, matched Swedish–English comparison of small local models across evidence conditions. Treat that as a candidate contribution until a systematic literature review confirms it. See the protocol for initial related-work leads and limits.
