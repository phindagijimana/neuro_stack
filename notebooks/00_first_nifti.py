# ---
# jupyter:
#   jupytext:
#     formats: py:percent
#     text_representation:
#       extension: .py
#       format_name: percent
# ---

# %% [markdown]
# # First NIfTI
#
# Companion notebook for [Getting Started → first NIfTI](../docs/getting-started/first-nifti.md).

# %% [markdown]
# ## 1. Imports

# %%
import matplotlib.pyplot as plt
import nibabel as nib
import numpy as np
from nilearn import datasets, plotting

# %% [markdown]
# ## 2. Get a real volume — use the MNI152 template shipped with Nilearn

# %%
mni = datasets.load_mni152_template()
img = nib.load(mni)
print(type(img), img.shape, img.header.get_zooms(),
      "orientation:", nib.aff2axcodes(img.affine))

# %% [markdown]
# ## 3. Plot one slice with raw Matplotlib

# %%
data = img.get_fdata()
mid = data.shape[2] // 2

fig, ax = plt.subplots(figsize=(4, 4), dpi=120)
ax.imshow(data[:, :, mid].T, cmap="gray", origin="lower")
ax.set(title=f"MNI152 axial slice {mid}"); ax.axis("off")
fig.tight_layout()

# %% [markdown]
# ## 4. Plot the same volume with Nilearn (publication-style)

# %%
plotting.plot_anat(img, title="MNI152", display_mode="ortho", cut_coords=(0, 0, 0))

# %% [markdown]
# ## 5. Try with a real subject — substitute your own path

# %%
# img = nib.load("data/sub-001_T1w.nii.gz")
# plotting.plot_anat(img, title="sub-001 T1w")
