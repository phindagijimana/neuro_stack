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

## Medical / clinical relevance

**Beginner — what it's used for, in one sentence.** GRE / T2\* highlights anything paramagnetic — blood, iron, calcium — making it indispensable for haemorrhage detection.

This section consolidates and expands the placeholder §4 ("Clinical and research uses").

### Routine clinical use

- **Acute intracranial haemorrhage exclusion** — every stroke MRI includes a T2\*/GRE (or SWI) sequence; T2\*/GRE outperforms CT for posterior-fossa and subacute haemorrhage detection.
- **Cerebral microbleeds** — paramagnetic haemosiderin deposits create blooming hypointensities; the substrate for cerebral amyloid angiopathy (CAA) and hypertensive small-vessel disease scoring (MARS, BOMBS).
- **Cavernous malformations** — the "popcorn" lesion with hemosiderin rim is the classic GRE finding; pre-operative mapping for resection.
- **Hemorrhagic transformation after stroke** — GRE differentiates HI-1, HI-2, PH-1, PH-2 categories (ECASS criteria) post-thrombolysis or post-thrombectomy.
- **Calcification detection** (when paired with phase or CT) — GRE blooming + phase polarity differentiates calcium from blood (CT correlation still gold standard).

### Disease applications

| Disease | Imaging finding | Clinical value | Cross-link |
|---|---|---|---|
| Acute intracranial haemorrhage | Blooming hypointensity on T2\*/GRE within minutes of bleed | More sensitive than CT for posterior fossa and subacute blood | [clinical/stroke-and-tbi.md](../../clinical/stroke-and-tbi.md) |
| Cerebral amyloid angiopathy (CAA) | Lobar microbleeds + cortical superficial siderosis | Boston criteria 2.0 diagnostic biomarker; predicts ICH risk | [clinical/alzheimers-and-dementia.md](../../clinical/alzheimers-and-dementia.md) |
| Cavernous malformations | Popcorn lesion with hemosiderin rim (Zabramski I–IV) | Risk stratification for bleeding; surgical decision-making | — |
| Hemorrhagic transformation post-stroke | Petechial vs parenchymal haematoma on T2\*/GRE | ECASS classification informs anticoagulation timing | [clinical/stroke-and-tbi.md](../../clinical/stroke-and-tbi.md) |
| Diffuse axonal injury (TBI) | Petechial haemorrhages at grey-white junction, corpus callosum, brainstem | Prognostic marker; SWI more sensitive (see [swi.md](./swi.md)) | [clinical/stroke-and-tbi.md](../../clinical/stroke-and-tbi.md) |
| Brain tumours (haemorrhagic mets, GBM) | Intratumoural haemorrhage on T2\*/GRE | Melanoma / choriocarcinoma / RCC metastasis prediction | — |

Seminal references for each row:

- GRE vs CT for acute haemorrhage: Fiebach JB, Schellinger PD, Gass A, et al. Stroke MRI is accurate in hyperacute intracerebral haemorrhage — multicenter study on the validity of stroke imaging. *Stroke.* 2004;35(2):502–506. [doi:10.1161/01.STR.0000118699.93720.83](https://doi.org/10.1161/01.STR.0000118699.93720.83).
- CAA microbleeds (Boston criteria foundation): Knudsen KA, Rosand J, Karluk D, Greenberg SM. Clinical diagnosis of cerebral amyloid angiopathy: validation of the Boston criteria. *Neurology.* 2001;56(4):537–539. [doi:10.1212/WNL.56.4.537](https://doi.org/10.1212/WNL.56.4.537).
- Cavernoma classification: Zabramski JM, Wascher TM, Spetzler RF, et al. The natural history of familial cavernous malformations: results of an ongoing study. *J Neurosurg.* 1994;80(3):422–432. [doi:10.3171/jns.1994.80.3.0422](https://doi.org/10.3171/jns.1994.80.3.0422).
- ECASS haemorrhagic transformation criteria: Berger C, Fiorelli M, Steiner T, et al. Hemorrhagic transformation of ischemic brain tissue: asymptomatic or symptomatic? *Stroke.* 2001;32(6):1330–1335. [doi:10.1161/01.STR.32.6.1330](https://doi.org/10.1161/01.STR.32.6.1330).

### Research depth

The specialist conversation around GRE is **quantitative susceptibility mapping (QSM)** and **multi-echo GRE biomarkers**. A 3D multi-echo GRE acquisition (5–8 echoes from ~5–40 ms) feeds both R2\* fitting (iron concentration proxy) and the QSM inverse problem (phase → χ map in ppm). QSM has produced replicated biomarkers across diseases: substantia-nigra susceptibility in Parkinson's disease and nigrosome-1 absence ([Schwarz 2014](https://doi.org/10.1212/WNL.0000000000000928)), paramagnetic-rim lesions (PRL) in MS as a marker of chronic active lesions ([Absinta 2019](https://doi.org/10.1001/jamaneurol.2019.2399)), and amyloid-related microhaemorrhage in Alzheimer's. See [swi.md](./swi.md) for the SWI / QSM bridge and [qmri.md](./qmri.md) for the multi-parameter quantitative-MRI framework that subsumes multi-echo GRE.

The other research thread is **functional connectivity from T2\* GRE** — BOLD fMRI is, after all, just a long-TR GRE-EPI readout sensitised to T2\*. Beyond fMRI, breath-hold and hypercapnia-challenge GRE map cerebrovascular reactivity (CVR) for steno-occlusive disease, Moyamoya, and pre-CEA planning. Rapid single-shot / single-breath-hold GRE variants enable fetal in-utero detection of intracranial haemorrhage (Daldrup-Link 2010), and intra-operative GRE during awake craniotomy verifies surgical haemostasis within minutes. Deep-learning susceptibility unwrapping (xQSM, [Liu 2020](https://doi.org/10.1002/mrm.28195); RTS-Net) is rapidly displacing classical Laplacian-based unwrapping in research pipelines, with FDA-clearance pending for clinical QSM products from several vendors.

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