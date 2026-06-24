# Validating a BIDS dataset

> Before you point a BIDS app at a dataset, validate it. Always.

## Why validate

A BIDS app trusts the spec. If your dataset is *almost* BIDS, the app will do *almost* the right thing — and the bug will surface six hours into the run, on subject 47, in a way that's painful to debug. The validator catches structural problems in seconds.

## Three ways to validate

### 1. The web validator

The web validator lives [here](https://bids-standard.github.io/bids-validator/).

Drag your dataset into the browser. Nothing leaves your machine — it's a JavaScript app running locally. Great for one-off checks, painful for large datasets.

### 2. The CLI

```bash
# Node version (the canonical implementation)
npx bids-validator path/to/dataset

# Container version
docker run -v $PWD/dataset:/data:ro bids/validator /data
apptainer run docker://bids/validator /data
```

The CLI returns non-zero exit codes on errors, which means you can wire it into CI:

```bash
npx bids-validator path/to/dataset --json > validation.json
jq '.issues.errors | length' validation.json
```

### 3. From Python

```python
from bids import BIDSLayout
layout = BIDSLayout("path/to/dataset", validate=True)  # raises on errors
```

PyBIDS — full docs [here](https://bids-standard.github.io/pybids/) — uses an older validator but it's good enough to catch the common errors.

## Reading the output

The validator returns three categories:

- **Errors** — your dataset is not BIDS. Fix before running anything.
- **Warnings** — your dataset is *probably* BIDS but something is unusual. Fix when you can.
- **Ignored files** — files outside the BIDS spec (a stray `README.txt`, a `.DS_Store`). Usually harmless.

Typical errors and the fix:

| Error | Cause | Fix |
| --- | --- | --- |
| `PARTICIPANT_ID_MISMATCH` | Subject folder name doesn't match `participants.tsv` | Align the casing and zero-padding |
| `MISSING_DATASET_DESCRIPTION` | No `dataset_description.json` at the root | Create one with `Name` and `BIDSVersion` |
| `BVAL_MULTIPLE_ROWS` | A `.bval` file has more than one row | One row per file; check the converter |
| `INTENDED_FOR_MISSING` | `IntendedFor` in a fmap sidecar points at a file that doesn't exist | Check the path; common after subject renames |
| `JSON_SCHEMA_VALIDATION_ERROR` | A sidecar key has the wrong type | Read the validator output — it tells you which key |

## Validate before, validate after

A useful discipline: run the validator on the **raw** dataset before the BIDS app, and on the `derivatives/` output after. The derivatives spec is part of BIDS too, and validating it catches half the "my pipeline outputs aren't recognised by the next pipeline" problems.

## BIDS Extension Proposals (BEPs) — what to adopt and when

BIDS grows by [BEPs](https://bids.neuroimaging.io/get_involved.html#extending-the-bids-specification): formal proposals that move from draft to merged into the main spec via the [BIDS Maintainers Group](https://bids.neuroimaging.io/governance.html) and pull requests against the [bids-standard/bids-specification](https://github.com/bids-standard/bids-specification) repo. Some are stable and shipped; some are still moving. At research depth the question is not "is there a BEP for X" but "is the BEP stable enough that my validator, my converter, and my downstream tools all agree on it".

A working snapshot of the BEPs most relevant to neuroimaging pipelines:

| BEP | Domain | Status verdict |
| --- | --- | --- |
| [BEP004](https://bids.neuroimaging.io/extensions.html) | PET | Adopted — merged into the spec, validate normally |
| [BEP016](https://bids.neuroimaging.io/extensions.html) | dMRI derivatives | Recent, mostly safe — supported by [QSIPrep](https://qsiprep.readthedocs.io/) |
| [BEP020](https://bids.neuroimaging.io/extensions.html) | fMRI derivatives | Stable — what [fMRIPrep](https://fmriprep.org/) writes |
| [BEP024](https://bids.neuroimaging.io/extensions.html) | Computed Tomography | Niche but stable |
| [BEP028](https://bids.neuroimaging.io/extensions.html) | MR Spectroscopy (MRS) | Recent — pair with [Osprey](https://github.com/schorschinho/osprey) |
| [BEP030](https://bids.neuroimaging.io/extensions.html) | Quantitative MRI (qMRI) | Recent — entity names still settling |
| [BEP037](https://bids.neuroimaging.io/extensions.html) | Microscopy | Separate domain, stable inside it |
| [BEP038](https://bids.neuroimaging.io/extensions.html) | Phenotypic / behavioural | In flux — wait |
| [BEP039](https://bids.neuroimaging.io/extensions.html) | Atlases | Early — experimental only |
| [BEP042](https://bids.neuroimaging.io/extensions.html) | Dataset description / DICOM dataset description | Admin, stable |

**Why this matters.** A validator pinned to BIDS 1.6 will flag perfectly valid BEP030 qMRI entities as errors. [PyBIDS](https://bids-standard.github.io/pybids/) lags the spec by months — entities introduced in a fresh BEP may not yet be queryable. And spec drift between draft BEP revisions means a dataset built against BEP028-draft-3 may not validate against BEP028-draft-5.

Practical guidance:

- **Pin the validator** in CI (`npx bids-validator@1.14.0`, or a fixed Docker tag). Upgrade deliberately, not on every push.
- **Declare your BEPs** in `dataset_description.json` under the `BIDSVersion` field, plus an `HEDVersion`/`DatasetType` where relevant — readers can see what they're consuming.
- **Track the upstream PR**. If the BEP you depend on hasn't merged into the spec yet, link the open PR in your dataset's README.
- **Respect the Maintainers Group decisions.** If a BEP is rejected or restructured, your dataset is technically debt; budget time to migrate rather than ignore it.

When in doubt, the [extensions overview](https://bids.neuroimaging.io/get_involved.html#extending-the-bids-specification) lists the live BEPs and their status, and the [spec repo](https://github.com/bids-standard/bids-specification) issues/PRs show what's currently moving.

## References

- BIDS Extension Proposals — [bids.neuroimaging.io/get_involved.html#extending-the-bids-specification](https://bids.neuroimaging.io/get_involved.html#extending-the-bids-specification)
- BIDS specification repository — [github.com/bids-standard/bids-specification](https://github.com/bids-standard/bids-specification)
- BIDS Validator — [bids-standard.github.io/bids-validator](https://bids-standard.github.io/bids-validator/)

## Where to next

[DICOM to BIDS](dicom-to-bids.md) — how the dataset got into BIDS shape in the first place.
