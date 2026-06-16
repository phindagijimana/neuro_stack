# Security, governance, privacy

> Identity, encryption, secrets, PII / PHI, regulations.

## Identity & Access Management

- **Authentication** — who you are. OIDC / SAML from a corporate IdP.
- **Authorisation** — RBAC for coarse access, ABAC for fine-grained.
- **Audit** — every privileged action logged.

For cloud, use IAM roles, not access keys. AWS best practices [here](https://docs.aws.amazon.com/IAM/latest/UserGuide/best-practices.html).

## Encryption

- **At rest** — server-side encryption is table stakes; KMS-managed keys for compliance.
- **In transit** — TLS 1.2+ everywhere; mTLS between services for zero-trust.
- **Field-level** — encrypt specific columns (`name`, `MRN`) with a key your application controls.

## Secrets

Never commit secrets. Use AWS Secrets Manager, [HashiCorp Vault](https://developer.hashicorp.com/vault), or 1Password Connect. CI/CD via OIDC trust → no long-lived credentials.

## PII / PHI handling for neuroimaging

- **De-identify at ingest.** Strip patient name, MRN, accession, DOB from DICOM. `dcm2niix -ba y`. Spot-check.
- **Deface.** `pydeface`, `mri_deface`, AFNI `@afni_refacer_run`.
- **Coded re-identification.** Separate, access-controlled `MRN → subject_id` map.
- **Audit access** to PHI separately from derivatives.

## Regulations to know in name

| Reg | Region | DE-relevant clauses |
|---|---|---|
| **HIPAA** | US | BAAs, access logging, breach notification |
| **GDPR** | EU | Right to erasure, lawful basis, DPIA |
| **CCPA** | California | Opt-out |
| **21 CFR Part 11** | US, FDA | Audit trails, e-signatures |
| **NIH Data Sharing** | US federal grants | Data management plan, repository |

## References

1. **NIST SP 800-53.** Security and Privacy Controls. [https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final](https://csrc.nist.gov/publications/detail/sp/800-53/rev-5/final)
2. **HIPAA Security Rule.** [https://www.hhs.gov/hipaa/](https://www.hhs.gov/hipaa/)
3. **GDPR official text.** [https://gdpr-info.eu/](https://gdpr-info.eu/)

## Where to next

[Infrastructure as Code](iac.md).
