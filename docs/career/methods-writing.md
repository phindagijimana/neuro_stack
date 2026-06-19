# Writing a reproducible methods section

> Another lab should be able to rerun your study from the methods alone. If they can't, the methods section is the bug.

The methods section is the part of the paper most people read carefully (reviewers, replicators, the meta-analyst who cites you in five years) and the part most authors write last, fastest, and worst. This page is a checklist and a template for fixing that.

It assumes you've already done the work. It does not teach you how to do science — only how to describe it so that someone else could.

## Why methods sections are usually bad

Three failure modes account for almost every reproducibility complaint:

1. **Vague.** "Standard preprocessing was performed using fMRIPrep." Which version? Which non-default flags? Which freesurfer license? Which container? "Standard" is a euphemism for "I don't remember."
2. **Irreproducible.** A pipeline is described, but the exact code, the container hash, and the parameter file are not shared. The reader can approximate; they cannot reproduce.
3. **Post-hoc.** The methods are written after the results are known, framed to make the analyses look planned. Exploratory steps appear confirmatory; the threshold that worked is the threshold that's reported.

A reproducible methods section is the antidote to all three: it is **specific**, **shareable**, and **time-stamped against a pre-registration** wherever possible.

## The minimum-information principle

The bar for "good methods" is operational, not aesthetic:

> Another competent lab, with access only to the paper and its supplementary materials, should be able to rerun the study end-to-end on a comparable dataset and reproduce the headline numbers within a defensible tolerance.

If that bar feels high, that is the bar. Everything below is in service of it.

The corollary: anything you would tell a careful collaborator over a shared screen should also be in the methods. The methods section is the persistent version of that conversation.

## Section-by-section template

A clean methods section has five subsections, in this order. Length is rarely the problem; specificity is.

### 1. Participants and sample size

- **Inclusion / exclusion criteria** — verbatim, not paraphrased.
- **Recruitment source** — clinic, registry, public dataset, community.
- **Demographics** — age (mean, SD, range), sex, handedness, race / ethnicity if reportable, clinical severity.
- **Sample size** — number screened, enrolled, excluded post-hoc and why. A flow diagram (CONSORT-style) is rarely wrong.
- **Power justification** — pilot d, simulation-based estimate, or pre-registered sequential-stopping rule. "Based on prior literature" is not a justification; cite the prior literature and the effect size you assumed.

For the design and power-analysis specifics, see [Analysis → Task fMRI design and power](../analysis/design.md).

### 2. Acquisition

- **Scanner** — vendor, model, field strength, software version (e.g. Siemens Prisma 3 T, syngo VE11C).
- **Coil** — receive channels.
- **Sequence parameters** — TR, TE, voxel size, FOV, matrix, parallel-imaging factor, multiband factor, b-values and directions for DWI, slice order, phase-encode direction, AP/PA fieldmap presence.
- **Acquisition duration** — per run, total.
- **Participant instructions and behaviour monitoring** — eye tracking, pulse, respiration belt.

Where a community standard exists, use it: **MRSinMRS** for spectroscopy, the **BIDS Dataset Description** fields for everything else.

### 3. Preprocessing

- **Pipeline name and version** — e.g. fMRIPrep 23.2.0, QSIPrep 0.21.0, FreeSurfer 7.3.2.
- **Container hash** — the Docker / Apptainer digest. This is the single most important line in your methods section. A version number without a digest can still drift; a `sha256:` digest cannot.
- **Non-default parameters** — every flag you changed from defaults, and why.
- **Manual interventions** — every subject where you re-ran with different settings, every QC failure you overrode.

Example, done well:

> "Preprocessing was performed using fMRIPrep 23.2.0 (RRID:SCR_016216), Docker digest `sha256:9a8b…c12`, with the flags `--use-aroma --output-spaces MNI152NLin2009cAsym:res-2 fsaverage5 --fs-license-file fs.lic`. No subjects required manual re-run. The full configuration is at `https://github.com/lab/study/blob/v1.0/code/run_fmriprep.sh`."

### 4. Analysis

- **Model specification** — first-level GLM regressors, contrasts, motion regression, denoising strategy (aCompCor, ICA-AROMA, scrubbing FD threshold).
- **Software and version** — e.g. nilearn 0.10.3, FSL 6.0.7.7, SPM12 r7771.
- **Threshold** — voxelwise p, cluster-defining threshold, FWE/FDR strategy.
- **Region definitions** — atlas name, version, transformation.
- **Group-level model** — design matrix, covariates, random vs fixed effects.

Pre-register the contrast and threshold; if you exploratorily added or changed either, say so.

### 5. Statistics

- **Multiple-comparison strategy** — cluster-level FWE via Gaussian random fields, non-parametric permutation via PALM / Randomise, TFCE, etc. Name it precisely.
- **Effect sizes** — Cohen's d, $\eta^2$, peak Z and cluster extent. A p-value alone is insufficient.
- **Confidence intervals** — for every reported effect.
- **Software** — package, version, random seed for any stochastic procedure (permutation, bootstrap).
- **Sharing of data and code** — repository URL, data DOI, release tag.

