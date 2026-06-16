# Querying with PyBIDS

Official PyBIDS documentation lives [here](https://bids-standard.github.io/pybids/).

> PyBIDS turns a BIDS dataset into a queryable database. Use it instead of glob patterns.

## Why not just glob

The bash habit of `find dataset -name '*T1w.nii.gz'` works on day 1 and breaks on day 14:

- A second session shows up → the glob now returns two files per subject.
- Someone runs the dataset through a defacing tool → there are now `*_desc-defaced_T1w.nii.gz` files too.
- A fmap is added → the glob doesn't see it but your pipeline needs it.

PyBIDS [Yarkoni et al., 2019](https://doi.org/10.21105/joss.01294)[^pybids] reads the spec and gives you typed queries.

## The 5-minute API

```python
from bids import BIDSLayout

layout = BIDSLayout("fixtures/sub-tiny")

# All subjects
print(layout.get_subjects())          # ['001', '002']

# All T1w images
t1s = layout.get(suffix="T1w", extension=".nii.gz")
for f in t1s:
    print(f.path, f.entities)

# Just one subject, one datatype
dwi = layout.get(subject="001", datatype="dwi", extension=".nii.gz")[0]
print(dwi.path)
print(dwi.get_metadata())  # JSON sidecar as a dict

# Get all subjects with both anat and dwi
have_both = [
    sub for sub in layout.get_subjects()
    if layout.get(subject=sub, datatype="anat") and
       layout.get(subject=sub, datatype="dwi")
]
```

## Filter by entity, not by filename

`layout.get(...)` accepts any BIDS entity (`subject`, `session`, `task`, `run`, `acquisition`, `desc`, etc.) plus `datatype`, `suffix`, and `extension`. Filenames are an output, not an input.

## Iterating sensibly

```python
for sub in layout.get_subjects():
    for ses in layout.get_sessions(subject=sub) or [None]:
        t1 = layout.get(subject=sub, session=ses, suffix="T1w", extension=".nii.gz")
        if not t1:
            continue
        dwi = layout.get(subject=sub, session=ses, suffix="dwi", extension=".nii.gz")
        process(t1[0].path, dwi[0].path if dwi else None)
```

That handles sessions-or-no-sessions and missing-DWI cleanly. Glob patterns can't.

## Querying derivatives

```python
layout = BIDSLayout("dataset", derivatives=True)
fmriprep = layout.derivatives["fMRIPrep"]
preproc = fmriprep.get(subject="001", desc="preproc", suffix="bold", extension=".nii.gz")
```

Every BIDS app should produce a `dataset_description.json` under its `derivatives/<name>/` folder. PyBIDS uses that to expose each derivative as its own layout.

## Validation as you go

```python
layout = BIDSLayout("dataset", validate=True)  # raises on spec violations
```

For pipelines, prefer `validate=True`: better to fail at startup than after 10 hours of compute. For exploration, `validate=False` is fine.

## When PyBIDS isn't enough

PyBIDS reads metadata into memory. For datasets with >10 k subjects you'll feel it (memory + startup). Options:

- **Cache the layout** — `layout = BIDSLayout(..., database_file="layout.sqlite")` writes a SQLite index that subsequent runs load instantly.
- **Pre-compute a manifest** — emit a small CSV or Parquet with the file paths and entities you need; query that.
- **Roll your own walker** — the repo ships a tiny one at `neuro_handbook.bids.walk_bids` for teaching purposes; PyBIDS-equivalent for the common cases.

## References

[^pybids]: Yarkoni T, Markiewicz CJ, de la Vega A, et al. PyBIDS: Python tools for BIDS datasets. *J Open Source Softw.* 2019;4(40):1294. [doi:10.21105/joss.01294](https://doi.org/10.21105/joss.01294)

## Where to next

[Derivatives layout](derivatives.md) — once you produce your own outputs, how do you lay them out so the next tool can read them?
