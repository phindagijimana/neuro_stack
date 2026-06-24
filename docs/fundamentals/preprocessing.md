# Preprocessing overview

Raw MRI volumes are not analysis-ready. A handful of preprocessing steps are nearly universal, and most labs no longer hand-roll them — they delegate to a community BIDS-app.

```mermaid
flowchart LR
    R[Raw NIfTI] --> Q[Format + QC check]
    Q --> D[Denoising +<br/>bias correction]
    D --> M[Motion correction<br/>4D only]
    M --> DC[Distortion correction<br/>EPI only]
    DC --> BX[Brain extraction]
    BX --> CR[Cross-modal<br/>coregistration]
    CR --> SN[Spatial<br/>normalisation]
    SN --> TS[Tissue segmentation]
    SN --> SR[Surface reconstruction]
    TS --> A[Analysis-ready<br/>BIDS derivatives]
    SR --> A
    style R fill:#fff,stroke:#888
    style A fill:#e0e0ff,stroke:#444
```

*<small>The universal MRI preprocessing pipeline. Each block has many implementations; BIDS apps standardise the chain. Original figure.</small>*

## The universal steps

| Step | What it does | When |
| --- | --- | --- |
| **Format check** | BIDS validation, header sanity | Once per dataset |
| **Denoising / bias correction** | Remove scanner artifacts, intensity inhomogeneity | All modalities |
| **Motion correction** | Align volumes across time (fMRI, DWI) | 4D modalities |
| **Distortion correction** | Correct susceptibility distortions using field maps | EPI sequences (fMRI, DWI) |
| **Brain extraction** | Skull strip; mask the brain | All modalities |
| **Coregistration** | Align modalities within a subject | Multi-modal sessions |
| **Spatial normalisation** | Warp to a standard template (MNI, fsaverage) | Group analyses |
| **Tissue segmentation** | Grey / white / CSF labels | Most pipelines |
| **Surface reconstruction** | Build cortical surface mesh | Surface-based pipelines |

Each step has many implementations. Each implementation has decades of papers behind it. You do not need to reinvent them.

## Use a BIDS-app

A **BIDS-app** is a containerised, opinionated pipeline that consumes a BIDS dataset and produces a BIDS-derivatives dataset. The dominant ones:

