# Benchmark data

`pilot.jsonl` is a draft, not a result or a research-ready benchmark. It contains 20 cases built from two fictional scenarios. Each scenario has English and Swedish versions and five evidence conditions: supported, partial, irrelevant documents, no context, and misleading conflict.

The Swedish text is machine-drafted and marked `translation_review.reviewed: false`. Have a fluent Swedish speaker check grammar, naturalness, ambiguity, and whether the evidence is equally strong in both languages before running the main experiment. Keep the fictional facts and expected answers paired when revising.

Each line is one JSON object matching `schema.json`. The model should receive the question and passages, but not the expected decision, answer key, misleading-claim label, or evidence IDs used for scoring. Those fields are gold labels for the evaluator. The runner deliberately selects only question and passage content for model prompts so labels are not leaked.


## Expanded draft

`expanded_draft.jsonl` adds 30 cases from three new fictional scenarios (C003–C005), each in English and Swedish across the same five conditions. It is deliberately kept separate from `pilot.jsonl`, so the pilot results and the larger draft cannot be mixed accidentally.

The expanded data is still a draft. All Swedish translations are marked unreviewed. Before running it, review Swedish fluency and fact equivalence, confirm that supported/partial/irrelevant labels match the questions, and check that every answer key is directly supported by its cited passage. The cases are synthetic and should not be described as representative of real-world documents.
