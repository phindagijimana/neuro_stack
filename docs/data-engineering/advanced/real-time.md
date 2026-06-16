# Real-time analytics

> When you actually need it; the serving-tier zoo; Lambda vs Kappa; a live cohort dashboard.

## When you actually need real-time

- **Operational decisions** on live data (fraud, anomaly alerts).
- **User-facing analytics** where 2-h delay is unusable.
- **Pipeline observability** (catch broken runs before morning).

For most neuroimaging research, *near-real-time* (minutes to hours) is plenty.

## The serving-tier zoo

| Engine | Strength |
|---|---|
| [**ClickHouse**](https://clickhouse.com/docs) | Columnar OLAP; fastest sub-second analytical queries |
| [**Apache Druid**](https://druid.apache.org) | Time-series + dimensional drill-down |
| [**Apache Pinot**](https://pinot.apache.org) | Real-time + batch; LinkedIn / Uber scale |
| **Snowflake / BigQuery** | Sub-second on small results; not for HTTP traffic |
| **TimescaleDB** | Postgres-flavoured time series |

If you need < 100 ms p95 at thousands of QPS → ClickHouse / Druid / Pinot. If 1-2 s warehouse query is fine → Snowflake / BigQuery + caching.

## Lambda vs Kappa

**Lambda** runs two parallel pipelines: batch (accurate, slow) + speed (approximate, fast) + serving layer queries both.

**Kappa** is "just use streaming for everything"; rewind and replay to reprocess. Modern infrastructure (Kafka with long retention, Flink replay) makes this practical. Most new systems pick Kappa.

## Worked example — live cohort dashboard

```text
each subject finishes
   → write manifest.json to S3
   → Lambda + EventBridge: parse, upsert into ClickHouse
   → Grafana queries ClickHouse on dashboard render
```

Answers "of the 76 subjects in this cohort, how many have finished QSIPrep / FreeSurfer / connectome, and what's the p95 runtime per stage?" — updated within seconds of each subject completing.

## References

1. **Marz N, Warren J.** *Big Data: Principles and Best Practices of Scalable Realtime Data Systems.* Manning; 2015. ISBN 978-1617290343.
2. **Kreps J.** Questioning the Lambda Architecture. *O'Reilly Radar.* 2014.
3. **Yang F, et al.** Druid: a real-time analytical data store. *SIGMOD.* 2014. [doi:10.1145/2588555.2595631](https://doi.org/10.1145/2588555.2595631)

## Where to next

[Ingestion patterns](ingestion.md).
