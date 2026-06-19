# Landmark work

> The papers, pipelines, datasets, and atlases every neuroimaging researcher should know — a curated, opinionated tour rather than an exhaustive bibliography.

Knowing the *literature* is what separates a competent user from someone who can adapt when the tools change. The pages here exist so that a new postdoc, a software engineer pivoting in, or an ML researcher new to medical data can build a working mental model of the field in a weekend — and know what to read next when a specific question comes up.

It is deliberately small. Each page lists a handful of works with one-line summaries. The goal is "if you read these, you can read the others."

## Section map

<div class="grid cards" markdown>

-   :material-book-open-page-variant: **[Foundational papers](papers.md)** — what to read, in what order, to understand how the field thinks today.

-   :material-database: **[Reference datasets](datasets.md)** — HCP, UK Biobank, ABCD, ADNI, OASIS, OpenNeuro: what's in each and how to get access.

-   :material-pipe: **[Major pipelines](pipelines.md)** — FreeSurfer, FSL, AFNI, ANTs, MRtrix3, fMRIPrep, QSIPrep, FastSurfer, MELD, HippUnfold — what each is for.

-   :material-application-cog: **[BIDS-app workflows](bids-apps.md)** — the standardised CLI shape and how to chain BIDS apps together.

-   :material-atlas: **[Atlases and templates](atlases.md)** — Desikan-Killiany, Destrieux, Schaefer, HCP-MMP, AAL, Glasser; MNI152, fsaverage, fsLR.

</div>

## How this section is curated

Each page is a hand-picked shortlist. Inclusion criteria, roughly: the work is cited by most modern pipelines, has shaped how the field defines a measurement, or unlocked a new modality at scale. Exclusion criteria: equally good but less canonical alternatives that don't change the story. Pull requests welcome to add missing pieces.

## What this section does *not* cover

- **A complete bibliography.** This is a shortlist by design. The papers cited here cite the rest of the field.
- **How to use the tools day-to-day.** That belongs in [BIDS](../bids/index.md), [Analysis](../analysis/index.md), [AI / ML](../ai/index.md), and [Computing](../computing/index.md). Here you learn what each tool *is*; the operational chapters teach you to run them.
- **Methodological critique.** Where a landmark paper has been challenged or superseded, the page flags it briefly, but the deep methods debate lives in the analysis pages, not here.

## Reading order

=== "Beginner"

    Goal: be able to follow a methods section without looking everything up.

    1. [Foundational papers](papers.md) — read top-to-bottom; the order is chronological-ish and pedagogically chosen.
    2. [Reference datasets](datasets.md) — at least skim, so you recognise dataset names in the wild.
    3. [Atlases and templates](atlases.md) — know what "MNI152 space" and "fsaverage" actually mean.

    After this you can read a paper in the field and parse the methods.

=== "Intermediate"

    Goal: pick the right tool and the right reference cohort for your question.

    1. [Major pipelines](pipelines.md) — what each pipeline is good at and where they overlap.
    2. [BIDS-app workflows](bids-apps.md) — how to chain pipelines without writing glue forever.
    3. [Reference datasets](datasets.md) revisited with an eye on which cohort matches your question.

    By the end you can defend a "we used X because Y" sentence to a reviewer.

=== "PhD / specialist"

    Goal: contribute methods, datasets, or tools — not just consume them.

    1. The primary citations behind your tool of choice, traced from [Major pipelines](pipelines.md) and [Foundational papers](papers.md).
    2. The data-access and consent terms behind the cohorts you plan to use, via [Reference datasets](datasets.md).
    3. The atlas comparison literature linked from [Atlases and templates](atlases.md) — when atlas choice changes the answer.

    Specialists distinguish *what the tool does* from *what the original paper claimed*; the gap is where novel work happens.

## Where to next

The papers and pipelines listed here are picked up in practice across [BIDS](../bids/index.md), [Analysis](../analysis/index.md), and [AI / ML](../ai/index.md). When you need the underlying physics or biology, jump back to [Fundamentals](../fundamentals/index.md).
