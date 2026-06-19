# Analysis

> What you can compute from preprocessed neuroimaging data — organised by modality, with the statistics chapters that apply to all of them.

This section assumes the data has already been through preprocessing (see [Fundamentals → Preprocessing](../fundamentals/preprocessing.md)) and a BIDS app or two. The pages below cover what comes next: the *measurements* you extract per subject, and the *inferences* you draw at the group level.

It's written for someone who already knows what an fMRI run or a DWI shell is, and now needs to extract a meaningful number from one. The section deliberately stays modality-focused; if you only do fMRI you can skip the diffusion page, but everyone reads the two statistics pages.

## Section map

<div class="grid cards" markdown>

-   :material-brain: **[Structural morphometry](structural.md)** — cortical thickness, surface area, subcortical volumes; FreeSurfer + ENIGMA pipelines.

-   :material-vector-polyline: **[Diffusion & tractography](diffusion.md)** — tensor metrics (FA / MD), HARDI reconstruction, fibre tracking, connectomes.

-   :material-pulse: **[Functional connectivity](functional.md)** — seed-based, ROI-to-ROI, ICA; Nilearn's role in the modern stack.

-   :material-grid: **[Surface-based analysis](surface.md)** — when volumetric analysis loses the signal and surfaces don't.

-   :material-wave: **[EEG / MEG](eeg-meg.md)** — sensor- and source-space analysis for electrophysiology.

-   :material-sigma: **[Group-level statistics](group-stats.md)** — voxel-wise, vertex-wise, network-level; GLM, mixed models, permutation.

-   :material-chart-bell-curve-cumulative: **[Multiple comparisons](multiple-comparisons.md)** — FDR, FWE, TFCE, cluster correction, and how to choose.

</div>

## Engineering vs analysis

Analysis is the *what*; engineering is the *how*. A well-engineered pipeline that computes the wrong statistic is no better than a brittle script that computes the right one. This section focuses on the methods; the [Data engineering](../data-engineering/index.md) section handles the pipeline mechanics around them.

## What this section does *not* cover

- **Preprocessing.** Assumed done. See [Fundamentals → Preprocessing](../fundamentals/preprocessing.md) for distortion correction, motion correction, normalisation, denoising.
- **Learning a representation.** If the per-subject "measurement" comes out of a neural net, you want [AI / ML for neuroimaging](../ai/index.md).
- **Cohort design and study power.** Those are upstream of any analysis page here; treat them as prerequisites.

The dividing line: this section assumes the data is clean and well-organised, and the question is *which number do I compute and how do I defend it*.

## Reading order

=== "Beginner"

    Goal: extract one credible measurement per subject in your modality of choice.

    1. The page for your primary modality — [Structural](structural.md), [Diffusion](diffusion.md), [Functional](functional.md), or [EEG / MEG](eeg-meg.md).
    2. [Group-level statistics](group-stats.md) — the basics of how those per-subject numbers become a result.
    3. [Multiple comparisons](multiple-comparisons.md) — before you publish *anything*.

    These three pages are enough to write up a single-modality study honestly.

=== "Intermediate"

    Goal: combine modalities or move beyond volumes.

    1. A second modality page to pair with your first (e.g. structural + diffusion).
    2. [Surface-based analysis](surface.md) — when cortex is your target.
    3. [Group-level statistics](group-stats.md) revisited with mixed-effects and longitudinal designs.

    At this stage you start picking the right *space* (volume / surface / network) for the question, not just the right tool.

=== "PhD / specialist"

    Goal: defend a methods section against a sceptical reviewer.

    1. [Multiple comparisons](multiple-comparisons.md) read end-to-end — TFCE, permutation, cluster failure modes (Eklund-style).
    2. The advanced sections of [Diffusion](diffusion.md) (HARDI, multi-tissue CSD) or [Functional connectivity](functional.md) (dynamic FC, dynamical-systems models).
    3. [Surface-based analysis](surface.md) for laminar / high-resolution work.
    4. Modality-specific landmark papers from [Landmark → Foundational papers](../landmark/papers.md).

    Specialist work lives in the gap between what the tools default to and what your question actually needs. These pages flag where those gaps are.

## Where to next

Want to make the per-subject numbers come out of a model rather than a classical pipeline? See [AI / ML for neuroimaging](../ai/index.md). Need to scale to thousands of subjects? See [Computing](../computing/index.md) and [Data engineering](../data-engineering/index.md).
