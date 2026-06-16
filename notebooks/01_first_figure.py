# ---
# jupyter:
#   jupytext:
#     formats: py:percent
# ---

# %% [markdown]
# # First figure
#
# Companion notebook for [Getting Started → first figure](../docs/getting-started/first-figure.md).

# %%
from pathlib import Path

import matplotlib.pyplot as plt
import seaborn as sns
from nilearn import datasets, plotting

sns.set_theme(context="paper", style="whitegrid", font_scale=1.1)
Path("figs").mkdir(exist_ok=True)

# %% [markdown]
# ## A. Ortho cuts of MNI152

# %%
mni = datasets.load_mni152_template()
fig = plotting.plot_anat(
    mni, display_mode="ortho", cut_coords=(0, 0, 0),
    title="MNI152 — orthogonal view", annotate=True,
)
fig.savefig("figs/mni152_ortho.png", dpi=300, bbox_inches="tight")
fig.close()

# %% [markdown]
# ## B. Overlay a parcellation

# %%
atlas = datasets.fetch_atlas_destrieux_2009()
plotting.plot_roi(
    atlas["maps"], bg_img=mni,
    title="Destrieux atlas on MNI152",
    output_file="figs/atlas_overlay.png", cmap="tab20",
)

# %% [markdown]
# ## C. Glass-brain projection

# %%
plotting.plot_glass_brain(
    mni, threshold=None, display_mode="lzry",
    title="Glass brain projections",
    output_file="figs/glass_brain.png",
)

print("Saved figs/ — open the .png files to inspect.")
