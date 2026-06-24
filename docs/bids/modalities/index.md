# Per-modality BIDS conversion guides

> One page per BIDS data type — the field-by-field, suffix-by-suffix, sidecar-by-sidecar recipe you need to actually get your data into valid BIDS for *this* modality.

Each of the sixteen pages below covers a single BIDS data type. The structure is identical across pages so you can read them as reference manuals: folder layout → allowed suffixes → entity ordering → required JSON sidecar fields → recommended fields → conversion recipes (DICOM / vendor-native → BIDS) → validation checks → common pitfalls → disease-specific use cases → software → references.

Every required-field list and entity-ordering rule is taken from the [canonical BIDS specification](https://bids-specification.readthedocs.io/en/latest/) (verified against the live spec). When the spec moves, these pages get re-verified against it — but the spec is always authoritative.

For the *operational* picture (DICOM walk, HeuDiConv heuristics, validator workflows, derivatives layout, pitfalls), the parent [BIDS toolkit](../index.md) pages remain the entry points; this subsection is the per-modality drill-down.

## MR family

<div class="grid cards" markdown>

-   :material-head: **[anat — Anatomical MRI](anat.md)** — T1w / T2w / FLAIR / PDw / qMRI source acquisitions (MP2RAGE, MTS, MPM).

-   :material-pulse: **[func — Functional MRI (BOLD)](func.md)** — task and resting-state BOLD; multi-echo; events.tsv; the `TaskName` rule.

-   :material-rotate-3d-variant: **[dwi — Diffusion MRI](dwi.md)** — DWI with mandatory `.bvec` / `.bval`; multi-shell HARDI / HCP-grade protocols.

-   :material-magnet: **[fmap — Field maps](fmap.md)** — phasediff, two-phase, direct Hz map, and PEPOLAR pairs; `IntendedFor` linkage.

-   :material-water: **[perf — Arterial spin labeling](perf.md)** — ASL with the mandatory `aslcontext.tsv`; PASL / CASL / pCASL specifics.

-   :material-chart-bell-curve: **[mrs — MR Spectroscopy](mrs.md)** — NIfTI-MRS format; single-voxel and MRSI; spec2nii for vendor conversion.

-   :material-blur-radial: **[swi — Susceptibility-weighted](swi.md)** — combined SWI plus the multi-echo GRE source needed for QSM.

-   :material-counter: **[qmri — Quantitative MRI](qmri.md)** — qMRI file collections (MP2RAGE, VFA, MPM, MTS, MESE, MEGRE, IRT1) and derived parametric maps.

</div>

## Non-MR family

<div class="grid cards" markdown>

-   :material-atom: **[pet — Positron Emission Tomography](pet.md)** — tracer + radioactivity + time fields; reconstruction metadata; blood-sampling TSVs.

-   :material-wave: **[eeg — Electroencephalography](eeg.md)** — BrainVision / EDF / EEGLAB / BDF formats; electrodes + coordsystem + channels TSVs.

-   :material-brain: **[ieeg — Intracranial EEG](ieeg.md)** — ECoG + sEEG + DBS; ACPC vs MNI coordinate frames; bipolar vs monopolar reference.

-   :material-radar: **[meg — Magnetoencephalography](meg.md)** — five vendor formats (FIF / CTF / 4D / KIT / ITAB); dewar-vs-head coordsystem.

-   :material-led-on: **[nirs — Near-infrared spectroscopy](nirs.md)** — SNIRF-only; optodes + coordsystem; vendor-to-SNIRF conversion.

-   :material-walk: **[motion — Motion / IMU / eye-tracking](motion.md)** — multiple tracking systems (IMU, optic, eyetracker); the `tracksys-` entity.

-   :material-microscope: **[micr — Microscopy](micr.md)** — 19 suffixes (TEM / SEM / CONF / BF / FLUO / SPIM); OME-TIFF and OME-ZARR; samples + stains TSVs.

-   :material-database: **[beh + physio + stim — Behaviour and accessory recordings](beh-physio.md)** — pure-behaviour datasets, physiological signals paired with imaging (RETROICOR, cardiac), and stimulus presentation logs.

</div>

## How to use this section

1. **Look up your modality** in the grid above.
2. **Confirm the folder name + suffix** for your data.
3. **Check the required JSON sidecar fields** — these are non-negotiable for the validator to pass.
4. **Follow the conversion recipe** (DICOM-based or vendor-native) to produce the right structure.
5. **Run the validator** ([BIDS Validator](https://bids-standard.github.io/bids-validator/)) and fix any errors before any pipeline runs.
6. **Cross-link** to the [fundamentals](../../fundamentals/sequences/index.md) page for physics and the [analysis](../../analysis/index.md) page for what to do with the data.

## Canonical references

- [BIDS Specification (latest)](https://bids-specification.readthedocs.io/en/latest/) — the authoritative source.
- [BIDS GitHub repository](https://github.com/bids-standard/bids-specification) — spec source + PR history.
- [BIDS examples](https://github.com/bids-standard/bids-examples) — minimal valid datasets for every modality.
- [BIDS Starter Kit](https://github.com/bids-standard/bids-starter-kit) — templates, walkthroughs, and modality cheatsheets.
- [BIDS extensions (BEPs)](https://bids.neuroimaging.io/extensions) — proposals being worked on or recently merged.
- [Pernet et al., 2019 — BIDS-EEG](https://doi.org/10.1038/s41597-019-0104-8), [Holdgraf et al., 2019 — BIDS-iEEG](https://doi.org/10.1038/s41597-019-0105-7), [Niso et al., 2018 — BIDS-MEG](https://doi.org/10.1038/sdata.2018.110), [Norgaard et al., 2022 — PET2BIDS](https://doi.org/10.1038/s41597-022-01164-1), [Clarke et al., 2022 — NIfTI-MRS](https://doi.org/10.1002/mrm.29418), [Luke et al., 2023 — BIDS-NIRS](https://doi.org/10.1038/s41597-023-02437-z), [Welzel et al., 2023 — BIDS-Motion](https://doi.org/10.1038/s41597-023-02022-4), [Bourget et al., 2022 — BIDS-Microscopy](https://doi.org/10.1038/s41597-022-01554-5), [Karakuzu et al., 2022 — qMRI-BIDS](https://doi.org/10.1038/s41597-022-01571-4), [Clement et al., 2022 — ASL-BIDS](https://doi.org/10.1016/j.neuroimage.2022.119025).

## Where to next

- [Validating a dataset](../validation.md) — once your conversion is done.
- [DICOM to BIDS](../dicom-to-bids.md) — the HeuDiConv / BIDScoin tool chain.
- [Derivatives layout](../derivatives.md) — when you're emitting your own outputs.
- [PyBIDS](../pybids.md) — programmatic access to whatever you converted.
- [Common pitfalls](../pitfalls.md) — the bugs that bite every modality.
