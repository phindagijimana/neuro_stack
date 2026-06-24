# From scientific HPC to industry DE — bridging the gap

> A direct mapping from the HPC habits you already have onto the industry tools you don't — Slurm to Airflow, scratch to S3, modulefiles to containers, MPI to Spark/Ray — plus an honest list of what carries over and what doesn't.

If you've shipped a working DWI pipeline on a Slurm cluster, you already do data engineering. You just call the parts by different names and miss a few habits an industry team would consider table-stakes. This page is the dictionary plus the gap analysis.

## 11.0 Two cultures

It's easier to bridge a gap if you can see both sides clearly. Scientific HPC and industry DE are two cultures that solve overlapping problems with different defaults.

**Scientific HPC** lives on top of a shared multi-tenant cluster — Slurm or PBS, a POSIX filesystem, the modulefile system, a shared queue, a finite institutional budget you don't see directly. The job is *novel inquiry*: every run is a slightly different question; reproducibility is desirable but the dominant pressure is "ship the paper". Operators are often the authors. The pipeline is glue (`submit.sh`, `array.sh`) around domain containers. Failure is annoying but rarely public.

**Industry data platforms** live on top of object storage, containers, and declarative orchestrators — Airflow, Dagster, K8s, Iceberg on S3, Snowflake, dbt. The job is *repeatable production* of data products another team consumes on a schedule, with consequences. Operators are usually distinct from authors. The pipeline is the product, not the glue. Failure is public, measured, and has an SLO attached.

Neither culture is "better". The cultures *evolved* under different constraints — research has variety and one-shot questions; industry has scale and repeating consumers. A great senior data engineer is fluent in both, and the bridge is the dialect this chapter teaches.

## 11.1 What you already have

The mental model is identical. You've built a multi-stage idempotent pipeline orchestrated by a scheduler, with containerised tasks, configurable via env vars, with structured logs. That's the same shape as the pipelines that move billions of rows a day at large companies — only the data type and tooling differ.

Specifically, if your repo has:

- A DAG (even an implicit one in `submit.sh`).
- Per-subject skip-if-output-exists logic.
- Pinned container tags.
- Per-job log files you can grep.
- Anything resembling a runbook.

…you have, in HPC dialect, the same five pillars an industry team has. The rest is translation and a few habits — versioned storage, observability beyond log files, governance — that scientific environments under-build because they don't have to.

## 11.2 What's different

| Scientific HPC | Industry DE |
| --- | --- |
| Single shared cluster (Slurm) | Heterogeneous compute (K8s, cloud batch, serverless, Spark on YARN) |
| Outputs on POSIX disk (NFS / Lustre) | Outputs in object storage + warehouse + table format (S3 + Iceberg) |
| Logs in `.out` files | Logs in a centralised aggregator (Loki, Datadog, Splunk) |
| Pipelines run when the researcher hits enter | Pipelines run on schedule, on event, on demand |
| "Done when it's done" | SLOs and on-call |
| Final artifact is an analysis or a paper | Final artifact is a contract another team depends on |
| The author is the operator | A separate platform team operates what you authored |
| One copy of the data, mutable | Versioned, immutable, time-travelable |
| Quota and FTE | Cloud bill, cost-per-row, per-cohort scaling |
| `seff`, `sacct` | Prometheus, Grafana, OpenTelemetry |
| Slurm priority queues | Multi-tenant namespaces with resource quotas |

The biggest cultural delta isn't tooling — it's that **someone else depends on your output, on a schedule, with consequences if it's late**. That changes everything about how you build.

## 11.3 The translation table

