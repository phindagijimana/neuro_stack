# dbt deeply

> SQL with version control, tests, lineage — why dbt eats the analytics world.

## Why dbt

Before dbt, analytics was a mix of stored procedures, Airflow operators, and undocumented dashboards. [dbt](https://docs.getdbt.com) collapses it into one pattern: every transformation is a SELECT in a versioned file; dbt compiles into the right `CREATE TABLE AS` for your warehouse.

## Project layout

```text
my_dbt_project/
├── dbt_project.yml
├── profiles.yml           # connection (~/.dbt, not committed)
├── models/
│   ├── staging/           # 1:1 with sources; rename, cast
│   ├── intermediate/      # joins, aggregations
│   └── marts/             # business-ready
├── seeds/                 # static CSVs
├── snapshots/             # SCD2
├── macros/                # reusable SQL helpers
└── tests/                 # custom tests
```

## Materializations

| Type | When | Cost |
|---|---|---|
| `view` | Cheap, transient transforms | None |
| `table` | Heavy transforms used by many | Full rebuild |
| `incremental` | Append-only or merge | Only new rows |
| `ephemeral` | Inlined as CTE | None |
| `materialized_view` | Engine-managed | Engine-managed refresh |

Pick `view` for staging, `table` for marts, `incremental` for facts that grow.

## Incremental strategies

```sql
{{ config(materialized='incremental', unique_key='manifest_id') }}

SELECT * FROM {{ source('raw', 'manifest') }}
{% if is_incremental() %}
  WHERE ingested_at > (SELECT MAX(ingested_at) FROM {{ this }})
{% endif %}
```

Strategies: `append`, `merge` (upsert), `delete+insert`, `insert_overwrite` (partition-level).

## Snapshots = SCD2 for free

```sql
{% snapshot subject_snapshot %}
{{ config(target_schema='snapshots', unique_key='subject_id',
          strategy='check', check_cols=['diagnosis', 'age_at_consent']) }}
SELECT * FROM {{ source('raw', 'subjects') }}
{% endsnapshot %}
```

dbt adds `dbt_valid_from` / `dbt_valid_to`. Run on schedule = full history.

## Tests

```yaml
models:
  - name: connectome
    columns:
      - name: subject_id
        tests:
          - not_null
          - relationships:
              to: ref('dim_subject')
              field: subject_id
      - name: edge_weight
        tests:
          - dbt_utils.accepted_range:
              min_value: 0
              max_value: 1e7
```

Add tests to every model. CI runs `dbt test` on every PR.

## Contracts (dbt 1.5+)

```yaml
- name: connectome
  config:
    contract:
      enforced: true
  columns:
    - name: subject_id
      data_type: text
      constraints:
        - type: not_null
```

Breaking schema changes fail at build time.

## Commands you'll type daily

```bash
dbt deps
dbt seed
dbt run
dbt test
dbt build                          # run + test in DAG order
dbt docs generate && dbt docs serve
```

## References

1. **dbt Documentation.** [https://docs.getdbt.com](https://docs.getdbt.com)
2. **Handel C.** *Analytics Engineering with dbt.* Packt; 2023. ISBN 978-1803246284.

## Where to next

[Data contracts and schema evolution](data-contracts.md).
