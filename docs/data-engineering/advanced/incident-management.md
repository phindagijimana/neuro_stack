# Incident management and postmortems

> Severity levels, roles, blameless postmortem template, RCA, on-call hygiene.

## Severity levels (typical)

| Sev | Definition | Response |
|---|---|---|
| **Sev 1** | Customer-facing outage / data loss | Page; war room; drop other work |
| **Sev 2** | Major degradation; workaround exists | Page in business hours |
| **Sev 3** | Bug or partial feature broken | Ticket; sprint |
| **Sev 4** | Cosmetic | Backlog |

Define cutoffs in advance.

## Roles during an incident

- **Incident commander (IC)** — owns response.
- **Comms lead** — updates stakeholders. Frees IC.
- **Investigator(s)** — figure out the cause.
- **Scribe** — writes everything in the channel.

Small teams: one person plays multiple roles for Sev 3. Sev 1 needs roles split.

## The blameless postmortem template

```markdown
# Postmortem: <short title>
**Status:** draft / in review / published
**Date:** YYYY-MM-DD
**Authors:** ...
**Severity:** Sev N
**Duration:** start → end (X minutes)

## Summary
## Impact
## Root cause
## Timeline
## What went well
## What went poorly
## Action items
- [ ] <owner> <due> add monitoring for X
- [ ] <owner> <due> write runbook for Y
```

Template enforces structure; blameless culture enforces honesty.

## Root cause analysis techniques

- **5 Whys.** Drive past symptoms.
- **Fishbone (Ishikawa).** Group causes by category.
- **Causal chain.** Multiple contributing causes — usually the right framing.

## On-call hygiene

- **Page only on user-impacting issues.**
- **Rotate.** Avoid burnout.
- **Compensate.** Pay or time-off.
- **Handover documents** between shifts.
- **Game-days** monthly.

## References

1. **Beyer B, Jones C, Petoff J, Murphy NR (eds).** *Site Reliability Engineering.* Free online: [https://sre.google/sre-book/](https://sre.google/sre-book/).
2. **Allspaw J, Robbins J.** *Web Operations.* O'Reilly; 2010.
3. **Murphy N, Wong C.** *The Site Reliability Workbook.* Free online: [https://sre.google/workbook/](https://sre.google/workbook/).

## Where to next

[Versioning everything](versioning.md).
