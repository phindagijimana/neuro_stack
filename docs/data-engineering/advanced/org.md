# Org-level data engineering

> Data Mesh, RFC culture, design docs, mentoring, OKRs.

## Data Mesh

[Zhamak Dehghani's Data Mesh](https://martinfowler.com/articles/data-monolith-to-mesh.html) reorganises by domain instead of by tool:

- **Domain-oriented ownership** — each domain owns its data products.
- **Data as a product** — domains treat consumers as customers.
- **Self-serve platform** — central team provides substrate.
- **Federated governance** — domain owners agree on cross-cutting standards.

Mesh works when the org is too big for a central data team. Below that threshold, centralisation is simpler.

## RFC culture

Any significant decision goes through an RFC reviewed by stakeholders.

```markdown
# RFC: <title>
**Status:** draft / accepted / superseded

## Context
## Proposal
## Alternatives considered
## Migration
## Open questions
```

Writing the RFC surfaces issues before you've spent two months building.

## Design docs (DD)

For implementation-level work, a design doc precedes coding.

```markdown
# Design Doc: <feature>
## Goal & Non-goals
## Background
## Proposed design
## API / Schema
## Failure modes
## Testing strategy
## Rollout plan
## Open questions
```

Reviewed in PRs.

## Mentoring as a force multiplier

A senior who helps three juniors get from L3 to L4 has had more org impact than one who shipped two solo projects. Patterns:

- Pair on hard debugging.
- Review every PR.
- Weekly office hour.
- Write the docs nobody else writes.

## OKRs / KRs

[Doerr's *Measure What Matters*](https://www.whatmatters.com) framing:

- **Objective** — qualitative, ambitious. ("Make the cohort QC dashboard trustworthy.")
- **Key Results** — quantitative. ("p95 dashboard freshness < 1 h"; "100% of subjects have a manifest"; "0 cluster-wide outages.")

KRs that are merely "did X" aren't KRs; they're tasks.

## References

1. **Dehghani Z.** *Data Mesh.* O'Reilly; 2022. ISBN 978-1492092391.
2. **Doerr J.** *Measure What Matters.* Portfolio; 2018. ISBN 978-0525536222.
3. **Kim G, Behr K, Spafford G.** *The Phoenix Project.* IT Revolution; 2013. ISBN 978-0988262508.

## Where to next

[Interview preparation](interviewing.md).
