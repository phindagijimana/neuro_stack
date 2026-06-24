# Concepts in depth

The chapters so far gave you the mental model. This chapter goes deeper into the specific ideas you'll meet daily.

## 5.1 ETL vs ELT

- **ETL** = Extract, **Transform**, then **Load** into the destination.
- **ELT** = Extract, **Load** raw into the destination (typically a warehouse), then **Transform** there using SQL.

Modern warehouses (Snowflake, BigQuery, Redshift, Databricks) made ELT dominant because SQL on huge tables is now cheap and fast. **dbt** is the industry-standard tool for the "T" in ELT.

In neuroimaging, "transform" usually happens in Python / MRtrix and the final artifacts get loaded into a warehouse for analytics — so you'd typically use a hybrid: **ET first** (the heavy lifting on the cluster), then **L** into a warehouse where downstream **T** queries live.

## 5.2 Idempotency — deeper

Idempotency depends on three things:

- **Deterministic output paths** — the same inputs always produce the same output path.
- **Atomic writes** — either the output appears completely or not at all. Half-written files break idempotency. Pattern: write to `output.tmp`, then `mv output.tmp output`.
- **Content-based skipping** — Snakemake / Make use file mtimes; more robust tools use content hashes (Bazel, Nix). Hash-based skipping survives `touch` and clock skew.

A pipeline that is non-idempotent will at some point cause an incident — a partially completed retry will leave inconsistent state, and re-running won't fix it.

## 5.3 Determinism and reproducibility

Two distinct properties often conflated:

- **Determinism** — the same code on the same inputs always gives the same outputs *bit-for-bit*. Hard to achieve when ML, randomness, parallel reductions, GPU drivers are involved.
- **Reproducibility** — a colleague (or you in two years) can re-run and get equivalent outputs given the same code version, container image, and inputs.

Containers + pinned container tags (**never `:latest`**) + pinned dataset versions get you most of the way to reproducibility. Bit-for-bit determinism is a research project of its own; usually not worth chasing in DE.

## 5.4 Schemas, contracts, validation

A **schema** declares the shape of data (field names, types, nullability, constraints). A **data contract** is a schema + an agreement between producer and consumer about backwards-compatibility, freshness, and ownership.

When you pass `--skip-bids-validation` to QSIPrep you are explicitly turning off your schema check. In industry that's equivalent to disabling Pydantic — sometimes pragmatic, often the cause of the next outage.

See [Data contracts and schema evolution](advanced/data-contracts.md) for the full treatment.

## 5.5 Data lineage and provenance

**Lineage** = the directed graph of "table X was produced by job Y consuming tables A, B, C". When something is wrong with X you can walk the graph upstream and find the root cause.

Industry tools: OpenLineage (open standard), Marquez (reference impl), Atlan / Collibra / DataHub (catalogs). dbt's `manifest.json` is a lineage artifact too.

Your pipeline's lineage is implicit in the bash dispatch. Snakemake makes it explicit (every output has a rule with declared inputs); a `--report` HTML page renders it.

## 5.6 Partitioning and sharding

**Partitioning** is how you split a big dataset along a natural key so consumers can read only the slice they need. Your "partition key" in neuroimaging is `subject_id`. Common industry keys: `date` (`/year=2026/month=05/day=12/...`), `region`, `tenant`.

Partitioning enables:

- **Selective reprocessing** — fix one subject without re-running the whole cohort.
- **Parallelism** — each partition is an independent task.
- **Pruning** — query engines skip partitions outside the filter.

Bad partition keys (high cardinality or no skew alignment) destroy these benefits. There are entire blog posts on the **small-files problem** — too many tiny partitions overwhelm metadata systems.

## 5.7 Backpressure, retries, exponential backoff

When a downstream system is overloaded, you don't keep hammering it — you slow down (**backpressure**), retry after a delay, and increase the delay each time (**exponential backoff**), with a little randomness (**jitter**):

```python
sleep = min(cap, base * 2 ** attempt) * random(0.5, 1.5)
```

In neuroimaging this matters for API-bound stages (TemplateFlow downloads, cloud storage). Slurm itself implements backpressure via the queue.

## 5.8 Cost-aware design

Every design choice has a $ price tag at scale:

- Running `recon-all` sequentially: 10 h × 60 subjects = **600 CPU-hours**.
- Running `recon-all` with 5-way concurrency: same total CPU-hours, but the cohort finishes in ~120 wall hours.
- Switching to FastSurfer: ~60 CPU-hours instead of 600. **Maybe 90% cost reduction** at the price of slightly different surfaces.

A senior DE always knows the *dollar-per-run* of their main pipeline and can speak to the cost / benefit of optimisations. In the cloud this is measured in AWS bill lines; in HPC it's CPU-hour quotas. The neuroimaging-specific cost regimes — N=10k UK-Biobank-scale storage tiering, fMRIPrep walltime budgeting, S3 egress for cohort downloads — are covered in [Cohort-scale pipelines](advanced/cohort-scale.md) and [Cloud computing](../computing/cloud.md#the-cost-math).

## Where to next

[Tooling landscape](tooling.md) — the orchestrators, storage, transformation, streaming, and observability tools that show up in this space.