| HPC concept | Industry analogue | Notes |
| --- | --- | --- |
| Slurm job | Airflow task / Dagster op / K8s Job | Same primitive, different scheduler. |
| `sbatch --array` | DAG with mapped tasks (Airflow `expand`, Dagster `DynamicOut`) | Per-subject fan-out has a first-class API. |
| `Snakefile` | Dagster asset graph / dbt model | All three are declarative DAGs. |
| Apptainer SIF | Docker image in ECR/GCR/Harbor | Same OCI layers; different runtime. |
| `module load X` | `pip install -e .[X]` inside a pinned container | Lockfiles + image digests, not env mutations. |
| `$SCRATCH` | S3 bucket with a lifecycle policy | `aws s3 sync` is the new `cp -r`. |
| NFS shared home | S3 + a manifest file | Object storage doesn't have POSIX semantics; pipelines must adapt. |
| `seff` / `sacct` | Datadog / Grafana / CloudWatch | Per-process metrics → per-task metrics in a TSDB. |
| `.out` / `.err` files | Loki / Elastic / Splunk | Grep is replaced by LogQL / KQL / SPL. |
| Slurm fair-share | K8s ResourceQuotas + priority classes | Same idea, different control plane. |
| Lab disk quota | S3 cost report + lifecycle | Cohort-scale tier rotation replaces quota. |
| `sbatch ... && sbatch --dependency=afterok` | DAG edges | The scheduler owns the dependency, not the user. |
| MPI / `mpirun` | Spark / Ray / Dask | Data-parallel framework instead of message-passing. |
| `pickle` / Parquet on Lustre | Iceberg / Delta on S3 | Tables on object storage with ACID. |
| `crontab` on a login node | Airflow DAG schedule / EventBridge | Centralised, observable scheduling. |
| Email when job fails | PagerDuty / Opsgenie | Real on-call rotation. |
| README + a wiki page | A data contract + a catalog entry (Datahub / Atlas / Unity) | Discoverability is a product feature. |
| Author-as-operator | Designated on-call rotation | The biggest delta. |

You don't need to leave HPC to learn these — most can be added inside an existing scientific repo and they're exactly what makes a portfolio piece read as "production-grade".

## 11.4 What transfers cleanly

The skills you already have from a scientific HPC career are mostly portable — they just go under different names. None of this is wasted.

- **Problem decomposition.** Breaking a paper-sized question into stages with explicit inputs and outputs *is* DAG thinking. Whether it's "denoise → eddy → tractography" or "extract → transform → load", the muscle is identical.
- **The DAG mindset.** Snakemake → Airflow is mostly syntax; the dependency model is identical.
- **Pipeline thinking.** "What does this stage need; what does it produce; what fails if its upstream is broken?" is the only question that matters in either world.
- **Scientific rigor.** The habits that make a clinical analysis defensible — pre-registration, ablations, sensitivity analyses, audited statistics — map directly to schema tests, data contracts, drift checks, and reproducibility guarantees in industry. The bar is, if anything, *higher* in science.
- **Idempotency.** Skip-if-output-exists works on S3 too. The pattern survives the move.
- **Containers.** SIFs and Docker images are both OCI artifacts; `apptainer pull docker://` literally bridges them.
- **Resource right-sizing.** Knowing QSIPrep needs 16 GB and 8 cores transfers verbatim to a K8s request/limit or a Batch job definition.
- **Failure triage instincts.** If you can read a Slurm `.out` file and find the OOM, you can read a Datadog log line and find the same OOM. The dialect changes, the skill doesn't.
- **The discipline of pinning versions.** You already do this for containers; it's the same habit for `requirements.lock`, `Dockerfile` digests, and Iceberg snapshot IDs.
- **Reading domain papers.** The ability to read a methods section and reproduce it in code is rare and valuable. Industry's "papers" are RFCs, ADRs, and design docs — the skill transfers.

## 11.5 What doesn't transfer — and what to add

The bad news is that you need a small but real set of *new* skills. The good news is that they're learnable in a few months of focused work, and each one has a clear "first deliverable" you can ship.

| Skill to add | Why it matters | First deliverable to aim for |
| --- | --- | --- |
| **Cloud primitives** (S3, IAM, VPC, EC2, Batch / GKE / Cloud Run) | Everything in industry sits on these. | Move bronze to S3; run one stage on Batch with a least-privilege IAM role. |
| **Infrastructure as code** (Terraform, Pulumi, CDK) | Reproducible infra is the cloud's `containerd`. Click-ops doesn't scale or audit. | Stand up the above bucket + Batch job from a `terraform apply`. |
| **Object-store semantics + lakehouse tables** (Iceberg / Delta / Hudi) | Object storage isn't POSIX; you need a table format to get ACID. | Write `connectome_edges` as an Iceberg table; do one rollback. |
| **Declarative orchestration** (Airflow / Dagster / Prefect) | The control plane the industry runs on. | Port one cohort run to a Dagster asset graph. |
| **dbt and SQL warehouse work** | The dominant transformation paradigm; how analytics engineers ship. | Write three dbt models against your gold layer; add tests. |
| **Observability stack** (Prometheus, Grafana, Loki, OpenTelemetry) | Beyond `.out` files; the substrate for SLOs and on-call. | One Grafana dashboard for the `runs` table; one alert that fires correctly. |
| **On-call and incident discipline** | The cultural delta. You will be paged; you will write postmortems. | Read [Incident management](advanced/incident-management.md); shadow one rotation. |
| **Cohort cost-awareness** | Every line has a $; every retry is a real number. | Add `cost_usd` per row to `runs`; build a weekly cost report. |
| **Security & compliance basics** (SOC 2 lite, encryption at rest/in transit, audit logs, secrets) | The PHI side of the work is more regulated than IRB; learn the equivalents. | Move secrets out of `.env` into Vault / SSM / Secret Manager. |
| **The product mindset** | Your output has consumers with expectations, not just a graph in Figure 3. | Write a one-page data contract for one gold table; circulate it. |

