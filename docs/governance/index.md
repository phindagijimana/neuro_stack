# Governance and ethics

> IRB, HIPAA, GDPR, consent, DUAs, and federated learning — the rules and recipes that decide whether your neuroimaging project actually ships, or sits in a drawer.

Most neuroimaging work is clinical-adjacent: the data was originally acquired on a patient, by a clinician, under a consent form, in a jurisdiction with a privacy regulator. Even a "pure research" cohort lives inside an ethics framework. This section pulls the governance topics that were previously scattered across the handbook into one place.

The framing here is operational. Not "what does GDPR Article 9 say" but "what do you have to do, in what order, before you can share a dataset on OpenNeuro". Not "what is the Belmont report" but "what will the IRB reviewer actually ask, and how do you answer".

## Section map

<div class="grid cards" markdown>

-   :material-account-group: **[IRB and research ethics](irb-and-ethics.md)** — Common Rule, exempt vs expedited vs full-board review, informed consent, broad consent, incidental-findings policies, Belmont and Helsinki.

-   :material-shield-lock: **[Privacy: HIPAA, GDPR, de-identification](privacy-and-hipaa-gdpr.md)** — the 18 HIPAA identifiers, defacing pipelines and the analyses they break, GDPR lawful basis and DPIAs, brain-as-fingerprint risks, differential privacy.

-   :material-server-network: **[Federated and privacy-preserving ML](federated-and-privacy-preserving.md)** — when the data can't move. FedAvg, FedProx, secure aggregation, DP-SGD, NVFlare / Flower / OpenFL, COINSTAC and ENIGMA, threat models.

-   :material-share-variant: **[Data sharing and DUAs](data-sharing-and-dua.md)** — NIH 2023 policy, FAIR, OpenNeuro / NDA / UK Biobank / ADNI, tiers of access, DUA clauses, the release checklist.

</div>

## Reading order

=== "Beginner"

    Goal: don't violate consent, don't leak PHI, and understand what an IRB is for.

    1. [IRB and research ethics](irb-and-ethics.md) — sections on consent and Common Rule basics.
    2. [Privacy: HIPAA, GDPR, de-identification](privacy-and-hipaa-gdpr.md) — the 18 identifiers, Safe Harbor, defacing.
    3. [Data sharing and DUAs](data-sharing-and-dua.md) — what tier of access your data falls under.

    Enough to be a useful junior on a clinical-imaging project without setting off the compliance office.

=== "Intermediate"

    Goal: write the consent form, the data-management plan, and the DUA for your own project.

    1. [IRB and research ethics](irb-and-ethics.md) end-to-end — including broad consent, re-consent, incidental findings.
    2. [Privacy](privacy-and-hipaa-gdpr.md) end-to-end — including Expert Determination, GDPR pseudonymisation, Schrems II.
    3. [Data sharing](data-sharing-and-dua.md) end-to-end — release a BIDS dataset on OpenNeuro using the checklist.
    4. Skim [Federated learning](federated-and-privacy-preserving.md) so you know when *not* to use it.

    You're the person on a project who can answer the compliance email without forwarding it.

=== "Advanced / specialist"

    Goal: lead governance for a multi-site consortium or a federated study.

    1. [Federated and privacy-preserving ML](federated-and-privacy-preserving.md) end-to-end — architectures, secure aggregation, DP-SGD, threat models, FUTURE-AI reporting.
    2. [Privacy](privacy-and-hipaa-gdpr.md) — re-identification literature, differential privacy limits in imaging.
    3. International transfers (Schrems II, SCCs) and the cross-border DUA in [Data sharing](data-sharing-and-dua.md).
    4. Pair with [AI/ML → Regulatory](../ai/regulatory.md) once a model goes near a clinical decision path.

## Adjacent chapters

- [AI/ML → Regulatory, reporting, clinical deployment](../ai/regulatory.md) — SaMD, TRIPOD+AI, CLAIM, model cards, FDA PCCP. Where governance meets product.
- [Data engineering → Security, governance, privacy](../data-engineering/advanced/security.md) — the infrastructure-side primer: IAM, encryption, secrets, de-identification at ingest.

These two pages are deliberately shorter. This section is where the *substance* lives — consent, ethics, privacy regulation, federated approaches, and data sharing. The other two are the surfaces.

## What this section is not

This is not legal advice. Your IRB, your DPO, your institution's privacy office, and (for clinical deployment) your regulatory affairs team are the authorities. This section gives you the vocabulary, the landscape, and a working set of defaults so the conversations with those authorities are productive rather than embarrassing.

## Where to next

Start with [IRB and research ethics](irb-and-ethics.md) — every other page in this section assumes you have an IRB-approved protocol.
