# Advanced topics

> For when the basics aren't enough.

The chapters in the main [Data engineering](../index.md) section get you to a production-grade pipeline. This sub-section covers what comes after: the topics that distinguish a senior data engineer from a competent one.

These are deliberately broad — they're written so you'll recognise the territory in job posts and architecture discussions, and so you can dive deeper from a solid mental map. Every chapter ends with a DWI tie-in showing how the concept lands in a neuroimaging context.

## Map

| Chapter | What it's about |
| --- | --- |
| [Data modeling](data-modeling.md) | Star schemas, slowly-changing dimensions, normal forms, data vault — and when each pays off. |
| [Lakehouse internals](lakehouse.md) | Parquet, Iceberg, Delta, Hudi — how columnar formats actually work. |
| [SQL beyond SELECT](sql.md) | Query plans, join algorithms, window functions, CTEs, materialised views. |
| [Distributed systems](distributed-systems.md) | CAP, consistency models, idempotency keys, quorums, consensus. |
| [Spark](spark.md) | Mental model, narrow vs wide transforms, the shuffle, AQE, sizing executors. |
| [Streaming](streaming.md) | Kafka topology, watermarks, exactly-once, CDC patterns. |
| [dbt](dbt.md) | Materializations, incremental strategies, snapshots, tests, contracts. |
| [Data contracts](data-contracts.md) | Producer–consumer agreements, compatibility modes, schema registries. |
| [Security & governance](security.md) | IAM, encryption, PII/PHI, GDPR/HIPAA primer for engineers. |
| [Infrastructure as code](iac.md) | Terraform, Helm, GitOps. |
| [Cohort-scale pipelines](cohort-scale.md) | N=10k+ patterns — sharding, tiered derivative storage, long-job checkpointing, partial-results recovery, BWAS readiness. |
| [Performance deep-dive](performance.md) | Little's law, percentiles, hot keys, locality. |
| [Concurrency](concurrency.md) | ACID isolation levels, MVCC, locks, deadlocks, connection pools. |
| [Data quality](data-quality.md) | Six dimensions, circuit breakers, drift detection. |
| [Catalogs & lineage](catalogs.md) | OpenLineage, DataHub, Atlan, why this matters at senior level. |
| [Real-time analytics](real-time.md) | Lambda vs Kappa, the serving-tier zoo. |
| [Ingestion patterns](ingestion.md) | Batch, CDC, webhooks vs polling, connector platforms. |
| [Event-driven architectures](event-driven.md) | Event sourcing, CQRS, outbox, sagas, DLQs. |
| [MLOps overlap](mlops.md) | Feature stores, vector stores, training/serving skew. |
| [Disaster recovery](disaster-recovery.md) | RTO/RPO, backup types, restore drills. |
| [Incident management](incident-management.md) | Severities, roles, blameless postmortems, RCA. |
| [Versioning everything](versioning.md) | Code, data, models — semver for data products. |
| [Networking essentials](networking.md) | VPCs, the cost trap, latency budgets, DNS pitfalls. |
| [Org-level DE](org.md) | Data mesh, RFCs, design docs, mentoring, OKRs. |
| [Interview prep](interviewing.md) | System-design template, five worked walkthroughs, SQL patterns. |
