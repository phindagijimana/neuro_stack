# BIDS toolkit

> Practical recipes for organising, validating, querying, and versioning BIDS datasets — the day-to-day craft that turns a folder of NIfTIs into a dataset other pipelines can consume.

The [Fundamentals → File formats](../fundamentals/file-formats.md) page explains what BIDS *is* ([Gorgolewski et al., 2016](https://doi.org/10.1038/sdata.2016.44))[^bids]. This section is about what you actually *do* with it: converting raw DICOMs, validating the result, querying it from Python, laying out derivatives, versioning whole studies, and avoiding the failure modes that quietly corrupt downstream analyses.

It's written for the person who has a directory of imaging data and now has to make it usable. Not for the person designing a new specification — for that, the [BIDS specification](https://bids-specification.readthedocs.io/en/stable/) is the source of truth.

## Section map

<div class="grid cards" markdown>

-   :material-shield-check: **[Validating a dataset](validation.md)** — running the BIDS validator (CLI, web, Python) and reading its output without panic.

-   :material-folder-arrow-right: **[DICOM to BIDS](dicom-to-bids.md)** — HeuDiConv, Dcm2Bids, and the heuristics file that does 80% of the work.

-   :material-database-search: **[Querying with PyBIDS](pybids.md)** — `BIDSLayout`, filters, and writing pipeline code that doesn't break on the next dataset.

-   :material-file-tree: **[Derivatives layout](derivatives.md)** — how to lay out your own outputs so the next BIDS app can read them.

-   :material-source-branch: **[Versioning with DataLad](datalad.md)** — git + git-annex for datasets that don't fit in git.

-   :material-alert-octagon: **[Common pitfalls](pitfalls.md)** — special characters in IDs, IntendedFor mistakes, sidecar inheritance bugs.

</div>

## The canonical BIDS resources

- The BIDS [specification](https://bids-specification.readthedocs.io/en/stable/) — your authoritative reference.
- Example BIDS [datasets](https://github.com/bids-standard/bids-examples) to test pipelines against.
- The BIDS [Starter Kit](https://github.com/bids-standard/bids-starter-kit), with templates and tutorials.
- A [glossary](https://bids-specification.readthedocs.io/en/stable/glossary.html) of every BIDS entity.

All examples in this section can run against `fixtures/sub-tiny/` in this repo, so you don't need a real cohort to follow along.

## What this section does *not* cover

- **The specification itself.** When in doubt, the BIDS spec wins; this section gives you the operational shortcuts but never overrides it.
- **Modality-specific acquisition advice.** That belongs in [Fundamentals → Modalities](../fundamentals/modalities.md).
- **What to compute once your data is BIDS-valid.** See [Analysis](../analysis/index.md) for that.

The dividing line: this section is about *moving data into the right shape*. Once the shape is right, the rest of the handbook takes over.

## Reading order

=== "Beginner"

    Goal: organise a small dataset, run the validator, and read it from Python.

    1. [DICOM to BIDS](dicom-to-bids.md)
    2. [Validating a dataset](validation.md)
    3. [Querying with PyBIDS](pybids.md)

    After these three pages you can write a script that says "give me all the T1w scans for these subjects" and trust the answer.

=== "Intermediate"

    Goal: produce your own BIDS-app outputs that downstream tools can consume.

    1. [Derivatives layout](derivatives.md)
    2. [Common pitfalls](pitfalls.md)
    3. Revisit [Querying with PyBIDS](pybids.md) with a multi-session, multi-task dataset.

    By the end you should be writing BIDS-compliant `derivatives/` trees that fMRIPrep, QSIPrep, or your own group-analysis code can ingest without special-casing.

=== "PhD / specialist"

    Goal: run a multi-site dataset that has to be reproducible years from now.

    1. [Versioning with DataLad](datalad.md) — datasets that outlive a single project.
    2. [Common pitfalls](pitfalls.md) revisited — the failure modes that only show up at scale.
    3. Extension proposals (BEPs) in the [BIDS specification repo](https://github.com/bids-standard/bids-specification) — what's coming for microscopy, NIRS, PET, computational models.
    4. The BIDS [maintainers' working groups](https://bids.neuroimaging.io/) — for contributing back.

    The skill at this level is knowing *which* BEPs you can adopt early without breaking the validator, and which derivatives conventions your downstream tools actually enforce.

## Where to next

When the dataset is solid, jump to [Analysis](../analysis/index.md) to start computing things from it, or to [Data engineering](../data-engineering/index.md) to scale the pipeline that produced it.

## References

[^bids]: Gorgolewski KJ, Auer T, Calhoun VD, et al. *Sci Data.* 2016;3:160044. [doi:10.1038/sdata.2016.44](https://doi.org/10.1038/sdata.2016.44)
