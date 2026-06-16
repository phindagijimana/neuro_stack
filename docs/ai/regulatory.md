# Regulatory, reporting, and clinical-deployment

> What separates a published model from a deployable one. SaMD, the reporting standards (TRIPOD+AI, CLAIM), model cards, the FDA's predetermined-change-control framework, and the documentation an audit will ask for.

This chapter assumes you've read [AI/ML → Evaluation pitfalls](evaluation.md). The evaluation chapter covered *how to know your model is honest*. This one covers *how to make it shippable*.

## Software as a Medical Device (SaMD)

The international regulatory frame for software that performs a clinical function on its own is **SaMD** (IMDRF definition). The defining question: does the software produce information that *drives a clinical decision*?

- Detecting a stroke on a CT? SaMD.
- A radiologist-assist that highlights suspicious regions but requires sign-off? Still typically SaMD, lower risk class.
- A research-only segmentation tool used by neuroscientists for a paper? *Not* SaMD.

The IMDRF risk framework crosses the **state of the patient** (critical → non-serious) with the **significance of the information** (treat/diagnose → inform). The four resulting classes map to FDA Class I-III equivalents and EU MDR Class IIa-IIb-III.

If you're building any model that will touch a clinical decision path, read:

- **IMDRF SaMD documents.** [https://www.imdrf.org/working-groups/software-medical-device-samd](https://www.imdrf.org/working-groups/software-medical-device-samd)
- **FDA SaMD overview.** [https://www.fda.gov/medical-devices/digital-health-center-excellence/software-medical-device-samd](https://www.fda.gov/medical-devices/digital-health-center-excellence/software-medical-device-samd)
- **EU MDR / IVDR** as applicable.

## TRIPOD+AI — the reporting standard for clinical-prediction models

[TRIPOD+AI](https://doi.org/10.1136/bmj-2023-078378) (Collins et al., 2024) is the modern reporting checklist for clinical prediction studies that use machine learning. 27 items grouped into:

- **Title + abstract** — declare it's an AI/ML model.
- **Source of data** — cohort definition, eligibility, time-frame, sites.
- **Participants** — demographics, sample-size justification.
- **Outcome** — definition and any blinding.
- **Predictors / inputs** — including pre-processing.
- **Sample size** — and how it was determined.
- **Missing data** — handling strategy.
- **Statistical analysis** — model class, hyper-parameters, training procedure.
- **Risk groups** — calibration, decision-curve analysis.
- **Model performance** — discrimination, calibration, fairness, with confidence intervals.
- **Model interpretability** — and the limits of that interpretability.
- **External validation** — different population, different site, different time.
- **Open science** — code + protocol + model weights availability.

Every paper that publishes a clinical-prediction model should fill in the TRIPOD+AI checklist as a supplementary file. Reviewers increasingly require it.

## CLAIM — for medical-imaging AI specifically

[CLAIM](https://doi.org/10.1148/ryai.2020200029) (Mongan, Moy & Kahn, 2020) — Checklist for Artificial Intelligence in Medical Imaging — is the imaging-specific complement to TRIPOD. 42 items spanning model design, data acquisition, training, and evaluation. Free template: [https://pubs.rsna.org/doi/10.1148/ryai.2020200029](https://pubs.rsna.org/doi/10.1148/ryai.2020200029).

The CLAIM items that catch the most people:

- **Source code availability** — most published models still aren't released.
- **Reproducibility of metrics** — exact splits, seeds, library versions.
- **Performance on out-of-distribution data** — site held-out, scanner held-out.
- **Failure-case analysis** — show three subjects where the model is wrong; explain why.

## Model cards

[Model cards](https://doi.org/10.1145/3287560.3287596) (Mitchell et al., 2019) are short, structured documents — 1-3 pages — that ship with the model. The minimum sections:

```markdown
# Model card — stroke_lesion_segmenter v1.0.0

## Intended use
- Primary use: automated segmentation of acute ischemic stroke
  lesions on DWI volumes.
- NOT intended for: chronic lesions, haemorrhage, paediatric data,
  pre-clinical animal data.

## Training data
- Source: 412 subjects from ATLAS v2.0 across 11 sites.
- Demographics: median age 64 (IQR 55-72); 58% male; 92% white.
- Pre-processing: brain-extracted, MNI152NLin2009cAsym, 1 mm isotropic.

## Evaluation
- Held-out test set: 89 subjects from ATLAS site 12.
- Cross-site test set: 50 subjects from a private MGH cohort.
- Reported metrics: Dice 0.71 (95% CI 0.68-0.74); HD95 6.8 mm;
  sensitivity at fixed specificity 0.85 = 0.79.

## Limitations
- Performance drops to Dice 0.58 on lesions < 1 mL.
- Tested only on 1.5 T and 3 T data; not validated at 7 T.
- Bias: under-represents older female patients.

## Ethical considerations
- Not FDA cleared.
- Should not be used for clinical decisions without radiologist
  oversight.

## Citation
@misc{...}
```

For neuroimaging models specifically, Hugging Face's model-card template ([here](https://huggingface.co/docs/hub/model-cards)) plus the CLAIM checklist together cover almost every documentation question an auditor will ask.

## FDA's Predetermined Change Control Plan (PCCP)

A traditional FDA submission locks the model at clearance time — changing a single weight requires re-clearance. **The PCCP framework** ([FDA draft guidance, 2024](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial)) lets you pre-declare:

- The **types of changes** you anticipate (e.g. periodic retraining on more data).
- The **methods** for making those changes (data quality bar, retraining protocol, validation).
- The **performance maintenance** — every iteration must hit the cleared metrics or trigger a halt.

If your roadmap includes "retrain quarterly on more sites", PCCP is how you get FDA clearance once and iterate within the plan rather than re-submit every quarter.

## What an auditor will actually ask

Practical questions you'll get:

1. **Show me the training data inventory** — every file, its source, its consent, its de-identification status.
2. **Show me the train / validation / test splits** — proof of subject-level separation.
3. **Show me the model artifact + the exact code that produced it** — git SHA, lockfile, container digest.
4. **Show me the test-set performance** — with CIs, per subgroup.
5. **Show me the failure modes you've documented.**
6. **Show me the model card.**
7. **Show me the post-deployment monitoring plan.**

A complete answer set is a multi-week documentation effort. Build the artifacts during development, not after.

## Post-deployment monitoring

Once a model is live, you need:

- **Drift detection** on the input distribution (PSI, KL divergence on key features).
- **Performance monitoring** on a labelled feedback sample.
- **Adverse-event capture** — every clinically significant model error logged.
- **Periodic re-validation** on fresh held-out cohorts.

For a clinical deployment, expect to spend at least as much engineering effort on monitoring as on initial training. [Sculley et al., 2015](https://papers.nips.cc/paper/2015/hash/86df7dcfd896fcaf2674f757a2463eba-Abstract.html) ("Hidden Technical Debt in Machine Learning Systems") is required reading.

## Equity and bias

The FDA increasingly asks about **performance equity** across demographic subgroups. Practical steps:

- Report metrics stratified by sex, age band, race/ethnicity, scanner vendor, field strength.
- Run a **fairness audit** using a structured tool ([Fairlearn](https://fairlearn.org), [Aequitas](https://github.com/dssg/aequitas)).
- Document data-collection bias and downstream risk.
- For genuine reproducibility, the train-test split must include subgroup labels.

## The minimal pre-deployment checklist

- [ ] TRIPOD+AI checklist completed (supplementary file).
- [ ] CLAIM checklist completed.
- [ ] Model card committed in repo.
- [ ] Training-data inventory with consent / de-identification status.
- [ ] Code + container digest + lockfile pinned at the trained checkpoint.
- [ ] Subject-level + site-level held-out evaluation.
- [ ] Per-subgroup performance stratified by demographics.
- [ ] Failure cases documented (≥ 3, with discussion).
- [ ] Monitoring plan (drift, performance, adverse events).
- [ ] Regulatory pathway identified (SaMD class, FDA / EU MDR / research-only).
- [ ] Post-deployment retraining policy + PCCP if applicable.

If you can tick all 11 you're ready for a serious external review.

## References

1. **Collins GS, Moons KGM, Dhiman P, et al.** TRIPOD+AI statement: updated guidance for reporting clinical prediction models that use regression or machine learning methods. *BMJ.* 2024;385:e078378. [doi:10.1136/bmj-2023-078378](https://doi.org/10.1136/bmj-2023-078378)
2. **Mongan J, Moy L, Kahn CE.** Checklist for Artificial Intelligence in Medical Imaging (CLAIM). *Radiol Artif Intell.* 2020;2(2):e200029. [doi:10.1148/ryai.2020200029](https://doi.org/10.1148/ryai.2020200029)
3. **Mitchell M, Wu S, Zaldivar A, et al.** Model cards for model reporting. *FAT\*.* 2019. [doi:10.1145/3287560.3287596](https://doi.org/10.1145/3287560.3287596)
4. **FDA.** Marketing Submission Recommendations for a Predetermined Change Control Plan for Artificial Intelligence/Machine Learning (AI/ML)-Enabled Device Software Functions. Draft guidance. 2024. [https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial](https://www.fda.gov/regulatory-information/search-fda-guidance-documents/marketing-submission-recommendations-predetermined-change-control-plan-artificial)
5. **IMDRF.** Software as a Medical Device (SaMD) — key definitions and risk categorisation framework. [https://www.imdrf.org/working-groups/software-medical-device-samd](https://www.imdrf.org/working-groups/software-medical-device-samd)
6. **Sculley D, Holt G, Golovin D, et al.** Hidden technical debt in machine learning systems. *NeurIPS.* 2015. [pdf](https://papers.nips.cc/paper/2015/file/86df7dcfd896fcaf2674f757a2463eba-Paper.pdf)
7. **Vokinger KN, Feuerriegel S, Kesselheim AS.** Mitigating bias in machine learning for medicine. *Commun Med.* 2021;1:25. [doi:10.1038/s43856-021-00028-w](https://doi.org/10.1038/s43856-021-00028-w)

## Exercises

1. **Pick a published medical-imaging model paper.** Fill in the TRIPOD+AI checklist against it. Score each item present / missing. Where are the gaps?
2. **Write a model card for the lesion-segmentation tutorial.** Use the template above; invent reasonable training-data demographics.
3. **Design a PCCP for a quarterly-retrained age-prediction model.** What changes do you pre-declare? What halt conditions trigger re-submission?

??? success "Solutions"
    1. Most published models miss external validation, calibration, fairness stratification, and open-source release. Itemise these.
    2. Cover: intended use, training data, evaluation, limitations, ethical considerations, citation. ~1 page.
    3. Pre-declare: data sources expanded with cohort approval; retraining protocol = held-out site evaluation; halt if Dice or HD95 drop > 5% on any cleared subgroup.

## Where to next

That closes the AI/ML section. From here, [Data engineering → MLOps overlap](../data-engineering/advanced/mlops.md) is the infrastructure side of getting a model into production safely.
