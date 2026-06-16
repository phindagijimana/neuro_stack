# ---
# jupyter:
#   jupytext:
#     formats: py:percent
# ---

# %% [markdown]
# # fMRI first/second-level GLM
#
# Companion notebook for [Tutorials → fMRI first/second-level GLM](../docs/tutorials/fmri-glm.md).
#
# Uses Nilearn's bundled "localizer" task dataset so the notebook runs end-to-end without external downloads.

# %%
import numpy as np
import pandas as pd
from nilearn import datasets, image, plotting
from nilearn.glm.first_level import FirstLevelModel
from nilearn.glm.second_level import SecondLevelModel

# %% [markdown]
# ## 1. Get a single-subject task-fMRI dataset

# %%
data = datasets.fetch_localizer_first_level()
print("BOLD:", data.epi_img)
print("Events:")
print(pd.read_csv(data.events).head())

# %% [markdown]
# ## 2. First-level GLM

# %%
flm = FirstLevelModel(
    t_r=2.4, hrf_model="spm + derivative",
    drift_model="cosine", high_pass=0.01,
    minimize_memory=True,
).fit(data.epi_img, events=pd.read_csv(data.events))
print("Design columns:", flm.design_matrices_[0].columns.tolist())

# %% [markdown]
# ## 3. Compute a contrast and plot

# %%
design = flm.design_matrices_[0]
contrast = np.zeros(design.shape[1])
# 'audio_left_hand_button_press' is one of the localizer conditions
target = next(c for c in design.columns if "audio" in c.lower())
contrast[design.columns.get_loc(target)] = 1.0
z = flm.compute_contrast(contrast, output_type="z_score")
plotting.plot_stat_map(z, threshold=2.3, display_mode="z",
                       cut_coords=[-20, -10, 0, 10, 20],
                       title=f"{target} (z > 2.3)")

# %% [markdown]
# ## 4. (Stub) Second-level
#
# In a real cohort you'd compute z-maps for every subject and fit a SecondLevelModel.
# Here we just demonstrate the API with a one-subject "group" of fake replicates.

# %%
fake_group = [z, z, z]
slm = SecondLevelModel().fit(
    fake_group,
    design_matrix=pd.DataFrame({"intercept": [1] * len(fake_group)}),
)
group_z = slm.compute_contrast("intercept", output_type="z_score")
plotting.plot_glass_brain(group_z, threshold=2.3, display_mode="lzry",
                          plot_abs=False, colorbar=True,
                          title="Toy group main effect")
