# Getting started

> The 30-minute on-ramp. Start here if you've never touched neuroimaging or shell tooling before — by the end you'll have run a real pipeline against a real BIDS dataset and saved your first figure.

The rest of the handbook assumes you have a working environment, can load a NIfTI file, and have run at least one BIDS app once. This mini-section gets you there. It is intentionally small: four pages, each one short, each one ending in a working artefact you can point at.

It is written for absolute beginners — students, software engineers from other domains, clinicians who code occasionally — but seasoned readers can skim it as a setup checklist for a fresh laptop or a new cluster account.

## Section map

<div class="grid cards" markdown>

-   :material-package-down: **[Installing your environment](install.md)** — Python 3.12, Apptainer / Docker, FSL or FreeSurfer license, VS Code Remote.

-   :material-brain: **[Your first NIfTI](first-nifti.md)** — load, inspect, plot a brain volume in ~15 lines of Python.

-   :material-application-cog-outline: **[Your first BIDS app](first-bids-app.md)** — run MRIQC on the bundled `sub-tiny` fixture.

-   :material-image-multiple: **[Your first figure](first-figure.md)** — render a publication-style brain figure with Nilearn.

</div>

By the end of these four pages you'll have done a complete mini-pipeline from raw data to a saved PNG.

## Prerequisites

- A Linux or macOS workstation (or WSL2 on Windows).
- Roughly 10 GB of free disk.
- A modern Python (3.10+).
- ~30 minutes.

You do **not** need an HPC account or a clinical scanner yet. The fixture dataset shipped with this repo is enough to follow every example.

## What this section does *not* cover

- **Real-world DICOM ingestion** and clinical PACS connectivity. Those come later — see [BIDS → DICOM to BIDS](../bids/dicom-to-bids.md).
- **HPC job submission, container building, or GPU training.** All deferred to [Computing](../computing/index.md). Here you stay on a single workstation.
- **Statistics or modelling.** The figure you produce is descriptive; inferential work belongs in [Analysis](../analysis/index.md).

The dividing line: this section gives you confidence that *something* works. The rest of the handbook turns that confidence into a research programme.

## Reading order

=== "Beginner"

    Do all four pages in order. Don't skip ahead — each one builds on the previous artefact.

    1. [Installing your environment](install.md)
    2. [Your first NIfTI](first-nifti.md)
    3. [Your first BIDS app](first-bids-app.md)
    4. [Your first figure](first-figure.md)

    At the end you'll have a working environment, a script that loads a brain, a `derivatives/` folder from a BIDS app, and a PNG worth screenshotting.

=== "Intermediate"

    Use this section as a checklist when bootstrapping a new machine or onboarding a new collaborator.

    1. [Installing your environment](install.md) for the environment-versioning details you might not have written down yet.
    2. Skim [Your first BIDS app](first-bids-app.md) for the canonical CLI invocation shape, then move on.

=== "Advanced / specialist"

    Probably skip this section, except to point a student at it.

    If you mentor newcomers, treat the four pages as the assignment for their first afternoon. The rest of the handbook becomes far easier to teach once everyone has run *one* pipeline end-to-end.

## Where to next

Once the on-ramp is done, [Reading paths](../paths/index.md) helps you choose where to go next — there are named paths for new researchers, software engineers pivoting in, clinicians, and ML engineers. If you want to keep building on the artefact you just produced, jump straight to [BIDS](../bids/index.md) or [Analysis](../analysis/index.md).