And the explicit "doesn't transfer" list — the things you do as a scientist that you should stop doing in industry:

- **POSIX assumptions.** `ls`, `mv`, file locks, hard links — none of these mean what you think on S3. Object storage is eventually-consistent (mostly fixed in 2020+ but the mental model still bites), has no real `mv`, no real directories, no append. Learn [Iceberg / Delta](advanced/lakehouse.md) over raw S3.
- **One big shared filesystem.** In the cloud, every team has its own bucket with explicit IAM. Cross-team data access is a *policy decision*, not a `chmod`.
- **"Submit and forget."** Industry pipelines have SLOs. Learn [SLOs and runbooks](reliability.md).
- **One copy of the data.** Production data is versioned (Iceberg snapshots, Delta time travel, S3 versioning). Overwriting in place is a footgun.
- **Author-as-operator.** In industry, the person who wakes up at 3am is on a rotation; the runbook is the bridge.
- **Free compute at the margin.** A loop that retries forever is an incident. At cohort scale this becomes its own discipline — see [Cohort-scale pipelines](advanced/cohort-scale.md).
- **MPI.** Almost nobody writes MPI for data pipelines in industry. Distributed memory is via Spark/Ray/Dask. Learn one of these — see [Spark](advanced/spark.md).
- **Bespoke everything.** The first instinct of a researcher is to write a tool; the first instinct of a platform engineer is to evaluate existing tools. Resist the urge to ship a homemade orchestrator.

## 11.6 Common painful mistakes when moving

The patterns below are the failure modes that every scientific-to-industry mover hits at least once. Naming them in advance halves the pain.

- **Treating S3 like NFS.** `os.rename` doesn't exist on S3 — every "rename" is a copy + delete and costs API calls. `ls -la` over a million keys takes minutes; budget for it. Use multipart upload + final rename for atomic publish; learn the [Iceberg / Delta](advanced/lakehouse.md) abstractions before fighting raw S3 semantics.
- **Ignoring egress.** Reading from S3 in `us-east-1` to compute in `us-west-2` looks free until the bill arrives — $0.02/GB cross-region, $0.09/GB to the public internet. Co-locate compute and storage; lifecycle bronze to a region you don't move.
- **Reading too eagerly.** A Pandas / Polars `read_parquet("s3://big/*")` happily pulls 500 GB across the wire because that's what you asked for. Push filters into the storage layer (predicate pushdown), partition pruning, projection. Spark/DuckDB/Athena do this automatically *if you write the query correctly*.
- **One giant script.** Moving a 2000-line `submit.sh` to Airflow by `BashOperator`-wrapping it works for exactly one demo, then becomes the same script you tried to escape. Decompose into stages with explicit inputs and outputs first; *then* port.
- **Storing PHI in the wrong bucket.** Industry buckets have IAM, encryption-at-rest, audit logging, retention policies. The lab share has chmod. Treat every cross-cluster move of clinical data as an audit event — the IRB will eventually ask.
- **Forgetting that "infinite scale" still bills you.** Slurm enforces quota; clouds enforce credit cards. A bug that retries forever is a $40k incident if nobody set a budget alarm.
- **Mistaking K8s for Slurm.** Both schedule containers, but their primitives, failure modes, and observability are different. Don't try to "translate `sbatch` to K8s YAML" — learn K8s `Job`, `CronJob`, `Workflow` (Argo) as their own concepts.
- **Putting model weights in git.** Object storage exists; LFS exists; weights belong there. A 4 GB git repo will haunt you.
- **One environment for everything.** Industry separates dev / staging / prod with separate buckets, IAM roles, and pipelines. Promoting code from one to the next is a discipline; running production from your laptop because "it's just this once" is a story you'll tell in a postmortem.

