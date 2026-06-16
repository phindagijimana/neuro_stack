# ---
# jupyter:
#   jupytext:
#     formats: py:percent
# ---

# %% [markdown]
# # Multimodal image + text (BiomedCLIP)
#
# Companion notebook for [Tutorials → multimodal image+text](../docs/tutorials/multimodal-image-text.md).
#
# This is a *zero-shot* demo: load a pretrained vision-language model, query it
# with free text against an image. Full fine-tuning needs a real dataset + GPU.

# %% [markdown]
# ## 1. Install (one-time)
#
# ```bash
# pip install open_clip_torch pillow
# ```

# %%
import torch
import torch.nn.functional as F
from PIL import Image

# %% [markdown]
# ## 2. Load BiomedCLIP

# %%
try:
    from open_clip import create_model_from_pretrained, get_tokenizer
    model, preprocess = create_model_from_pretrained(
        "hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224")
    tokenizer = get_tokenizer(
        "hf-hub:microsoft/BiomedCLIP-PubMedBERT_256-vit_base_patch16_224")
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model = model.to(device).eval()
    print("BiomedCLIP loaded on", device)
except Exception as e:
    print("Could not load BiomedCLIP:", e)
    print("Falling back to a synthetic zero-shot demo")

# %% [markdown]
# ## 3. Zero-shot classification of one image
#
# Replace `query_image.png` with any of your own .png / .jpg.

# %%
try:
    img = Image.open("query_image.png").convert("RGB")
except FileNotFoundError:
    # Make a synthetic noisy image so the notebook still runs
    import numpy as np
    img = Image.fromarray((np.random.rand(224, 224, 3) * 255).astype("uint8"))

prompts = [
    "an MRI of a healthy brain",
    "an MRI showing acute ischemic stroke",
    "an MRI showing a brain tumour",
    "an MRI showing multiple sclerosis lesions",
]

with torch.no_grad():
    img_t = preprocess(img).unsqueeze(0).to(device)
    txt_t = tokenizer(prompts).to(device)
    v = F.normalize(model.encode_image(img_t), dim=-1)
    t = F.normalize(model.encode_text(txt_t), dim=-1)
    sims = (v @ t.T).softmax(dim=-1)[0]

for p, s in zip(prompts, sims):
    print(f"{s.item():.3f}  {p}")

# %% [markdown]
# ## 4. Text → image retrieval (against a small corpus)

# %%
import glob
corpus_paths = glob.glob("corpus/*.png") or []
if corpus_paths:
    with torch.no_grad():
        corpus = torch.stack([preprocess(Image.open(p).convert("RGB"))
                              for p in corpus_paths]).to(device)
        cfeats = F.normalize(model.encode_image(corpus), dim=-1)
        q = "ring-enhancing lesion in the right temporal lobe"
        qfeat = F.normalize(model.encode_text(tokenizer([q]).to(device)), dim=-1)
        sims = (qfeat @ cfeats.T)[0]
    for s, idx in zip(*sims.topk(min(5, len(corpus_paths)))):
        print(f"{s.item():.3f}  {corpus_paths[idx]}")
else:
    print("(no images in corpus/; skip retrieval demo)")

# %% [markdown]
# For a real fine-tune workflow, see the markdown tutorial — needs MIMIC-CXR / OpenI
# and a multi-hour GPU run.
