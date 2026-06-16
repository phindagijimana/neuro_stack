# ---
# jupyter:
#   jupytext:
#     formats: py:percent
# ---

# %% [markdown]
# # Lesion segmentation (toy MONAI training loop)
#
# Companion notebook for [Tutorials → lesion segmentation](../docs/tutorials/lesion-segmentation.md).
#
# This notebook trains a 3D U-Net for 50 steps on synthetic volumes so you can see the
# full mixed-precision + AMP loop work without a real GPU dataset. Replace the synthetic
# data loader with a MONAI `Dataset` over your BIDS-derived volumes for real runs.

# %%
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
print("device =", device)

# %% [markdown]
# ## 1. Synthetic dataset (96^3 patches with a bright "lesion")

# %%
class ToyLesion(Dataset):
    def __init__(self, n=64, size=64):
        self.n, self.size = n, size

    def __len__(self):
        return self.n

    def __getitem__(self, i):
        s = self.size
        x = torch.randn(1, s, s, s) * 0.1 + 0.5
        y = torch.zeros(1, s, s, s)
        cx, cy, cz = np.random.randint(s // 4, 3 * s // 4, 3)
        r = np.random.randint(4, 8)
        xs, ys, zs = torch.meshgrid(
            torch.arange(s), torch.arange(s), torch.arange(s), indexing="ij")
        mask = ((xs - cx) ** 2 + (ys - cy) ** 2 + (zs - cz) ** 2) < r ** 2
        x[0][mask] += 1.0
        y[0][mask] = 1.0
        return x, y

loader = DataLoader(ToyLesion(64, 32), batch_size=4, shuffle=True)
xb, yb = next(iter(loader))
print("batch shapes:", xb.shape, yb.shape)

# %% [markdown]
# ## 2. Toy 3D U-Net (tiny, for CPU-friendly demo)

# %%
class TinyUNet3D(nn.Module):
    def __init__(self, ch=8):
        super().__init__()
        self.enc = nn.Sequential(
            nn.Conv3d(1, ch, 3, padding=1), nn.ReLU(), nn.Conv3d(ch, ch, 3, padding=1), nn.ReLU())
        self.pool = nn.MaxPool3d(2)
        self.bottleneck = nn.Sequential(
            nn.Conv3d(ch, ch * 2, 3, padding=1), nn.ReLU(),
            nn.Conv3d(ch * 2, ch * 2, 3, padding=1), nn.ReLU())
        self.up = nn.ConvTranspose3d(ch * 2, ch, 2, stride=2)
        self.dec = nn.Sequential(
            nn.Conv3d(ch * 2, ch, 3, padding=1), nn.ReLU(),
            nn.Conv3d(ch, 1, 1))

    def forward(self, x):
        e = self.enc(x)
        b = self.bottleneck(self.pool(e))
        d = self.up(b)
        return self.dec(torch.cat([d, e], dim=1))

model = TinyUNet3D().to(device)
print(sum(p.numel() for p in model.parameters()), "params")

# %% [markdown]
# ## 3. Train 50 steps with mixed precision + Dice + BCE

# %%
opt = torch.optim.AdamW(model.parameters(), lr=1e-3)
bce = nn.BCEWithLogitsLoss()
scaler = torch.amp.GradScaler(device.type) if device.type == "cuda" else None

def dice_loss(pred, y, eps=1e-6):
    pred = torch.sigmoid(pred)
    inter = (pred * y).sum()
    return 1 - (2 * inter + eps) / (pred.sum() + y.sum() + eps)

for step in range(50):
    xb, yb = next(iter(loader))
    xb, yb = xb.to(device), yb.to(device)
    opt.zero_grad(set_to_none=True)
    if scaler:
        with torch.autocast(device_type="cuda", dtype=torch.bfloat16):
            p = model(xb); loss = bce(p, yb) + dice_loss(p, yb)
        scaler.scale(loss).backward(); scaler.step(opt); scaler.update()
    else:
        p = model(xb); loss = bce(p, yb) + dice_loss(p, yb)
        loss.backward(); opt.step()
    if step % 10 == 0:
        with torch.no_grad():
            dice = 1 - dice_loss(p, yb).item()
        print(f"step {step:3d}  loss={loss.item():.3f}  dice={dice:.3f}")

# %% [markdown]
# ## 4. Visualise one prediction

# %%
import matplotlib.pyplot as plt
model.eval()
with torch.no_grad():
    pred = torch.sigmoid(model(xb)).cpu().numpy()
fig, ax = plt.subplots(1, 3, figsize=(9, 3), dpi=120)
mid = xb.shape[2] // 2
ax[0].imshow(xb[0, 0, mid].cpu(), cmap="gray"); ax[0].set_title("input")
ax[1].imshow(yb[0, 0, mid].cpu(), cmap="hot");  ax[1].set_title("label")
ax[2].imshow(pred[0, 0, mid],      cmap="hot"); ax[2].set_title("predicted (sigmoid)")
for a in ax: a.axis("off")

print("\nFor real training: replace ToyLesion with a MONAI Dataset over BIDS, "
      "expand the U-Net to MONAI's UNet, increase epochs, use AdamW + cosine LR, "
      "checkpoint every epoch, and run on a real GPU. See the markdown tutorial.")