## Reporting standards you should know

Find the standard for your sub-field, fill out its checklist, and submit it as supplementary material. Reviewers increasingly require this; many journals now mandate it.

| Standard | Domain | Reference |
| --- | --- | --- |
| **COBIDAS** | Task and resting-state fMRI | Nichols et al., 2017 |
| **COBIDAS-MEEG** | MEG / EEG | Pernet et al., 2020 |
| **BIDS Dataset Description** | Any BIDS-compliant dataset | Gorgolewski et al., 2016 |
| **MRSinMRS** | Magnetic-resonance spectroscopy | Lin et al., 2021 |
| **CLAIM** | AI / ML in medical imaging | Mongan, Moy & Kahn, 2020 |
| **TRIPOD+AI** | Clinical prediction models | Collins et al., 2024 |
| **STARD** | Diagnostic-accuracy studies | Bossuyt et al., 2015 |
| **ARRIVE** | Animal-model studies | Percie du Sert et al., 2020 |
| **CONSORT** | Randomised trials | Schulz et al., 2010 |

For AI / ML-flavoured neuroimaging work, see also [AI/ML → Regulatory](../ai/regulatory.md) for the production-side reporting (CLAIM, TRIPOD+AI, model cards).

## Pre-registration

A pre-registration is a time-stamped commitment to the design and analysis plan, made *before* you see the analysed data.

