# Tools landscape

> Opinionated map of the tools you'll meet — what they do and when to reach for each, with **official documentation links** so you can jump straight to the source.

This page is a quick index organised by what the tool *does* rather than where it sits in the stack. Each row links to the canonical documentation and (where one exists) to a deeper treatment elsewhere in the handbook.

!!! note "How to read this section"
    Tables on this page are the **catalogue** — names, one-liners, and when-to-pick notes. The companion pages turn that catalogue into decisions:

    - **[Decision trees](decision-trees.md)** — flowcharts for the five choices that bite teams hardest (orchestrator, storage, DICOM converter, preprocessing pipeline, DL framework).
    - **[Visualisation and EDA](viz-and-eda.md)** — viewers, plotting libraries, and QC dashboards, with opinions on when to reach for each.
    - **[Clinical deployment](clinical-deployment.md)** — DICOM I/O, PACS bridges, inference servers, and the regulatory wrappers around them.

    If you're new to the stack, skim the tables here first, then jump to the decision-tree page for the calls you actually have to make this week.

## Neuroimaging-specific

The neuroimaging-specific tools are mostly **non-substitutable** — they encode domain knowledge (BIDS layout, surface topology, diffusion modeling) that generic tools don't have. The real choices are between a few canonical options per task:

- **DICOM → NIfTI:** `dcm2niix` is the engine; `HeuDiConv` and `Dcm2Bids` are the BIDS-layout wrappers on top. Pick by team size and how stable your scan protocol is — see [Decision trees → Which DICOM converter?](decision-trees.md#which-dicom-converter).
- **Cortical surfaces:** FreeSurfer is the citation-weighted default; FastSurfer is the deep-learning drop-in when you have GPUs and need throughput.
- **Preprocessing:** BIDS apps (fMRIPrep, QSIPrep, sMRIPrep) are the path of least resistance and the right default. Roll your own only when you have a specific reason — see [Decision trees → Which preprocessing pipeline?](decision-trees.md#which-preprocessing-pipeline).

| Tool | What it does | Notes |
| --- | --- | --- |
| **dcm2niix** | DICOM → NIfTI conversion | The de-facto standard; embeds BIDS-friendly sidecars. |
| **HeuDiConv / Dcm2Bids** | Build a BIDS dataset from DICOM | Heuristic-driven; pick HeuDiConv for institutional repeatability, Dcm2Bids for one-off conversions. |
| **BIDS Validator** | Check a dataset against the BIDS spec | Run before *any* pipeline. |
| **FreeSurfer** (`recon-all`) | Cortical surface reconstruction, parcellations | Slow (≈10 h / subject); FastSurfer is the DL-accelerated drop-in. |
| **fMRIPrep / QSIPrep / sMRIPrep** | BIDS-app preprocessing | Standardised, container-shipped; outputs are reusable across downstream analyses. |
| **MRtrix3** | Diffusion modeling, tractography | Workhorse for DWI streamlines and FOD-based methods. |
| **ANTs / FSL / AFNI** | Registration, segmentation, fMRI stats | Mature, well-cited, slower-moving. |
| **Nilearn** | Python analytics on NIfTI / Niimg | Best Python entry point if you're coming from scikit-learn. |
| **PyBIDS** | Programmatic BIDS access | Use it instead of writing glob patterns. |
| **TemplateFlow** | Versioned standard templates | Pin versions in your pipeline. |

## Workflow orchestrators

Orchestrators differ along three axes: **how they model a job** (file targets vs channels vs assets), **how they scale** (HPC scheduler vs Kubernetes vs managed cloud), and **what they assume about your team** (Python-only vs polyglot, scientific vs warehouse). For a neuroimaging lab on Slurm with mostly Python tools, the default is Snakemake. For a translational team that already runs Nextflow on bioinformatics pipelines, keep using it. The full decision lives in [Decision trees → Which orchestrator?](decision-trees.md#which-orchestrator-for-my-lab).

| Tool | Strength | When to pick |
| --- | --- | --- |
| **Snakemake** | File-target rules; native HPC integration | Best fit for neuroimaging on Slurm. |
| **Nextflow** | Containerised, channel-based; massive bioinformatics adoption | When your team already uses it. |
| **Airflow** | Time-based scheduling; huge ecosystem | Tabular / warehouse-centric pipelines. |
| **Dagster** | Asset-based mental model; strong typing | Modern data platforms, software-defined assets. |
| **Prefect** | Pythonic; flexible deployment | Lighter weight than Airflow. |
| **Argo Workflows** | Kubernetes-native | When the rest of the stack is on K8s. |

## Storage layers

Storage choices follow data volume and access pattern, not preference. POSIX is fastest within a node and miserable across one; object storage is the inverse. Lakehouse table formats sit on top of object stores to give you ACID and time travel without the warehouse price tag. For neuroimaging specifically, DataLad is the only tool that treats *datasets* as first-class versioned objects rather than blobs to back up. See [Decision trees → Which storage layer?](decision-trees.md#which-storage-layer) for the full call.

| Tool | What | Notes |
| --- | --- | --- |
| **POSIX filesystem** | Plain files | What HPC clusters give you. Fast within a node, painful across. |
| **S3 / GCS / Azure Blob** | Object storage | Cloud default; cheap at rest, network-egress costs bite. |
| **Parquet** | Columnar file format | The lingua franca of analytical data. |
| **Iceberg / Delta / Hudi** | Table formats on top of Parquet | ACID transactions, time-travel, schema evolution. See [Lakehouse internals](../data-engineering/advanced/lakehouse.md). |
| **DataLad** | Git-annex for datasets | The neuroimaging-native versioning answer. |
| **DICOM PACS** | Clinical image archives | Where data starts; rarely where it lives during research. |

## Analytics & transformation

For cohort-scale tabular work (subjects, sessions, derived metrics), the modern Python default is **DuckDB + Polars**: in-process, columnar, fast on a laptop, and they speak Parquet natively. Reach for Spark only when the data genuinely does not fit on one machine — which for neuroimaging derivatives is rarer than people assume. dbt earns its keep when SQL transformations need version control, tests, and lineage; see [dbt deeply](../data-engineering/advanced/dbt.md).

| Tool | When |
| --- | --- |
| **DuckDB** | In-process SQL on Parquet / CSV. Excellent for cohort summaries. |
| **Polars** | Fast single-node DataFrames. |
| **Pandas** | Familiar, ubiquitous, slower at scale. |
| **Spark / PySpark** | When the data doesn't fit on one machine. See [Spark](../data-engineering/advanced/spark.md). |
| **dbt** | SQL transformations with version control, tests, lineage. See [dbt](../data-engineering/advanced/dbt.md). |

## Visualisation & EDA

Volume viewers, surface viewers, programmatic plotting, and QC dashboards each have a clear best-in-class for the common cases. The pairing most labs settle on is **ITK-SNAP** for quick volumetric edits, **Connectome Workbench** for surfaces, **Nilearn plotting** in notebooks, and **MRIQC** for cohort-scale QC. See [Visualisation and EDA](viz-and-eda.md) for the full breakdown.

## Clinical deployment

Once a model leaves the lab, the tool list changes: DICOM libraries, PACS bridges, inference servers, FHIR for orders/results, and DICOM SR for structured outputs. Most of these are commercial-adjacent — pick the open option that matches your regulatory posture. See [Clinical deployment](clinical-deployment.md).

## Experiment tracking & MLOps

Once you're training models the catalogue of tools you actually need is small. The split between **experiment tracking** (per-run metrics, artifacts, configs) and **model registry / serving** (versioned models, deployment) is where most teams either pick a single platform or stitch two together.

| Tool | What it does | Notes |
| --- | --- | --- |
| **Weights & Biases** | Tracking + sweeps + reports | Best UX; SaaS by default, self-host available |
| **MLflow** | Tracking + registry + serving | The open-source default; runs anywhere |
| **TensorBoard** | Local metrics + tensor visualisations | Use alongside W&B / MLflow, not instead |
| **DVC** | Data + model versioning on git | Pairs with DataLad-style provenance |
| **Hugging Face Hub** | Model + dataset hosting + cards | Increasingly used for foundation-model checkpoints |

See [Data engineering → MLOps](../data-engineering/advanced/mlops.md) for how these fit into a production stack.

## Observability

Observability is the part that's almost identical to a generic data platform. Lift these patterns from industry rather than inventing them.

| Layer | Tool |
| --- | --- |
| Logs | Loki, ELK, Datadog Logs |
| Metrics | Prometheus + Grafana, Datadog |
| Traces | OpenTelemetry, Jaeger, Tempo |
| Lineage | OpenLineage + Marquez, DataHub, Atlan |
| Data quality | Great Expectations, Pandera, Soda |

---

## References

1. **Gorgolewski KJ, Auer T, Calhoun VD, et al.** The brain imaging data structure (BIDS). *Sci Data.* 2016;3:160044. [doi:10.1038/sdata.2016.44](https://doi.org/10.1038/sdata.2016.44)
2. **Esteban O, Markiewicz CJ, Blair RW, et al.** fMRIPrep: a robust preprocessing pipeline for functional MRI. *Nat Methods.* 2019;16:111-116. [doi:10.1038/s41592-018-0235-4](https://doi.org/10.1038/s41592-018-0235-4)
3. **Halchenko YO, Goncalves M, Castello MVD, et al.** HeuDiConv — flexible DICOM conversion into structured directory layouts. *J Open Source Softw.* 2024. [doi:10.21105/joss.05839](https://doi.org/10.21105/joss.05839)
4. **Mölder F, Jablonski KP, Letcher B, et al.** Sustainable data analysis with Snakemake. *F1000Res.* 2021;10:33. [doi:10.12688/f1000research.29032.2](https://doi.org/10.12688/f1000research.29032.2)
5. **Di Tommaso P, Chatzou M, Floden EW, et al.** Nextflow enables reproducible computational workflows. *Nat Biotechnol.* 2017;35:316-319. [doi:10.1038/nbt.3820](https://doi.org/10.1038/nbt.3820)

## Where to next

- [Decision trees](decision-trees.md) — flowcharts for the choices teams agonise over.
- [Visualisation and EDA](viz-and-eda.md) — viewers, plotting, and QC dashboards.
- [Clinical deployment](clinical-deployment.md) — moving models from notebooks to scanners.

This is a starting map, not an exhaustive catalogue. Tools change; the *categories* don't.
