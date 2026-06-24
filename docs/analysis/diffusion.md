# Diffusion & tractography

> From a 4D DWI series to a connectome: the standard pipeline.

## Where to go deeper

This page is the *analysis-side* view: from a preprocessed DWI series to streamlines, edge weights, and group statistics. The *acquisition-side* counterpart — DTI's failure modes, HARDI / multi-shell design, NODDI, DKI, MSMT-CSD compartment models, and free-water imaging ([Pasternak et al., 2009](https://doi.org/10.1002/mrm.22055)) — lives in [advanced-diffusion.md](../fundamentals/sequences/advanced-diffusion.md). When a section here references a biophysical model (NODDI's $\nu_{\mathrm{ic}}$, free-water $f$, MSMT response functions), treat that page as the load-bearing derivation; this page focuses on what you do with the resulting maps and streamlines.

## Stages

1. **Preprocess** with QSIPrep [Cieslak et al., 2021](https://doi.org/10.1038/s41592-021-01185-5)[^qsiprep] (denoising, motion + distortion correction, registration to T1).
2. **Model** the local diffusion: tensor (single-shell), CSD or NODDI (multi-shell).
3. **Track** fibres through the model field: deterministic (FACT, EuDX) or probabilistic (iFOD2, PFT).
4. **Filter** the streamlines: SIFT / SIFT2 / COMMIT corrects for the over-representation of streamlines in dense regions.
5. **Connectome**: count streamlines connecting each pair of atlas regions.

## Local models

| Model | When | Tool |
| --- | --- | --- |
| **Tensor (DTI)** | Single-shell b ≈ 1000, quick estimates of FA / MD | FSL `dtifit`, MRtrix3 `dwi2tensor` |
| **CSD** | Multi-shell, robust to crossings | MRtrix3 `dwi2fod` |
| **NODDI** | Multi-shell, microstructure indices | AMICO, NODDI Matlab toolbox |
| **DSI / DKI** | Specific high-end protocols | MRtrix3, DIPY |

For a typical research-grade multi-shell acquisition, MRtrix3 CSD is the default. DIPY (Python) is the right choice for prototyping new models [Garyfallidis et al., 2014](https://doi.org/10.3389/fninf.2014.00008)[^dipy].

## Tractography in MRtrix3 [Tournier et al., 2019](https://doi.org/10.1016/j.neuroimage.2019.116137)[^mrtrix]

A minimal pipeline:

```bash
# After QSIPrep — you have preproc_dwi.mif and a 5tt segmentation.
dwi2response dhollander preproc_dwi.mif wm.txt gm.txt csf.txt
dwi2fod msmt_csd preproc_dwi.mif wm.txt wm_fod.mif \
                                    gm.txt gm_fod.mif \
                                    csf.txt csf_fod.mif
tckgen wm_fod.mif tractogram.tck \
    -act 5tt.nii.gz -backtrack -seed_dynamic wm_fod.mif \
    -select 10M -minlength 5 -maxlength 250
tcksift2 tractogram.tck wm_fod.mif weights.txt
```

10 M streamlines is overkill for many uses; 1 M is often enough for connectome construction. Memory and disk grow linearly with `-select`.

## Connectomes

```bash
# Map streamlines to an atlas-defined connectome
tck2connectome tractogram.tck atlas.nii.gz connectome.csv \
    -tck_weights_in weights.txt -symmetric -zero_diagonal
```

The output is an `N x N` matrix where `N` is the number of atlas regions. The Desikan-Killiany atlas gives 84×84 (68 cortical + 16 subcortical). Schaefer-400 + Tian-S4 gives ≈ 450.

The QC `check_connectome_shape` helper in this repo (`neuro_handbook.qc`) is exactly the schema test you should run on every connectome before treating it as analysis-ready.

## What "edge weight" actually means

A connectome's edge can be:

- **Streamline count** — the raw output of `tck2connectome`. Easy to bias by region size.
- **Streamline density** — count divided by region surface area or volume.
- **SIFT-weighted streamline count** — the COMMIT/SIFT correction tries to match diffusion data better.
- **Mean FA along the bundle** — a microstructure-weighted metric.

Always state which one. A "DK connectome" with no specification is ambiguous.

## Pitfalls

- **b-vector flips.** A swapped axis in `.bvec` mirrors your tractogram. Check by running a known commissural seed (corpus callosum) — streamlines should cross.
- **5TT segmentation errors.** Bad cortical / WM boundaries cause streamlines to terminate prematurely. Visualise 5TT before tractography.
- **Over-interpretation.** A streamline is a *modelling artifact*, not a real axon. "There's a connection between A and B" is a hypothesis, not a measurement.

## Edge cases and specialist concerns

The standard pipeline above runs on most datasets. The list below is what separates a defensible thesis chapter from a connectome that won't survive peer review.

### HARDI angular under-sampling and response-function pitfalls

CSD's angular resolution is bounded by the maximum spherical-harmonic order $\ell_\mathrm{max}$ you can fit, which in turn is bounded by the number of unique gradient directions: $\ell_\mathrm{max} = 8$ needs $\geq 45$ directions, $\ell_\mathrm{max} = 10$ needs $\geq 66$. Under-sampling at high $b$ silently caps $\ell_\mathrm{max}$ at 6 and you lose the ability to resolve three-way crossings — exactly the regime CSD was invented for. Worse, the WM response function estimated by `dwi2response tournier` or `dwi2response dhollander` ([Dhollander et al., 2016](https://www.researchgate.net/publication/307863133_Unsupervised_3-tissue_response_function_estimation_from_single-shell_or_multi-shell_diffusion_MR_data_without_a_co-registered_T1_image)) is sensitive to the voxel set it's seeded from: pure single-fibre WM voxels in adults are scarce in paediatric, demyelinating, or oedematous brains, and a contaminated response biases every fODF in the volume. Always inspect the response with `shview` and compare across subjects before group analysis.

### Partial volume between fibre populations

A "crossing" voxel is not just two clean sticks at 90 degrees. Realistic voxels mix sharp interhemispheric callosal fibres with diffuse association bundles at a continuum of angles and at different intrinsic diffusivities. CSD assumes a *single* WM response shared across populations; when the corticospinal tract and the superior longitudinal fasciculus share a voxel, their differing axon-diameter distributions break that assumption and the smaller-amplitude peak gets absorbed into noise. Fixel-based analysis ([Raffelt et al., 2017](https://doi.org/10.1016/j.neuroimage.2016.09.029)) is the current best answer — it assigns each fODF lobe its own fibre density (FD), fibre cross-section (FC), and combined FDC metric, letting you do statistics per *fixel* instead of per voxel.

### MSMT-CSD failure modes in pathology

[MSMT-CSD](https://doi.org/10.1016/j.neuroimage.2014.07.061) ([Jeurissen et al., 2014](https://doi.org/10.1016/j.neuroimage.2014.07.061)) assumes three tissue responses — WM, GM, CSF — whose ratios are stable across the brain. In MS lesions, glioma, and chronic stroke, demyelinated WM signal can look like GM (lower anisotropy, similar mean diffusivity), and necrotic cores can look like CSF. The fitter then mis-allocates lesion signal to the GM or CSF compartment, inflating those volume fractions and *suppressing* the WM fODF inside the lesion — so tractography terminates at the lesion edge and the very tracts you wanted to study disappear. The `dhollander` algorithm is more robust than `msmt_5tt` here because it estimates responses unsupervised, but neither is immune. Mitigations: lesion-fill T1 before 5TT generation, use lesion masks to exclude tissue-response seed voxels, and report fODF amplitudes inside lesions explicitly rather than treating tract loss as ground truth.

### Tractography algorithmic bias and the validation debate

Deterministic streamline tractography (FACT, EuDX) is biased toward dominant peaks and systematically misses lateral branches; probabilistic methods (iFOD2, BedpostX + ProbtrackX) recover more anatomy at the cost of an explosion of false positives. The [Tractometer challenge](http://www.tractometer.org/) ([Maier-Hein et al., 2017](https://doi.org/10.1038/s41467-017-01285-x)) sent the same synthetic dataset to 20 groups running 96 pipelines: the median submission recovered 21 of 25 ground-truth bundles but generated four times as many invalid bundles as valid ones — and bundle-by-bundle valid/invalid ratios were uncorrelated with reported reconstruction "quality." The takeaway is not that tractography is useless; it is that *whole-brain tractogram comparisons across studies are unreliable*, and you should report sensitivity and specificity separately, ideally on a phantom or post-mortem benchmark. Anatomically constrained tractography ([Smith et al., 2012](https://doi.org/10.1016/j.neuroimage.2012.06.005)) and SIFT2 ([Smith et al., 2015](https://doi.org/10.1016/j.neuroimage.2015.06.092)) help but do not eliminate the bias.

### Connectome scaling: parcellation choice and edge-density distortion

The same tractogram routed through Desikan-Killiany (84 nodes), Glasser HCP-MMP1 (360 nodes, [Glasser et al., 2016](https://doi.org/10.1038/nature18933)), Schaefer-400 + Tian-S4 (~450 nodes), or Lausanne-250/500/1000 ([Cammoun et al., 2012](https://doi.org/10.1016/j.jneumeth.2011.09.031)) produces connectomes with mean edge densities that differ by an order of magnitude. Streamline count per edge falls roughly as $1/N^2$ for $N$ nodes, so a Lausanne-1000 connectome has many edges with zero or one streamline and a graph-theoretic small-worldness that is dominated by noise. Network metrics — clustering coefficient, modularity, rich-club coefficient — are *not* parcellation-invariant: a hub at DK resolution can fragment across several Lausanne-500 nodes and vanish from the rich club. Either justify a single resolution against your hypothesis or run a multi-resolution sensitivity analysis (the Lausanne family was designed for exactly this).

### Bundle-specific analysis: when ROI-based stats beat whole-brain

Whole-brain TBSS and connectome-wide NBS suffer from massive multiple comparisons and a "wash-out" effect: a real focal change in the uncinate fasciculus gets diluted by 100,000 voxels of stable WM. Bundle-specific approaches reverse this. [AFQ](https://yeatmanlab.github.io/AFQ/) ([Yeatman et al., 2012](https://doi.org/10.1371/journal.pone.0049790)) profiles FA/MD along 100 nodes of each of ~20 canonical tracts; [TractSeg](https://github.com/MIC-DKFZ/TractSeg) ([Wasserthal et al., 2018](https://doi.org/10.1016/j.neuroimage.2018.07.070)) uses a CNN on CSD peaks to segment 72 bundles without registration to a template. Use bundle-specific when (a) you have a tract-level hypothesis (uncinate in psychosis, arcuate in aphasia), (b) you want to localise *where along the tract* a change sits, or (c) cohort size is small and you cannot afford whole-brain correction. Use whole-brain TBSS or fixel-based when the hypothesis is genuinely diffuse (ageing, generalised MS). The full TBSS / FBA / tract-profile group-statistics machinery is in [wm-stats.md](wm-stats.md).

### Free-water modelling: a one-line pointer

Free-water elimination ([Pasternak et al., 2009](https://doi.org/10.1002/mrm.22055)) and bi-tensor fits are covered in [advanced-diffusion.md §8](../fundamentals/sequences/advanced-diffusion.md#8-free-water-imaging-pasternak); on the analysis side, the only thing to remember is that any FA or MD comparison near ventricles, oedema, or lesions without a free-water correction is reporting partial-volume noise.

### The reproducibility crisis

Run the same dataset through MRtrix3 + iFOD2 + SIFT2, FSL BedpostX + ProbtrackX, and DSI Studio + QSDR and you get three different connectomes whose pairwise edge-weight correlations sit around 0.3–0.6 ([Yeh et al., 2021](https://doi.org/10.1016/j.neuroimage.2020.117628); [Schilling et al., 2019](https://doi.org/10.1016/j.neuroimage.2019.01.077)). Connectome geometry — which edges *exist* — is more stable than edge weights, but even existence depends on streamline-count thresholds that vary by tool. The practical implications: (1) lock your pipeline before you see the data and pre-register it; (2) report tool, version, and every non-default parameter; (3) if a finding only appears with one tool, treat it as exploratory; (4) when feasible, replicate across at least two reconstruction stacks and report the intersection.

## References

[^mrtrix]: Tournier J-D, Smith R, Raffelt D, et al. MRtrix3. *NeuroImage.* 2019;202:116137. [doi:10.1016/j.neuroimage.2019.116137](https://doi.org/10.1016/j.neuroimage.2019.116137)
[^qsiprep]: Cieslak M, Cook PA, He X, et al. QSIPrep. *Nat Methods.* 2021;18(7):775-778. [doi:10.1038/s41592-021-01185-5](https://doi.org/10.1038/s41592-021-01185-5)
[^dipy]: Garyfallidis E, Brett M, Amirbekian B, et al. DIPY, a library for the analysis of diffusion MRI data. *Front Neuroinform.* 2014;8:8. [doi:10.3389/fninf.2014.00008](https://doi.org/10.3389/fninf.2014.00008)

Additional citations for *Edge cases and specialist concerns*:

- Jeurissen B, Tournier J-D, Dhollander T, Connelly A, Sijbers J. Multi-tissue constrained spherical deconvolution for improved analysis of multi-shell diffusion MRI data. *NeuroImage.* 2014;103:411-426. [doi:10.1016/j.neuroimage.2014.07.061](https://doi.org/10.1016/j.neuroimage.2014.07.061)
- Raffelt DA, Tournier J-D, Smith RE, et al. Investigating white matter fibre density and morphology using fixel-based analysis. *NeuroImage.* 2017;144(Pt A):58-73. [doi:10.1016/j.neuroimage.2016.09.029](https://doi.org/10.1016/j.neuroimage.2016.09.029)
- Maier-Hein KH, Neher PF, Houde J-C, et al. The challenge of mapping the human connectome based on diffusion tractography. *Nat Commun.* 2017;8:1349. [doi:10.1038/s41467-017-01285-x](https://doi.org/10.1038/s41467-017-01285-x)
- Smith RE, Tournier J-D, Calamante F, Connelly A. Anatomically-constrained tractography. *NeuroImage.* 2012;62(3):1924-1938. [doi:10.1016/j.neuroimage.2012.06.005](https://doi.org/10.1016/j.neuroimage.2012.06.005)
- Smith RE, Tournier J-D, Calamante F, Connelly A. SIFT2: Enabling dense quantitative assessment of brain white matter connectivity. *NeuroImage.* 2015;119:338-351. [doi:10.1016/j.neuroimage.2015.06.092](https://doi.org/10.1016/j.neuroimage.2015.06.092)
- Glasser MF, Coalson TS, Robinson EC, et al. A multi-modal parcellation of human cerebral cortex. *Nature.* 2016;536(7615):171-178. [doi:10.1038/nature18933](https://doi.org/10.1038/nature18933)
- Cammoun L, Gigandet X, Meskaldji D, et al. Mapping the human connectome at multiple scales with diffusion spectrum MRI. *J Neurosci Methods.* 2012;203(2):386-397. [doi:10.1016/j.jneumeth.2011.09.031](https://doi.org/10.1016/j.jneumeth.2011.09.031)
- Yeatman JD, Dougherty RF, Myall NJ, Wandell BA, Feldman HM. Tract profiles of white matter properties: automating fiber-quantification. *PLoS One.* 2012;7(11):e49790. [doi:10.1371/journal.pone.0049790](https://doi.org/10.1371/journal.pone.0049790)
- Wasserthal J, Neher P, Maier-Hein KH. TractSeg — fast and accurate white matter tract segmentation. *NeuroImage.* 2018;183:239-253. [doi:10.1016/j.neuroimage.2018.07.070](https://doi.org/10.1016/j.neuroimage.2018.07.070)
- Pasternak O, Sochen N, Gur Y, Intrator N, Assaf Y. Free water elimination and mapping from diffusion MRI. *Magn Reson Med.* 2009;62(3):717-730. [doi:10.1002/mrm.22055](https://doi.org/10.1002/mrm.22055)
- Yeh C-H, Jones DK, Liang X, Descoteaux M, Connelly A. Mapping structural connectivity using diffusion MRI: Challenges and opportunities. *J Magn Reson Imaging.* 2021;53(6):1666-1682. [doi:10.1016/j.neuroimage.2020.117628](https://doi.org/10.1016/j.neuroimage.2020.117628)
- Schilling KG, Nath V, Hansen C, et al. Limits to anatomical accuracy of diffusion tractography using modern approaches. *NeuroImage.* 2019;185:1-11. [doi:10.1016/j.neuroimage.2019.01.077](https://doi.org/10.1016/j.neuroimage.2019.01.077)

## Where to next

- [White-matter group statistics](wm-stats.md) — TBSS, fixel-based analysis (FBA), and tract-profile (AFQ / TractSeg / BUAN) machinery for group inference on DWI-derived scalars.
- [Functional connectivity](functional.md) — what the BOLD signal tells you about the same connections.
