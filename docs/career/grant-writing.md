# Grant writing for neuroimaging

> A grant is a sales document with footnotes. Reviewers spend ten minutes on yours; they decide in the first one. Write accordingly.

This page is about the documents and budgets that pay for the work. It does not romanticise the process. It assumes you have a project worth funding and a track record consistent with the funder's level — those are the prerequisites, not the deliverables.

If you have neither, the answer is not "write better"; it is to do more work and try again later. This page helps with everything between those two.

## Funding landscape

Different funders have different incentives. Match the project to the mechanism, not the other way around.

| Funder | Mechanism | Career stage | Duration | Direct costs | Notes |
| --- | --- | --- | --- | --- | --- |
| **NIH** | F31 | PhD trainee | 2–5 y | Stipend + tuition | Predoctoral; institute-specific. |
| **NIH** | F32 | Postdoc (≤3 y in) | 2–3 y | Stipend + research | Postdoc fellowship. |
| **NIH** | K99/R00 | Late postdoc | 2 + 3 y | ~$90 k → ~$249 k/y | Mentored → independent transition. The single most career-shaping NIH mechanism. |
| **NIH** | K01 | Early career | 3–5 y | Salary + research | Mentored career-development. |
| **NIH** | K23 | Clinician-scientist | 3–5 y | Salary + research | Patient-oriented research; for MDs. |
| **NIH** | R21 | Any | 2 y | ≤$275 k total | Exploratory / high-risk. No preliminary data *required*. |
| **NIH** | R01 | Independent | 3–5 y | ~$250–500 k/y | The flagship; the bar is high. |
| **NIH** | R03 | Any | 2 y | ≤$50 k/y | Small grants. Underused. |
| **NSF** | CAREER | Assistant prof | 5 y | ~$500 k–1 M total | Research + education plan. |
| **NSF** | Standard / BRAIN | Any | 3 y | Variable | Less translational than NIH. |
| **EU Horizon** | ERC Starting / Consolidator / Advanced | Stage-gated | 5 y | €1.5–3.5 M | Single PI, blue-sky. |
| **EU Horizon** | MSCA Postdoc | Postdoc | 1–2 y | Salary + mobility | Fellowship; requires moving country. |
| **Wellcome** | Discovery Awards, Early Career | Any | 5–8 y | £1–3 M | Generous, flexible, hard to win. |
| **MRC (UK)** | Programme / Project / CDA | Any | 3–5 y | Variable | UK-focused. |
| **BBSRC (UK)** | sLoLa / pump-priming | Any | 3–5 y | Variable | Less neuro than MRC; biology-flavoured. |
| **Foundations** | Brain & Behavior (NARSAD), Simons, CZI, Doris Duke, McKnight, Klingenstein | Variable | 1–5 y | $50–250 k/y | Faster, smaller, less paperwork than federal. Underused by junior investigators. |

For institute-specific NIH guidance:

- **NIMH** — [https://www.nimh.nih.gov/funding](https://www.nimh.nih.gov/funding) — psychiatric and circuit-level work; computational psychiatry is a current priority.
- **NIA** — [https://www.nia.nih.gov/research/grants-funding](https://www.nia.nih.gov/research/grants-funding) — ageing, ADRD; large cohort programmes (ADNI, A4).
- **NINDS** — [https://www.ninds.nih.gov/funding](https://www.ninds.nih.gov/funding) — stroke, TBI, epilepsy, MS, ALS; method-development is welcomed but must be linked to a disease.

The NIH Reporter ([https://reporter.nih.gov](https://reporter.nih.gov)) is the single best research tool: it lets you read every funded grant in your area. Read at least ten before you write one.

## The Specific Aims page

The Specific Aims page is one page. Every reviewer reads it. Many reviewers read *only* it. Treat it as the document, and the rest of the proposal as the appendix.

The structure that works:

1. **Hook paragraph (3–5 sentences).** The problem. The gap. The cost of leaving the gap unfilled. End with a one-sentence statement of the long-term goal.
2. **Overall objective / central hypothesis (1 paragraph).** What this specific proposal will accomplish, and the testable hypothesis it rests on. Name the conceptual innovation here.
3. **Aims (1 paragraph each, 2–3 aims).** Each aim has:
   - A one-sentence title (verb-first: "Determine…", "Establish…", "Develop…").
   - The working hypothesis specific to that aim.
   - The approach, in two or three sentences.
   - The expected outcome — what success looks like.
4. **Innovation / Impact paragraph (4–6 sentences).** What changes in the field if this works. Be specific about who uses the result and how.

A clean Specific Aims page has:

- Three aims, not two (one is suspicious), not four (one will get cut by reviewers).
- Aims that are conceptually distinct, not technically sequential. "Aim 2 fails if Aim 1 fails" is a red flag.
- One sentence at the end of each aim describing the **deliverable**: a model, a dataset, a method, a clinical biomarker.
- A figure if it earns its space. A bad figure is worse than no figure.

## Significance — framing for non-imagers

Most of your reviewers are not imagers. The Significance section must convince a clinician, a statistician, and a circuit neuroscientist that the *problem* matters before you ask any of them to evaluate your *solution*.

The structure:

1. **Disease / scientific burden.** Numbers. Prevalence, mortality, cost, unanswered question. Cite the canonical recent review.
2. **What is currently done.** State of the art, including its limits.
3. **What is missing.** The specific gap your work fills. Be honest — overclaiming the gap is the most common reviewer complaint.
4. **Why now.** New data, new method, new collaboration that makes this possible *this cycle*.

For neuroimaging-flavoured proposals, the "why now" answer is often: a new sequence, a new pipeline, a new atlas, a new public cohort (UK Biobank, ABCD, HCP, ADNI, ENIGMA), or a new computational substrate. Name it.

## Innovation

NIH study sections score Innovation as a separate criterion. Two kinds count:

- **Methodological innovation.** A new pipeline, a new model class, a new acquisition technique. Imaging methods papers are the easy case here.
- **Translational / conceptual innovation.** Applying an existing method to a question where it has never been applied. The Innovation here is the *bridge*, not the method.

Avoid claiming innovation that's only "this combination of methods has not been applied to this disease before." Reviewers see this framing every cycle and discount it.

## Approach — rigour and fallbacks

The Approach section is where grants are won or lost. The standard structure for each Aim:

1. **Rationale.** Why this experiment, this design, this analysis.
2. **Experimental design.** Recruitment, acquisition, behavioural, intervention.
3. **Analysis plan.** Pipelines (with versions), models, statistics, thresholds.
4. **Power analysis.** A concrete sample-size justification. See [Analysis → Task fMRI design and power](../analysis/design.md).
5. **Expected results and interpretation.** What success looks like; what the alternative outcomes mean.
6. **Potential problems and fallback strategies.** Every aim. No exceptions.

The fallback paragraph is the single highest-ROI investment in the Approach. Reviewers explicitly look for it; its absence is the most-cited weakness in unfunded NIH proposals (the "no alternative if X fails" critique).

A good fallback paragraph names:

- The most likely failure mode of the aim ("If recruitment falls below 80% of target…").
- The decision criterion ("…by month 18 of year 2…").
- The pivot ("…we will draw on the public ABCD cohort to address Aim 2 in a complementary sample.").

## Preliminary data — how much, what kind

The unwritten rule: **R01** needs enough preliminary data to make the approach feel low-risk. **R21** is meant to be high-risk, but in practice still needs feasibility data. **F31 / F32 / K99** need enough to demonstrate *you* can do the work.

What counts:

- A pilot dataset, even small (N = 5–10), showing your pipeline produces the expected effect.
- A published or pre-printed methods paper demonstrating the technique on benchmark data.
- A figure showing convergent evidence from a public cohort (UK Biobank, HCP) that the effect is real.
- A letter of support from a collaborator who controls the cohort or the scanner time.

What does not count:

- A figure from someone else's paper, recoloured.
- Simulations alone.
- "We have access to N=200 subjects" with no analysis shown.

## Power-analysis appendices

Reviewers expect a power calculation that:

1. Names the effect size assumed, and cites or shows where it came from.
2. Specifies the test (whole-brain, ROI, multivariate, longitudinal mixed model).
3. Reports the assumed correction strategy.
4. Reports the target power and alpha.

A defensible imaging power-analysis snippet for a between-groups ROI contrast at d = 0.5:

```python
from statsmodels.stats.power import TTestIndPower

analysis = TTestIndPower()
n_per_group = analysis.solve_power(
    effect_size=0.5,   # Cohen's d from pilot lower 95% CI
    alpha=0.05,
    power=0.80,
    alternative="two-sided",
)
print(f"n per group = {n_per_group:.0f}")  # ~64 per group
```

For voxelwise whole-brain inference at the same effect size, multiply the per-group N by 2–4 and justify the multiplier with simulation. For a defensible whole-brain power calculation see [Analysis → Task fMRI design and power](../analysis/design.md), which walks through the Mumford & Nichols (2008) and `neuropower` (Durnez et al., 2016) approaches.

## Common reviewer criticisms — and how to pre-empt them

The four critiques that sink the most neuroimaging proposals:

| Critique | Pre-emption |
| --- | --- |
| "Not enough preliminary data." | Include a Figure 1 with your own pilot showing the effect in your hands, on your scanner. |
| "Methods are routine." | Pull one methodological choice into the Innovation section and defend it with a sub-figure. Or state explicitly that the project's novelty is conceptual, not methodological, and link it to the disease question. |
| "No fallback if X fails." | One paragraph at the end of each Aim. Named failure mode, decision point, pivot. |
| "Sample size is too small." | Pre-emptive power-analysis appendix with simulation code in the supplement. Cite Mumford & Nichols, 2008 for the calculation. |

Two further critiques specific to imaging:

- **"Multi-site heterogeneity not addressed."** Name your harmonisation strategy (ComBat, RAVEL, or site as a random effect) and cite the validation.
- **"Pipelines are not pre-registered."** Pre-register the pipeline version and parameter file on OSF; cite the registration in the Approach.

## Budget realism for imaging studies

Reviewers can spot an unrealistic budget. Round numbers:

| Item | Typical cost (US, 2024) |
| --- | --- |
| 3 T research scan, 1 hour | $500–900 |
| 7 T research scan, 1 hour | $900–1500 |
| MEG hour | $500–1000 |
| PET tracer + scan | $2 000–5 000 |
| Cloud compute (per subject, full fMRIPrep) | $5–20 |
| HPC core-hour | $0.01–0.05 internal; $0.05–0.15 commercial |
| Apptainer / Docker registry | $0–500 / y |
| FreeSurfer / FSL / SPM | Free for academic |
| MATLAB license (per seat) | $800–2 000 / y |
| Postdoc FTE (fully loaded, US) | $80–140 k / y |
| Graduate student FTE (fully loaded, US) | $50–80 k / y |
| Statistician 5% effort | $7–15 k / y |
| Subject incentive (per scan) | $25–100 |

For imaging-heavy R01s, the scan budget alone is often $80–200 k / year. Build the per-subject cost line by line; reviewers will ask.

## K vs F vs R timeline

A rough timeline of mechanisms, for someone moving from PhD through faculty:

```
PhD year 2–3:   F31 (predoctoral fellowship)
PhD year 5+:    F32 (postdoc fellowship)
Postdoc 2–3 y:  K99/R00 — apply ~6 months before the 4-year postdoc deadline
Faculty year 1–3: K23 (clinician) or K01 (basic) or first R01
Faculty year 2–5: R01 — the goal of the K mechanism
```

For non-NIH paths: a parallel ladder is MSCA postdoc → ERC Starting → ERC Consolidator → ERC Advanced in the EU, or a Wellcome Early Career → Wellcome Discovery in the UK. The lesson is the same — apply for the next mechanism while the current one is funding you, not after it ends.

## Resubmission strategy

Most successful NIH grants are second or third submissions. The data:

- ~10–20% of R01s are funded on first submission.
- ~30–35% are funded on resubmission (A1).

After NIH eliminated the A2 in 2014, only one resubmission is allowed per submitted version. The right strategy:

1. **Read the summary statement immediately. Then do not respond for two weeks.** Visceral reactions to reviewer comments make worse rebuttals.
2. **Triage the critiques.** Three buckets: factual errors (rare), legitimate weaknesses (common), and stylistic preferences (also common).
3. **Address every critique in the introduction.** One paragraph per reviewer, in their numbering. Tone: respectful, specific, evidence-driven. Never sarcastic; never dismissive.
4. **Add data where possible.** Even a small new figure can change the score.
5. **Resubmit fast.** Within 1–2 cycles, before the field moves on.

If the summary statement contains the phrase "enthusiasm was dampened by" three or more times, the proposal is not resubmittable as-is; it needs structural revision (different Aims, different Innovation framing), not a rebuttal.

## The data-engineering portfolio angle

For grants that involve releasing software, a pipeline, a model, or a public dataset, the proposal is stronger if you can credibly commit to *operating* the artefact, not just publishing it. The [Data engineering → Portfolio roadmap](../data-engineering/portfolio-roadmap.md) walks through the milestones (Snakemake port, CI, observability, warehouse layer) that turn a pipeline into an operable artefact. The same milestones are exactly what an NIH reviewer wants to see in a "Resource Sharing" plan for a software-producing R01.

## Where to next

[Transitions](transitions.md) — the career moves that determine which funder you'll be writing to in five years. Or [Methods writing](methods-writing.md) for the same specificity, applied to the paper a grant will eventually produce.

## References

1. **NIH Reporter.** [https://reporter.nih.gov](https://reporter.nih.gov)
2. **NIH Grants & Funding.** [https://grants.nih.gov](https://grants.nih.gov)
3. **NIH Office of Extramural Research — Application Guide.** [https://grants.nih.gov/grants/how-to-apply-application-guide.html](https://grants.nih.gov/grants/how-to-apply-application-guide.html)
4. **NSF — Proposal & Award Policies and Procedures Guide (PAPPG).** [https://www.nsf.gov/publications/pub_summ.jsp?ods_key=pappg](https://www.nsf.gov/publications/pub_summ.jsp?ods_key=pappg)
5. **EU Horizon Europe Funding & Tenders Portal.** [https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home](https://ec.europa.eu/info/funding-tenders/opportunities/portal/screen/home)
6. **European Research Council.** [https://erc.europa.eu](https://erc.europa.eu)
7. **Wellcome.** [https://wellcome.org/grant-funding](https://wellcome.org/grant-funding)
8. **UKRI / MRC.** [https://www.ukri.org/councils/mrc](https://www.ukri.org/councils/mrc)
9. **Mumford JA, Nichols TE.** Power calculation for group fMRI studies accounting for arbitrary design and temporal autocorrelation. *NeuroImage.* 2008;39(1):261–268. [doi:10.1016/j.neuroimage.2007.07.061](https://doi.org/10.1016/j.neuroimage.2007.07.061)
10. **Durnez J, Degryse J, Moerkerke B, et al.** Power and sample size calculations for fMRI studies based on the prevalence of active peaks. *bioRxiv.* 2016. [doi:10.1101/049429](https://doi.org/10.1101/049429)
11. **Poldrack RA, Baker CI, Durnez J, et al.** Scanning the horizon: towards transparent and reproducible neuroimaging research. *Nat Rev Neurosci.* 2017;18(2):115–126. [doi:10.1038/nrn.2016.167](https://doi.org/10.1038/nrn.2016.167)
12. **Bourne PE, Chalupa LM.** Ten simple rules for getting grants. *PLoS Comput Biol.* 2006;2(2):e12. [doi:10.1371/journal.pcbi.0020012](https://doi.org/10.1371/journal.pcbi.0020012)
