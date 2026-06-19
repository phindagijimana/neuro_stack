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

The full [Stejskal–Tanner](https://doi.org/10.1063/1.1695690) expression for a rectangular gradient pair of amplitude $G$, duration $\delta$, and separation $\Delta$ is

$$
b = \gamma^2 G^2 \delta^2 \left(\Delta - \frac{\delta}{3}\right),
$$

with $\gamma$ the gyromagnetic ratio. Three things to internalise:

- **$G$ dominates.** $b \propto G^2$. Doubling gradient amplitude quadruples b at fixed timing. Connectome-scale b > 5000 s/mm² requires Connectom-class gradients ($\geq 80$ mT/m), not clinical 40 mT/m systems.
- **$\delta$ enters quadratically.** Lengthening the encoding lobe is cheap until $\delta \to \Delta$ and the geometric factor $(\Delta - \delta/3)$ saturates.
- **$\Delta$ sets the diffusion time** — the timescale over which restriction is probed. Resolving cortical neurite radii ($\sim 1\,\mu$m) requires short $\Delta$ at high $G$.

### 2.4 ADC

- Apparent diffusion coefficient — effective diffusivity along encoding direction in tissue (microstructure + perfusion effects at low b in some models).

Log-linear model (mono-exponential, often used clinically):

\[
\frac{S}{S_0} = e^{-b \cdot \mathrm{ADC}}
\]

(Single direction DWI image is not “the ADC” — ADC maps require multiple b values or appropriate fitting.)

### 2.5 q-space sampling — the intuition

The b-value is a scalar summary; the underlying object is a vector — the **q-vector**:

$$
\mathbf{q} = \gamma\,\delta\,\mathbf{G},
$$

where $\gamma$ is the gyromagnetic ratio, $\delta$ the diffusion-gradient duration, and $\mathbf{G}$ the gradient vector. The Stejskal–Tanner result is a *Fourier* relationship between the (normalised) diffusion signal $E(\mathbf{q})$ and the ensemble-average displacement propagator $P(\mathbf{r}, \tau)$:

$$
E(\mathbf{q}) = \int P(\mathbf{r},\tau)\,e^{-i\,2\pi\,\mathbf{q}\cdot\mathbf{r}}\,d\mathbf{r}.
$$

In words: by sampling enough points in q-space, you can reconstruct the probability distribution of where water molecules went during time $\tau$. b-values are radii in q-space ($|\mathbf{q}|^2 \propto b/\tau$); diffusion directions are points on a sphere of that radius.

**Why single-shell DTI under-samples q-space.** DTI typically uses one shell (e.g. b = 1000 s/mm²) with 30 directions. That is one radius and a sparse spherical sampling. You cannot resolve non-Gaussian features (kurtosis, restriction) without a second radius, and you cannot resolve crossing-fibre angular structure without denser angular sampling.

**Multi-shell intuition.** Each b-shell probes a different displacement scale: low b is dominated by fast (extra-axonal, free water) diffusion; high b is dominated by slow / restricted (intra-axonal) signal. A canonical protocol of three shells — b = 1000 / 2000 / 3000 s/mm² — recovers enough of the q-space landscape to fit non-Gaussian and multi-compartment models (see [advanced-diffusion](./advanced-diffusion.md)).

**Spherical-design vs grid sampling.** On a single shell you want directions that are *uniformly distributed on the sphere* so that the angular Fourier basis (spherical harmonics) is well-conditioned. Three workhorse schemes:

- **Jones30 / Jones60** ( Jones, Horsfield & Simmons 1999) — minimum-energy electrostatic-repulsion sets of 30 and 60 directions. Still the de facto vendor default for clinical DTI.
- **Electrostatic-repulsion / spherical t-designs** — generalise Jones to arbitrary shell sizes.
- **Caruyer 2013 incremental scheme** — multi-shell sampling that is uniform on each shell *and* uniform when the scan is prematurely truncated (motion, dropout). Strongly recommended for multi-shell.

Cartesian-grid q-space sampling (DSI) requires hundreds of measurements and is largely historical.

**Rule of thumb for protocol design.**

| Goal | b-shells (s/mm²) | Directions per shell |
|---|---|---|
| Clinical DWI / ADC | 0, 1000 | 3–6 (trace) |
| Single-tensor DTI | 0, 1000 | 30 (Jones30 minimum) |
| HARDI / CSD | 0, 2000–3000 | 60–90 |
| MSMT-CSD / NODDI / DKI | 0, 1000, 2000 (± 3000) | 30 / 60 / 60 |

Always include ≥1 reversed phase-encode b0 for [`topup`](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup). Record $\Delta$ and $\delta$ — biophysical models need them. For protocol templates, see the [HCP Lifespan diffusion protocol](https://www.humanconnectome.org/study/hcp-lifespan-development/document/diffusion-mri-protocol) and the [MRtrix3 documentation](https://mrtrix.readthedocs.io/en/latest/).

### 2.6 Multi-band acceleration — the angular-coverage trade

A DWI volume is a stack of EPI slices. Simultaneous-multi-slice (SMS / multi-band, [Larkman 2001](https://doi.org/10.1002/jmri.1241), [Setsompop 2012](https://doi.org/10.1002/mrm.23097)) excites $M$ slices at once and unmixes them with coil sensitivities — shortening per-volume TR by a factor of $M$. That extra time budget is *what makes high-angular HARDI and multi-shell protocols feasible at all* on clinical scanners.

The trade-off chain:

- **MB factor $M$ → TR / $M$.** A 64-slice 2.0 mm protocol drops from TR ≈ 9 s (single-band) to ≈ 2 s (MB = 4) at HCP-grade gradients.
- **More angular directions per session.** That 4–5× speedup pays directly for higher-b shells and more directions.
- **Cost: g-factor noise** and slice-leakage artefacts when coil sensitivities are not well-separated along the slice axis. Inspect [eddy QC](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy) and `LeakBlock`-style reconstruction.
- **Practical ceiling.** MB 3–4 is routine at 3 T with a 32-channel head coil; MB 6–8 is HCP / Connectome territory and benefits from blipped-CAIPI (Setsompop 2012) to spread aliasing across PE.

## 3. Pulse sequence families

## 4. Acquisition parameters

## 5. Artifacts and mitigations

## 6. DTI and beyond (overview)

- DTI: ≥6 non-collinear directions → 3×3 symmetric tensor estimate → FA, MD, tractography (streamline algorithms — many pitfalls).

- HARDI / multi-shell: Crossing fibers violate single-tensor model → higher order models (CSD, etc.) — research pipelines.

### 6.1 DTI vs CSD — model assumptions

The single-tensor model fits a $3\times3$ symmetric positive-definite matrix $\mathbf{D}$ to

$$
S(\mathbf{g}, b) = S_0\,\exp\!\left(-b\,\mathbf{g}^\top \mathbf{D}\,\mathbf{g}\right).
$$

That is **one Gaussian** per voxel, with **one principal direction**. It is wrong in most of white matter.

**Where DTI fails.**

- **Crossing / kissing / fanning fibres.** Jeurissen 2013 estimates 60–90% of WM voxels contain more than one fibre population. The single-tensor estimate flattens — FA drops, the principal eigenvector wanders — and tractography snaps to the dominant bundle.
- **Partial volume with CSF.** A fast isotropic compartment inflates MD and crushes FA near ventricles and sulci.
- **Restricted / non-Gaussian regimes.** Above b ≈ 1500 s/mm² the log-signal curves; DTI absorbs this curvature into a biased $\mathbf{D}$.

**HARDI insight.** Drop the tensor altogether. Sample many directions on a high-b shell and estimate the full angular profile of the diffusion signal — the **orientation distribution function (ODF)** — on the sphere, typically via a spherical-harmonic basis. HARDI on its own buys angular resolution but not biophysical specificity.

**CSD (Tournier 2007).** The diffusion signal on the sphere is modelled as a *convolution* of a single-fibre **response function** $R$ with an unknown **fibre ODF (fODF)** $f$:

$$
S(\mathbf{g}) = \int_{S^2} R(\mathbf{g}\cdot\mathbf{u})\,f(\mathbf{u})\,d\mathbf{u}.
$$

Constrained Spherical Deconvolution inverts this with a non-negativity constraint on $f$. The fODF recovers multiple peaks per voxel — the basis of modern tractography. Caveat: classic CSD assumes a *spatially constant* response function — wrong wherever WM/GM/CSF mix. **MSMT-CSD** ( Jeurissen 2014) relaxes this with multi-tissue response functions estimated from multi-shell data — see [advanced-diffusion](./advanced-diffusion.md).

**Tensor positivity in practice.** Naive ordinary least squares (OLS) on $\ln(S/S_0)$ can return a $\mathbf{D}$ with negative eigenvalues — physically nonsense. Two standard fixes:

- **Weighted least squares (WLS)** — weights each equation by $S^2$ to undo the log-induced heteroscedasticity.
- **Non-linear least squares (NLLS)** — fits $S$ directly in the original (non-log) space; slower, more robust, and almost always returns positive-definite tensors.

For tractography-grade DTI use WLS at minimum; NLLS for quantitative tensor maps.

**One-line comparison.**

| Model | Voxel assumption | Min acquisition | Recovers | Fails when |
|---|---|---|---|---|
| DTI | Single Gaussian, one direction | 1 shell, 30 directions | $\mathbf{D}$ → FA, MD, V1 | Crossings, CSF mix, b > 1500 |
| HARDI / qball | Arbitrary ODF on a shell | 1 high-b shell, 60+ dir | Diffusion ODF | No compartment / tissue specificity |
| CSD | fODF = response ⊛ fibre density | 1 high-b shell, 60+ dir | Multi-peak fODF | Response function not spatially constant |
| MSMT-CSD | Tissue-specific responses | ≥2 shells + b0, 60+ dir | WM / GM / CSF fODFs | Very low SNR, severe motion |

**FOD spherical-harmonic order $l_\text{max}$.** The fODF is expanded in even-order spherical harmonics up to order $l_\text{max}$. The number of free coefficients is $(l_\text{max} + 1)(l_\text{max} + 2)/2$ — 28 at $l_\text{max} = 6$, 45 at $l_\text{max} = 8$. As a rule of thumb: $l_\text{max} = 6$ needs ≥28 directions per shell, $l_\text{max} = 8$ needs ≥45, $l_\text{max} = 10$ needs ≥66. Higher $l_\text{max}$ resolves sharper peaks but amplifies noise. Set it from your direction budget, not from defaults.

### 6.2 Tractography post-processing — ACT, SIFT2, and bundle QC

Streamline tractography from CSD or DTI is *biased*: streamlines preferentially track strong, long bundles and leave the cortex underseeded. Two indispensable post-hoc correctors:

- **ACT — Anatomically-Constrained Tractography** ([Smith 2012](https://doi.org/10.1016/j.neuroimage.2012.06.005)). Uses a 5-tissue-type segmentation (cortical GM, sub-cortical GM, WM, CSF, pathological) from a registered T1 to gate streamline generation. Streamlines that enter CSF, exit the WM-GM boundary into deep WM, or terminate mid-WM are rejected or truncated at the cortical surface. Without ACT, a substantial fraction of streamlines terminate inside white matter — a geometric artefact, not biology. [`tckgen -act`](https://mrtrix.readthedocs.io/en/latest/quantitative_structural_connectivity/act.html) is the MRtrix3 entry point.
- **SIFT2 — Spherical-deconvolution Informed Filtering of Tractograms** ([Smith 2015](https://doi.org/10.1016/j.neuroimage.2015.06.092)). Assigns a *weight* to each streamline so that the bundle population reproduces the underlying fODF amplitudes voxel-by-voxel. Crucial when computing edge weights in connectomes: raw streamline counts are not quantitative, SIFT2-weighted sums approximately are.

**How good is this in practice?** The **[Tractometer](http://www.tractometer.org/)** project ([Côté 2013](https://doi.org/10.1016/j.media.2013.03.009), [Maier-Hein 2017](https://doi.org/10.1038/s41467-017-01285-x)) is the standard phantom benchmark: known ground-truth bundles in a digital phantom, then score tractography pipelines on valid-bundle recovery, invalid bundles, and average bundle coverage. Headline finding (Maier-Hein 2017, ISMRM-2015 challenge): even the best 2015-era pipelines recovered ~90% of valid bundles but produced 4× more *invalid* bundles. Default tractography is not a measurement of anatomy. Use ACT + SIFT2 + bundle segmentation ([TractSeg](https://github.com/MIC-DKFZ/TractSeg), [RecoBundles](https://docs.dipy.org/stable/examples_built/streamline_analysis/recobundles_isbi2018.html)) and report Tractometer-style sanity checks where possible.

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

- Jones DK, Horsfield MA, Simmons A. Optimal strategies for measuring diffusion in anisotropic systems by magnetic resonance imaging. *Magn Reson Med.* 1999;42(3):515–525. https://doi.org/10.1002/(SICI)1522-2594(199909)42:3<515::AID-MRM14>3.0.CO;2-Q

- Tournier J-D, Calamante F, Connelly A. Robust determination of the fibre orientation distribution in diffusion MRI: non-negativity constrained super-resolved spherical deconvolution. *Neuroimage.* 2007;35(4):1459–1472. https://doi.org/10.1016/j.neuroimage.2007.02.016

- Jeurissen B, Leemans A, Tournier J-D, Jones DK, Sijbers J. Investigating the prevalence of complex fiber configurations in white matter tissue with diffusion MRI. *Hum Brain Mapp.* 2013;34(11):2747–2766. https://doi.org/10.1002/hbm.22099

- Caruyer E, Lenglet C, Sapiro G, Deriche R. Design of multishell sampling schemes with uniform coverage in diffusion MRI. *Magn Reson Med.* 2013;69(6):1534–1540. https://doi.org/10.1002/mrm.24736

- Larkman DJ, et al. Use of multicoil arrays for separation of signal from multiple slices simultaneously excited. *J Magn Reson Imaging.* 2001;13(2):313–317. https://doi.org/10.1002/jmri.1241

- Setsompop K, et al. Blipped-CAIPI multi-band EPI with reduced g-factor penalty. *Magn Reson Med.* 2012;67(5):1210–1224. https://doi.org/10.1002/mrm.23097

- Smith RE, Tournier J-D, Calamante F, Connelly A. Anatomically-constrained tractography (ACT). *NeuroImage.* 2012;62(3):1924–1938. https://doi.org/10.1016/j.neuroimage.2012.06.005

- Smith RE, Tournier J-D, Calamante F, Connelly A. SIFT2: Enabling dense quantitative assessment of brain white matter connectivity. *NeuroImage.* 2015;119:338–351. https://doi.org/10.1016/j.neuroimage.2015.06.092

- Maier-Hein KH, et al. The challenge of mapping the human connectome based on diffusion tractography. *Nat Commun.* 2017;8(1):1349. https://doi.org/10.1038/s41467-017-01285-x

## 13. Credible online resources

- [MRtrix3 user documentation](https://mrtrix.readthedocs.io/en/latest/) — CSD, ACT, SIFT2, `dwi2response`, `tckgen`, MSMT-CSD.
- [DIPY user guide](https://docs.dipy.org/stable/) — DTI / DKI / NODDI / CSD in Python; example gallery worth reading.
- [FSL `topup` and `eddy`](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/) — distortion + motion / eddy-current correction.
- [Tractometer phantom suite](http://www.tractometer.org/) — track-level evaluation against ground truth.
- [HCP Lifespan diffusion protocol PDF](https://www.humanconnectome.org/study/hcp-lifespan-development/document/diffusion-mri-protocol) — gold-standard 3-shell + reversed-PE multi-band protocol.
- [QSIPrep](https://qsiprep.readthedocs.io/en/latest/) — BIDS-app preprocessing of multi-shell DWI.
- [mriquestions — DWI](https://mriquestions.com/what-is-diffusion.html) — clinical-physics primer.

## 14. References (sources used to create this content)

- [FSL documentation — eddy, topup](https://fsl.fmrib.ox.ac.uk/)
- [MRtrix3 docs — CSD, ACT, SIFT2](https://mrtrix.readthedocs.io/en/latest/)
- [DIPY user guide](https://docs.dipy.org/stable/)
- Hagmann P, et al. *Diffusion MRI* — introductory chapters.
- Vendor DWI pulse sequence manuals.

### Closing

Mandatory pairing: EPI ( readout), SpinEcho ( refocusing concept), preprocessing scripts in `training/pipelines` where listed.