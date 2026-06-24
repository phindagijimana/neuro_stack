# FLAIR (fluid-attenuated inversion recovery) — full course

Course map: Inversion recovery → CSF null → parameters → artifacts → vs T2w → analysis outputs (lesion masks, ratings) → how outputs are used → examples → references.

## 1. Learning objectives

- Write longitudinal magnetization recovery after a 180° inversion and identify TI where Mz = 0 for CSF ( conceptual null).

- Explain why FLAIR shows T2-like lesion contrast while suppressing CSF signal.

- Compare 2D slice-selective FLAIR vs 3D SPACE / CUBE-style FLAIR tradeoffs.

- Recognize incomplete CSF suppression and flow artifacts on FLAIR.

## 2. Physics — inversion recovery

### 2.1 Inversion pulse

- 180° inversion flips Mz to −M₀. Tissues recover toward +M₀ at rates governed by T1.

### 2.2 Null time (TI)

- Mz(TI) = M₀ (1 − 2 e^(−TI/T1)) for ideal instantaneous inversion ( simplified model).

- Null when Mz = 0 → TI_null ≈ T1 ln(2) for that tissue ( approximate starting point — actual protocols tune TI for field strength and sequence details).

### 2.3 CSF suppression

- CSF has long T1 (~ 3000–4500 ms at 1.5 T, field-dependent). TI chosen so CSF signal is near null at excitation → dark CSF on image.

### 2.4 Readout

- After TI, 90° excitation tips remaining longitudinal magnetization into transverse plane → TSE readout yields T2-weighted contrast for non-null tissues.

## 3. Why FLAIR is not “just T2w”

## 4. Acquisition parameters

## 5. 2D vs 3D FLAIR

- 2D FLAIR: Slice-selective inversion / excitation — robust, per-slice timing; CSF flow can vary by slice.

- 3D FLAIR (e.g., SPACE, CUBE, VISTA): Isotropic high resolution; long acquisitions; reformat planes — great for small lesions detection when SNR allows.

## 6. Artifacts

- Incomplete CSF suppression: wrong TI, B1 inhomogeneity, patient motion between inversion and readout.

- Flow artifacts: CSF pulsation / flow in cisterns.

- SAR: long TR / many RF pulses at 3 T.

## 7. Clinical and research contexts

## 8. Analysis outputs, derivatives, and how they are used

### 8.1 Image-level outputs

### 8.2 Lesion and abnormality maps

### 8.3 Mapping research questions to FLAIR-derived measures

### 8.4 Multimodal dependencies

- Lesion segmentation is more reliable when T1 provides anatomical prior — joint T1+FLAIR models (SynthSeg, SAMSEG, custom CNNs) output label maps in T1 space after registration**.

## 9. Worked examples

### Example A — Null condition (order of magnitude)

- If T1_CSF ≈ 4000 ms, TI_null ≈ T1 ln(2) ≈ 2770 ms — illustrative only; scanner presets differ.

### Example B — TR constraint

- TI = 2500 ms, readout + spoiling ≈ 2000 ms → TR must be ≥ 4500 ms ( simplified timing budget).

## 10. Pitfalls

- Comparing FLAIR across sites without noting TI, TE, resolution — appearance changes.

- Confusing FLAIR hyperintensity with T2 alone — pathology also depends on T1 recovery into readout.

## Medical / clinical relevance

**Beginner — what it's used for, in one sentence.** FLAIR shows white-matter lesions on a CSF-suppressed background — it is the sequence MS, vascular dementia, and infection diagnosis depend on.

### Routine clinical use

- **Multiple sclerosis workup** — FLAIR is *the* sequence in the 2017 McDonald criteria for dissemination in space and time; 3D-FLAIR is now standard for lesion counting and brainstem / spinal-cord lesions.
- **Vascular small-vessel disease** — white-matter hyperintensity (WMH) burden on FLAIR is the routine quantitative biomarker for cerebral small-vessel disease, used in dementia, stroke risk stratification, and trial endpoints (STRIVE criteria).
- **Encephalitis** — limbic encephalitis, herpes simplex encephalitis, autoimmune (anti-LGI1, anti-NMDAR) encephalitis all hinge on mesial temporal FLAIR hyperintensity.
- **Post-stroke gliosis and chronic infarct mapping** — FLAIR distinguishes chronic from acute lesions when paired with DWI.
- **Peritumoural oedema vs infiltrative tumour** — FLAIR signal extent is part of RANO criteria for glioma response assessment, especially for non-enhancing tumour burden.
- **Status epilepticus** — peri-ictal cortical FLAIR hyperintensity supports the diagnosis when EEG is inconclusive.

### Disease applications

| Disease | Imaging finding | Clinical value | Cross-link |
|---|---|---|---|
| Multiple sclerosis | Periventricular, juxtacortical, infratentorial T2/FLAIR lesions | McDonald 2017 dissemination in space/time; lesion counting | [clinical/multiple-sclerosis.md](../../clinical/multiple-sclerosis.md) |
| Cerebral small-vessel disease (CSVD) | Periventricular and deep WM hyperintensities (Fazekas / WMH-volume) | Quantifies vascular contribution to cognitive impairment | — |
| Limbic / autoimmune encephalitis | Mesial temporal lobe (hippocampus, amygdala) FLAIR hyperintensity | Supports anti-LGI1 / anti-NMDAR diagnosis when antibody pending | — |
| Glioblastoma / glioma | Peritumoural FLAIR hyperintensity = oedema + infiltrative tumour | Distinguishes vasogenic oedema from non-enhancing tumour for RANO | — |
| Neonatal hypoxic-ischaemic encephalopathy | Basal ganglia / thalamic FLAIR signal abnormality | Prognostic biomarker for neurodevelopmental outcome | — |
| Status epilepticus | Cortical and subcortical FLAIR signal (peri-ictal) | Supports diagnosis when EEG ambiguous; tracks resolution | [clinical/epilepsy.md](../../clinical/epilepsy.md) |

