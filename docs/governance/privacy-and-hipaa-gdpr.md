# Privacy: HIPAA, GDPR, and de-identification

> The 18 identifiers, defacing pipelines and what they break, GDPR lawful basis, the brain-as-fingerprint problem, and why differential privacy hasn't solved imaging.

Ethics approval is necessary but not sufficient. Privacy law sits on top, and it has teeth: regulators fine, sponsors withdraw, and re-identification incidents end careers. This page is the working knowledge a neuroimaging engineer needs in the US and EU.

For the infrastructure-level controls (encryption, IAM, secrets), see [data engineering → security](../data-engineering/advanced/security.md). This page is the regulatory layer above that, plus the imaging-specific bit nobody else covers: defacing.

## HIPAA — the basics

The Health Insurance Portability and Accountability Act of 1996, plus the Privacy Rule (2003), Security Rule (2005), Breach Notification Rule (2009), and Omnibus Rule (2013). Applies to **covered entities** (providers, plans, clearinghouses) and **business associates** (anyone handling PHI on a covered entity's behalf).

For a researcher:

- If your institution is a covered entity (most US academic medical centres are), data acquired in the course of clinical care arrives to you as **Protected Health Information (PHI)**.
- PHI may be used for research only under (a) authorization, (b) waiver granted by the IRB, or (c) a Limited Data Set with a Data Use Agreement.
- You may de-identify PHI; once de-identified per the Privacy Rule, it's no longer PHI and HIPAA doesn't constrain it.

**De-identification** under the Privacy Rule has two routes:

| Route | What | When to use |
|---|---|---|
| **Safe Harbor** | Strip all 18 enumerated identifiers and have no actual knowledge of residual re-id risk | Default. Most research uses this. |
| **Expert Determination** | A qualified statistician certifies risk of re-id is "very small" given the data and disclosure context | When you need to retain something Safe Harbor would strip (dates, geographic detail) |

## The 18 HIPAA identifiers

Memorise these. They appear in every audit:

1. Names
2. Geographic subdivisions smaller than a state (street, city, county, ZIP — except first three digits of ZIP for areas > 20,000 people)
3. Dates (except year) — birth date, admission, discharge, death — and all ages over 89
4. Telephone numbers
5. Fax numbers
6. Email addresses
7. Social Security numbers
8. Medical record numbers
9. Health-plan beneficiary numbers
10. Account numbers
11. Certificate / license numbers
12. Vehicle identifiers
13. Device identifiers and serial numbers
14. URLs
15. IP addresses
16. Biometric identifiers (fingerprints, voice prints)
17. **Full-face photographs and any comparable images**
18. Any other unique identifying number, characteristic, or code

Identifier 17 is the imaging gotcha. **A 3D head MRI with the face intact is comparable to a full-face photograph** — face-recognition algorithms can match a de-faced MRI to a social-media photo with high accuracy. This is why defacing exists.

## Defacing — the imaging-specific de-identification

The standard tools:

| Tool | Approach | Notes |
|---|---|---|
| **PyDeface** ([Gulban 2019](https://doi.org/10.5281/zenodo.3524401)) | Registers a face mask in MNI space to the input, applies the mask | The de-facto default. Conservative; sometimes clips frontal cortex on small heads |
| **mri_deface** (FreeSurfer) | Atlas-based facial-feature removal | Bundled with FreeSurfer. Older. |
| **mri_reface** ([Schwarz 2021](https://doi.org/10.1016/j.neuroimage.2021.117845)) | Replaces face features with an average face rather than removing them | Preserves orbits and frontal cortex. Reduces downstream-analysis damage. |
| **AFNI `@afni_refacer_run`** | Replaces face with a template | AFNI users. Similar idea to mri_reface. |
| **fsl_deface** (FSL) | Registration-based deface | FSL users. |

### Where defacing breaks downstream analysis

Defacing is not free:

- **Cortical-surface reconstruction near the orbit.** FreeSurfer's `recon-all` uses face landmarks for initial registration; aggressive defacing can corrupt the frontal-lobe surface.
- **Brain-extraction with whole-head FOV models.** Some skull-stripping networks are trained on intact-face data; the missing face is out-of-distribution.
- **Registration to a face-bearing atlas.** Mutual information drops near the orbit.
- **fMRI normalisation pipelines** that rely on T1 anatomical priors can suffer correlated downstream errors.
- **Multi-modal alignment** (MRI to PET, MRI to CT) loses anchor points.

Practical default: use `mri_reface` if you need to keep the cortical surfaces clean, `pydeface` if you only need volumetric / subcortical analyses. Always run your standard pipeline once with and once without defacing on a small subset to characterise the bias.

The MRI Reface paper ([Schwarz 2021](https://doi.org/10.1016/j.neuroimage.2021.117845)) measures this directly and is worth reading before you commit to a defacing choice for a large cohort.

## GDPR — the basics

The General Data Protection Regulation (Regulation 2016/679) applies to processing personal data of people in the EU and EEA, regardless of where the processor is. It is the world's most influential privacy regulation; it has teeth (4% of global turnover or €20M, whichever is greater) and a strong extraterritorial reach.

Core concepts:

- **Personal data** — any information relating to an identified or identifiable natural person. Brain imaging is personal data.
- **Special category data** (Article 9) — includes **data concerning health**, **genetic data**, **biometric data for unique identification**. Brain imaging is special category. Processing requires both a lawful basis (Article 6) *and* a special-category condition (Article 9).
- **Lawful basis** — most commonly for research: explicit consent (Art 6(1)(a) + Art 9(2)(a)) or scientific research with Member-State derogation (Art 9(2)(j)).
- **DPIA** (Data Protection Impact Assessment) — required where processing is "likely to result in a high risk". Large-scale imaging cohorts almost always require one.
- **DPO** (Data Protection Officer) — required for public bodies, large-scale special-category processing. Your institution will have one; involve them early.

Data-subject rights (Articles 12-22): access, rectification, erasure ("right to be forgotten"), restriction, portability, objection, and rights related to automated decision-making.

For research, **erasure** is the hardest. Once a brain scan is in a trained model, can you really remove it? GDPR Article 17(3)(d) provides a research exemption when erasure would seriously impair the research, but it doesn't apply universally. Bake erasure semantics into your data plan.

### Pseudonymisation vs anonymisation

This is the semantic GDPR / HIPAA mismatch that trips up Americans:

| Term | GDPR | HIPAA |
|---|---|---|
| **Anonymisation** | Truly irreversible; not personal data; GDPR no longer applies | Equivalent to "de-identification" |
| **Pseudonymisation** | Reversible with a separately-held key; still personal data; GDPR still applies | Roughly equivalent to "coded" data |
| **De-identification** | Not a defined term; used colloquially | Statutory definition (Safe Harbor / Expert Determination) |

Under GDPR, pseudonymised data is still personal data. Under HIPAA, de-identified data is no longer PHI. A US researcher who says "this dataset is de-identified" is often, under GDPR, sharing pseudonymised data — and the EU regulator treats that as personal data.

## Re-identification risks

The "but we de-identified it" defence has been eroded by a series of demonstrations. The two you should cite:

- **Brain connectomes are fingerprints.** Finn et al. ([2015](https://doi.org/10.1038/nn.4135)) showed that an individual's functional connectome reliably identifies them across sessions — 80%+ matching accuracy in a cohort of 126. This is a **biometric identifier** in the sense of HIPAA identifier #16.
- **3D face reconstruction from de-identified MRI.** Schwarz et al. ([2019](https://doi.org/10.1056/NEJMc1908881)) reconstructed recognisable faces from research-grade structural MRI and matched them to social-media photos with 70% accuracy. This is the empirical basis of identifier #17.

Other documented attack surfaces:

- **Genetic data co-released with imaging** — even a few SNPs are highly identifying.
- **Cohort metadata** — rare diseases, rare ages, rare combinations.
- **Linkage attacks** — combining a "de-identified" dataset with a public dataset to re-id.

Sweeney's classic result ([2002](https://doi.org/10.1142/S0218488502001648)) is the conceptual basis: 87% of the US population is uniquely identifiable by ZIP + birth-date + sex. Imaging cohorts often have all three after a sloppy Safe Harbor pass.

## De-identification failure cases — when scrubbing isn't enough

Safe Harbor + defacing is the floor, not the ceiling. The literature now documents at least five distinct ways a "de-identified" structural or functional MRI cohort can be re-identified or attacked. A specialist threat model treats each of them.

### Brain shape as fingerprint

The structural and functional architecture of an individual brain is itself a biometric. The functional connectome result of Finn et al. ([2015](https://doi.org/10.1038/nn.4135)) — 80%+ identification accuracy across sessions in a 126-subject cohort, with frontoparietal connections carrying most of the signal — was followed by Wachinger's **BrainPrint** ([2015](https://doi.org/10.1016/j.neuroimage.2015.06.025)), which uses Laplace-Beltrami spectral shape descriptors of cortical and subcortical surfaces and achieves >99% subject identification on ADNI and OASIS. Neither attack requires the face — Safe-Harbor scrubbing and aggressive defacing leave the surface-based features fully intact. The implication: identifier #16 ("biometric identifiers") is implicit in any high-resolution T1w volume, regardless of identifier #17 (face).

### Face reconstruction from "de-identified" MRI

Schwarz et al. ([2019](https://doi.org/10.1056/NEJMc1908881)) reconstructed recognisable 3D face renderings from research-grade T1w volumes and matched them against social-media photos with 70–83% accuracy depending on the defacing aggressiveness. The result quantified what privacy lawyers had assumed: an intact face on a 1 mm isotropic T1w is comparable to a full-face photograph (identifier #17). Modern defacing — [PyDeface](https://doi.org/10.5281/zenodo.3524401), [mri_deface](https://surfer.nmr.mgh.harvard.edu/), and the face-replacement [mri_reface](https://doi.org/10.1016/j.neuroimage.2021.117845) — closes most of the gap, but not all of it: "permissive" defacing that preserves the nose, orbital ridge, or ear cartilage to spare downstream pipelines is exactly what made the Schwarz attack so effective. The trade-off is real — aggressive defacing damages frontal-lobe cortical-surface reconstruction, orbital segmentation, and multi-modal MRI / PET / CT alignment — but the cost of preserving anatomy near the face is a residual re-identification surface.

### Diffusion fingerprinting

The fingerprinting problem extends beyond grey matter. Sarwate and colleagues ([Sarwate 2014](https://doi.org/10.3389/fninf.2014.00024) and the connectome-fingerprinting follow-ons) showed that diffusion-derived white-matter tract signatures — fibre orientations, tract volumes, connectivity matrices — are individually distinctive at high enough resolution. Shared diffusion derivatives are not as obviously biometric as a face, but they are not anonymous either, particularly when combined with cohort metadata.

### Membership-inference attacks on models

When you publish a model trained on a private cohort, you publish a function of the training data. Shokri et al. ([2017](https://doi.org/10.1109/SP.2017.41)) demonstrated **membership inference**: an adversary with black-box access to the model can determine, with non-trivial accuracy, whether a given record was in the training set. For a clinical imaging model trained on, say, a rare-disease cohort, a positive membership inference is itself a diagnosis. The attack succeeds best when models overfit; the imaging-AI norm of small-sample fine-tuning on rare diagnoses is exactly the regime where membership inference is most dangerous.

### Linkage attacks

The classical re-identification mode. Imaging metadata that survives a Safe-Harbor pass — site, scanner, acquisition date truncated to year, sex, age band, broad diagnosis — is often enough to single out a subject when joined against a public phenotype database. UK Biobank participant-ID leaks and the recurring "we matched the de-identified MRI cohort against the public genome cohort" demonstrations are the canonical examples. The defence is *contextual integrity*: control the metadata you release alongside the imaging, not just the imaging itself.

### The mitigation hierarchy

There is no single fix; defence in depth is the only honest answer.

| Layer | Tool / practice | What it buys you |
| --- | --- | --- |
| **Aggressive defacing** | [PyDeface](https://doi.org/10.5281/zenodo.3524401), [mri_reface](https://doi.org/10.1016/j.neuroimage.2021.117845), AFNI `@afni_refacer_run` | Closes identifier #17; preserves downstream usability if you pick the right one |
| **Metadata scrubbing** | `dcm2niix -ba y`, dedicated DICOM scrubbers, private-tag review, burnt-in-pixel check | Closes Safe Harbor identifiers and vendor leaks |
| **Resolution reduction** | Downsample to 2-3 mm where the science permits | Reduces surface-based fingerprinting fidelity |
| **DP training** | [DP-SGD](https://doi.org/10.1145/2976749.2978318) with calibrated $\epsilon$ | Bounds membership inference on the trained model |
| **Federated learning** | Keep raw data in-institution; share gradients / updates | Avoids the export-then-defend problem entirely |
| **Controlled access** | Controlled tier on [OpenNeuro](https://openneuro.org/), [NDA](https://nda.nih.gov/), [LONI IDA](https://ida.loni.usc.edu/) | Adds DUA + audit log on top of all of the above |

### The honest disclaimer

100% de-identification does not exist for high-resolution structural MRI. The Safe Harbor list is necessary; defacing is necessary; metadata hygiene is necessary; none of them are sufficient. Treat IRB authorisation, DUAs, and controlled-access repositories as the legal backstop that does the work technique cannot. A privacy-engineering plan for an imaging cohort that promises "fully anonymous" data is a plan that has not read the literature.

## Differential privacy — the short story

**Differential privacy** ([Dwork 2006](https://doi.org/10.1007/11787006_1)) is the gold-standard mathematical privacy guarantee. A mechanism is $(\epsilon, \delta)$-differentially private if for any two datasets differing in one record, the output distribution changes by at most a factor of $e^\epsilon$ plus $\delta$. Smaller $\epsilon$ = stronger privacy = more noise.

It's mature for statistical-database queries (the US Census uses it). For medical imaging it sits in an awkward gap:

- The unit of privacy is the **individual subject**, but each subject contributes a high-dimensional volume. Adding meaningful noise destroys the signal that makes the volume useful.
- DP-SGD ([Abadi 2016](https://doi.org/10.1145/2976749.2978318)) trains models with per-sample gradient clipping and Gaussian noise. It works in principle. In practice, the $\epsilon$ values that publish well in CS papers ($\epsilon < 1$) catastrophically degrade clinical metrics, and the $\epsilon$ values that preserve clinical performance ($\epsilon = 10$+) provide weak guarantees.
- The **imaging community has not converged on an $\epsilon$ that's both safe and useful** for diagnostic models. Treat DP as a defence-in-depth, not as a substitute for access control and DUAs.

See the [federated learning chapter](federated-and-privacy-preserving.md) for DP applied to distributed training.

## International transfers — Schrems II and SCCs

Moving personal data from the EU to the US (or anywhere outside the EEA) is heavily regulated. The **Schrems II** ruling ([CJEU C-311/18, 2020](https://curia.europa.eu/juris/document/document.jsf?docid=228677)) invalidated the previous EU-US Privacy Shield and tightened standard contractual clauses (SCCs). For an EU-US imaging collaboration today, you need:

- **Standard Contractual Clauses** (the 2021 versions) between the EU exporter and the US importer.
- A **transfer impact assessment** (TIA) documenting that the destination jurisdiction's law doesn't undermine the SCCs.
- Often, **supplementary measures** — strong encryption, key custody in the EU, or pseudonymisation before export.
- The **EU-US Data Privacy Framework** ([2023](https://commission.europa.eu/law/law-topic/data-protection/international-dimension-data-protection/eu-us-data-transfers_en)) provides a self-certification route for US recipients. Federated approaches (data stays in the EU) avoid the transfer-rule problem entirely; see the [federated chapter](federated-and-privacy-preserving.md).

UK transfers post-Brexit use the **UK International Data Transfer Agreement** or the UK addendum to the EU SCCs.

## Pre-share checklist

Before any dataset leaves your institution:

- [ ] IRB (or equivalent) authorises the release for the stated purpose.
- [ ] Safe Harbor pass run; identifiers stripped; spot-check on a sample.
- [ ] Defacing applied; sample inspected for residual identifying features and for analysis damage.
- [ ] DICOM private tags reviewed (vendor-specific tags often leak PHI).
- [ ] Burnt-in pixel data checked (some scanners burn patient name into images).
- [ ] Subject IDs are new (not MRN, not initials, not a deterministic hash of MRN).
- [ ] Key map is stored separately under access control.
- [ ] DUA in place with the recipient (see [data sharing chapter](data-sharing-and-dua.md)).
- [ ] For EU data: transfer mechanism (SCCs / adequacy decision / DPF) documented.
- [ ] Receiving repository's access tier matches the sensitivity (open / registered / controlled).
- [ ] Audit log enabled on the source bucket.

## Practical defaults

For most US academic neuroimaging projects:

- Run `dcm2niix -ba y` (anonymise BIDS sidecars).
- Run `pydeface` or `mri_reface` depending on downstream pipeline tolerance.
- Use random, non-deterministic subject IDs (`uuid4`).
- Keep the MRN → subject_id map encrypted on an internal server; do not co-release.
- Release on OpenNeuro for open data, NDA / IDA for controlled data.

For EU projects, add:

- DPIA documented before processing starts.
- DPO involved at protocol design.
- Lawful basis explicit in the consent form.
- Transfer mechanism documented if any collaborator is outside the EEA.

## Where to next

- [Federated and privacy-preserving ML](federated-and-privacy-preserving.md) — what you do when the data can't be shared at all.
- [Data sharing and DUAs](data-sharing-and-dua.md) — the contracts that govern release.
- [Data engineering → security](../data-engineering/advanced/security.md) — the infrastructure controls underneath.

## References

1. **US Department of Health and Human Services.** HIPAA Privacy Rule — De-identification Standard (45 CFR 164.514). [https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/index.html)
2. **European Parliament and Council.** Regulation (EU) 2016/679 (GDPR). [https://gdpr-info.eu/](https://gdpr-info.eu/)
3. **Schwarz CG, Kremers WK, Therneau TM, et al.** Identification of anonymous MRI research participants with face-recognition software. *N Engl J Med.* 2019;381(17):1684-1686. [doi:10.1056/NEJMc1908881](https://doi.org/10.1056/NEJMc1908881)
4. **Schwarz CG, Kremers WK, Wiste HJ, et al.** Changing the face of neuroimaging research: comparing a new MRI de-facing technique with popular alternatives. *NeuroImage.* 2021;231:117845. [doi:10.1016/j.neuroimage.2021.117845](https://doi.org/10.1016/j.neuroimage.2021.117845)
5. **Finn ES, Shen X, Scheinost D, et al.** Functional connectome fingerprinting: identifying individuals using patterns of brain connectivity. *Nat Neurosci.* 2015;18(11):1664-1671. [doi:10.1038/nn.4135](https://doi.org/10.1038/nn.4135)
6. **Sweeney L.** k-anonymity: a model for protecting privacy. *Int J Uncertain Fuzziness Knowl-Based Syst.* 2002;10(5):557-570. [doi:10.1142/S0218488502001648](https://doi.org/10.1142/S0218488502001648)
7. **Dwork C.** Differential privacy. *ICALP.* 2006. [doi:10.1007/11787006_1](https://doi.org/10.1007/11787006_1)
8. **Abadi M, Chu A, Goodfellow I, et al.** Deep learning with differential privacy. *ACM CCS.* 2016. [doi:10.1145/2976749.2978318](https://doi.org/10.1145/2976749.2978318)
9. **Gulban OF, Nielson D, Poldrack R, et al.** poldracklab/pydeface. *Zenodo.* 2019. [doi:10.5281/zenodo.3524401](https://doi.org/10.5281/zenodo.3524401)
10. **Court of Justice of the European Union.** Schrems II (Case C-311/18). 2020. [https://curia.europa.eu/juris/document/document.jsf?docid=228677](https://curia.europa.eu/juris/document/document.jsf?docid=228677)
11. **Wachinger C, Golland P, Kremen W, et al.** BrainPrint: a discriminative characterization of brain morphology. *NeuroImage.* 2015;109:232-248. [doi:10.1016/j.neuroimage.2015.06.025](https://doi.org/10.1016/j.neuroimage.2015.06.025)
12. **Sarwate AD, Plis SM, Turner JA, et al.** Sharing privacy-sensitive access to neuroimaging and genetics data: a review and preliminary validation. *Front Neuroinform.* 2014;8:35. [doi:10.3389/fninf.2014.00024](https://doi.org/10.3389/fninf.2014.00024)
13. **Shokri R, Stronati M, Song C, Shmatikov V.** Membership inference attacks against machine learning models. *IEEE S&P.* 2017. [doi:10.1109/SP.2017.41](https://doi.org/10.1109/SP.2017.41)
