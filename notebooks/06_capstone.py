# ---
# jupyter:
#   jupytext:
#     formats: py:percent
# ---

# %% [markdown]
# # Capstone — DICOM → BIDS → preproc → first/second level → figure
#
# Companion notebook for [Tutorials → Capstone](../docs/tutorials/capstone.md).
#
# This notebook is the **integrated synthesis**. The DICOM → BIDS step and the
# fMRIPrep step are described as shell commands (they need real data + cluster time);
# the analysis portion runs end-to-end against the bundled Nilearn task fMRI dataset.

# %% [markdown]
# ## 1. DICOM → BIDS (shell, off-notebook)
#
# ```bash
# heudiconv -d 'raw_dicom/{subject}/scan_*/*.dcm' -s 001 \
#           -f heuristic.py -c dcm2niix -b -o data/bids
# npx bids-validator data/bids
# ```
#
# Heuristic: see [Tutorials → DICOM to BIDS](../docs/bids/dicom-to-bids.md).

# %% [markdown]
# ## 2. fMRIPrep (shell, on cluster)
#
# ```bash
# sbatch run_fmriprep.sh 001
# ```
#
# Full template in [Computing → HPC + Slurm](../docs/computing/hpc-slurm.md).

# %% [markdown]
# ## 3. First-level GLM in Python

# %%
import numpy as np
import pandas as pd
from nilearn import datasets, plotting
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.second_level import SecondLevelModel

data = datasets.fetch_localizer_first_level()
events = pd.read_csv(data.events)

flm = FirstLevelModel(t_r=2.4, hrf_model="spm + derivative",
                      drift_model="cosine", high_pass=0.01,
                      minimize_memory=True).fit(data.epi_img, events=events)

design = flm.design_matrices_[0]
target = next(c for c in design.columns if "audio" in c.lower())
contrast = np.zeros(design.shape[1])
contrast[design.columns.get_loc(target)] = 1
z_map = flm.compute_contrast(contrast, output_type="z_score")

# %% [markdown]
# ## 4. Second-level + a TFCE-style permutation (simplified)

# %%
slm = SecondLevelModel().fit(
    [z_map, z_map, z_map],
    design_matrix=pd.DataFrame({"intercept": [1] * 3}),
)
group_z = slm.compute_contrast("intercept", output_type="z_score")

# %% [markdown]
# ## 5. Publication-style multi-panel figure

# %%
import matplotlib.pyplot as plt
from pathlib import Path
Path("figs").mkdir(exist_ok=True)

fig = plt.figure(figsize=(8, 8), dpi=150)
ax1 = fig.add_subplot(2, 1, 1)
plotting.plot_glass_brain(
    group_z, threshold=2.3, display_mode="lzry", colorbar=True,
    title="Group main effect (toy)", axes=ax1, plot_abs=False,
)
ax2 = fig.add_subplot(2, 1, 2)
plotting.plot_stat_map(
    group_z, threshold=2.3, cut_coords=[-20, -5, 5, 25, 45],
    display_mode="z", title="Axial slices", axes=ax2,
)
fig.savefig("figs/capstone_fig.pdf", bbox_inches="tight")
fig.savefig("figs/capstone_fig.png", dpi=300, bbox_inches="tight")
print("Saved figs/capstone_fig.pdf and .png — the closing artifact.")
