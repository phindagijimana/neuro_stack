# Foundations

> What "data engineering" actually means once you strip the marketing — the mental shift from scripts to systems, the five jobs of a DE platform, the vocabulary that recurs everywhere, and how to tell which shape of pipeline you're really building.

## 1.0 The mental shift — from scripts that worked once to systems that survive change

Most scientists arrive at data engineering through the same path: a script that ran on one subject, then a `for` loop over a cohort, then a bash wrapper that submits the loop to Slurm, then a directory full of `*.sh` files that nobody remembers writing. That's a perfectly natural progression and it produces real science. It also produces something that breaks the moment any of four things change — and one of them always changes.

A **script** is optimised for the run that's happening right now: the cohort sitting in `$BIDS`, the container that's loaded on the cluster today, the analyst who's awake to babysit it. A **system** is optimised for *the runs that haven't happened yet*: a new scanner site joins next month, the recon container ships a bug fix, a co-author asks for the cohort "but only adults", and someone has to backfill last year. Everything in this section is about making the second case cheap — *without* losing the first case's ease.

The mental shift is to stop asking "did the code work?" and start asking "what happens to the output the next time something I don't control changes?". That's the question a data engineer is paid to answer.

## 1.1 The four pressures

Every design choice in this section is a response to one of four pressures. Spot them in any pipeline and you can predict where it will break.

| Pressure | What's growing | Symptom when ignored | The DE response |
| --- | --- | --- | --- |
| **Scale** | Cohort size, file size, throughput | "It worked on 5, it OOMs on 500" | Partitioning, parallelism, streaming, lakehouses. |
| **Variety** | Modalities, sites, schemas, sources | "Site B's DICOM headers break the converter" | Schemas, contracts, validation, quarantines. |
| **Change** | Code, containers, dependencies, vendors | "We can't reproduce the figure in the resubmission" | Versioning, lineage, manifests, content-addressing. |
| **Time** | Real-world calendar, deadlines, SLAs | "Statistician needed it Monday; it's Thursday" | Orchestration, SLOs, observability, on-call. |

A "research script" only has to survive one snapshot of all four. A "platform" has to survive each of them moving independently for years. The chapters that follow are organised around these pressures — orchestration and reliability for **time**, contracts and validation for **variety**, performance and lakehouses for **scale**, versioning and lineage for **change**.

## 1.2 What data engineering actually is

A **data engineer** builds and operates the systems that move, transform, store, and serve data so that downstream consumers — analysts, scientists, ML systems, products — can rely on it. The output of a data engineer is not an analysis or a model; it's *infrastructure* that other people use.

Three roles, frequently confused:

- **Data analyst / scientist** — asks questions of data; produces dashboards, reports, models.
- **ML engineer** — productionises models; lives at the boundary of research and serving.
- **Data engineer** — owns the pipelines that produce the data the other two consume. If their pipeline is down, nobody else works.

If you write code that takes diffusion-weighted images from a scanner, preprocesses them, computes a connectome matrix, and lands the result on disk for someone else to analyse — congratulations, you're doing data engineering for neuroimaging. The "data" is DWI volumes, FreeSurfer surfaces, and connectome matrices; the "consumers" are eventually statistical analyses and downstream ML.

## 1.3 The five jobs of a DE platform

Every data platform — from a one-person scientific pipeline to a thousand-engineer warehouse at a tech giant — has the same five jobs. The proportions differ; the jobs don't.

| Job | Question it answers | Neuroimaging example | Industry example |
| --- | --- | --- | --- |
| **Ingestion** | How does data enter the system? | Pull DICOMs from scanner; pull demographics from REDCap. | Stripe webhook; Kafka topic; nightly SFTP. |
| **Storage** | Where does it live, in what format, for how long? | BIDS on NFS; Parquet on S3; DuckDB on disk. | Snowflake; S3 + Iceberg; Postgres. |
| **Transformation** | How is raw data turned into something usable? | QSIPrep, recon-all, tractography. | dbt models; Spark jobs; Flink streams. |
| **Serving** | How do consumers read the result? | A Parquet file the statistician opens in R; a Streamlit dashboard. | A BI tool; a feature store; an API. |
| **Governance** | Who can see/change what, and how do we know? | Subject IDs hashed; manifests with code SHA; audit log of writes. | Row-level security; SOC 2 audit; data contracts. |

A pipeline that does only the first three is a script. A platform that does all five is infrastructure. The gap is mostly governance and serving — the parts research code routinely under-builds.

