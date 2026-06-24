# Group-level statistics

> Going from per-subject maps to "is this effect real across the cohort?"

## The general linear model

Almost everything is a GLM:

```text
y = X β + ε
```

- `y` — a per-subject value at each voxel / vertex / edge.
- `X` — the design matrix: one column per regressor (group label, age, sex, motion, etc.).
- `β` — the regression weights (what you want to estimate).
- `ε` — noise, assumed iid Gaussian.

Run the GLM at each voxel; produce a statistical map; correct for multiple comparisons.

The GLM as used in fMRI was formalised in [Friston et al., 1995](https://doi.org/10.1002/hbm.460020402)[^friston-glm], which extended Worsley's earlier random-field results ([Worsley et al., 1992](https://doi.org/10.1038/jcbfm.1992.127)[^worsley1992]) into the framework SPM, FSL, and AFNI still use today.

## Two analysis levels

- **First-level** — within a single subject. For fMRI, this is the BOLD timeseries regressed against the task design matrix; the output per voxel is one β per condition.
- **Group-level (second-level)** — across subjects. The βs from first level become the `y` of the group GLM.

This is the "summary-statistics approach" — FSL's FEAT and SPM's basic pipeline both implement it. It's an approximation (it ignores within-subject variance heterogeneity) but it works well in practice.

## Mixed models when subjects vary

When subjects contribute different numbers of timepoints (longitudinal data), or first-level variance differs dramatically (different number of trials, dropouts), the summary-statistics approximation breaks. Switch to a proper mixed model:

- **`nilearn.glm.second_level`** — handles weighted least squares with per-subject variance.
- **FSL FLAME / FLAME1** ([Beckmann et al., 2003](https://doi.org/10.1016/S1053-8119(03)00435-X)[^flame]) — Bayesian mixed-effects with full uncertainty propagation; the standard for FSL-based group analyses.
- **`afex` / `lme4`** in R — when you want full mixed-model flexibility.

## Designs you'll meet

- **Two-sample t-test** — group A vs group B.
- **Paired t-test** — same subjects, two conditions / timepoints.
- **One-way ANOVA** — three or more groups.
- **Regression on a covariate** — e.g., effect of age on cortical thickness.
- **Interaction** — group × covariate, group × condition.

Always sketch the design matrix on paper before you trust the output of any tool.

## Permutation testing — the safe default [Winkler et al., 2014](https://doi.org/10.1016/j.neuroimage.2014.01.060)[^palm]

Parametric GLM p-values assume normality, independence, and the right model. For neuroimaging — small samples, heavy-tailed errors, spatial correlation — permutation tests are usually more honest. The canonical neuroimaging permutation-testing reference is [Nichols & Holmes, 2002](https://doi.org/10.1002/hbm.1058)[^nichols-holmes], which formalised single-step max-T and TFCE-style maxima distributions for spatial statistical maps:

- **PALM** (FSL) — voxel-wise or vertex-wise, supports arbitrary designs, including freedman-lane for confound regression. See the [PALM repo](https://github.com/andersonwinkler/PALM).
- **[FSL `randomise`](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/Randomise)** — the canonical permutation engine; PALM is its more flexible successor.
- **`nilearn.mass_univariate.permuted_ols`** — simpler, Python-native.

The cost is compute (~1000× a single GLM); the benefit is p-values that survive review.

### Why permutation over parametric — and when each wins

The parametric GLM assumes residuals are i.i.d. Gaussian. With typical neuroimaging $N$ (20–100 per group) and structured residuals — spatial autocorrelation, site effects, heteroscedastic motion — that assumption is routinely violated. Inference then leans on a $t$- or $F$-distribution that the data don't actually live on.

Permutation drops the Gaussianity assumption entirely. It builds the null distribution by *shuffling labels* (group, condition, sign) under an exchangeability assumption, recomputing the test statistic, and comparing the observed value to that empirical null. Whatever distribution the noise actually has, the null inherits it.

| Situation | Prefer |
| --- | --- |
| $N>1000$, simple between-subject design (e.g. UK Biobank) | **Parametric** — analytic tails are accurate, permutation is wasted compute |
| Smooth Gaussian fields with strong theory (Worsley RFT) | **Parametric (RFT)** |
| Small samples, non-Gaussian residuals | **Permutation** |
| Mixed-effects with custom contrasts or rank-based statistics | **Permutation** |
| TFCE on voxel/vertex maps | **Permutation** (TFCE has no parametric null) |
| Complex within-subject correlation, multi-level designs | **Permutation** with carefully chosen exchangeability blocks |

The cost is twofold. Compute: 5000 permutations × your full second-level pipeline. And exchangeability: you have to *think* about what's swappable and what must be held fixed — Winkler 2014[^palm] lays out the block structure for paired, repeated-measures, and multi-site designs. A naive `np.random.permutation` on a paired design gives you a confidently wrong p-value.

## Effect sizes — report them

A `p < 0.05` map says where the effect is unlikely-to-be-noise; it does not say where the effect is *large*. Always report:

- **Cohen's d** (for group differences).
- **R²** (for regressions).
- **Confidence intervals** on the effect, not just on the test statistic.

A reviewer can't tell a Cohen's d = 0.05 result from a d = 1.5 result from a thresholded map alone. Show both.

## References

[^palm]: Winkler AM, Ridgway GR, Webster MA, Smith SM, Nichols TE. Permutation inference for the general linear model. *NeuroImage.* 2014;92:381-397. [doi:10.1016/j.neuroimage.2014.01.060](https://doi.org/10.1016/j.neuroimage.2014.01.060)
[^friston-glm]: Friston KJ, Holmes AP, Worsley KJ, Poline JB, Frith CD, Frackowiak RSJ. Statistical parametric maps in functional imaging: a general linear framework. *Hum Brain Mapp.* 1995;2(4):189-210. [doi:10.1002/hbm.460020402](https://doi.org/10.1002/hbm.460020402)
[^worsley1992]: Worsley KJ, Evans AC, Marrett S, Neelin P. A three-dimensional statistical analysis for CBF activation studies in human brain. *J Cereb Blood Flow Metab.* 1992;12(6):900-918. [doi:10.1038/jcbfm.1992.127](https://doi.org/10.1038/jcbfm.1992.127)
[^nichols-holmes]: Nichols TE, Holmes AP. Nonparametric permutation tests for functional neuroimaging: a primer with examples. *Hum Brain Mapp.* 2002;15(1):1-25. [doi:10.1002/hbm.1058](https://doi.org/10.1002/hbm.1058)
[^flame]: Beckmann CF, Jenkinson M, Smith SM. General multilevel linear modeling for group analysis in FMRI. *NeuroImage.* 2003;20(2):1052-1063. [doi:10.1016/S1053-8119(03)00435-X](https://doi.org/10.1016/S1053-8119(03)00435-X)

## Where to next

[Multiple comparisons](multiple-comparisons.md) — what to do about the 100 000 tests you just ran.
