# Computing environment

> What you actually need on your machine — or your cluster account, or your cloud project — to do neuroimaging work that other people can reproduce.

Neuroimaging code is computationally heavy and dependency-fragile. A "works on my laptop" pipeline that doesn't run on the cluster is a research-integrity problem, not just a logistics one. This section is about getting the environment right from day one and keeping it right as the project grows.

It's written for someone who can already write Python but hasn't yet had to put a pipeline behind a job scheduler, ship it in a container, or hand it to a collaborator on another continent. Hardware vendors and cloud providers change every year; the principles here do not.

## Section map

<div class="grid cards" markdown>

-   :material-language-python: **[Python scientific stack](python-stack.md)** — `numpy`, `scipy`, `nibabel`, `nilearn`, `pybids`, `dipy`, `mne`; choosing between `conda` / `mamba` / `uv` / `pip`.

-   :material-docker: **[Containers (Docker, Apptainer)](containers.md)** — why every modern pipeline ships as a container, and how to run them on HPC where Docker is forbidden.

-   :material-server-network: **[HPC and Slurm](hpc-slurm.md)** — the standard scheduler, array jobs, GPU partitions, queue etiquette.

-   :material-cloud: **[Cloud (AWS / GCP / Azure)](cloud.md)** — when to leave HPC, common patterns, the egress-cost trap.

-   :material-expansion-card: **[GPUs and accelerators](gpus.md)** — CUDA / cuDNN / driver dance, multi-GPU training, picking an instance type.

-   :material-code-tags: **[Editor and IDE setup](editor.md)** — VS Code Remote, Jupyter, the small productivity wins that compound.

-   :material-package-variant: **[Dependency management](dependencies.md)** — lockfiles, virtual envs, pinning, the "what's the actual FSL version on this node" problem.

-   :material-check-decagram: **[Reproducibility checklist](reproducibility.md)** — a short pre-publication audit that catches most "I can't rerun this" issues.

</div>

## Read this section before...

...you start coding on a new machine, ...you submit your first cluster job, ...you containerise a pipeline for a collaborator, or ...you write the *Computing environment* paragraph of a methods section. Half of it is one-time setup; the other half is operational discipline that pays off over years.

## What this section does *not* cover

- **Imaging-specific algorithms.** Those live in [Analysis](../analysis/index.md) and [AI / ML](../ai/index.md).
- **Pipeline orchestration design** (DAGs, idempotency, observability). That's [Data engineering](../data-engineering/index.md). This section is about the *substrate* the orchestrator runs on.
- **Vendor-specific procurement advice.** GPU model numbers and cloud instance families change yearly; the principles for choosing one do not.

The dividing line: this section is about the environment your code runs in, not the code itself.

## Reading order

=== "Beginner"

    Goal: a single workstation where you can run a small pipeline and edit code comfortably.

    1. [Python scientific stack](python-stack.md)
    2. [Editor and IDE setup](editor.md)
    3. [Containers](containers.md) — at least know how to *run* one.
    4. [Reproducibility checklist](reproducibility.md) — read once even if you don't apply everything yet.

    That's enough to do real work locally and on a single remote machine.

=== "Intermediate"

    Goal: production-grade pipelines on a shared cluster.

    1. [HPC and Slurm](hpc-slurm.md)
    2. [Dependency management](dependencies.md) — the moment two people share the codebase.
    3. [Containers](containers.md) revisited — building, not just running.
    4. [GPUs and accelerators](gpus.md) if you're training models.

    At this stage you should be writing job scripts and container recipes that someone else can rerun unchanged.

=== "PhD / specialist"

    Goal: scale, cost-control, and long-term reproducibility for a programme of work.

    1. [Cloud](cloud.md) — when HPC stops scaling or the data lives in S3.
    2. [GPUs and accelerators](gpus.md) in depth — multi-GPU, mixed precision, profiling.
    3. [Reproducibility checklist](reproducibility.md) applied to a full study.
    4. The [Data engineering](../data-engineering/index.md) section — orchestration, observability, and operations.

    Specialists own the environment, not just the code that runs in it.

## Where to next

Once the environment is solid, point it at [BIDS](../bids/index.md) and [Analysis](../analysis/index.md) for the imaging-specific work, or move into [Data engineering](../data-engineering/index.md) for the orchestration layer above.