## 1.4 ETL vs ELT vs ML pipelines vs research scripts

These four terms get conflated. They are different shapes with different operational profiles.

| Shape | What runs where | Who owns the "T" | Failure mode | Best fit |
| --- | --- | --- | --- | --- |
| **ETL** | Transform on a compute substrate, load result into the store | Engineer | Slow heavy jobs, expensive re-runs | Heavy unstructured / binary data (neuroimaging, video). |
| **ELT** | Load raw into a warehouse, transform with SQL | Analyst / analytics engineer | Bad SQL costs warehouse $$ | Tabular business data, BigQuery / Snowflake era. |
| **ML pipeline** | ETL plus a training step plus a serving step plus monitoring | ML engineer | Drift, training/serving skew | Productionised models. |
| **Research script** | A notebook; whatever the author had open | The author, until they leave | Cannot be reproduced | Exploration. |

A neuroimaging cohort pipeline is ETL with a touch of ELT at the end: heavy lifting on the cluster (Extract + Transform), then the gold layer gets Loaded into DuckDB / Snowflake where downstream Transforms (cohort filters, group stats) live in SQL. See [Concepts in depth](concepts.md) for the ETL/ELT mechanics.

## 1.5 Batch vs streaming vs micro-batch

Three execution models. Most teams need only one.

- **Batch** — accumulate inputs; process them on a schedule (hourly, daily) or on demand. Throughput-optimised. Almost all scientific pipelines are batch. Tools: Snakemake, Airflow, Spark.
- **Streaming** — process each event as it arrives, with latencies measured in milliseconds to seconds. Latency-optimised. Tools: Kafka + Flink, Kinesis + Lambda.
- **Micro-batch** — batches of a few seconds. A compromise; in practice this is "streaming people who got tired of streaming". Tools: Spark Structured Streaming.

When in doubt, batch. Streaming buys lower latency at the cost of an order of magnitude more operational complexity. Researchers rarely have a latency budget that justifies it; clinicians sometimes do (real-time monitoring), and that's when streaming earns its keep.

## 1.6 Where DE differs from research scripting

A research script and a production pipeline can look identical for one run. They diverge the second time you run them, and on every run after that.

| Property | Research script | Production pipeline |
| --- | --- | --- |
| Inputs | "The data on my disk" | A versioned, schema-checked source |
| Re-running | "Hope it still works" | Idempotent and explicitly tested |
| Failure | Author re-runs interactively | Retries, alerts, runbook, on-call |
| Consumers | The author | Other humans + downstream systems |
| Lifetime | Weeks | Years |
| Change rate | Constant tweaking | Reviewed PRs, releases |
| Cost model | Free at the margin (sunk cluster) | A line item someone watches |

Both are valuable. The mistake is using a research script in a production-shaped slot — that's how cohorts silently drift, models silently break, and someone spends a week reconstructing why `sub-042`'s connectome looks weird.

## 1.7 What "production-grade" means

A pipeline is **production-grade** when it satisfies, roughly, these six properties:

- **Correct** — outputs match the contract you advertised.
- **Idempotent** — running it twice with the same inputs gives the same outputs and no side effects.
- **Observable** — when something goes wrong you can find out *what*, *where*, *when*, and ideally *why* without re-running the pipeline.
- **Recoverable** — a failed run can be resumed from the point of failure without redoing finished work.
- **Documented** — a new teammate can run it without paging you.
- **Tested** — changes are validated automatically before they hit the cluster or cloud.

Most scientific pipelines satisfy *some* of these. A bash pipeline that already skips already-completed `recon-all` runs and emits structured logs has idempotency and partial observability. The rest of this section is mostly about closing the remaining gaps.

!!! tip "Self-check"
    Pick your current pipeline. Score it 0–5 on each of the six properties. Pillars scoring 0 or 1 are where the next milestone of work should go.

## 1.8 The "data product" mindset

The most useful shift, once the mechanics are in place, is to stop thinking of your pipeline as code and start thinking of it as a **product** with users:

- The output has a **contract** (schema, freshness SLO, owner, on-call).
- It has **versions** that change in reviewed PRs, not at 2am.
- It has a **changelog** consumers can read.
- It has **support** — a way for consumers to file issues, ask for a backfill, request a schema change.

A statistician who can read `connectome_edges.parquet`'s schema page, see "last updated 6h ago, owner @phin, p99 freshness 18h, last incident 47 days ago", and know they can trust the file — that's a data product. Everything else in this section is in service of that outcome.

