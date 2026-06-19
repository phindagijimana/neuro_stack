# Registration

> Finding the spatial transformation that aligns one image to another. The geometric backbone of multi-modal analysis, longitudinal studies, atlas-based segmentation, and group statistics.

## 1. Theory

Registration finds a transformation $T: \Omega_M \to \Omega_F$ that warps a **moving image** $M$ onto a **fixed image** $F$ so a similarity metric is optimised:

$$
\hat T = \arg\min_T\; D(F, M \circ T) + \lambda R(T)
$$

- $D$ — image-similarity metric (SSD, NCC, MI).
- $R(T)$ — regularisation on the transformation (smoothness, invertibility).
- $\lambda$ — trade-off.

Three transformation families:

- **Rigid** — 6 DoF (3 rotation + 3 translation). Same modality within a subject (motion correction, longitudinal).
- **Affine** — 12 DoF (adds scale + shear). Cross-modal within a subject; coarse cross-subject.
- **Deformable / diffeomorphic** — millions of DoF; non-linear warps for cross-subject normalisation, atlas-based segmentation.

## 2. Mathematics

### Transformation models

Rigid:

$$
T(\vec r) = R \vec r + \vec t, \qquad R \in SO(3),\; \vec t \in \mathbb{R}^3
$$

Affine:

$$
T(\vec r) = A \vec r + \vec t, \qquad A \in GL(3)
$$

Diffeomorphic — $T = \phi_1$, the time-1 flow of a velocity field:

$$
\frac{d \phi_t}{dt} = v_t(\phi_t), \qquad \phi_0 = \mathrm{Id}
$$

