# Echo-planar imaging (EPI) — full course

Course map: Physics → k-space trajectory → parameters → artifacts & correction → fMRI / DWI pipelines → analysis outputs & derivatives → how outputs are used → clinical uses → worked examples → pitfalls → references.

## 1. Learning objectives

By the end of this handout you should be able to:

- Explain why EPI is used for fast 2D imaging and how single-shot readout differs from line-by-line spin-echo imaging.

- Name the main acquisition parameters (TR, TE, bandwidth, parallel imaging, multiband) and describe their trade-offs for SNR, distortion, and temporal resolution.

- Identify susceptibility distortion, Nyquist ghosting, and chemical shift in EPI and know which correction tools address them.

- List preprocessing steps that touch EPI in fMRI (motion, slice-time, topup/fieldmaps) and DWI (eddy).

- Document BIDS fields needed for unwarping and reproducibility.

- Name typical first- and second-level fMRI derivatives (motion TSV, betas, group z-maps) and DWI derivatives (FA, tract files) and state how they feed group stats or clinical decisions.

## 2. What EPI is (conceptual foundation)

### 2.1 The problem EPI solves

- Standard 2D Fourier imaging acquires one phase-encoding line per TR. For 128×128 pixels, that is 128 TRs per slice — far too slow for whole-brain fMRI at ~1–2 s per volume.

- Echo-planar imaging (EPI) fills most of k-space after one (or a few) RF excitation(s) by rapidly alternating the frequency-encoding (readout) gradient and applying small phase-encoding blips between echoes.

- Single-shot EPI acquires an entire 2D slice in tens of milliseconds — short enough to freeze much physiological motion for that slice (though between-slice and head motion remain).

### 2.2 Relationship to GRE and T2*

- The readout is gradient-echo-like: there is no 180° refocusing pulse during the EPI train (unless combined in diffusion prepulses). Signal decays with T2* within the echo train.

- Longer total readout → more T2* decay → signal loss and blurring in the phase-encode** direction.

### 2.3 Where EPI is used in neuroimaging

## 3. k-space trajectory in EPI

### 3.1 Zigzag path

- After slice-selective excitation, the readout gradient dephases then rephases to the echo; frequency encoding moves along k_x (or equivalent axis).

- Phase-encoding blips step k_y (or k_z for blipped 3D variants). The trajectory is often zigzag (alternating readout direction) or spiral-like variants (depending on product).

- Echo spacing (ES) — time between adjacent echoes in the train — is a key parameter: longer ES increases T2* loss and often worsens effective resolution in the phase-encode direction.

### 3.2 Single-shot vs multi-shot

- Single-shot: entire k_y extent in one train — fast, motion-robust slice-wise; long readout → distortion and signal attenuation.

- Multi-shot: k-space split across shots — can reduce distortion per shot but increases motion sensitivity and phase errors between shots.

### 3.3 Readout bandwidth

- Receiver bandwidth (BW) — kHz/pixel or Hz/pixel per vendor — wider BW → shorter readout window per line → less blurring from T2* during readout, but more noise in the receiver (noise bandwidth increases).

## 4. Acquisition parameters (detailed)

### 4.1 fMRI (BOLD) GRE-EPI — typical themes

Field strength: T2* and susceptibility scale with B₀; optimal TE and distortion severity differ 1.5 T vs 3 T vs 7 T.

### 4.2 DWI-EPI — additional parameters

## 5. Artifacts and distortions

### 5.1 Susceptibility-induced geometric distortion

- B₀ inhomogeneity near air–tissue interfaces ( sinuses, ear canals, orbitofrontal cortex) causes mis-mapping of signal along the phase-encode direction — stretch or compress anatomy.

- Stronger at higher B₀; worse with long readout time ( more k_y steps at fixed ES).

### 5.2 Correction strategies

- Field map from dual-echo GRE — estimates ΔB₀ for unwarping to T1.

- FSL topup — uses paired acquisitions with opposite phase-encoding polarity (blip-up / blip-down) to estimate distortion field.

- Document PhaseEncodingDirection, TotalReadoutTime or EffectiveEchoSpacing in BIDS.

### 5.3 Nyquist ghosting

- Asymmetry between odd and even echoes (timing, eddy currents) creates replicate images shifted in phase-encode direction. Phase correction in reconstruction reduces ghosts.

### 5.4 Chemical shift

- Fat–water frequency difference causes misregistration in readout direction — relevant near skull and marrow.

### 5.5 Multiband leakage

- Simultaneous excitation of slices can cause signal cross-talk if reconstruction is imperfect — inspect QC plots from reconstruction pipeline.

## 6. BOLD fMRI — analysis pipeline (overview)

- Drop dummy TRs (equilibration).

- Slice-time correction — align slice times within TR.

