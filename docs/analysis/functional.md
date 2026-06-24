# Functional connectivity

> Estimating which brain regions co-fluctuate in their BOLD signal — the most common rs-fMRI analysis.

## The standard pipeline

1. **Acquire** resting-state or task BOLD.
2. **Preprocess** with fMRIPrep (motion correction, distortion correction, registration, optional [ICA-AROMA](ica.md#44-ica-aroma-the-motion-cleanup-killer-app)).
3. **Confound regression** — remove motion, physiological noise, and global signal effects.
4. **Parcellate** — extract one timecourse per atlas region.
5. **Compute connectivity** — typically Pearson correlation, partial correlation, or tangent-space embedding.
6. **Threshold or weight** the resulting matrix; analyse.

## Nilearn — the Python workhorse [Abraham et al., 2014](https://doi.org/10.3389/fninf.2014.00014)[^nilearn]

Nilearn (<https://nilearn.github.io>) wraps the preprocessing-to-connectivity pipeline for fMRI in a scikit-learn-style API:

```python
from nilearn.maskers import NiftiLabelsMasker
from nilearn.connectome import ConnectivityMeasure
import nibabel as nib

masker = NiftiLabelsMasker(
    labels_img="Schaefer400.nii.gz",
    standardize=True,
    detrend=True,
    high_pass=0.01,
    low_pass=0.1,
    t_r=2.0,
)
timecourses = masker.fit_transform(
    "sub-001_desc-preproc_bold.nii.gz",
    confounds="sub-001_desc-confounds_timeseries.tsv",
)
conn = ConnectivityMeasure(kind="correlation").fit_transform([timecourses])[0]
```

A 400×400 connectivity matrix in ~30 lines.

## Confound regression — the part most people get wrong

fMRIPrep emits a `*_desc-confounds_timeseries.tsv` with dozens of columns. You don't use all of them. Common reasonable strategies:

| Strategy | Columns |
| --- | --- |
| **6 motion + global signal** | `trans_x..z`, `rot_x..z`, `global_signal` |
| **24 motion** | The 6 motion params, their squares, derivatives, derivatives squared |
| **ACompCor** | Top-5 PCA components from white matter + CSF masks |
| **ICA-AROMA + 24 motion** | Use AROMA-cleaned BOLD plus motion |

Pick one strategy, document it, apply it consistently across your cohort. The reproducibility crisis in resting-state fMRI is partly a "everyone picks a different confound set" crisis.

## Connectivity measures

- **Pearson correlation** — the workhorse. Symmetric, interpretable.
- **Partial correlation** — controls for the rest of the network. Cleaner for graph-theory analyses.
- **Tangent-space embedding** — Nilearn's `kind="tangent"`. Better for ML on cohorts of connectomes (Pearson matrices live on a curved manifold; tangent projections live on a flat one).
- **Mutual information / sparse covariance** — for non-linear or sparse connectivity assumptions.

For most papers, Pearson + Fisher z-transform is fine.

## Group analyses

A common pattern: stack each subject's connectivity matrix into a 3D array `(n_subjects, n_regions, n_regions)`, then:

- **Edge-wise tests** — `n_regions * (n_regions - 1) / 2` mass-univariate tests. Multiple-comparison correction is essential.
- **Network-level summaries** — within-network connectivity, modularity, degree.
- **NBS — Network-Based Statistics** [Zalesky et al., 2010](https://doi.org/10.1016/j.neuroimage.2010.06.041)[^nbs] — clusters of connected significant edges; usually more powerful than edge-wise FDR.

See [Multiple comparisons](multiple-comparisons.md) before believing any p-value.

## Pitfalls

- **Motion is the dominant confound.** A "group difference" between movers and non-movers is what you'll find if you don't censor or regress motion properly.
- **Global signal regression is contentious.** Removes some real signal along with the noise. Document whether you did or didn't.
- **Atlas choice matters.** Schaefer-400 is not equivalent to Power-264 is not equivalent to Yeo-7. Stick with one per study.

## Edge cases — when standard FC pipelines mislead

The pipeline above runs cleanly on most cohorts. The failures below are the ones reviewers and replication attempts find later.

- **GSR over-aggression.** Global signal regression scrubs some shared artifact, but it also mathematically forces the mean correlation across the brain toward zero — inducing apparent anti-correlations between networks that aren't biologically real [Murphy & Fox, 2017](https://doi.org/10.1016/j.neuroimage.2016.11.052)[^gsr]. Pre-register GSR vs no-GSR before you peek at the matrices; report both. Anti-correlations between DMN and task-positive networks should be treated as load-bearing only when they survive *without* GSR.
- **Atlas-based parcellation leakage.** When an atlas is resampled into native or low-resolution functional space, adjacent ROIs end up sharing voxels. Their timecourses are then literally the same signal averaged with different weights, and their FC is artifactually $\rho \to 1$. Always render the resampled atlas labels over the BOLD reference and inspect ROI–ROI mask overlap; drop or merge pairs above ~5% overlap.
- **Low-SNR edge voxels.** Cortical-edge voxels carry partial-volume CSF. They have wild variance, low tSNR, and — if you don't mask them — they can dominate the off-diagonal of a connectivity matrix purely as noise. Apply a tSNR threshold (e.g. tSNR > 50) inside the masker before computing correlations.
- **Motion despite scrubbing.** Censoring high-FD volumes is necessary but not sufficient; residual motion still correlates with FC strength after scrubbing [Power et al., 2014](https://doi.org/10.1016/j.neuroimage.2013.08.048)[^power]. Always report mean framewise displacement per subject and include it as a group-level covariate. If your effect of interest disappears when mean FD enters the model, the effect *was* motion.
- **Pulsatile and respiratory aliasing.** With short TR and multiband, cardiac (~1 Hz) and respiratory (~0.3 Hz) components alias into the 0.01–0.1 Hz band that connectivity lives in. [RetroICOR](https://doi.org/10.1002/1522-2594(200007)44:1%3C162::AID-MRM23%3E3.0.CO;2-E) [Glover et al., 2000](https://doi.org/10.1002/1522-2594(200007)44:1%3C162::AID-MRM23%3E3.0.CO;2-E)[^glover] (with recorded physio traces) or [aCompCor](https://doi.org/10.1016/j.neuroimage.2007.04.042) [Behzadi et al., 2007](https://doi.org/10.1016/j.neuroimage.2007.04.042)[^acompcor] (no physio needed; PCA on WM+CSF masks) reduces but does not eliminate it. If you have physio, use it; if not, log that limitation explicitly.

## References

[^nilearn]: Abraham A, Pedregosa F, Eickenberg M, et al. Machine learning for neuroimaging with scikit-learn. *Front Neuroinform.* 2014;8:14. [doi:10.3389/fninf.2014.00014](https://doi.org/10.3389/fninf.2014.00014)
[^nbs]: Zalesky A, Fornito A, Bullmore ET. Network-based statistic: identifying differences in brain networks. *NeuroImage.* 2010;53(4):1197-1207. [doi:10.1016/j.neuroimage.2010.06.041](https://doi.org/10.1016/j.neuroimage.2010.06.041)
[^gsr]: Murphy K, Fox MD. Towards a consensus regarding global signal regression for resting state functional connectivity MRI. *NeuroImage.* 2017;154:169-173. [doi:10.1016/j.neuroimage.2016.11.052](https://doi.org/10.1016/j.neuroimage.2016.11.052)
[^power]: Power JD, Mitra A, Laumann TO, Snyder AZ, Schlaggar BL, Petersen SE. Methods to detect, characterize, and remove motion artifact in resting state fMRI. *NeuroImage.* 2014;84:320-341. [doi:10.1016/j.neuroimage.2013.08.048](https://doi.org/10.1016/j.neuroimage.2013.08.048)
[^acompcor]: Behzadi Y, Restom K, Liau J, Liu TT. A component based noise correction method (CompCor) for BOLD and perfusion based fMRI. *NeuroImage.* 2007;37(1):90-101. [doi:10.1016/j.neuroimage.2007.04.042](https://doi.org/10.1016/j.neuroimage.2007.04.042)
[^glover]: Glover GH, Li T-Q, Ress D. Image-based method for retrospective correction of physiological motion effects in fMRI: RETROICOR. *Magn Reson Med.* 2000;44(1):162-167. [doi:10.1002/1522-2594(200007)44:1<162::AID-MRM23>3.0.CO;2-E](https://doi.org/10.1002/1522-2594(200007)44:1%3C162::AID-MRM23%3E3.0.CO;2-E)

## Where to next

- [ICA for neuroimaging](ica.md) — the decomposition that powers ICA-AROMA, dual regression, and most of the intrinsic-network literature.
- [Surface-based analysis](surface.md) — when volumetric BOLD averaging blurs across sulci.
