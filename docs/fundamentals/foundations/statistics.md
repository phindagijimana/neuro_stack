# Statistics

> The inferential machinery every neuroimaging analysis sits on. Get this layer right and the rest is technical work; get it wrong and your conclusions are decoration.

## Probability — the layer underneath

Probability quantifies uncertainty. Three concepts to keep clear:

- **Random variable** — a measurable function from outcomes to numbers (the BOLD value at voxel $v$ at time $t$).
- **Probability density / mass function** — describes how likely each value is.
- **Expectation, variance, covariance** — moments that summarise distributions:

$$
\mathbb{E}[X] = \int x \, p(x) \, dx, \quad
\mathrm{Var}(X) = \mathbb{E}\!\left[(X - \mathbb{E}[X])^2\right]
$$

The Gaussian (normal) distribution dominates neuroimaging modelling because of the **Central Limit Theorem** — the sum of many independent contributions tends Gaussian. Tests like the t-test rest on that assumption; check it.

## Descriptive statistics

Always report, per variable:

- **Centre** — mean or median.
- **Spread** — standard deviation or IQR.
- **Shape** — skewness, kurtosis, or just a histogram.
- **Sample size** — and the missing-data rate.

Effect sizes (next section) often matter more than significance.

## Hypothesis testing — the GLM is most of what you need

The **general linear model** subsumes the t-test, ANOVA, regression, and most fMRI / morphometry tests:

$$
y = X\beta + \varepsilon, \qquad \varepsilon \sim \mathcal{N}(0, \sigma^2 I)
$$

- $y$ — observed values (per subject or per voxel).
- $X$ — design matrix (regressors).
- $\beta$ — unknown coefficients to estimate.
- $\varepsilon$ — Gaussian noise.

The OLS estimator $\hat\beta = (X^TX)^{-1}X^Ty$ is the best linear unbiased estimator under standard assumptions (Gauss-Markov theorem). t- and F-statistics from this fit are the workhorses of mass-univariate neuroimaging.

### A one-line worked example (per-voxel age effect on thickness)

$$
\text{thickness}_{i} = \beta_0 + \beta_1\,\text{age}_i + \beta_2\,\text{sex}_i + \beta_3\,\text{site}_i + \varepsilon_i
$$

$\beta_1$ is the per-voxel effect of age controlling for sex and site. Repeat at every voxel/vertex; correct for multiple comparisons (next section).

## Mixed models — when measurements are not independent

Longitudinal scans of the same subject share subject-level variance; multi-site cohorts share site-level variance. **Linear mixed-effects models** explicitly model these:

$$
y_{ij} = X_{ij}\beta + Z_{ij}b_i + \varepsilon_{ij}, \quad b_i \sim \mathcal{N}(0, \Sigma)
$$

- $b_i$ — random effects per cluster (subject, site).
- Fitted with REML.

