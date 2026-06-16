# Interview preparation

> System-design template, five walkthroughs, SQL whiteboard patterns, behavioural (STAR), take-homes.

## The system-design template

1. **Clarify requirements** — functional + non-functional.
2. **Estimate scale** — QPS, payload size, total data.
3. **High-level architecture** — boxes and arrows.
4. **Component deep-dive** — pick hardest box.
5. **Failure modes** — when each component fails.
6. **Trade-offs** — name the consistency / availability / cost decisions.
7. **Open questions** — what you'd validate.

The template signals seniority.

## Five DE walkthroughs

### Spotify-style listening-events

100 M MAU × 30 plays/day = 3 B events/day. Clients buffer + retry → Kafka partitioned by user_id → Flink for real-time top-tracks; batch for nightly aggregates → BigQuery + ClickHouse.

### E-commerce CDC

OLTP Postgres → Debezium → Kafka → Snowflake. Outbox for transactional consistency. dbt models staging → marts. Schema registry + dbt contracts.

### Fraud-detection feature store

Online: Redis, p95 < 5 ms. Offline: BigQuery for training, point-in-time joins. Feast across both. Training-serving skew tests in CI.

### IoT temperature-sensor dashboards

Millions of devices → MQTT → Kafka. ClickHouse / Druid for sub-second dashboards. Cold storage: Parquet on S3 partitioned by device + day. Flink CEP for alerts.

### Multi-tenant SaaS warehouse

Per-tenant logical isolation via Snowflake roles + row-access policies. Bronze → silver → gold per tenant. dbt project per tenant or single project with macros. Cost attribution per tenant via tagged warehouses.

## SQL whiteboard patterns

Practice from memory:

- Top-N per group: `ROW_NUMBER() OVER (PARTITION BY ... ORDER BY ...)`.
- Running total: `SUM(...) OVER (PARTITION BY ... ORDER BY ... ROWS UNBOUNDED PRECEDING)`.
- Find duplicates: `GROUP BY ... HAVING COUNT(*) > 1`.
- Pivot: `MAX(CASE WHEN cat = 'X' THEN val END)`.
- Gaps and islands: window-function streak detection.

## Behavioural (STAR)

- **S — Situation** — context in 1-2 sentences.
- **T — Task** — what you needed to do.
- **A — Action** — what *you* did (not "we did").
- **R — Result** — measurable outcome.

Prep 6-8 stories covering: leadership, conflict, failure-and-learning, scaling something, decision under uncertainty, mentoring, cross-team negotiation.

## Take-home patterns

Common scoring: clean clone runs; readable code; edge cases handled or noted; good README; at least one test. The README is the single most under-invested artifact — spend disproportionate time on it.

## References

1. **Xu A.** *System Design Interview – An Insider's Guide.* Self-published; 2020. ISBN 978-1736049129.
2. **Karumanchi N.** *Data Engineering Interview Bible.* 2nd ed; 2022.

## Where to next

That closes the Advanced section. Loop back to [Portfolio roadmap](../portfolio-roadmap.md) and pick the next milestone for your repo.
