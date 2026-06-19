# Task fMRI design and power analysis

> The result of your study is already determined the moment you finalise the paradigm. Bad design cannot be saved by clever statistics.

This chapter is about the work that happens *before* you scan a single subject: choosing the design class, modelling the HRF, balancing nuisance structure, and convincing yourself (and a reviewer, and a grant panel) that your sample size will actually detect the effect you care about.

If your analysis pipeline already runs, see [Functional connectivity](functional.md) and [Group-level statistics](group-stats.md); this page is upstream of both.

## Block vs event-related vs mixed

| Design | What it is | When to use |
| --- | --- | --- |
| **Block** | Long (~20-30 s) homogeneous epochs of one condition | Detection power. Localising a region that responds to a category at all. |
| **Event-related (slow)** | Single trials with long ISIs (~12-20 s) | Estimating the shape of the HRF; trial-wise decoding. |
| **Event-related (rapid)** | Single trials with short, jittered ISIs (~2-6 s) | Most cognitive paradigms; better estimation power than blocks for differentiating conditions. |
| **Mixed** | Block-level state + embedded trial events | Separating sustained from transient signals (e.g., attention vs detection). |

The classic trade-off [Birn et al., 2002](https://doi.org/10.1006/nimg.2002.1227)[^birn]:

- **Detection power** (is the region active at all?) peaks for blocks.
- **Estimation power** (what is the HRF shape?) peaks for slow event-related.
- **Rapid event-related** is the practical compromise for differentiating conditions.

If you cannot decide, start with rapid event-related and a hypothesis-driven contrast. Blocks are for binary "this region cares about faces" questions.

## The HRF and convolution intuition

The BOLD response to a single neural event is delayed and smeared by ~6 s. We model this as a linear time-invariant system:

$$
y(t) = (x * h)(t) = \int_{-\infty}^{\infty} x(\tau)\, h(t - \tau)\, d\tau
$$

- $x(t)$ — the stimulus regressor (1 at event onsets, 0 elsewhere).
- $h(t)$ — the canonical HRF (typically a difference of two gamma functions; SPM and FSL ship slightly different defaults).
- $y(t)$ — the predicted BOLD timecourse.

The first-level GLM fits $\beta$ for *the convolved regressor*, not the raw stimulus train. A 1 s event therefore produces a ~12 s ripple in the design matrix — which is why event spacing below ~2 s makes regressors highly collinear.

Two common upgrades:

- **Temporal + dispersion derivatives** (`SPM`'s default) — allow small shifts in HRF latency and width.
- **FIR / finite-impulse-response basis** — estimate one $\beta$ per post-onset timepoint per condition; useful when the canonical shape is suspect (children, patients, novel regions like brainstem).

## Counterbalancing, jittering, and orthogonality

Three nuisance structures will eat your effect if you let them:

1. **Order effects.** Counterbalance condition order across subjects (Latin square, m-sequence, or de Bruijn sequence). Never present all of condition A first.
2. **Stimulus repetition.** Adaptation halves the BOLD response on the second presentation. Either randomise across runs or include "novelty" as a regressor.
3. **Regressor collinearity.** If your contrast of interest is `A - B` but A and B always co-occur, the GLM cannot separate them. Compute the variance inflation factor (VIF) for each regressor — VIF > 5 is a warning, > 10 is a problem.

**Jittering** the ISI is what buys you orthogonality in rapid event-related designs. A fixed 4 s ISI synchronises the regressors with the slow components of low-frequency drift; an exponentially jittered ISI with mean ~4 s does not. Use `optseq2` or `nilearn`'s design utilities to optimise jitter for your specific contrast.

## Power analysis — three honest options

Reviewers now expect a power calculation. None of the off-the-shelf tools are perfect, so pick the one that matches your inference target.

### 1. Simulation-based [Mumford & Nichols, 2008](https://doi.org/10.1093/scan/nsn018)[^mn]

The gold standard. You simulate per-subject data under your effect size of interest, run your actual analysis pipeline (including motion regression, smoothing, multiple-comparison correction), and count rejections.

```python
import numpy as np
from nilearn.glm.first_level import make_first_level_design_matrix

n_subjects, n_sims = 25, 1000
tr, n_scans = 2.0, 200
frame_times = np.arange(n_scans) * tr

events = ...  # pandas DataFrame: onset, duration, trial_type
dm = make_first_level_design_matrix(frame_times, events, hrf_model="spm")
X = dm[["A", "B"]].to_numpy()
contrast = np.array([1.0, -1.0])

def sim_one_subject(true_beta):
    eps = np.random.randn(n_scans) * 1.0
    y = X @ true_beta + eps
    beta_hat = np.linalg.pinv(X) @ y
    return contrast @ beta_hat

rejections = 0
for _ in range(n_sims):
    cope = np.array([sim_one_subject(np.array([0.5, 0.0])) for _ in range(n_subjects)])
    t = cope.mean() / (cope.std(ddof=1) / np.sqrt(n_subjects))
    if abs(t) > 2.06:  # df=24, two-tailed alpha=0.05
        rejections += 1
print(f"power = {rejections / n_sims:.2f}")
```

Loop over `n_subjects` to find the smallest cohort that hits 80%.

### 2. G*Power for ROI inference

If you pre-register a single ROI and a single contrast, you have a single hypothesis test. G*Power's `t test` family handles it — feed it the expected Cohen's d (from pilot or literature) and the desired power.

For a within-subject paired t-test at d = 0.6, two-tailed alpha = 0.05, power = 0.8, you need ~24 subjects. For whole-brain voxel-wise inference at the same effect size, you need 2-4× more.

### 3. `neuropower` for whole-brain [Durnez et al., 2016](https://doi.org/10.1101/049429)[^np]

`neuropower` (<https://github.com/neuropower/neuropower>) reads a pilot statistical map and estimates the sample size needed for whole-brain FWE-corrected detection. It is the most defensible option for exploratory whole-brain studies.

## Pilot data and effect-size estimation

You almost never know the true effect size *a priori*. The honest options:

- **Use published effect sizes from similar paradigms.** Discount them ~30% — the published literature is biased upward by selective reporting.
- **Run a 5-10 subject pilot.** Estimate effect size with a wide confidence interval; use the *lower* CI bound for power calculations.
- **Use a region you trust as a positive control.** Motor cortex during finger tapping has a known d ≈ 1.5; if your pipeline shows d = 0.3 there, fix the pipeline before scanning the rest of the cohort.

Do not run your full analysis on the pilot and then add subjects until significance — that is p-hacking dressed up as power analysis.

## Pre-registration

A pre-registration is a time-stamped commitment to a design and analysis plan, made before data collection (or at least before unblinding).

- **OSF Registries** (<https://osf.io/registries>) — flexible, free, the standard for cognitive neuroscience.
- **AsPredicted** (<https://aspredicted.org>) — short-form; eight questions; for simple designs.
- **Registered Reports** — peer review of the protocol *before* you collect data; the journal commits to publishing the results regardless of outcome. Cortex, NeuroImage, and eLife all accept them.

What to lock down: the exact contrast, the threshold, the inclusion criteria, the stopping rule. What to leave flexible: exploratory analyses (just label them as such).

## Common design mistakes

- **All events at the same lag from run start.** Synchronises with scanner drift; null result.
- **Two conditions perfectly counterbalanced trial-by-trial.** Their regressors are anti-correlated; the difference contrast has high variance.
- **Modelling a 30 s block as one regressor.** Fine for detection; useless for trial-wise decoding.
- **Ignoring run effects.** Always include per-run intercepts (or run-mean regressors) when concatenating.
- **Counting catch trials in the contrast.** Catch trials are nuisance; model them separately.
- **Using a fast event-related design but reporting only block-level contrasts.** Wastes the design's information.

## Worked example — checking design efficiency

```python
import numpy as np, pandas as pd
from nilearn.glm.first_level import make_first_level_design_matrix

tr, n_scans = 2.0, 240
frame_times = np.arange(n_scans) * tr

def design_efficiency(events, contrast):
    dm = make_first_level_design_matrix(
        frame_times, events, hrf_model="spm + derivative",
        drift_model="cosine", high_pass=0.01,
    )
    X = dm.drop(columns=[c for c in dm.columns if "drift" in c or c == "constant"]).to_numpy()
    c = np.zeros(X.shape[1]); c[:len(contrast)] = contrast
    return 1.0 / (c @ np.linalg.pinv(X.T @ X) @ c.T)

# Two designs to compare
rng = np.random.default_rng(0)
fixed_isi = pd.DataFrame({
    "onset": np.arange(20, n_scans*tr - 20, 4.0),
    "duration": 0.5,
    "trial_type": np.tile(["A", "B"], 50)[:int((n_scans*tr - 40)/4.0)],
})
jittered = fixed_isi.copy()
jittered["onset"] = np.cumsum(rng.exponential(4.0, len(jittered))) + 20

print("fixed ISI efficiency:", design_efficiency(fixed_isi, [1, -1]))
print("jittered efficiency :", design_efficiency(jittered, [1, -1]))
```

Run it: the jittered design typically has 1.5-2× the efficiency of a fixed-ISI design for an A−B contrast. That is roughly the difference between 25 and 50 subjects of scanning.

!!! tip "Beginner takeaway"
    Five things to lock down before you scan:

    1. Block, event-related, or mixed — pick one and justify it.
    2. Counterbalance order across subjects.
    3. Jitter your ISI for any A vs B contrast.
    4. Check VIF / design efficiency on the planned design matrix.
    5. Pre-register the contrast and the threshold.

## References

[^birn]: Birn RM, Cox RW, Bandettini PA. Detection versus estimation in event-related fMRI: choosing the optimal stimulus timing. *NeuroImage.* 2002;15(1):252-264. [doi:10.1006/nimg.2002.1227](https://doi.org/10.1006/nimg.2002.1227)
[^mn]: Mumford JA, Nichols TE. Power calculation for group fMRI studies accounting for arbitrary design and temporal autocorrelation. *NeuroImage.* 2008;39(1):261-268. [doi:10.1016/j.neuroimage.2007.07.061](https://doi.org/10.1016/j.neuroimage.2007.07.061)
[^np]: Durnez J, Degryse J, Moerkerke B, et al. Power and sample size calculations for fMRI studies based on the prevalence of active peaks. *bioRxiv.* 2016. [doi:10.1101/049429](https://doi.org/10.1101/049429)

1. **Friston KJ, Zarahn E, Josephs O, et al.** Stochastic designs in event-related fMRI. *NeuroImage.* 1999;10(5):607-619. [doi:10.1006/nimg.1999.0498](https://doi.org/10.1006/nimg.1999.0498)
2. **Dale AM.** Optimal experimental design for event-related fMRI. *Hum Brain Mapp.* 1999;8(2-3):109-114.
3. **Poldrack RA, Baker CI, Durnez J, et al.** Scanning the horizon: towards transparent and reproducible neuroimaging research. *Nat Rev Neurosci.* 2017;18(2):115-126. [doi:10.1038/nrn.2016.167](https://doi.org/10.1038/nrn.2016.167)
4. **Munafò MR, Nosek BA, Bishop DVM, et al.** A manifesto for reproducible science. *Nat Hum Behav.* 2017;1:0021. [doi:10.1038/s41562-016-0021](https://doi.org/10.1038/s41562-016-0021)

## Where to next

[Quality control](qc.md) — once the design is locked, you still have to convince yourself the data is usable.
