# MP-RAGE (magnetization-prepared rapid gradient echo) — full course

> The workhorse 3D T1-weighted structural scan. Every BIDS dataset has one because every downstream tool needs to know where grey matter is.

## What MPRAGE actually is

MP-RAGE = **M**agnetisation **P**repared **RA**pid **G**radient **E**cho. Two ideas glued together:

1. **Inversion-recovery preparation** to maximise T1 contrast — same family idea as [FLAIR](flair.md), but the goal here is grey-matter / white-matter discrimination, not lesion conspicuity. A 180° inversion pulse flips magnetisation, and after a tuned inversion time TI different tissues have recovered to different points on their T1 curves. Pick TI well and GM, WM, and CSF separate cleanly.
2. **A fast 3D spoiled gradient-echo readout** that captures the whole brain volume in ~5 min. Traditional spin-echo inversion-recovery for the same contrast and coverage would take ~20 min and be unusable for routine clinical or large-cohort research scans.

The result is a high-contrast 3D T1-weighted volume, typically 1 mm isotropic, that is sharp enough for surface reconstruction and consistent enough across sites to anchor every other modality. It is the workhorse of structural neuroimaging — Mugler & Brookeman introduced it in [1990](https://doi.org/10.1002/mrm.1910150117) and it has barely been displaced since.

For the physics building blocks underneath (inversion recovery, gradient echo, k-space), see [Foundations → Physics](../foundations/physics.md). For the contrast-engineering view across sequences, see the [Sequences index](index.md).

## Why every BIDS dataset has a T1w

Almost every downstream tool needs a T1w volume:

- **Registration target** — [fMRI / BOLD EPI](epi.md), [DWI](dwi.md), and [PET](pet.md) volumes are coregistered to the T1w because the T1w has the structural detail those modalities lack. The T1w → MNI warp ([ANTs](http://stnava.github.io/ANTs/), [SPM](https://www.fil.ion.ucl.ac.uk/spm/), [FSL FNIRT](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FNIRT)) is what puts everything else in a common space.
- **Atlas alignment** — applying any parcellation (Desikan-Killiany, HCP-MMP1, Schaefer; see [Foundations → Neuroscience](../foundations/neuroscience.md)) starts from the T1w-to-template transform.
- **Surface reconstruction** — [FreeSurfer](https://surfer.nmr.mgh.harvard.edu) `recon-all` and [FastSurfer](https://github.com/Deep-MI/FastSurfer) consume the T1w to build the cortical mesh, generate `aparc+aseg`, and compute cortical thickness.
- **Voxel-based morphometry** — any GM-density or volume analysis needs the T1w-derived tissue segmentation.
- **Defacing and de-identification** — face-removal pipelines ([pydeface](https://github.com/poldracklab/pydeface), `mri_reface`) operate on the T1w.

If you have one structural scan, you want it to be a T1w MPRAGE. Everything else assumes it exists. The BIDS spec ([Gorgolewski et al., 2016](https://doi.org/10.1038/sdata.2016.44)) makes this convention explicit: `sub-XX/anat/sub-XX_T1w.nii.gz` is the canonical anchor.

Course map: Inversion prep → k-space ordering → TI / TD → contrast mechanism → MP2RAGE unified T1 → artifacts → analysis outputs (surfaces, thickness, volumes) → how outputs are used → examples → references.

## 1. Learning objectives

- Explain why MP-RAGE combines inversion recovery with 3D spoiled GRE readout.

- Describe “view order” effects (linear vs elliptical centric) on effective contrast and motion sensitivity (conceptual).

- Contrast MP-RAGE T1w contrast from standard spoiled GRE T1w.

- Summarize MP2RAGE two inversion efficiencies for T1 map estimation and bias field correction (high level).

- List artifacts (B1 +, motion, incomplete inversion) specific to inversion-prepared 3D scans.

- Identify typical downstream files (FreeSurfer aparc+aseg, thickness GIFTI, stats tables) and one research use per output class.

## 2. Physics — building blocks

### 2.1 Inversion preparation

- 180° inversion ( non-selective or slab-selective — vendor dependent) creates T1 weighting before readout — similar spirit to FLAIR but goal is T1 contrast for GM/WM, not CSF null.

### 2.2 3D spoiled GRE readout

- Short TR, small flip angle RF spoiled GRE fills 3D k-space — fast volume coverage (GRE handout).

### 2.3 Contrast timing

- TI ( time inversion to k-space region of interest — definitions vary by vendor) sets where on T1 recovery curve central k-space is acquired → dominant image contrast.

## 3. Why MP-RAGE for T1w neuroanatomy

## 4. MP2RAGE (unified T1 mapping — conceptual)

- Two different inversion efficiencies ( two images) → algebraic combination yields T1 estimate robust to receive field bias (B1⁻ effects still matter).

- Used in research for quantitative T1 maps and high-contrast UNI-like images.

## 5. Acquisition parameters (typical ballparks)

## 6. Artifacts

- Motion between inversion and readout → ghosting / inconsistent contrast.

- B1 inhomogeneity → inhomogeneous inversion efficiency.

- Denoising / intensity non-uniformity — bias field correction in pipelines (FreeSurfer, ANTs).

## 7. Downstream: segmentation and morphometry (overview)

- FreeSurfer expects reasonable T1 contrast and resolution — check protocol compatibility documentation.

- MP2RAGE UNI images may need different intensity normalization than MPRAGE.

## 8. Analysis outputs, derivatives, and how they are used

### 8.1 Volumetric and label outputs (example: FreeSurfer-style)

### 8.2 Surface-based outputs

### 8.3 MP2RAGE-specific derivatives

### 8.4 Alternative pipelines (same inputs, different filenames)

- fast (FSL) → partial volume estimates PVE maps; first → GM/WM/CSF segmentation.

- ANTs Atropos / antsCorticalThickness → thickness + DK labels in ANTs naming.

- SynthSeg / FastSurfer → deep segmentation from T1 — different file layout but same scientific roles (parcellation → volumes / ROI means).

### 8.5 Mapping questions to outputs

## 9. Worked examples

### Example A — Contrast goal

- Shorter effective TI emphasis → different GM/WM ratio — why multisite studies harmonize protocols.

### Example B — Scan time

- 256³ matrix, partial Fourier, parallel imaging → tradeoff table in vendor manual.

## 10. Pitfalls

- Assuming all “MPRAGE” labels are identical — Siemens vs GE vs Philips differ in timing nomenclature.

- Using MP2RAGE without understanding UNI contrast — not the same as classic MPRAGE for visual QC habits.

## Medical / clinical relevance

**Beginner — what it's used for, in one sentence.** MPRAGE is the standard high-resolution 3D T1-weighted scan — the brain-anatomy backbone of nearly every neuro MRI exam.

### Routine clinical use

- **Anatomical reference** for every other sequence — DWI, FLAIR, fMRI, SWI, and PET are all coregistered to it because no other contrast resolves cortex, basal ganglia, and brainstem this cleanly at 1 mm isotropic.
- **FreeSurfer / FastSurfer / SynthSeg input** for cortical surfaces, `aparc+aseg`, subcortical volumes, and cortical thickness — the substrate for every structural biomarker downstream.
- **Surgical and neuromodulation planning** — DBS lead trajectory, tumour resection margins, epilepsy resection, focused-ultrasound targeting all key off the T1w volume.
- **Atlas registration and parcellation** — MNI, Desikan-Killiany, HCP-MMP, Schaefer, Yeo all reach a subject's brain through the T1w → template warp.
- **Pre- and post-gadolinium T1w** for blood-brain-barrier breakdown — tumour enhancement, active MS lesions, infection, vasculitis.

### Disease applications

| Disease | Imaging finding | Clinical value | Cross-link |
|---|---|---|---|
| Alzheimer's disease | Hippocampal and entorhinal atrophy; medial temporal lobe atrophy (MTA) score | Supports diagnosis (NIA-AA criteria); tracks progression; pre-screens for amyloid PET | [clinical/alzheimers-and-dementia.md](../../clinical/alzheimers-and-dementia.md) |
| Multiple sclerosis | T1 "black holes" — chronic hypointense lesions reflecting axonal loss | Predicts disability progression beyond T2 lesion count | [clinical/multiple-sclerosis.md](../../clinical/multiple-sclerosis.md) |
| Brain tumours (glioma, metastases) | Pre-contrast T1w for registration; post-contrast T1w for enhancing tumour | Standardised by BraTS / RANO criteria for response assessment | — |
| Mesial temporal sclerosis (epilepsy) | Hippocampal atrophy, loss of internal architecture on T1w volumetry | Lateralises temporal lobe epilepsy for surgical workup | [clinical/epilepsy.md](../../clinical/epilepsy.md) |
| Paediatric myelination | T1w GM/WM contrast reverses 6–12 months and matures by ~24 months | Detects delayed or arrested myelination, leukodystrophy screening | — |
| Parkinson's disease | Substantia nigra / midbrain morphometry, cortical thinning in advanced PD | Differentiates PD from atypical parkinsonism with multimodal MRI | [clinical/parkinsons-and-movement.md](../../clinical/parkinsons-and-movement.md) |

Seminal references for each row:

- Alzheimer's hippocampal atrophy: Frisoni GB, Fox NC, Jack CR Jr, Scheltens P, Thompson PM. The clinical use of structural MRI in Alzheimer disease. *Nat Rev Neurol.* 2010;6(2):67–77. [doi:10.1038/nrneurol.2009.215](https://doi.org/10.1038/nrneurol.2009.215).
- MS T1 black holes: van Walderveen MA, Kamphorst W, Scheltens P, et al. Histopathologic correlate of hypointense lesions on T1-weighted spin-echo MRI in multiple sclerosis. *Neurology.* 1998;50(5):1282–1288. [doi:10.1212/WNL.50.5.1282](https://doi.org/10.1212/WNL.50.5.1282).
- Tumour response (RANO / BT-RADS extension): Ellingson BM, Bendszus M, Boxerman J, et al. Consensus recommendations for a standardized brain tumor imaging protocol in clinical trials. *Neuro Oncol.* 2015;17(9):1188–1198. [doi:10.1093/neuonc/nov095](https://doi.org/10.1093/neuonc/nov095).
- Hippocampal volumetry in TLE: Bernasconi N, Bernasconi A, Caramanos Z, Antel SB, Andermann F, Arnold DL. Mesial temporal damage in temporal lobe epilepsy: a volumetric MRI study of the hippocampus, amygdala and parahippocampal region. *Brain.* 2003;126(2):462–469. [doi:10.1093/brain/awg250](https://doi.org/10.1093/brain/awg250).
- Paediatric myelination on T1w: Barkovich AJ. MR imaging of the neonatal brain. *Radiology.* 2006;241(1):14–34. [doi:10.1148/radiol.2391050316](https://doi.org/10.1148/radiol.2391050316).

### Research depth

Most current methodological work on MPRAGE is about **acquisition acceleration and quantitative substitutes**. Deep-learning-synthesised MPRAGE from under-sampled k-space, variable-flip-angle (VFA) acquisitions, and SynthMPRAGE-style cross-modal estimators (Iglesias et al., SynthSR) collapse 5-minute MPRAGE protocols toward sub-minute scans without losing FreeSurfer-compatible contrast — important for paediatric, intra-operative, and motion-prone populations. **MP2RAGE** (Marques 2010) and its companions (MP3RAGE, FLAWS) recover a self-bias-corrected unified T1 image plus a quantitative T1 map in a single acquisition, which is now the de facto 7 T anatomical scan and a research-grade myelination biomarker. At ultra-high field, MP2RAGE at 0.5–0.7 mm enables **laminar cortical imaging** — mapping cortical layers within the ~3 mm ribbon — opening structural correlates of layer-specific microcircuitry in psychiatry and small-vessel disease research.

The other major research thread is **MPRAGE as a phenotype** — UK Biobank, ADNI, ABCD, HCP all pivot on the T1w volume. Harmonisation across vendors (ComBat, neuroHarmonize), longitudinal stability of FreeSurfer / SAMSEG outputs, and the reproducibility crisis around cortical thickness estimates (Madan 2019, Bhagwat 2021) are active controversies. Quantitative T1 maps derived from MP2RAGE or MPM protocols (Weiskopf 2013) are emerging as **myelin-sensitive biomarkers** in MS, schizophrenia, and ageing — see also [qmri.md](./qmri.md) for the broader quantitative-T1 / T2 / PD landscape, and [tools/index.md](../../tools/index.md) for FreeSurfer, FastSurfer, and SAMSEG implementations.

## 11. Credible peer-reviewed papers

- Mugler JP 3rd, Brookeman JR. Three-dimensional magnetization-prepared rapid gradient-echo imaging (3D MP RAGE). *Magn Reson Med.* 1990;15(1):152–157. https://doi.org/10.1002/mrm.1910150117

- Marques JP, et al. MP2RAGE, a self bias-field corrected sequence for improved segmentation and T1-mapping at high field. *Neuroimage.* 2010;49(2):1271–1281. https://doi.org/10.1016/j.neuroimage.2010.07.024

## 12. Credible online resources

- FreeSurfer — recommended acquisitions

- mriquestions — MP-RAGE

## 13. References (sources used to create this content)

- Mugler & Brookeman — original MP-RAGE — https://doi.org/10.1002/mrm.1910150117

- Marques et al. — MP2RAGE — https://doi.org/10.1016/j.neuroimage.2010.07.024

- Gorgolewski KJ, Auer T, Calhoun VD, et al. The brain imaging data structure (BIDS), a format for organizing and describing outputs of neuroimaging experiments. *Sci Data.* 2016;3:160044. [doi:10.1038/sdata.2016.44](https://doi.org/10.1038/sdata.2016.44)

- Vendor MPRAGE / MP2RAGE product manuals.

### Closing

Pair with GRE ( readout block), FLAIR ( inversion recovery concepts), and pipeline docs for segmentation tools used in the lab.