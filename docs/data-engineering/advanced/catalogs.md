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

## Worked example — emit OpenLineage from a Snakefile

Stand up a Marquez backend in one command, then have every Snakemake rule emit a START / COMPLETE event.

### 1. Stand up Marquez locally

```bash
git clone https://github.com/MarquezProject/marquez && cd marquez
./docker/up.sh                       # http://localhost:3000 (UI), :5000 (API)
```

### 2. Emit events from Snakemake

Add to your `Snakefile`:

```python
import requests, uuid, datetime

MARQUEZ = "http://localhost:5000/api/v1/lineage"

def emit(event_type, job, run_id, inputs=None, outputs=None):
    payload = {
        "eventType": event_type,
        "eventTime": datetime.datetime.utcnow().isoformat() + "Z",
        "producer":  "https://github.com/phindagijimana/neuro_stack",
        "job":       {"namespace": "neuro_stack.dwi", "name": job},
        "run":       {"runId": run_id},
        "inputs":    [{"namespace": "fs", "name": i} for i in (inputs or [])],
        "outputs":   [{"namespace": "fs", "name": o} for o in (outputs or [])],
    }
    requests.post(MARQUEZ, json=payload, timeout=5)

onsuccess:
    emit("COMPLETE", "cohort_pipeline", str(uuid.uuid4()))

onerror:
    emit("FAIL", "cohort_pipeline", str(uuid.uuid4()))
```

For per-rule lineage, wrap each rule's `shell:` block in a Python helper that calls `emit()` before and after.

### 3. Browse the lineage graph

Open <http://localhost:3000>. You'll see every job as a node, with inputs / outputs as edges. Time-travel: every run is recorded.

### 4. Wire it into CI

In production: replace `localhost:5000` with the Marquez endpoint your platform team runs. The same code works against any OpenLineage backend (DataHub, Astronomer, etc.).

That's the minimum lineage instrumentation. From here it's a small step to per-rule lineage, asset-level metadata, and a portfolio of pipelines all reporting into one catalog.

## Why this matters at senior level

A senior DE is judged on **time-to-insight** for the org. Catalog + lineage collapses that time by an order of magnitude. The single most leveraged investment after the warehouse itself.

## References

1. **OpenLineage Specification.** [https://openlineage.io](https://openlineage.io)
2. **DAMA-DMBOK** chapter on Metadata Management.

## Where to next

[Real-time analytics](real-time.md).
