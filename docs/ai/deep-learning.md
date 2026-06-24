# Deep learning for imaging

> Architectures and training tricks for when the input is voxels.

If your task is segmentation, lesion detection, image-to-image translation, or anything where the *spatial structure* of the image matters, deep learning is the default. This chapter covers the parts that are different from generic computer vision.

## 2D vs 2.5D vs 3D

| Approach | Pro | Con |
| --- | --- | --- |
| **2D** (slice-by-slice) | Cheap, leverages 2D pre-training | Ignores out-of-plane context |
| **2.5D** (3 orthogonal slices through the voxel) | Cheap + some context | Asymmetric receptive field |
| **3D** (volume) | True spatial context | Memory-hungry; rarely pre-trained |

A common pattern: a 2.5D model on full volumes for rough localisation, then a 3D model on cropped patches around regions of interest.

## Segmentation: U-Net and its descendants

The 3D U-Net [Ronneberger et al., 2015](https://doi.org/10.1007/978-3-319-24574-4_28)[^unet]; [Çiçek et al., 2016](https://doi.org/10.1007/978-3-319-46723-8_49)[^unet3d] is the workhorse for medical segmentation. Skip connections preserve fine detail; the bottleneck enforces context.

**nnU-Net** [Isensee et al., 2021](https://doi.org/10.1038/s41592-020-01008-z)[^nnunet] is the reference implementation — it auto-configures architecture, patch size, normalisation, and training schedule from the dataset. Start there. Beat it before you build your own.

## Volume transformers

The Vision Transformer (ViT, [Dosovitskiy et al., 2020](https://doi.org/10.48550/arXiv.2010.11929)[^vit]) was the first pure-transformer architecture to match CNNs on ImageNet, opening the door to medical-imaging transformers (Swin, UNETR, ViT-V-Net, etc.).

For larger datasets and richer tasks (multi-class segmentation, captioning), transformer-based architectures (Swin UNETR [Hatamizadeh et al., 2022](https://doi.org/10.48550/arXiv.2201.01266)[^swinunetr], UNETR [Hatamizadeh et al., 2021](https://doi.org/10.1109/WACV51458.2022.00181)[^unetr]) are now competitive with — and often beat — pure CNN U-Nets.

Key idea: tokenise the volume into patches, attend across patches, decode back to voxel space. Memory cost is quadratic in number of tokens, so patch size and stride matter enormously.

## Training tricks that actually matter

- **Patch sampling.** Brains are mostly background. Sampling patches uniformly wastes compute. Use class-balanced or foreground-biased sampling.
- **Class imbalance loss.** Cross-entropy is dominated by background. Combine with Dice (`DiceCE`, `Focal`, `Tversky`).
- **3D augmentation.** Rotations and flips must respect anatomy (don't flip left/right unless the task is symmetric). Elastic deformations help; intensity augmentation (bias field, Gaussian noise) helps more than you'd think.
- **Mixed precision.** `torch.autocast` cuts memory ~40% with no accuracy hit. Always on.
- **Gradient accumulation.** When a single 3D patch fills the GPU, accumulate gradients over multiple patches before stepping the optimiser.
- **Sliding-window inference.** At test time, run the model on overlapping patches and average the predictions. MONAI's `sliding_window_inference` handles this.

## A minimal MONAI training loop [Cardoso et al., 2022](https://doi.org/10.48550/arXiv.2211.02701)[^monai]

```python
import torch
from monai.data import DataLoader, Dataset
from monai.networks.nets import UNet
from monai.losses import DiceCELoss
from monai.transforms import Compose, LoadImaged, RandFlipd, ScaleIntensityd, ToTensord

transforms = Compose([
    LoadImaged(keys=["image", "label"]),
    ScaleIntensityd(keys="image"),
    RandFlipd(keys=["image", "label"], spatial_axis=0, prob=0.5),
    ToTensord(keys=["image", "label"]),
])

dataset = Dataset(data=train_records, transform=transforms)
loader = DataLoader(dataset, batch_size=2, shuffle=True, num_workers=4)

model = UNet(
    spatial_dims=3,
    in_channels=1,
    out_channels=4,
    channels=(16, 32, 64, 128, 256),
    strides=(2, 2, 2, 2),
).cuda()

loss_fn = DiceCELoss(softmax=True, to_onehot_y=True)
opt = torch.optim.AdamW(model.parameters(), lr=1e-4)

for batch in loader:
    x = batch["image"].cuda()
    y = batch["label"].cuda()
    with torch.autocast(device_type="cuda"):
        pred = model(x)
        loss = loss_fn(pred, y)
    opt.zero_grad()
    loss.backward()
    opt.step()
```

This is intentionally simple. Real production code adds checkpointing, AMP scaling, distributed training, and learning-rate schedules — but the skeleton above is enough to *understand* what's happening.

## References

[^unet]: Ronneberger O, Fischer P, Brox T. U-Net: Convolutional Networks for Biomedical Image Segmentation. *MICCAI.* 2015. [doi:10.1007/978-3-319-24574-4_28](https://doi.org/10.1007/978-3-319-24574-4_28)
[^unet3d]: Çiçek Ö, Abdulkadir A, Lienkamp SS, Brox T, Ronneberger O. 3D U-Net: learning dense volumetric segmentation from sparse annotation. *MICCAI.* 2016. [doi:10.1007/978-3-319-46723-8_49](https://doi.org/10.1007/978-3-319-46723-8_49)
[^nnunet]: Isensee F, Jaeger PF, Kohl SAA, Petersen J, Maier-Hein KH. nnU-Net: a self-configuring method for deep learning-based biomedical image segmentation. *Nat Methods.* 2021;18(2):203-211. [doi:10.1038/s41592-020-01008-z](https://doi.org/10.1038/s41592-020-01008-z)
[^swinunetr]: Hatamizadeh A, Nath V, Tang Y, Yang D, Roth HR, Xu D. Swin UNETR. *arXiv:2201.01266.* 2022. [doi:10.48550/arXiv.2201.01266](https://doi.org/10.48550/arXiv.2201.01266)
[^unetr]: Hatamizadeh A, Tang Y, Nath V, et al. UNETR: Transformers for 3D Medical Image Segmentation. *WACV.* 2022. [doi:10.1109/WACV51458.2022.00181](https://doi.org/10.1109/WACV51458.2022.00181)
[^monai]: Cardoso MJ, Li W, Brown R, et al. MONAI: An open-source framework for deep learning in healthcare. *arXiv:2211.02701.* 2022. [doi:10.48550/arXiv.2211.02701](https://doi.org/10.48550/arXiv.2211.02701)
[^vit]: Dosovitskiy A, Beyer L, Kolesnikov A, et al. An image is worth 16x16 words: Transformers for image recognition at scale. *ICLR.* 2021. [doi:10.48550/arXiv.2010.11929](https://doi.org/10.48550/arXiv.2010.11929)

## Where to next

[Foundation models](foundation-models.md) — when even your custom architecture isn't enough and you need to stand on someone else's pre-training.
