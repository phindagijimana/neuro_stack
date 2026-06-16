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