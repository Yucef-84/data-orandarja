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

## Execution gates

The first gate is source and morphology integrity. No enrichment or learning
unit generation begins until both source and morphology QA pass:

- 1,356 unique `Sentno` values, exactly 1..1356;
- source `WordCount` sum 30,919;
- exact source replay from the upstream sentence file;
- 30,919 morphology rows with the exact upstream 16-column schema;
- no orphan or unlinked tokens;
- per-sentence WordCount and Wordno sequences match exactly;
- no source or morphology mutation.

The current local snapshot is expected to expose any upstream inconsistency;
the builder must report it rather than fabricate annotations.

## Source provenance

MADOran is retained under its upstream CC BY-NC 3.0 terms. The local snapshot
is associated with Mendeley Data DOI `10.17632/pgr766jbhp.2`; exact file hashes
are recorded in `data/master/provenance_manifest.json`.

## Next phases after the first gate

1. Enrich all 1,356 source rows without altering `arabic_original`.
2. Add morphology-aware features and six-level CEFR/difficulty annotations.
3. Derive learning units with source spans.
4. Run automated QA, LLM cross-checks, and native audits for modified or
   generated Darija.
5. Generate purpose-specific exports and use additional licensed Oran sources
   only where the measured distribution is insufficient.
