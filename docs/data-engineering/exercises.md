# Exercises

> Three tiers of graded, hands-on exercises against your own repo — fundamentals (DAGs, checksums, atomic writes), reliability (kill a worker, replay a backfill), and scale (port to Spark, add Iceberg). Each has a goal, a starter, and a success criterion.

Read the chapters once; do the exercises and the material sticks. Tier 1 takes an afternoon each; Tier 2 a weekend; Tier 3 a weekend to a week. Pick the tier that matches where you are; nothing forces a strict order.

## Tier 1 — Fundamentals

Build the muscles for DAGs, idempotency, atomic writes, schemas, and configuration. These map onto [The DAG mental model](dag.md) and [The five pillars](five-pillars.md).

### 1.1 Draw the DAG

- **Goal** — externalise the dependency structure of your current pipeline so you can reason about it.
- **Starter** — open Mermaid Live, Excalidraw, or paper. List every stage; every input and output file.
- **Do** — draw arrows for every "produces" / "consumes" edge, including subtle ones (a `.lta` registration consumed two stages later counts). Commit as `docs/dag.md` with a Mermaid block.
- **Success criterion** — a teammate who has never seen your pipeline can predict, from the diagram alone, which stages re-run when `aparc+aseg.mgz` is deleted.

### 1.2 Write a DAG from scratch

- **Goal** — internalise the orchestrator-as-DAG-engine abstraction.
- **Starter** — empty repo. Three "stages": a Python script that reads `subjects.txt`, one that emits a per-subject `.json` of dummy stats, and one that aggregates them to `cohort.parquet`.
- **Do** — implement it three ways: pure `Makefile`, `Snakefile`, and a Dagster asset graph. Run each.
- **Success criterion** — all three produce the same `cohort.parquet`. You can articulate which feels nicest for which kind of workload.

### 1.3 Add a checksum gate

- **Goal** — replace mtime-based skipping with content-addressable skipping.
- **Starter** — pick one stage. Compute `sha256(input.nii.gz) + container_digest + git_sha`; persist it in `_manifest.json` next to the output.
- **Do** — at the top of the stage, refuse to re-run if the manifest matches. Verify by `touch`-ing the input file (should still skip) and by changing a container tag (should re-run).
- **Success criterion** — `touch input.nii.gz` does not trigger work; bumping the container digest does.

### 1.4 Make `run_recon()` content-addressable

- **Goal** — apply 1.3 to a stage that actually costs hours.
- **Starter** — `run_recon()` in your repo, today.
- **Do** — cache key = `sha256(T1w nifti + container hash + tool flag)`. Skip if a hash file already exists. Compare with the current mtime / existence check.
- **Success criterion** — a no-op re-run of the whole pipeline takes seconds, not minutes; a single-flag change re-runs only that stage.

### 1.5 Implement atomic writes for the DK CSV

- **Goal** — make idempotency robust to mid-write crashes.
- **Starter** — the stage that writes `dk_connectome.csv`.
- **Do** — write to `dk_connectome.csv.tmp` then `os.replace`. Kill the job mid-write with `kill -9`. Re-run.
- **Success criterion** — the output is never observed in a half-written state; the rerun produces a clean file.

### 1.6 Add a per-subject `manifest.json`

- **Goal** — make every output self-describing.
- **Starter** — wrap your stage entry points.
- **Do** — capture subject ID, container SHA, git SHA, start/end timestamps, exit code per stage, host name, peak RSS (from `seff` / `time -v`).
- **Success criterion** — you can answer "what container produced this file?" from the file alone, no log spelunking.

### 1.7 Three data tests

- **Goal** — introduce schema-level guardrails.
- **Starter** — `pip install pytest`. One test file.
- **Do** — write three asserts, any framework:
    - DK matrix is 84×84 numeric.
    - Tractogram count is between 100 k and 100 M.
    - Every QSIPrep `*.bval` parses and contains at least one `b > 0`.
- **Success criterion** — `pytest -q` reports three passing tests; deliberately breaking one fails it loudly.

### 1.8 Pydantic config object

- **Goal** — replace string-shaped config with validated config.
- **Starter** — `pip install pydantic`. Create `dwi_pipeline/config.py`.
- **Do** — mirror today's env vars as a `pydantic.BaseSettings`. Replace `${RESULTS_ROOT:-…}` with `cfg.results_root`. Run with a valid config and an invalid one (negative `n_cpus`, missing path).
- **Success criterion** — bad config fails at startup with a clear error, not at hour 7 of a cluster job.

## Tier 2 — Reliability

Build the muscles for retries, recovery, observability, and replays. Maps onto [Reliability & operations](reliability.md) and the failure-mode section of the [DWI case study](dwi-case-study.md).

