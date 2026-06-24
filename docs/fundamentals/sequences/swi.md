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

## Medical / clinical relevance

**Beginner — what it's used for, in one sentence.** SWI is GRE on steroids — combines magnitude and phase to make microbleeds, veins, and iron impossible to miss.

This expands the placeholder §4 ("Clinical and research uses") with disease-specific content.

### Routine clinical use

- **Traumatic microbleeds** — SWI roughly doubles the microbleed detection rate compared with T2\*/GRE; the standard sequence for moderate-to-severe TBI and concussion research.
- **Cavernous malformations** — more sensitive than GRE for small or familial cavernomas; replaces GRE in most modern stroke protocols.
- **Venous mapping** — clearly resolves cortical and deep venous anatomy without contrast; used for DBS targeting, surgical planning, and venous sinus thrombosis follow-up.
- **MS lesion characterisation** — central vein sign (CVS) for MS diagnosis (vs CSVD mimics); paramagnetic rim lesions (PRL) for chronic active inflammation.
- **Acute stroke** — "brush sign" (prominent ipsilateral deep medullary veins) indicates impaired oxygen extraction distal to large-vessel occlusion.

### Disease applications

| Disease | Imaging finding | Clinical value | Cross-link |
|---|---|---|---|
| TBI / diffuse axonal injury | Petechial microbleeds at GM-WM junction, corpus callosum, brainstem | Doubles microbleed detection vs T2\*/GRE; prognostic for outcome | [clinical/stroke-and-tbi.md](../../clinical/stroke-and-tbi.md) |
| Cerebral cavernous malformations | Popcorn lesion with prominent hemosiderin rim | More sensitive than GRE; familial CCM screening | — |
| Multiple sclerosis | Central vein sign (CVS, ≥ 40 % rule) and paramagnetic-rim lesions (PRL) | MS diagnosis vs CSVD mimics; PRL marks chronic active inflammation | [clinical/multiple-sclerosis.md](../../clinical/multiple-sclerosis.md) |
| Cerebral amyloid angiopathy (CAA) | Lobar cerebral microbleeds + cortical superficial siderosis | Boston criteria 2.0 imaging biomarker; ICH risk stratification | [clinical/alzheimers-and-dementia.md](../../clinical/alzheimers-and-dementia.md) |
| Acute large-vessel-occlusion stroke | Prominent veins distal to occlusion ("brush sign") | Indicates penumbra at risk; correlates with infarct growth | [clinical/stroke-and-tbi.md](../../clinical/stroke-and-tbi.md) |
| Parkinson's disease | Loss of nigrosome-1 ("swallow-tail sign") in SNpc on high-resolution SWI | Differentiates PD from healthy controls and essential tremor | [clinical/parkinsons-and-movement.md](../../clinical/parkinsons-and-movement.md) |

Seminal references for each row:

- SWI doubles microbleed detection in TBI: Tong KA, Ashwal S, Holshouser BA, et al. Diffuse axonal injury in children: clinical correlation with hemorrhagic lesions. *Radiology.* 2008;247(3):816–824. [doi:10.1148/radiol.2473070994](https://doi.org/10.1148/radiol.2473070994).
- Cavernoma SWI sensitivity: de Souza JM, Domingues RC, Cruz LCH Jr, Domingues FS, Iasbeck T, Gasparetto EL. Susceptibility-weighted imaging for the evaluation of patients with familial cerebral cavernous malformations. *AJNR Am J Neuroradiol.* 2008;29(1):154–158. [doi:10.3174/ajnr.A0851](https://doi.org/10.3174/ajnr.A0851).
- MS central vein sign: Sati P, Oh J, Constable RT, et al. The central vein sign and its clinical evaluation for the diagnosis of multiple sclerosis: a consensus statement from the NAIMS Cooperative. *Nat Rev Neurol.* 2016;12(12):714–722. [doi:10.1038/nrneurol.2016.166](https://doi.org/10.1038/nrneurol.2016.166).
- MS paramagnetic-rim lesions: Absinta M, Sati P, Masuzzo F, et al. Association of chronic active multiple sclerosis lesions with disability in vivo. *JAMA Neurol.* 2019;76(12):1474–1483. [doi:10.1001/jamaneurol.2019.2399](https://doi.org/10.1001/jamaneurol.2019.2399).
- CAA microbleeds + superficial siderosis: Charidimou A, Boulouis G, Gurol ME, et al. Emerging concepts in sporadic cerebral amyloid angiopathy. *Neurology.* 2017;89(20):2128–2135. [doi:10.1212/WNL.0000000000003610](https://doi.org/10.1212/WNL.0000000000003610).
- Brush sign in acute stroke: Hermier M, Nighoghossian N. Contribution of susceptibility-weighted imaging to acute stroke assessment. *Stroke.* 2008;39(5):e60. [doi:10.1161/STROKEAHA.107.512525](https://doi.org/10.1161/STROKEAHA.107.512525).
- Nigrosome-1 sign in PD: Schwarz ST, Afzal M, Morgan PS, Bajaj N, Gowland PA, Auer DP. The 'swallow tail' appearance of the healthy nigrosome — a new accurate test of Parkinson's disease: a case-control and retrospective cross-sectional MRI study at 3T. *Neurology.* 2014;82(7):547–554. [doi:10.1212/WNL.0000000000000928](https://doi.org/10.1212/WNL.0000000000000928).

### Research depth

The big specialist question on top of SWI is **SWI-derived QSM as a quantitative iron / myelin biomarker**. QSM-derived susceptibility in the substantia nigra is a replicated PD biomarker (Acosta-Cabronero 2017); in MS, paramagnetic rims around chronic lesions reflect ongoing iron-laden microglia and predict disability progression beyond T2 lesion count; in Alzheimer's, cortical χ correlates with amyloid PET (Tiepolt 2018) and may track iron-amyloid interaction. **High-resolution SWI / QSM at 7 T** enables laminar venous mapping (penetrating-vessel resolution), with implications for understanding BOLD specificity and laminar fMRI quantification. The SWI-MR-angiography hybrid (SWAN, multi-echo SWI) extends to **cerebrovascular reserve mapping** for steno-occlusive disease without contrast.

Tooling is moving rapidly. **Deep-learning susceptibility unwrapping and inversion** — xQSM ([Bollmann 2019](https://doi.org/10.1016/j.neuroimage.2019.116207)), DeepQSM, RTS-Net, QSMNet+ — has compressed the QSM pipeline from minutes-to-hours of MEDI / STI iteration down to seconds while improving streak artefact handling. The 2024 QSM Reconstruction Challenge benchmarks are now driving methodological standardisation. **DBS planning** is the highest-impact clinical translation: SWI clearly resolves the STN and GPi, and high-resolution 7 T QSM has displaced classical T2 for direct STN visualisation at several DBS centres. For automated PRL detection in MS, see deep-learning tools surveyed at [tools/index.md](../../tools/index.md); for the broader susceptibility-physics context, see [gre.md](./gre.md) and [qmri.md](./qmri.md).

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