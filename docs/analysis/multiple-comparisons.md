# Multiple comparisons

> Choosing between FDR, FWE, TFCE, and cluster correction — without lying to yourself or your reviewers.

## The problem

A typical voxel-wise GLM is ≈ 100 000 tests. At α = 0.05, you expect ≈ 5 000 false positives by chance. Without correction, every "result" is mostly noise.

## The toolbox

### Bonferroni — almost never the answer

Divide α by the number of tests. Correct, ultra-conservative, throws away every distributed effect. Useful as a sanity check, almost never as a primary correction.

### FDR (False Discovery Rate)

Control the *expected proportion of false positives among rejected nulls*. Less conservative than Bonferroni; widely accepted. [Genovese et al., 2002](https://doi.org/10.1006/nimg.2001.1037)[^genovese] introduced FDR control to fMRI thresholding, extending [Benjamini & Hochberg, 1995](https://doi.org/10.1111/j.2517-6161.1995.tb02031.x) to spatial statistical maps. Two flavours:

- **Benjamini-Hochberg** — independence or positive dependence.
- **Benjamini-Yekutieli** — arbitrary dependence; more conservative.

`statsmodels.stats.multitest.multipletests(p, method="fdr_bh")` is the Python entry point.

### FWE (Family-Wise Error)

Control the *probability of one or more false positives anywhere in the map*. Stricter than FDR. Two ways to compute it:

- **Random Field Theory (RFT)** — analytical, assumes smoothness; SPM and old FSL. The neuroimaging-RFT framework was introduced by [Worsley et al., 1992](https://doi.org/10.1038/jcbfm.1992.127)[^worsley1992-mc] and extended in [Worsley et al., 1996](https://doi.org/10.1002/(SICI)1097-0193(1996)4:1%3C58::AID-HBM4%3E3.0.CO;2-O)[^worsley1996].
- **Permutation** — empirical, robust to smoothness assumptions; PALM, FSL `randomise`, `nilearn`. The canonical neuroimaging permutation reference is [Nichols & Holmes, 2002](https://doi.org/10.1002/hbm.1058)[^nichols-holmes-mc], which formalised single-step max-T and TFCE-style maxima distributions for spatial statistical maps.

For modern neuroimaging, prefer permutation FWE over RFT FWE.

### Cluster correction

Threshold the statistical map at a lenient voxel-wise threshold (e.g., p < 0.001), then keep only spatially contiguous clusters larger than a critical size. The cluster size threshold is calibrated to control FWE.

- Very high sensitivity for spatially extended effects.
- Notoriously sensitive to the cluster-forming threshold. **The Eklund 2016 wake-up call** [Eklund et al., 2016](https://doi.org/10.1073/pnas.1602413113)[^eklund] traced back to cluster correction with p = 0.01 thresholds inflating FWE to > 70%. Use p ≤ 0.001 cluster-forming.

### TFCE (Threshold-Free Cluster Enhancement) [Smith & Nichols, 2009](https://doi.org/10.1016/j.neuroimage.2008.03.061)[^tfce]

Combines cluster extent and peak intensity into a single statistic that doesn't require a cluster-forming threshold. Then a permutation distribution gives FWE-corrected p-values. **The current default for voxel-wise neuroimaging.**

FSL `randomise -T` and PALM [Winkler et al., 2014](https://doi.org/10.1016/j.neuroimage.2014.01.060)[^palm] `-T` both implement it.

## Picking one

| Situation | Choice |
| --- | --- |
| Voxel-wise (mass-univariate) | **TFCE + permutation** |
| ROI / atlas-level | **FDR** |
| Network-level (NBS) | **NBS** with permutation |
| Vertex-wise on the surface | **TFCE + permutation** (or FreeSurfer cluster-correction with strict threshold) |
| A few pre-registered tests | **Bonferroni** |

## The honest disclosure section

Whatever you pick, **report it explicitly**:

- The threshold (e.g., "TFCE-corrected p < 0.05 with 10 000 permutations").
- The cluster-forming threshold if you used voxel-wise cluster correction.
- The smoothing kernel — corrections that assume smoothness depend on it.

If your figures show uncorrected maps with a label like "p < 0.001 uncorrected", say so loudly in the legend. There's nothing wrong with showing exploratory maps; there's something wrong with hiding that they're exploratory.

## References

[^eklund]: Eklund A, Nichols TE, Knutsson H. Cluster failure: why fMRI inferences for spatial extent have inflated false-positive rates. *PNAS.* 2016;113(28):7900-7905. [doi:10.1073/pnas.1602413113](https://doi.org/10.1073/pnas.1602413113)
[^tfce]: Smith SM, Nichols TE. Threshold-free cluster enhancement. *NeuroImage.* 2009;44(1):83-98. [doi:10.1016/j.neuroimage.2008.03.061](https://doi.org/10.1016/j.neuroimage.2008.03.061)
[^palm]: Winkler AM, Ridgway GR, Webster MA, Smith SM, Nichols TE. Permutation inference for the general linear model. *NeuroImage.* 2014;92:381-397. [doi:10.1016/j.neuroimage.2014.01.060](https://doi.org/10.1016/j.neuroimage.2014.01.060)
[^genovese]: Genovese CR, Lazar NA, Nichols T. Thresholding of statistical maps in functional neuroimaging using the false discovery rate. *NeuroImage.* 2002;15(4):870-878. [doi:10.1006/nimg.2001.1037](https://doi.org/10.1006/nimg.2001.1037)
[^worsley1992-mc]: Worsley KJ, Evans AC, Marrett S, Neelin P. A three-dimensional statistical analysis for CBF activation studies in human brain. *J Cereb Blood Flow Metab.* 1992;12(6):900-918. [doi:10.1038/jcbfm.1992.127](https://doi.org/10.1038/jcbfm.1992.127)
[^worsley1996]: Worsley KJ, Marrett S, Neelin P, Vandal AC, Friston KJ, Evans AC. A unified statistical approach for determining significant signals in images of cerebral activation. *Hum Brain Mapp.* 1996;4(1):58-73. [doi:10.1002/(SICI)1097-0193(1996)4:1<58::AID-HBM4>3.0.CO;2-O](https://doi.org/10.1002/(SICI)1097-0193(1996)4:1%3C58::AID-HBM4%3E3.0.CO;2-O)
[^nichols-holmes-mc]: Nichols TE, Holmes AP. Nonparametric permutation tests for functional neuroimaging: a primer with examples. *Hum Brain Mapp.* 2002;15(1):1-25. [doi:10.1002/hbm.1058](https://doi.org/10.1002/hbm.1058)

## Where to next

That closes the Analysis section. From here, [Data engineering](../data-engineering/index.md) tells you how to make pipelines that produce these statistics reliably on hundreds of subjects.