Stationary velocity: $\phi = \exp(v)$, computed by scaling-and-squaring. Time-varying velocity: the LDDMM framework ([Beg et al., 2005](https://doi.org/10.1023/B:VISI.0000043755.93987.aa)).

### Similarity metrics

- **Sum of squared differences (SSD)** — same-modality, same-contrast:

$$
D_{\mathrm{SSD}}(F, M_T) = \sum_v (F(v) - M_T(v))^2
$$

- **Normalised cross-correlation (NCC)** — robust to global intensity changes:

$$
D_{\mathrm{NCC}}(F, M_T) = -\frac{\sum_v (F - \bar F)(M_T - \bar M_T)}{\sqrt{\sum_v (F - \bar F)^2 \sum_v (M_T - \bar M_T)^2}}
$$

- **Mutual information (MI)** ([Maes et al., 1997](https://doi.org/10.1109/42.563664); [Wells et al., 1996](https://doi.org/10.1016/S1361-8415(01)80004-9)) — multi-modal:

$$
\mathrm{MI}(F, M_T) = \sum_{f, m} p(f, m)\, \log \frac{p(f, m)}{p(f)\, p(m)}
$$

estimated via Parzen-window joint histograms. Mattes MI ([Mattes et al., 2003](https://doi.org/10.1109/TMI.2002.806275)) is the canonical neuroimaging variant.

### Regularisation

For diffeomorphic registration:

$$
R(v) = \|L v\|^2_{L^2}
$$

where $L$ is a differential operator (e.g. $L = (I - \alpha \nabla^2)^k$) controlling smoothness. The Beltrami flow, viscous-fluid, demons regularisation are all instances.

### Optimisation

- **Powell** for low-DoF rigid/affine.
- **Gradient descent + line search** for affine.
- **Symmetric Normalisation (SyN)** — symmetric pair of forward and backward velocity fields composed at half-time; the workhorse in ANTs ([Avants et al., 2008](https://doi.org/10.1016/j.media.2007.06.004)).
- **L-BFGS** for many medium-DoF parameterisations.

### Multi-resolution / pyramid strategy

Almost every classical registration uses a pyramid: start at coarse resolution to escape local minima, refine to native resolution. Gaussian pyramids with `[8 4 2 1]` voxel-smoothing schedules are standard.

```mermaid
flowchart LR
    M0[Moving<br/>8× smooth] --> M1[Moving<br/>4× smooth]
    M1 --> M2[Moving<br/>2× smooth]
    M2 --> M3[Moving<br/>native]
    F0[Fixed<br/>8× smooth] --> F1[Fixed<br/>4× smooth]
    F1 --> F2[Fixed<br/>2× smooth]
    F2 --> F3[Fixed<br/>native]
    M0 --> R0[Rigid → affine]
    F0 --> R0
    R0 --> R1[Affine] --> R2[Deformable<br/>coarse] --> R3[Deformable<br/>fine]
    M1 --> R1
    F1 --> R1
    M2 --> R2
    F2 --> R2
    M3 --> R3
    F3 --> R3
    R3 --> T[Final transform T]
    style T fill:#e0e0ff,stroke:#444
```

*<small>The coarse-to-fine pyramid in classical registration. Solves the local-minimum problem at coarse scales and refines accuracy at fine scales. Original figure.</small>*

### Velocity fields, SyN, and diffeomorphisms

!!! tip "Beginner takeaway"
    Don't optimise the deformation directly — optimise a *velocity field* and integrate it. That single trick is what gives ANTs SyN its smooth, invertible, topology-preserving warps.

#### Why parameterise a velocity, not a deformation

A naive parameterisation of $\phi$ as a per-voxel displacement field has no guarantee of being invertible: nothing stops two voxels from being mapped to the same target ("folding"), and once that happens you can't recover a clean inverse warp. The fix is to parameterise a smooth, time-varying **velocity field** $v(\mathbf{x}, t)$, and obtain the deformation as the *flow* of $v$:

$$
\frac{d\phi_t}{dt} = v_t(\phi_t), \qquad \phi_0 = \mathrm{Id}, \qquad \phi = \phi_1
$$

This is the LDDMM construction ([Beg et al., 2005](https://doi.org/10.1023/B:VISI.0000043755.93987.aa)). Provided $v$ stays smooth enough, the flow is a **diffeomorphism** — smooth, bijective, smoothly invertible, topology-preserving.

#### The formal definition

A map $\phi: \mathbb{R}^3 \to \mathbb{R}^3$ is in $\text{Diff}(\mathbb{R}^3)$ iff both $\phi$ and $\phi^{-1}$ exist and are smooth ($C^\infty$, or in practice $C^1$ with bounded derivatives). Equivalently, $\det J_\phi(\mathbf{x}) > 0$ everywhere — the warp never folds. Without this, group analyses on warped images are **statistically suspect**: a fold or tear means a voxel "has no inverse identity", and per-voxel statistics on the resampled image describe a region that doesn't correspond cleanly to any region in the original.

#### Symmetric Normalization (SyN)

SyN ([Avants et al., 2008](https://doi.org/10.1016/j.media.2007.06.004)) extends LDDMM with one more idea: instead of warping moving → fixed in one direction, compute *two* half-warps that meet in the middle,

$$
\phi_{\text{fwd}} \circ \phi_{\text{inv}}^{-1} = \mathrm{Id}
$$

by construction. This symmetry removes a class of biases (the result no longer depends on which image you called "moving") and is the reason ANTs SyN has been near-the-top in every published registration benchmark since [Klein et al., 2009](https://doi.org/10.1016/j.neuroimage.2008.12.037).

#### Worked example — antsRegistrationSyN.sh

```bash
antsRegistrationSyN.sh \
    -d 3 \                          # dimensionality (3D volume)
    -f fixed.nii.gz \               # fixed / target image
    -m moving.nii.gz \              # moving / source image
    -o out \                        # output prefix
    -t s                            # transform type: s = rigid + affine + SyN
```

Outputs:

| File | What it is |
|---|---|
| `out0GenericAffine.mat` | the rigid + affine part as an ITK transform |
| `out1Warp.nii.gz` | forward non-linear displacement field (moving → fixed) |
| `out1InverseWarp.nii.gz` | inverse non-linear displacement field (fixed → moving) |
| `outWarped.nii.gz` | the moving image resampled into the fixed space |

The `-t` flag selects the pipeline: `r` (rigid only), `a` (rigid + affine), `s` (rigid + affine + SyN), `b` (rigid + affine + B-spline SyN). For atlas-based segmentation, always use `s` or `b` — a pure affine is too rigid to absorb inter-subject anatomy.

#### Practical note — verifying the diffeomorphism

Most "registration failed" tickets in atlas-based studies turn out to be **non-diffeomorphic warps** rather than bad similarity fits. Two cheap sanity checks:

1. **Compose forward + inverse** with `antsApplyTransforms` and confirm the result is near-identity (max displacement < 1 voxel). A non-zero residual is the easiest detector of folding.
2. **Compute the Jacobian determinant** with `CreateJacobianDeterminantImage 3 out1Warp.nii.gz jac.nii.gz`. If `min(jac) < 0` anywhere inside the brain mask, the warp folds — drop the cost-function smoothing or revisit pre-alignment.

For a deeper tour see the [ANTs wiki](https://github.com/ANTsX/ANTs/wiki).

#### Symmetric vs asymmetric formulations — the unbiased-atlas consequence

A registration algorithm is **asymmetric** if swapping the roles of moving and fixed (then composing with an inverse) gives a different answer. Asymmetry biases group templates: an asymmetric algorithm anchored at subject 0 produces a "template" that is really subject 0 with slight blur. SyN is symmetric *by construction* — it parameterises two velocity fields, integrates each from $t=0$ to $t=1/2$, and matches at the geodesic midpoint:

$$
\hat v_M, \hat v_F = \arg\min_{v_M, v_F}\; D\bigl(F \circ \phi_F^{1/2},\, M \circ \phi_M^{1/2}\bigr) + \lambda \bigl(\|L v_M\|^2 + \|L v_F\|^2\bigr)
$$

The final transform is the composition $\phi_F^{-1/2} \circ \phi_M^{1/2}$. Running with roles swapped yields the same warp up to numerical noise. For **unbiased atlas building** (see [section 4: group template construction](#group-template-construction)) this matters: the average geometry depends on the cohort, not the indexing.

#### Why ANTs SyN dominates benchmarks

The [Klein et al., 2009](https://doi.org/10.1016/j.neuroimage.2008.12.037) evaluation of 14 nonlinear deformation algorithms placed SyN (and the closely related [ART](https://www.nitrc.org/projects/art/)) at the top of every overlap-based ranking. The reasons are not exotic — they compound:

- **Time-varying velocity-field parameterisation.** Full diffeomorphism group, guaranteed inverse, no folding.
- **Cross-correlation metric over local windows.** $D_{\mathrm{NCC}}$ over patches is robust to bias-field drift and partial-volume effects, where MI estimated globally is noisier.
- **Symmetric forward + inverse integration.** Removes the bias direction of every other algorithm in the Klein comparison.
- **Aggressive multi-scale optimisation.** Long coarse-to-fine schedule with sane defaults — most users never tune it.
- **Robust defaults out of the box.** `antsRegistrationSyN.sh` sets sensible smoothing, shrink factors, and convergence per pyramid level.

What the alternatives trade off:

| Tool | Parameterisation | Strength | Trade-off |
| --- | --- | --- | --- |
| [FSL FNIRT](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FNIRT) | B-spline grid | Fast, integrated with FSL | No diffeomorphism guarantee; lower Klein-2009 scores |
| [SPM DARTEL](https://doi.org/10.1016/j.neuroimage.2007.07.007) | Stationary velocity | Diffeomorphic; tight SPM integration | Stationary $v$; population-template focus |
| [NiftyReg `reg_f3d`](https://github.com/KCL-BMEIS/niftyreg) | B-spline grid | Very fast; GPU options | No diffeomorphism guarantee |
| [ANTs SyN](https://doi.org/10.1016/j.media.2007.06.004) | Time-varying velocity | Top of Klein 2009; symmetric; robust | Slowest of the four |
| [VoxelMorph](https://doi.org/10.1109/TMI.2019.2897538) | Learned U-Net | ~100 ms inference | OOD risk; quality depends on training distribution |

If runtime is not the bottleneck, SyN is the safe default. If it is, [VoxelMorph](https://doi.org/10.1109/TMI.2019.2897538) trained on your distribution is the modern alternative; otherwise [FNIRT](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FNIRT) or [NiftyReg](https://github.com/KCL-BMEIS/niftyreg) for speed at the cost of explicit folding checks.

#### Diffeomorphic atlas building

A study-specific template is more than the voxelwise average of registered images. Naive averaging biases toward whichever subject was used as the registration anchor and blurs anatomy that is misaligned. The ANTs [`antsMultivariateTemplateConstruction2.sh`](https://github.com/ANTsX/ANTs/blob/master/Scripts/antsMultivariateTemplateConstruction2.sh) workflow (descended from `buildtemplateparallel.sh`) computes the **iterative geodesic mean**:

1. Initialise the template as a linear average of all subjects.
2. Register every subject to the current template with SyN.
3. Average the warped images and the *inverse warps*. The inverse-warp average encodes the residual bias of the current template.
4. Apply the average inverse warp to the current template, pulling it toward the cohort mean in geometry as well as intensity.
5. Repeat to convergence (typically 4–6 iterations).

The fixed point is a template at the [Fréchet mean](https://en.wikipedia.org/wiki/Fr%C3%A9chet_mean) of the cohort under the diffeomorphism metric — equidistant in deformation-space from every subject. This is qualitatively different from a Euclidean average of pre-registered images, which is biased by the anchor and has blurred boundaries wherever subjects disagree. The same logic underpins [TemplateFlow's](https://www.templateflow.org/browse/) construction of versioned cohort templates and is why pediatric / disease-specific atlases must be rebuilt rather than re-averaged.

## 3. Steps — generic registration pipeline

1. **Preprocess** both images: bias correction, intensity normalisation, skull strip (if appropriate).
2. **Initialise** — centre-of-mass alignment or identity.
3. **Rigid** — coarse → fine pyramid; SSD or MI.
4. **Affine** — initialise from rigid result; same metric.
5. **Deformable / SyN** — initialise from affine; coarse-to-fine velocity field.
6. **Apply transform** to all derived images (segmentations, statistical maps) using the same $T$.
7. **QC** — overlay edges or use a quantitative metric (Dice on a known label, target-registration error on landmarks).

## 4. Special cases in neuroimaging

### Within-subject across-modality

T1w ↔ FLAIR, T1w ↔ T2*, T1w ↔ DWI b=0. Use **affine** + **MI**. Boundary-based registration (BBR, [Greve & Fischl, 2009](https://doi.org/10.1016/j.neuroimage.2009.06.060)) refines the fit using cortical-WM boundaries from FreeSurfer.

### Across subjects (normalisation to template)

Non-linear registration to MNI152 / fsLR. ANTs SyN, FSL FNIRT, DARTEL (SPM), or VoxelMorph for fast inference. Always pin the template version ([TemplateFlow](https://www.templateflow.org)).

### Longitudinal

A subject scanned multiple times. Use **subject-specific halfway template** to avoid bias toward any one timepoint (FreeSurfer longitudinal stream; ANTs longitudinal pipeline).

### Distortion correction (within-acquisition)

EPI ↔ T1w correction via field maps (`topup`) or fieldmap-less methods (SyN-SDC); see [Fundamentals → Preprocessing](../preprocessing.md).

### Atlas-based segmentation

Register atlas labels into subject space (or vice versa). Used by FreeSurfer aseg, multi-atlas + JLF, hippocampal subfield pipelines.

### Group template construction

Iterate registration + averaging to build a study-specific template (ANTs `buildtemplateparallel`). Reduces inter-subject bias.

## 5. Practical example — ANTs SyN registration

```bash
# T1w-to-MNI152 with affine + SyN
antsRegistrationSyN.sh \
    -d 3 \
    -f MNI152_T1_1mm_brain.nii.gz \
    -m sub-001_T1w_brain.nii.gz \
    -o sub-001_to_MNI_ \
    -t s            # s = rigid + affine + SyN

# Apply the same transform to the label map
antsApplyTransforms \
    -d 3 \
    -i sub-001_aparc+aseg.nii.gz \
    -r MNI152_T1_1mm_brain.nii.gz \
    -t sub-001_to_MNI_1Warp.nii.gz \
    -t sub-001_to_MNI_0GenericAffine.mat \
    -o sub-001_aparc+aseg_in_MNI.nii.gz \
    -n MultiLabel
```

Three details:

- **Bias-corrected, skull-stripped** brains as input — SyN's similarity metric is sensitive to non-brain intensities.
- **`-n MultiLabel`** for segmentations — uses majority-label interpolation, not linear.
- **Concatenate transforms in reverse order** when applying — `antsApplyTransforms` applies right-to-left.

## 6. Practical example — VoxelMorph (deep-learning registration)

```python
import voxelmorph as vxm
import tensorflow as tf

# Build a registration U-Net that predicts a displacement field
vol_shape = (160, 192, 224)
nb_unet_features = [[16, 32, 32, 32], [32, 32, 32, 32, 32, 16, 16]]
model = vxm.networks.VxmDense(vol_shape, nb_unet_features, int_steps=7)

# Loss: image similarity + smoothness on the displacement field
losses = [vxm.losses.NCC().loss, vxm.losses.Grad('l2').loss]
loss_weights = [1, 0.01]
model.compile(optimizer=tf.keras.optimizers.Adam(lr=1e-4),
              loss=losses, loss_weights=loss_weights)

# Train on pairs (moving, fixed); inference is a single forward pass
model.fit(generator, epochs=200, steps_per_epoch=100)
```

VoxelMorph ([Balakrishnan et al., 2019](https://doi.org/10.1109/TMI.2019.2897538)) replaces iterative optimisation with a learned U-Net. Inference is ~100 ms per pair on a GPU vs ~10 minutes for SyN. Accuracy is comparable on in-distribution data; OOD remains a concern.

## 7. Evaluation

- **Target registration error (TRE)** — Euclidean distance between corresponding landmarks. Gold standard when landmarks exist.
- **Dice / Jaccard on a known label** — overlap of warped masks; proxy for TRE.
- **Inverse consistency** — $T \circ T^{-1} \approx I$. Diffeomorphic algorithms minimise this by construction.
- **Visual QC** — checker-board overlays of fixed and warped moving images. Always do this on a few subjects.

## 8. Common pitfalls

- **Skull-stripping mismatch** — non-brain tissue dominates SSD/NCC; mask both images.
- **Bias-field uncorrected images** — drift across the image confuses MI.
- **Wrong pyramid schedule** — too coarse → miss fine detail; too fine → local minimum.
- **Initial misalignment** — if the centre-of-mass is far off, the first iteration may diverge; pre-align with a header-based or moments-of-inertia step.
- **Wrong interpolation for labels** — never use trilinear / cubic on integer label maps; use nearest-neighbour or majority-voting (`-n MultiLabel`).
- **Bias in cross-subject template** — if all subjects are warped to one subject's image, that subject's features dominate. Use an averaged template.

## 9. References

1. **Sotiras A, Davatzikos C, Paragios N.** Deformable medical image registration: a survey. *IEEE Trans Med Imaging.* 2013;32(7):1153-1190. [doi:10.1109/TMI.2013.2265603](https://doi.org/10.1109/TMI.2013.2265603)
2. **Maes F, Collignon A, Vandermeulen D, Marchal G, Suetens P.** Multimodality image registration by maximization of mutual information. *IEEE Trans Med Imaging.* 1997;16(2):187-198. [doi:10.1109/42.563664](https://doi.org/10.1109/42.563664)
3. **Wells WM, Viola P, Atsumi H, Nakajima S, Kikinis R.** Multi-modal volume registration by maximization of mutual information. *Med Image Anal.* 1996;1(1):35-51. [doi:10.1016/S1361-8415(01)80004-9](https://doi.org/10.1016/S1361-8415(01)80004-9)
4. **Mattes D, Haynor DR, Vesselle H, Lewellen TK, Eubank W.** PET-CT image registration in the chest using free-form deformations. *IEEE Trans Med Imaging.* 2003;22(1):120-128. [doi:10.1109/TMI.2002.806275](https://doi.org/10.1109/TMI.2002.806275)
5. **Avants BB, Epstein CL, Grossman M, Gee JC.** Symmetric diffeomorphic image registration with cross-correlation: evaluating automated labeling of elderly and neurodegenerative brain. *Med Image Anal.* 2008;12(1):26-41. [doi:10.1016/j.media.2007.06.004](https://doi.org/10.1016/j.media.2007.06.004) — SyN.
6. **Beg MF, Miller MI, Trouvé A, Younes L.** Computing large deformation metric mappings via geodesic flows of diffeomorphisms. *Int J Comput Vis.* 2005;61(2):139-157. [doi:10.1023/B:VISI.0000043755.93987.aa](https://doi.org/10.1023/B:VISI.0000043755.93987.aa) — LDDMM.
7. **Vercauteren T, Pennec X, Perchant A, Ayache N.** Diffeomorphic demons: efficient non-parametric image registration. *NeuroImage.* 2009;45(1 Suppl):S61-S72. [doi:10.1016/j.neuroimage.2008.10.040](https://doi.org/10.1016/j.neuroimage.2008.10.040)
8. **Ashburner J.** A fast diffeomorphic image registration algorithm. *NeuroImage.* 2007;38(1):95-113. [doi:10.1016/j.neuroimage.2007.07.007](https://doi.org/10.1016/j.neuroimage.2007.07.007) — DARTEL.
9. **Greve DN, Fischl B.** Accurate and robust brain image alignment using boundary-based registration. *NeuroImage.* 2009;48(1):63-72. [doi:10.1016/j.neuroimage.2009.06.060](https://doi.org/10.1016/j.neuroimage.2009.06.060) — BBR.
10. **Balakrishnan G, Zhao A, Sabuncu MR, Guttag J, Dalca AV.** VoxelMorph: a learning framework for deformable medical image registration. *IEEE Trans Med Imaging.* 2019;38(8):1788-1800. [doi:10.1109/TMI.2019.2897538](https://doi.org/10.1109/TMI.2019.2897538)
11. **Chen J, Frey EC, He Y, et al.** TransMorph: transformer for unsupervised medical image registration. *Med Image Anal.* 2022;82:102615. [doi:10.1016/j.media.2022.102615](https://doi.org/10.1016/j.media.2022.102615)
12. **Klein A, Andersson J, Ardekani BA, et al.** Evaluation of 14 nonlinear deformation algorithms applied to human brain MRI registration. *NeuroImage.* 2009;46(3):786-802. [doi:10.1016/j.neuroimage.2008.12.037](https://doi.org/10.1016/j.neuroimage.2008.12.037) — landmark benchmarking paper.
13. **ANTs documentation and wiki.** [https://github.com/ANTsX/ANTs/wiki](https://github.com/ANTsX/ANTs/wiki) — reference for `antsRegistrationSyN.sh`, transform conventions, and Jacobian / inverse-consistency tooling.
14. **Modat M, Ridgway GR, Taylor ZA, et al.** Fast free-form deformation using graphics processing units (NiftyReg `reg_f3d`). *Comput Methods Programs Biomed.* 2010;98(3):278-284. [doi:10.1016/j.cmpb.2009.09.002](https://doi.org/10.1016/j.cmpb.2009.09.002)
15. **NiftyReg.** [https://github.com/KCL-BMEIS/niftyreg](https://github.com/KCL-BMEIS/niftyreg) — B-spline free-form deformation registration tool.
16. **antsMultivariateTemplateConstruction2.sh.** [https://github.com/ANTsX/ANTs/blob/master/Scripts/antsMultivariateTemplateConstruction2.sh](https://github.com/ANTsX/ANTs/blob/master/Scripts/antsMultivariateTemplateConstruction2.sh) — diffeomorphic atlas building workflow.

## Exercises

1. **Pick a similarity metric.** Which is best for: (a) T1w ↔ T1w within subject, (b) T1w ↔ DWI b=0, (c) longitudinal T1w → halfway template? Justify.
2. **TRE vs Dice.** What does TRE measure that Dice does not? Why is TRE the "gold standard" when landmarks are available?
3. **Pyramid debugging.** A SyN registration gives a great affine fit but a poor deformable refinement. List four diagnostic checks.

??? success "Solutions"
    1. (a) SSD or NCC — same contrast. (b) MI — multi-modal. (c) NCC or MI — small contrast shifts across time, robust to drift.
    2. TRE: physical mm error at known landmarks. Dice rewards overlap area; can miss boundary-shift errors that TRE catches directly.
    3. Check bias-field correction; check skull-stripping mismatch; check pyramid smoothing schedule (too coarse at finest level?); check Jacobian for folding (negative det J).

## Where to next

[Enhancement & quality](enhancement.md) — improving images before, during, or after registration.