In R: [`lme4::lmer(y ~ age + (1 | subject))`](https://cran.r-project.org/package=lme4). In Python: [`statsmodels.formula.api.mixedlm`](https://www.statsmodels.org/stable/mixed_linear.html) or [`pymer4`](https://eshinjolly.com/pymer4/) (a thin wrapper around `lme4` callable from Python). In MATLAB: `fitlme`. Always.

## Random-effects structure choices — multi-site and longitudinal designs

The hard part of a mixed model is rarely the fixed effects; it is deciding *which* random effects to include. The choices, in increasing complexity:

| Structure | R formula | When |
|---|---|---|
| **Random intercept only** | `y ~ x + (1 \| id)` | Each cluster has its own baseline; the slope of `x` is shared. |
| **Random intercept + uncorrelated slope** | `y ~ x + (1 \| id) + (0 + x \| id)` | Each cluster has its own slope; the intercept-slope correlation is fixed to zero. |
| **Random intercept + correlated slope** | `y ~ x + (1 + x \| id)` | The "full" model: each cluster has its own baseline *and* slope, and they may covary. |
| **Crossed random effects** | `y ~ x + (1 \| subject) + (1 \| site)` | Subjects nested in (or crossed with) sites — classic multi-site neuroimaging. |

[Barr et al., 2013](https://doi.org/10.1016/j.jml.2012.11.001) argued for the **maximal random-effects structure justified by the design** — include random slopes for every within-cluster fixed effect, otherwise Type I error inflates. [Bates et al., 2015](https://arxiv.org/abs/1506.04967) pushed back: maximal models often fail to converge or are over-parameterised; prefer the most complex model that the data can identify (via `rePCA` or singular-value checks).

Convergence failures are the day-to-day pain. The standard triage:

- Centre and scale continuous predictors (`age_c = age - 50`); this alone fixes a surprising fraction of failures.
- Try a different optimiser (`lmerControl(optimizer = "bobyqa")` in [`lme4`](https://cran.r-project.org/package=lme4), or `method="lbfgs"` in [`statsmodels`](https://www.statsmodels.org/)).
- Drop the correlation term (`(1 | id) + (0 + x | id)` instead of `(1 + x | id)`).
- If still degenerate, the data genuinely cannot estimate that slope variance — simplify, and report it.

```python
# pymer4 — fit the maximal model and inspect random-effect variance
from pymer4.models import Lmer
m = Lmer("thickness ~ age_c * group + sex + (1 + age_c | subject) + (1 | site)", data=df)
m.fit(REML=True)
print(m.ranef_var)   # variance components per random effect
```

For repeated-measures designs in particular, see [Analysis → Longitudinal](../../analysis/longitudinal.md).

## Multiple comparisons — the wake-up call

A typical voxel-wise GLM is ≈ 10⁵ tests. At $\alpha = 0.05$, **5 000 false positives** by chance. Without correction, every "result" is mostly noise.

| Method | Controls | When to use |
|---|---|---|
| **Bonferroni** | FWER | Tiny number of tests |
| **FDR (BH / BY)** | False Discovery Rate | Most cases; less conservative than FWE |
| **FWE permutation** | FWER, empirically | Strong, distribution-free |
| **Cluster-extent** | FWER on cluster size | Spatial effects; threshold p ≤ 0.001 |
| **TFCE** | FWER on weighted clusters | The modern default for voxel-wise neuroimaging |

See [Analysis → Multiple comparisons](../../analysis/multiple-comparisons.md) for the depth on each.

## Permutation testing — the safe default

Parametric p-values assume normality, independence, and the right model. Permutation tests assume only that, under the null, labels are exchangeable.

The recipe:

1. Compute the observed test statistic.
2. Randomly permute group labels; recompute the statistic. Repeat 10 000 times.
3. The p-value is the fraction of permuted statistics ≥ the observed.

For neuroimaging GLMs, [PALM](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/PALM) (Winkler et al., 2014) is the canonical tool.

## Effect-size reporting and clinical significance

A "significant" p-value with a tiny effect is rarely clinically meaningful. Always report a standardised effect size *with* a confidence interval; the p-value alone is the weakest of the three numbers.

| Measure | Formula | Used for |
|---|---|---|
| **Cohen's d** | $d = (\bar x_1 - \bar x_2) / s_p$ | Two-group mean difference, pooled SD. |
| **Hedges' g** | $g = d \cdot J(n)$ with small-sample correction $J$ | Same as $d$ but bias-corrected for small $n$ — preferred at $n < 50$. |
| **Standardised mean difference (SMD)** | Family including $d$, $g$, Glass's $\Delta$ | Meta-analysis across heterogeneous studies. |
| **Partial $\eta^2$** | $\eta_p^2 = \mathrm{SS}_\text{effect} / (\mathrm{SS}_\text{effect} + \mathrm{SS}_\text{error})$ | ANOVA / GLM factor-level variance explained. |
| **Odds / risk ratio** | $\mathrm{OR} = \frac{p_1/(1-p_1)}{p_2/(1-p_2)}$ | Binary outcomes (case-control, classifier-derived labels). |

Cohen's rough conventions ($d \approx 0.2$ small, $0.5$ medium, $0.8$ large) are field-agnostic and should not substitute for context. In brain-wide association studies most reproducible effects sit at $d \lesssim 0.1$ ([Marek et al., 2022](https://doi.org/10.1038/s41586-022-04492-9)) — small by Cohen's scale, real by neuroscience standards.

Statistical significance is not clinical significance. The **minimum important difference (MID)** is the smallest change a patient or clinician would consider meaningful — e.g. a 3-point MoCA change, a 0.5-SD cortical-thickness change associated with measurable cognitive decline. Define the MID *before* analysis and report effect sizes relative to it. A $p < 0.001$ effect that is one-tenth of the MID is a paper, not a treatment decision.

For predictive-model effect sizes (calibration, NRI, decision-curve analysis), cross-link to [AI → Evaluation](../../ai/evaluation.md).

## Power analysis

**Statistical power** = $1 - \beta$ = probability of detecting an effect of a given size with a given sample.

Given a target power (typically 0.8) and effect size, you can solve for the required $n$:

```python
from statsmodels.stats.power import TTestIndPower
analysis = TTestIndPower()
n = analysis.solve_power(effect_size=0.5, alpha=0.05, power=0.8)
print(n)   # ~64 per group
```

Marek et al., 2022 ([doi:10.1038/s41586-022-04492-9](https://doi.org/10.1038/s41586-022-04492-9)) demonstrated that brain-wide-association studies need **thousands** of subjects for reproducible effects. Plan accordingly. For voxel- and cluster-level power calculations specifically, [`neuropower`](https://neuropowertools.org/) (Durnez et al.) estimates the sample size required for a target peak/cluster detection rate from a pilot statistic map.

## Bayesian thinking — when priors matter

Bayes's theorem:

$$
p(\theta \mid y) = \frac{p(y \mid \theta)\,p(\theta)}{p(y)}
$$

You update a prior belief about $\theta$ using the likelihood of observed data. In neuroimaging this shows up as:

- **Bayesian model averaging** — averaging over candidate models weighted by evidence.
- **Bayesian fMRI GLM** — SPM's default since ~2005.
- **PyMC / Stan** — general-purpose probabilistic programming.

Bayesian credibility intervals are intuitive (95% credibility = "I believe 95% probability that the true value lies here"); frequentist confidence intervals are *not* the same thing.

## Bayesian hierarchical models for multi-site / heterogeneous data

The frequentist GLM and its mixed-model extension cover most analyses; a fully Bayesian hierarchical formulation earns its complexity only in specific regimes.

### When the frequentist GLM stops being enough

- **Multi-site studies where between-site variance is structured** rather than nuisance. If you actually care about which sites differ, by how much, and with what uncertainty, point estimates and a single REML variance component are not the right summary.
- **Small per-site samples with reasonable prior knowledge.** When some sites contribute only a handful of subjects, frequentist random effects can collapse to zero variance or fail to converge; weakly informative priors keep the model well-posed.
- **Hierarchical effects that interact with the question of interest** — e.g. an age-by-site slope that you want to interrogate per site rather than marginalise over.

### The hierarchical generative model

Write the per-site mean as drawn from a higher-level distribution:

$$
y_{ij} \sim \mathcal{N}(\mu_j, \sigma^2), \qquad \mu_j \sim \mathcal{N}(\mu_0, \tau^2)
$$

with hyperparameters $\mu_0$ (grand mean) and $\tau$ (between-site SD). The posterior on each $\mu_j$ is a **partial-pooling** estimator that lives between two limiting cases:

- **Full pooling** ($\tau \to 0$): all sites share one mean — ignores site heterogeneity.
- **No pooling** ($\tau \to \infty$): each site is fit independently — over-fits small sites.

For finite $\tau$, small-site estimates are shrunk toward $\mu_0$ in proportion to their noise; large sites are barely moved. In multi-site neuroimaging this is exactly what you want: a 12-subject site does not get to define its own group mean, and a 400-subject site does not get diluted by 12-subject neighbours. This is precisely the structure that lets [ENIGMA](https://enigma.ini.usc.edu/)-style consortia and the [Marek et al., 2022 BWAS analysis](https://doi.org/10.1038/s41586-022-04492-9) combine hundreds of small cohorts without over-weighting the noisiest sites.

### Prior specification basics

[Gelman 2006](https://doi.org/10.1214/06-BA117A) is the standard reference for priors in hierarchical models. The defaults that will not embarrass you:

- **Weakly informative priors** on standardised coefficients: $\beta \sim \mathcal{N}(0, 2.5^2)$.
- **Half-Normal or half-Student-t** on standard deviations: $\tau \sim \mathrm{Half}\mathcal{N}(0, 1)$.
- **Avoid flat priors** on $\tau$ in low-$J$ hierarchies — they pathologically inflate the between-site variance and dominate the posterior.

### Random-effects structure choices

The hierarchical structure is a modelling decision, not a default:

- **Random intercepts only** — captures site-level mean shifts. This is the Bayesian analogue of ComBat's additive term for the mean.
- **Random slopes** — captures site-by-effect interactions (e.g. the age slope on cortical thickness differs by scanner vendor).
- **Crossed random effects** — multiple non-nested grouping factors (`(1 | site) + (1 | scanner) + (1 | cohort)`) when the same scanner appears across sites or vice versa.
- **Maximal random structure** (Barr et al., 2013) — include random slopes for every fixed effect that varies within a cluster; back off only when the sampler fails to converge or $\tau$ posteriors pile up at zero.

### Tools

- [**`brms`**](https://paul-buerkner.github.io/brms/) (R) — formula syntax on top of Stan; the most ergonomic option for `lme4`-style users.
- [**`bambi`**](https://bambinos.github.io/bambi/) (Python) — `brms`-style formula interface compiled to PyMC; the right starting point for Python users.
- [**`PyMC`**](https://www.pymc.io/) — Python-native; explicit model code, NUTS sampler.
- [**`NumPyro`**](https://num.pyro.ai/) — JAX-backed, fast on GPU for larger hierarchies.
- [**`Stan`**](https://mc-stan.org/) — the reference implementation; called from R/Python/Julia.
- [**`pymer4`**](https://eshinjolly.com/pymer4/) — a frequentist bridge that exposes `lme4` from Python when you want fast mixed models without going Bayesian.

### Worked Python snippet

Bare `PyMC`, when you want explicit control of the generative model:

```python
import pymc as pm
import numpy as np

with pm.Model() as m:
    mu0   = pm.Normal("mu0", 0, 5)
    tau   = pm.HalfNormal("tau", 2)
    site  = pm.Normal("site_effect", mu0, tau, shape=n_sites)
    sigma = pm.HalfNormal("sigma", 1)
    y_obs = pm.Normal("y", site[site_idx], sigma, observed=y)
    idata = pm.sample(2000, tune=2000, target_accept=0.95)
```

The same model in `bambi`, when you want the `lme4`/`brms` formula ergonomics:

```python
import bambi as bmb
model = bmb.Model("thickness ~ age + sex + (1 | site)", data=cohort, family="gaussian")
fit = model.fit(draws=2000, tune=1000, chains=4, target_accept=0.95)
```

### Diagnostics and posterior summaries

Report, per parameter of interest:

- **94% highest-density interval (HDI)** — the narrowest interval containing 94% of posterior mass.
- **$\hat R$ < 1.01** — between-chain agreement; values above 1.01 indicate the sampler has not converged.
- **Effective sample size (ESS) > 1000** — for both bulk and tail; below this, posterior quantiles are noisy.

Model comparison uses **PSIS-LOO** (Vehtari et al., 2017) rather than raw deviance: `az.compare({"m1": idata1, "m2": idata2})` returns LOO scores and standard errors.

### When NOT to go Bayesian

If you can satisfy frequentist mixed-model assumptions, have enough sites for the variance components to be identifiable, and don't need per-site posteriors, `lme4::lmer` / `statsmodels.mixedlm` is faster to fit, easier to publish, and easier for reviewers to interpret. The Bayesian formulation buys you principled small-sample inference and explicit uncertainty on hierarchical parameters; pay that cost only when you need them.

See [Analysis → Longitudinal modelling](../../analysis/longitudinal.md) for the repeated-measures structure that often layers on top, and [Analysis → Group statistics](../../analysis/group-stats.md) for the frequentist mixed-model alternative used most often in practice.

## Clinical decision-making under heterogeneous effects

In clinical and biomarker contexts the inferential question shifts: the clinician wants the predicted outcome **for this patient**, not whether a group mean differs from zero. The hierarchical machinery above adapts directly:

- The **posterior predictive distribution** $p(\tilde y \mid y)$ integrates over parameter uncertainty and gives a calibrated prediction interval for a new individual.
- Calibration of credible intervals at the individual level is a separate empirical question — see [AI → Uncertainty](../../ai/uncertainty.md) for the link to conformal prediction and reliability diagrams.

### Normative modelling

Normative modelling (Marquand et al., 2016) reframes the group GLM as a Bayesian model of **healthy variation** as a function of covariates (age, sex, site). Patients are then scored by how far their measured feature lies from the healthy posterior — a per-subject z-score or deviation map, rather than a group p-value.

This is the right framing when:

- The clinical population is heterogeneous (no single "patient mean" to compare against).
- You want a per-subject map you can show in clinic.
- Sample sizes for the patient group are small but the healthy reference is large.

Reference implementation: **PCNToolkit** ([github.com/amarquand/PCNtoolkit](https://github.com/amarquand/PCNtoolkit)) — Gaussian process and hierarchical Bayesian linear regression backends, with site harmonisation built in.

## Common pitfalls

- **HARKing** — Hypothesising After the Results are Known. Pre-register.
- **p-hacking** — repeatedly testing until something is significant.
- **Garden of forking paths** — analytical degrees of freedom inflate false-positive rate.
- **Confounding** — site, scanner, age, sex *will* confound your effect unless modelled.
- **Conditioning on a collider** — adjusting for a variable caused by both X and Y creates spurious associations.

[Botvinik-Nezer et al., 2020](https://doi.org/10.1038/s41586-020-2314-9) shows that 70 teams analysing the same data report 70 different conclusions. Discipline matters.

## Reporting checklist

- [ ] Effect size + confidence interval for every test.
- [ ] Multiple-comparison method explicitly named.
- [ ] Random effects (subject, site) modelled.
- [ ] Pre-registered or explicitly exploratory.
- [ ] Code + data available, or a justification for why not.
- [ ] Sensitivity analysis showing the conclusion is robust to reasonable analytic choices.

## Exercises

1. **GLM by hand.** With `X` (n×p) and `y` (n,), implement OLS via `np.linalg.lstsq` and via the normal equation `(X^T X)^(-1) X^T y`. Compare results.
2. **Permutation test.** Two independent samples; write a 1000-iteration permutation test for the difference in means.
3. **Power analysis.** What sample size does an independent-samples t-test need to detect Cohen's d = 0.4 at α = 0.05 and power = 0.8?

??? success "Solutions"
    1. `beta1, *_ = np.linalg.lstsq(X, y, rcond=None); beta2 = np.linalg.inv(X.T @ X) @ X.T @ y; np.allclose(beta1, beta2)` should be True.
    2. `obs = a.mean()-b.mean(); pool = np.concatenate([a,b]); cnt = sum(np.abs(np.random.permutation(pool)[:len(a)].mean()-np.random.permutation(pool)[len(a):].mean()) >= abs(obs) for _ in range(1000))/1000`.
    3. ~99 per group via `TTestIndPower().solve_power(effect_size=0.4, alpha=0.05, power=0.8)`.

## References

1. **Gelman A, Carlin JB, Stern HS, Dunson DB, Vehtari A, Rubin DB.** *Bayesian Data Analysis.* 3rd ed. CRC Press; 2013. ISBN 978-1439840955. Free online: [http://www.stat.columbia.edu/~gelman/book/](http://www.stat.columbia.edu/~gelman/book/)
2. **Hastie T, Tibshirani R, Friedman J.** *The Elements of Statistical Learning.* 2nd ed. Springer; 2009. ISBN 978-0387848570. Free online: [https://hastie.su.domains/ElemStatLearn/](https://hastie.su.domains/ElemStatLearn/)
3. **Cohen J.** *Statistical Power Analysis for the Behavioral Sciences.* 2nd ed. Routledge; 1988. ISBN 978-0805802832.
4. **Eklund A, Nichols TE, Knutsson H.** Cluster failure: why fMRI inferences for spatial extent have inflated false-positive rates. *PNAS.* 2016;113(28):7900-7905. [doi:10.1073/pnas.1602413113](https://doi.org/10.1073/pnas.1602413113)
5. **Marek S, Tervo-Clemmens B, Calabro FJ, et al.** Reproducible brain-wide association studies require thousands of individuals. *Nature.* 2022;603:654-660. [doi:10.1038/s41586-022-04492-9](https://doi.org/10.1038/s41586-022-04492-9)
6. **Winkler AM, Ridgway GR, Webster MA, Smith SM, Nichols TE.** Permutation inference for the general linear model. *NeuroImage.* 2014;92:381-397. [doi:10.1016/j.neuroimage.2014.01.060](https://doi.org/10.1016/j.neuroimage.2014.01.060)
7. **Botvinik-Nezer R, Holzmeister F, Camerer CF, et al.** Variability in the analysis of a single neuroimaging dataset by many teams. *Nature.* 2020;582:84-88. [doi:10.1038/s41586-020-2314-9](https://doi.org/10.1038/s41586-020-2314-9)
8. **Gelman A.** Prior distributions for variance parameters in hierarchical models. *Bayesian Analysis.* 2006;1(3):515-534. [doi:10.1214/06-BA117A](https://doi.org/10.1214/06-BA117A)
9. **Barr DJ, Levy R, Scheepers C, Tily HJ.** Random effects structure for confirmatory hypothesis testing: keep it maximal. *Journal of Memory and Language.* 2013;68(3):255-278. [doi:10.1016/j.jml.2012.11.001](https://doi.org/10.1016/j.jml.2012.11.001)
9. **Bates D, Kliegl R, Vasishth S, Baayen H.** Parsimonious mixed models. *arXiv.* 2015. [arXiv:1506.04967](https://arxiv.org/abs/1506.04967)
10. **Vehtari A, Gelman A, Gabry J.** Practical Bayesian model evaluation using leave-one-out cross-validation and WAIC. *Statistics and Computing.* 2017;27:1413-1432. [doi:10.1007/s11222-016-9696-4](https://doi.org/10.1007/s11222-016-9696-4)
11. **Marquand AF, Rezek I, Buitelaar J, Beckmann CF.** Understanding heterogeneity in clinical cohorts using normative models: beyond case-control studies. *Biological Psychiatry.* 2016;80(7):552-561. [doi:10.1016/j.biopsych.2015.12.023](https://doi.org/10.1016/j.biopsych.2015.12.023)

## Where to next

[Mathematics](mathematics.md) — the linear algebra, calculus, and signal processing under the statistics.