## 1.9 Vocabulary you'll meet everywhere

A handful of words recur in every chapter, every job interview, and every postmortem. Lock them down now and the rest of the section stops feeling like jargon.

| Word | What it actually means | Example |
| --- | --- | --- |
| **Data** | The bytes a consumer eventually reads. | The 84×84 connectome matrix; the `participants.tsv` row. |
| **Metadata** | Bytes that *describe* data — schema, units, provenance, ownership. | The JSON sidecar next to a NIfTI; the `_manifest.json` next to an output. |
| **Sidecar** | A metadata file colocated with its data, sharing the stem. | `dwi.nii.gz` ↔ `dwi.json` in BIDS. |
| **Artifact** | A concrete file (or table) that a stage produces. | `aparc+aseg.mgz`, `dk_connectome.csv`. |
| **Derivative** | An artifact computed from another artifact, not from raw input. | QSIPrep output is a derivative of the bronze DWI. |
| **Manifest** | A machine-readable record of *what produced what, with which versions*. | `{"code_sha": "abc1234", "container": "qsiprep@sha256:..."}` |
| **Schema** | The shape of data — fields, types, nullability, constraints. | "DK matrix: float64, shape (84,84), no NaN." |
| **Contract** | Schema + behavioural promise (freshness, owner, compat policy). | "`connectome_edges` is refreshed daily by 08:00, owned by @phin." |
| **Lineage** | The graph of "X was produced from Y". | DICOM → BIDS → QSIPrep → DK matrix → cohort table. |
| **Provenance** | The full causal story for one artifact: code, container, inputs, environment. | The `_manifest.json` next to `sub-042/dk.parquet`. |
| **Backfill** | Re-running historical periods (or subjects) with new code or new inputs. | "Re-run all subjects with QSIPrep 0.24." |
| **Replay** | A targeted, often incremental, recompute. | "Recompute `sub-007` because we found a bvec flip." |
| **Bronze / silver / gold** | Layers — raw / curated / analysis-ready. | DICOM / BIDS / `connectome_edges.parquet`. |
| **SLO / SLA** | An internal target / an external promise on freshness or availability. | "p95 freshness of gold ≤ 24h." |

If a sentence in this section uses one of these words and you can't define it without scrolling, scroll. The whole section presumes them.

## 1.10 Everything is a function — and side-effects are where pipelines bleed

A useful way to view every stage in a pipeline is as a **function**:

```
stage : (inputs, config) -> outputs
```

The healthier you keep this view, the easier your pipeline is to reason about, test, retry, and parallelise. The two relevant concepts borrow from functional programming:

- A **pure** function depends only on its inputs and produces only its declared outputs. No reads of global state, no surprise side-effects, no nondeterminism. Given the same inputs you get the same outputs, always.
- A **side-effect** is anything else a stage does: writing logs, mutating a database, sending an email, racing on a shared file, reading the current time.

In a real pipeline you cannot eliminate side-effects — the whole *point* of a pipeline is to produce artifacts on disk and rows in a database. The discipline is to push side-effects to the **edges**, where they are explicit and auditable, and keep the core logic pure:

```python
# Edge: side-effect (read input).
arr = load_nifti(input_path)

# Core: pure function. Easy to unit-test; given the same arr, same result.
mask = brain_mask(arr, threshold=cfg.threshold)

# Edge: side-effect (write output, emit manifest).
atomic_write_nifti(mask, output_path)
emit_manifest(output_path, code_sha=cfg.code_sha, container=cfg.container)
```

The pure-core / impure-edge pattern is what lets you:

- **Unit-test** the science without standing up Slurm.
- **Parallelise** across subjects without worrying about contention — pure functions don't share state.
- **Cache** results by content hash — only pure functions are safely content-addressable.
- **Retry** safely — pure functions are trivially idempotent; side-effects must be made idempotent on purpose (atomic write, upsert, dedup key).

