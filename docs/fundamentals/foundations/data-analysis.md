# Data analysis

> Turning a folder of derivatives into a defensible analysis. The applied, hands-on layer between *statistics-the-theory* and *running-the-cluster*.

This page is about the day-to-day mechanics: cleaning tables, joining derivatives, exploring distributions, choosing a model, and producing the figure that will end up in the paper. The depth of *what test* is in [Statistics](statistics.md); this page is about *how the analysis actually happens*.

## A reproducible analysis workflow

Most published neuroimaging analyses follow a recognisable shape:

```text
raw BIDS dataset
    │
    ▼
preprocess (fMRIPrep, QSIPrep, FreeSurfer)
    │
    ▼
derivatives/  ── per-subject tables, NIfTI maps, surfaces
    │
    ▼
extract  ── one row per subject, columns = features
    │
    ▼
clean    ── missing, outliers, harmonisation (ComBat)
    │
    ▼
explore  ── distributions, correlations, QC plots
    │
    ▼
model    ── GLM, mixed effects, ML, group stats
    │
    ▼
report   ── figures, tables, methods text
```

Each arrow is a script you can re-run; the final figure is a function of the raw BIDS + the code.

## The cohort table — your single source of truth

For most analyses you'll end up with **one wide DataFrame** keyed by `subject_id` (or `(subject_id, session_id)`):

```python
import pandas as pd

participants = pd.read_csv("participants.tsv", sep="\t")
fs_stats     = gather_freesurfer_stats("derivatives/freesurfer/")  # 84 cols
qc           = pd.read_parquet("derivatives/mriqc/group_metrics.parquet")
beh          = pd.read_csv("behavioral.csv")

cohort = (
    participants
    .merge(fs_stats, on="subject_id", how="left", validate="one_to_one")
    .merge(qc,       on="subject_id", how="left", validate="one_to_one")
    .merge(beh,      on="subject_id", how="left", validate="one_to_one")
)
print(cohort.shape, cohort.columns.tolist())
```

Three habits to copy:

- **`validate="one_to_one"`** — fails loud if a join produces duplicates.
- **`how="left"`** — keep every subject; let missing imaging be `NaN`.
- **Save the joined table** to Parquet next to the inputs; the joining script is committed to git.

## Exploratory data analysis (EDA) — the part people skip

Before any inferential test, look at your data. The cost is hours; skipping it costs months.

### Univariate look

```python
import seaborn as sns, matplotlib.pyplot as plt

fig, axes = plt.subplots(2, 3, figsize=(12, 6))
for ax, col in zip(axes.ravel(), ["age", "fd_mean", "wm_volume",
                                  "lh_thickness_mean", "behavior_z",
                                  "education_years"]):
    sns.histplot(cohort[col].dropna(), ax=ax, kde=True)
    ax.set_title(col)
fig.tight_layout()
```

Check: range, skew, multimodality, the proportion of `NaN`. A bimodal "age" with peaks at 25 and 65 is a *cohort* problem, not an analysis problem.

### Bivariate look

```python
sns.pairplot(cohort[["age", "fd_mean", "behavior_z", "wm_volume"]],
             diag_kind="kde", corner=True)
```

Look for: implausible outliers, monotonic vs non-linear relationships, the well-known motion-age coupling.

### Missing-data audit

```python
miss = cohort.isna().mean().sort_values(ascending=False)
print(miss.head(20))
```

Three classes of missingness — covered in depth in the next section:

- **MCAR** — Missing Completely at Random. Drop or impute, your choice.
- **MAR** — Missing at Random *given* other observed variables. Multiple imputation or IPW.
- **MNAR** — Missing Not at Random. The hard case; usually requires sensitivity analysis.

Subjects who failed `recon-all` are *not* MCAR — they probably moved more. Drop them and you bias your effect.

## Missing-data mechanisms — MCAR, MAR, MNAR

