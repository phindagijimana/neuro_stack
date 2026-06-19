# Visualisation and EDA

> The tools you'll actually open when something goes wrong with a pipeline, a model, or a paper figure. Viewers, plotting libraries, and QC dashboards — with an opinion on each.

EDA on imaging is different from EDA on tabular data because **a histogram of voxel intensities is rarely the thing that tells you the truth**. A bad mask is obvious in a viewer and invisible in summary statistics. The tools below are organised by what you're looking at — a volume, a surface, a connectome, or a cohort.

## Volume viewers

You need one heavyweight viewer for editing and labelling, one lightweight one for snapshots, and ideally one programmatic one for figures.

| Tool | Best at | Watch out for |
| --- | --- | --- |
| **ITK-SNAP** | Quick manual segmentation; semi-automatic snake tools | Older OpenGL on some clusters; X11 forwarding can crawl |
| **3D Slicer** | Everything; extensions for DICOM, registration, ML | Heavy install; steep learning curve |
| **FSLeyes** | Fast NIfTI / GIFTI / CIFTI overlay viewer | FSL-centric defaults; mind the colour-map gotchas |
| **MRIcroGL** | One-shot screenshots; pretty 3D renders | Less suited for editing |
| **Freeview** | FreeSurfer outputs (surfaces + volumes together) | FreeSurfer install required |

A practical layout most labs converge on:

- **ITK-SNAP** for manual edits and label QC. The active-contour ("snake") tools save real time on lesion masks.
- **FSLeyes** for "open this overlay against MNI quickly". It also reads CIFTI, which is uncommon.
- **MRIcroGL** when a non-imaging collaborator needs a screenshot.
- **3D Slicer** when you need DICOM ingestion, registration, or one of its hundreds of extensions.

```bash
# Open a fMRIPrep output against MNI in FSLeyes
fsleyes ${TEMPLATEFLOW_HOME}/tpl-MNI152NLin2009cAsym/tpl-MNI152NLin2009cAsym_res-01_T1w.nii.gz \
        sub-001/func/sub-001_task-rest_space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz \
        --cmap red-yellow
```

## Surface viewers

The moment you leave volumetric space, the viewer list narrows to two real options.

| Tool | Best at | Notes |
| --- | --- | --- |
| **Connectome Workbench (`wb_view`)** | CIFTI / GIFTI on fs_LR; HCP-style figures | The right answer for surface-based fMRI work |
| **Freeview** | FreeSurfer's fsaverage / individual surfaces | Tighter integration with `recon-all` outputs |

Workbench is the more polished tool for figures and the harder one to install correctly. Freeview ships with FreeSurfer and is the path of least resistance if you're already running `recon-all`. See [Analysis → Surface-based analysis](../analysis/surface.md) for the underlying space conventions.

## Programmatic plotting

This is where most production figures actually come from. The four libraries below cover 90% of neuroimaging plotting needs.

### Nilearn plotting

The default for axial/sagittal/coronal montages, glass brains, and surface projections from Python.

```python
from nilearn import plotting, datasets

stat_map = "results/group/zstat1.nii.gz"
plotting.plot_stat_map(
    stat_map,
    bg_img=datasets.load_mni152_template(),
    threshold=3.1,
    display_mode="ortho",
    output_file="figures/group_zstat1.png",
    dpi=200,
)
```

When to reach for it: any figure that needs to land in a paper without a 2-hour Inkscape session. It handles thresholding, colour maps, and MNI alignment by default.

### surfplot / brainspace

For publication-quality cortical surface figures with multiple views (lateral/medial × left/right) on one canvas. `surfplot` is the more opinionated wrapper; `brainspace` is the substrate.

```python
from surfplot import Plot
from neuromaps.datasets import fetch_fslr

surfaces = fetch_fslr()
p = Plot(surfaces["inflated"][0], surfaces["inflated"][1], size=(800, 400))
p.add_layer(my_map_lh, my_map_rh, cmap="viridis", color_range=(0, 1))
p.build().savefig("figures/surface.png", dpi=300)
```

When to reach for it: any time the figure needs to show both hemispheres and both medial/lateral views without manual compositing.

### Plotly for connectomes

For interactive 3D connectome plots — circular ideograms, force-directed layouts, or 3D node-edge graphs you can rotate. Static connectomes are easier in Nilearn's `plot_connectome`; interactive ones belong in Plotly or `pyvis`.

```python
import plotly.graph_objects as go
# nodes: (x, y, z); edges: list of (i, j, weight)
fig = go.Figure([
    go.Scatter3d(x=nodes[:, 0], y=nodes[:, 1], z=nodes[:, 2], mode="markers"),
    go.Scatter3d(x=edge_x, y=edge_y, z=edge_z, mode="lines",
                 line=dict(width=2, color="rgba(80,80,200,0.4)")),
])
fig.write_html("figures/connectome.html")
```

When to reach for it: collaborator demos, supplementary HTML, anything where someone will ask "can I see that from the other side?".

## QC dashboards

QC is where viz tools meet pipelines. The choice is "use a standard report or build your own" — and for the standard cases the standard reports are excellent.

