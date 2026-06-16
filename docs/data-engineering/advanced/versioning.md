# Versioning everything

> Code, data, models — semver for data products.

## What needs to be versioned

- **Code.** Git, semver tags, signed releases.
- **Data.** Raw and derived. Snapshots, lakehouse versions, DataLad commits.
- **Container images.** Pinned tags + content digests; never `:latest`.
- **Models.** Weights + training data + hyperparameters together.
- **Configs.** YAML in git; never editable in prod.
- **Schemas.** Schema registry.
- **Atlases / templates.** TemplateFlow versions in your manifest.

A run that doesn't pin all of these isn't reproducible.

## Data versioning options

| Tool | Mental model |
|---|---|
| **DataLad** | Git + git-annex; per-file granularity |
| [**DVC**](https://dvc.org) | Git pointers to S3 objects; pipeline-aware |
| [**LakeFS**](https://docs.lakefs.io) | Git semantics over object storage |
| **Iceberg / Delta snapshots** | Built-in time-travel |
| **Pachyderm** | Container-native pipelines + versioning |

BIDS → DataLad. Analytical tables → Iceberg / Delta. ML training data → DVC or LakeFS.

## Semver for data products

[Semantic Versioning](https://semver.org):

- **MAJOR** — breaking schema change.
- **MINOR** — backward-compatible addition.
- **PATCH** — bug fix, no schema change.

## A coherent versioning manifest

```json
{
  "code":           {"git_sha": "abc123", "release": "v2.4.1"},
  "data_raw":       {"datalad_tag": "dataset-v1.3"},
  "data_derived":   {"iceberg_snapshot": 9217341123},
  "containers":     {"fmriprep": "nipreps/fmriprep:24.0.0@sha256:..."},
  "models":         {"segmenter": "lab/seg:1.0.0", "weights_sha": "..."},
  "templates":      {"templateflow": "0.10.0", "MNI152NLin2009cAsym": "res-1"}
}
```

Reproducibility becomes a `git checkout` away.

## References

1. **Semantic Versioning 2.0.0.** [https://semver.org](https://semver.org)
2. **DataLad Handbook.** [https://handbook.datalad.org](https://handbook.datalad.org)
3. **DVC Documentation.** [https://dvc.org/doc](https://dvc.org/doc)

## Where to next

[Networking essentials](networking.md).
