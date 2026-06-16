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

## Where to next

[DICOM to BIDS](dicom-to-bids.md) — how the dataset got into BIDS shape in the first place.
