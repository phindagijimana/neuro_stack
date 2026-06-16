# ---
# jupyter:
#   jupytext:
#     formats: py:percent
# ---

# %% [markdown]
# # Cortical-thickness ML
#
# Companion notebook for [Tutorials → cortical-thickness ML](../docs/tutorials/cortical-thickness-ml.md).
#
# Uses a synthetic cohort to demonstrate site-stratified group K-Fold with proper bootstrap CIs.

# %%
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.linear_model import Ridge
from sklearn.preprocessing import StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GroupKFold, GridSearchCV

sns.set_theme(context="paper", style="whitegrid")
rng = np.random.default_rng(42)

# %% [markdown]
# ## 1. Synthesise a 3-site cohort of cortical-thickness vectors

# %%
N, SITES, P = 300, 3, 68
ages = rng.uniform(18, 80, N)
site = rng.integers(0, SITES, N)
# Each region's thickness depends on age + site-specific bias
W_age = rng.normal(-0.005, 0.001, P)        # cortical-thinning trend
W_site = rng.normal(0, 0.05, (SITES, P))
X = np.outer(ages, W_age) + W_site[site] + rng.normal(0, 0.02, (N, P)) + 2.5
sids = [f"sub-{i:03d}" for i in range(N)]
df = pd.DataFrame(X, columns=[f"roi_{j:02d}" for j in range(P)])
df["subject_id"] = sids; df["age"] = ages; df["site"] = site
print(df.shape, df.head(3))

# %% [markdown]
# ## 2. Nested GroupKFold + Ridge

# %%
features = [c for c in df.columns if c.startswith("roi_")]
X = df[features].values
y = df["age"].values
groups = df["site"].values

pipe = Pipeline([("scaler", StandardScaler()), ("ridge", Ridge())])
mae_per_fold, pred = [], np.zeros_like(y, dtype=float)
outer = GroupKFold(n_splits=3)

for tr, te in outer.split(X, y, groups):
    gs = GridSearchCV(
        pipe, param_grid={"ridge__alpha": [0.1, 1, 10, 100]},
        cv=GroupKFold(n_splits=2),
        scoring="neg_mean_absolute_error", n_jobs=2,
    )
    gs.fit(X[tr], y[tr], groups=groups[tr])
    pred[te] = gs.predict(X[te])
    mae_per_fold.append(np.mean(np.abs(pred[te] - y[te])))
print(f"Outer MAE: mean={np.mean(mae_per_fold):.2f}  std={np.std(mae_per_fold):.2f}")

# %% [markdown]
# ## 3. Bootstrap CI on MAE

# %%
boot = []
for _ in range(2000):
    idx = rng.integers(0, len(y), len(y))
    boot.append(np.mean(np.abs(pred[idx] - y[idx])))
ci = np.percentile(boot, [2.5, 97.5])
print(f"95% bootstrap CI for MAE: [{ci[0]:.2f}, {ci[1]:.2f}]")

# %% [markdown]
# ## 4. Honest reporting plot

# %%
fig, ax = plt.subplots(1, 2, figsize=(10, 4.5), dpi=120)
sns.scatterplot(x=y, y=pred, hue=site, ax=ax[0], alpha=0.7,
                palette="deep")
lo, hi = y.min(), y.max()
ax[0].plot([lo, hi], [lo, hi], "k--", lw=1)
ax[0].set(xlabel="Age", ylabel="Predicted age",
          title=f"GroupKFold CV (MAE={np.mean(mae_per_fold):.1f})")

mae_df = pd.DataFrame({"site": site, "err": np.abs(pred - y)})
sns.boxplot(data=mae_df, x="site", y="err", ax=ax[1])
ax[1].set(xlabel="Site", ylabel="|prediction-truth|",
          title="Per-site error")
fig.tight_layout()
