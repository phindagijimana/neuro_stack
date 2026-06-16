# Networking essentials

> Cloud networking stack, the cost trap, latency budgets, DNS pitfalls.

## The cloud networking stack (AWS-flavoured)

```text
Region
└── VPC (your virtual network, /16)
    ├── AZ A
    │   ├── public subnet  (/24, IGW route)
    │   └── private subnet (/24, NAT route)
    ├── AZ B
    │   └── ...
    ├── Internet Gateway
    ├── NAT Gateway / Instance
    ├── Security Groups (stateful, instance-level)
    └── Network ACLs (stateless, subnet-level)
```

Same model in GCP (VPC + subnets + firewall) and Azure (VNet + subnets + NSGs). AWS [networking foundations](https://docs.aws.amazon.com/whitepapers/latest/aws-vpc-connectivity-options/introduction.html).

## The cost trap

| Path | Cost |
|---|---|
| Same AZ | free |
| Cross-AZ same region | ~$0.01–0.02 / GB |
| Cross-region | ~$0.02–0.05 / GB |
| Internet egress | ~$0.05–0.09 / GB |

Implications: keep Spark + S3 in the same region; use VPC endpoints / PrivateLink; export from cloud-to-lab can be seven figures/year at neuroimaging scale.

## Latency budgets

| Hop | Typical |
|---|---|
| Same VM, in-memory | 0.1 μs |
| Same VM, NVMe | 100 μs |
| Same AZ, network | 0.5 ms |
| Cross-AZ | 1–2 ms |
| Cross-region (US-east → US-west) | 70 ms |
| Cross-ocean | 150–200 ms |
| Cold S3 GET | 10–50 ms |

User-facing: ~200 ms budget. ML inference: ~100 ms. Distribute across hops.

## DNS pitfalls

- **TTL too high** — failover takes hours. ≤ 60 s for user-facing.
- **TTL too low** — resolver load + bills. Don't go below 10 s.
- **Private DNS in cloud** — Route 53 / Cloud DNS private zones for internal names.
- **Kubernetes CoreDNS** caching can mask outages; tune.

## References

1. **Tanenbaum AS, Wetherall DJ.** *Computer Networks.* 5th ed. Pearson; 2010. ISBN 978-0132126953.
2. **AWS VPC User Guide.** [https://docs.aws.amazon.com/vpc/latest/userguide/](https://docs.aws.amazon.com/vpc/latest/userguide/)
3. **Grigorik I.** *High Performance Browser Networking.* Free: [https://hpbn.co](https://hpbn.co)

## Where to next

[Org-level data engineering](org.md).