### 2.1 Kill a worker, recover

- **Goal** — prove your pipeline survives a node crash without data loss or duplicate work.
- **Starter** — pipeline running on 5 subjects.
- **Do** — `kill -9` the Snakemake process during the QSIPrep stage of `sub-003`. Re-run. Inspect the outputs.
- **Success criterion** — completed subjects are not recomputed; `sub-003` resumes cleanly; no half-written file in gold.

### 2.2 Replay a targeted backfill

- **Goal** — practice the everyday operational ask: "re-run sub-007 through sub-012 with the new container".
- **Starter** — bump the QSIPrep container digest in your config.
- **Do** — run the pipeline; verify only those six subjects re-run; verify the rest is a no-op by inspecting the `runs` table or Snakemake's `--summary`.
- **Success criterion** — the diff in your gold layer is exactly six subjects' parquet files; everything else is byte-identical to before.

### 2.3 A `runs` table

- **Goal** — make operational state queryable.
- **Starter** — DuckDB, one Python helper.
- **Do** — emit a row per (subject, stage, attempt) capturing run_id, timestamps, exit_code, peak_rss_gb, host, container_sha, code_sha, log_path. See [DWI case study §4.6](dwi-case-study.md#46-observability-what-you-wire-up-on-day-one).
- **Success criterion** — you can answer in SQL: "p95 runtime of QSIPrep this week", "subjects that retried more than once", "which container produced sub-042's connectome".

### 2.4 A retry policy with classes

- **Goal** — encode the "what's worth retrying" decision once.
- **Starter** — your stage dispatch loop.
- **Do** — implement `run_with_retry` with the five failure classes (input, resource, dependency, transient, logic) and the right policy for each. Inject a fake `ResourceError` and watch the resource bump. Inject a fake `InputError` and watch the quarantine path.
- **Success criterion** — different exception types lead to different behaviour, observable in the `runs` table.

### 2.5 Write a runbook

- **Goal** — make a top failure mode soluble by someone who isn't you, at 3am.
- **Starter** — pick the most frequent failure in the last month.
- **Do** — write `docs/runbook_recon_failed.md` covering symptoms, common causes, diagnostic commands, remediation, escalation. Test it: ask a labmate to use only the runbook to diagnose a planted failure.
- **Success criterion** — they fix it without paging you.

### 2.6 A `--dry-run` flag

- **Goal** — make planned work auditable before submission.
- **Starter** — `submit.sh`.
- **Do** — add `--dry-run` that prints the planned `sbatch` command and the list of subjects that would actually be processed (skipping those already complete).
- **Success criterion** — `submit.sh --dry-run` reports zero subjects on a freshly-completed cohort.

### 2.7 Build the cohort-summary DuckDB

- **Goal** — practice the gold-layer load and reduce.
- **Starter** — DuckDB CLI or `import duckdb`.
- **Do** — load `dk_connectome.csv` from every subject into a single table; write a SQL query that returns mean edge weight per (`subject`, `source_region`).
- **Success criterion** — one query, one Parquet output; the statistician can open it without help.

## Tier 3 — Scale

Build the muscles for moving from a single-cluster pipeline to a real data platform. Maps onto the [Advanced topics](advanced/index.md) and the cloud sections of [HPC → industry](hpc-to-industry.md). These are the exercises that turn a portfolio piece from "neat scientific pipeline" into "credible DE platform".

### 3.1 Port a stage to Snakemake (if you haven't already)

- **Goal** — replace bash glue with a declarative DAG.
- **Starter** — Snakemake docs; `recon` is a good first stage.
- **Do** — write the rule; declare `input`, `output`, `container`, `threads`, `resources`. Run `snakemake --executor slurm -j 2` for `sub-001` and `sub-007`.
- **Success criterion** — `snakemake -n` correctly reports the work-to-do diff; `snakemake --report report.html` produces a provenance artifact.

### 3.2 Port the cohort reduce to Spark

- **Goal** — feel where Spark earns its keep — and where it doesn't.
- **Starter** — `pyspark` on your laptop (`pip install pyspark`); your gold Parquet files.
- **Do** — rewrite the cohort-load + edge aggregation in PySpark. Run on local mode first; then on a 4-worker cluster (Docker Compose or `spark-submit --master k8s`).
- **Success criterion** — same output as the DuckDB version, within float tolerance; you can explain why DuckDB is faster for 150 subjects and Spark is faster for 150,000.

### 3.3 Land the gold layer in Iceberg

- **Goal** — give the gold layer transactions, snapshots, and time travel.
- **Starter** — `pyiceberg` or Spark + Iceberg. MinIO or AWS S3 as backing store.
- **Do** — write `connectome_edges` as an Iceberg table partitioned by `run_id`. Run two consecutive cohort loads; query the previous snapshot with `SELECT * FROM connectome_edges.snapshot_id = ...`.
- **Success criterion** — you can roll back a bad load by reading the previous snapshot; concurrent writers don't corrupt the table.

### 3.4 Add a data-quality gate before promotion

- **Goal** — gate prod promotion on the data, not just the code.
- **Starter** — `pip install great-expectations` or write the checks by hand.
- **Do** — define checks: row count within ±20% of last run, no nulls in `subject_id`, `streamline_count >= 0`, `fa_mean` mean within ±0.05 of last run. Wire into the [CI/CD](cicd.md) `promote` step.
- **Success criterion** — a deliberately corrupted cohort load fails the gate and never moves the `_current` pointer.

### 3.5 Replace NFS with object storage

- **Goal** — feel what changes when POSIX assumptions disappear.
- **Starter** — MinIO on a single node, or a personal S3 bucket.
- **Do** — port one stage to read inputs from and write outputs to S3. Notice everywhere the code assumed `os.rename`, hard links, or globs.
- **Success criterion** — the stage works against S3 with the same idempotency guarantees as before; atomic publish uses multipart upload + rename, not POSIX `mv`.

### 3.6 Add ephemeral PR environments

- **Goal** — let a reviewer poke at a real (tiny) pipeline run before merging.
- **Starter** — GitHub Actions and an S3 bucket.
- **Do** — implement [CI/CD §10.5](cicd.md#105-ephemeral-environments): each PR gets `s3://cohort-staging/pr-{N}/`, runs the pipeline on a 3-subject shadow cohort, posts a QC summary as a PR comment, deletes itself on PR close.
- **Success criterion** — a reviewer approves a non-trivial PR based on the QC delta, not just the code diff.

### 3.7 Streaming intake of new subjects

- **Goal** — appreciate what changes when "batch" becomes "as data arrives".
- **Starter** — Kafka in Docker; a producer that drops new DICOM tarball paths on a topic.
- **Do** — replace the cron-based intake stage with a Kafka consumer that triggers the per-subject DAG on each message. Add a dead-letter topic for bad inputs.
- **Success criterion** — a new DICOM dropped into the scanner share triggers the pipeline within seconds; a malformed input goes to the DLQ and the rest of the pipeline keeps running.

### 3.8 FinOps dashboard

- **Goal** — make cost a first-class signal.
- **Starter** — your `runs` table plus a cost-per-stage estimate (CPU-hours × $/CPU-hour).
- **Do** — emit `cost_usd` per run; build a Grafana panel showing $/subject, $/stage, top 10 most expensive subjects of the week.
- **Success criterion** — you can answer "what would it cost to rerun the whole cohort with the new container?" in a minute, with numbers.

## A self-check before you stop

If you've done a representative sample across the tiers, you can answer all of these honestly:

- I can show the DAG of my pipeline from memory.
- A no-op re-run takes seconds because everything is content-addressable.
- Killing a worker mid-run never corrupts state.
- I can backfill any subset of subjects with a one-line command.
- Every output has a manifest that traces back to a code SHA and a container digest.
- A reviewer sees schema and QC deltas as PR comments.
- I can answer cost questions about my pipeline in SQL.

That's not "junior research scripter"; that's "DE-credible operator". The [portfolio roadmap](portfolio-roadmap.md) sequences these into a public-facing case study.

## References

1. **Köster J, Rahmann S.** Snakemake — a scalable bioinformatics workflow engine. *Bioinformatics.* 2012;28(19):2520–2522. [doi:10.1093/bioinformatics/bts480](https://doi.org/10.1093/bioinformatics/bts480)
2. **Armbrust M, Das T, Sun L, et al.** Delta Lake: high-performance ACID table storage. *VLDB.* 2020. [doi:10.14778/3415478.3415560](https://doi.org/10.14778/3415478.3415560)
3. **Raasveldt M, Mühleisen H.** DuckDB: an embeddable analytical database. *SIGMOD.* 2019. [doi:10.1145/3299869.3320212](https://doi.org/10.1145/3299869.3320212)
4. **Zaharia M, Chowdhury M, Franklin MJ, et al.** Spark: cluster computing with working sets. *HotCloud.* 2010.
5. **Great Expectations.** [greatexpectations.io](https://greatexpectations.io/)

## Where to next

- [Portfolio roadmap](portfolio-roadmap.md) — these exercises framed as a six-milestone progression you can publish.
- [Advanced topics](advanced/index.md) — data modeling, lakehouses, Spark internals, streaming, dbt, contracts, FinOps when the basics aren't enough.
- [DWI case study](dwi-case-study.md) — the worked pipeline these exercises stretch.
