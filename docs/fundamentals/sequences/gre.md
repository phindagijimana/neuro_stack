# Gradient-recalled echo (GRE) — full course

Course map: GRE vs spin echo → T2* physics → spoiling → parameters → artifacts → analysis outputs (maps, qMRI) → how outputs are used → examples → pitfalls → references.

## 1. Learning objectives

- Explain why GRE signal depends on T2* rather than T2 and what that implies near air and metal.

- Describe RF spoiling vs gradient spoiling at a high level and why spoiled GRE is used for fast T1w.

- Use TR, TE, and flip angle to predict whether contrast is T1-dominant, PD-like, or T2*-weighted.

- Recognize chemical shift, susceptibility signal void, and banding in steady-state sequences.

- Map vendor names (FLASH, SPGR, FFE, TFE) to the same physics family.

## 2. Physics — GRE vs spin echo

### 2.1 How the echo forms

- In spin echo (SE), a 180° pulse refocuses static B₀ inhomogeneity → T2 weighting (ideal case).

- In GRE, gradient reversals refocus dephasing due to frequency-encoding gradients — no 180° refocusing of all field inhomogeneities. Local ΔB₀ from susceptibility differences causes irreversible dephasing on the time scale of TE → T2* weighting.

### 2.2 T2 vs T2*

- T2: spin–spin relaxation + reversible dephasing in homogeneous field.

- **T2*: T2 plus susceptibility-induced dephasing — faster decay → signal drops with TE more rapidly in GRE than in SE at the same TE** (conceptually).

### 2.3 Spoiled vs steady-state GRE

- Spoiled GRE: destroy transverse magnetization before the next TR (RF spoiling, gradient spoiling) → no steady-state coherence across TRs → T1 and PD weighting controllable via TR, TE, α.

- Steady-state GRE (e.g., FISP, FFE): some coherence remains → mixed T1/T2 contrast; banding if imperfect balance.

## 3. Acquisition parameters (deep dive)

## 4. Clinical and research uses

## 5. Artifacts

- Susceptibility: signal loss / distortion near air, hemorrhage, metal.

- Chemical shift: fat vs water misregistration in readout direction.

- Steady-state banding: incomplete spoiling or off-resonance in SSFP-like sequences (not spoiled T1).

## 6. Analysis outputs, derivatives, and how they are used

GRE sequences rarely end at reconstruction — research pipelines derive parametric maps or use GRE as input to multistep models.

### Mapping questions to GRE derivatives

## 7. Worked examples

### Example A — Flip angle and TR

- Fixed TR, increasing α toward Ernst optimum → more signal until too large → excessive saturation. Vendor presets encode this.

### Example B — TE near sinuses

- TE = 8 ms vs TE = 20 ms GRE near frontal sinus — longer TE shows more signal void from susceptibility gradients.

## 8. Pitfalls

- Confusing GRE T1w with MP-RAGE — MP-RAGE adds inversion preparation (see MP-RAGE course).

- Using long TE GRE for quantitative T1 mapping without correct spoiling model.

## 9. Credible peer-reviewed papers (GRE)

- Haase A, et al. FLASH imaging: rapid NMR imaging using low flip-angle pulses. *J Magn Reson.* 1986;67(2):258–266. https://doi.org/10.1016/0022-2364(86)90092-390092-3)

- Frahm J, et al. FLASH MRI: experimental and theoretical assessment of balance between signal-to-noise ratio and spatial resolution. *Magn Reson Med.* 1988;6(4):422–433. https://doi.org/10.1002/mrm.1910060406

## 10. Credible online resources

- mriquestions — Gradient echo

- ISMRM

## 11. References (sources used to create this content)

- mriquestions.com — GRE vs spin echo, spoiling — https://mriquestions.com/

- Haacke EM, et al. *Magnetic Resonance Imaging* — gradient echo chapters.

- Vendor pulse-sequence manuals — FLASH / SPGR / TFE naming.

### Closing

Pair with `MPRAGE` (inversion-prepared GRE), `SWI` (GRE + phase), and `EPI` (fast readout).