# Experiments

These folders define expected evaluation paths and outputs. FALCON H2 has the
first local-data-ready path; the speech, authorization, naturalistic, and
selection folders are synthetic protocol scaffolds until dataset-specific
ingestion is implemented.

The synthetic experiment is only a sanity check. Real-data evidence starts with
FALCON H2 after ingestion is implemented.

Pass 4 turns the Card, Willett, and Kunz speech-path folders into executable
synthetic protocol scaffolds. They validate contracts for communication,
language-prior attribution, and authorization before real-data ingestion.

Pass 5 turns the AJILE12 folder into an executable synthetic naturalistic
weak-label scaffold with proxy confidence and ambiguity metadata.

Pass 6 adds the bigP3BCI executable synthetic selection scaffold with prompted
symbol proxies and observed selection accuracy metadata.