[Rubin, 1976](https://doi.org/10.1093/biomet/63.3.581) introduced the taxonomy every modern missing-data method rests on. The mechanism is a statement about *what determines* whether a value is missing, not just how much is missing.

| Mechanism | Definition | Concrete neuroimaging example |
|---|---|---|
| **MCAR** — Missing Completely at Random | $P(R = 1 \mid Y, X) = P(R = 1)$. Missingness is independent of both observed and unobserved values. | Scanner crash mid-acquisition; a tech accidentally deletes a sequence. |
| **MAR** — Missing at Random | $P(R = 1 \mid Y, X) = P(R = 1 \mid X)$. Missingness depends on observed covariates only. | Drop-out at visit 3 predicted by baseline age, education, or baseline cognitive score — all measured. |
| **MNAR** — Missing Not at Random | Missingness depends on the *unobserved* value itself, $P(R = 1 \mid Y, X) \ne P(R = 1 \mid X)$. | Drop-out predicted by current cognitive decline at the missed visit; subjects fail `recon-all` because they moved more, and motion is correlated with the diagnosis under study. |

Why this matters: **complete-case analysis (CCA) is unbiased only under MCAR**. Under MAR, CCA is biased *and* inefficient; valid methods are multiple imputation ([`scikit-learn`'s `IterativeImputer`](https://scikit-learn.org/stable/modules/impute.html), R's [`mice`](https://amices.org/mice/)) or inverse-probability weighting (next section). Under MNAR the bias is worse, and no method recovers the truth without external assumptions — you fall back on sensitivity analysis. The bias grows as you move MCAR → MAR → MNAR *and* as the missingness fraction grows.

## Inverse-probability weighting (IPW)

When the missingness mechanism is MAR — observation depends on *measured* covariates — **inverse-probability weighting** restores an unbiased estimate by upweighting subjects whose covariates make them under-represented. The IPW estimator of the population mean is

$$
\hat\mu_{\text{IPW}} = \frac{1}{N}\sum_{i=1}^{N} \frac{R_i\,Y_i}{\hat\pi(X_i)}
$$

where $R_i \in \{0,1\}$ indicates whether subject $i$ is observed and $\hat\pi(X_i) = \widehat{P}(R_i = 1 \mid X_i)$ is the estimated observation probability — typically a logistic regression of $R$ on baseline covariates. Each observed subject "stands in" for $1/\hat\pi(X_i)$ subjects in the original population.

Why it works under MAR: conditional on $X$, observed and missing subjects have the same outcome distribution, so reweighting by $1/\hat\pi(X)$ recovers the population mean. The same logic underpins **propensity-score weighting** for causal-effect estimation (see the causal-inference section below).

```python
import numpy as np
import pandas as pd
from sklearn.linear_model import LogisticRegression

# X: baseline covariates, R: 1 if observed, Y: outcome (NaN where R==0)
covariates = ["age", "sex", "site", "baseline_score", "fd_baseline"]
pi_model = LogisticRegression(max_iter=1000).fit(cohort[covariates], cohort["observed"])
pi_hat   = pi_model.predict_proba(cohort[covariates])[:, 1]

# Stabilise extreme weights by truncating at the 1st/99th percentile
pi_clip  = np.clip(pi_hat, np.quantile(pi_hat, 0.01), 1.0)
w        = cohort["observed"] / pi_clip
mu_ipw   = (w * cohort["outcome"].fillna(0)).sum() / len(cohort)
```

Practical pitfalls:

- **Extreme weights.** A subject with $\hat\pi = 0.02$ contributes 50 times more than one with $\hat\pi = 1.0$ — one odd subject can dominate. Truncate at the 1st/99th percentile or use stabilised weights $w_i = \bar\pi / \hat\pi(X_i)$.
- **Model misspecification.** If the propensity model is wrong, $\hat\pi$ is wrong and IPW is biased. Calibrate (Brier score, reliability curve) and consider flexible learners ([`scikit-learn` gradient boosting](https://scikit-learn.org/stable/modules/ensemble.html), [`xgboost`](https://xgboost.readthedocs.io/)) — at the cost of variance.
- **Positivity violation.** If $\hat\pi(X_i) \approx 0$ for some $X_i$ (e.g. nobody at site 7 returned for visit 3), no amount of weighting recovers them. Inspect the propensity distribution and trim in regions of non-overlap.

**Doubly robust** estimators (augmented IPW / AIPW, targeted maximum-likelihood estimation / TMLE) combine an outcome model with a propensity model and are consistent if *either* is correct. Implementations: [`econml`](https://www.microsoft.com/en-us/research/project/econml/), [`doubleml`](https://docs.doubleml.org/), [`zEpid`](https://zepid.readthedocs.io/).

## Sensitivity analysis for unmeasured confounding

The hardest critique of any observational neuroimaging result is "what if there's an unmeasured confounder?" Sensitivity analysis quantifies *how strong* such a confounder would need to be to overturn the conclusion — moving the discussion from "could there be one?" (always yes) to "how plausible would it need to be?"

The **E-value** ([VanderWeele & Ding, 2017](https://doi.org/10.7326/M16-2607)) is the most widely reported sensitivity metric. For an observed risk ratio $\mathrm{RR}$,

$$
E = \mathrm{RR} + \sqrt{\mathrm{RR}\,(\mathrm{RR} - 1)}
$$

is the minimum strength of association (on the RR scale) that an unmeasured confounder would need with *both* exposure and outcome — beyond measured covariates — to fully explain the observed effect away. An E-value of 1.5 is easy to imagine; an E-value of 4.0 demands a confounder bigger than any measured covariate, which is much harder to argue. The [E-value calculator](https://www.evalue-calculator.com/) handles odds-ratio and continuous-outcome variants.

Related techniques:

- **R²-style tipping-point analysis** ([Cinelli & Hazlett, 2020](https://doi.org/10.1111/rssb.12348), implemented in [`sensemakr`](https://carloscinelli.com/sensemakr/)) — expresses the unmeasured confounder in terms of partial $R^2$ with treatment and outcome, plotting contours of the adjusted coefficient.
- **Negative controls** — outcomes that *should* be unaffected by exposure (e.g. fracture risk in a study of antidepressants and hippocampal volume). A non-null estimate on the negative control is evidence of residual confounding.

When the confounding is too severe for any sensitivity analysis to rescue, switch to **design-based** identification: **instrumental variables** (Mendelian randomisation in [UK Biobank](https://www.ukbiobank.ac.uk/) genetics), **regression discontinuity** (sharp treatment-guideline cut-offs), **difference-in-differences** (policy changes that affect some sites and not others). These rarely apply cleanly in neuroimaging, but when they do they are far more credible than yet another covariate-adjusted GLM.

## Causal inference primer for observational neuroimaging

Most group-level fMRI, connectomics, and morphometry analyses are **observational** — subjects are not randomly assigned to a diagnosis or to a level of cognition. Standard GLM coefficients therefore estimate *associations*, not causal effects. Claiming mechanism without the appropriate machinery is the single most common over-reach in the field.

The minimum toolkit:

**Potential outcomes (Neyman-Rubin) framework.** For each subject $i$, define $Y_i(1)$ and $Y_i(0)$ as the outcomes they would have under exposure and control. The individual treatment effect is $Y_i(1) - Y_i(0)$; the average treatment effect (ATE) is $\mathbb{E}[Y(1) - Y(0)]$. Only one of $Y_i(1)$, $Y_i(0)$ is ever observed (the fundamental problem of causal inference), so identification rests on assumptions: **consistency**, **positivity**, and **conditional exchangeability** ("no unmeasured confounders given $X$").

**Directed acyclic graphs (DAGs) and the back-door criterion.** A DAG encodes assumed causal relationships among variables; the back-door criterion ([Pearl, 1995](https://doi.org/10.1093/biomet/82.4.669)) tells you which set $Z$ of covariates is *sufficient* to adjust for to identify the causal effect of $X$ on $Y$. Draw the DAG explicitly with [DAGitty](https://www.dagitty.net/) and let it list the minimal adjustment sets — you will be surprised how often the "obvious" covariate set is wrong (adjusting for a mediator like ICV between brain volume and cognition blocks part of the effect of interest; adjusting for a collider like recruitment-into-study introduces selection bias).

**Propensity scores.** $e(X) = P(\text{exposure} = 1 \mid X)$. Matching, stratifying, or weighting (the IPW estimator above) on the propensity score balances covariates between groups and identifies the conditional treatment effect under exchangeability + positivity.

Practical tooling:

- [Hernán & Robins, *Causal Inference: What If*](https://www.hsph.harvard.edu/miguel-hernan/wp-content/uploads/sites/1268/2024/04/hernanrobins_WhatIf_26apr24.pdf) — the standard free textbook; the first six chapters cover the conceptual core.
- [DAGitty](https://www.dagitty.net/) — draw DAGs in the browser; export adjustment sets.
- [`dowhy`](https://www.pywhy.org/dowhy/) — Python library that forces you to write the DAG, identify the estimand, estimate it, and run refutation tests in sequence.
- [`econml`](https://www.microsoft.com/en-us/research/project/econml/) — heterogeneous-effect estimation (DR-learner, causal forests).

The high-level rule for observational neuroimaging studies in [ENIGMA](https://enigma.ini.usc.edu/), [ABCD](https://abcdstudy.org/), and [UK Biobank](https://www.ukbiobank.ac.uk/): name your estimand, draw the DAG, justify the adjustment set, and stop writing "X causes Y" in the abstract unless the design supports it. Cross-link to [AI → Evaluation](../../ai/evaluation.md) for the predictive-model analogue (counterfactual reasoning, decision-curve analysis, fairness audits).

## Outlier handling

Two categories:

- **Statistical outliers** — outside expected distribution. Often legitimate biology; rarely drop.
- **QC failures** — bad acquisition, failed preprocessing. Drop, but document.

The MRIQC group report ([Esteban et al., 2017](https://doi.org/10.1371/journal.pone.0184661)) gives per-subject IQMs (Image Quality Metrics) you can threshold. Don't drop subjects based on the analysis-of-interest variable — that's circular.

## Harmonisation — when sites or scanners differ

Multi-site cohorts have site/scanner variance that often exceeds biology.

### ComBat — the workhorse

[Johnson et al., 2007](https://doi.org/10.1093/biostatistics/kxj037) (microarray origin) and the neuroimaging adaptation [Fortin et al., 2018](https://doi.org/10.1016/j.neuroimage.2017.11.024) model site as an additive + multiplicative effect on each feature; estimate it empirical-Bayes-shrunk; subtract. Implementations: [`neuroCombat`](https://github.com/Jfortin1/ComBatHarmonization), [`neuroHarmonize`](https://github.com/rpomponio/neuroHarmonize) (preserves biology), longitudinal ComBat.

```python
from neuroCombat import neuroCombat
res = neuroCombat(
    dat=cohort_features.T.values,            # features × subjects
    covars=cohort[["site", "age", "sex", "diagnosis"]],
    batch_col="site",
    categorical_cols=["sex", "diagnosis"],
    continuous_cols=["age"],
)
harmonised = pd.DataFrame(res["data"].T, columns=cohort_features.columns)
```

Always preserve the **biological covariates** during harmonisation. Always validate that harmonisation didn't accidentally remove your effect.

### Site as a covariate — when ComBat overcorrects

Sometimes the right answer is `y ~ age + sex + site + ...` in the GLM. Cheap and transparent; doesn't generalise to a held-out site, but neither does ComBat.

## Confound regression — the fMRI special case

fMRIPrep emits `*_desc-confounds_timeseries.tsv` with ~30 columns. Standard regressors:

| Strategy | Columns |
|---|---|
| **6 motion** | `trans_x/y/z`, `rot_x/y/z` |
| **24 motion** | The 6 + squares + derivatives + derivative squares |
| **aCompCor** | Top 5 PCA components from CSF + WM masks |
| **ICA-AROMA** | Use the AROMA-cleaned BOLD as input |
| **Global signal** | Controversial; document either way |

Pick one strategy and use it across your cohort. Mixing strategies inside a single analysis is a reviewer's gift.

## Missing data mechanisms (MCAR / MAR / MNAR)

The EDA section above named the three classes; this section is the depth — what each one assumes, what it breaks, and which tool is safe under which assumption. Rubin's 1976 taxonomy is the canonical reference.

### Definitions

Let $R_i = 1$ if observation $i$ is observed and $0$ otherwise; let $Y_i$ be the outcome and $X_i$ the covariates.

- **MCAR** — missing completely at random: $R \perp (Y, X)$. The missingness mechanism is independent of everything you care about.
- **MAR** — missing at random: $R \perp Y \mid X_{\text{observed}}$. The probability of being missing depends only on observed covariates.
- **MNAR** — missing not at random: $R$ depends on the unobserved $Y$ itself even after conditioning on $X$.

### Why it matters in neuroimaging

Dropouts in longitudinal cohorts are almost never MCAR. Patients whose cognition deteriorates are more likely to miss the year-3 scan; subjects with high in-scanner motion are more likely to have failed reconstructions. Both produce MNAR for the endpoint you actually want to model. The naive complete-case mean of cognition at year 3 is then biased *upward*, and any treatment effect estimated from it is biased toward zero.

### Default strategies and what they assume

| Strategy | Valid under | Notes |
|---|---|---|
| **Complete-case analysis** | MCAR only | Drops any row with missingness; biased under MAR/MNAR. |
| **Mean / median imputation** | Essentially never | Shrinks variance and distorts covariance; do not use. |
| **Multiple imputation (MI)** | MAR | Impute $m$ times, fit the model $m$ times, pool with Rubin's rules. Tools: [`mice`](https://amices.org/mice/) (R), [`IterativeImputer`](https://scikit-learn.org/stable/modules/impute.html) (sklearn), [`miceforest`](https://github.com/AnotherSamWilson/miceforest) (Python, gradient-boosted). |
| **Mixed-effects with MLE** | MAR for the outcome | `lme4` / `statsmodels.mixedlm` give consistent estimates under MAR for $Y$, but assume MAR for covariates. |
| **Inverse-probability weighting (IPW)** | MAR (correctly-specified propensity) | Reweights observed sample back to the target population; details below. |
| **Pattern-mixture / selection models** | MNAR | Require an explicit, untestable assumption about the missingness mechanism; use as sensitivity analyses. |

The longitudinal page has more on dropout in repeated-measures designs: see [Analysis → Longitudinal modelling](../../analysis/longitudinal.md).

## Inverse-probability weighting in practice

IPW is the workhorse for MAR data when you don't want to commit to a parametric imputation model. The idea: each observed unit stands in for itself and for the units like it that were lost; weight by the inverse probability of being observed.

### The recipe

1. **Propensity model.** Fit a logistic regression for the probability of being observed, using the baseline covariates: $\hat p_i = \widehat{P}(R_i = 1 \mid X_i)$.
2. **Raw weights.** $w_i = 1 / \hat p_i$.
3. **Stabilise** (S-IPW). Replace raw weights with stabilised ones to reduce variance:

    $$
    sw_i = \frac{P(R = 1)}{\widehat{P}(R = 1 \mid X_i)}
    $$

   where $P(R=1)$ is the marginal observation probability.
4. **Trim extreme weights.** Cap at the 1st and 99th percentiles (or at a fixed value like 10) to avoid variance explosion from tiny propensity scores.
5. **Fit the substantive model** weighted by $w$ (or $sw$): weighted OLS, weighted GLM, or weighted GEE.

### Worked Python snippet

```python
import numpy as np
import statsmodels.api as sm

# Step 1: propensity model for being observed.
ps = sm.Logit(observed, sm.add_constant(X_base)).fit().predict()

# Step 2: raw IPW weights.
w = observed / ps + (1 - observed) / (1 - ps)

# Step 3: stabilise.
p_marg = observed.mean()
sw = np.where(observed == 1, p_marg / ps, (1 - p_marg) / (1 - ps))

# Step 4: trim at 1st / 99th percentile.
lo, hi = np.quantile(sw, [0.01, 0.99])
sw = np.clip(sw, lo, hi)

# Step 5: weighted outcome regression on the observed subset.
mask = observed == 1
fit = sm.WLS(y[mask], sm.add_constant(X[mask]), weights=sw[mask]).fit()
print(fit.summary())
```

### When IPW shines

- Longitudinal cohorts with informative dropout where you have rich baseline covariates that predict who stays.
- Case-control designs where sampling fractions differ by stratum.
- Multi-site studies where the per-site observed fraction varies — IPW reweights toward a target population.

### When IPW fails

- **Tiny propensity scores.** Any $\hat p_i$ near zero or one explodes the weights; a single subject can dominate the regression.
- **Positivity violations.** If some covariate stratum has $P(R = 1 \mid X) \approx 0$, no weighting can rescue inference there; the target population was never sampled.
- **Mis-specified propensity model.** IPW is only as good as the model for $\hat p_i$; this is why doubly-robust methods (e.g. AIPW, TMLE) are increasingly the default in causal-inference workflows.

## Sensitivity analysis for observational neuroimaging

Observational neuroimaging — almost all of it — sits under the shadow of **unmeasured confounders**. Sensitivity analysis is the discipline of quantifying how much hidden confounding would be needed to overturn a result, and is rapidly becoming a reviewer expectation.

### E-value (VanderWeele & Ding, 2017)

The **E-value** is the minimum strength of association, on the risk-ratio scale, that an unmeasured confounder would need to have with both the exposure and the outcome — above and beyond measured covariates — to fully explain away the observed effect. For a risk ratio $RR > 1$:

$$
E\text{-value} = RR + \sqrt{RR \,(RR - 1)}
$$

An E-value of 2.0 means a confounder would need to roughly double the risk of both exposure and outcome to nullify the result; an E-value of 1.1 means a tiny confounder is enough. The corresponding number for the lower confidence-interval bound is reported alongside.

### Tipping-point analysis

Parametrise an assumed confounder by its association with exposure and outcome; sweep over the parameter space and find the contour where the adjusted effect crosses zero. Reviewers will accept "the result tips only at confounder effect sizes larger than any covariate already in the model" but will not accept "we adjusted for what we had and hoped".

### Negative controls

A **negative-control outcome** is a variable that should *not* be affected by the exposure (e.g. eye colour vs. cortical thickness). A **negative-control exposure** is one that should not affect the outcome. If the negative control shows a "significant" effect under your analysis, residual confounding is the leading explanation. The technique is borrowed from pharmacoepidemiology and translates cleanly to multi-site imaging cohorts.

### Worked framing: cortical thickness vs. cognition

Suppose an observational cohort shows that mean cortical thickness predicts a cognitive composite ($\beta = 0.32$, 95% CI $[0.18, 0.46]$, adjusted for age, sex, education, site). To defend it:

1. **E-value** on $\beta$ and its lower CI bound (after converting to an approximate RR if the outcome is dichotomised; see VanderWeele & Ding for the continuous-outcome formula).
2. **Negative-control outcome**: refit the model with hair colour (or any biologically implausible outcome) as the dependent variable; a null result strengthens the original.
3. **Negative-control exposure**: replace cortical thickness with a feature known to be unrelated to cognition; should yield a null.
4. **Tipping-point**: simulate an unmeasured confounder correlated $r = 0.3$ with both age-residualised thickness and cognition; report the strength at which the effect crosses zero.

### Tools

- **`EValue`** R package — single-call E-value computation with built-in plots.
- **`tipr`** R package — tipping-point analyses with a clean API.
- **Manual sensitivity in Python** — for simple sweeps; no widely-adopted package as of 2026, but the formulas in VanderWeele & Ding are short enough to implement directly.

### Why this matters in neuroimaging

Brain-imaging features routinely co-vary with age, sex, education, scanner, and site. Several high-profile brain-wide association results have failed to replicate when the original cohort's confounding structure did not transfer (Marek et al., 2022). A sensitivity analysis paragraph in the methods is cheap insurance and increasingly expected by editors at *NeuroImage*, *Brain*, and *Nature Mental Health*.

## Feature extraction — from voxels to a row

Many analyses become tabular at this step. Examples:

```python
# FreeSurfer thickness per DK region → 1 row of 68 features per subject
df = pd.read_csv("aparc.lh.thickness.tsv", sep="\t")

# Mean BOLD timecourse per Schaefer-400 parcel → 1 row per subject after FC
from nilearn.maskers import NiftiLabelsMasker
masker = NiftiLabelsMasker(labels_img="Schaefer400.nii.gz", standardize=True)
ts = masker.fit_transform("sub-001_bold.nii.gz",
                         confounds="sub-001_desc-confounds.tsv")

# Connectome upper triangle → 79,800 features per subject (Schaefer-400)
import numpy as np
conn = np.corrcoef(ts.T)
triu = conn[np.triu_indices_from(conn, k=1)]
```

Decide early whether to analyse voxel-wise (mass-univariate maps) or feature-wise (tabular ML). Both have a place; mixing strategies hurts.

## Pipelines for the analysis itself

The same data-engineering primitives apply to *analysis*: DAG, idempotency, observability. For an iterative analysis I recommend:

- **Snakemake / Nextflow** for cohort-scale recomputation. See [Data engineering → Foundations](../../data-engineering/foundations.md).
- **Make** for small projects (`make figs/fig2.pdf`).
- **Notebook** for the final figure, *restarted and run from the top* before publication.
- **`papermill` + parameterised notebooks** for per-subject reports.

## A pragmatic figure recipe

Most paper figures are some variant of:

```python
# Figure 2: cohort age effect on cortical thickness, by site
import seaborn as sns
sns.set_theme(style="whitegrid", context="paper", font_scale=1.1)

g = sns.lmplot(
    data=cohort, x="age", y="mean_thickness",
    hue="site", col="diagnosis", height=3.6, aspect=1.1,
    scatter_kws={"alpha": 0.5, "s": 25}, line_kws={"lw": 2},
)
g.set_axis_labels("Age (years)", "Mean cortical thickness (mm)")
for ax in g.axes.ravel():
    ax.set_xlim(18, 90)
g.savefig("figs/fig2_age_thickness.pdf", bbox_inches="tight", dpi=300)
```

Save vector formats (`.pdf`, `.svg`) — journals will rasterise them at 600+ DPI. Keep raw data behind every figure committed (`figs/fig2_data.parquet`) so reviewers can ask "but what about excluding...".

## Building dashboards / reports

For per-cohort reports (especially during data collection):

- **Plotly + Dash** ([docs](https://dash.plotly.com)) — Python web dashboards.
- **Streamlit** ([docs](https://docs.streamlit.io)) — minimal-code web apps.
- **Quarto** ([docs](https://quarto.org)) — versioned scientific reports, Python + R + Jupyter.
- **Static HTML** — sometimes the right choice; everyone can open it.

For internal labs that just want "is the QC dashboard fresh?", a single `cohort_qc.html` regenerated on every Snakemake run beats a stack of cloud infrastructure.

## Common pitfalls

- **Concatenating instead of joining.** `pd.concat(axis=0)` stacks; if you meant a wide join you'll silently double rows.
- **`pd.merge` without `validate`.** A many-to-many join produces row explosions you won't catch until the analysis says n=4892 instead of 489.
- **Plotting with default Matplotlib for paper figures.** Default DPI is too low; default font is ugly. Set up once, reuse.
- **Not saving the intermediate cohort table.** A reviewer asks "what happens if you exclude subjects with FD > 0.3?" — be able to answer in 30 seconds, not an afternoon.
- **Running analysis in a notebook only.** Notebooks should be the *presentation* layer; the logic should be importable modules with tests.

## A reproducibility audit (10 minutes)

Before sending an analysis to a co-author, run this checklist:

- [ ] `make` or `snakemake -n` reports zero changes (everything is up to date).
- [ ] `pytest` passes.
- [ ] The cohort table CSV / Parquet hash is committed.
- [ ] Every figure script writes a sibling `.tsv` of its raw data.
- [ ] The seed for any randomised step is fixed and recorded.
- [ ] The container / lockfile is documented.
- [ ] A `methods.md` paragraph summarising what was done is up to date.

## Exercises

1. **Missing-data audit.** Read `participants.tsv`. Print the percentage missing per column, sorted descending; classify each column as likely MCAR, MAR, or MNAR with one sentence each.
2. **Group K-Fold.** Using `sklearn.model_selection.GroupKFold`, set up a 5-fold split on a synthetic DataFrame with 50 subjects across 3 sites. Verify no subject ID appears in train and test of the same fold.
3. **ComBat sanity check.** After harmonisation, compute the F-statistic for `site` predicting each harmonised feature. Report what changed vs raw.

??? success "Solutions"
    1. `df.isna().mean().sort_values(ascending=False) * 100`; reason from domain knowledge.
    2. `gkf = GroupKFold(5); for tr, te in gkf.split(X, y, groups=df['subject_id']): assert set(df.iloc[tr]['subject_id']) & set(df.iloc[te]['subject_id']) == set()`.
    3. Use `scipy.stats.f_oneway` per feature, comparing pre/post; per-feature F values should drop substantially.

## References

1. **McKinney W.** *Python for Data Analysis.* 3rd ed. O'Reilly; 2022. ISBN 978-1098104030. Free online: [https://wesmckinney.com/book/](https://wesmckinney.com/book/)
2. **Tukey JW.** *Exploratory Data Analysis.* Addison-Wesley; 1977. ISBN 978-0201076165.
3. **Wickham H, Çetinkaya-Rundel M, Grolemund G.** *R for Data Science.* 2nd ed. O'Reilly; 2023. ISBN 978-1492097402. Free online: [https://r4ds.hadley.nz/](https://r4ds.hadley.nz/) — the EDA chapters generalise across languages.
4. **Fortin J-P, Cullen N, Sheline YI, et al.** Harmonization of cortical thickness measurements across scanners and sites. *NeuroImage.* 2018;167:104-120. [doi:10.1016/j.neuroimage.2017.11.024](https://doi.org/10.1016/j.neuroimage.2017.11.024)
5. **Pomponio R, Erus G, Habes M, et al.** Harmonization of large MRI datasets for the analysis of brain imaging patterns throughout the lifespan. *NeuroImage.* 2020;208:116450. [doi:10.1016/j.neuroimage.2019.116450](https://doi.org/10.1016/j.neuroimage.2019.116450) — neuroHarmonize.
6. **Esteban O, Birman D, Schaer M, et al.** MRIQC: advancing the automatic prediction of image quality in MRI from unseen sites. *PLoS One.* 2017;12(9):e0184661. [doi:10.1371/journal.pone.0184661](https://doi.org/10.1371/journal.pone.0184661)
7. **Botvinik-Nezer R, Holzmeister F, Camerer CF, et al.** Variability in the analysis of a single neuroimaging dataset by many teams. *Nature.* 2020;582:84-88. [doi:10.1038/s41586-020-2314-9](https://doi.org/10.1038/s41586-020-2314-9)
8. **Allen M, Poggiali D, Whitaker K, et al.** Raincloud plots: a multi-platform tool for robust data visualization. *Wellcome Open Res.* 2021;4:63. [doi:10.12688/wellcomeopenres.15191.2](https://doi.org/10.12688/wellcomeopenres.15191.2)
9. **Rubin DB.** Inference and missing data. *Biometrika.* 1976;63(3):581-592. [doi:10.1093/biomet/63.3.581](https://doi.org/10.1093/biomet/63.3.581)
10. **Robins JM, Hernán MA, Brumback B.** Marginal structural models and causal inference in epidemiology. *Epidemiology.* 2000;11(5):550-560. [doi:10.1097/00001648-200005000-00012](https://doi.org/10.1097/00001648-200005000-00012)
11. **VanderWeele TJ, Ding P.** Sensitivity analysis in observational research: introducing the E-value. *Annals of Internal Medicine.* 2017;167(4):268-274. [doi:10.7326/M16-2607](https://doi.org/10.7326/M16-2607)
12. **Marek S, Tervo-Clemmens B, Calabro FJ, et al.** Reproducible brain-wide association studies require thousands of individuals. *Nature.* 2022;603:654-660. [doi:10.1038/s41586-022-04492-9](https://doi.org/10.1038/s41586-022-04492-9)

## Where to next

[Statistics](statistics.md) — the inferential layer on top of the workflows on this page.
