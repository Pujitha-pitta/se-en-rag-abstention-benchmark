# Swedish draft language review

**Review type:** AI-assisted editorial review  
**Date:** 2026-10-22  
**Scope:** The 15 Swedish cases in `data/expanded_draft.jsonl` for scenarios C003–C005  
**Human review:** Not completed. No fluent Swedish speaker reviewed these cases.

## What was checked

The Swedish questions, passages, source labels, answer keys, and condition labels were compared with their matched English cases. The review checked that dates, numbers, entities, and the intended evidence strength were preserved, and that the `partial` cases leave the requested detail unresolved.

Two small terminology edits were made: `projektlaptop` was changed to `projektdator`, and `kalkylblad` to `kalkylark`.

## Case alignment notes

- **C003 — travel reimbursement:** The supported and conflict cases preserve the 30 June 2026 deadline; the superseded claim remains 31 May. The partial case gives only the month, and the irrelevant case discusses eligible expenses without a deadline.
- **C004 — equipment loan:** The supported and conflict cases preserve the 14-calendar-day loan period; the superseded claim remains 21 days. The partial case asks for a return date but omits the checkout date.
- **C005 — arts grant:** The supported and conflict cases preserve the signature requirement. The partial case establishes that the form must be signed but does not say who signs it. The irrelevant case describes eligibility, not signature requirements.

## Limitation

This is an AI-assisted consistency and editing pass, not human language validation. It cannot establish that the Swedish is fully idiomatic or free of subtle ambiguity. All Swedish entries therefore remain `translation_review.reviewed: false`. Treat results using this draft as exploratory and disclose the lack of fluent-human review.
