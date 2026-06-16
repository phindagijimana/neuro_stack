# dwi_pipeline_ref — reference implementation

A minimal but real implementation of the DWI cohort pipeline described in [Data engineering → Portfolio roadmap](../../docs/data-engineering/portfolio-roadmap.md). The goal is *executable code you can read*, not a competitor to QSIPrep.

## What's in here

```text
examples/dwi_pipeline_ref/
├── README.md               # this file
├── Snakefile               # DAG of the pipeline stages
├── config.yaml             # subjects, paths, containers
├── Makefile                # convenience targets
├── envs/
│   └── env.yaml            # conda env for snakemake-managed deps
├── scripts/
│   ├── extract_metrics.py  # per-subject feature extraction
│   ├── aggregate_cohort.py # merge into a cohort table
│   ├── emit_manifest.py    # per-subject observability manifest
│   └── make_report.py      # cohort QC HTML report
└── tests/
    └── test_extract.py     # unit tests for the helpers
```

## What it demonstrates

The five pillars the handbook talks about, made tangible:

- **Orchestration** — Snakemake DAG.
- **Idempotency** — each rule has declared `output:` files; reruns skip completed work.
- **Isolation** — container directives per rule.
- **Observability** — per-subject `manifest.json` emitted by every stage.
- **Configuration** — `config.yaml` parameterises everything.

Plus:

- **Testing** — `pytest` over the Python helpers; `snakemake -n` dry-run in CI.
- **Reproducibility** — pinned container tags + lockfile.

## Run it

```bash
# From repo root, with .venv activated and snakemake installed
pip install snakemake>=8

cd examples/dwi_pipeline_ref
snakemake -n               # dry-run; shows what would execute
snakemake --cores 4        # actually run
snakemake report.html      # provenance report
```

On a Slurm cluster:

```bash
snakemake --executor slurm --jobs 50 --use-singularity
```

## Adapt to your cohort

1. Edit `config.yaml`:

    ```yaml
    bids_root: /path/to/your/bids
    derivatives_root: /path/to/derivatives
    container_root: /path/to/containers
    subjects:
      - sub-001
      - sub-002
    ```

2. Make sure each subject already has QSIPrep + QSIRecon outputs (this reference pipeline starts at the analysis layer; the QSIPrep step is a separate BIDS-app run).

3. `snakemake --cores N`.

## Where this fits in the handbook

This implementation closes the gap between *reading about* the portfolio roadmap and *building* it. Read along with [Data engineering → Portfolio roadmap](../../docs/data-engineering/portfolio-roadmap.md) and [Computing → HPC and Slurm](../../docs/computing/hpc-slurm.md).
