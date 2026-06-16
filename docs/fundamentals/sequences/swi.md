# SWI (susceptibility-weighted imaging) — full course

Course map: Susceptibility physics → GRE long TE → phase images → mIP / filtered products → analysis outputs (SWI, R2*, QSM) → how outputs are used → artifacts → QSM bridge → examples → references.

## 1. Learning objectives

- Explain why veins and iron deposits alter local magnetic field and create signal and phase patterns on GRE.

- Describe how SWI combines magnitude and high-pass filtered phase to emphasize susceptibility sources.

- Differentiate SWI venous maps from QSM (quantitative susceptibility mapping) goals and pipelines.

- Recognize motion, incomplete flow compensation, and aliasing in phase images.

## 2. Physics — susceptibility and GRE

### 2.1 Local field offsets

- Tissue susceptibility χ differences ( deoxygenated hemoglobin in veins, iron, calcium) create ΔB inside and outside structures — dipole patterns in phase images.

### 2.2 Magnitude vs phase

- Magnitude GRE at long TE → T2* weighting → veins dark ( blood susceptibility) and iron regions signal loss.

- Phase accumulates along B₀ as spins precess at offset frequencies → structured patterns around sources.

### 2.3 SWI combination (typical)

- High-pass filter phase ( remove slowly varying background) → multiply with magnitude (or similar contrast scheme — vendor specific) → enhance fine susceptibility structures.

## 3. Acquisition (typical themes)

## 4. Clinical and research uses

## 5. SWI vs QSM

- SWI: Qualitative contrast optimized for radiological interpretation and vein visibility.

- QSM: Inverse problem from phase → χ map (ppm) — quantitative group studies, iron longitudinal tracking — separate pipelines (STI, MEDI, etc.).

## 6. Analysis outputs, derivatives, and how they are used

### 6.1 Vendor / reconstruction outputs

### 6.2 Quantitative chains (often multi-echo GRE, not SWI alone)

### 6.3 Mapping questions to SWI-family outputs

## 7. Artifacts

- Motion between echoes or segments → phase errors.

- Wrap / aliasing in phase unwrapping steps (QSM pipelines).

- Incomplete background field removal → residual low frequency bias.

## 8. Worked examples

### Example A — TE choice

- TE = 20 ms vs 40 ms at 3 T — longer TE increases phase contrast ∝ TE (first-order) but reduces magnitude SNR.

### Example B — Vein signal

- Deoxyhemoglobin Δχ → local field gradient → intra-voxel dephasing → dark veins on magnitude.

## 9. Pitfalls

- Confusing SWI hypointensity with calcification without CT / sequence correlation.

- Using SWI as quantitative iron measure — prefer R2* / QSM for quantification.

## 10. Credible peer-reviewed papers

- Haacke EM, et al. Improved MR venography: susceptibility weighted imaging. *Magn Reson Med.* 2004;52(4):818–824. https://doi.org/10.1002/mrm.20200

- Reichenbach JR, et al. High-resolution MR venography of the brain at 3 Tesla. *J Comput Assist Tomogr.* 2002;26(6):867–873. https://doi.org/10.1097/00004728-200211000-00019

## 11. Credible online resources

- mriquestions — SWI

- Radiopaedia — SWI

## 12. References (sources used to create this content)

- Haacke EM, et al. *Magnetic Resonance Imaging* — SWI and phase imaging chapters.

- Haacke et al. 2004 — SWI — https://doi.org/10.1002/mrm.20200

- Vendor SWI product manuals.

### Closing

Pair with GRE ( sequence family), T2* mapping / R2* literature for quantitative susceptibility work, and QSM pipelines when lab adopts them.