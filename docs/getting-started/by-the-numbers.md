# By the numbers: typical scales

> Orientation for newcomers. Voxel sizes, TRs, file sizes, dataset scales, compute times — concrete magnitudes you can plug into a back-of-envelope estimate.

Most of the confusion in a first neuroimaging project comes from not having a sense of *scale*. Is 30 GB a lot for one subject? Is 12 hours of GPU time normal for recon? This page is a lookup table.

All numbers are rough 2025-era research norms. Clinical scans and ultra-high-field protocols differ; consult your protocol.

## Voxel sizes by modality

| Modality | Typical voxel (mm³) | Notes |
|---|---|---|
| T1w MPRAGE (3 T) | 1 × 1 × 1 | Research-grade standard; HCP uses 0.7 iso |
| T2w / FLAIR (3 T) | 1 × 1 × 1 to 1 × 1 × 3 | FLAIR often anisotropic in clinical scans |
| fMRI BOLD (3 T) | 2-3 mm iso | HCP rs-fMRI: 2 mm; ABCD: 2.4 mm; older studies 3-3.5 mm |
| DWI (3 T) | 1.5-2.5 mm iso | HCP: 1.25 mm; ABCD: 1.7 mm; clinical: 2-2.5 mm |
| Structural at 7 T | 0.5-0.8 mm iso | Sub-millimetre cortical layers become visible |
| fMRI at 7 T | 0.8-1.6 mm iso | Laminar fMRI domain |
| Infant MRI (newborn) | 0.5-0.8 mm iso | Smaller heads, smaller voxels |
| Mouse MRI (preclinical) | 0.05-0.1 mm iso | Different field strength (9.4-15 T) |
| CT (head) | 0.5 × 0.5 × 1-5 | Through-plane often coarse |
| PET | 2-4 mm iso (recon) | Intrinsic resolution worse (~4-6 mm) |

!!! tip "Beginner takeaway"
    1 mm isotropic is the safe assumption for a structural T1; 2-3 mm isotropic for BOLD; 1.5-2 mm for DWI. Anything else, look at the sidecar.

## TRs (repetition times)

| Sequence | Typical TR | Notes |
|---|---|---|
| MPRAGE T1w (3 T) | 2.0-2.5 s | Per-volume; full scan ~5-7 min |
| T2w / FLAIR | 2.5-9 s | Long TR for T2 contrast |
| rs-fMRI single-band (legacy) | 2-3 s | Pre-2010 standard |
| rs-fMRI multiband (HCP-era) | 0.7-1.0 s | MB=8 typical; faster sampling |
| Task fMRI multiband | 0.8-1.5 s | Trade SNR for sampling |
| DWI (single shell) | 6-12 s | Per-volume across the diffusion-encoded series |
| ASL | 4-5 s | Pulsed / pseudo-continuous labelling |

## Acquisition durations

| Sequence | Typical scan time | Notes |
|---|---|---|
| T1w MPRAGE | 5-7 min | Single run |
| T2w | 4-6 min | |
| FLAIR | 4-6 min | |
| DWI (b=1000, ~30 dir) | 6-10 min | Single-shell clinical-research |
| DWI multi-shell (HCP-style) | 30-60 min | Across b=1000/2000/3000 + reverse PE |
| rs-fMRI run | 6-10 min | HCP: 4 × 15 min; ABCD: 4 × 5 min |
| Task fMRI run | 5-12 min | Block / event-related design |
| ASL perfusion | 4-6 min | Often paired with M0 reference |
| Field map | 1-3 min | Fast — but required for distortion correction |

## Subject scan-session length

| Cohort type | Total session | Notes |
|---|---|---|
| Research adult (typical) | 45-75 min | T1 + DWI + 2× rs-fMRI + task = ~60 min |
| HCP Young Adult per session | ~60 min × 2 days | Famously dense |
| ABCD per session | ~120 min total | Includes breaks, paediatric |
| UK Biobank | ~35 min imaging | Brain only; multimodal but condensed |
| Pediatric (school age) | 20-40 min | Motion budget is short |
| Pediatric (sedated infant) | 30-60 min | Sleep window |
| Clinical (head MRI) | 20-30 min | Diagnostic protocol |

## File sizes

