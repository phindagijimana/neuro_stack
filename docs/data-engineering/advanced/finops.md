# FinOps and cost engineering

> The five FinOps levers; showbacks vs chargebacks; cost of a 1000-subject DK rerun.

## The five FinOps levers

| Lever | Controls |
|---|---|
| **Right-sizing** | Instance type vs actual usage |
| **Spot / preemptible** | Trade availability for ~70% cut |
| **Reserved / committed** | Pre-commit for ~30–50% off |
| **Storage tiering** | Cold data to Glacier / Archive |
| **Data egress** | Keep compute near data |

[FinOps Foundation framework](https://www.finops.org/framework/) is the public reference.

## Showbacks vs chargebacks

- **Showback** — bill is shown per team but paid centrally.
- **Chargeback** — each team is billed and accountable.

Most orgs start with showback; move to chargeback when leadership wants accountability.

## Worked example — cost of a 1000-subject DK rerun

| Substrate | Per-subject | Cohort cost | Notes |
|---|---|---|---|
| HPC, included | "free" | "free" | Pre-paid; not really free |
| AWS Batch on-demand `c6i.4xlarge` | ~$2.40 (3 h) | ~$2,400 | Predictable |
| AWS Batch spot `c6i.4xlarge` | ~$0.72 (3 h) | ~$720 | Possible preemption |
| AWS Batch + FastSurfer GPU | ~$0.50 (10 min `g5.xlarge`) | ~$500 | Algorithm choice beats infra |

Cost is dominated by algorithm (`recon-all` vs FastSurfer), then by spot vs on-demand.

## Tools

- **AWS Cost Explorer / GCP Billing / Azure Cost Management** — first-party.
- **Vantage / CloudZero / Datadog Cost** — third-party, multi-cloud.
- **Kubecost / OpenCost** — Kubernetes-native.

## References

1. **Storment JR, Fuller M.** *Cloud FinOps.* 2nd ed. O'Reilly; 2023. ISBN 978-1492054634.
2. **FinOps Foundation Framework.** [https://www.finops.org/framework/](https://www.finops.org/framework/)

## Where to next

[Performance — queues, percentiles, skew](performance.md).
