# Contextual expansion layer

This directory adds learner-oriented contextual samples without changing the
888-row lexical core. The first pilot is Batch 01:

- 96 source-backed utterances from MADOran V2
- A1 48 and A2 48
- four domains, 24 rows each: school/work, city/transport, body/health,
  food/shopping
- all rows start with review_status=source_verified and learner_ready=false

The canonical lexical dataset remains data/oran_darija_verified.tsv.
Contextual rows live under data/contextual/ and use the ODC identifier
namespace. lexical_refs points back to existing OD lexical IDs; no reverse
links or edits to the lexical core are required.

The source replay gate compares each source_form with the cited sentence in
the local MADOran sentence file. In this pilot arabic is retained exactly as
the source form and derivation_type=source_direct; later normalization must
include an explicit note and remain replayable.

This is an implementation batch, not a native-certified release. GPT review
must inspect all four chunks of 24 rows, and two independent Oran-native
reviews remain required before public learner release or audio/model use.
