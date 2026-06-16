# Backup, disaster recovery, RTO/RPO

> Define the terms, backup types, object-storage versioning, cross-region replication, restore drills.

## Define the terms

- **RTO — Recovery Time Objective.** How long until service is restored.
- **RPO — Recovery Point Objective.** How much data you can afford to lose.
- **BCP — Business Continuity Plan.** Broader procedural doc.
- **DR — Disaster Recovery.** Technical execution.

Research lab might accept RTO = 24 h, RPO = 1 h. Clinical = RTO 15 min, RPO 0.

## Backup types

| Type | What | Cost |
|---|---|---|
| **Full** | Everything | Slow, large |
| **Incremental** | Changes since last backup | Fast, small |
| **Differential** | Changes since last full | Medium |
| **Snapshot** | Point-in-time at storage layer | Instant |
| **Logical** (pg_dump, mongodump) | Portable | Slow for large DBs |
| **Physical** | Raw data files | Fast restore; engine-specific |

Common recipe: nightly logical dump + continuous WAL archiving + weekly snapshot.

## Object-storage versioning and immutable backups

- [**S3 Versioning**](https://docs.aws.amazon.com/AmazonS3/latest/userguide/Versioning.html) — every overwrite keeps the previous version.
- **Object Lock** — immutable, WORM. Defends against ransomware.
- **MFA Delete** — versioned-bucket deletes require MFA.

For BIDS datasets: S3 Versioning + Object Lock with 1-year retention = "did I just `rm -rf` my career" insurance.

## Cross-region replication

- **S3 CRR / GCS Multi-region** — auto-copy to another region.
- **RDS Multi-AZ** — synchronous replica in another AZ.
- **Cross-region read replicas** — async; lower RPO than backup-restore.

Trade-off: ~1× storage cost per region.

## Restore drills

The backup nobody has restored is not a backup. Drill on schedule:

1. Restore latest backup to non-prod environment.
2. Verify a known query returns expected results.
3. Time the restore; compare against RTO.
4. Write up the drill in a runbook.

## References

1. **NIST SP 800-34 Rev. 1.** Contingency Planning Guide. [link](https://csrc.nist.gov/publications/detail/sp/800-34/rev-1/final)
2. **AWS Disaster Recovery Whitepaper.** [link](https://docs.aws.amazon.com/whitepapers/latest/disaster-recovery-workloads-on-aws/disaster-recovery-workloads-on-aws.html)

## Where to next

[Incident management and postmortems](incident-management.md).
