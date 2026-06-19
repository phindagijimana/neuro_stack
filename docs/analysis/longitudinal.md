# Longitudinal and mixed-effects models

> The most common mistake in longitudinal neuroimaging is treating repeated measures as independent observations. Do that, and your p-values are wrong by an order of magnitude.

This page covers the modelling layer that sits above [Group-level statistics](group-stats.md) once you have more than one scan per subject — whether that's a 12-month follow-up, a treatment trial, or a developmental trajectory.

## Why repeated measures are special

Two scans from the same person are not two independent observations. The covariance structure looks like:

$$
\text{Cov}(y_{ij}, y_{ik}) = \sigma_b^2 \quad (j \ne k, \text{ same subject } i)
$$

with $\sigma_b^2$ the between-subject variance and $\sigma_w^2$ the within-subject (residual) variance. The **intraclass correlation** is

$$
\text{ICC} = \frac{\sigma_b^2}{\sigma_b^2 + \sigma_w^2}.
$$

For cortical thickness, ICC ≈ 0.9; for fMRI connectivity, often ≈ 0.4-0.6; for diffusion metrics, ≈ 0.8. The higher the ICC, the more catastrophic it is to ignore the structure: standard errors are too small, t-statistics inflated, false-positive rate explodes.

The fix: a linear mixed model (LMM) with a random subject term.

## The model

$$
y_{ij} = \beta_0 + \beta_1 \text{time}_{ij} + \beta_2 \text{group}_i + \beta_3 (\text{time} \times \text{group})_{ij} + b_{0i} + b_{1i} \text{time}_{ij} + \varepsilon_{ij}
$$

- $\beta$ — fixed effects (population-level slopes / intercepts).
- $b_{0i}$ — random intercept per subject (individual baseline).
- $b_{1i}$ — random slope per subject (individual rate of change).
- $\varepsilon_{ij}$ — residual.

The interesting clinical effect is usually $\beta_3$ — the time × group interaction, i.e., do groups diverge?

## R — `lme4` is the reference

```r
library(lme4)
library(lmerTest)

m <- lmer(thickness ~ time * group + age0 + sex + (1 + time | subj), data = df,
          REML = TRUE)
summary(m)
anova(m)        # F-tests with Satterthwaite df via lmerTest
confint(m)      # profile-likelihood CIs
```

R remains the most defensible choice for longitudinal stats; reviewers expect `lme4` output for non-trivial models.

## Python — `statsmodels` and `pymer4`

`statsmodels.MixedLM` handles random intercepts well and random slopes acceptably; for crossed random effects or non-Gaussian outcomes, use `pymer4` (which wraps `lme4` from Python) or `bambi` (PyMC under the hood).

```python
import statsmodels.formula.api as smf
import pandas as pd
df = pd.read_csv("long.csv")  # cols: subj, time, group, age0, sex, thickness

m = smf.mixedlm(
    "thickness ~ time * group + age0 + sex",
    data=df, groups=df["subj"],
    re_formula="~ time",
).fit(method="lbfgs", reml=True)
print(m.summary())
```

Notes:

- `re_formula="~ time"` adds the random slope. Drop it for intercept-only.
- `method="lbfgs"` is more robust than the default `bfgs` for complex variance structures.
- Use `groups` (not a formula) for the cluster variable — `statsmodels` quirk.

## Random intercepts vs random slopes

| You should include a random slope if... | You can stay intercept-only if... |
| --- | --- |
| Subjects clearly differ in their rates of change | All subjects move at roughly the same rate |
| You report a time × group interaction | You only report a main effect of group |
| Pilot variance components estimate $\sigma_{b1}^2 > 0$ | Likelihood-ratio test for random slope is n.s. |