- **fMRIPrep** ([docs](https://fmriprep.org)) — functional MRI preprocessing [Esteban et al., 2019](https://doi.org/10.1038/s41592-018-0235-4)[^fmriprep].
- **QSIPrep** ([docs](https://qsiprep.readthedocs.io)) — diffusion MRI preprocessing [Cieslak et al., 2021](https://doi.org/10.1038/s41592-021-01185-5)[^qsiprep].
- **sMRIPrep** — structural MRI preprocessing.
- **MRIQC** ([docs](https://mriqc.readthedocs.io)) — automated quality control reports [Esteban et al., 2017](https://doi.org/10.1371/journal.pone.0184661)[^mriqc].
- **PETPrep** — PET preprocessing.
- **HippUnfold**, **MELD**, **NiBabies**, **NiRodents** — modality / population specific.

They all run with the same CLI shape:

```bash
docker run --rm \
  -v $PWD/bids_dataset:/data:ro \
  -v $PWD/derivatives:/out \
  nipreps/fmriprep:24.0.0 /data /out participant \
  --fs-license-file /opt/fs_license.txt
```

The argument order — input, output, analysis-level — is part of the BIDS-app spec, so the same orchestration script works for all of them.

## Why this matters for data engineering

From a pipeline-engineering perspective, BIDS-apps give you four big things for free:

1. **Containerisation** — pinned, reproducible images.
2. **Idempotency** — most BIDS-apps skip already-completed work.
3. **Provenance** — output `dataset_description.json` records the BIDS-app version, key parameters, and a citation graph.
4. **Schema enforcement** — input validation happens before compute.

That covers four of the five pillars from [Data engineering → The five pillars](../data-engineering/five-pillars.md). The fifth — observability — is what you add on top.

## Pitfalls

- **TemplateFlow downloads.** Many BIDS-apps fetch templates at runtime. On HPC nodes without network access, pre-populate `${TEMPLATEFLOW_HOME}` before the run.
- **FreeSurfer license.** `recon-all` (and anything that wraps it) needs a `license.txt`. Free, but you have to request it from the FreeSurfer site.
- **Long runtimes.** `recon-all` is ~10 h per subject on CPU. FastSurfer is the DL-accelerated drop-in if your throughput matters.
- **Resource sizing.** fMRIPrep peaks at ~16 GB RAM and uses many cores; QSIPrep is heavier still. Look at the docs before sizing Slurm requests.

## Failure modes — what goes wrong in practice

!!! tip "Beginner takeaway"
    Every preprocessing step has one or two characteristic ways it fails. Knowing the symptom → cause → fix triplet is what separates "ran fMRIPrep once" from "can run fMRIPrep on a real cohort".

The pipeline above is the happy path. Below is the failure catalogue.

### Brain extraction fails on pediatric or pathological brains

- **Symptom** — BET drops too much frontal lobe or chunks of cerebellum; FreeSurfer's skull-strip misses the skull base; the brain mask has a "bite" out of one side.
- **Cause** — classical methods were tuned on adult, neurotypical, lesion-free brains. Pediatric brains have different T1 contrast; tumours / oedema / large ventricles violate the shape prior.
- **Fix** — switch to a learned, domain-robust extractor: **SynthStrip** ([Hoopes et al., 2022](https://doi.org/10.1016/j.neuroimage.2022.119474))[^synthstrip] or **HD-BET** ([Isensee et al., 2019](https://doi.org/10.1002/hbm.24750))[^hdbet]. Both handle pediatric, glioma, and post-surgical brains far better than BET. As a last resort, hand-edit the mask in ITK-SNAP / 3D Slicer.

### Topup vs SyN-SDC distortion correction

- **Symptom** — EPI ventral frontal cortex still looks compressed after preprocessing, or geometry doesn't match the T1 even after coregistration.
- **Cause** — `topup` needs a reversed phase-encode acquisition (a "blip-up / blip-down" pair); SyN-based fieldmap-less correction (the fMRIPrep `--use-syn-sdc` path) needs a *clean T1* and a plausible distortion prior.
- **When SyN fails** — severe susceptibility (7 T, dental hardware), missing T1, or post-surgical anatomy that breaks the registration prior. Don't trust SyN-SDC silently; eyeball the report.
- **Fix** — acquire reversed-PE volumes as protocol policy. If the data is already collected without them, use `pepolar` if you have *any* short reverse-PE scan, otherwise SyN-SDC with manual QC.

### N4 bias correction over-corrects in low-SNR regions

- **Symptom** — bright hyperintense rim around the cortex; signal drop in the centre of the brain; "ghostly" intensity gradients on the QC slice.
- **Cause** — N4 fits a smooth multiplicative field; in low-SNR regions (cerebellum, brainstem) it over-fits.
- **Fix** — shorten the convergence schedule, mask aggressively before correction (use a generous brain mask, not the head), and run N4 twice with an intermediate mask refinement rather than a single deep pass.

### FreeSurfer recon-all pial-surface errors

The single most common cause of `recon-all` QC failure: the pial surface includes dura, the dural sinus, or skull. Cortical thickness is then wildly over-estimated near the parietal vertex or the temporal pole.

- **Cause** — high-intensity dura is misclassified as grey matter.
- **Fix** — edit `wm.mgz` (white-matter cuts) or `brain.finalsurfs.mgz` (manual control points), then rerun with `recon-all -autorecon-pial -subjid <id>`. The [andysbrainbook FreeSurfer-edits chapter](https://andysbrainbook.readthedocs.io/en/latest/FreeSurfer/FS_ShortCourse/FS_07_Editing.html) walks through the gestures.

### Slice-timing correction for multi-band sequences

- **Symptom** — task GLMs fit poorly, especially for fast (<1 s) TRs.
- **Cause** — simultaneous multi-slice (SMS / multiband) acquisitions invalidate "ascending" / "interleaved" / "descending" assumptions. Multiple slices are excited together, then stepped by a multiband factor.
- **Fix** — *never* infer slice timing from the protocol name. Read the `SliceTiming` field from the BIDS JSON sidecar — it lists the acquisition time of every slice in seconds. fMRIPrep does this automatically; if you're rolling your own correction, mirror it.

### Eddy-current correction on small cohorts

- **Symptom** — DWI tractography crosses to the wrong hemisphere or produces missing tracts.
- **Cause** — `eddy_correct` (the old tool) rotates the volumes but does *not* rotate the `.bvec` directions. Tractography then integrates along the wrong directions.
- **Fix** — use FSL `eddy` (the newer one), which rotates bvecs internally. If stuck with `eddy_correct`, apply a bvec rotation step using the eddy-output transforms (`fdt_rotate_bvecs`).

### Coregistration cost-function choice

- **Symptom** — partial-volume regions (cortical ribbon, brainstem) silently misalign; whole-brain Dice looks fine.
- **Cause** — wrong similarity metric for the modality pair. Sum-of-squared-differences and normalised cross-correlation assume intensity scales match; mutual information assumes only a joint-histogram relationship.
- **Fix** — **NMI / MI** for cross-modal (T1 ↔ EPI, T1 ↔ FLAIR, T1 ↔ PET); **NCC or SSD** for intra-modal, same-contrast. For T1 ↔ EPI specifically, use **boundary-based registration (BBR)** when a FreeSurfer surface is available — it dominates pure intensity-based methods.

## Distortion correction — picking a method

The "topup vs SyN-SDC" failure-mode entry above is the symptom view. Here is the design-time view: a comparison across the three families of EPI distortion correction, so you can pick before you scan rather than debug afterwards.

| Method | Requires | Accuracy | Cost | Fails when |
| --- | --- | --- | --- | --- |
| **[topup](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup) (blip-up/down)** | Reversed-PE pair acquired in-session | Best when data are clean | Extra ~30 s of scan time | One direction is motion-corrupted; PE directions mislabelled in BIDS |
| **Fieldmap-based (`gre_field_mapping`)** | Dedicated B0 fieldmap acquisition | Good; gives voxel-displacement map directly | Extra ~1 min of scan time; sequence setup | Subject motion between fieldmap and EPI; phase wraps at long TE |
| **[Synb0-DisCo](https://github.com/MASILab/Synb0-DISCO)** | T1w only — DL synthesises a distortion-free b=0 | Adequate when no fieldmap exists | Zero scanner cost; GPU at processing time | T1w is poor quality; DL OOD on non-adult anatomy |
| **SyN-SDC (fieldmap-less SyN)** | T1w only — non-linear EPI → T1w | Adequate; fMRIPrep's fallback | Pure compute cost | Strong distortions near sinus / ear canals overwhelm regularisation |

Cost ordering: topup > fieldmap > Synb0/SyN-SDC, in scanner time and setup complexity. Accuracy roughly tracks cost when everything works.

**Why ASL and DWI typically choose differently from fMRI.** [DWI](sequences/dwi.md) has very high distortion (long readouts, low bandwidth) and the diffusion-weighted volumes are useless for image registration; topup using the b=0 volumes is the standard ([QSIPrep](https://qsiprep.readthedocs.io) defaults to it). [ASLPrep](https://www.nitrc.org/projects/aslprep) acquires very short labelled/control pairs where a separate fieldmap usually does not survive the perfusion contrast; Synb0-DisCo or SyN-SDC are more common. fMRI sits in the middle: topup when reversed-PE was acquired, otherwise fieldmap, with synthetic methods as a fallback. If you cannot identify which method your BIDS-app actually ran, look at the [fMRIPrep](https://fmriprep.org) or [QSIPrep](https://qsiprep.readthedocs.io) HTML report — both document the per-subject fieldmap-selection decision.

## Pipeline choice — roll your own vs adopt a BIDS-app

There is a spectrum from "raw FSL scripts in bash" to "off-the-shelf BIDS-app, no flags".

```mermaid
flowchart LR
    A[Raw FSL/AFNI/ANTs<br/>shell scripts] --> B[nipype custom<br/>workflow]
    B --> C[BIDS-app + flags]
    C --> D[BIDS-app defaults]
    A -.->|highest control,<br/>highest cost| Z[ ]
    D -.->|lowest control,<br/>lowest cost| Z
    style A fill:#ffe0e0,stroke:#a44
    style D fill:#e0ffe0,stroke:#4a4
    style Z fill:#fff,stroke:#fff
```

*<small>The preprocessing-pipeline spectrum. Most labs should sit between C and D. Original figure.</small>*

**When to adopt a BIDS-app default.** You are a clinical research group, your cohort matches the BIDS-app's training population, you want reviewer-defensible provenance, you do not have a methodologist on staff. This is the right answer for ~80% of projects — typically [fMRIPrep](https://fmriprep.org), [QSIPrep](https://qsiprep.readthedocs.io), [sMRIPrep](https://www.nipreps.org/smriprep/), or [FastSurfer](https://github.com/Deep-MI/FastSurfer) as a `recon-all` drop-in.

**When to customise via flags.** You have an unusual acquisition (multi-echo, sub-millimetre, 7T, pediatric); you need a specific output space; you want to disable a step your QC says is harming you. Stay within the BIDS-app flag surface — every flag you set is a thing you must justify in methods.

**When to write a [nipype](https://nipype.readthedocs.io/) workflow.** You are doing something the BIDS-apps do not support (custom field-map handling, multi-modal fusion, lesion-aware steps for cohorts like [MELD](https://meldproject.github.io/)). You accept the cost of writing, testing, containerising, and documenting it.

**When to roll raw shell scripts.** Almost never. The reproducibility tax is too high. If you find yourself here, ask whether a [nipype](https://nipype.readthedocs.io/) port or a fork of an existing BIDS-app is cheaper in the long run.

The cost of "I just need to change one step" is rarely one step — it is one step plus a year of explaining why your derivatives differ from everyone else's.

### Decision section — roll your own vs adopt a BIDS-app (advanced)

The narrative above is the qualitative answer. Below is the decision you actually defend in a thesis committee or grant: numbers, trade-offs by axis, and a flowchart you can point at.

**Speed — rough wall-clock per subject.** These are order-of-magnitude figures for a structural + single fMRI run + single-shell DWI session on a modern CPU with ~16 cores, no GPU acceleration of [FreeSurfer](https://surfer.nmr.mgh.harvard.edu).

| Pipeline | Per-subject wall clock | Notes |
| --- | --- | --- |
| Hand-rolled [FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki) + [ANTs](http://stnava.github.io/ANTs/) shell | 6-10 h | Dominated by `antsRegistrationSyN` (~2 h) and `recon-all` (~10 h CPU) |
| [fMRIPrep](https://fmriprep.org) (T1w + 1 BOLD, with recon-all) | 10-14 h | recon-all is the long pole; `--fs-no-reconall` drops to ~3 h |
| [fMRIPrep](https://fmriprep.org) (`--fs-no-reconall`, [FastSurfer](https://github.com/Deep-MI/FastSurfer) on GPU) | 1-2 h | The throughput config most cohorts now run |
| [QSIPrep](https://qsiprep.readthedocs.io) (single-shell, [topup](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup) + [eddy](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy)) | 3-6 h | `eddy_cuda` on GPU is ~3-5x faster than CPU `eddy` |
| [sMRIPrep](https://www.nipreps.org/smriprep/) only (no fMRI/DWI) | 8-12 h | recon-all dominated; same FastSurfer caveat |

The hand-rolled column is *not* faster on average. Where it wins is on a single sequence you can skip steps for (e.g. T1-only volumetry without surfaces ≈ 30 min). Where it loses is when you re-derive cross-modal registration, fieldmap selection, and confound regression by hand — those are the steps a BIDS-app already wrote for you and tested across thousands of sites.

**Accuracy — when fMRIPrep's confounds actually beat hand-tuned.** The honest answer depends on the cohort and the downstream model.

- **fMRIPrep wins** when the cohort is heterogeneous (multi-site, mixed scanners, mixed motion). The [aCompCor](https://doi.org/10.1016/j.neuroimage.2007.04.042) + 6-motion + global signal stack in the confounds TSV is competitive with cohort-specific tuning ([Ciric et al., 2017](https://doi.org/10.1016/j.neuroimage.2017.03.020)). When a reviewer asks "did you regress out the same thing as everyone else?", you can say yes.
- **Hand-tuned wins** when you have prior knowledge the generic pipeline ignores: a known physiological-noise regressor (RETROICOR with recorded cardiac / respiratory), a custom ICA-AROMA variant trained on your scanner, or task-specific HRF modelling that needs the residuals from a particular nuisance model. The marginal gain over fMRIPrep's defaults on a single-site, low-motion adult cohort is usually small (1-3% variance explained).
- **fMRIPrep loses** when the cohort is OOD for its training assumptions — neonates (use [NiBabies](https://www.nipreps.org/nibabies/)), severe pathology that breaks normalisation, novel acquisitions (multi-echo with non-standard echo counts, sub-millimetre 7T).

[Bhagwat et al., 2021](https://doi.org/10.1371/journal.pcbi.1008979)[^bhagwat2021] is the canonical cross-pipeline harmonisation paper: different pipelines on the same data produce non-negligibly different volumes / thicknesses, and the disagreement is itself site-dependent. The takeaway is *not* "all pipelines are equally good"; it is "report your pipeline version and never mix derivatives across pipelines without a harmonisation step ([ComBat](https://github.com/Jfortin1/ComBatHarmonization), CovBat)."

**Maintainability cost.** The expensive parts of running a BIDS-app are not the science — they are the engineering tail:

- **Docker / Singularity pulls.** A pinned `nipreps/fmriprep:24.1.1` image is ~12 GB; QSIPrep is similar. Mirror it locally on HPC; rebuilding the upstream image with a different base layer is a non-starter mid-project.
- **Version pinning.** Pin to a *minor* version (`24.1.x`) for a study, not `latest`. The [release notes](https://fmriprep.org/en/stable/changes.html) sometimes change defaults that move group statistics by 1-2%. Lock the version in your dataset's `dataset_description.json` GeneratedBy block.
- **Atlas / template updates.** [TemplateFlow](https://www.templateflow.org/) versions drift; lock the resolution and version you use (`MNI152NLin2009cAsym:res-2`).
- **FreeSurfer license.** Required, free, but expires per institution — keep it under config management.
- **Re-running on container upgrades.** When you upgrade fMRIPrep mid-cohort, you re-run *everyone* or you mix derivatives. Budget for a full re-run when the major version bumps.

Roll-your-own avoids the container-pull tax but pays it back in script maintenance, environment drift (`conda` solver churn), and an undocumented oral tradition.

**When classical scripts still win.** Despite all of the above, there are real cases for not adopting a BIDS-app:

- **Bespoke artifact correction** — a scanner-specific spike / RF-leak pattern that needs a custom filter before any BIDS-app step.
- **Custom multi-band reconstruction** — vendor-proprietary `.dat` files, [Pulseq](https://pulseq.github.io/) sequences, or in-house GRAPPA recon.
- **Novel sequences** — MR fingerprinting, multi-parametric mapping ([hMRI](https://hmri-group.github.io/hMRI-toolbox/)), spiral readouts, ZTE / UTE. The BIDS-app world does not yet have a canonical pipeline.
- **Infants and severe pathology** — large lesions, hydrocephalus, post-surgical anatomy. [NiBabies](https://www.nipreps.org/nibabies/) and lesion-aware variants ([BIANCA](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/BIANCA), [LST](https://www.applied-statistics.de/lst.html)) help but often need wrapping in a custom workflow.
- **Methods development** — if your paper *is* the preprocessing step, you cannot evaluate it inside an opinionated pipeline.

```mermaid
flowchart TD
    Q1{N >= 50 subjects<br/>from a single site?}
    Q2{Cohort matches BIDS-app<br/>training population?<br/>(adult, no severe pathology)}
    Q3{Novel acquisition?<br/>(multi-echo, 7T, MRF,<br/>sub-mm, infants)}
    Q4{Methodologist on staff<br/>+ time budget for<br/>maintenance?}
    BA[Adopt BIDS-app default<br/>fMRIPrep / QSIPrep / sMRIPrep]
    BF[BIDS-app with documented flags<br/>justify each flag in methods]
    NP[nipype workflow<br/>or BIDS-app fork]
    HR[Hand-rolled FSL/ANTs<br/>last resort, justify in thesis]
    Q1 -->|yes| Q2
    Q1 -->|no| Q3
    Q2 -->|yes| BA
    Q2 -->|no| Q3
    Q3 -->|no| BF
    Q3 -->|yes| Q4
    Q4 -->|yes| NP
    Q4 -->|no| HR
    style BA fill:#e0ffe0,stroke:#4a4
    style BF fill:#fff3cd,stroke:#a84
    style NP fill:#ffe0cc,stroke:#a64
    style HR fill:#ffe0e0,stroke:#a44
```

*<small>The decision the methods section has to defend. Single-site, in-distribution cohorts collapse to the green branch. Original figure.</small>*

The default position is the green branch. Every step away from it costs reviewer goodwill and your own time; spend that cost on something the science requires, not on the satisfaction of rolling your own.

## Quality-control gates

Preprocessing should *fail loudly* at gates and *warn quietly* elsewhere. A failure gate stops the pipeline and excludes the subject from downstream analysis; a warning is logged but the run continues.

| Step | Gate or warn? | Why |
| --- | --- | --- |
| BIDS validation | **Gate** | Wrong metadata corrupts every downstream step |
| Brain extraction Dice vs reference | **Gate** | A bad mask poisons coregistration and normalisation |
| Coregistration final cost value | **Warn** | Numeric metric, hard threshold is brittle |
| Normalisation Jacobian negative voxels | **Gate** | Folding means the warp is non-diffeomorphic |
| Motion FD spikes (fMRI) | **Warn** | Mark for scrubbing downstream, do not exclude here |
| `recon-all` exit code + `IsRunning.lh` flag | **Gate** | Surface reconstruction silently fails otherwise |

Expose every gate decision to downstream code via a BIDS-derivatives sidecar (a `_desc-qc_bold.json` with `pass: false` and the reason) so cohort analyses can filter without re-deriving QC. See [Neuroimaging Analysis → QC](../analysis/qc.md) for the cohort-level view.

## When preprocessing breaks the science

A pipeline can be technically correct and still erase the signal you were paid to find. Common own-goals:

- **Smoothing kernel ≫ effect size.** A 12 mm FWHM Gaussian washes out a 3 mm focal activation. Pick the kernel from the expected effect, not the protocol default.
- **Aggressive motion scrubbing biases low-motion groups.** Censoring frames with FD > 0.2 mm differentially removes data from kids, patients, and older subjects. The remaining data is "cleaner" *and* biased ([Power et al., 2014](https://doi.org/10.1016/j.neuroimage.2013.08.048))[^power2014]. Report the per-group censored fraction; consider FD as a continuous nuisance regressor instead of a hard threshold.
- **Defacing destroys the orbital frontal cortex.** Standard defacing tools blur or excise voxels near the face — including OFC grey matter. Surface reconstruction near the orbital frontal cortex then fails. Use *skull-stripping* before sharing instead, or a face-only defacer (`mri_reface`, `pydeface --applyto`) tested against your downstream pipeline. See [Governance → Privacy and HIPAA/GDPR](../governance/privacy-and-hipaa-gdpr.md).
- **High-pass filter cutoff < $1/T_{\text{task}}$.** A 1/100 Hz filter on a 120 s block design removes the task fundamental. Match the cutoff to the longest task period you care about.
- **Normalising to the wrong template.** A pediatric cohort warped to adult MNI152 silently distorts ventricular and cerebellar structures. Pin the right template (NKI-pediatric, UNC neonate) via TemplateFlow.

## Visual references

- **fMRIPrep workflow diagram (official).** [https://fmriprep.org/en/stable/workflows.html](https://fmriprep.org/en/stable/workflows.html) — annotated per-step pipeline figures published with the tool.
- **QSIPrep workflow diagram.** [https://qsiprep.readthedocs.io/en/latest/preprocessing.html](https://qsiprep.readthedocs.io/en/latest/preprocessing.html) — diffusion-specific preprocessing chain with illustrations.
- **MRIQC group report examples.** [https://mriqc.readthedocs.io/en/stable/reports.html](https://mriqc.readthedocs.io/en/stable/reports.html) — what the per-subject and cohort QC reports look like.
- **FreeSurfer surface-reconstruction wiki.** [https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all](https://surfer.nmr.mgh.harvard.edu/fswiki/recon-all) — figures of every `recon-all` stage.
- **ANTs registration tutorial.** [https://github.com/ANTsX/ANTs/wiki/Anatomy-of-an-antsRegistration-call](https://github.com/ANTsX/ANTs/wiki/Anatomy-of-an-antsRegistration-call) — illustrated step-through.

## References

[^fmriprep]: Esteban O, Markiewicz CJ, Blair RW, et al. fMRIPrep: a robust preprocessing pipeline for functional MRI. *Nat Methods.* 2019;16(1):111-116. [doi:10.1038/s41592-018-0235-4](https://doi.org/10.1038/s41592-018-0235-4)
[^qsiprep]: Cieslak M, Cook PA, He X, et al. QSIPrep: an integrative platform for preprocessing and reconstructing diffusion MRI data. *Nat Methods.* 2021;18(7):775-778. [doi:10.1038/s41592-021-01185-5](https://doi.org/10.1038/s41592-021-01185-5)
[^mriqc]: Esteban O, Birman D, Schaer M, Koyejo OO, Poldrack RA, Gorgolewski KJ. MRIQC: Advancing the automatic prediction of image quality in MRI from unseen sites. *PLoS One.* 2017;12(9):e0184661. [doi:10.1371/journal.pone.0184661](https://doi.org/10.1371/journal.pone.0184661)
[^synthstrip]: Hoopes A, Mora JS, Dalca AV, Fischl B, Hoffmann M. SynthStrip: skull-stripping for any brain image. *NeuroImage.* 2022;260:119474. [doi:10.1016/j.neuroimage.2022.119474](https://doi.org/10.1016/j.neuroimage.2022.119474)
[^hdbet]: Isensee F, Schell M, Pflueger I, et al. Automated brain extraction of multisequence MRI using artificial neural networks. *Hum Brain Mapp.* 2019;40(17):4952-4964. [doi:10.1002/hbm.24750](https://doi.org/10.1002/hbm.24750)
[^power2014]: Power JD, Mitra A, Laumann TO, Snyder AZ, Schlaggar BL, Petersen SE. Methods to detect, characterize, and remove motion artifact in resting state fMRI. *NeuroImage.* 2014;84:320-341. [doi:10.1016/j.neuroimage.2013.08.048](https://doi.org/10.1016/j.neuroimage.2013.08.048)
[^bhagwat2021]: Bhagwat N, Barry A, Dickie EW, et al. Understanding the impact of preprocessing pipelines on neuroimaging cortical surface analyses. *PLoS Comput Biol.* 2021;17(7):e1008979. [doi:10.1371/journal.pcbi.1008979](https://doi.org/10.1371/journal.pcbi.1008979)

- **Schilling KG, Blaber J, Hansen C, et al.** Synthesized b0 for diffusion distortion correction (Synb0-DisCo). *Magn Reson Imaging.* 2020;64:62-70. [doi:10.1016/j.mri.2019.05.008](https://doi.org/10.1016/j.mri.2019.05.008)
- **Andersson JLR, Skare S, Ashburner J.** How to correct susceptibility distortions in spin-echo echo-planar images: application to diffusion tensor imaging (`topup`). *NeuroImage.* 2003;20(2):870-888. [doi:10.1016/S1053-8119(03)00336-7](https://doi.org/10.1016/S1053-8119(03)00336-7)
- **Henschel L, Conjeti S, Estrada S, Diers K, Fischl B, Reuter M.** FastSurfer — A fast and accurate deep learning based neuroimaging pipeline. *NeuroImage.* 2020;219:117012. [doi:10.1016/j.neuroimage.2020.117012](https://doi.org/10.1016/j.neuroimage.2020.117012)
- **Spitzer H, Ripart M, Whitaker K, et al.** Interpretable surface-based detection of focal cortical dysplasias (MELD Graph). *Brain.* 2022;145(11):3859-3871. [doi:10.1093/brain/awac224](https://doi.org/10.1093/brain/awac224)
- **NiBabies.** Neonatal preprocessing pipeline. [https://www.nipreps.org/nibabies/](https://www.nipreps.org/nibabies/)
- **Ciric R, Wolf DH, Power JD, et al.** Benchmarking of participant-level confound regression strategies for the control of motion artifact in studies of functional connectivity. *NeuroImage.* 2017;154:174-187. [doi:10.1016/j.neuroimage.2017.03.020](https://doi.org/10.1016/j.neuroimage.2017.03.020)
- **Behzadi Y, Restom K, Liau J, Liu TT.** A component based noise correction method (CompCor) for BOLD and perfusion based fMRI. *NeuroImage.* 2007;37(1):90-101. [doi:10.1016/j.neuroimage.2007.04.042](https://doi.org/10.1016/j.neuroimage.2007.04.042)

## Where to next

Once you have preprocessed data, you're in the [Data engineering](../data-engineering/index.md) section's world: how do you turn those derivatives into a reliable, observable, well-tested cohort-level pipeline?
