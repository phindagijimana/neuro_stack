# Medical imaging

> The cross-modality engineering layer — how images are *acquired*, *reconstructed*, *segmented*, *registered*, and *enhanced* — written for research-grade neuroimaging work.

The [MRI sequences](../sequences/index.md) section explains the physics of specific MR sequences. The [Medical imaging physics](../foundations/physics.md) page covers the physical basis of every modality. This section covers the **methodological layer** that turns raw scanner output into the volumes, surfaces, and labels every downstream analysis depends on.

## The end-to-end pipeline

Every imaging-derived dataset follows the same five-step shape, regardless of modality:

```text
patient / phantom
    │
    ▼
1. ACQUISITION      ── raw scanner measurements (k-space, sinogram, list-mode)
    │
    ▼
2. RECONSTRUCTION   ── inverse problem: measurements → image volume
    │
    ▼
3. ENHANCEMENT      ── denoising, bias correction, artifact removal
    │
    ▼
4. REGISTRATION     ── align to template, atlas, or other modality
    │
    ▼
5. SEGMENTATION     ── label voxels into anatomical / pathological classes
    │
    ▼
quantitative analysis
```

The steps are conceptually separate but in practice often interleaved (joint reconstruction-segmentation, image-to-image deep learning that fuses several steps). Knowing the canonical decomposition is what lets you read a methods section and place every block.

## Chapters

<div class="grid cards" markdown>

-   :material-camera-iris: **[Acquisition](acquisition.md)**

    ---

    The forward model $y = A x + n$; per-modality acquisition steps for MRI, CT, PET, ultrasound, and optical. Sampling theory and the bias each modality introduces.

-   :material-puzzle: **[Reconstruction](reconstruction.md)**

    ---

    Analytic methods (FBP, inverse FFT), iterative algorithms (ART, MLEM/OSEM), compressed sensing, model-based and deep-learning reconstruction. Worked examples per modality.

-   :material-shape: **[Segmentation](segmentation.md)**

    ---

    Thresholding, region growing, GMM, level sets, graph cut, multi-atlas + label fusion, U-Net family, nnU-Net, SAM / MedSAM. Loss functions, evaluation metrics, calibration.

-   :material-vector-link: **[Registration](registration.md)**

    ---

    Rigid → affine → diffeomorphic transforms; intensity-based and feature-based similarity (SSD, NCC, MI); SyN / ANTs; deep-learning registration (VoxelMorph); evaluation.

-   :material-auto-fix: **[Enhancement & quality](enhancement.md)**

    ---

    Bias-field correction (N4), denoising (NLM, MP-PCA, NORDIC), Gibbs unringing, motion / distortion correction, super-resolution, and automated QC.

</div>

## How every chapter is structured

To make this section consistent and reviewable each chapter follows the same five-section pattern:

1. **Theory** — the conceptual model and the physical / mathematical assumptions.
2. **Mathematics** — the equations and the algorithmic primitives, written compactly.
3. **Steps** — the algorithm or pipeline, in numbered form.
4. **Practical example** — a runnable recipe on neuroimaging data, often pointing at a tool (ANTs, FreeSurfer, MONAI, nnU-Net).
5. **References** — peer-reviewed primary sources with DOIs.

## Aim

The aim is to take an advanced reader from "I can run fMRIPrep" to "I can read the original methods papers, evaluate them critically, and modify the underlying algorithms when my data needs it" — across every imaging modality a neuroimaging cohort might contain.

## Visual references

Curated, openly-licensed image galleries that complement the chapters in this section:

- **MRtrix3 figure gallery.** [https://mrtrix.readthedocs.io/en/latest/](https://mrtrix.readthedocs.io/en/latest/) — diffusion-MRI reconstruction and tractography illustrated.
- **MONAI tutorials gallery.** [https://github.com/Project-MONAI/tutorials](https://github.com/Project-MONAI/tutorials) — segmentation, registration, generative-model notebooks with rendered figures.
- **The fastMRI dataset.** [https://fastmri.med.nyu.edu](https://fastmri.med.nyu.edu) — under-sampled k-space + reconstructed images, with publication-grade visualisations.
- **ITK examples.** [https://itk.org/ITKExamples/](https://itk.org/ITKExamples/) — registration and segmentation walkthroughs with sample volumes and rendered output.
- **Radiopaedia case library.** [https://radiopaedia.org/articles](https://radiopaedia.org/articles) — clinical example cases with all modalities labelled.
- **3D Slicer training portal.** [https://www.slicer.org/wiki/Documentation/Nightly/Training](https://www.slicer.org/wiki/Documentation/Nightly/Training) — interactive segmentation / registration screencasts.