- **OSF Registries** (<https://osf.io/registries>) — flexible templates; the de facto standard in cognitive neuroscience.
- **AsPredicted** (<https://aspredicted.org>) — short-form, eight questions; good for simple designs.
- **Registered Reports** — protocol peer-reviewed before data collection; the journal commits to publishing the results regardless of outcome. *Cortex*, *NeuroImage*, *eLife*, *Royal Society Open Science* all accept them.

What to lock down: the hypothesis, the contrast, the threshold, inclusion / exclusion criteria, the stopping rule. What to leave flexible: clearly-labelled exploratory analyses.

A pre-registration is not a prison. You can deviate — but you must report deviations honestly, in a section labelled "deviations from pre-registration."

## The methods supplement pattern

Modern methods sections are usually too long for the main text and too short for full reproducibility. The standard pattern is now:

- **Main-text methods** — narrative, ~1–2 pages, written for a non-specialist reader. Cite the supplement.
- **Methods supplement** — exhaustive: parameter files, container digests, every flag, every threshold.
- **Public repository** — code, environment, container recipe, intermediate scripts. Tagged with the release version corresponding to the publication.
- **Reporting-standard checklist** — COBIDAS / CLAIM / TRIPOD+AI checklist as a separate supplementary file.

The repository is the source of truth. The main-text methods is the executive summary. The supplement is the bridge.

## Before / after examples

### Example 1 — preprocessing

**Before** (one sentence; reproducible by nobody):

> "Data were preprocessed using fMRIPrep with standard settings."

**After** (specific, shareable, time-stamped):

> "Data were preprocessed using fMRIPrep 23.2.0 (RRID:SCR_016216; container digest `sha256:9a8b…c12`) with `--use-aroma`, `--fs-license-file fs.lic`, and `--output-spaces MNI152NLin2009cAsym:res-2 fsaverage5`. Two subjects required manual re-run of the susceptibility-distortion correction step due to fieldmap failure; both were re-run with `--use-syn-sdc`. The full configuration script is in the repository (<https://github.com/lab/study/blob/v1.0/code/run_fmriprep.sh>)."

### Example 2 — statistics

**Before:**

> "Significance was assessed at p < 0.05, corrected for multiple comparisons."

**After:**

> "Group-level inference used non-parametric permutation testing via FSL `randomise` 6.0.7.7 (5000 permutations, random seed 42), with threshold-free cluster enhancement [Smith & Nichols, 2009] and family-wise-error correction at $p_{\text{FWE}} < 0.05$. Cohen's d and 95% bootstrap confidence intervals are reported for each surviving cluster (Table 2)."

### Example 3 — sample size

**Before:**

> "Twenty-five subjects were recruited based on prior fMRI studies."

**After:**

> "We pre-registered a sample size of 25 based on a simulation-based power analysis [Mumford & Nichols, 2008] assuming Cohen's d = 0.5 for the A − B contrast (lower 95% CI of pilot estimate from N=8) and a target power of 0.80 at $\alpha = 0.05$, two-tailed. Simulation code: <https://osf.io/abcde>."

## Open materials — a sharing checklist

The minimum bar for a reproducible publication:

- [ ] **Code** — public repository, release-tagged at submission.
- [ ] **Environment** — `environment.yml` / `pyproject.toml` / `renv.lock`, plus the container recipe.
- [ ] **Container digest** — `sha256:` pinned in the methods.
- [ ] **Data** — raw and / or derivatives shared via OpenNeuro, NDA, GIN, Zenodo, or an institutional repository, with a DOI.
- [ ] **Data-use agreement and consent language** — if data sharing is restricted, document why and how to request access.
- [ ] **Reporting checklist** — COBIDAS / CLAIM / TRIPOD+AI as appropriate.
- [ ] **Pre-registration** — link in the methods.
- [ ] **README** — one paragraph telling a stranger how to reproduce Figure 2.

The 2023 NIH Data Management and Sharing Policy now expects most of this for NIH-funded work. Check your funder's specifics: NIH ([https://sharing.nih.gov](https://sharing.nih.gov)), Wellcome ([https://wellcome.org/grant-funding/guidance/open-access-guidance](https://wellcome.org/grant-funding/guidance/open-access-guidance)), and the EU Horizon Open Science requirements all converge on similar bars.

## Common reviewer asks

Pre-empt these in the first draft:

1. **"What was the rationale for the sample size?"** — power calculation, with the assumed effect size and source.
2. **"Why this threshold?"** — pre-registered or defended; do not just cite convention.
3. **"How were motion / physiological noise handled?"** — explicit denoising strategy.
4. **"Was the analysis pre-registered?"** — yes / no with a link or an honest "no, this is exploratory."
5. **"Where is the code?"** — public repository URL in the methods, not in a "code available on reasonable request" hand-wave.
6. **"What about site / scanner effects?"** — explicit harmonisation strategy (ComBat or equivalent) for multi-site data.
7. **"What about multiple comparisons across exploratory analyses?"** — separate exploratory section; do not bury the count.
8. **"Calibration and confidence intervals?"** — for any predictive model. See [AI/ML → Evaluation pitfalls](../ai/evaluation.md).

If the first draft answers all of these, the methods reviewer comments are usually about clarity, not about substance.

## References

1. **Nichols TE, Das S, Eickhoff SB, et al.** Best practices in data analysis and sharing in neuroimaging using MRI (COBIDAS). *Nat Neurosci.* 2017;20(3):299–303. [doi:10.1038/nn.4500](https://doi.org/10.1038/nn.4500)
2. **Pernet C, Garrido MI, Gramfort A, et al.** Issues and recommendations from the OHBM COBIDAS MEEG committee for reproducible EEG and MEG research. *Nat Neurosci.* 2020;23(12):1473–1483. [doi:10.1038/s41593-020-00709-0](https://doi.org/10.1038/s41593-020-00709-0)
3. **Gorgolewski KJ, Auer T, Calhoun VD, et al.** The brain imaging data structure (BIDS), a format for organizing and describing outputs of neuroimaging experiments. *Sci Data.* 2016;3:160044. [doi:10.1038/sdata.2016.44](https://doi.org/10.1038/sdata.2016.44)
4. **Lin A, Andronesi O, Bogner W, et al.** Minimum reporting standards for in vivo magnetic resonance spectroscopy (MRSinMRS). *NMR Biomed.* 2021;34(5):e4484. [doi:10.1002/nbm.4484](https://doi.org/10.1002/nbm.4484)
5. **Mongan J, Moy L, Kahn CE.** Checklist for Artificial Intelligence in Medical Imaging (CLAIM). *Radiol Artif Intell.* 2020;2(2):e200029. [doi:10.1148/ryai.2020200029](https://doi.org/10.1148/ryai.2020200029)
6. **Collins GS, Moons KGM, Dhiman P, et al.** TRIPOD+AI statement: updated guidance for reporting clinical prediction models. *BMJ.* 2024;385:e078378. [doi:10.1136/bmj-2023-078378](https://doi.org/10.1136/bmj-2023-078378)
7. **Bossuyt PM, Reitsma JB, Bruns DE, et al.** STARD 2015: an updated list of essential items for reporting diagnostic accuracy studies. *BMJ.* 2015;351:h5527. [doi:10.1136/bmj.h5527](https://doi.org/10.1136/bmj.h5527)
8. **Percie du Sert N, Hurst V, Ahluwalia A, et al.** The ARRIVE guidelines 2.0. *PLoS Biol.* 2020;18(7):e3000410. [doi:10.1371/journal.pbio.3000410](https://doi.org/10.1371/journal.pbio.3000410)
9. **Schulz KF, Altman DG, Moher D.** CONSORT 2010 statement. *BMJ.* 2010;340:c332. [doi:10.1136/bmj.c332](https://doi.org/10.1136/bmj.c332)
10. **Poldrack RA, Baker CI, Durnez J, et al.** Scanning the horizon: towards transparent and reproducible neuroimaging research. *Nat Rev Neurosci.* 2017;18(2):115–126. [doi:10.1038/nrn.2016.167](https://doi.org/10.1038/nrn.2016.167)
11. **Smith SM, Nichols TE.** Threshold-free cluster enhancement. *NeuroImage.* 2009;44(1):83–98. [doi:10.1016/j.neuroimage.2008.03.061](https://doi.org/10.1016/j.neuroimage.2008.03.061)
12. **NIH Office of Science Policy.** NIH Data Management and Sharing Policy. 2023. [https://sharing.nih.gov](https://sharing.nih.gov)

## Where to next

[Grant writing](grant-writing.md) — the same specificity, applied to a Specific Aims page. Or [AI/ML → Regulatory](../ai/regulatory.md) for the production-side reporting standards (CLAIM, TRIPOD+AI, model cards).
