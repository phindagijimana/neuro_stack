# MR Spectroscopy (MRS)

> MRI tells you where. MRS tells you what — in millimolar concentrations, from a single voxel, if you shimmed it.

Course map: Why MRS → chemical shift basics → localisation (PRESS, STEAM, sLASER) → MEGA-PRESS for GABA → CSI / MRSI → quantification ([LCModel](http://s-provencher.com/lcmodel.shtml), [Osprey](https://schorschinengel.github.io/osprey/)) → metabolite catalogue → reporting ([MRSinMRS](https://www.mrshub.org/mrsinmrs)) → pitfalls → clinical → worked snippet → references.

## 1. Learning objectives

- State why protons in different molecules resonate at slightly different frequencies (chemical shift in ppm).

- Distinguish PRESS, STEAM, sLASER, and MEGA-PRESS by what they sacrifice and what they buy.

- Define an internal water reference and an external phantom reference.

- List the standard metabolites visible at clinical 3T and what each indicates.

- Recite the MRSinMRS minimum reporting fields.

- Recognise the top three artifacts: bad shim, residual water, lipid contamination.

## 2. Why MRS

MRI exploits water proton density and relaxation. MRS exploits the fact that protons in NAA, choline, creatine, glutamate, GABA, lactate, etc. resonate at slightly different frequencies because of their local electronic environment ( chemical shift). The result is a 1D NMR spectrum — peaks at characteristic positions in parts per million (ppm) relative to a reference (TMS / water).

Concentrations are millimolar (mM), three to four orders below water. MRS needs large voxels (1–8 cm³), water suppression, and careful shimming to recover them.

## 3. Chemical shift basics

Resonance frequency:

\[
\omega = \gamma B_0 (1 - \sigma),
\]

where $\sigma$ is the electron shielding constant. Differences in $\sigma$ shift peaks by a few ppm.

At 3T, 1 ppm ≈ 128 Hz. Typical metabolite spread: 0–4 ppm.

## 4. Localisation sequences

Single-voxel proton MRS for clinical use was established by [Frahm et al., 1989](https://doi.org/10.1002/mrm.1910090110) using the STEAM (stimulated-echo acquisition mode) sequence, alongside [Bottomley, 1987 PRESS](https://doi.org/10.1002/mrm.1910050208) which dominates clinical practice today. Single-voxel spectroscopy uses three orthogonal slice-selective pulses to define a cubic ROI.

| Sequence | Pulses | Pros | Cons |
|---|---|---|---|
| **PRESS** | 90° – 180° – 180° | Higher SNR, shortest minimum TE moderate | Chemical shift displacement error (CSDE) larger |
| **STEAM** | 90° – 90° – 90° | Short TE, sharper voxel | Half the SNR of PRESS |
| **sLASER** | 90° + adiabatic 180° pairs | Low CSDE, robust at high field | Longer TE, vendor-limited |
| **MEGA-PRESS** | PRESS + editing pulse on GABA | Detects 3 ppm GABA-H4 | Long scan, frequency drift sensitivity |

### 4.1 CSDE

Different metabolites at different ppm see the slice-select gradient differently, so the actual voxel is shifted slightly per metabolite. At 3T PRESS the shift is a few percent of voxel size; at 7T it is large enough to need OVS bands or sLASER.

## 5. Spectroscopic imaging (CSI / MRSI)

Phase-encode in 2 or 3 dimensions to get a metabolite map across a slab.

- 2D MRSI: 16×16 grid, ~10×10×15 mm voxels, 10 min.

- Accelerated MRSI (EPSI, spiral, compressed sensing) — research, vendor-specific.

- Trade SNR for coverage. Quantification per voxel becomes statistical.

## 6. Shimming, water suppression, eddy currents

- **Shimming**: line width is everything. Target ≤ 10 Hz water FWHM in voxel before acquisition. Vendor automated shims work for cortex; manual / FASTMAP for brainstem and temporal lobe.

- **Water suppression**: CHESS / VAPOR — frequency-selective saturation. Residual water swamps the upfield peaks if mistuned.

- **Eddy current correction**: phase the FID against a non-water-suppressed reference acquisition (Klose 1990). Mandatory in [LCModel](http://s-provencher.com/lcmodel.shtml) input.

## 7. MEGA-PRESS for GABA

GABA-H4 (3 ppm) overlaps creatine. MEGA-PRESS alternates an editing 180° pulse on the GABA-H3 coupling partner (1.9 ppm):

- **ON** scans: GABA coupling refocused.

- **OFF** scans: standard PRESS.

- Subtract ON − OFF → edited spectrum shows GABA at 3 ppm and Glx at 3.75 ppm; everything else cancels.

Frequency drift (a few Hz over 10 min) blows the subtraction up — use frequency/phase correction (Near 2015), and check [Gannet](https://markmikkelsen.github.io/Gannet-docs/) QA.

## 8. Quantification

### 8.1 Model fitting

- **[LCModel](http://s-provencher.com/lcmodel.shtml)** (Provencher 1993) — gold standard. Linear combination of in-vitro basis set; outputs concentrations and Cramér–Rao lower bounds (CRLB).

- **[Tarquin](http://tarquin.sourceforge.net/)** — open-source LCModel-like.

- **[Osprey](https://schorschinengel.github.io/osprey/)** (Oeltzschner 2020) — open-source, BIDS-aware, MATLAB.

- **[GANNET](https://markmikkelsen.github.io/Gannet-docs/)** — MEGA-PRESS GABA only, MATLAB.

- **[FSL-MRS](https://open.win.ox.ac.uk/pages/fsl/fsl_mrs/)** — Python/FSL pipeline with Bayesian fitting.

- **[jMRUI](http://www.jmrui.eu/)** — Java GUI for time-domain quantification (AMARES, QUEST).

### 8.2 Concentration units

Two roads:

- **Internal water reference**: scale metabolite signal by tissue water signal, correct for tissue $T_1, T_2$, partial volume of GM/WM/CSF (Gasparovic 2006). Reports mM in tissue water.

- **External phantom**: scan a calibrated phantom in the same session. More work, more reproducible across sites.

CRLB < 20% per metabolite is the usual quality threshold. CRLB > 50% means "do not report this concentration."

## 9. Metabolite catalogue (3T, healthy GM)

| Metabolite | ppm | Concentration | Indicates |
|---|---|---|---|
| **NAA** (N-acetylaspartate) | 2.01 | 8–11 mM | Neuronal integrity |
| **Cr + PCr** (total creatine) | 3.03, 3.93 | 7–9 mM | Energy buffer; common reference |
| **Cho** (choline cmpds) | 3.22 | 1–2 mM | Membrane turnover |
| **mI** (myo-inositol) | 3.55 | 4–6 mM | Glial proliferation |
| **Glu + Gln** (Glx) | 2.1–2.4, 3.7 | 8–12 mM | Excitatory neurotransmission, energy |
| **GABA** | 3.0 (edited) | 1–2 mM | Inhibitory tone |
| **Lac** (lactate) | 1.33 (doublet) | <1 mM normal | Anaerobic metabolism |
| **Lip / MM** | 0.9–1.4 | variable | Necrosis, contamination |

NAA/Cr, Cho/Cr ratios are commonly reported but mask Cr changes — prefer absolute concentrations when possible.

## 10. Reporting standards

The **[MRSinMRS](https://www.mrshub.org/mrsinmrs)** checklist (Lin 2021) lists ~30 mandatory fields covering hardware, sequence (TE, TR, voxel, suppression), processing (line broadening, eddy correction), quantification (basis set, reference, CRLB), and data sharing. Reviewers increasingly require it. The [MRSHub](https://www.mrshub.org/) hosts the form, example basis sets, code, and community-maintained tutorials.

## 11. Pitfalls

- **Voxel positioning reproducibility**: 5 mm shift can change NAA by 10%. Use structural-guided planning, screenshot every voxel.

- **Partial volume CSF**: 30% CSF in voxel → 30% concentration error if not corrected. Segment T1, compute tissue fractions, apply Gasparovic correction.

- **Age effects**: NAA drops, mI rises with age — always include age as covariate.

- **Field drift in MEGA-PRESS**: leads to false positive GABA differences. Correct or interleave.

- **Lipid contamination from skull**: poor voxel placement near scalp. Use outer-volume suppression.

- **B1 inhomogeneity at 7T**: use adiabatic pulses (sLASER).

## 12. Medical / clinical relevance

**Beginner.** MRS measures chemical concentrations (NAA, creatine, choline, lactate, lipids) in vivo — a non-invasive biopsy for tumours, mitochondrial disease, and metabolic disorders.

**Routine clinical use.**

- Brain tumour grading and treatment-response monitoring.
- Suspected mitochondrial disease (Leigh, MELAS, MERRF) — lactate at long TE.
- Leukodystrophies and paediatric metabolic disorders.
- Hepatic encephalopathy work-up.
- Mesial-temporal-sclerosis lateralisation in pre-surgical epilepsy.

**Disease applications.**

| Disease | Imaging finding | Clinical value | Cross-link |
|---|---|---|---|
| Brain tumour grading | High Cho/NAA, low NAA, lipid + lactate ≈ high grade; 2-HG peak at 2.25 ppm → IDH-mutant glioma | Non-invasive grading + molecular pre-test | [doi:10.5114/wo.2013.38114](https://doi.org/10.5114/wo.2013.38114) (Bulik 2013); [doi:10.1038/nm.2682](https://doi.org/10.1038/nm.2682) (Choi 2012, 2-HG) |
| Mitochondrial disease (Leigh, MELAS) | Elevated lactate doublet + reduced NAA in affected territories | Diagnosis and follow-up of treatment | [doi:10.1212/01.WNL.0000094322.31957.4D](https://doi.org/10.1212/01.WNL.0000094322.31957.4D) (Bianchi 2003) |
| Leukodystrophies | Canavan: NAA elevated; Pelizaeus–Merzbacher: NAA reduced; vanishing white matter: lactate + low NAA | Subtype assignment in undiagnosed leukodystrophy | [doi:10.1148/radiol.2492072028](https://doi.org/10.1148/radiol.2492072028) (Bizzi 2008) |
| Hepatic encephalopathy | Elevated glutamine, reduced myo-inositol | Severity tracking, treatment response | Kreis 1992 |
| Multiple sclerosis | NAA reduction in normal-appearing WM; choline elevation in active lesions | Axonal-injury biomarker beyond lesion count | [doi:10.1212/WNL.0b013e31819b27a8](https://doi.org/10.1212/WNL.0b013e31819b27a8) (Sajja 2009); [clinical/multiple-sclerosis.md](../../clinical/multiple-sclerosis.md) |
| Acute stroke | Lactate elevation in penumbra; NAA loss in infarct core | Penumbra vs core characterisation | [doi:10.1212/WNL.45.2.343](https://doi.org/10.1212/WNL.45.2.343) (Saunders 1995) |
| Alzheimer's disease | Hippocampal NAA reduction, myo-inositol elevation | Adjunct biomarker; mI rises early in MCI | [doi:10.1212/01.wnl.0000256697.49263.61](https://doi.org/10.1212/01.wnl.0000256697.49263.61) (Kantarci 2007); [clinical/alzheimers-and-dementia.md](../../clinical/alzheimers-and-dementia.md) |
| Mesial-temporal sclerosis | Asymmetric hippocampal NAA reduction | Lateralisation when MRI is non-lesional | Cross-link [clinical/epilepsy.md](../../clinical/epilepsy.md) |

**Research depth.** The next decade of clinical MRS is dominated by *edited* and *high-field* acquisitions. **MEGA-PRESS** and Hadamard-encoded extensions (HERMES, HERCULES) push GABA, glutathione, and NAAG into clinical psychiatry, addiction, and ageing research — see [Gannet](https://markmikkelsen.github.io/Gannet-docs/) for the de facto pipeline. **7 T MRS** separates glutamine from glutamate with sub-ppm resolution, opening glutamate excitotoxicity as a clinical-research target in schizophrenia, depression, and treatment-resistant psychiatry. Hetero-nuclear MRS — $^{31}$P (PCr / ATP, intracellular pH), $^{23}$Na (intracellular sodium), $^{13}$C dynamics — quantifies high-energy phosphates and ionic shifts in stroke, oncology, and muscle disease, though clinical hardware is restricted. MRS as a **clinical-trial endpoint** is operational in MS (NAA recovery on remyelinating agents), brain tumour (treatment-response prediction — [Hu 2014](https://doi.org/10.1093/neuonc/nou175)), and dementia (NAA / mI trajectories), and the [MRSinMRS](https://www.mrshub.org/mrsinmrs) checklist plus [Wilson 2019](https://doi.org/10.1002/mrm.27742) consensus are the standardisation work that lets multi-site MRS endpoints survive regulatory scrutiny. Vendor-harmonised basis sets ([MRSHub](https://www.mrshub.org/)) and modern fitters ([Osprey](https://schorschinengel.github.io/osprey/), [FSL-MRS](https://open.win.ox.ac.uk/pages/fsl/fsl_mrs/)) are closing the reproducibility gap that historically kept MRS out of large trials.

## 13. Worked example

### 13.1 [suspect](https://suspect.readthedocs.io/) (Python) — load and plot

```python
import suspect
import matplotlib.pyplot as plt

# Load Siemens TWIX
data = suspect.io.load_twix("press_te30.dat")
print(data.shape, data.dt, data.f0)

# Frequency / phase correction
corrected = suspect.processing.frequency_correction.spectral_registration(data)

# Average, FFT, plot
spec = corrected.mean(axis=0).fft()
plt.plot(spec.frequency_axis_ppm(), spec.real)
plt.gca().invert_xaxis()
plt.xlabel("ppm"); plt.ylabel("a.u.")
plt.xlim(4.2, 0.5)
```

### 13.2 Osprey command line

```bash
# Edit OspreyJob_*.json with paths to .dat / .nii / basis set
matlab -batch "OspreyJob('OspreyJob_subj01.json'); \
               OspreyLoad(MRSCont); OspreyProcess(MRSCont); \
               OspreyFit(MRSCont); OspreyCoreg(MRSCont); \
               OspreySeg(MRSCont); OspreyQuantify(MRSCont)"
```

Output: per-metabolite concentrations, CRLBs, water-scaled and tissue-corrected.

## 14. External tools & resources

### Quantification software

- [LCModel](http://s-provencher.com/lcmodel.shtml) — historical gold standard for linear-combination model fitting.
- [Osprey](https://schorschinengel.github.io/osprey/) — open-source MATLAB pipeline, BIDS-aware, modern community standard.
- [Tarquin](http://tarquin.sourceforge.net/) — open-source command-line quantification.
- [jMRUI](http://www.jmrui.eu/) — time-domain Java GUI (AMARES, QUEST).
- [GANNET](https://markmikkelsen.github.io/Gannet-docs/) — MEGA-PRESS GABA-edited pipeline.
- [FSL-MRS](https://open.win.ox.ac.uk/pages/fsl/fsl_mrs/) — Python/FSL with Bayesian fitting.

### Python tooling

- [suspect](https://suspect.readthedocs.io/) — vendor-format I/O, frequency/phase correction, plotting.

### Reporting and community

- [MRSinMRS](https://www.mrshub.org/mrsinmrs) — minimum reporting checklist (Lin 2021).
- [MRSHub](https://www.mrshub.org/) — community hub: basis sets, code, tutorials, datasets.

## 15. References

1. Lin A, Andronesi O, Bogner W, et al. Minimum Reporting Standards for in vivo Magnetic Resonance Spectroscopy (MRSinMRS): Experts' consensus recommendations. *NMR Biomed.* 2021;34(5):e4484. https://doi.org/10.1002/nbm.4484

2. Provencher SW. Estimation of metabolite concentrations from localized in vivo proton NMR spectra. *Magn Reson Med.* 1993;30(6):672–679. https://doi.org/10.1002/mrm.1910300604

3. Mescher M, Merkle H, Kirsch J, Garwood M, Gruetter R. Simultaneous in vivo spectral editing and water suppression. *NMR Biomed.* 1998;11(6):266–272. https://doi.org/10.1002/(SICI)1099-1492(199810)11:6<266::AID-NBM530>3.0.CO;2-J

4. Gasparovic C, et al. Use of tissue water as a concentration reference for proton spectroscopic imaging. *Magn Reson Med.* 2006;55(6):1219–1226. https://doi.org/10.1002/mrm.20901

5. Near J, et al. Frequency and phase drift correction of magnetic resonance spectroscopy data by spectral registration in the time domain. *Magn Reson Med.* 2015;73(1):44–50. https://doi.org/10.1002/mrm.25094

6. Oeltzschner G, et al. Osprey: Open-source processing, reconstruction & estimation of magnetic resonance spectroscopy data. *J Neurosci Methods.* 2020;343:108827. https://doi.org/10.1016/j.jneumeth.2020.108827

7. Choi C, et al. 2-hydroxyglutarate detection by magnetic resonance spectroscopy in IDH-mutated patients with gliomas. *Nat Med.* 2012;18(4):624–629. https://doi.org/10.1038/nm.2682

8. Wilson M, et al. Methodological consensus on clinical proton MRS of the brain. *Magn Reson Med.* 2019;82(2):527–550. https://doi.org/10.1002/mrm.27742

9. Frahm J, Bruhn H, Gyngell ML, Merboldt KD, Hänicke W, Sauter R. Localized high-resolution proton NMR spectroscopy using stimulated echoes: initial applications to human brain in vivo. *Magn Reson Med.* 1989;9(1):79–93. https://doi.org/10.1002/mrm.1910090110 — the STEAM single-voxel ¹H-MRS founding paper.

## Where to next

- Foundations: [../foundations/physics.md](../foundations/physics.md) — for the Larmor frequency and chemical shift basics.

- MPRAGE: [./mprage.md](./mprage.md) — for partial-volume segmentation of the MRS voxel.

- Analysis: [../../analysis/structural.md](../../analysis/structural.md) — for tissue fraction pipelines.

- PET: [./pet.md](./pet.md) — the other molecular-specificity tool.

### Closing

MRS is the only in vivo modality that returns labelled chemistry. Treat it that way: shim it like a chemist, suppress water like a physicist, quantify it like a statistician, and report every field MRSinMRS asks for.
