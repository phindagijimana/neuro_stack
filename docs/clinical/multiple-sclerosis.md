# Multiple sclerosis

> A disease defined and tracked by MRI. The clearest example of a disorder where imaging biomarkers are also the diagnostic criteria and the trial endpoints.

Multiple sclerosis (MS) is the disease where MRI has the longest unbroken history as both diagnostic instrument and outcome measure. The McDonald criteria for diagnosis are MRI criteria. Disease-activity monitoring on therapy is MRI. Trial endpoints are MRI lesion counts and brain-volume change. And the recent additions — central vein sign, paramagnetic rim lesions, quantitative myelin imaging — are reshaping how the field defines both the disease and the response to treatment.

For the underlying demyelination biology, periventricular lesion distribution, and McDonald-criteria vocabulary, see [Fundamentals → Neuroscience & neurology](../fundamentals/foundations/neuroscience.md).

## Clinical picture

### Phenotypes

- **Relapsing-remitting MS (RRMS)** — most common (~85% at onset). Discrete neurological episodes (relapses) followed by partial or complete recovery.
- **Secondary progressive MS (SPMS)** — gradual disability accrual after an initial relapsing course.
- **Primary progressive MS (PPMS)** — gradual progression from onset, without distinct relapses (~10–15%).
- **Clinically isolated syndrome (CIS)** — first demyelinating event; often progresses to MS.
- **Radiologically isolated syndrome (RIS)** — incidental MRI findings consistent with MS without clinical events.

### McDonald criteria — diagnosis is MRI

