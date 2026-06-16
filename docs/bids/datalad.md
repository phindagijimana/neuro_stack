# Versioning datasets with DataLad

> Git for datasets that don't fit in git.

## The problem

A BIDS dataset is a folder of (often large) files. You want to track every change — what got added, when, by whom — but `git add my_dwi.nii.gz` chokes on a 200 MB blob and `git status` over a 100 GB tree takes minutes.

**DataLad** [Halchenko et al., 2021](https://doi.org/10.21105/joss.03262)[^datalad] solves this by combining `git` (for the small text files and the structure) with `git-annex` (for the large binary files).

## Mental model

DataLad treats a dataset like a git repo where:

- Small files (`participants.tsv`, JSON sidecars, README) are tracked normally.
- Large files (`.nii.gz`, `.dcm`, `.mgz`) are tracked as **annexed** — git stores a pointer; the actual bytes live in a content store (local disk, S3, an HTTP server).
- You can `datalad get` a file to materialise the bytes, `datalad drop` to free disk space without losing history.

The dataset itself is still git — every change is a commit, every release is a tag, every branch is a parallel timeline.

## Common operations

```bash
# Initialise a new dataset
datalad create -c text2git my_dataset
cd my_dataset

# Add files
datalad save -m "Add 10 subjects" .

# Get / drop content
datalad get sub-001/anat/sub-001_T1w.nii.gz
datalad drop sub-001/anat/sub-001_T1w.nii.gz   # frees disk; pointer survives

# Clone someone else's dataset (lazy — no large files yet)
datalad clone https://github.com/OpenNeuroDatasets/ds000114.git
cd ds000114
datalad get sub-01   # fetch one subject's bytes
```

## Why this is useful

- **Time-travel** — `git checkout v1.0.0` rolls the *whole dataset* back to a tagged release. Reproduce a published result.
- **Provenance** — `datalad run` wraps a command, records the inputs and outputs, and commits the resulting changes. Each commit becomes a recipe.
- **Cohort assembly** — datasets-of-datasets. Your study can be one DataLad superdataset containing many sub-datasets (raw cohort + each derivatives pipeline).
- **Sharing** — push a dataset to GitHub + a content store (S3, GIN). Collaborators clone the metadata cheaply and `get` only what they need.

## When to bother

- The dataset will live longer than the current project → yes.
- More than one person will touch it → yes.
- You're working alone for one paper → probably skip unless you already know DataLad.

The DataLad handbook — the single best learning resource — lives [here](https://handbook.datalad.org). DataLad has a learning curve. Most labs adopt it once they've been burned by "what changed between v1 and v2?" once. The official handbook (<https://handbook.datalad.org>) is excellent and worth a full day of reading before you commit to a project.

## References

[^datalad]: Halchenko YO, Meyer K, Poldrack B, et al. DataLad: distributed system for joint management of code, data, and their relationship. *J Open Source Softw.* 2021;6(63):3262. [doi:10.21105/joss.03262](https://doi.org/10.21105/joss.03262)

## Where to next

[Common pitfalls](pitfalls.md) — the bugs that break BIDS pipelines in production.