| Object | Typical size | Notes |
|---|---|---|
| Single DICOM file (1 slice) | 100 KB - 4 MB | Depends on bit depth, compression |
| One DICOM series (e.g. T1) | 50-300 MB | Hundreds of slices |
| One full DICOM scan session | 1-5 GB | All series combined |
| NIfTI T1w (compressed `.nii.gz`) | 10-30 MB | After `dcm2niix` |
| NIfTI T2w / FLAIR | 10-30 MB | |
| NIfTI DWI (~30 directions) | 50-150 MB | More volumes = larger |
| NIfTI DWI (HCP multi-shell) | 500 MB - 1.5 GB | Hundreds of volumes |
| NIfTI fMRI run | 100-400 MB | TR × duration × voxel count |
| BIDS sidecar JSON | 1-5 KB | Negligible |
| Single subject BIDS `sub-XXX/` dir | 1-5 GB | All raw modalities |
| fMRIPrep derivatives per subject | 2-8 GB | Includes confounds, warped data |
| FreeSurfer recon-all per subject | 400-700 MB | Surfaces + volumes + stats |
| Cohort of 1000 subjects (raw) | 1-5 TB | |
| Cohort of 1000 subjects (raw + derivatives) | 5-20 TB | |

## Dataset scales — the cohorts you'll meet

| Dataset | Subjects | Modalities | Reference |
|---|---|---|---|
| HCP Young Adult (HCP-1200) | ~1,200 | T1, T2, dMRI, rs/task-fMRI, MEG (subset) | Van Essen 2013 |
| HCP Development | ~1,300 | Ages 5-21 | Somerville 2018 |
| HCP Aging | ~1,200 | Ages 36-100+ | Bookheimer 2019 |
| UK Biobank Imaging | 50,000+ (target 100k) | T1, T2 FLAIR, dMRI, rs/task-fMRI | Miller 2016 |
| ABCD | ~12,000 | Longitudinal, 9-10 y at baseline | Casey 2018 |
| ADNI (1/GO/2/3) | ~3,000 cumulative | Alzheimer's biomarker cohort | Mueller 2005 |
| OASIS-3 | ~1,100 | Longitudinal, aging + AD | LaMontagne 2019 |
| PNC (Philadelphia) | ~1,400 | Youth, 8-21 y | Satterthwaite 2014 |
| BraTS (challenge) | ~2,000+ | Glioma segmentation labels | Bakas 2017 |
| OpenNeuro (platform) | 1,000+ datasets, ~50k subjects | Heterogeneous public BIDS | Markiewicz 2021 |

## Preprocessing times

Wall-clock estimates per subject on typical research hardware.

| Pipeline | CPU time | GPU time | Notes |
|---|---|---|---|
| FreeSurfer `recon-all` | 6-12 h | n/a | Single thread; `-parallel` cuts ~30% |
| FastSurfer (deep-learning) | 30-60 min | 1-2 h | GPU dominates; CPU fallback ~6 h |
| MRIQC (single subject) | 15-45 min | n/a | T1 + BOLD + DWI |
| fMRIPrep (one BOLD run) | 6-12 h | n/a | More if multiple runs / sessions |
| fMRIPrep (full subject, multi-run) | 12-24 h | n/a | |
| QSIPrep | 8-24 h | Optional GPU for eddy | Multi-shell HCP-style: 24h+ |
| sMRIPrep | 8-12 h | n/a | Surface generation dominates |
| ASLPrep | 2-4 h | n/a | |
| XCP-D (post-fMRIPrep) | 1-3 h | n/a | Confound regression, parcellation |
| dcm2niix conversion | 1-10 min | n/a | One session |

!!! tip "Beginner takeaway"
    Budget *one day per subject* end-to-end for a multi-modal pipeline. A 100-subject study is a 1-2 week compute job on a small cluster.

## GPU memory & training scales

| Workload | GPU memory needed | Notes |
|---|---|---|
| 2D U-Net (256×256 slice) | 4-8 GB | Fits on consumer GPUs |
| 3D U-Net (96³ patch) | 12-24 GB | RTX 3090 / A5000 territory |
| 3D U-Net (full 192³ volume) | 40-80 GB | A100 / H100 |
| nnU-Net 3D full-res training | 24-48 GB | Plus 2-7 days wall time |
| 3D foundation model (e.g. SAM-style) | 40-80 GB | Often multi-GPU |
| Diffusion model 3D (3D LDM) | 40 GB+ | Memory bottleneck is the 3D U-Net |
| LLM-class 7B fine-tuning | 24-40 GB | LoRA; full FT needs 80 GB+ |

Single-GPU training run for a 3D medical segmentation model: typically 1-7 days on one A100.

## Network egress (cloud data)

| Operation | Cost (2025 est.) | Notes |
|---|---|---|
| AWS S3 egress, 1 GB | $0.08-0.09 | Pricing varies by region/destination |
| Pull HCP-1200 raw (~80 TB) | Several thousand USD if egressed | Mostly used via AWS Open Data / mirror |
| Pull UK Biobank cohort | Free download to approved researcher | But local storage is yours |
| Pull a single OpenNeuro dataset (~50 GB) | ~$5 egress | Or use the AWS S3 mirror |
| Sync 1 TB to/from cluster | A few hundred USD if cloud → on-prem | Plan for it |

