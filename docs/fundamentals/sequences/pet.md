# Positron Emission Tomography (PET)

> MRI maps water. PET maps a molecule of your choice. The cost is ionising radiation, a cyclotron-fed tracer, and a kinetic model with assumptions you must own.

Course map: Why PET → physics from positron to sinogram → reconstruction → tracers (FDG, amyloid, tau, dopamine, TSPO) → SUV / SUVR → dynamic kinetic modelling (1TC, 2TC, Logan, Patlak) → partial volume → PET-MR / attenuation correction → [Centiloid](https://www.gaain.org/centiloid-project) → software → clinical use → worked Logan example → references.

## 1. Learning objectives

- Trace the path from positron emission through annihilation, coincidence detection, sinogram, and reconstruction.

- Distinguish OSEM from MLEM in one sentence each.

- Name three amyloid tracers and one each for tau, dopamine D2, and TSPO.

- Define SUV, SUVR, $V_T$, $BP_{ND}$, $K_i$ and state which kinetic model gives which.

- Choose a reference-tissue vs arterial-input model based on tracer and study design.

- Recite the rationale for the Centiloid scale.

## 2. Why PET

MR contrast is biophysical. PET contrast is *molecular*: glucose metabolism, amyloid plaques, tau tangles, D2 receptor availability, translocator protein density. The price is radiation dose (~5–10 mSv) and short-lived isotopes that require on- or near-site production for $^{11}$C and a cyclotron network for $^{18}$F.

## 3. Physics

### 3.1 Positron emission

Proton-rich isotope decays via $\beta^+$:

\[
p \to n + e^+ + \nu_e.
\]

The positron travels a tracer-specific range (mm scale) and annihilates with an electron:

\[
e^+ + e^- \to \gamma + \gamma,\quad E_\gamma = 511\;\mathrm{keV}.
\]

The two 511 keV photons travel ~180° apart.

### 3.2 Coincidence detection

Coincidence-detection PET tomography was introduced by [Phelps et al., 1975](https://jnm.snmjournals.org/content/16/3/210) at Washington University, building on positron-annihilation physics worked out by Wrenn and others in the 1950s-60s. Ring of scintillator detectors record pairs within a coincidence window (~4–6 ns). Each pair defines a line of response (LOR). Effective spatial resolution: 3–6 mm for clinical scanners, 1–2 mm for HRRT and modern total-body.

### 3.3 Sinogram

LORs are binned by angle and radial offset → 2D sinogram per axial slice (or full 3D list-mode preserved). Sinograms feed the reconstruction.

### 3.4 Reconstruction

- **FBP** (filtered back-projection): analytical, fast, noisy in low-count data.

- **MLEM** (maximum likelihood expectation maximisation, Shepp 1982): iterative, Poisson noise model:

\[
\lambda_j^{(n+1)} = \frac{\lambda_j^{(n)}}{\sum_i a_{ij}} \sum_i a_{ij}\,\frac{y_i}{\sum_k a_{ik}\,\lambda_k^{(n)}}.
\]

- **OSEM** (ordered-subset EM, Hudson 1994): MLEM partitioned into subsets, ~10× faster, the clinical default.

- **PSF / TOF reconstructions** improve spatial resolution and SNR (Conti 2011).

## 4. Tracers

| Class | Isotope/Tracer | Target | Use |
|---|---|---|---|
| Metabolism | $^{18}$F-FDG | Glucose | AD, FTD, oncology, epilepsy localisation |
| Amyloid | [$^{11}$C]PIB | Aβ plaques | AD research |
| Amyloid | [$^{18}$F]florbetapir, florbetaben, flutemetamol | Aβ plaques | AD clinical (FDA approved) |
| Tau | [$^{18}$F]flortaucipir (AV-1451) | Paired helical filament tau | AD |
| Tau | [$^{18}$F]MK-6240, PI-2620 | Tau (newer generation) | AD, PSP, CBD |
| Dopamine | [$^{11}$C]raclopride | D2/D3 | Parkinson’s, schizophrenia |
| Dopamine | [$^{18}$F]DOPA | Pre-synaptic | PD, neuroendocrine |
| Neuroinflammation | [$^{11}$C]PBR28, [$^{18}$F]DPA-714 | TSPO (microglia) | Confound: TSPO genotype |
| Synaptic density | [$^{11}$C]UCB-J | SV2A | Schizophrenia, AD |

## 5. Quantification

### 5.1 Static — SUV and SUVR

For a single late-frame scan:

\[
\mathrm{SUV} = \frac{C(t)\;[\mathrm{kBq/mL}]}{\mathrm{injected\ dose}\;[\mathrm{kBq}]\,/\,\mathrm{body\ weight}\;[\mathrm{g}]}.
\]

Scale-free, comparable across patients. Influenced by uptake time, weight, glucose level (FDG).

**SUVR** = target SUV / reference-region SUV; common reference is cerebellar grey matter (amyloid, tau) or pons (FDG, sometimes). SUVR has no kinetic interpretation but is robust and the basis of clinical reading.

### 5.2 Dynamic — kinetic modelling

Acquire from injection for 60–90 min in time frames. Fit a compartment model.

**1-tissue compartment (1TC)** for inert tracers like $^{15}$O-water:

\[
\frac{dC_T(t)}{dt} = K_1 C_P(t) - k_2 C_T(t).
\]

**2-tissue compartment (2TC)** for receptor / specific binding tracers ([$^{11}$C]raclopride, [$^{18}$F]FDG, [$^{11}$C]PIB):

\[
\frac{dC_{ND}}{dt} = K_1 C_P - (k_2 + k_3)C_{ND} + k_4 C_S,
\]

\[
\frac{dC_S}{dt} = k_3 C_{ND} - k_4 C_S.
\]

Total volume of distribution:

\[
V_T = \frac{K_1}{k_2}\left(1 + \frac{k_3}{k_4}\right).
\]

Non-displaceable binding potential:

\[
BP_{ND} = \frac{k_3}{k_4} = \frac{V_T - V_{ND}}{V_{ND}}.
\]

For irreversible tracers (FDG, [$^{18}$F]FDOPA), the influx constant $K_i = K_1 k_3/(k_2 + k_3)$.

### 5.3 Logan plot (Logan 1990) — reversible tracers

Transform the convolution equation into a linear plot:

\[
\frac{\int_0^t C_T(\tau)\,d\tau}{C_T(t)} = V_T\,\frac{\int_0^t C_P(\tau)\,d\tau}{C_T(t)} + b,\quad t > t^*.
\]

Slope = $V_T$. No need for a kinetic model fit — graphical, robust to noise after $t^*$.

### 5.4 Patlak plot (Patlak 1983) — irreversible tracers

\[
\frac{C_T(t)}{C_P(t)} = K_i\,\frac{\int_0^t C_P(\tau)\,d\tau}{C_P(t)} + V_0,\quad t > t^*.
\]

Slope = $K_i$ (e.g., FDG metabolic rate).

### 5.5 Input function

- **Arterial input**: gold standard but invasive (arterial cannulation, blood sampling).

- **Image-derived input**: from carotid ROI on dynamic data — partial-volume corrected.

- **Reference tissue models** (SRTM, Lammertsma 1996): use a region devoid of specific binding (cerebellum for many tracers). Outputs $BP_{ND}$ without blood sampling.

Pick the input strategy that matches the tracer's biology — never use cerebellum as reference if your tracer binds in cerebellum.

## 6. Partial volume correction (PVC)

PET resolution (4–6 mm FWHM) blurs activity across tissue boundaries. Cortical SUVR underestimates by 20–40% in atrophic brain.

- **Müller-Gärtner** (1992): voxel-wise correction using GM/WM/CSF segmentation from co-registered MR.

- **Geometric Transfer Matrix (GTM, Rousset 1998)**: region-based; assumes uniform activity per ROI.

- **[PETPVC toolbox](https://github.com/UCL/PETPVC)** (Thomas 2016): collects ~10 methods.

PVC matters most for tau (small late-stage signals in atrophic cortex) and dopamine (striatal volumes).

## 7. Attenuation correction

511 keV photons are attenuated by ~50% per 7 cm of soft tissue. Correction is mandatory and a major source of quantification error.

- **PET-CT**: CT-based μ-map from Hounsfield units. Standard, accurate.

- **PET-MR**: MR is not directly an attenuation map (no signal from bone). Solutions:

    - **Dixon segmentation** (4 classes): air, lung, soft tissue, fat — misses bone, biases by ~5–10%.

    - **UTE / ZTE**: capture bone signal — better, vendor-specific.

    - **Atlas-based / deep-learning AC**: state of the art.

Always report the AC method.

## 8. Standardisation: [Centiloid](https://www.gaain.org/centiloid-project) (Klunk 2015)

A linear rescaling of any amyloid PET SUVR to a common 0–100 scale:

- 0 = young healthy controls.

- 100 = typical AD dementia.

Allows pooling florbetapir, florbetaben, flutemetamol, PIB studies. The Centiloid level for "amyloid positive" is around 20–30 CL ( vendor- and reference-region-dependent).

## 9. Software

| Tool | Notes |
|---|---|
| **[PMOD](https://www.pmod.com/web/)** | Commercial; gold-standard kinetic modelling, ROI definition |
| **[Turku PET Centre scripts](https://www.turkupetcentre.fi/)** | Open-source, command-line, all major models |
| **[MIAKAT](https://www.invicro.com/platforms/miakat)** (Imperial) | MATLAB, validated for receptor PET |
| **[PETPVC](https://github.com/UCL/PETPVC)** | Partial volume correction methods |
| **[NiftyPET / kineticAnalysis](https://github.com/NiftyPET/NiftyPET)** (Python) | Scriptable kinetic fits |
| **[Centiloid](https://www.gaain.org/centiloid-project) pipelines** | [GAAIN](https://www.gaain.org/) reference data + scripts |
| **[PETPrep](https://github.com/nipreps/petprep_hmc)** ([BIDS](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/positron-emission-tomography.html)) | Reproducible PET pre-processing |
| **[AMIDE](https://amide.sourceforge.net/)** | Open-source viewer and ROI analysis |
| **[nibabel](https://nipy.org/nibabel/)** | NIfTI / Analyze / ECAT I/O in Python |

## 10. Medical / clinical relevance

**Beginner.** PET maps molecular targets — glucose metabolism (FDG), amyloid, tau, dopamine, neuroinflammation — that MR cannot see.

**Routine clinical use.**

- Dementia work-up: combined FDG + amyloid PET, increasingly tau PET for staging.
- Oncology staging, restaging, and treatment-response (FDG and tracer-specific).
- Pre-surgical epilepsy localisation (interictal FDG hypometabolism).
- Parkinson's disease and atypical parkinsonism (DAT-SPECT / PET, FDG patterns).
- Anti-amyloid therapy monitoring (Centiloid drop as efficacy endpoint).
- Brain tumour residual / recurrent disease (amino-acid tracers: FET, methionine).

**Disease applications.**

| Disease | Imaging finding | Clinical value | Cross-link |
|---|---|---|---|
| Alzheimer's disease | Amyloid PET (florbetapir, florbetaben, flutemetamol) → Centiloid scale; tau PET (flortaucipir, MK-6240) for staging; FDG hypometabolism in temporoparietal cortex and posterior cingulate | A/T/N framework biomarkers; anti-amyloid eligibility | [doi:10.1016/j.jalz.2014.07.003](https://doi.org/10.1016/j.jalz.2014.07.003) (Klunk 2015, Centiloid); [clinical/alzheimers-and-dementia.md](../../clinical/alzheimers-and-dementia.md) |
| Frontotemporal dementia | FDG hypometabolism in frontal and anterior-temporal lobes; tau PET pattern depends on tauopathy subtype | Distinguishes from AD pattern | Standard FTD work-up |
| Parkinson's disease | ¹⁸F-DOPA / ¹¹C-DTBZ: nigrostriatal dopamine loss; DAT-SPECT / PET (FP-CIT) for diagnosis | Diagnose PD vs essential tremor, drug-induced parkinsonism | [doi:10.1212/WNL.0b013e3181f2a16d](https://doi.org/10.1212/WNL.0b013e3181f2a16d) (Brooks 2010); [clinical/parkinsons-and-movement.md](../../clinical/parkinsons-and-movement.md) |
| Multiple system atrophy / PSP | ¹⁸F-FDG cerebellar / striatal patterns; distinct from idiopathic PD | Atypical-parkinsonism differential | Standard movement-disorder PET |
| Pre-surgical epilepsy | Interictal FDG hypometabolism lateralises temporal-lobe epilepsy when MR is non-lesional; FCD localisation | Adjunct to MRI in MRI-negative cases | [doi:10.1002/ana.21500](https://doi.org/10.1002/ana.21500) (Knowlton 2008); [clinical/epilepsy.md](../../clinical/epilepsy.md) |
| Brain tumour residual / recurrent | ¹⁸F-FET, ¹¹C-methionine: amino-acid uptake delineates active tumour vs treatment effect | Treatment planning, radiation re-targeting | [doi:10.1093/neuonc/now058](https://doi.org/10.1093/neuonc/now058) (Albert 2016) |
| Neuroinflammation | ¹⁸F-DPA-714, ¹¹C-PK11195 TSPO PET: microglial activation in MS, AD, ALS | Neuroinflammation biomarker; trial endpoint | [doi:10.1038/s41582-020-0395-6](https://doi.org/10.1038/s41582-020-0395-6) (Kreisl 2020) |
| Anti-amyloid therapy | Centiloid drop on serial amyloid PET (lecanemab, donanemab) | Efficacy endpoint in trials and post-approval monitoring | Centiloid family; cross-link [clinical/alzheimers-and-dementia.md](../../clinical/alzheimers-and-dementia.md) |
| Oncology staging | FDG: glucose metabolism for staging / restaging; tracer-specific for tumour biology | Treatment planning across haemato- and solid tumours | Standard oncology guidelines |

**Research depth.** **PET-MR vs PET-CT** integration — simultaneous PET-MR systems (Siemens Biograph mMR, GE Signa PET/MR) deliver perfusion-MRI + PET in one acquisition, but face the MR-attenuation-correction problem (no signal from cortical bone) addressed by UTE / ZTE / atlas-based / deep-learning AC. **Kinetic modelling** with arterial input function remains the gold standard for receptor and metabolic-rate quantification, but reference-tissue models ([Lammertsma 1996](https://doi.org/10.1006/nimg.1996.0066)) dominate clinical settings — picking the right strategy is tracer-biology-specific. **Partial-volume correction** is increasingly mandatory in atrophic brains for tau and dopamine quantification (20–40% underestimate without it). **Deep-learning PET image quality enhancement** (low-dose PET reconstruction, denoising, super-resolution) is reducing radiation dose and scan-time bottlenecks. The **PET radiotracer development pipeline** is the gating constraint: preclinical → first-in-human → clinical translation typically takes 5–10 years, and modern targets in active development include **synuclein PET** (no clinical tracer yet despite a decade of effort — the unmet need in Parkinson's and synucleinopathy diagnostics), **GLP-1 receptor PET** (metabolic / neurodegeneration crossover), SV2A synaptic-density imaging ([¹¹C-UCB-J](https://doi.org/10.1126/scitranslmed.aaf6667), Finnema 2016) for schizophrenia and AD, and next-generation tau tracers (PI-2620, MK-6240) with reduced off-target meningeal binding. Total-body PET scanners (uEXPLORER) deliver 40× sensitivity gain and enable previously impractical dynamic protocols at sub-mSv doses, opening paediatric and longitudinal applications.



## 11. Pitfalls

- Reporting SUV when kinetic data are available — throws away information.

- Using cerebellar reference when the tracer binds in cerebellum (e.g., some tau tracers bind to off-target meninges → spill-in).

- Centiloid with the wrong reference region or pipeline — values do not pool with literature.

- Neglecting PVC in atrophic brains for tau or dopamine.

- TSPO genotype confound: high-, mixed-, and low-affinity binders must be stratified.

- MR-based AC in PET-MR without bone correction — biases cortical SUVR.

## 12. Worked Python pseudocode — Logan plot for $V_T$

```python
import numpy as np

# Inputs
t      = np.array([...])   # frame midpoints (min)
C_T    = np.array([...])   # tissue TAC (kBq/mL), per voxel or ROI
C_P    = np.array([...])   # plasma input (kBq/mL)
t_star = 30.0              # start of linear regime (min, tracer-dependent)

# Cumulative integrals (trapezoidal)
intCT = np.concatenate([[0], np.cumsum(0.5 * (C_T[1:] + C_T[:-1]) * np.diff(t))])
intCP = np.concatenate([[0], np.cumsum(0.5 * (C_P[1:] + C_P[:-1]) * np.diff(t))])

x = intCP / C_T
y = intCT / C_T

mask = t > t_star
slope, intercept = np.polyfit(x[mask], y[mask], 1)

V_T = slope
print(f"V_T = {V_T:.2f} mL/cm^3,  intercept = {intercept:.2f}")
```

Reference-tissue Logan replaces $C_P$ with a reference TAC and yields the distribution volume ratio (DVR), where $BP_{ND} = \mathrm{DVR} - 1$.

## 13. External tools & resources

### Kinetic modelling and quantification

- [PMOD](https://www.pmod.com/web/) — commercial gold-standard kinetic modelling and ROI analysis suite.
- [Turku PET Centre scripts](https://www.turkupetcentre.fi/) — open-source command-line library covering 1TC, 2TC, Logan, Patlak, SRTM.
- [MIAKAT](https://www.invicro.com/platforms/miakat) — MATLAB-based receptor PET pipeline.
- [NiftyPET](https://github.com/NiftyPET/NiftyPET) — Python framework for reconstruction and kinetic analysis.

### Partial-volume correction and viewers

- [PETPVC](https://github.com/UCL/PETPVC) — collection of ~10 PVC methods (Müller-Gärtner, GTM, RBV, ...).
- [AMIDE](https://amide.sourceforge.net/) — open-source PET/SPECT/CT viewer with ROI quantification.
- [nibabel](https://nipy.org/nibabel/) — Python I/O for NIfTI/Analyze/ECAT/PAR-REC.

### Standardisation and harmonisation

- [Centiloid project](https://www.gaain.org/centiloid-project) — reference data, ROIs, and scripts for cross-tracer amyloid harmonisation.
- [GAAIN](https://www.gaain.org/) — Global Alzheimer's Association Interactive Network data portal.
- [BIDS PET extension](https://bids-specification.readthedocs.io/en/stable/modality-specific-files/positron-emission-tomography.html) — standard layout for PET data and metadata.

## 14. References

1. Klunk WE, Koeppe RA, Price JC, et al. The Centiloid Project: standardizing quantitative amyloid plaque estimation by PET. *Alzheimers Dement.* 2015;11(1):1–15.e4. https://doi.org/10.1016/j.jalz.2014.07.003

2. Patlak CS, Blasberg RG, Fenstermacher JD. Graphical evaluation of blood-to-brain transfer constants from multiple-time uptake data. *J Cereb Blood Flow Metab.* 1983;3(1):1–7. https://doi.org/10.1038/jcbfm.1983.1

3. Logan J, Fowler JS, Volkow ND, et al. Graphical analysis of reversible radioligand binding from time–activity measurements. *J Cereb Blood Flow Metab.* 1990;10(5):740–747. https://doi.org/10.1038/jcbfm.1990.127

4. Lammertsma AA, Hume SP. Simplified reference tissue model for PET receptor studies. *Neuroimage.* 1996;4(3):153–158. https://doi.org/10.1006/nimg.1996.0066

5. Hudson HM, Larkin RS. Accelerated image reconstruction using ordered subsets of projection data. *IEEE Trans Med Imaging.* 1994;13(4):601–609. https://doi.org/10.1109/42.363108

6. Shepp LA, Vardi Y. Maximum likelihood reconstruction for emission tomography. *IEEE Trans Med Imaging.* 1982;1(2):113–122. https://doi.org/10.1109/TMI.1982.4307558

7. Müller-Gärtner HW, Links JM, Prince JL, et al. Measurement of radiotracer concentration in brain gray matter using positron emission tomography: MRI-based correction for partial volume effects. *J Cereb Blood Flow Metab.* 1992;12(4):571–583. https://doi.org/10.1038/jcbfm.1992.81

8. Rousset OG, Ma Y, Evans AC. Correction for partial volume effects in PET: principle and validation. *J Nucl Med.* 1998;39(5):904–911. https://jnm.snmjournals.org/content/39/5/904

9. Innis RB, Cunningham VJ, Delforge J, et al. Consensus nomenclature for in vivo imaging of reversibly binding radioligands. *J Cereb Blood Flow Metab.* 2007;27(9):1533–1539. https://doi.org/10.1038/sj.jcbfm.9600493

10. Phelps ME, Hoffman EJ, Mullani NA, Ter-Pogossian MM. Application of annihilation coincidence detection to transaxial reconstruction tomography. *J Nucl Med.* 1975;16(3):210–224. https://jnm.snmjournals.org/content/16/3/210 — the founding coincidence-detection PET tomography paper.

## Where to next

- Foundations: [../foundations/physics.md](../foundations/physics.md) — radioactive decay, photon attenuation.

- MRS: [./mrs.md](./mrs.md) — the molecular-specificity sibling within MRI.

- qMRI: [./qmri.md](./qmri.md) — quantitative MRI for multimodal PET-MR studies.

- Analysis: [../../analysis/structural.md](../../analysis/structural.md) — segmentations consumed by PVC.

- Registration: [../medical-imaging/registration.md](../medical-imaging/registration.md) — PET to MR alignment.

### Closing

PET is the only widespread in vivo tool that returns *molecular* signal. Earn it with proper input functions, partial-volume correction, attenuation correction, and Centiloid (where it applies). SUVR is a screening tool; kinetic modelling is the science.