## 11.7 A 3-6 month bridge plan

A concrete, sequenced plan from "Slurm-only" to "industry-credible". Each month is about ~10 hours/week of focused study + portfolio work, doable alongside a day job.

**Month 1 — DAG and idempotency on what you already own.**

- Port your existing pipeline to Snakemake (or Nextflow, or Dagster). Even if you keep submitting to Slurm, the DAG now lives outside `submit.sh`.
- Add the manifest-based idempotency contract from [DWI case study §4.4](dwi-case-study.md#44-idempotency-contract).
- Write the `runs` table from [§4.6](dwi-case-study.md#46-observability-what-you-wire-up-on-day-one).
- Deliverable: a public repo whose README says "this is a DAG with content-addressable idempotency", with one of the [exercises](exercises.md) as proof.

**Month 2 — Containers, CI, and a fixture subject.**

- Pin every container by digest, not tag.
- Build a fixture subject ([cicd.md §10.2](cicd.md#102-the-fixture-subject-your-most-important-asset)).
- Stand up the [GitHub Actions workflow](cicd.md#103-a-github-actions-workflow-that-pulls-its-weight) — lint, unit, dag-dryrun, integration, schema-diff.
- Deliverable: a PR that fails CI when you deliberately break a stage; passes when fixed.

**Month 3 — Cloud primitives.**

- Open an AWS or GCP account (free tier is enough for everything below).
- Move bronze (or a copy of it) to S3 / GCS.
- Run one stage on AWS Batch or GCP Batch instead of Slurm. Compare runtime and cost.
- Learn IAM enough to write a policy that grants exactly one bucket prefix + one container access, no more.
- Deliverable: a cohort run whose bronze is in S3 and whose one expensive stage ran on Batch.

**Month 4 — Infrastructure as code.**

- Stand up the same bucket + IAM + Batch job definition via Terraform or Pulumi.
- Destroy and re-create it from the IaC. The fact that you can is the deliverable.
- Read [Infrastructure as code](advanced/iac.md) for what to graduate to.

**Month 5 — A lakehouse table and a contract.**

- Replace your gold Parquet with an Iceberg or Delta table. Practice rollbacks via snapshot.
- Write a [data contract](advanced/data-contracts.md) for the gold table: schema, freshness, owner, on-call.
- Add a data-quality gate before promotion ([cicd.md §10.6](cicd.md#106-bluegreen-and-canary-for-data-pipelines)).
- Deliverable: a corrupted run that gets rejected by the gate.

**Month 6 — Observability and one polish.**

- Wire structured logs to a real aggregator (Loki on a single VM is fine).
- Build a Grafana dashboard on top of the `runs` table: throughput, p95 runtime per stage, $/subject.
- Write one runbook for your most common failure and have a labmate use it.
- Pick *one* polish: streaming intake, ephemeral PR environments, cost dashboard. Ship it.
- Deliverable: a README that ends with screenshots of the dashboard and a list of SLOs you actually meet.

At the end of six months, your repo demonstrates DAGs, idempotency, containers, CI, cloud compute, IaC, lakehouse tables, contracts, observability, and a defended SLO. That is what an industry hiring loop is looking for; nothing else needs to be on the CV. See [Portfolio roadmap](portfolio-roadmap.md) for the public-facing case-study framing of this plan and [Interviewing for senior DE roles](advanced/interviewing.md) for what the loop itself looks like.

## 11.8 A concrete porting exercise

Take a single Slurm submission and translate it. Side by side:

**HPC version (`array.sh`):**

```bash
#!/usr/bin/env bash
#SBATCH --array=1-150
#SBATCH --cpus-per-task=8
#SBATCH --mem=18G
#SBATCH --time=12:00:00
#SBATCH --output=logs/qsiprep_%A_%a.out

SUBJECT=$(sed -n "${SLURM_ARRAY_TASK_ID}p" subjects.txt)
apptainer run --bind ${BIDS}:/data qsiprep_0.23.1.sif \
    /data /out participant --participant-label ${SUBJECT} \
    --n_cpus 8 --mem_mb 16000
```

**Industry-flavoured version (Airflow, abbreviated):**

```python
# dags/qsiprep.py
from airflow.decorators import dag, task
from airflow.providers.cncf.kubernetes.operators.pod import KubernetesPodOperator
from datetime import datetime

@dag(schedule="@daily", start_date=datetime(2026, 1, 1), catchup=False)
def qsiprep_cohort():
    subjects = task(read_subjects_from_s3)("s3://cohort/bronze/subjects.txt")

    @task
    def run_one(subject_id: str):
        return KubernetesPodOperator(
            task_id=f"qsiprep_{subject_id}",
            image="ghcr.io/pennlinc/qsiprep:0.23.1",
            cmds=["qsiprep", "/data", "/out", "participant",
                  "--participant-label", subject_id, "--n_cpus", "8"],
            container_resources={"requests": {"cpu": "8", "memory": "18Gi"}},
            retries=2, retry_delay=300,
        ).execute({})

    run_one.expand(subject_id=subjects)
```

Same DAG, same container, same idempotency requirement. What changed: who schedules it, where logs and metrics flow, how retries are declared, who owns the SLO. Notice that the *scientific* content — the QSIPrep flags — is byte-identical. That's the bridge.

## 11.9 The honest summary

You can become an industry-credible data engineer without leaving your cluster by adding, in this order:

1. A real DAG tool (Snakemake or Dagster) — not bash glue.
2. Content-addressable idempotency (manifests with input/container/code hashes).
3. A `runs` table in DuckDB or Postgres that an SLO query can hit.
4. Object storage for the gold layer (even MinIO on a single node teaches the lesson).
5. A runbook for each of the top three failure modes.
6. A CI pipeline that runs the whole DAG on a fixture subject (see [CI/CD](cicd.md)).

Do those six and the rest is vocabulary.

## References

1. **Reis J, Housley M.** *Fundamentals of Data Engineering.* O'Reilly; 2022.
2. **Kleppmann M.** *Designing Data-Intensive Applications.* O'Reilly; 2017.
3. **Köster J, Rahmann S.** Snakemake — a scalable bioinformatics workflow engine. *Bioinformatics.* 2012;28(19):2520–2522. [doi:10.1093/bioinformatics/bts480](https://doi.org/10.1093/bioinformatics/bts480)
4. **Yoo AB, Jette MA, Grondona M.** SLURM: simple Linux utility for resource management. *JSSPP.* 2003. [doi:10.1007/10968987_3](https://doi.org/10.1007/10968987_3)
5. **Zaharia M, Chowdhury M, Franklin MJ, et al.** Spark: cluster computing with working sets. *HotCloud.* 2010.
6. **Moritz P, Nishihara R, Wang S, et al.** Ray: a distributed framework for emerging AI applications. *OSDI.* 2018. [arXiv:1712.05889](https://arxiv.org/abs/1712.05889)
7. **Di Tommaso P, Chatzou M, Floden EW, et al.** Nextflow enables reproducible computational workflows. *Nature Biotechnology.* 2017;35:316–319. [doi:10.1038/nbt.3820](https://doi.org/10.1038/nbt.3820)
8. **Wilkinson MD, Dumontier M, Aalbersberg IJ, et al.** FAIR Guiding Principles for scientific data management and stewardship. *Scientific Data.* 2016;3:160018. [doi:10.1038/sdata.2016.18](https://doi.org/10.1038/sdata.2016.18)
9. **Beam AL, Manrai AK, Ghassemi M.** Challenges to the reproducibility of machine learning models in health care. *JAMA.* 2020;323(4):305–306. [doi:10.1001/jama.2019.20866](https://doi.org/10.1001/jama.2019.20866)
10. **Lambin P, Leijenaar RTH, Deist TM, et al.** Radiomics: the bridge between medical imaging and personalized medicine. *Nature Reviews Clinical Oncology.* 2017;14:749–762. [doi:10.1038/nrclinonc.2017.141](https://doi.org/10.1038/nrclinonc.2017.141)

## Where to next

- [Portfolio roadmap](portfolio-roadmap.md) — concrete, weekend-sized milestones that turn a working bash pipeline into a strong DE portfolio piece.
- [Tooling landscape](tooling.md) — the orchestrators, compute substrates, and storage layers referenced above, in one map.
- [CI/CD](cicd.md) — how the industry side does testing and deploy that an HPC repo usually skips.
- [Reliability & operations](reliability.md) — SLOs, runbooks, and the on-call habits that mark the cultural difference.