The "maximal random-effect structure" advice [Barr et al., 2013](https://doi.org/10.1016/j.jml.2012.11.001)[^barr] is to include every random effect supported by the design. In practice, that often fails to converge — in which case, drop random slopes for the highest-order interactions first.

## Convergence troubleshooting

You will see warnings like `Model failed to converge` or `singular fit`. The order of operations:

1. **Centre and scale continuous predictors.** A baseline age of 65 ± 8 in raw units pushes the optimiser into ill-conditioned territory.
2. **Try a different optimiser.** `lme4`: `bobyqa`, `Nelder_Mead`. `statsmodels`: `lbfgs`, `powell`.
3. **Simplify the random-effects structure.** Drop random slopes for nuisance variables first.
4. **Check for boundary fits.** A near-zero random-effect variance with a `singular` warning means the random effect isn't supported by the data; drop it.
5. **Switch to ML estimation** (`REML = FALSE`) for likelihood-ratio tests comparing nested fixed-effect structures; back to REML for the final fit.

## Missing data — MCAR, MAR, MNAR

The three mechanisms [Little & Rubin, 2019](https://doi.org/10.1002/9781119482260)[^lr]:

- **MCAR** — missing completely at random. Drop-out unrelated to anything observed or unobserved. Rare; complete-case analysis is unbiased.
- **MAR** — missing at random. Drop-out related to *observed* covariates (e.g., older subjects miss more visits). LMMs under MAR with ML give unbiased estimates of the fixed effects, *if* the model is correctly specified.
- **MNAR** — missing not at random. Drop-out related to the *unobserved* outcome (e.g., subjects who would have shown atrophy drop out *because* of disease). No general fix; requires sensitivity analysis or pattern-mixture models.

Practical defaults:

- Use ML-based LMMs (not GEE) — they handle MAR correctly.
- Report the drop-out pattern: how many subjects at each visit, by group.
- Run a sensitivity analysis under a plausible MNAR scenario (e.g., last-observation-carried-forward, multiple imputation with `mice` in R or `IterativeImputer` in `sklearn`).

## FreeSurfer longitudinal stream [Reuter et al., 2012](https://doi.org/10.1016/j.neuroimage.2012.02.084)[^reuter]

Standard `recon-all` processes each timepoint independently — but the registration noise is then re-introduced into your slope estimates. The FreeSurfer longitudinal stream:

1. Cross-sectionally process each timepoint (`recon-all -all`).
2. Build a within-subject template (`recon-all -base`).
3. Re-process each timepoint *initialised from the template* (`recon-all -long`).

Result: dramatically reduced within-subject variance in cortical thickness; ~30-50% increase in power for slope detection. Always use it for any longitudinal FreeSurfer study.

```bash
recon-all -base tp_template -tp tp1.nii.gz -tp tp2.nii.gz -all
recon-all -long tp1 tp_template -all
recon-all -long tp2 tp_template -all
```

## Within-subject percent change and annualised rates

Two derived measures the clinical literature loves:

$$
\text{Percent change} = 100 \cdot \frac{y_{i,2} - y_{i,1}}{y_{i,1}}
$$

$$
\text{Annualised rate} = \frac{y_{i,2} - y_{i,1}}{y_{i,1}} \cdot \frac{12}{\Delta t_\text{months}}
$$

They are useful for descriptive tables but inferior to LMM slopes for statistical inference. Never use them when interval lengths vary across subjects without re-introducing $\Delta t$ as a covariate.

## Bayesian alternatives

For small samples, weakly identified random-effect variances, or hierarchical structures with > 2 levels, Bayesian LMMs are usually more honest about uncertainty.

- **R**: `brms` (Stan back-end), `rstanarm`. Same formula syntax as `lme4`.
- **Python**: `PyMC`, `bambi`. `bambi` mirrors `brms`'s formula API.

```python
import bambi as bmb
model = bmb.Model("thickness ~ time * group + age0 + sex + (1 + time | subj)", data=df)
idata = model.fit(draws=2000, chains=4, target_accept=0.95)
print(model.summary(idata, kind="diagnostics"))
```

Watch the divergences and $\hat R$; if either is off, reparametrise (non-centred for random effects) or set tighter priors.

## Power for longitudinal studies

The closed-form approximation for a two-group × two-timepoint design [Diggle et al., 2002] generalises to LMMs via simulation. The R package `longpower` and Python's `LMMpower` give analytic solutions for common designs; for anything bespoke, simulate:

```python
import numpy as np
from statsmodels.formula.api import mixedlm
import pandas as pd

def sim_power(n, n_sims=500, alpha=0.05):
    rej = 0
    for _ in range(n_sims):
        subj = np.repeat(np.arange(n), 3)
        time = np.tile([0, 1, 2], n)
        group = np.repeat(np.random.choice([0, 1], n), 3)
        b0i = np.random.randn(n).repeat(3) * 0.5
        b1i = np.random.randn(n).repeat(3) * 0.1
        eps = np.random.randn(n*3) * 0.3
        y = 2.5 + 0.0*time + 0.0*group + (-0.15)*time*group + b0i + b1i*time + eps
        df = pd.DataFrame(dict(y=y, subj=subj, time=time, group=group))
        try:
            m = mixedlm("y ~ time * group", df, groups=df["subj"],
                        re_formula="~ time").fit(reml=False, method="lbfgs")
            p = m.pvalues["time:group"]
            if p < alpha: rej += 1
        except Exception:
            continue
    return rej / n_sims

for n in [30, 60, 90, 120]:
    print(f"n={n}: power = {sim_power(n):.2f}")
```

Run a sweep; pick the smallest $n$ that gives 80%. Honest power calculation requires simulating under your *actual* model, not a t-test approximation.

## Worked example — fitting a longitudinal cortical-thickness model

```python
import pandas as pd
import statsmodels.formula.api as smf

df = pd.read_csv("ct_long.csv")  # subj, visit_months, group, age0, sex, ct_lh_precuneus
df["time_yr"] = df["visit_months"] / 12.0
df["age0_c"] = df["age0"] - df["age0"].mean()

m = smf.mixedlm(
    "ct_lh_precuneus ~ time_yr * group + age0_c + sex",
    data=df, groups=df["subj"], re_formula="~ time_yr",
).fit(method="lbfgs", reml=True)

print(m.summary())
print("\nAnnual decline (control):", m.params["time_yr"])
print("Group × time interaction:",  m.params["time_yr:group[T.patient]"],
      "p =", m.pvalues["time_yr:group[T.patient]"])
```

The interaction coefficient is the *difference in slopes* between patients and controls — that's the clinical effect.

## Common pitfalls

- **Treating visits as repeated levels of a between-subject factor.** Inflates df; wrong.
- **Modelling time as categorical when intervals vary.** Loses information; pool with caution.
- **Forgetting to centre time at baseline.** Intercepts become uninterpretable; can hurt convergence.
- **Reading "p > 0.05" on the random slope variance as evidence of no slope variation.** It's underpowered; use AIC / BIC instead.
- **Running an LMM per voxel without correction.** Voxel-wise LMMs at the whole-brain level need permutation; see [Multiple comparisons](multiple-comparisons.md).

!!! tip "Beginner takeaway"
    Five-step longitudinal workflow:

    1. Lock the data: one row per (subject, visit), with `time_yr` and group columns.
    2. Centre `age0`; express `time_yr` from baseline.
    3. Fit an intercept-only LMM first; add random slopes if the model converges.
    4. Report the time × group interaction with a 95% CI, not just a p-value.
    5. Document the drop-out pattern and run one MNAR sensitivity analysis.

## References

[^barr]: Barr DJ, Levy R, Scheepers C, Tily HJ. Random effects structure for confirmatory hypothesis testing: keep it maximal. *J Mem Lang.* 2013;68(3):255-278. [doi:10.1016/j.jml.2012.11.001](https://doi.org/10.1016/j.jml.2012.11.001)
[^lr]: Little RJA, Rubin DB. *Statistical Analysis with Missing Data.* 3rd ed. Wiley; 2019. [doi:10.1002/9781119482260](https://doi.org/10.1002/9781119482260)
[^reuter]: Reuter M, Schmansky NJ, Rosas HD, Fischl B. Within-subject template estimation for unbiased longitudinal image analysis. *NeuroImage.* 2012;61(4):1402-1418. [doi:10.1016/j.neuroimage.2012.02.084](https://doi.org/10.1016/j.neuroimage.2012.02.084)

1. **Bates D, Mächler M, Bolker B, Walker S.** Fitting linear mixed-effects models using lme4. *J Stat Softw.* 2015;67(1):1-48. [doi:10.18637/jss.v067.i01](https://doi.org/10.18637/jss.v067.i01)
2. **Bernal-Rusiel JL, Greve DN, Reuter M, Fischl B, Sabuncu MR.** Statistical analysis of longitudinal neuroimage data with linear mixed effects models. *NeuroImage.* 2013;66:249-260. [doi:10.1016/j.neuroimage.2012.10.065](https://doi.org/10.1016/j.neuroimage.2012.10.065)
3. **Bürkner P-C.** brms: an R package for Bayesian multilevel models using Stan. *J Stat Softw.* 2017;80(1):1-28. [doi:10.18637/jss.v080.i01](https://doi.org/10.18637/jss.v080.i01)
4. **Diggle PJ, Heagerty P, Liang K-Y, Zeger SL.** *Analysis of Longitudinal Data.* 2nd ed. Oxford; 2002.

## Where to next

[RSA and encoding/decoding models](rsa-decoding.md) — for when group-level mean differences aren't enough and you want to ask what information a region carries.
