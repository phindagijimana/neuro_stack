# MP-RAGE (magnetization-prepared rapid gradient echo) — full course

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

## 11. Credible peer-reviewed papers

- Mugler JP 3rd, Brookeman JR. Three-dimensional magnetization-prepared rapid gradient-echo imaging (3D MP RAGE). *Magn Reson Med.* 1990;15(1):152–157. https://doi.org/10.1002/mrm.1910150117

- Marques JP, et al. MP2RAGE, a self bias-field corrected sequence for improved segmentation and T1-mapping at high field. *Neuroimage.* 2010;49(2):1271–1281. https://doi.org/10.1016/j.neuroimage.2010.07.024

## 12. Credible online resources

- FreeSurfer — recommended acquisitions

- mriquestions — MP-RAGE

## 13. References (sources used to create this content)

- Mugler & Brookeman — original MP-RAGE — https://doi.org/10.1002/mrm.1910150117

- Marques et al. — MP2RAGE — https://doi.org/10.1016/j.neuroimage.2010.07.024

- Vendor MPRAGE / MP2RAGE product manuals.

### Closing

Pair with GRE ( readout block), FLAIR ( inversion recovery concepts), and pipeline docs for segmentation tools used in the lab.