| Tool | What it is | When to use |
| --- | --- | --- |
| **MRIQC** | BIDS-app that computes ~100 QC metrics + per-subject HTML reports | Always, on every cohort, before any analysis |
| **fMRIPrep reports** | Per-subject HTML emitted by fMRIPrep | Review every subject; don't trust group stats until you have |
| **Custom Streamlit / Dash** | Cohort-level dashboards over derived metrics | When the standard reports don't slice the way you need |
| **PyBIDS + Jupyter** | Ad-hoc cohort EDA notebooks | First-pass exploration; not a deliverable |

The MRIQC + fMRIPrep report combo is essentially **free QC** for the most common modalities. If you skip it you will spend three times as long debugging analysis-stage problems that were already visible in the report.

For cohort-level dashboards, the pattern most labs converge on:

```python
# qc_dashboard.py — minimal Streamlit cohort QC
import streamlit as st
import polars as pl
from pathlib import Path

df = pl.read_parquet("derivatives/qc/cohort_qc.parquet")

st.title("Cohort QC")
st.metric("Subjects", df["subject"].n_unique())
st.metric("Sessions", df.height)

fail = df.filter(pl.col("fd_mean") > 0.5)
st.subheader(f"High-motion sessions (FD > 0.5 mm): {fail.height}")
st.dataframe(fail.select(["subject", "session", "task", "fd_mean", "tsnr"]))

site = st.selectbox("Site", df["site"].unique().to_list())
st.bar_chart(df.filter(pl.col("site") == site).select(["fd_mean"]))
```

This kind of dashboard belongs alongside the pipeline, not after it — wire it into the [DAG](../data-engineering/dag.md) so it rebuilds whenever derivatives change.

## Notebook viz patterns

In notebooks, two patterns cover most needs:

**Pattern 1 — `matplotlib` + `nilearn` for static figures.** Reproducible, version-controlled, paper-ready. Default for anything that will end up in a manuscript.

```python
import matplotlib.pyplot as plt
from nilearn import plotting

fig, axes = plt.subplots(1, 2, figsize=(12, 4))
plotting.plot_stat_map("zstat1.nii.gz", axes=axes[0], title="Run 1")
plotting.plot_stat_map("zstat2.nii.gz", axes=axes[1], title="Run 2")
fig.savefig("fig2.pdf", bbox_inches="tight")
```

**Pattern 2 — `niwidgets` / `itkwidgets` for interactive in-notebook scrubbing.** Useful for live demos and one-off "let me check this volume" moments. Don't ship widgets in shared notebooks — they're noisy in version control and brittle in Colab.

```python
from niwidgets import NiftiWidget
NiftiWidget("sub-001_T1w.nii.gz").nifti_plotter()
```

If a teammate needs to interact with a volume, sending them an ITK-SNAP session is usually cleaner than sending a notebook.

## Picking a stack

A defensible default stack for a small lab:

- **Viewer:** ITK-SNAP for editing, FSLeyes for quick overlays, MRIcroGL for screenshots.
- **Surfaces:** Connectome Workbench if you do surface-based work, Freeview otherwise.
- **Plotting:** Nilearn for volumes, surfplot for surfaces, Plotly for interactive supplementary figures.
- **QC:** MRIQC + fMRIPrep reports as table stakes, Streamlit for cohort-level summaries.

Replace any of these only when you have a specific reason — most "alternative" tools cost more to learn than they save in any single project.

---

## References

1. **Esteban O, Birman D, Schaer M, et al.** MRIQC: advancing the automatic prediction of image quality in MRI from unseen sites. *PLoS One.* 2017;12:e0184661. [doi:10.1371/journal.pone.0184661](https://doi.org/10.1371/journal.pone.0184661)
2. **Abraham A, Pedregosa F, Eickenberg M, et al.** Machine learning for neuroimaging with scikit-learn (Nilearn). *Front Neuroinform.* 2014;8:14. [doi:10.3389/fninf.2014.00014](https://doi.org/10.3389/fninf.2014.00014)
3. **Marcus DS, Harwell J, Olsen T, et al.** Informatics and data mining tools and strategies for the Human Connectome Project (Workbench). *Front Neuroinform.* 2011;5:4. [doi:10.3389/fninf.2011.00004](https://doi.org/10.3389/fninf.2011.00004)
4. **Yushkevich PA, Piven J, Hazlett HC, et al.** User-guided 3D active contour segmentation (ITK-SNAP). *NeuroImage.* 2006;31:1116-28. [doi:10.1016/j.neuroimage.2006.01.015](https://doi.org/10.1016/j.neuroimage.2006.01.015)
5. **Fedorov A, Beichel R, Kalpathy-Cramer J, et al.** 3D Slicer as an image computing platform for the quantitative imaging network. *Magn Reson Imaging.* 2012;30:1323-41. [doi:10.1016/j.mri.2012.05.001](https://doi.org/10.1016/j.mri.2012.05.001)
6. **Vos de Wael R, Benkarim O, Paquola C, et al.** BrainSpace: a toolbox for the analysis of macroscale gradients. *Commun Biol.* 2020;3:103. [doi:10.1038/s42003-020-0794-7](https://doi.org/10.1038/s42003-020-0794-7)

## Where to next

- [Clinical deployment](clinical-deployment.md) — viz that moves out of notebooks and into the clinical workflow.
- [Decision trees](decision-trees.md) — the upstream tool choices that determine what you'll be plotting.
- [Analysis → Surface-based analysis](../analysis/surface.md) — the conventions the surface viewers assume.
