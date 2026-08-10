# B1/B2 contextual expansion

This directory is reserved for source-backed contextual additions after the
A1/A2 native pilot gate. It does not alter the frozen Batch01/Batch02 files or
the 888-row lexical core.

The head-review decision fixes the active target at 4,200 contextual rows:

- A1: 600 active
- A2: 600 active
- B1: 1,500 active
- B2: 1,500 active

`hold` rows are retained for auditability but excluded from active and
learner-ready counts. A row may become `learner_ready=true` only after the
two independent native reviews are recorded and the final status is
`native2_approved`.

Each future batch should be no larger than roughly 100 raw rows, with GPT
review submitted in chunks of about 25 rows. A source-backed row must replay
exactly to its cited source. LLM-composed Darija, translations from MSA or
English, and reconstructed sentences from isolated lexical items are not
source rows and must not be used to fill a quota.

The current local source inventory contains 1,156 unused MADOran sentences
after Batch01/02. That is an inventory for selection, not an automatic
learner release: level, domain, translation, standalone status, and native
acceptability still require review. A separate Oran source corpus is needed to
reach the full 4,200 active target without duplicating or inventing material.
