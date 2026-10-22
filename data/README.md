# Benchmark data

`pilot.jsonl` is a draft, not a result or a research-ready benchmark. It contains 20 cases built from two fictional scenarios. Each scenario has English and Swedish versions and five evidence conditions: supported, partial, irrelevant documents, no context, and misleading conflict.

The Swedish text is draft material and marked `translation_review.reviewed: false`. A fluent Swedish reviewer is preferred. If one is unavailable, use two independent language-model checks plus a Swedish-to-English back-translation to find possible wording and meaning mismatches. These checks do not count as human validation: keep `reviewed: false`, document the limitation, and treat Swedish results as exploratory. Keep fictional facts and expected answers paired when revising.

Each line is one JSON object matching `schema.json`. The model should receive the question and passages, but not the expected decision, answer key, misleading-claim label, or evidence IDs used for scoring. Those fields are gold labels for the evaluator. The runner deliberately selects only question and passage content for model prompts so labels are not leaked.


## Expanded draft

`expanded_draft.jsonl` adds 30 cases from three new fictional scenarios (C003–C005), each in English and Swedish across the same five conditions. It is deliberately kept separate from `pilot.jsonl`, so the pilot results and the larger draft cannot be mixed accidentally.

The expanded data is still a draft. All Swedish translations are marked unreviewed. Before running it, check fact equivalence, confirm that supported/partial/irrelevant labels match the questions, and verify that every answer key is directly supported by its cited passage. Prefer a fluent human review; if unavailable, record independent language-model checks and back-translation as a weaker substitute. Do not claim human-validated Swedish or draw strong language-comparison conclusions from it. The cases are synthetic and should not be described as representative of real-world documents.
