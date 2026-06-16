# Data modeling

> Star schemas, normal forms, slowly-changing dimensions, data vault — and when each pays off.

## Why model

Data modeling is the discipline of choosing how facts are represented, related, and updated. The choice you make at the model layer determines what's cheap and what's expensive for every query that follows.

- **No model** — everything in one giant denormalised table. Cheap to load, painful to evolve.
- **Over-modelled** — every column normalised into its own table. Pristine for inserts, catastrophic for analytics.

## Normal forms

For OLTP, classical normalisation (Codd's 3NF) is the right starting point: minimise redundancy, enforce one source of truth.

- **1NF** — atomic columns, no repeating groups.
- **2NF** — every non-key column depends on the whole primary key.
- **3NF** — no transitive dependencies.

For neuroimaging metadata (`participants.tsv`, `sessions.tsv`), 3NF works. For analytics, keep reading.

## The star schema

One central **fact** table surrounded by **dimension** tables. Kimball's [Data Warehouse Toolkit](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/books/data-warehouse-dw-toolkit/) is the canonical reference.

## Slowly-changing dimensions (SCD)

| Type | Behaviour | Use when |
|---|---|---|
| **SCD 1** | Overwrite | History doesn't matter |
| **SCD 2** | New row with `valid_from`/`valid_to` | History matters (default) |
| **SCD 3** | Add `previous_value` column | Only previous state matters |

dbt snapshots ([docs here](https://docs.getdbt.com/docs/build/snapshots)) implement SCD2 declaratively.

## Data vault

For multi-source enterprise warehouses, **Data Vault 2.0** splits modelling into **Hubs** (business keys), **Links** (relationships), **Satellites** (descriptive attributes). Heavyweight; rarely the right call for a single-lab neuroimaging warehouse — use a star.

## Worked example — DWI as a star schema

```sql
CREATE TABLE dim_subject (
  subject_key       SERIAL PRIMARY KEY,
  subject_id        TEXT,
  sex               TEXT,
  age_at_consent    NUMERIC,
  valid_from        TIMESTAMPTZ,
  valid_to          TIMESTAMPTZ
);

CREATE TABLE dim_region (
  region_key        SERIAL PRIMARY KEY,
  atlas             TEXT,
  region_label      TEXT,
  hemisphere        TEXT,
  lobe              TEXT
);

CREATE TABLE fact_connectome (
  subject_key       INT REFERENCES dim_subject(subject_key),
  session_key       INT,
  source_region_key INT REFERENCES dim_region(region_key),
  target_region_key INT REFERENCES dim_region(region_key),
  streamline_count  INT,
  edge_weight       NUMERIC
);
```

## References

1. **Kimball R, Ross M.** *The Data Warehouse Toolkit.* 3rd ed. Wiley; 2013. ISBN 978-1118530801.
2. **Linstedt D, Olschimke M.** *Building a Scalable Data Warehouse with Data Vault 2.0.* Morgan Kaufmann; 2015. ISBN 978-0128025109.
3. **Inmon WH.** *Building the Data Warehouse.* 4th ed. Wiley; 2005. ISBN 978-0764599446.

## Where to next

[Lakehouse internals](lakehouse.md) — when relational warehouses run out and Parquet on object storage becomes the substrate.