- Motion realignment — rigid 6 DOF; scrub or censor spikes.

- Susceptibility distortion correction — fieldmap or topup.

- Coregistration — mean EPI to T1; then normalization to template (workflow-dependent).

- GLM — task + nuisance regressors (motion, WM/CSF, compCorr, optional ICA-AROMA).

- Inference — cluster permutation or TFCE; multiple comparisons correction.

### 6.1 First-level outputs (typical derivatives)

These are not raw DICOM; they are what pipelines produce after preprocessing (names vary by fMRIPrep, FSL FEAT, AFNI, SPM, Nilearn — principle is the same).

### 6.2 Second-level (group) outputs

### 6.3 Resting-state (rs-fMRI) outputs (EPI-based)

### 6.4 How fMRI outputs are used in research (mapping questions → files)

### 6.5 BIDS and provenance

- Raw BIDS: sub-*/func/sub-*_bold.nii.gz + JSON sidecar (TR, PhaseEncodingDirection, SliceTiming, …).

- Derivatives: e.g. derivatives/fmriprep/ or derivatives/fsl/ — always record pipeline name + version in methods.

## 7. DWI with EPI — analysis pipeline (overview)

- Concatenate b=0 and diffusion volumes.

- FSL eddy (or equivalent) — motion and eddy-current distortion per volume.

- Brain mask; optional denoising (e.g. MP-PCA).

- Tensor or CSD fit — match directions to model.

- Registration of FA/b0 to T1 for ROI analysis.

### 7.1 Typical DWI outputs after preprocessing (EPI readout)

*(Full DWI output catalog and clinical nuance — DWI sequence handout.)*

### 7.2 How DWI-EPI outputs are used

## 8. Clinical and research uses

- DWI-EPI — acute ischemic stroke (restricted diffusion); interpretation requires clinical training.

- fMRI-EPI — presurgical language/motor mapping ( protocol-specific); research vs clinical workflow separation.

- Research parameters may not be diagnostic quality.

## 9. Worked examples (step-by-step)

### Example A — Temporal sampling and Nyquist (fMRI)

- TR = 2000 ms → 0.5 Hz volume rate. Cardiac ~1 Hz is not fully sampled — aliasing of physiological noise into low frequencies possible; respiration retrospective correction or nuisance regression helps.

### Example B — Echo train duration (order of magnitude)

- Echo spacing 0.55 ms, Ny_phase = 64 → readout ~35 ms (ignoring ramp samples) — order of magnitude for T2* decay across train.

### Example C — topup / blip-up blip-down

- Acquire same distortion geometry with A→P and P→A phase encoding — distortion reverses — FSL topup solves for field for unwarping. Store PhaseEncodingDirection in JSON sidecars.

### Example D — DWI SNR vs b

- Higher b → stronger attenuation exp(−b·ADC) — SNR drops; need more averages or thicker slices or lower resolution.

## 10. Common pitfalls (checklist)

- [ ] TotalReadoutTime or EffectiveEchoSpacing missing → unwarping fails or wrong scale.

- [ ] PhaseEncodingDirection wrong sign → topup direction error.

- [ ] Multiband without LeakBlock QC → unnoticed slice leakage.

- [ ] Ignoring motion in long resting-state → group maps driven by motion correlation.

## 11. Credible peer-reviewed papers (EPI / fMRI)

- Mansfield P. Multi-planar image formation using NMR spin echoes. *J Phys C Solid State Phys.* 1977;10(3):L55–L58. https://doi.org/10.1088/0022-3719/10/3/004

- Jezzard P, Clare S. *Functional MRI: An Introduction to Methods.* Oxford University Press.

- Andersson JLR, et al. How to correct susceptibility distortions in spin-echo echo-planar images: application to diffusion tensor imaging. *NeuroImage.* 2003;20(2):870–888. https://doi.org/10.1016/S1053-8119(03)00336-700336-7)

- Ogawa S, et al. Brain magnetic resonance imaging with contrast dependent on blood oxygenation. *Proc Natl Acad Sci U S A.* 1990;87(24):9868–9872. https://doi.org/10.1073/pnas.87.24.9868

## 12. Credible online resources

- FSL — topup, eddy, FEAT

- mriquestions — EPI

- AFNI documentation

## 13. References (sources used to create this content)

- Jezzard P, Clare S. *Functional MRI: An Introduction to Methods.* Oxford University Press.

- FSL topup and eddy documentation — https://fsl.fmrib.ox.ac.uk/

- mriquestions.com — EPI k-space and ghosting — https://mriquestions.com/

- BIDS specification — fMRI and diffusion metadata — https://bids-specification.readthedocs.io/

### Closing

Your scanner PDF protocol and physicist sign-off override generic numbers here. Always archive sequence parameters in BIDS sidecars.