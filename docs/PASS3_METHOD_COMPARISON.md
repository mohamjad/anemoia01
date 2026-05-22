# Pass 3 Method Comparison

Pass 3 turns baseline comparison into runnable infrastructure.

Implemented scope:

- typed `LabeledExample` feature records
- identity, session-centering, whitening, and whitening-coloring transforms
- nearest-centroid prediction baseline
- default centroid baseline suite
- synthetic sanity eval
- FALCON H2 character-window feature baseline eval
- comparison reports with ranking disagreement and over-adaptation events

The baseline models are intentionally simple. They are evaluation plumbing and
reference methods, not state-of-the-art decoders.

