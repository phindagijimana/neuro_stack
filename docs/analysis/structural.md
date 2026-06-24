# Structural morphometry

> Measuring brain anatomy: cortical thickness, surface area, subcortical volume.

## The standard pipeline

1. **Acquire** a T1-weighted MPRAGE or MP2RAGE.
2. **Preprocess** with sMRIPrep or fMRIPrep (handles bias correction, brain extraction, normalisation).
3. **Reconstruct surfaces** with FreeSurfer's `recon-all` or its DL-accelerated equivalent **FastSurfer**.
4. **Parcellate** using the Desikan-Killiany (DK), Destrieux, or HCP-MMP atlas.
5. **Extract metrics** per region: thickness, surface area, volume, curvature, sulcal depth.

The output is a per-subject table: rows = regions, columns = metrics.

## FreeSurfer's standard outputs

FreeSurfer is the reference cortical reconstruction pipeline [Fischl, 2012](https://doi.org/10.1016/j.neuroimage.2012.01.021)[^fs]; key methods papers describe surface reconstruction [Dale et al., 1999](https://doi.org/10.1006/nimg.1998.0395)[^dale], thickness estimation [Fischl & Dale, 2000](https://doi.org/10.1073/pnas.200033797)[^fd], and `aseg` segmentation [Fischl et al., 2002](https://doi.org/10.1016/S0896-6273(02)00569-X)[^aseg].

After `recon-all`, every subject has:

```text
$SUBJECTS_DIR/sub-001/
├── mri/aparc+aseg.mgz          # cortical + subcortical parcellation
├── surf/lh.thickness            # per-vertex thickness, left hemi
├── surf/rh.thickness            # right hemi
├── label/lh.aparc.annot         # DK atlas labels on the left surface
└── stats/
    ├── aseg.stats               # subcortical volumes
    ├── lh.aparc.stats           # left cortical metrics per DK region
    └── rh.aparc.stats           # right
```

The `*.stats` files are tab-delimited text — read them with pandas.

## FastSurfer [Henschel et al., 2020](https://doi.org/10.1016/j.neuroimage.2020.117012)[^fastsurfer]

`recon-all` takes ~10 hours per subject. FastSurfer replaces the slow parts (brain extraction, segmentation) with deep nets; runtime drops to ~1 hour CPU or ~10 minutes GPU. Outputs are FreeSurfer-compatible; downstream tools don't notice the difference.

If your cohort is > 50 subjects, switching to FastSurfer pays for itself in one rerun.

## ENIGMA harmonisation [Thompson et al., 2020](https://doi.org/10.1038/s41398-020-0705-1)[^enigma]

The ENIGMA consortium publishes scripts that summarise FreeSurfer outputs into a single per-subject CSV with consistent column naming. Use them when:

- You're contributing to or pulling from a meta-analysis.
- You want to make site comparisons easier later.

## A quick worked example

```python
import pandas as pd
from pathlib import Path

# Pull every subject's DK thickness into one wide DataFrame.
rows = []
for stats in Path("derivatives/freesurfer").glob("sub-*/stats/lh.aparc.stats"):
    sub = stats.parents[1].name
    df = pd.read_csv(
        stats, comment="#", sep=r"\s+", header=None,
        names=["StructName", "NumVert", "SurfArea", "GrayVol",
               "ThickAvg", "ThickStd", "MeanCurv", "GausCurv",
               "FoldInd", "CurvInd"],
    )
    df = df[["StructName", "ThickAvg"]].set_index("StructName").T
    df.index = [sub]
    rows.append(df)

cohort = pd.concat(rows)
print(cohort.shape)  # (n_subjects, ~35 regions)
```

That's a cohort-level feature table. Feed it to the classical ML in [AI / ML → Classical ML](../ai/classical-ml.md).

## Pitfalls

- **Pial-surface failures.** A bad skull strip puts the pial surface inside the bone. Visual QC is non-optional.
- **Motion.** A subject who moved during the MPRAGE has noisy surfaces. Higher thickness variance than expected = check the raw scan.
- **Cross-sectional vs longitudinal.** FreeSurfer's longitudinal stream is *not* the same as running `recon-all` twice and subtracting. Use the longitudinal stream if you have timepoints.

## Multi-site harmonisation and longitudinal pitfalls

The numbers that come out of FreeSurfer are not site-invariant. Cortical thickness and subcortical volume systematically shift with scanner manufacturer (Siemens vs GE vs Philips), field strength (1.5T vs 3T vs 7T), sequence parameters (resolution, inversion time, parallel imaging), and even the recon-all version. The [ENIGMA consortium](http://enigma.ini.usc.edu/) has documented Siemens-vs-GE biases in subcortical volume that are large enough to swamp small clinical effects. If you pool across sites without thinking, you measure the scanner.

**ComBat-style harmonisation.** [ComBat](https://doi.org/10.1093/biostatistics/kxj037) [Johnson et al., 2007](https://doi.org/10.1093/biostatistics/kxj037)[^combat_orig] was lifted from genomics by [Fortin et al., 2018](https://doi.org/10.1016/j.neuroimage.2017.11.024)[^combat_neuro] for cortical thickness — see [neuroCombat](https://github.com/Jfortin1/neuroCombat). It models each feature as

$$y_{ijk} = \alpha + X\beta + \gamma_i + \delta_i \, \epsilon_{ijk}$$

where $\gamma_i, \delta_i$ are site-specific additive/multiplicative effects estimated with empirical Bayes, and you preserve biological covariates in $X$. Works when each site contributes multiple subjects.

**When ComBat fails silently.** Site confounded with diagnosis (only one site collected cases). Tiny sites (N<10 — empirical Bayes shrinks site estimates to garbage). Residuals that aren't even approximately Gaussian. Cross-sectional ComBat applied to longitudinal data, which breaks within-subject correlation; use [longitudinal ComBat](https://doi.org/10.1016/j.neuroimage.2020.117129) [Beer et al., 2020](https://doi.org/10.1016/j.neuroimage.2020.117129)[^combat_long] for repeat scans.

**Longitudinal FreeSurfer.** [Reuter et al., 2012](https://doi.org/10.1016/j.neuroimage.2012.02.084)[^reuter] introduced a within-subject template plus iterative re-registration. Test-retest noise drops dramatically vs running cross-sectional recon-all twice and subtracting. It does *not* save you from a scanner upgrade mid-study — that's a fixed-effect shift no template can hide.

**Software version.** `recon-all` 6.0 and 7.x produce measurably different cortical thickness in the same subject. Pin the version in `dataset_description.json` and your container; if you upgrade, re-process the whole cohort, don't mix.

**The honest disclaimer.** Harmonisation reduces bias; it never eliminates it. Pre-register *site as a covariate* in your second-level GLM, AND run a sensitivity analysis without ComBat. If the headline effect survives both, you have something. If it only survives one, say so.

## References

[^fs]: Fischl B. FreeSurfer. *NeuroImage.* 2012;62(2):774-781. [doi:10.1016/j.neuroimage.2012.01.021](https://doi.org/10.1016/j.neuroimage.2012.01.021)
[^dale]: Dale AM, Fischl B, Sereno MI. Cortical surface-based analysis. I. Segmentation and surface reconstruction. *NeuroImage.* 1999;9(2):179-194. [doi:10.1006/nimg.1998.0395](https://doi.org/10.1006/nimg.1998.0395)
[^fd]: Fischl B, Dale AM. Measuring the thickness of the human cerebral cortex from MR images. *PNAS.* 2000;97(20):11050-11055. [doi:10.1073/pnas.200033797](https://doi.org/10.1073/pnas.200033797)
[^aseg]: Fischl B, Salat DH, Busa E, et al. Whole brain segmentation. *Neuron.* 2002;33(3):341-355. [doi:10.1016/S0896-6273(02)00569-X](https://doi.org/10.1016/S0896-6273(02)00569-X)
[^fastsurfer]: Henschel L, Conjeti S, Estrada S, Diers K, Fischl B, Reuter M. FastSurfer. *NeuroImage.* 2020;219:117012. [doi:10.1016/j.neuroimage.2020.117012](https://doi.org/10.1016/j.neuroimage.2020.117012)
[^enigma]: Thompson PM, Jahanshad N, Ching CRK, et al. ENIGMA and global neuroscience: a decade of large-scale studies. *Transl Psychiatry.* 2020;10:100. [doi:10.1038/s41398-020-0705-1](https://doi.org/10.1038/s41398-020-0705-1)
[^combat_orig]: Johnson WE, Li C, Rabinovic A. Adjusting batch effects in microarray expression data using empirical Bayes methods. *Biostatistics.* 2007;8(1):118-127. [doi:10.1093/biostatistics/kxj037](https://doi.org/10.1093/biostatistics/kxj037)
[^combat_neuro]: Fortin J-P, Cullen N, Sheline YI, et al. Harmonization of cortical thickness measurements across scanners and sites. *NeuroImage.* 2018;167:104-120. [doi:10.1016/j.neuroimage.2017.11.024](https://doi.org/10.1016/j.neuroimage.2017.11.024)
[^reuter]: Reuter M, Schmansky NJ, Rosas HD, Fischl B. Within-subject template estimation for unbiased longitudinal image analysis. *NeuroImage.* 2012;61(4):1402-1418. [doi:10.1016/j.neuroimage.2012.02.084](https://doi.org/10.1016/j.neuroimage.2012.02.084)
[^combat_long]: Beer JC, Tustison NJ, Cook PA, et al. Longitudinal ComBat: a method for harmonizing longitudinal multi-scanner imaging data. *NeuroImage.* 2020;220:117129. [doi:10.1016/j.neuroimage.2020.117129](https://doi.org/10.1016/j.neuroimage.2020.117129)

## Where to next

- [Voxel-based morphometry (VBM)](vbm.md) — the voxelwise grey-matter group-stats workhorse that pairs with the SBM cortical pipelines on this page.
- [Diffusion & tractography](diffusion.md) — what the white-matter side of the same brain tells you.
