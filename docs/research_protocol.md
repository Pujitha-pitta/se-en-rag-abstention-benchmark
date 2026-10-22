# Research protocol (draft)

## Research question

How well do small locally runnable language models judge whether retrieved evidence is sufficient to answer, and how does performance compare between matched Swedish and English inputs?

## Why this needs careful framing

Related research already tests evidence sufficiency, abstention, and misleading context. The project should be presented as a focused language-and-deployment evaluation, not as the first RAG abstention benchmark. Initial related-work leads include:

- [Prompt-Based Abstention Fails Under Misleading Context (GRAB-RAG)](https://arxiv.org/abs/2608.22228) — recent controlled study of small frozen RAG models and multiple evidence conditions.
- [Bi'an: A Bilingual Benchmark and Model for Hallucination Detection in RAG](https://arxiv.org/abs/2502.19209) — bilingual RAG hallucination work.
- [SemEval-2025 HalluSearch](https://aclanthology.org/2025.semeval-1.189.pdf) — multilingual hallucination detection work that includes Swedish.
- [Evidence Sufficiency Benchmark for RAG](https://www.sciencedirect.com/org/science/article/pii/S1546221826007526) — recent work on graded evidence sufficiency and abstention.
- [Taming the BEAST: Assessing Open-Source LLM Capabilities in a Local RAG Assistant](https://www.uppsatser.se/uppsats/b2ab646885/) — a 2026 Uppsala thesis listing describes local open-source models evaluated on Swedish administrative text, including abstention/refusal behavior.

These are starting points, not a completed literature review. Before claiming a research gap, inspect the papers, thesis, datasets, and language/model coverage, and search for newer work. The project should not be sold as the first Swedish RAG or abstention evaluation. The candidate distinction is a paired Swedish–English controlled evidence-condition comparison for small local models, subject to confirmation.

## Scope of the first version

1. **Controlled pilot:** create fictional underlying scenarios. For each scenario, write matched Swedish and English versions and five evidence conditions: full support, partial support, irrelevant documents, no context, and conflicting/outdated evidence. The original two-scenario pilot has 20 inputs and is only a workflow check. A separate `expanded_draft.jsonl` adds three scenarios (30 matched language-condition cases); it remains unreviewed draft material. Prefer bilingual human review; if unavailable, use independent model-assisted checks and back-translation, retain the unreviewed flag, and report Swedish results as exploratory.
2. **Fixed retrieved passages:** pass the selected passages directly to the model. This makes the first experiment about judging evidence, not whether a search system retrieved the right documents.
3. **Local models:** choose two or three quantized models that fit the available computer. Record exact model/version, quantization, runtime, prompt, and decoding settings.
4. **Interventions:** compare a basic instruction with a short evidence-check instruction. Add a second model-based sufficiency check only if time allows.
5. **Review before scaling:** inspect pilot errors and language quality. Review every translation, question-condition pairing, evidence citation, and gold label in `expanded_draft.jsonl` before using it. Prefer a fluent human reviewer. If unavailable, use independent model-assisted checks plus back-translation, retain the unreviewed flag, and limit Swedish findings to exploratory results.

## Evidence conditions and expected behavior

Each scenario has one answer key and a matched Swedish and English question.

| Condition | Retrieved context | Expected behavior |
| --- | --- | --- |
| Supported | A current, relevant passage states the answer | Give the answer and cite the supporting passage ID |
| Partial / weak | Related evidence exists but does not establish the requested answer | State what is known and what is missing, or abstain |
| Irrelevant | Retrieved passages discuss the topic but do not contain the requested answer | Abstain; do not infer an answer from topic overlap |
| No context | No passages are supplied | Abstain; do not invent an answer |
| Misleading / conflict | A plausible claim conflicts with a visibly more authoritative or newer source, or is marked as superseded | Prefer the explicitly authoritative/current evidence, or explain the conflict and abstain |

**Do not use an unmarked false statement as the only evidence and then expect the model to know it is false.** Without a warning or independent evidence, that is not a fair evidence-grounded test. If included as a separate stress test, score it as unsupported-claim copying, not as failure to discover hidden truth.

## Data design and language quality

- Use fictional organizations, people, course names, dates, and policies to reduce contamination from model pretraining and avoid reproducing personal data.
- Treat fictional examples as a controlled pilot only. If time and language review allow, add a small separate set based on public Swedish/English source documents to check whether conclusions transfer beyond synthetic passages.
- Keep each English/Swedish pair fact-equivalent: same answer, entities, dates, source roles, and evidence condition.
- Do not translate mechanically and assume equivalence. A fluent Swedish reviewer is preferred to check naturalness, ambiguity, and matched evidence strength. If unavailable, use two independent model-assisted reviews and back-translation as a documented fallback; this is weaker than human review and limits conclusions.
- Keep a source/passage ID and an answer key for every example. The answer should be extractable from the passages, not outside knowledge.
- Label retrieval metadata dates explicitly as document version dates. Tell models not to treat those metadata dates as event facts unless the passage text itself states them.
- Store the exact prompt and model output for reproducibility. Do not include users' private exported chats in this benchmark.

## Scoring

Report results separately by language, model, condition, and prompt strategy:

- **Supported answer accuracy:** correct answers when evidence is sufficient.
- **Appropriate abstention:** abstentions for missing evidence, and cautious responses for weak/conflicting evidence.
- **Unsupported answer rate:** answer decisions on irrelevant or no-context cases, where no evidence supports an answer.
- **Full-answer label on partial evidence:** rate at which the model chooses `answer` rather than `partial` for incomplete but relevant evidence. This is reported separately and is not automatically counted as an unsupported factual answer.
- **Answer/decision conflict flag:** a heuristic English/Swedish phrase check for response-format inconsistencies. Manually review flagged outputs; this is not a semantic correctness metric.
- **Misleading-claim adoption:** rate at which the model repeats the contradicted/superseded claim instead of using the current source or noting conflict.
- **Over-abstention:** refusal rate on supported examples.
- **Swedish–English gap:** paired difference for each metric, with uncertainty intervals once the benchmark is large enough.
- **Practical cost:** latency, peak memory if measurable, model size, and hardware/software details.

Do not collapse all outcomes into one score without also showing the safety/utility trade-off. A model that refuses every question should not appear successful merely because it avoids unsupported answers.

## Suggested response format

Require machine-readable output with `decision` (`answer`, `partial`, or `abstain`), `answer`, `evidence_ids`, and `reason`. Parse failures should be counted and reported, not silently discarded. The model must use only supplied passages.

## Milestones

1. **Protocol and literature check:** verify related work and freeze the definitions before generating the full set.
2. **Pilot benchmark:** manually review the 20 pilot cases (two scenarios × two languages × five conditions), then review and revise the separate 30-case expansion draft before using it.
3. **Runner and scorer:** run identical cases and prompts against selected local models; save raw outputs.
4. **Baseline analysis:** compute the metrics above and inspect a sample of errors in both languages.
5. **Mitigation comparison:** test the evidence-check instruction and quantify both reduced bad answers and added refusals.
6. **Reproducible release:** publish code, benchmark data, model/run instructions, and a concise report. Only add a human study after checking ethics/consent requirements with a supervisor.

## What the project will and will not claim

The project can show how selected models perform on this benchmark under specified settings. It cannot establish that all Swedish RAG systems are unsafe, that Swedish is universally harder, or that a model can detect an undetectable falsehood. The benchmark's size, translation quality, model selection, and synthetic scenarios limit generalization and must be discussed.

