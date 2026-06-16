# Catalogs, discovery, lineage

> The "we have 50 tables and nobody knows which is the right one" problem.

## The problem

A mid-sized org has thousands of tables, dashboards, ML features, and data products. A new analyst can spend a week asking "is `users_v2` or `dim_user` the right source?" Catalogs make discovery a documented capability.

## Catalog feature matrix

| Feature | Datahub | Atlan | Alation | OpenMetadata | Unity Catalog |
|---|---|---|---|---|---|
| Search across tables / dashboards / models | ✓ | ✓ | ✓ | ✓ | ✓ |
| Auto-pulled column descriptions from dbt | ✓ | ✓ | ✓ | ✓ | partial |
| Lineage across orchestrators | ✓ | ✓ | partial | ✓ | partial |
| Open source | ✓ | ✗ | ✗ | ✓ | partial |

[DataHub](https://datahubproject.io) and [OpenMetadata](https://docs.open-metadata.org) are the open-source defaults.

## OpenLineage

[OpenLineage](https://openlineage.io) is a vendor-neutral schema for emitting lineage events from orchestrators. Airflow, dbt, Spark, Flink all have integrations. Marquez is the reference backend.

```json
{
  "eventType": "COMPLETE",
  "eventTime": "2026-06-15T12:34:56Z",
  "job":      {"namespace": "neuro", "name": "dk_connectome"},
  "run":      {"runId": "abc-123"},
  "inputs":   [{"namespace": "s3://bids", "name": "sub-001"}],
  "outputs":  [{"namespace": "s3://derivatives", "name": "sub-001_dk_connectome.csv"}]
}
```

Every "what produced this table" becomes a graph query.

## Why this matters at senior level

A senior DE is judged on **time-to-insight** for the org. Catalog + lineage collapses that time by an order of magnitude. The single most leveraged investment after the warehouse itself.

## References

1. **OpenLineage Specification.** [https://openlineage.io](https://openlineage.io)
2. **DAMA-DMBOK** chapter on Metadata Management.

## Where to next

[Real-time analytics](real-time.md).
