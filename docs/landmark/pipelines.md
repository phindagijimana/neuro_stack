# Major pipelines

> One paragraph each on the pipelines you'll encounter, each with the primary methods paper.

## Anatomical / structural

- **FreeSurfer (`recon-all`)** ([homepage](https://surfer.nmr.mgh.harvard.edu)) — Cortical surface reconstruction + parcellation + subcortical segmentation. The reference. Slow (~10 h / subject); outputs every other surface-based tool consumes. [Fischl, 2012](https://doi.org/10.1016/j.neuroimage.2012.01.021)[^fs]; [Dale et al., 1999](https://doi.org/10.1006/nimg.1998.0395)[^dale]; [Fischl & Dale, 2000](https://doi.org/10.1073/pnas.200033797)[^fd].
- **FastSurfer** ([repo](https://github.com/Deep-MI/FastSurfer)) — Deep-learning re-implementation of `recon-all`. Same outputs, ~10 minutes GPU. [Henschel et al., 2020](https://doi.org/10.1016/j.neuroimage.2020.117012)[^fastsurfer].
- **sMRIPrep** — BIDS-app wrapper around the anatomical preprocessing in fMRIPrep.
- **ANTs** ([docs](https://github.com/ANTsX/ANTs)) `antsCorticalThickness` — Volumetric thickness; some communities prefer it. [Tustison et al., 2014](https://doi.org/10.1016/j.neuroimage.2014.05.044)[^ants_ct].

## Functional

- **fMRIPrep** ([docs](https://fmriprep.org)) — The standard BIDS-app for functional MRI preprocessing. Reads BIDS, writes BIDS-derivatives, ships a per-subject QC report. [Esteban et al., 2019](https://doi.org/10.1038/s41592-018-0235-4)[^fmriprep].
- **C-PAC** — Configurable Pipeline for the Analysis of Connectomes. Older, more customisable.
- **AFNI's `afni_proc.py`** — AFNI's official preprocessing script generator. [Cox, 1996](https://doi.org/10.1006/cbmr.1996.0014)[^afni].

## Diffusion

- **QSIPrep** ([docs](https://qsiprep.readthedocs.io)) — The fMRIPrep of diffusion. Handles preprocessing across many DWI acquisition flavours. [Cieslak et al., 2021](https://doi.org/10.1038/s41592-021-01185-5)[^qsiprep].
- **QSIRecon** — Reconstruction layer on top of QSIPrep: SS3T-CSD, MSMT-CSD, NODDI, tractography.
- **MRtrix3** ([docs](https://mrtrix.readthedocs.io)) — The reconstruction / tractography workhorse. [Tournier et al., 2019](https://doi.org/10.1016/j.neuroimage.2019.116137)[^mrtrix].
- **DIPY** ([docs](https://dipy.org)) — Python-native diffusion library. Best for prototyping new models. [Garyfallidis et al., 2014](https://doi.org/10.3389/fninf.2014.00008)[^dipy].
- **FSL DTI / BedpostX / ProbtrackX** ([docs](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/FDT)) — The legacy diffusion stack. [Jenkinson et al., 2012](https://doi.org/10.1016/j.neuroimage.2011.09.015)[^fsl].

## Specialist

- **HippUnfold** ([docs](https://hippunfold.readthedocs.io)) — Unfolds the hippocampus into a 2D surface for sharper analysis of subfields. [DeKraker et al., 2022](https://doi.org/10.7554/eLife.77945)[^hippunfold].
- **MELD** ([repo](https://github.com/MELDProject/meld_classifier)) — Lesion detection in epilepsy patients. Deep learning on FreeSurfer surfaces. [Spitzer et al., 2022](https://doi.org/10.1093/brain/awac224)[^meld].
- **MRIQC** ([docs](https://mriqc.readthedocs.io)) — Automated QC reports for raw T1w, T2w, BOLD. Always run it. [Esteban et al., 2017](https://doi.org/10.1371/journal.pone.0184661)[^mriqc].
- **PETPrep** — BIDS-app for PET preprocessing.
- **NiBabies / Infant-FS** — Paediatric variants.
- **Nighres** — High-resolution / 7 T cortical processing. [Huntenburg et al., 2018](https://doi.org/10.1007/s10548-018-0617-z)[^nighres].

## Decision quick-reference

| You have | Use |
|---|---|
| T1w + want cortical surfaces | FreeSurfer or FastSurfer |
| Task / resting fMRI | fMRIPrep |
| DWI for tractography or microstructure | QSIPrep + QSIRecon (or MRtrix3 directly) |
| Big cohort, slow `recon-all` is the bottleneck | Switch to FastSurfer |
| Hippocampal subfields | HippUnfold |
| PET | PETPrep |
| Lesion detection in epilepsy | MELD |
| Infant data | NiBabies |

## References

[^fs]: Fischl B. FreeSurfer. *NeuroImage.* 2012;62(2):774-781.
[^dale]: Dale AM, Fischl B, Sereno MI. Cortical surface-based analysis. I. Segmentation and surface reconstruction. *NeuroImage.* 1999;9(2):179-194.
[^fd]: Fischl B, Dale AM. Measuring the thickness of the human cerebral cortex from magnetic resonance images. *PNAS.* 2000;97(20):11050-11055.
[^fastsurfer]: Henschel L, Conjeti S, Estrada S, Diers K, Fischl B, Reuter M. FastSurfer — a fast and accurate deep learning based neuroimaging pipeline. *NeuroImage.* 2020;219:117012.
[^ants_ct]: Tustison NJ, Cook PA, Klein A, et al. Large-scale evaluation of ANTs and FreeSurfer cortical thickness measurements. *NeuroImage.* 2014;99:166-179.
[^fmriprep]: Esteban O, Markiewicz CJ, Blair RW, et al. fMRIPrep: a robust preprocessing pipeline for functional MRI. *Nat Methods.* 2019;16(1):111-116.
[^afni]: Cox RW. AFNI: software for analysis and visualization of functional magnetic resonance neuroimages. *Comput Biomed Res.* 1996;29(3):162-173.
[^qsiprep]: Cieslak M, Cook PA, He X, et al. QSIPrep: an integrative platform for preprocessing and reconstructing diffusion MRI data. *Nat Methods.* 2021;18(7):775-778.
[^mrtrix]: Tournier J-D, Smith R, Raffelt D, et al. MRtrix3. *NeuroImage.* 2019;202:116137.
[^dipy]: Garyfallidis E, Brett M, Amirbekian B, et al. DIPY, a library for the analysis of diffusion MRI data. *Front Neuroinform.* 2014;8:8.
[^fsl]: Jenkinson M, Beckmann CF, Behrens TEJ, Woolrich MW, Smith SM. FSL. *NeuroImage.* 2012;62(2):782-790.
[^hippunfold]: DeKraker J, Haast RAM, Yousif MD, et al. Automated hippocampal unfolding for morphometry and subfield segmentation with HippUnfold. *eLife.* 2022;11:e77945.
[^meld]: Spitzer H, Ripart M, Whitaker K, et al. Interpretable surface-based detection of focal cortical dysplasias. *Brain.* 2022;145(11):3859-3871.
[^mriqc]: Esteban O, Birman D, Schaer M, Koyejo OO, Poldrack RA, Gorgolewski KJ. MRIQC: Advancing the automatic prediction of image quality in MRI from unseen sites. *PLoS One.* 2017;12(9):e0184661.
[^nighres]: Huntenburg JM, Steele CJ, Bazin P-L. Nighres: processing tools for high-resolution neuroimaging. *GigaScience.* 2018;7(7):giy082.

## Where to next

[BIDS-app workflows](bids-apps.md) — the CLI shape they all share, and how to chain them.
