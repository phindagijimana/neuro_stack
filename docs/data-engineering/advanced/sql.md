# SQL beyond SELECT

> Query plans, join algorithms, window functions, CTEs, materialised views, indexes vs clustering.

## Query plans

Every engine compiles SQL into a plan. Postgres `EXPLAIN ANALYZE` docs [here](https://www.postgresql.org/docs/current/sql-explain.html); BigQuery, Snowflake, DuckDB have equivalents. Reading plans is what separates someone who writes SQL from someone who optimises it.

## Join algorithms — when each wins

| Join | Wins when | Cost |
|---|---|---|
| **Hash** | Equality, one side fits memory | Build hash on smaller side |
| **Merge** | Both inputs already sorted | `O(n + m)` after sort |
| **Nested loop** | Small outer, indexed inner | `O(n × log m)` |
| **Broadcast** | Tiny dim joined to huge fact | Ship dim to every worker |
| **Shuffle / partitioned** | Both huge | Network-heavy |

The optimiser picks based on statistics. Bad picks usually mean stale stats.

## Window functions — the senior-DE workhorse

```sql
SELECT
  subject_id,
  fd_mean,
  NTILE(4) OVER (ORDER BY fd_mean)              AS fd_quartile,
  AVG(fd_mean)  OVER (PARTITION BY scanner)     AS scanner_mean,
  ROW_NUMBER()  OVER (PARTITION BY subject_id
                      ORDER BY session_id)      AS session_rank
FROM fact_scan_qc;
```

A whole class of "self-join with `MAX(...)`" patterns disappear once you fluent at window functions. [Postgres window functions](https://www.postgresql.org/docs/current/tutorial-window.html) is the cleanest tutorial.

## CTEs vs subqueries

`WITH name AS (...)` names a subquery for reuse. Caveats:

- Some engines materialise CTEs (older Postgres / pre-2024 MySQL) — they block predicate pushdown.
- Recursive CTEs handle hierarchies.
- Don't nest more than 2 levels.

## Materialised views

A saved query + result, refreshed on schedule. Precompute `cohort_qc_summary` materialised view; refresh nightly. Queries are instant.

- Postgres: `CREATE MATERIALIZED VIEW`, `REFRESH ... CONCURRENTLY`.
- BigQuery / Snowflake: managed.

## Indexes vs clustering

- **Row-store B-tree** — `CREATE INDEX ON fact_scan_qc (subject_id)`. Costs writes.
- **Columnar clustering** — physical ordering; min/max stats prune. BigQuery clustering, Iceberg sort orders. Costs nothing on read.

## References

1. **Garcia-Molina H, Ullman JD, Widom J.** *Database Systems: The Complete Book.* 2nd ed. Pearson; 2008. ISBN 978-0131873254.
2. **Graefe G.** Query evaluation techniques for large databases. *ACM Comput Surv.* 1993;25(2):73-169. [doi:10.1145/152610.152611](https://doi.org/10.1145/152610.152611)

## Where to next

[Distributed systems](distributed-systems.md) — what happens when one machine isn't enough.
