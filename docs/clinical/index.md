# Clinical applications

> Where techniques meet diseases. The section a PhD student lives in once their pipeline starts saying something about a patient.

Most neuroimaging methods are developed against healthy adult cohorts (HCP, UK Biobank) and only later asked to behave in the presence of pathology. This section flips the orientation: each chapter starts from a *disease* — its clinical picture, its biology — and works outward to the imaging biomarkers, pipelines, atlases, and reference cohorts the field has built around it.

The point is integration. Knowing that DWI shows restricted diffusion is fundamentals. Knowing that a DWI-perfusion mismatch decides whether a patient gets thrombectomy at hour 18 is clinical. The first lets you process an image; the second lets you talk to the neurologist.

If you're new to the underlying neuroanatomy, read [Fundamentals → Neuroscience & neurology](../fundamentals/foundations/neuroscience.md) first — that page gives the macro / micro anatomy and a one-paragraph tour of each disease. This section assumes that vocabulary and goes deeper into the imaging-specific evidence.

## Section map

<div class="grid cards" markdown>

-   :material-brain: **[Alzheimer's & related dementias](alzheimers-and-dementia.md)** — A/T/N framework, amyloid + tau PET, hippocampal atrophy, ADNI, the lecanemab era.

-   :material-walk: **[Parkinson's & movement disorders](parkinsons-and-movement.md)** — DaTscan, neuromelanin MRI, QSM iron in SN, PPMI, DBS targeting.

-   :material-pulse: **[Stroke & traumatic brain injury](stroke-and-tbi.md)** — DWI/ADC, perfusion-DWI mismatch, late-window thrombectomy, ISLES, ATLAS, TRACK-TBI.

-   :material-flash: **[Epilepsy](epilepsy.md)** — HARNESS-MRI, FCD detection (MELD), SISCOM, MEG localisation, surgical planning.

-   :material-head-cog: **[Psychiatric disorders](psychiatry.md)** — small effect sizes, big samples, ENIGMA, ABCD, the Marek 2022 reckoning.

-   :material-circle-multiple: **[Multiple sclerosis](multiple-sclerosis.md)** — FLAIR lesion load, central vein sign, paramagnetic rim lesions, SIENA atrophy, myelin imaging.

</div>

## Reading order

=== "Beginner"

    Goal: understand why a clinician orders the scans they order.

    1. Skim [Fundamentals → Neuroscience & neurology](../fundamentals/foundations/neuroscience.md) for the disease vocabulary.
    2. [Stroke & TBI](stroke-and-tbi.md) — the most time-critical, the cleanest imaging-to-decision pipeline.
    3. [Alzheimer's & dementia](alzheimers-and-dementia.md) — the most heavily standardised biomarker framework.
    4. [Multiple sclerosis](multiple-sclerosis.md) — disease-activity monitoring as a longitudinal imaging problem.

    After this you can read a clinical research paper and parse why each modality is in the methods section.

=== "Intermediate"

    Goal: pick a pipeline / atlas / cohort that matches a specific clinical question.

    1. The disease page closest to your project (e.g. [Parkinson's](parkinsons-and-movement.md) for a DAT-SPECT study).
    2. The [Landmark → Reference datasets](../landmark/datasets.md) entry for the matching cohort (ADNI, PPMI, ENIGMA-X, ABCD).
    3. The pipeline page in [Landmark → Major pipelines](../landmark/pipelines.md) that emits the derivative you need (FreeSurfer, MELD, SAMSEG, fMRIPrep).

    By the end you can defend a "we used X biomarker on Y cohort because Z" sentence to a reviewer.

=== "PhD / specialist"

    Goal: contribute clinical methods — not just consume them.

    1. The primary biomarker papers cited on each disease page (Jack 2018, Klunk 2015, Langkammer 2016, Absinta 2019, van Erp 2018, Marek 2022, Spitzer 2022).
    2. The harmonisation literature — across tracers (Centiloid), across scanners (ComBat), across sites (ENIGMA pipelines). Each disease page flags its own harmonisation problem.
    3. The open-questions block at the foot of each page. That's where the field is moving; if your project is not in one of those buckets, ask why not.

    Specialists distinguish *what a biomarker measures* from *what the original validation study claimed*. The gap is where novel work happens.

## Cross-cutting themes

A few patterns recur across every disease in this section:

- **Multimodal beats unimodal.** Structural MRI + PET + fluid markers + clinical scales together outperform any single modality. The A/T/N framework formalised this; other diseases are catching up.
- **Harmonisation is the bottleneck.** Across scanners, tracers, sites. Most "novel ML model" papers in clinical neuroimaging are really harmonisation papers in disguise.
- **Effect sizes are bigger in neurology than in psychiatry.** A Parkinson's DAT-SPECT effect is unmissable; a depression sgACC effect needs thousands of subjects to see. This shapes study design.
- **Surgery and treatment selection drive the hardest imaging problems.** Epilepsy surgery, stroke thrombectomy windows, DBS targeting — these are where imaging directly chooses an intervention.

## What this section does *not* cover

- **Brain tumours / neuro-oncology.** BraTS, glioma grading, radiomics — important, but covered briefly in [Foundations → Neuroscience](../fundamentals/foundations/neuroscience.md) and deserve their own future chapter.
- **Pediatric / developmental disorders** beyond what shows up under epilepsy and psychiatry. dHCP-style developmental imaging is a methods topic, covered in [Landmark → Reference datasets](../landmark/datasets.md).
- **Day-to-day clinical radiology** — reporting workflows, PACS, billing. This handbook is research-flavoured.

## Where to next

If you came here from the methods side, pair each clinical chapter with the matching modality page in [Fundamentals → Sequences](../fundamentals/sequences/index.md). If you came here from the data side, pair with [Landmark → Reference datasets](../landmark/datasets.md) and [Landmark → Major pipelines](../landmark/pipelines.md). And if you want the broader scientific context, [Fundamentals → Neuroscience & neurology](../fundamentals/foundations/neuroscience.md) is the page these all build on.
