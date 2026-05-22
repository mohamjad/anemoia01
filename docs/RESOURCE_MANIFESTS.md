# Resource Manifests

Resource manifests are YAML files under
`src/intentfidelity/resources/manifests/`.

Each manifest names a dataset, its first-pass status, the available proxy
sources, known limitations, and the role it plays in the evaluation roadmap.

Required fields:

- `dataset_id`
- `title`
- `domain`
- `status`
- `priority`
- `access`
- `modalities`
- `weak_proxy_sources`
- `known_limitations`
- `first_pass_role`

The registry validates shape and ordering, but it does not imply that ingestion
or real-data evaluation has been implemented.

For FALCON H2, the manifest also records the DANDI identifier, source URL,
expected split directories, and the current evidence stage for the pass-2 path.
