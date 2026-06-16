# Spin echo (SE) and fast spin echo (TSE / FSE) — full course

Course map: 90°–180° physics → TSE echo train → parameters → artifacts → PD vs T2 → analysis outputs → how outputs are used → vs FLAIR → examples → references.

## 1. Learning objectives

- Draw the timing diagram for a single-echo spin echo and state TE = 2τ (idealized) between 90° and echo.

- Explain how TSE acquires multiple k-space lines per TR and how effective TE is chosen.

- Predict T2 vs PD weighting from TR and TE combinations.

- Describe blurring, motion, and SAR limitations in long echo trains.

- Contrast TSE T2w with FLAIR ( inversion null of CSF — separate handout).

## 2. Physics — classic spin echo

### 2.1 Pulse timing

- 90° excitation tips M into the transverse plane. Static B₀ inhomogeneity causes rapid dephasing of spins.

- 180° refocusing pulse (at time τ after 90°) flips the dephasing — rephasing at TE = 2τ forms the echo.

- Refocusing cancels static ΔB₀ effects to first order → T2 weighting (not T2*) for that echo — ideal for high contrast near susceptibility interfaces vs GRE.

### 2.2 Contrast weighting

- Long TR → minimize T1 effects ( full recovery between TRs for many tissues).

- Long TE → emphasize T2 differences — CSF bright on T2w.

## 3. Fast spin echo (TSE / FSE / RARE)

### 3.1 Echo train

- After 90°, a train of 180° pulses produces multiple echoes per TR. Each echo can encode different phase-encoding lines → ETL lines per TR → scan time ↓ ~ETL (simplified).

### 3.2 Effective TE

- Echoes in the train have different TEs. The effective TE ( echo used for central k-space or weighted average — vendor-specific) determines T2 contrast.

### 3.3 SAR

- Each 180° pulse deposits RF energy. High ETL at 3 T → SAR limits may force longer TR or fewer slices per TR.

## 4. Parameter tables

## 5. Artifacts

- Motion between echoes in train → ghosting / inconsistent phase.

- TSE blurring: point spread broadening along phase encode ( vendor models differ).

- CSF flow pulsation → artifact in periventricular regions.

## 6. PD-weighted imaging

- Long TR + short TE ( first echo emphasis in TSE) → proton-density-like contrast — mix of PD and T2 depending on sequence design.

## 7. Analysis outputs, derivatives, and how they are used

### Mapping questions to outputs

*(Structural segmentation outputs overlap heavily with MP-RAGE — T2 often combined as secondary contrast for lesions.)*

## 8. Worked examples

### Example A — Echo time

- τ = 6 ms → first echo at TE = 12 ms ( 2τ ) in ideal single-echo SE.

### Example B — Scan time scaling

- Matrix 256 phase steps, ETL = 1 → 256 TRs per slice ( single-echo). ETL = 16 → ~16× fewer TRs per slice ( idealized).

## 9. Pitfalls

- Treating TSE T2w as identical to single-echo T2w — contrast may differ due to refocusing train efficiency and magnetization pathway.

- Confusing with FLAIR — FLAIR uses inversion null of CSF ( FLAIR handout).

## 10. Credible peer-reviewed papers

- Hennig J, et al. RARE imaging: a fast imaging method for clinical MR. *Magn Reson Med.* 1986;3(6):823–833. https://doi.org/10.1002/mrm.1910030606

- Melki PS, et al. Comparing the FAISE and the RARE sequences. *J Magn Reson Imaging.* 1991;1(2):163–168. https://doi.org/10.1002/jmri.1880010209

## 11. Credible online resources

- mriquestions — Spin echo

- ISMRM

## 12. References (sources used to create this content)

- mriquestions.com — spin echo and TSE — https://mriquestions.com/spin-echo.html

- Bushberg JT, et al. *The Essential Physics of Medical Imaging* — spin echo timing.

- Vendor TSE product manuals — ETL, effective TE, SAR models.

### Closing

For CSF-suppressed T2-like contrast, use FLAIR ( inversion recovery + TSE readout) — FLAIR handout.