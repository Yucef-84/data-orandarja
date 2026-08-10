# MADOran master dataset plan

This is the authoritative plan for the MADOran master database. The older
`B2_EXPANSION_PLAN.md` is retained only as historical context.

## Objective

Preserve all 1,356 MADOran source sentences as canonical Oran Darija assets,
link the upstream morphology annotation, and add reusable enrichment and
learning-unit layers without changing the source corpus. CEFR is a six-level
classification axis (`A1` through `C2`), not a quota or a source filter.

## Layers

1. `data/master/source/madoran_sentences.tsv` — exact source text, locator,
   WordCount, canonical source state, and immutable provenance.
2. `data/master/morphology/madoran_tokens.tsv` — the upstream 16-column
   morphology projection, linked by `Sentno` and `Wordno`.
3. Enrichment — separate fields for Arabic normalization, Latin, English,
   Korean, CEFR, difficulty, domain, topic, speech act, register, genre,
   linguistic features, and use permissions.
4. Learning units — derived segments, vocabulary, expressions, grammar, and
   culture assets with explicit source spans.
5. Exports — A1–C2, TTS, ASR, translation, morphology, vocabulary, and other
   views generated from the master layers.

## State and provenance policy

- MADOran original Arabic is always `source_status=canonical`.
- Source state is independent from enrichment and review state.
- Enrichment states are `not_started`, `draft`, `qa_passed`, `reviewed`, and
  `flagged`.
- Derived Arabic provenance is one of `source_exact`, `source_span_exact`,
  `source_modified`, or `generated`.
- `source_exact` and `source_span_exact` do not require mandatory native
  review. Modified or generated Darija does.
- The old contextual batches and native review files remain historical and
  calibration assets; they do not decide whether a MADOran source sentence is
  canonical.
- The provenance manifest uses POSIX paths and Git-canonical bytes (LF for
  tracked text); it records SHA-256, Git blob SHA-1, and byte size for the
  upstream snapshot. The builder and validator refuse to silently re-baseline
  a pinned snapshot.

## Execution gates

The project uses layered gates so an upstream morphology defect cannot block
safe work that depends only on the immutable source sentence layer. The
foundation, source, and source-provenance gates must pass before any derived
asset is written. Source-only enrichment is then `READY` even while the
morphology gate is blocked. Morphology-dependent enrichment, morphology
features, and morphology-dependent learning units remain blocked until the
morphology gate passes:

- 1,356 unique `Sentno` values, exactly 1..1356;
- source `WordCount` sum 30,919;
- exact source replay from the upstream sentence file;
- 30,919 morphology rows with the exact upstream 16-column schema;
- no orphan or unlinked tokens;
- per-sentence WordCount and Wordno sequences match exactly;
- no source or morphology mutation.

The current layer decision is recorded in
`data/master/state/madoran_layer_status.json` under HeadGPT decision
`HEAD-MADORAN-2026-08-10-01`. The unresolved upstream defect is recorded in
`data/master/issues/madoran_morphology_upstream_defect.json`.

The current local snapshot is expected to expose any upstream inconsistency;
the builder must report it rather than fabricate annotations. The four
official morphology representations are reconciled by
`scripts/reconcile_madoran_formats.py` before any integrity-gate decision.
For the current snapshot, TSV, CSV, JSON, and SQLite are identical at 30,915
rows and share the same missing/extra positions, so the result is
`UPSTREAM_DEFECT_CONFIRMED` and the morphology gate remains blocked.

## Source provenance

MADOran is retained under its upstream CC BY-NC 3.0 terms. The local snapshot
is associated with Mendeley Data DOI `10.17632/pgr766jbhp.2`; exact Git-canonical
file hashes and blob IDs are recorded in
`data/master/provenance_manifest.json`.

## Next phases after the first gate

1. Create and validate the source-only enrichment scaffold at
   `data/master/enrichment/madoran_sentence_enrichment.tsv`; it contains one
   row per canonical source sentence and does not copy `arabic_original`.
2. Enrich the 1,356 source rows in provenance-tracked batches with Latin,
   English, Korean, CEFR, difficulty, and source-grounded semantic labels.
3. Derive source-exact learning units with explicit source spans; keep
   morphology-dependent units blocked.
4. Add morphology-aware features and morphology-dependent exports only after
   a corrected official artifact satisfies the acceptance policy in the issue
   record.
5. Run automated QA, HeadGPT cross-checks, and native audits for modified or
   generated Darija, then generate purpose-specific exports.
6. Use additional licensed Oran sources only where the measured distribution
   is insufficient and provenance permits their inclusion.