Mølbak and Beauchemin call this *functional data engineering*; Snakemake, dbt, Dagster, and Bazel all bake it in. The deeper treatment is in [Concepts in depth](concepts.md#52-idempotency-deeper).

## 1.11 Cohort thinking vs subject thinking

A script reasons about one subject at a time: "for `sub-001`, run the steps". A pipeline reasons about the cohort as a first-class object: "for the cohort, here is the per-subject DAG, here is the cohort-level reducer, here is what 'done' means at the cohort level".

The shift shows up in five places:

| Concern | Subject thinking | Cohort thinking |
| --- | --- | --- |
| **Done** | "`sub-001` finished." | "147 of 150 subjects complete; 2 quarantined; 1 in retry." |
| **Failure** | "It crashed; I'll re-run it." | "Failure rate is 2% this week, up from 0.5% — investigate." |
| **Cost** | "It took 6 hours on my GPU." | "$7.20 / subject × 150 = $1,080 for the cohort; here's the per-stage breakdown." |
| **Schema** | "The output looks right." | "100% of subjects emit the 7-column gold row; nulls are 0." |
| **Backfill** | "I'll loop over the subjects." | "One command, one run_id, the scheduler handles fan-out and skipping." |

Cohort thinking is what makes statements like "the pipeline's p95 freshness is 18h" meaningful. Subject thinking can't make them; it has no aggregate. Once you reason at the cohort level, the [runs table](dwi-case-study.md#46-observability-what-you-wire-up-on-day-one) and the [SLOs](reliability.md) that sit on top of it stop feeling like overkill and start feeling like the obvious move.

## 1.12 A short tour of the storage hierarchy

Performance and cost in data pipelines are dominated by *where the bytes live*. The hierarchy is roughly:

| Layer | Latency (random read) | Throughput | $/GB·month | Right job |
| --- | --- | --- | --- | --- |
| **CPU cache (L1/L2/L3)** | <10 ns | TB/s | n/a | Hot loops inside a process. |
| **RAM** | ~100 ns | tens of GB/s | $0 (sunk) | Working set; DuckDB / Polars / Spark in-memory. |
| **Local NVMe** | ~100 µs | GB/s | $0.05–0.20 | Scratch; container layer cache; intermediate parquet. |
| **Cluster NFS / Lustre** | ~1 ms | hundreds of MB/s shared | $0.02–0.05 | BIDS, silver derivatives, "scratch but shared". |
| **Object storage (S3 / GCS)** | ~50–200 ms | hundreds of MB/s per stream | $0.023 (Standard) | Bronze, gold, cross-cluster sharing. |
| **Cold object storage (Glacier)** | minutes to hours | low | $0.001–0.004 | Archive of frozen cohorts. |
| **Tape** | hours | low | $0.001 | Institutional archival; you rarely see it directly. |

Two intuitions to internalise:

- Each step down is ~10–100× the previous in latency. Reading 1 GB from RAM is "instant"; from S3 it's "go get coffee". Pipelines that ignore this read S3 in a tight Python loop and wonder why they're slow.
- Each step down is ~5–20× cheaper per stored GB. That's why bronze ends up in S3 and gold ends up in DuckDB / Parquet — different storage tiers for different access patterns is the whole game.

The lakehouse architectures (Iceberg, Delta, Hudi) exist precisely to give object storage warehouse-like *behaviour* — transactions, snapshots, schema evolution — without paying the warehouse $/GB. See [Lakehouse internals](advanced/lakehouse.md) for the deeper treatment, and [Performance & scale](performance.md) for how to spot which tier is your bottleneck.

## 1.13 Time, lineage, and versioning as first-class concerns

The biggest difference between a research script and a platform is what each treats as **first-class** — i.e., what the system represents explicitly, not what's left to convention or memory.

A research script's first-class concerns are usually just *correctness on this run*. A platform adds three more:

- **Time** — every artifact has a "produced at" timestamp; every query can specify "as of when". This is what lets you reproduce a figure six months later, or roll a release back to yesterday's gold.
- **Lineage** — every artifact knows what produced it, with which code, against which inputs. The lineage graph is queryable; you can walk from `connectome_edges.parquet` back to a particular DICOM tarball and a particular git SHA.
- **Versioning** — code, container, schema, and data each have a version with a sane upgrade story. Snapshots, semver, content hashes, Iceberg time travel, container digests — these are all names for the same instinct: "I will need yesterday's answer tomorrow".

The clean test for whether you treat these as first-class is the **paper-resubmission test**: a reviewer asks for a small change to Figure 3 nine months after submission. Can you recompute the figure on the *same* code, container, and data that produced the original? If yes, time / lineage / versioning are first-class for you. If no — and most scientific pipelines fail this test — they aren't, and the chapters on [versioning](advanced/versioning.md), [data contracts](advanced/data-contracts.md), and [catalogs](advanced/catalogs.md) are where you fix it.

## 1.14 The five jobs, expanded

The platform jobs from §1.2 are worth a closer look — every chapter that follows is, in effect, building one of them out.

### Ingestion

The boundary between systems you don't control and systems you do. Three properties you want:

- **At-least-once delivery** — if the source crashes mid-transfer, you can resume; no input is silently dropped.
- **Schema-on-read at minimum** — the validator runs before the data lands in silver. See [Testing pipelines](testing.md).
- **Backpressure** — if downstream is slow, ingestion slows or buffers, not crashes.

In neuroimaging the source is usually a DICOM share. The same principles apply — `rsync --partial`, checksum verification, quarantine on validator failure.

### Storage

Three layers, three jobs:

- **Bronze** — immutable raw. Optimised for cheap writes, infrequent reads, eventual lifecycle to cold storage.
- **Silver** — curated, conformed. Optimised for repeated reads by transformation jobs.
- **Gold** — analysis-ready. Optimised for queries from humans and BI tools.

Format choice: NIfTI/MGZ for medical-image silver, Parquet for tabular silver/gold, JSON sidecars for metadata everywhere. Object storage (S3, GCS) replaces NFS once you outgrow a single cluster — the abstraction stops being POSIX and starts being "buckets and keys".

### Transformation

The job that consumes the most code. Three flavours, often mixed:

- **Heavy/binary** — Python + a domain library (MRtrix, FreeSurfer, MONAI). Slow, expensive, cluster jobs.
- **Tabular** — SQL via dbt or Spark. Fast, cheap, warehouse jobs.
- **ML** — training + inference. See the [AI](../ai/index.md) section.

A neuroimaging pipeline does all three; the trick is putting each in its right substrate.

### Serving

Who reads the result and how. In order of increasing engineering investment:

- A Parquet file the statistician opens in R or pandas.
- A DuckDB / SQLite database with a documented schema.
- A Streamlit / Dash dashboard for cohort browsing.
- A warehouse table (Snowflake, BigQuery) that BI tools and notebooks both hit.
- An API or a feature store for ML systems.

Pick the lightest one that works. Building an API when a Parquet file would do is gold-plating.

### Governance

The job most often skipped, and the one that bites hardest later. Four sub-questions:

- **Access** — who can read what? PHI / PII access lists; row-level filtering for multi-site cohorts.
- **Lineage** — where did this number come from? Manifests, run IDs, code SHAs.
- **Audit** — who changed what, when? An append-only log of writes to gold.
- **Retention** — how long do we keep it? GDPR right-to-be-forgotten, IRB data destruction clauses.

You don't have to build all of this on day one. You do have to know it's there so you don't paint yourself into a corner.

## 1.15 A 60-second worked example

To make all of the above concrete, here is a one-cell version of the platform applied to a single subject:

```python
# A "platform" in 30 lines.
from pathlib import Path
import json, hashlib, subprocess, time

def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()

def stage(name, inputs, output, run):
    """Idempotent stage: skip if manifest matches; else run; emit manifest."""
    manifest_path = output.with_suffix(output.suffix + ".manifest.json")
    key = sha256_of([sha(i) for i in inputs] + [CODE_SHA, CONTAINER_DIGEST])
    if manifest_path.exists():
        if json.loads(manifest_path.read_text())["key"] == key:
            return                                        # cached: free
    tmp = output.with_suffix(output.suffix + ".tmp")
    t0 = time.time()
    run(inputs, tmp)                                       # the actual work
    tmp.replace(output)                                    # atomic publish
    manifest_path.write_text(json.dumps({
        "key": key, "code_sha": CODE_SHA,
        "container": CONTAINER_DIGEST, "elapsed_s": time.time() - t0,
    }))
```

Thirty lines, every pillar present: orchestration (the function is the unit a scheduler calls), idempotency (manifest gate), isolation (container digest in the key), observability (manifest = telemetry), configuration (`CODE_SHA` and `CONTAINER_DIGEST` are config). Everything else in this section is making each line robust at scale.

## 1.16 Principles → chapters map

The principles above are not abstract — every later chapter operationalises one of them. Use this map as the table of contents you actually need.

| Principle from §1.0–§1.8 | Operationalised in |
| --- | --- |
| Scripts → systems | [The DAG mental model](dag.md), [The five pillars](five-pillars.md). |
| Pure-core / impure-edge | [Concepts in depth](concepts.md), [Testing pipelines](testing.md). |
| The four pressures — **time** | [Reliability & operations](reliability.md), [DWI case study §4.7](dwi-case-study.md#47-failure-modes-and-retries). |
| The four pressures — **variety** | [Data contracts](advanced/data-contracts.md), [Data quality](advanced/data-quality.md), [Ingestion](advanced/ingestion.md). |
| The four pressures — **scale** | [Performance & scale](performance.md), [Lakehouse](advanced/lakehouse.md), [Spark](advanced/spark.md). |
| The four pressures — **change** | [Versioning](advanced/versioning.md), [CI/CD](cicd.md), [Catalogs](advanced/catalogs.md). |
| Vocabulary — **data / metadata / manifest** | [DWI case study §4.4](dwi-case-study.md#44-idempotency-contract). |
| Vocabulary — **schemas / contracts** | [Data contracts](advanced/data-contracts.md). |
| Vocabulary — **lineage / provenance** | [Concepts §5.5](concepts.md#55-data-lineage-and-provenance), [Catalogs](advanced/catalogs.md). |
| Vocabulary — **bronze / silver / gold** | [DWI case study §4.3](dwi-case-study.md#43-layers-bronze-silver-gold), [Data modeling](advanced/data-modeling.md). |
| Cohort thinking | [Reliability & operations](reliability.md), [Performance & scale](performance.md). |
| Storage hierarchy | [Tooling §6.3](tooling.md#63-storage-layers), [Performance & scale](performance.md), [Lakehouse](advanced/lakehouse.md). |
| Time, lineage, versioning as first-class | [Versioning](advanced/versioning.md), [Disaster recovery](advanced/disaster-recovery.md). |
| Data-product mindset | [Portfolio roadmap](portfolio-roadmap.md), [Org-level DE](advanced/org.md). |
| The five jobs — **ingestion** | [Ingestion](advanced/ingestion.md), [Event-driven](advanced/event-driven.md). |
| The five jobs — **storage** | [Lakehouse](advanced/lakehouse.md), [Data modeling](advanced/data-modeling.md). |
| The five jobs — **transformation** | [SQL](advanced/sql.md), [dbt](advanced/dbt.md), [Spark](advanced/spark.md). |
| The five jobs — **serving** | [Real-time analytics](advanced/real-time.md), [MLOps overlap](advanced/mlops.md). |
| The five jobs — **governance** | [Security](advanced/security.md), [Data contracts](advanced/data-contracts.md), [Catalogs](advanced/catalogs.md). |

If you only read foundations + the DAG + the five pillars + the DWI case study, you have a working mental model. The rest of the table is depth-on-demand: when one of the pressures bites in real life, that's the chapter to open.

## References

1. **Kleppmann M.** *Designing Data-Intensive Applications.* O'Reilly; 2017. ISBN 978-1449373320.
2. **Reis J, Housley M.** *Fundamentals of Data Engineering.* O'Reilly; 2022. ISBN 978-1098108304.
3. **Zaharia M, Ghodsi A, Xin R, Armbrust M.** Lakehouse: a new generation of open platforms that unify data warehousing and advanced analytics. *CIDR.* 2021. [PDF](https://www.cidrdb.org/cidr2021/papers/cidr2021_paper17.pdf)
4. **Gorgolewski KJ, Auer T, Calhoun VD, et al.** The Brain Imaging Data Structure (BIDS). *Scientific Data.* 2016;3:160044. [doi:10.1038/sdata.2016.44](https://doi.org/10.1038/sdata.2016.44)
5. **Bornstein M.** Emerging architectures for modern data infrastructure. *a16z.* 2020. [link](https://a16z.com/emerging-architectures-for-modern-data-infrastructure/)
6. **Beauchemin M.** Functional data engineering — a modern paradigm for batch data processing. *Maxime Beauchemin blog.* 2018. [link](https://maximebeauchemin.medium.com/functional-data-engineering-a-modern-paradigm-for-batch-data-processing-2327ec32c42a)
7. **Wilkinson MD, Dumontier M, Aalbersberg IJ, et al.** The FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data.* 2016;3:160018. [doi:10.1038/sdata.2016.18](https://doi.org/10.1038/sdata.2016.18)
8. **Backus J.** Can programming be liberated from the von Neumann style? A functional style and its algebra of programs. *Comm. ACM.* 1978;21(8):613–641. [doi:10.1145/359576.359579](https://doi.org/10.1145/359576.359579)

## Where to next

- [The DAG mental model](dag.md) — the abstraction every workflow tool uses under the hood.
- [The five pillars](five-pillars.md) — orchestration, idempotency, isolation, observability, configuration.
- [DWI case study](dwi-case-study.md) — these foundations made concrete against a real cohort pipeline.
- [Concepts in depth](concepts.md) — ETL vs ELT, schemas, lineage, partitioning at greater depth.
