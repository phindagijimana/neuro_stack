# File formats and lakehouse internals

> Row vs columnar; how Parquet actually works; the three modern table formats (Iceberg, Delta, Hudi).

## Row vs columnar

A row-based file stores `row[0], row[1], row[2], ...` consecutively. Reading one column requires touching every row. Good for OLTP, bad for analytics. A **columnar** file stores `col_a[0..n], col_b[0..n], ...` — the default for modern analytics.

## Parquet internals (every DE must know cold)

Apache Parquet ([spec here](https://parquet.apache.org/docs/file-format/)) is structured as:

```text
File
├── Row Group 1
│   ├── Column Chunk: col_a (compressed pages, page index, stats)
│   └── Column Chunk: col_b
├── Row Group 2
└── Footer (schema, per-column metadata, magic bytes)
```

Three properties that matter:

1. **Predicate pushdown.** Each column chunk has min/max/null stats; `WHERE age > 60` can skip whole row groups.
2. **Page-level encoding** (dictionary, RLE, delta) + compression (Snappy, Zstd, LZ4). Zstd for cold, Snappy for hot.
3. **Footer is the index.** Engines read the footer first, prune, then read the data they need.

```python
import pyarrow.parquet as pq
pf = pq.ParquetFile("connectome.parquet")
print(pf.schema_arrow)
print(pf.metadata.row_group(0).column(0).statistics)
```

## Lakehouse table formats

A "table format" wraps Parquet files with a transaction log + metadata so the directory behaves like a SQL table.

| Format | Origin | Notes |
|---|---|---|
| **Apache Iceberg** ([docs](https://iceberg.apache.org)) | Netflix | Open governance; strongest cross-engine support; default for new projects |
| **Delta Lake** ([docs](https://delta.io)) | Databricks | Best Spark integration; UniForm bridges to Iceberg/Hudi |
| **Apache Hudi** ([docs](https://hudi.apache.org)) | Uber | Stream-first; best for high-velocity CDC ingest |

All three solve the same problem. Pick by engine and existing skills, not by data.

## Worked example — DK matrices as an Iceberg table

```python
from pyiceberg.catalog import load_catalog
from pyiceberg.schema import Schema
from pyiceberg.types import IntegerType, StringType, TimestampType, NestedField

catalog = load_catalog("rest")
catalog.create_namespace_if_not_exists("dwi")

schema = Schema(
    NestedField(1, "subject_id",       StringType(),    required=True),
    NestedField(2, "source_region",    IntegerType(),   required=True),
    NestedField(3, "target_region",    IntegerType(),   required=True),
    NestedField(4, "streamline_count", IntegerType(),   required=False),
    NestedField(5, "pipeline_version", StringType(),    required=True),
    NestedField(6, "ingested_at",      TimestampType(), required=True),
)
catalog.create_table("dwi.connectome", schema)
```

Advantages over plain Parquet:

- **Snapshots** — `SELECT * FROM connectome FOR SYSTEM_TIME AS OF '2026-06-01'`.
- **Schema evolution** — add `qc_status` without rewriting data.
- **Partition evolution** — switch from `subject_id` to `cohort_year` mid-life.
- **Compaction** — small-file merging without downtime.

## When to stay on raw Parquet

- Single-writer analytics on a small lab cohort.
- Read-only published datasets.
- When the metastore overhead exceeds the value of ACID.

A reasonable rule: introduce a table format the day you have two writers or a downstream contract.

## References

1. **Apache Parquet Format specification.** [https://parquet.apache.org/docs/file-format/](https://parquet.apache.org/docs/file-format/)
2. **Armbrust M, Ghodsi A, Xin R, Zaharia M.** Lakehouse: a new generation of open platforms. *CIDR.* 2021. [pdf](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)
3. **Behm A, Palkar S, Reiss F, et al.** Delta Lake. *VLDB.* 2020. [doi:10.14778/3415478.3415560](https://doi.org/10.14778/3415478.3415560)

## Where to next

[SQL beyond SELECT](sql.md) — the query side of the analytical workload.
