# Diffusion-weighted imaging (DWI) — full course

Course map: Diffusion physics → b-table → ADC → artifacts → DTI / HARDI → preprocessing → analysis outputs & derivatives → how outputs are used → clinical → examples → references.

## 1. Learning objectives

- Explain why motion of water molecules reduces signal when strong diffusion-encoding gradients are applied.

- Compute order-of-magnitude b-value scaling with gradient amplitude and duration ( qualitative G² dependence).

- Define ADC from multi-b signal model S/S₀ = exp(−b·ADC) ( Gaussian approximation).

- List EPI-related artifacts in DWI and name mitigations (PE polarity, fieldmaps, eddy).

- Outline DTI (≥6 directions) vs HARDI / multi-shell rationale.

- List standard derivative files (eddy-corrected DWI, FA, MD, V1, tractography, connectome matrices) and match each to a research or clinical use case.

## 2. Physics — what DWI measures

### 2.1 Random walk

- Water diffusion is random Brownian motion. Without barriers, mean-squared displacement grows linearly with time (Einstein relation links to D).

### 2.2 Stejskal–Tanner

- Two matched diffusion-encoding gradient lobes before and after the 180° refocusing pulse ( spin-echo DWI) encode phase accumulation proportional to displacement between lobes.

- Static spins rephase; diffusing spins lose phase coherence → signal attenuation increases with stronger encoding (higher b).

### 2.3 b-value (conceptual)

- b summarizes gradient strength, duration, and spacing — units s/mm². Higher b → more diffusion weighting → lower signal ( fixed ADC).

### 2.4 ADC

- Apparent diffusion coefficient — effective diffusivity along encoding direction in tissue (microstructure + perfusion effects at low b in some models).

Log-linear model (mono-exponential, often used clinically):

\[
\frac{S}{S_0} = e^{-b \cdot \mathrm{ADC}}
\]

(Single direction DWI image is not “the ADC” — ADC maps require multiple b values or appropriate fitting.)

## 3. Pulse sequence families

## 4. Acquisition parameters

## 5. Artifacts and mitigations

## 6. DTI and beyond (overview)

- DTI: ≥6 non-collinear directions → 3×3 symmetric tensor estimate → FA, MD, tractography (streamline algorithms — many pitfalls).

- HARDI / multi-shell: Crossing fibers violate single-tensor model → higher order models (CSD, etc.) — research pipelines.

## 7. Preprocessing stack (typical research)

- Convert DICOM → NIfTI

- Denote PE direction and index

- `topup` ( if AP/PA or blip-up/down)

- `eddy` ( motion + eddy distortion)

- Brain mask, tensor fit or model of choice

## 8. Analysis outputs, derivatives, and how they are used

### 8.1 Core files after motion / distortion correction

### 8.2 Model-based maps (tensor and beyond)

### 8.3 Tractography and connectivity outputs

### 8.4 Mapping research questions to outputs

### 8.5 Integration with T1 / fMRI

- Register FA or b0 → T1w (or inverse) before labeling tracts with atlas ROIs**.

- Functional connectivity (EPI) and structural connectivity (DWI) both use parcellations — do not mix spaces without resampling and documentation.

## 9. Clinical pearls

- Acute ischemia: restricted diffusion → bright DWI, low ADC.

- T2 shine-through: high T2 lesion can look bright on DWI without true restriction — check ADC map.

- Abscess vs necrotic tumor: ADC patterns — radiology context.

## 10. Worked examples

### Example A — Signal drop

- ADC = 0.7×10⁻³ mm²/s, b = 1000 → S/S₀ = exp(−0.7) ≈ 0.50 ( illustrative).

### Example B — TE impact

- Same b, TE increases from 70 to 90 ms → T2 decay additional loss — why protocols fight for short TE.

## 11. Pitfalls

- Interpreting single direction DWI as “diffusion tensor result”.

- Ignoring distortion when overlaying DWI on T1 — must resample after topup / syn fieldmap.

## 12. Credible peer-reviewed papers

- Stejskal EO, Tanner JE. Spin diffusion measurements: spin echoes in the presence of a time-dependent field gradient. *J Chem Phys.* 1965;42(1):288–292. https://doi.org/10.1063/1.1695690

- Le Bihan D, et al. Separation of diffusion and perfusion in intravoxel incoherent motion MR imaging. *Radiology.* 1988;168(2):497–505. https://doi.org/10.1148/radiology.168.2.3393671

- Basser PJ, et al. MR diffusion tensor spectroscopy and imaging. *Biophys J.* 1994;66(1):259–267. https://doi.org/10.1016/S0006-3495(94)80775-180775-1)

## 13. Credible online resources

- FSL — eddy, topup

- mriquestions — DWI

## 14. References (sources used to create this content)

- FSL documentation — eddy, topup — https://fsl.fmrib.ox.ac.uk/

- Hagmann P, et al. *Diffusion MRI* — introductory chapters.

- Vendor DWI pulse sequence manuals.

### Closing

Mandatory pairing: EPI ( readout), SpinEcho ( refocusing concept), preprocessing scripts in `training/pipelines` where listed.