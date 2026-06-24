# Enhancement & quality

> The step between reconstruction and analysis that quietly determines whether your downstream numbers are honest. Denoising, bias correction, artifact removal, super-resolution, and the automated QC that catches what humans miss.

## 1. Theory

Reconstructed images carry residual structured error — slowly varying bias from coil sensitivity, intensity noise that scales with signal, motion ghosting, Gibbs ringing at sharp edges. Each error class has a characteristic statistical signature; modelling that signature lets you remove the error without destroying signal.

We model the observed image as

$$
I_{\mathrm{obs}}(\vec r) = B(\vec r) \cdot I_{\mathrm{true}}(\vec r) + n(\vec r)
$$

where $B$ is the bias field, $n$ is residual noise (potentially non-Gaussian and spatially correlated), and the assumed multiplicative form distinguishes intensity inhomogeneity from additive noise.

Two enhancement strategies:

- **Model-driven** — explicit statistical model + parameter estimation (N4, NLM, MP-PCA).
- **Learned** — a network trained on paired clean/noisy data, or self-supervised (Noise2Noise, Noise2Self).

## 2. Mathematics

### Bias-field correction — N4

[N4ITK](https://doi.org/10.1109/TMI.2010.2046908) (Tustison et al., 2010) iteratively refines a smooth bias field $B$ by alternating histogram sharpening with B-spline smoothing:

$$
\log B^{(k+1)} = \mathrm{Smooth}\!\left( \log I_{\mathrm{obs}} - \log \hat I_{\mathrm{true}}^{(k)} \right)
$$

Default `--bspline-fitting [200,3]` controls smoothness; tighter `[100, 4]` for high-resolution data.

### Non-local means denoising

NLM ([Buades et al., 2005](https://doi.org/10.1109/CVPR.2005.38)) replaces each voxel with a weighted average of patches whose neighbourhood matches:

$$
\hat I(v) = \frac{1}{C(v)} \sum_{u \in \Omega(v)} w(u, v)\, I(u),
\quad w(u, v) = \exp\!\left(-\tfrac{\|N(I, v) - N(I, u)\|^2}{h^2}\right)
$$

with $N(\cdot)$ a small patch. The MR-specific variant [Manjón et al., 2010](https://doi.org/10.1002/jmri.22003) adapts $h$ per voxel.

### MP-PCA — patch-PCA noise estimation for DWI

DWI volumes share a low-rank structure. [Veraart et al., 2016](https://doi.org/10.1016/j.neuroimage.2016.08.016) propose:

1. Extract overlapping 4D patches.
2. Compute SVD per patch.
3. Truncate singular values above the **Marchenko-Pastur** noise threshold:

$$
\sigma^2 = \tfrac{1}{N - M} \sum_{i > M} \lambda_i, \qquad
M = \arg\min_M \left| \lambda_M - 4 \sqrt{\tfrac{N - M}{N}}\, \sigma^2 \right|
$$

`dwidenoise` in MRtrix3 implements this. Removes ~30% noise variance from typical DWI with no resolution loss.

### NORDIC — for fMRI

[NORDIC](https://doi.org/10.1016/j.neuroimage.2021.117941) (Vizioli et al., 2021) extends MP-PCA to complex-valued fMRI to reduce thermal noise without smoothing. Pre-acquisition magnitude-and-phase data required.

### Gibbs unringing

Sharp edges in MR produce ringing artefacts from truncated k-space. The sub-voxel shift method ([Kellner et al., 2016](https://doi.org/10.1002/mrm.26054)) interpolates between optimal sub-voxel shifts to suppress oscillations. `mrdegibbs` in MRtrix3.

### Super-resolution

Given a low-resolution image, recover a high-resolution one. Model:

$$
I_{LR} = D B I_{HR} + n
$$

where $D$ down-samples and $B$ blurs (PSF). Reconstruction methods: bicubic, RKHS, sparse-coding, U-Net regression, diffusion-prior posterior sampling. [SynthSR](https://doi.org/10.1126/sciadv.add3607) is the state-of-the-art unsupervised brain MRI super-resolution / contrast-synthesis tool.

## 3. Steps — generic enhancement pipeline

```text
1. Visualise raw data — never skip this step.
2. Bias-field correction (N4).
3. Denoising (MP-PCA for DWI; NORDIC for fMRI; NLM for structural).
4. Gibbs unringing (DWI / structural with TSE).
5. Motion / distortion correction (modality-specific).
6. Skull strip and intensity normalisation.
7. Automated QC: compute IQMs; flag outliers.
8. Visual QC: human review of flagged subjects.
```

Each step is optional but **always document the chosen pipeline** so downstream analyses are reproducible.

## 4. Per-modality enhancement priorities

| Modality | Top concerns | Tools |
|---|---|---|
| **Structural MRI** | Bias field, motion ringing | N4, NLM, mrdegibbs |
| **DWI** | Thermal noise, Gibbs, motion+eddy, distortion | MP-PCA, mrdegibbs, `eddy`, `topup` |
| **BOLD fMRI** | Thermal noise, motion, distortion, physiological | NORDIC, motion regression, RETROICOR, `topup` |
| **PET** | Partial volume, low counts, noise | PVC, post-recon smoothing, deep-learning denoising |
| **CT** | Beam hardening, metal streaks, photon noise | Iterative recon, MAR, learned denoising |
| **Ultrasound** | Speckle, shadowing | Speckle reduction, compounding |
| **EEG / MEG** | Powerline, eye blinks, muscle, jumps | ICA, ASR, autoreject |

## 5. Automated QC — the safety net

[MRIQC](https://doi.org/10.1371/journal.pone.0184661) computes ~40 image-quality metrics (CNR, SNR, EFC, FBER, GSR, motion summaries) per subject and trains classifiers to predict pass/fail labels. Use thresholds derived from large reference datasets (HCP, ABCD).

For DWI specifically, the [Quad](https://doi.org/10.1016/j.neuroimage.2018.12.011) (Quality Assessment of Diffusion Data) and `eddy_quad` toolboxes produce per-subject motion summaries, outlier maps, and a colour-coded pass/fail.

A reasonable automated-QC policy:

- Compute IQMs for every subject.
- Auto-flag subjects beyond ±2σ from the cohort distribution on key metrics (FD > 0.5 mm, EFC outliers).
- Human-review *all flagged* and a 10% random subset of non-flagged for calibration.
- Document the exclusion criteria *before* looking at the analysis-of-interest.

## 6. Practical example — DWI enhancement chain

```bash
# 1. Denoise with MP-PCA
dwidenoise dwi.nii.gz dwi_dn.nii.gz -noise noise.nii.gz

# 2. Gibbs unringing
mrdegibbs dwi_dn.nii.gz dwi_dn_dg.nii.gz

# 3. Distortion correction (requires reverse-PE acquisition or fmap)
topup --imain=b0_pair.nii.gz --datain=acq.txt --config=b02b0.cnf --out=topup_

# 4. Motion + eddy correction
eddy_cuda10.2 --imain=dwi_dn_dg.nii.gz \
              --mask=brain_mask.nii.gz --acqp=acq.txt --index=index.txt \
              --bvecs=bvecs --bvals=bvals --topup=topup_ \
              --out=dwi_eddy --repol --niter=5

# 5. Bias-field correction on the b=0
N4BiasFieldCorrection -d 3 -i b0.nii.gz -o b0_n4.nii.gz \
    -b [200,3] -c [50x50x50x50,0.0]
```

Pipelines like QSIPrep automate this whole chain with sensible defaults; for custom work you'll reassemble it.

## 7. Practical example — automated cohort QC dashboard

```python
import pandas as pd, glob, json
from pathlib import Path

rows = []
for js in glob.glob("derivatives/mriqc/sub-*/anat/*_T1w.json"):
    iqms = json.load(open(js))
    iqms["subject_id"] = Path(js).parents[1].name
    rows.append(iqms)

df = pd.DataFrame(rows)
# Flag outliers per IQM
for k in ["cnr", "efc", "fber", "snr_total"]:
    z = (df[k] - df[k].median()) / df[k].mad()
    df[f"flag_{k}"] = z.abs() > 3

df["any_flag"] = df.filter(like="flag_").any(axis=1)
print(df["any_flag"].sum(), "subjects flagged")
df.to_parquet("derivatives/qc/group_qc.parquet")
```

Pair the table with a static HTML report (Quarto / Streamlit) and the lab has a self-updating QC dashboard.

## 8. Common pitfalls

- **Over-denoising** — aggressive smoothing eliminates the signal you wanted. Always compare denoised and raw side-by-side.
- **Bias-correction order** — bias correction *before* skull strip can drift extra-cranial intensities; *after* skull strip is more typical. Test both.
- **Excluding subjects after seeing results** — the cardinal QC sin. Pre-register exclusion criteria.
- **Trusting automated QC blindly** — always look at the flagged subjects yourself.
- **Forgetting to record the enhancement chain** — six months later you won't remember whether NORDIC was on for that cohort.

## 9. References

1. **Tustison NJ, Avants BB, Cook PA, et al.** N4ITK: improved N3 bias correction. *IEEE Trans Med Imaging.* 2010;29(6):1310-1320. [doi:10.1109/TMI.2010.2046908](https://doi.org/10.1109/TMI.2010.2046908)
2. **Buades A, Coll B, Morel JM.** A non-local algorithm for image denoising. *CVPR.* 2005. [doi:10.1109/CVPR.2005.38](https://doi.org/10.1109/CVPR.2005.38)
3. **Manjón JV, Coupé P, Martí-Bonmatí L, Collins DL, Robles M.** Adaptive non-local means denoising of MR images with spatially varying noise levels. *J Magn Reson Imaging.* 2010;31(1):192-203. [doi:10.1002/jmri.22003](https://doi.org/10.1002/jmri.22003)
4. **Veraart J, Novikov DS, Christiaens D, et al.** Denoising of diffusion MRI using random matrix theory. *NeuroImage.* 2016;142:394-406. [doi:10.1016/j.neuroimage.2016.08.016](https://doi.org/10.1016/j.neuroimage.2016.08.016) — MP-PCA.
5. **Vizioli L, Moeller S, Dowdle L, et al.** Lowering the thermal noise barrier in functional brain mapping with magnetic resonance imaging. *NeuroImage.* 2021;234:117941. [doi:10.1016/j.neuroimage.2021.117941](https://doi.org/10.1016/j.neuroimage.2021.117941) — NORDIC.
6. **Kellner E, Dhital B, Kiselev VG, Reisert M.** Gibbs-ringing artifact removal based on local subvoxel-shifts. *Magn Reson Med.* 2016;76(5):1574-1581. [doi:10.1002/mrm.26054](https://doi.org/10.1002/mrm.26054)
7. **Andersson JLR, Skare S, Ashburner J.** How to correct susceptibility distortions in spin-echo echo-planar images: application to diffusion tensor imaging. *NeuroImage.* 2003;20(2):870-888. [doi:10.1016/S1053-8119(03)00336-7](https://doi.org/10.1016/S1053-8119(03)00336-7) — `topup` foundation.
8. **Andersson JLR, Sotiropoulos SN.** An integrated approach to correction for off-resonance effects and subject movement in diffusion MR imaging. *NeuroImage.* 2016;125:1063-1078. [doi:10.1016/j.neuroimage.2015.10.019](https://doi.org/10.1016/j.neuroimage.2015.10.019) — FSL `eddy`.
9. **Esteban O, Birman D, Schaer M, et al.** MRIQC: advancing the automatic prediction of image quality in MRI from unseen sites. *PLoS One.* 2017;12(9):e0184661. [doi:10.1371/journal.pone.0184661](https://doi.org/10.1371/journal.pone.0184661)
10. **Iglesias JE, Billot B, Balbastre Y, et al.** SynthSR: a public AI tool to turn heterogeneous clinical brain scans into high-resolution T1-weighted images. *Sci Adv.* 2023;9(5):eadd3607. [doi:10.1126/sciadv.add3607](https://doi.org/10.1126/sciadv.add3607)
11. **Bastiani M, Cottaar M, Fitzgibbon SP, et al.** Automated quality control for within and between studies diffusion MRI data using a non-parametric framework for movement and distortion correction. *NeuroImage.* 2019;184:801-812. [doi:10.1016/j.neuroimage.2018.12.011](https://doi.org/10.1016/j.neuroimage.2018.12.011) — eddy QUAD.
12. **Lehtinen J, Munkberg J, Hasselgren J, et al.** Noise2Noise: learning image restoration without clean data. *ICML.* 2018. [arXiv:1803.04189](https://doi.org/10.48550/arXiv.1803.04189)

## Exercises

1. **MP-PCA threshold.** Explain why a uniform-noise patch SVD's spectrum should match the Marchenko-Pastur distribution. What does deviation indicate?
2. **NORDIC vs NLM.** When would you choose each for fMRI denoising? Name one scan parameter that flips the answer.
3. **Cohort QC outlier policy.** Design an automated outlier-flagging rule combining at least two IQMs; describe a sensitivity analysis to defend the threshold.

??? success "Solutions"
    1. Pure noise eigenvalues follow MP. Signal contributes additional large eigenvalues above the MP edge; keep those, discard the rest.
    2. NORDIC if magnitude+phase data available; NLM for magnitude-only data. Flips when phase reconstruction is unavailable or unstable.
    3. e.g. flag if FD_mean > 0.5 mm AND CNR < 5th percentile; sensitivity = sweep both thresholds, show flagging rate is monotonic and stable around chosen values.

## Where to next

- [Visualization](visualization.md) — turning the cleaned, registered, segmented volumes into figures a human can interpret.
- The [Analysis](../../analysis/index.md) section shows what you do with the enhanced, registered, segmented data.
- The [AI / ML](../../ai/index.md) section covers learned alternatives to several of the steps above.
- The [Data engineering](../../data-engineering/index.md) section shows how to run all of it at cohort scale.