The lesson: process in the cloud where the data lives, or pull once and cache.

## Atlas resolutions

| Template | Common resolutions | Notes |
|---|---|---|
| MNI152NLin2009cAsym | 1 mm, 2 mm | fMRIPrep default; the "modern MNI" |
| MNI152NLin6Asym | 1 mm, 2 mm | FSL's MNI; many legacy results |
| MNI152NLin2009bAsym | 1 mm | Symmetric variant |
| HCP fsLR (surface) | 32k, 59k, 164k vertices | Cortical mid-thickness |
| fsaverage (FreeSurfer) | fsaverage{3..6}, fsaverage7 | 642 to 163k vertices/hemi |
| dHCP (neonatal) | 0.5 mm | High-res infant template |
| Schaefer parcellation | 100 to 1000 parcels | At 1 mm and 2 mm |
| AAL | 116 ROIs | 1 mm and 2 mm |

A 1 mm volumetric atlas is ~10-30 MB; 2 mm is ~3-8 MB. Surface atlases are tiny by comparison.

## Reporting conventions

| Item | Convention |
|---|---|
| Voxel-wise statistical threshold | FDR q < 0.05 or FWE p < 0.05 (cluster) |
| Cluster size for whole-brain | At least ~10-50 voxels at 2 mm (≥ ~80-400 mm³) |
| Effect size for group fMRI | Cohen's *d* alongside *t* / *p* |
| Motion threshold | FD (Power) < 0.5 mm typical; report % volumes flagged |
| Sample size justification | Cohen's *f²* or *d* + power; psychiatric studies need n in the thousands |
| Multiple comparisons (DTI) | TFCE + permutation (5000 iterations) |
| Reproducibility | Code + container hash + dataset DOI |
| Brain coverage | Report % of subjects with full FOV |

## Where to next

- [Common errors cheatsheet](common-errors.md) — the pitfalls that show up when these scales clash with your assumptions.
- [Your first NIfTI](first-nifti.md) — feel one of these voxel sizes in your hands.
- [Fundamentals → File formats](../fundamentals/file-formats.md) — what makes a NIfTI those tens of MB.
- [Fundamentals → Coordinate systems](../fundamentals/coordinate-systems.md) — what those 1 mm vs 2 mm voxels mean in world space.

## References

1. **Van Essen DC, Smith SM, Barch DM, et al.** The WU-Minn Human Connectome Project: an overview. *NeuroImage.* 2013;80:62-79. [doi:10.1016/j.neuroimage.2013.05.041](https://doi.org/10.1016/j.neuroimage.2013.05.041)
2. **Glasser MF, Sotiropoulos SN, Wilson JA, et al.** The minimal preprocessing pipelines for the Human Connectome Project. *NeuroImage.* 2013;80:105-124. [doi:10.1016/j.neuroimage.2013.04.127](https://doi.org/10.1016/j.neuroimage.2013.04.127)
3. **Miller KL, Alfaro-Almagro F, Bangerter NK, et al.** Multimodal population brain imaging in the UK Biobank prospective epidemiological study. *Nat Neurosci.* 2016;19:1523-1536. [doi:10.1038/nn.4393](https://doi.org/10.1038/nn.4393)
4. **Casey BJ, Cannonier T, Conley MI, et al.** The Adolescent Brain Cognitive Development (ABCD) study: imaging acquisition across 21 sites. *Dev Cogn Neurosci.* 2018;32:43-54. [doi:10.1016/j.dcn.2018.03.001](https://doi.org/10.1016/j.dcn.2018.03.001)
5. **Markiewicz CJ, Gorgolewski KJ, Feingold F, et al.** The OpenNeuro resource for sharing of neuroscience data. *eLife.* 2021;10:e71774. [doi:10.7554/eLife.71774](https://doi.org/10.7554/eLife.71774)
6. **Esteban O, Markiewicz CJ, Blair RW, et al.** fMRIPrep: a robust preprocessing pipeline for functional MRI. *Nat Methods.* 2019;16:111-116. [doi:10.1038/s41592-018-0235-4](https://doi.org/10.1038/s41592-018-0235-4)
7. **Henschel L, Conjeti S, Estrada S, et al.** FastSurfer — a fast and accurate deep-learning based neuroimaging pipeline. *NeuroImage.* 2020;219:117012. [doi:10.1016/j.neuroimage.2020.117012](https://doi.org/10.1016/j.neuroimage.2020.117012)
8. **Marek S, Tervo-Clemmens B, Calabro FJ, et al.** Reproducible brain-wide association studies require thousands of individuals. *Nature.* 2022;603:654-660. [doi:10.1038/s41586-022-04492-9](https://doi.org/10.1038/s41586-022-04492-9)
