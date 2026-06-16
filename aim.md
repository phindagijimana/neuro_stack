# Aim — internal

> Not published to the website. Lives at the repo root so it's visible on GitHub but excluded from the MkDocs build (which only ingests `docs/`).

## What we're aiming for

The neuro-handbook exists to take **someone who is brand new to neuroimaging** all the way to **senior Research engineer / Data engineer / AI engineer in neuroimaging at a PhD level**.

In practice that means a reader who works through the handbook end-to-end should be able to:

- Walk into any neuroimaging lab, read its methods sections critically, and run its pipelines.
- Stand up a production cohort pipeline on HPC or cloud, with proper observability, testing, and reproducibility.
- Train and honestly evaluate a 3D segmentation / classification model on multi-site data.
- Read the original methods papers (Pruessmann, Avants, Esteban, Isensee, etc.) and modify the underlying algorithms when their data needs it.
- Defend their analysis choices in front of a PhD committee, an FDA reviewer, or a senior data-engineering interviewer.

We treat "beginner → PhD" as a real, measurable claim:

- **Beginner entry**: a first-year graduate student with some Python should be able to install the environment, load a NIfTI, run a BIDS app, and produce a figure in their first afternoon (`Getting Started`).
- **PhD-level depth**: every methods chapter cites the primary literature with DOIs, derives the key math, and shows the worked example. Foundations (Mathematics, Physics, Statistics, Neuroscience), Medical imaging (Acquisition, Reconstruction, Segmentation, Registration), and the AI/ML training mechanics chapter are written so a PhD student can defend the content in a thesis chapter.
- **Engineering at scale**: the Data engineering section (Part I + 25 Part II chapters) is calibrated against what a senior data engineer is expected to know — Kleppmann, Reis & Housley, SRE book, Kimball, dbt, Iceberg / Delta, Flink, etc.

## Why we don't say this on the public site

Stating the aim on the website would distract from the content itself and risk reading as marketing. Readers should be able to *judge from the content* whether it meets the PhD-level claim — not be told it does.

So this document lives in the repo root, visible to maintainers and contributors via the GitHub file tree, but is not part of the MkDocs build (`mkdocs.yml` only ingests `docs/`).

## How we measure ourselves against the aim

Concrete signals the aim is being met:

- Every methods page cites at least one primary paper with a DOI.
- Every Foundations and Medical Imaging chapter has an Exercises block with 3 questions + collapsible solutions.
- Getting Started → first figure can be completed in under an hour by a true beginner.
- The Capstone tutorial walks DICOM → published figure end-to-end on one screen.
- Reading Paths gives at least four named sequences for distinct backgrounds.
- The Glossary has ≥ 100 cross-linked entries covering neuroimaging, statistics, data engineering, and ML.
- The repo's pytest suite + ruff + `mkdocs build --strict` all pass in CI.

Failing any of these is a defect to fix, not a feature to leave alone.

## Audience priority order

When trade-offs arise, we weight in this order:

1. The brand-new researcher who needs a working mental model before they can ask a precise question.
2. The PhD student who needs depth and the primary literature.
3. The software / data engineer / ML engineer pivoting in from outside neuroimaging.
4. The clinician learning the engineering side.

Anything that benefits only the senior reader at the expense of the newcomer is the wrong trade-off. Anything that simplifies for the newcomer but loses the citation / math depth is also wrong.

## Maintainer notes

- This file is `aim.md` at the repo root.
- It is not in `docs/` and is not in `mkdocs.yml` nav, so `mkdocs build` ignores it.
- GitHub will render it via its file browser.
- Update this file when the aim genuinely shifts. Don't update it just because the content changed; the aim should outlive any specific chapter.