Seminal references for each row:

- McDonald 2017 criteria: Thompson AJ, Banwell BL, Barkhof F, et al. Diagnosis of multiple sclerosis: 2017 revisions of the McDonald criteria. *Lancet Neurol.* 2018;17(2):162–173. [doi:10.1016/S1474-4422(17)30470-2](https://doi.org/10.1016/S1474-4422(17)30470-2).
- STRIVE / CSVD reporting: Wardlaw JM, Smith EE, Biessels GJ, et al. Neuroimaging standards for research into small vessel disease and its contribution to ageing and neurodegeneration. *Lancet Neurol.* 2013;12(8):822–838. [doi:10.1016/S1474-4422(13)70060-7](https://doi.org/10.1016/S1474-4422(13)70060-7).
- Autoimmune encephalitis: Graus F, Titulaer MJ, Balu R, et al. A clinical approach to diagnosis of autoimmune encephalitis. *Lancet Neurol.* 2016;15(4):391–404. [doi:10.1016/S1474-4422(15)00401-9](https://doi.org/10.1016/S1474-4422(15)00401-9).
- FLAIR for tumour / oedema differentiation: Eidel O, Burth S, Neumann JO, et al. Tumor infiltration in enhancing and non-enhancing parts of glioblastoma: a correlation with histopathology. *PLoS One.* 2017;12(1):e0169292. [doi:10.1371/journal.pone.0169292](https://doi.org/10.1371/journal.pone.0169292).
- Neonatal HIE on FLAIR/T2: Barkovich AJ, Hajnal BL, Vigneron D, et al. Prediction of neuromotor outcome in perinatal asphyxia: evaluation of MR scoring systems. *AJNR Am J Neuroradiol.* 1998;19(1):143–149.
- Peri-ictal FLAIR changes: Cole AJ. Status epilepticus and periictal imaging. *Epilepsia.* 2004;45(Suppl 4):72–77.

### Research depth

The methodological frontier on FLAIR is **derived contrasts and lesion segmentation**. **FLAIR\*** combines FLAIR with T2\* in a multiplicative weighting that sharply emphasises the **central vein sign** — pathognomonic for MS lesions versus mimics (CSVD, migraine, NMOSD) and adopted into the 2024 MAGNIMS-NAIMS criteria refresh ([Sati 2016](https://doi.org/10.1038/nrneurol.2016.166)). **FLAIR²** (Wiggermann 2016) computes FLAIR² = T2-weighted × FLAIR², improving lesion-to-WM contrast for small cortical and infratentorial MS lesions. **3D-FLAIR** (SPACE, CUBE, VISTA) with 1 mm isotropic resolution is now the de facto MS / dementia research standard, displacing 2D-FLAIR at high-volume MS centres because of higher infratentorial sensitivity and better reformatting for tractography ROIs.

Deep-learning **FLAIR lesion segmentation** is the most clinically advanced AI application in neuroradiology. Tools in active clinical use include **[LST / LST-AI](https://www.applied-statistics.de/lst.html)** for MS lesion counts, **[SAMSEG](https://surfer.nmr.mgh.harvard.edu/fswiki/Samseg)** (joint anatomical + lesion segmentation), **icobrain**, **QyScore**, and **mdbrain** — all FDA / CE-cleared in some markets — and research-tier **nnU-Net** and **MedNeXt** pipelines that consistently beat per-rater inter-observer variability on public challenges (MICCAI MSSEG, WMH 2017). See [tools/index.md](../../tools/index.md) for the broader segmentation tooling landscape and [analysis/structural.md](../../analysis/structural.md) for the FLAIR-WMH → SVD-pathway analysis chain. WMH harmonisation across scanners and field strengths remains an open problem; ENIGMA-WMH and the multi-site WMH-2017 challenge are the reference benchmarks.

## 11. Credible peer-reviewed papers

- Bydder GM, Young IR. MR imaging: digital subtraction angiography using moment nulled inversion recovery. *Radiology.* 1985;157(3):657–658. https://doi.org/10.1148/radiology.157.3.4059555

- Hajnal JV, et al. Use of fluid attenuated inversion recovery (FLAIR) pulse sequences in MRI of the brain. *J Comput Assist Tomogr.* 1992;16(6):841–844. https://doi.org/10.1097/00004728-199211000-00001

## 12. Credible online resources

- mriquestions — FLAIR

- Radiopaedia — FLAIR

## 13. References (sources used to create this content)

- mriquestions.com — inversion recovery and FLAIR — https://mriquestions.com/

- Bernstein MA, et al. *Handbook of MRI Pulse Sequences* — inversion recovery chapter.

- Vendor FLAIR product manuals — TI presets by field strength.

### Closing

Pair with DWI ( acute stroke), T2 TSE ( alternative contrast), and post-contrast T1 ( tumor protocols).