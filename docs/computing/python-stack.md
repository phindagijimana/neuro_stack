# Python scientific stack

> The packages every neuroimaging Python project ends up importing — and the package manager that won't fight you.

## The unavoidable core

- **`numpy`** — every n-dimensional array.
- **`scipy`** — interpolation, optimisation, statistics, sparse linear algebra.
- **`pandas`** / **`polars`** — tabular data.
- **`matplotlib`** + **`seaborn`** — plots.
- **`scikit-learn`** — classical ML.

## Neuroimaging specifics

- **[`nibabel`](https://nipy.org/nibabel/)** — read/write every imaging format you'll meet (NIfTI, GIFTI, CIFTI, MGH, etc.).
- **[`nilearn`](https://nilearn.github.io)** — high-level fMRI analysis, statistical maps, plotting, masking.
- **[`pybids`](https://bids-standard.github.io/pybids/)** — query a BIDS dataset.
- **[`dipy`](https://dipy.org)** — diffusion MRI methods (registration, reconstruction, tractography).
- **[`mne`](https://mne.tools)** — MEG/EEG analysis (also surface-based; useful even for non-MEG work).
- **[`templateflow`](https://www.templateflow.org)** — versioned standard templates (MNI, fsaverage, fsLR).
- **[`pydicom`](https://pydicom.github.io/pydicom/stable/)** — read DICOM if you must.

## Deep learning specifics

- **`torch`** + **`torchvision`** — the default training framework.
- **[`MONAI`](https://monai.io)** — medical-imaging-aware extension. Use it unless you have a specific reason.
- **`accelerate`** + **`bitsandbytes`** — multi-GPU and quantisation.

## Package managers

| Tool | When |
| --- | --- |
| **`pip`** + `venv` | Pure-Python projects, simple environments |
| **`conda`** / **`mamba`** | When you need non-Python binaries (FSL, FreeSurfer Python wrappers, NumPy with MKL) |
| **`uv`** | New, fast, pip-compatible. Default for greenfield projects in 2026. |
| **`pixi`** | Conda-flavoured but reproducible by default; growing adoption in scientific Python |

For a brand-new project, the sane defaults are:

1. **`uv`** if you only need Python packages.
2. **`pixi`** or **`mamba`** if you need binaries (e.g., FSL via the `bioconda` channel).
3. Always commit a lockfile (`uv.lock`, `pixi.lock`, `conda-lock`).

## A minimal `pyproject.toml` for a neuroimaging project

```toml
[project]
name = "my_neuro_project"
version = "0.1.0"
requires-python = ">=3.10"
dependencies = [
    "numpy>=1.26",
    "scipy>=1.13",
    "pandas>=2.2",
    "nibabel>=5.2",
    "nilearn>=0.10.4",
    "pybids>=0.16",
    "matplotlib>=3.8",
]

[project.optional-dependencies]
dev = ["pytest>=8.0", "ruff>=0.5"]
dl = ["torch>=2.4", "monai>=1.4"]
```

Pin major versions. Update intentionally, on a schedule, with the test suite as the safety net.

## Where to next

[Containers](containers.md) — for everything that isn't pure Python.
