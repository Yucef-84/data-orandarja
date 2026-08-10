# CEFR B2 expansion decision

The project head reviewed the current state and fixed “B2” as **CEFR B2**,
not contextual Batch02. Batch02 is complete at the GPT-review stage (104 raw,
87 active, 17 HOLD; all four chunks passed), but it is not native-certified.

## Active target

The long-term contextual target is 4,200 active rows:

| level | active target |
|---|---:|
| A1 | 600 |
| A2 | 600 |
| B1 | 1,500 |
| B2 | 1,500 |
| total | 4,200 |

HOLD rows are retained for auditability and excluded from active and
`learner_ready` counts. The lexical core remains frozen at 888 rows.

## Required gates

1. Run a native pilot on the current 183 active contextual rows with two
   independent Oran/Wahran reviewers.
2. Cluster and repair pilot errors; do not begin the next quota if the pilot
   misses the agreed acceptance thresholds.
3. Build A1/A2 to 1,200 active, then B1 to 1,500, then B2 to 1,500.
4. Use exact replayable Oran sources. GPT review and native review are separate
   gates; GPT `PASS` never makes a row learner-ready.
5. Set `learner_ready=true` only after `native2_approved` and disagreement
   resolution.

## Source reality check

The local MADOran V2 source has 1,356 sentences. After excluding the 200
sentences already used in Batch01/02, 1,156 unused sentences remain in
`data/contextual/madoran_unused_source_inventory.tsv`. This is not enough to
reach 4,200 active rows, and not every sentence will be suitable for every
level/domain. The inventory therefore does not assign a CEFR level or domain.

The repository must not fill the gap by translating MSA/English, composing
Darija with an LLM, or treating isolated words as source utterances. CORVAM
Oran is a conditional supplemental source only when its exact transcript,
locator, citation, and permitted use are preserved. A new licensed Oran native
corpus is required for the remaining B1/B2 volume.

## Implementation artifacts

- `data/contextual/schema_v2.json` defines A1–B2 levels and native-gated states.
- `scripts/build_contextual_source_inventory.py` builds the exact unused-source
  inventory without turning it into learner rows.
- `scripts/validate_contextual_expansion.py` reports raw, active, HOLD, and
  learner-ready counts and enforces replay/native gates.
- `reviews/native_contextual_reviews.tsv` and
  `reviews/native_contextual_review_summary.tsv` are the separate native-review
  records.
