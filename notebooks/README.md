# Notebooks

Runnable companion notebooks for the [Tutorials section](../docs/tutorials/index.md).

## Format

Each notebook is committed as a **jupytext percent-format `.py` file** so it diffs cleanly in git. To open as a real Jupyter notebook:

```bash
pip install jupytext jupyterlab
jupytext --to ipynb 00_first_nifti.py        # one-time conversion
jupyter lab 00_first_nifti.ipynb
```

Or open the `.py` file directly in VS Code / PyCharm / JupyterLab — the percent cells render as notebook cells automatically.

To round-trip (edit either side, sync the other):

```bash
jupytext --set-formats py:percent,ipynb 00_first_nifti.py
jupytext --sync 00_first_nifti.py
```

## Notebooks shipped

| File | Tutorial | Runtime |
|---|---|---|
| `00_first_nifti.py` | [Getting Started → first NIfTI](../docs/getting-started/first-nifti.md) | ~5 min |
| `01_first_figure.py` | [Getting Started → first figure](../docs/getting-started/first-figure.md) | ~5 min |
| `02_dwi_cohort.py` | [Tutorials → DWI cohort](../docs/tutorials/dwi-cohort.md) | hours |
| `03_fmri_glm.py` | [Tutorials → fMRI GLM](../docs/tutorials/fmri-glm.md) | ~1 h |
| `04_cortical_thickness_ml.py` | [Tutorials → cortical thickness ML](../docs/tutorials/cortical-thickness-ml.md) | ~30 min |
| `05_lesion_segmentation.py` | [Tutorials → lesion segmentation](../docs/tutorials/lesion-segmentation.md) | GPU hours |
| `06_capstone.py` | [Capstone — DICOM to figure](../docs/tutorials/capstone.md) | full day |
| `07_multimodal.py` | [Tutorials → multimodal image+text](../docs/tutorials/multimodal-image-text.md) | GPU hours |

## Dependencies

```bash
pip install -e "..[dev,docs,neuro]"
pip install jupytext jupyterlab seaborn nilearn nibabel pandas
```

For deep-learning notebooks add `torch` and `monai`. For multi-GPU training you need a working CUDA install.

## Data

Notebooks fetch their own small example data from public sources (Nilearn datasets, OpenNeuro) or use the bundled `../fixtures/sub-tiny/` skeleton. Real lab data is never committed.
