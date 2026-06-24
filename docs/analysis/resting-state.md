# Resting-state connectivity in practice

> The rs-fMRI literature is enormous, the reproducibility is variable, and the choices that matter most are usually made in the first ten minutes of analysis.

This page goes deeper than [Functional connectivity](functional.md): how to choose between seed / ICA / parcellation, when to switch from Pearson to partial correlation, what the dynamic-FC literature actually claims, and the null models you need before publishing graph metrics.

## Three analysis families

| Family | What you get | When it's the right tool |
| --- | --- | --- |
| **Seed-based** | A whole-brain map of correlations with one ROI's timecourse | Targeted hypothesis: "does the amygdala couple to vmPFC differently in patients?" |
| **ICA** | Spatially independent components ≈ canonical networks (DMN, salience, etc.) | Data-driven; finds networks you didn't anatomically specify; [dual regression](ica.md#43-dual-regression) for group stats. The full ICA machinery (MELODIC, AMICA, ICASSO) is in [ica.md](ica.md). |
| **Parcellation-based** | A region × region FC matrix | The default for connectomics, ML on connectomes, graph-theory metrics. |

Most labs do all three; the question determines which one you report first.

## Static FC — measures

### Pearson correlation

Symmetric, scale-invariant, the default. Apply Fisher z-transform before averaging or doing parametric stats:

$$
z = \tfrac{1}{2}\ln\!\left(\frac{1+r}{1-r}\right)
$$

### Partial correlation

The correlation between two regions *after* regressing out every other region. Closer to a "direct" connection; the matrix is the negative-normalised inverse of the covariance matrix. Numerically unstable for $p > n$ (more regions than timepoints) — which is most cohorts.

### Regularised inverse covariance [Smith et al., 2011](https://doi.org/10.1016/j.neuroimage.2010.08.063)[^smith]

Use `sklearn.covariance.GraphicalLassoCV` or `nilearn`'s `ConnectivityMeasure(kind="precision")` with shrinkage. The sparsity prior gives a defensible partial-correlation matrix even when $p > n$.

```python
from nilearn.connectome import ConnectivityMeasure
cm = ConnectivityMeasure(kind="partial correlation", standardize="zscore_sample")
mats = cm.fit_transform(list_of_timecourses_per_subject)
```

## Dynamic FC

Static FC averages over the entire scan; dynamic FC asks whether connectivity *fluctuates* in interpretable ways during a single ~10 minute session.

### Sliding window

Compute FC in 30-60 s windows shifted by ~TR. Cluster the resulting matrices (k-means; the "states" literature). Easy to do, hard to defend:

- Window length must be > 1/lowest-frequency-of-interest; below ~30 s you measure noise.
- Apparent state transitions arise from i.i.d. noise in null simulations [Laumann et al., 2017](https://doi.org/10.1093/cercor/bhw265)[^laumann] — always run a phase-randomised null.

### HMM-based [Vidaurre et al., 2017](https://doi.org/10.1073/pnas.1705120114)[^vidaurre]

Hidden Markov Models on parcellated timeseries identify recurring states with explicit transition probabilities, no window length to tune. The `HMM-MAR` toolbox (MATLAB; Python wrappers exist) is the reference implementation.

### Null models

You cannot interpret a dynamic-FC result without comparing it to a null where the *time-varying* structure is destroyed but the static structure is preserved:

- **Phase randomisation** — randomise Fourier phases per region; preserves spectra and static FC.
- **Autoregressive surrogates** — fit AR(p) per region, simulate, recompute FC.

If your "state dwell times" do not differ from these nulls, you don't have a dynamic-FC effect.

## Graph metrics

Once you have a FC matrix, the graph-theory literature gives you a hundred summary scalars. The ones that survive replication:

| Metric | What it measures | Interpretation pitfall |
| --- | --- | --- |
| **Degree** | Number of edges per node | Depends on threshold; report at multiple densities. |
| **Modularity (Q)** | Strength of community structure | Heuristic optimisation; results vary across runs — use consensus clustering. |
| **Participation coefficient** | How distributed a node's connections are across modules | Only meaningful once modules are stable. |
| **Small-worldness (σ)** | $C/C_{rand}$ vs $L/L_{rand}$ ratio | Almost every brain network is "small-world" — the metric is rarely diagnostic. |
| **Rich-club coefficient** | Hub-to-hub preferential connectivity | Needs density-matched null. |

**Reliability is the elephant.** Test-retest ICC of graph metrics is often < 0.5 [Andellini et al., 2015](https://doi.org/10.1016/j.jneumeth.2015.05.020)[^andellini]; group differences on a single 5-minute scan are not credible. Use ≥ 10 min of data, and report ICC alongside any group statistic.

## Network atlases

| Atlas | Regions | Notes |
| --- | --- | --- |
| **Power 264** | 264 spherical ROIs | Pioneer of FC parcellations; non-contiguous. |
| **Schaefer** | 100-1000 | Multi-resolution; aligned to Yeo networks; the modern default. |
| **Yeo 7 / 17** | 7 or 17 networks | Coarse-grained for high-level reports. |
| **Glasser HCP-MMP1** | 360 surface parcels | Multimodal; surface-only; pairs naturally with HCP pipelines. |
| **AAL / Harvard-Oxford** | 90-110 | Anatomically defined; older; not great for FC. |

Pick one resolution per study. A 100-region matrix and a 1000-region matrix do not give the same answer to "is the DMN hypo-connected" — and reviewers know it.

## Null models for spatial maps

When you correlate a brain map (e.g., a FC summary) with another map (gene expression, cortical thickness), spatial autocorrelation makes naive p-values useless [Burt et al., 2018](https://doi.org/10.1038/s41593-018-0195-0)[^brainsmash].

- **BrainSMASH** — generates spatially autocorrelated surrogate maps that preserve the autocorrelation structure of the original.
- **Spin tests** [Alexander-Bloch et al., 2018](https://doi.org/10.1016/j.neuroimage.2018.05.070)[^spin] — rotate the spherical cortical surface; correlate against the rotated maps.

Both produce a null distribution against which your observed map-map correlation is compared. The "null = scrambled vertices" approach is wrong; do not use it.

## The motion confound

Re-read [QC](qc.md) before this section. The TL;DR for FC:

- **Mean FD correlates with global FC strength.** Patient groups often move more. Without strict matching or motion regression, every group difference is partly motion.
- **Scrubbing** (Power 2012): censor volumes with FD > 0.2-0.5 mm. Apply *before* connectivity computation, not after.
- **Global signal regression (GSR)** removes both noise *and* signal that has a brain-wide spatial pattern. The current consensus is "report both with and without GSR" [Murphy & Fox, 2017](https://doi.org/10.1016/j.neuroimage.2016.11.052)[^gsr]. Pick a side and defend it.

## Sample size

The grim arithmetic: stable individual FC fingerprints need ~30+ min of data per subject [Gordon et al., 2017](https://doi.org/10.1016/j.neuron.2017.07.011)[^gordon]; reliable group-difference effects at typical neuroimaging effect sizes need n > 100 [Marek et al., 2022](https://doi.org/10.1038/s41586-022-04492-9)[^marek]. The 20-subject FC studies in the older literature were almost certainly underpowered.

## Python recipe — seed and atlas-based FC

```python
import numpy as np
from nilearn.maskers import NiftiLabelsMasker, NiftiSpheresMasker
from nilearn.connectome import ConnectivityMeasure
from nilearn.interfaces.fmriprep import load_confounds

bold = "sub-01_task-rest_desc-preproc_bold.nii.gz"
confounds, sample_mask = load_confounds(
    bold, strategy=["motion", "wm_csf", "scrub"],
    motion="basic", wm_csf="basic", scrub=0, fd_threshold=0.5,
)

# ---- atlas-based: Schaefer-400 x Yeo-17 ----
atlas_masker = NiftiLabelsMasker(
    labels_img="Schaefer2018_400Parcels_17Networks_FSLMNI152_2mm.nii.gz",
    standardize="zscore_sample", detrend=True,
    high_pass=0.008, low_pass=0.09, t_r=2.0,
)
tc = atlas_masker.fit_transform(bold, confounds=confounds, sample_mask=sample_mask)
fc = ConnectivityMeasure(kind="correlation").fit_transform([tc])[0]
fc_z = np.arctanh(np.clip(fc - np.eye(fc.shape[0]), -0.999, 0.999))

# ---- seed-based: PCC (-7, -55, 25) ----
seed_masker = NiftiSpheresMasker([(-7, -55, 25)], radius=6,
                                 standardize="zscore_sample",
                                 detrend=True, high_pass=0.008,
                                 low_pass=0.09, t_r=2.0)
seed_tc = seed_masker.fit_transform(bold, confounds=confounds,
                                    sample_mask=sample_mask)

# correlate seed against every Schaefer region
seed_fc = np.corrcoef(seed_tc.squeeze(), tc.T)[0, 1:]
```

That's a 400×400 matrix plus a seed map in ~30 lines. Save `fc_z` per subject; stack across the cohort; you're ready for [Group-level statistics](group-stats.md) and [Multiple comparisons](multiple-comparisons.md).

## Common pitfalls

- **Reporting only positive correlations.** Anti-correlations may be real or may be a GSR artefact — disclose your processing.
- **Comparing across atlases.** Schaefer-400 and Power-264 differ in granularity; "DMN connectivity" computed on each is a different quantity.
- **Edge-thresholding before group stats.** Equivalent to picking edges based on the data; biases the group test. Use NBS or edge-wise FDR instead.
- **Ignoring within-network vs between-network distinction.** Often the more interpretable contrast than node-level metrics.
- **Treating dynamic-FC states as ground truth.** Always run a static + phase-randomised null.

!!! tip "Beginner takeaway"
    A defensible rs-fMRI analysis in five steps:

    1. ≥ 10 minutes of data per subject; scrub at FD > 0.5 mm.
    2. One atlas (Schaefer-400 or HCP-MMP1); report both with and without GSR.
    3. Pearson for matrices; partial correlation only with shrinkage.
    4. NBS for edge-wise group stats; spin / BrainSMASH for map-map.
    5. Skip dynamic-FC unless you have > 30 min of data and a null model.

## References

[^smith]: Smith SM, Miller KL, Salimi-Khorshidi G, et al. Network modelling methods for FMRI. *NeuroImage.* 2011;54(2):875-891. [doi:10.1016/j.neuroimage.2010.08.063](https://doi.org/10.1016/j.neuroimage.2010.08.063)
[^laumann]: Laumann TO, Snyder AZ, Mitra A, et al. On the stability of BOLD fMRI correlations. *Cereb Cortex.* 2017;27(10):4719-4732. [doi:10.1093/cercor/bhw265](https://doi.org/10.1093/cercor/bhw265)
[^vidaurre]: Vidaurre D, Smith SM, Woolrich MW. Brain network dynamics are hierarchically organized in time. *PNAS.* 2017;114(48):12827-12832. [doi:10.1073/pnas.1705120114](https://doi.org/10.1073/pnas.1705120114)
[^andellini]: Andellini M, Cannatà V, Gazzellini S, Bernardi B, Napolitano A. Test-retest reliability of graph metrics of resting state MRI functional brain networks. *J Neurosci Methods.* 2015;253:183-192. [doi:10.1016/j.jneumeth.2015.05.020](https://doi.org/10.1016/j.jneumeth.2015.05.020)
[^brainsmash]: Burt JB, Helmer M, Shinn M, Anticevic A, Murray JD. Generative modeling of brain maps with spatial autocorrelation. *NeuroImage.* 2020;220:117038. [doi:10.1016/j.neuroimage.2020.117038](https://doi.org/10.1016/j.neuroimage.2020.117038)
[^spin]: Alexander-Bloch AF, Shou H, Liu S, et al. On testing for spatial correspondence between maps of human brain structure and function. *NeuroImage.* 2018;178:540-551. [doi:10.1016/j.neuroimage.2018.05.070](https://doi.org/10.1016/j.neuroimage.2018.05.070)
[^gsr]: Murphy K, Fox MD. Towards a consensus regarding global signal regression for resting state functional MRI. *NeuroImage.* 2017;154:169-173. [doi:10.1016/j.neuroimage.2016.11.052](https://doi.org/10.1016/j.neuroimage.2016.11.052)
[^gordon]: Gordon EM, Laumann TO, Gilmore AW, et al. Precision functional mapping of individual human brains. *Neuron.* 2017;95(4):791-807. [doi:10.1016/j.neuron.2017.07.011](https://doi.org/10.1016/j.neuron.2017.07.011)
[^marek]: Marek S, Tervo-Clemmens B, Calabro FJ, et al. Reproducible brain-wide association studies require thousands of individuals. *Nature.* 2022;603(7902):654-660. [doi:10.1038/s41586-022-04492-9](https://doi.org/10.1038/s41586-022-04492-9)

1. **Schaefer A, Kong R, Gordon EM, et al.** Local-global parcellation of the human cerebral cortex. *Cereb Cortex.* 2018;28(9):3095-3114. [doi:10.1093/cercor/bhx179](https://doi.org/10.1093/cercor/bhx179)
2. **Glasser MF, Coalson TS, Robinson EC, et al.** A multi-modal parcellation of human cerebral cortex. *Nature.* 2016;536(7615):171-178. [doi:10.1038/nature18933](https://doi.org/10.1038/nature18933)
3. **Yeo BTT, Krienen FM, Sepulcre J, et al.** The organization of the human cerebral cortex estimated by intrinsic functional connectivity. *J Neurophysiol.* 2011;106(3):1125-1165. [doi:10.1152/jn.00338.2011](https://doi.org/10.1152/jn.00338.2011)

## Where to next

- [ICA for neuroimaging](ica.md) — the decomposition behind MELODIC, dual regression, ICA-AROMA, and the intrinsic-network parcellations.
- [Longitudinal and mixed-effects models](longitudinal.md) — when the same subjects come back for follow-up scans.