The current [McDonald 2017 criteria](https://doi.org/10.1016/S1474-4422(17)30470-2) (Thompson et al.) require **dissemination in space (DIS)** — lesions in ≥ 2 of 4 typical locations (periventricular, juxtacortical, infratentorial, spinal cord) — and **dissemination in time (DIT)** — simultaneous gadolinium-enhancing and non-enhancing lesions, or new lesions on follow-up, *or* CSF oligoclonal bands.

This is a diagnostic framework in which imaging carries most of the weight.

## Lesion imaging

The bread-and-butter MS sequences.

| Sequence | What it shows | Use |
|---|---|---|
| **T2 / FLAIR** | All MS lesions, T2-hyperintense | Lesion count, volume, DIS criterion |
| **T1 post-Gd** | Acute / sub-acute (active) lesions | DIT criterion; treatment response |
| **T1 (unenhanced)** | "Black holes" — chronic T1-hypointense lesions associated with axonal loss | Chronic disability marker |
| **3D FLAIR** | Higher resolution for juxtacortical / leptomeningeal | Increasingly the standard |
| **DIR (double inversion recovery)** | Cortical lesions | Specialist; cortical lesions are common but classical FLAIR misses them |
| **SWI / phase imaging** | Iron-rich rims around lesions | PRL detection (see below) |
| **FLAIR\*** (FLAIR + T2*) | Central vein sign | CVS detection |

### Lesion distribution

Periventricular, juxtacortical, infratentorial (brainstem, cerebellum), and spinal cord. The classical "Dawson's fingers" on FLAIR are periventricular lesions oriented along medullary veins — a hint at the perivenular nature of MS pathology that the central vein sign formalises.

### Lesion segmentation pipelines

| Tool | Notes |
|---|---|
| **SAMSEG (FreeSurfer)** | Joint segmentation of brain tissue + lesions; widely adopted |
| **LST / LST-AI** | SPM-based lesion segmentation toolbox; longstanding standard |
| **BIANCA (FSL)** | k-NN-based lesion segmentation |
| **nicMSlesions** | Deep-learning multi-channel lesion segmentation |
| **Mass-univariate FLAIR thresholding** | Quick baseline; quality varies |
| **icobrain MS, mdbrain** | Commercial/clinical-grade tools |
| **DeepLesionBrain, nnU-Net variants** | Recent open DL pipelines |

## Central vein sign (CVS)

The single most specific imaging feature for distinguishing MS from MS-mimickers (microvascular disease, NMO, MOGAD).

[Sati et al., 2016](https://doi.org/10.1038/nrneurol.2016.166) (NAIMS consortium) established CVS as a research biomarker; the proportion of lesions with a central vein on FLAIR\* (or T2\*-weighted susceptibility-sensitive sequences) is much higher in MS than in mimickers. Practical thresholds:

- **40% rule** — ≥ 40% of lesions show CVS suggests MS.
- **Select-3 / Select-6** — simplified rules counting CVS-positive lesions among 3 or 6 picked lesions.

3T or 7T with optimised FLAIR\* is needed; routine clinical 1.5T struggles.

## Paramagnetic rim lesions (PRLs)

A second susceptibility-based MS biomarker. [Absinta et al., 2019](https://doi.org/10.1001/jamaneurol.2019.2399) showed that lesions with iron-laden microglia at the chronic-active rim — visible as paramagnetic (dark) rims on SWI / QSM — are associated with worse disability and faster disability accumulation.

PRLs are interpreted as markers of **smouldering inflammation** — the slow, chronic-active pathology that disease-modifying therapies have historically failed to address. They are the leading candidate biomarker for progressive disease activity.

For susceptibility-imaging physics, see [Fundamentals → SWI](../fundamentals/sequences/swi.md).

## Spinal cord imaging

Spinal cord disease accounts for substantial MS disability. Cervical cord lesions are common; thoracic less so but specific.

Practical issues: cord motion, small cross-section, CSF pulsation artefact. Dedicated 3D phase-sensitive inversion recovery (PSIR) or STIR sequences are recommended. Spinal cord atrophy (cervical cord cross-sectional area) is an active disability-progression biomarker (Spinal Cord Toolbox).

## Brain atrophy

Whole-brain atrophy in MS proceeds at ~0.5–1.0% per year — about double the healthy rate. Atrophy correlates with long-term disability better than lesion load.

| Tool | Use |
|---|---|
| **SIENA (FSL)** | Percent brain volume change between two timepoints |
| **SIENAX** | Cross-sectional normalised brain volume |
| **FreeSurfer / FastSurfer** | Regional cortical / subcortical volumes |
| **icobrain MS, MSmetrix** | Commercial clinical reporting |

Deep grey matter (thalamus especially) is now thought to be a particularly sensitive marker, both early and progressive.

## Disease activity on therapy

Treatment-response monitoring is the most clinically routine MRI use after diagnosis. The composite **NEDA-3** (No Evidence of Disease Activity) endpoint:

1. No relapses.
2. No disability progression.
3. No new T2 / Gd-enhancing lesions.

NEDA-4 adds normalised brain volume loss < 0.4%/year. NEDA is now a routine treatment-success criterion.

## Quantitative myelin imaging

Conventional MS imaging detects lesions; quantitative myelin imaging tries to measure the underlying tissue substance.

| Method | What it measures | Notes |
|---|---|---|
| **MTR (magnetisation transfer ratio)** | Macromolecular pool fraction proxy | Quick, robust; semi-quantitative |
| **MTsat (magnetisation transfer saturation)** | More robust to B1 inhomogeneity than MTR | Replacing MTR in research protocols |
| **qMT (quantitative magnetisation transfer)** | Pool size ratios, exchange rates | Most fully quantitative; complex |
| **MWF (myelin water fraction)** | Multi-component T2 — myelin water signal | Most specific but motion / time-intensive |
| **g-ratio mapping** | Combined qMT + DWI; axon-to-fibre ratio | Research |
| **T1 mapping, T2 mapping** | Tissue-level relaxometry | qMRI fundamentals |

These are covered in [Fundamentals → Quantitative MRI](../fundamentals/sequences/qmri.md).

The clinical use case is **remyelination imaging** — quantifying whether tissue is remyelinating spontaneously or under therapy. Trials of remyelinating agents (clemastine, opicinumab) use MWF / MTsat as candidate endpoints.

## Datasets

| Dataset | Description |
|---|---|
| **MICCAI MS lesion segmentation challenges** | 2008 (Boston), 2015 (ISBI), 2016, ongoing — benchmarks for lesion seg |
| **MSSEG / MSSEG-2** | French multi-site MS challenge data |
| **MS-LIA / MS Lesion Image Analysis** | Open MS reference cohorts |
| **OFSEP** | French MS cohort registry, growing imaging arm |
| **ENIGMA-MS** | Meta-analytic structural cohort |
| **ADNI-MS-analog cohorts** | Various national longitudinal MS cohorts |
| **OpenMS / OpenNeuro MS sets** | Public BIDS datasets |

## Open questions

- **Progressive-disease biomarkers.** RRMS treatment works; PPMS / SPMS treatment is much weaker. PRLs, smouldering inflammation, spinal-cord atrophy, deep-grey atrophy — which combination best tracks progression?
- **Remyelination imaging endpoints.** For remyelination trials, what's the right myelin metric — MWF, MTsat, qMT? Sensitivity and trial-timescale feasibility are unsettled.
- **Automated CVS / PRL detection.** Both biomarkers are currently labour-intensive to score; deep-learning detection is an active area.
- **NMOSD / MOGAD differential.** Imaging features that reliably separate MS from antibody-mediated demyelinating disorders matter increasingly as those disorders get specific therapies.
- **Spinal-cord imaging at scale.** Standardised cord protocols, automated CSA, cord-lesion segmentation — Spinal Cord Toolbox is the open infrastructure but adoption is uneven.
- **Cortical lesion detection.** Cortical lesions are common in MS and correlate with disability, but conventional FLAIR misses them. DIR, 7T phase imaging, and ML-augmented detection are active.
- **Pediatric MS imaging.** Pediatric-onset MS has different baseline imaging features and disease course.
- **Patient-specific lesion-evolution models.** Predicting which lesion will become a "black hole" or PRL is unsettled.

## References

1. **Absinta M, Sati P, Masuzzo F, et al.** Association of chronic active multiple sclerosis lesions with disability in vivo. *JAMA Neurol.* 2019;76(12):1474-1483. [doi:10.1001/jamaneurol.2019.2399](https://doi.org/10.1001/jamaneurol.2019.2399)
2. **Sati P, Oh J, Constable RT, et al.** The central vein sign and its clinical evaluation for the diagnosis of multiple sclerosis: a consensus statement from the North American Imaging in Multiple Sclerosis Cooperative. *Nat Rev Neurol.* 2016;12(12):714-722. [doi:10.1038/nrneurol.2016.166](https://doi.org/10.1038/nrneurol.2016.166)
3. **Thompson AJ, Banwell BL, Barkhof F, et al.** Diagnosis of multiple sclerosis: 2017 revisions of the McDonald criteria. *Lancet Neurol.* 2018;17(2):162-173. [doi:10.1016/S1474-4422(17)30470-2](https://doi.org/10.1016/S1474-4422(17)30470-2)
4. **Filippi M, Bar-Or A, Piehl F, et al.** Multiple sclerosis. *Nat Rev Dis Primers.* 2018;4:43. [doi:10.1038/s41572-018-0041-4](https://doi.org/10.1038/s41572-018-0041-4)
5. **Cerri S, Puonti O, Meier DS, et al.** A contrast-adaptive method for simultaneous whole-brain and lesion segmentation in multiple sclerosis. *NeuroImage.* 2021;225:117471. [doi:10.1016/j.neuroimage.2020.117471](https://doi.org/10.1016/j.neuroimage.2020.117471) (SAMSEG-MS)
6. **Smith SM, Zhang Y, Jenkinson M, et al.** Accurate, robust, and automated longitudinal and cross-sectional brain change analysis. *NeuroImage.* 2002;17(1):479-489. [doi:10.1006/nimg.2002.1040](https://doi.org/10.1006/nimg.2002.1040) (SIENA)
7. **De Stefano N, Stromillo ML, Giorgio A, et al.** Establishing pathological cut-offs of brain atrophy rates in multiple sclerosis. *J Neurol Neurosurg Psychiatry.* 2016;87(1):93-99. [doi:10.1136/jnnp-2014-309903](https://doi.org/10.1136/jnnp-2014-309903)
8. **Mancini M, Karakuzu A, Cohen-Adad J, et al.** An interactive meta-analysis of MRI biomarkers of myelin. *eLife.* 2020;9:e61523. [doi:10.7554/eLife.61523](https://doi.org/10.7554/eLife.61523)
9. **Carass A, Roy S, Jog A, et al.** Longitudinal multiple sclerosis lesion segmentation: resource and challenge. *NeuroImage.* 2017;148:77-102. [doi:10.1016/j.neuroimage.2016.12.064](https://doi.org/10.1016/j.neuroimage.2016.12.064)
10. **Maggi P, Sati P, Nair G, et al.** Paramagnetic rim lesions are specific to MS. *Ann Neurol.* 2020;88(5):1034-1042. [doi:10.1002/ana.25877](https://doi.org/10.1002/ana.25877)

## Where to next

- For susceptibility / SWI physics underlying CVS and PRL detection, see [Fundamentals → SWI](../fundamentals/sequences/swi.md).
- For quantitative myelin imaging (MTR, MTsat, qMT, MWF), see [Fundamentals → Quantitative MRI](../fundamentals/sequences/qmri.md).
- For FLAIR / structural sequence fundamentals, see [Fundamentals → FLAIR](../fundamentals/sequences/flair.md).
- For the broader cohort / dataset context, see [Landmark → Reference datasets](../landmark/datasets.md).
- For FreeSurfer / SAMSEG and segmentation infrastructure, see [Landmark → Major pipelines](../landmark/pipelines.md).
