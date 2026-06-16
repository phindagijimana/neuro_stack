# Apache Spark

> Mental model, narrow vs wide transforms, the shuffle, AQE, sizing executors, reading the Spark UI.

## Mental model

Spark is a lazy DAG engine: you describe transformations on DataFrames, Spark builds an optimised plan when you call an action. Docs [here](https://spark.apache.org/docs/latest/).

- **Logical plan** — what you asked for. Optimised by Catalyst.
- **Physical plan** — how Spark will execute it.

`df.explain(mode="extended")` shows both. Read it on every non-trivial job.

## Narrow vs wide transformations

| Type | Examples | Cost |
|---|---|---|
| **Narrow** | `select`, `filter`, `withColumn`, `union` | One partition out per partition in |
| **Wide** | `groupBy`, `join`, `distinct`, `orderBy` | Shuffle: data crosses the network |

Wide transformations are where time goes.

## The shuffle and how to minimise it

- **Broadcast joins.** If one side is < ~10 MB (`spark.sql.autoBroadcastJoinThreshold`), broadcast it. AQE does this dynamically.
- **Bucketing.** Pre-shuffle data into N buckets; subsequent joins on the bucket key avoid shuffling.
- **Partition pruning.** Filter on the partition column before joining.
- **Skew handling.** Salt the key (`key + rand(0, 10)`), aggregate, then re-aggregate.

## AQE — Adaptive Query Execution

Since 3.0, Spark re-plans the physical plan during execution:

- Dynamic broadcast switch when one side is actually small.
- Partition coalescing.
- Skew join split at runtime.

Enabled by default in 3.2+; verify `spark.sql.adaptive.enabled=true`.

## Worked example — cohort summary

```python
from pyspark.sql import functions as F

manifests = spark.read.parquet("s3://bucket/manifests/")
conn      = spark.read.parquet("s3://bucket/derivatives/connectome/")

cohort = (
    conn.alias("c")
        .join(F.broadcast(manifests.alias("m")), "subject_id", "left")
        .filter(F.col("m.success") == True)
        .groupBy("m.scanner", "c.source_region", "c.target_region")
        .agg(
            F.count("*").alias("n"),
            F.mean("c.edge_weight").alias("mean_weight"),
            F.stddev("c.edge_weight").alias("std_weight"),
        )
)
cohort.write.mode("overwrite").parquet("s3://bucket/derived/cohort_summary/")
```

## Sizing executors

- **Memory** — 8–16 GB.
- **Cores** — 4–5; more and S3 client contention bites.
- **Driver** — same range; bigger only if you `.collect()` (don't).
- **Dynamic allocation** — `spark.dynamicAllocation.enabled=true`.

## Reading the Spark UI

In order of importance:

1. **Jobs tab** — which stages take time.
2. **SQL tab** — physical plan with per-operator metrics.
3. **Stages tab** — task-level skew (p95/median ratio > 5 = problem).
4. **Storage tab** — what's cached.
5. **Environment tab** — sanity-check configs.

## References

1. **Zaharia M, Xin RS, Wendell P, et al.** Apache Spark: a unified engine for big data processing. *Commun ACM.* 2016;59(11):56-65. [doi:10.1145/2934664](https://doi.org/10.1145/2934664)
2. **Armbrust M, Xin RS, Lian C, et al.** Spark SQL. *SIGMOD.* 2015. [doi:10.1145/2723372.2742797](https://doi.org/10.1145/2723372.2742797)
3. **Karau H, Warren R.** *High Performance Spark.* O'Reilly; 2017. ISBN 978-1491943205.

## Where to next

[Streaming systems](streaming.md) — when batch isn't fast enough.
