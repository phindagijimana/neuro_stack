# AI / ML for neuroimaging

> What machine learning on brain data actually looks like — the parts that bite teams arriving from generic computer vision or NLP.

This section assumes you can write training loops in PyTorch (or are willing to learn). It focuses on the parts of ML that are *specific* to neuroimaging: small 3D/4D datasets, scanner and site effects, clinically meaningful evaluation, and the engineering needed to train on patches of a 256³ volume without running out of memory.

It's written for engineers who already know that a U-Net exists and a transformer exists, and now need to deploy them against medical volumes without overfitting, leaking, or shipping a model that fails the moment a different scanner shows up.

## Section map

<div class="grid cards" markdown>

-   :material-chart-scatter-plot: **[Classical ML on volumetrics](classical-ml.md)** — when you don't need deep learning. Feature engineering on volumes, surfaces, and connectomes; linear models, SVMs, gradient-boosted trees; sample-size reality checks.

-   :material-network: **[Deep learning for imaging](deep-learning.md)** — 2D vs 2.5D vs 3D convnets, U-Nets for segmentation, ViTs and Swin variants for volumes, augmentation in 3D.

-   :material-cog-play: **[Training mechanics](training-mechanics.md)** — mixed precision, patch sampling, gradient accumulation, multi-GPU, checkpointing, OOM debugging, profiling.

-   :material-cube-outline: **[Foundation models](foundation-models.md)** — the landscape of large pre-trained models for medical imaging, when fine-tuning beats training from scratch, multimodal models that combine imaging with text or genomics.

-   :material-scale-balance: **[Evaluation pitfalls](evaluation.md)** — subject-level splits, site/scanner effects (ComBat and friends), reporting Dice / HD95 / AUROC honestly, calibration.

-   :material-gavel: **[Regulatory](regulatory.md)** — FDA, CE / MDR, ISO 13485, IEC 62304; what "software as a medical device" means for an ML model.

</div>

## Why this is separate from generic ML

Three reasons neuroimaging ML is different enough to warrant its own section:

1. **The data is 3D or 4D and small.** A medical dataset is typically hundreds to low-thousands of subjects, not millions of images. Most of your engineering effort goes into *not* overfitting.
2. **Site and scanner effects dominate noise.** A model that "works" on Site A often falls over on Site B because of field strength, coil, sequence, or vendor differences. Harmonisation is a first-class concern.
3. **Clinical context shapes what "good" means.** A 0.85 Dice that misses a small lesion is worse than a 0.80 Dice that catches it. Metrics that ignore failure modes are misleading.

Everything in this section is written with those three constraints in mind.

## What this section does *not* cover

- **General-purpose ML theory.** Stochastic gradient descent, regularisation, the bias-variance tradeoff — assumed. Plenty of better resources exist for those.
- **Software-engineering basics for training.** Mixed precision and multi-GPU live in [Training mechanics](training-mechanics.md); CUDA drivers and cluster jobs live in [Computing](../computing/index.md).
- **Clinical decision support and product design.** Touched on in [Regulatory](regulatory.md), but a product playbook is out of scope.

The dividing line: this section is the *neuroimaging-shaped* parts of ML — what makes a model trained on brain volumes different from a model trained on ImageNet.

## Reading order

=== "Beginner"

    Goal: train one credible model on one dataset and evaluate it without lying to yourself.

    1. [Classical ML on volumetrics](classical-ml.md) — start here even if you plan to do deep learning later; the data-handling habits transfer.
    2. [Deep learning for imaging](deep-learning.md) — the architectural vocabulary.
    3. [Evaluation pitfalls](evaluation.md) — read *before* you split your data, not after.

    These three pages are enough to do an honest baseline.

=== "Intermediate"

    Goal: production-quality training runs on a shared GPU cluster.

    1. [Training mechanics](training-mechanics.md) — mixed precision, patch sampling, multi-GPU.
    2. [Foundation models](foundation-models.md) — fine-tuning beats from-scratch for most clinical questions today.
    3. [Evaluation pitfalls](evaluation.md) revisited with multi-site cohorts and harmonisation.

    By the end you should be running multi-day training jobs that produce models you'd actually deploy.

=== "PhD / specialist"

    Goal: contribute methods, ship clinical tools, or stand up a fine-tuned foundation model on a programme cohort.

    1. The advanced sections of [Training mechanics](training-mechanics.md) — distributed training, gradient checkpointing, profiling.
    2. [Foundation models](foundation-models.md) read end-to-end, including multimodal.
    3. [Regulatory](regulatory.md) — necessary the moment a model touches a patient or a trial.
    4. Landmark deep-learning papers via [Landmark → Foundational papers](../landmark/papers.md).

    Specialists own both the modelling and the operational story around it (data lineage, monitoring, governance).

## Where to next

For the engineering substrate underneath the training loops, see [Computing → GPUs and accelerators](../computing/gpus.md) and the [Data engineering](../data-engineering/index.md) section. For the imaging-side context, [Analysis](../analysis/index.md) covers what the ML models are competing with — and complementing.
