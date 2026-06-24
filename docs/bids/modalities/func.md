# Functional MRI (BOLD) in BIDS

> Task or rest, single- or multi-echo, single- or multi-band — the spec is the same. The bug surface is in the sidecar.

**Primary spec:** [BIDS — Magnetic Resonance Imaging Data → Task (including resting state) imaging data](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#task-including-resting-state-imaging-data).

Course map: folder layout → suffixes → entities → required + recommended sidecar → `events.tsv` → conversion → validation → multi-echo / multi-band → pitfalls → special use cases → tools → references → where to next.

Physics for BOLD / EPI lives in [fundamentals/sequences/epi.md](../../fundamentals/sequences/epi.md). Analysis pipelines for task / resting state live in [analysis/functional.md](../../analysis/functional.md) and [analysis/resting-state.md](../../analysis/resting-state.md).

## Folder layout (one-glance)

```text
sub-01/
└── ses-01/
    └── func/
        ├── sub-01_ses-01_task-rest_run-01_bold.nii.gz
        ├── sub-01_ses-01_task-rest_run-01_bold.json
        ├── sub-01_ses-01_task-rest_run-01_sbref.nii.gz
        ├── sub-01_ses-01_task-rest_run-01_sbref.json
        ├── sub-01_ses-01_task-nback_run-01_bold.nii.gz
        ├── sub-01_ses-01_task-nback_run-01_bold.json
        ├── sub-01_ses-01_task-nback_run-01_events.tsv
        ├── sub-01_ses-01_task-mb_echo-1_part-mag_bold.nii.gz
        ├── sub-01_ses-01_task-mb_echo-2_part-mag_bold.nii.gz
        └── sub-01_ses-01_task-mb_echo-3_part-mag_bold.nii.gz
```

The `task-<label>` entity is **required** on every BOLD file. Resting state is `task-rest` by convention.

## Allowed suffixes

| Suffix | What it is | When to use |
| --- | --- | --- |
| `bold` | The BOLD time-series itself | Every functional run |
| `sbref` | Single-band reference image | Multi-band protocols — one volume, no MB acceleration, used as a registration target |
| `cbv` | Cerebral blood volume time-series | VASO / iron-oxide CBV studies |
| `phase` | Phase channel of the BOLD acquisition (deprecated) | Replaced by `part-phase` entity in newer BIDS versions — use that |
| `events` | The stimulus / response timing file | Pair with each task run; required for task runs |

`bold` and `cbv` are 4D NIfTIs. `sbref` is 3D. `events` is a TSV — not an image.

## Filename entities — in order

```
sub- ses- task- acq- ce- rec- dir- run- echo- part- chunk- split-
```

| Entity | Used when | Example |
| --- | --- | --- |
| `task-` | **Always** — names the task (`rest`, `nback`, `flanker`, `movie`) | `task-rest`, `task-faceloc` |
| `acq-` | Different EPI protocol for the same task | `acq-mb6`, `acq-singleband` |
| `ce-` | Contrast agent (rare for BOLD; common for CBV) | `ce-mion` for iron-oxide CBV |
| `rec-` | Different reconstruction (online vs offline) | `rec-online` |
| `dir-` | Phase-encoding direction label | `dir-AP`, `dir-PA` |
| `run-` | Repeats of the same task | `run-01`, `run-02` |
| `echo-` | Multi-echo runs | `echo-1`, `echo-2`, `echo-3` |
| `part-` | Magnitude / phase of complex data | `part-mag`, `part-phase` |
| `chunk-` | Long runs split for file-size reasons | `chunk-01`, `chunk-02` |
| `split-` | Multi-part recordings exceeding 2 GB | Heavy long-duration scans only |

`task-rest` is convention but the validator does not enforce it — `task-restingstate` will validate too. Pick one for the study.

## Required JSON sidecar fields

| Field | Type | Example | Why it matters |
| --- | --- | --- | --- |
| `TaskName` | string | `"n-back"` | **MUST match the `task-` entity in the filename** (case-insensitive, hyphens / underscores normalised) — fMRIPrep checks this and fails loudly otherwise |
| `RepetitionTime` | number (s) | `0.8` | Slice timing, GLM design, motion regression — all assume this is correct and in *seconds*, not ms |
| `EchoTime` | number or array (s) | `0.032` or `[0.014, 0.032, 0.050]` | Required for multi-echo |

Required *if* fieldmap-based distortion correction is intended:

| Field | Type | Example | Why |
| --- | --- | --- | --- |
| `PhaseEncodingDirection` | string | `"j-"` | `topup` / SDC need to know which way the EPI distorts |
| `TotalReadoutTime` | number (s) | `0.0289` | `topup` math depends on this |
| `EffectiveEchoSpacing` | number (s) | `0.000295` | Alternative parameterisation; SDC tools want one of the two |

## Recommended fields

| Field | Why |
| --- | --- |
| `SliceTiming` | Array of N-slice acquisition times in seconds. Required for slice-timing correction. **In seconds, not fraction of TR.** |
| `FlipAngle` | Ernst-angle diagnostics |
| `MultibandAccelerationFactor` | The MB factor; downstream tools branch on it |
| `ParallelReductionFactorInPlane` | GRAPPA / SENSE factor |
| `B0FieldIdentifier` / `B0FieldSource` | New (BIDS 1.7+) way to link fieldmaps without `IntendedFor` — see [fmap.md](./fmap.md) |
| `InstitutionName` `Manufacturer` `MagneticFieldStrength` `ReceiveCoilName` | Multi-site harmonisation |
| `DelayTime` | TR padding between volumes (sparse-sampling fMRI) |
| `AcquisitionDuration` | Total scan duration |

## events.tsv — required for task fMRI

Every `task-*_bold.nii.gz` that is not pure resting state should have a sibling `task-*_events.tsv`. Columns:

| Column | Type | Required | Notes |
| --- | --- | --- | --- |
| `onset` | number (s) | yes | Seconds from the **start of the run** (i.e. first volume, not first trigger). |
| `duration` | number (s) | yes | Seconds; `0` for instantaneous events. |
| `trial_type` | string | recommended | Condition label for GLM design (`face`, `house`, `target`). |
| `response_time` | number (s) | optional | Subject's RT, seconds from onset. |
| `stim_file` | string | optional | Path under `stimuli/` for the actual stimulus file. |
| `HED` | string | optional | [Hierarchical Event Descriptor](https://www.hed-resources.org/) tags. |

Minimal `events.tsv`:

```text
onset	duration	trial_type	response_time
0.0	2.0	face	0.742
4.0	2.0	house	0.689
8.0	2.0	face	0.811
```

## Conversion recipes

### `dcm2niix`

`dcm2niix` writes the 4D NIfTI + sidecar; populates `RepetitionTime`, `EchoTime`, `PhaseEncodingDirection`, `MultibandAccelerationFactor`. It does **not** know the `TaskName` — your heuristic must add it.

### HeuDiConv heuristic snippet

```python
def infotodict(seqinfo):
    rest = create_key("sub-{subject}/[ses-{session}/]func/"
                      "sub-{subject}[_ses-{session}]_task-rest_run-{item:02d}_bold")
    nback = create_key("sub-{subject}/[ses-{session}/]func/"
                       "sub-{subject}[_ses-{session}]_task-nback_run-{item:02d}_bold")
    sbref_rest = create_key("sub-{subject}/[ses-{session}/]func/"
                            "sub-{subject}[_ses-{session}]_task-rest_run-{item:02d}_sbref")
    info = {rest: [], nback: [], sbref_rest: []}
    for s in seqinfo:
        pn = s.protocol_name.lower()
        if "rest" in pn and "sbref" in pn:
            info[sbref_rest].append(s.series_id)
        elif "rest" in pn and s.dim4 > 50:
            info[rest].append(s.series_id)
        elif "nback" in pn and s.dim4 > 50:
            info[nback].append(s.series_id)
    return info
```

### Inject `TaskName` after conversion

`dcm2niix` does not set `TaskName`. Patch every sidecar:

```python
import json, pathlib
for p in pathlib.Path("bids").rglob("*_task-*_bold.json"):
    task = p.name.split("task-")[1].split("_")[0]
    meta = json.loads(p.read_text())
    meta["TaskName"] = task
    p.write_text(json.dumps(meta, indent=2))
```

### Minimal `bold.json`

```json
{
  "TaskName": "n-back",
  "RepetitionTime": 0.8,
  "EchoTime": 0.032,
  "FlipAngle": 52,
  "PhaseEncodingDirection": "j-",
  "TotalReadoutTime": 0.0289,
  "EffectiveEchoSpacing": 0.000295,
  "SliceTiming": [0.0, 0.4, 0.0727, 0.4727, 0.1455, 0.5455],
  "MultibandAccelerationFactor": 6,
  "ParallelReductionFactorInPlane": 1,
  "MagneticFieldStrength": 3,
  "Manufacturer": "Siemens",
  "InstitutionName": "URMC"
}
```

## Validation checks

- **`TaskName` matches `task-` entity.** Most common BIDS bug in func. `task-nback` + `"TaskName": "n-back"` is fine (BIDS strips hyphens), but `task-nback` + `"TaskName": "working_memory"` is not.
- **`RepetitionTime` in seconds.** A TR of `800` will validate but every analysis is silently wrong. The validator does not check unit *magnitude*; you must.
- **`SliceTiming` in seconds.** Each entry must be `0 ≤ t < TR`. fMRIPrep refuses to run otherwise.
- **`PhaseEncodingDirection` sign.** `j-` vs `j` flips the direction of the distortion correction. Confirm against the scanner protocol once per protocol family.
- **Multi-echo files paired.** All `echo-N` files for one run must share `task-`, `run-`, and (if used) `part-` entities.
- **`sbref` 3D, `bold` 4D.** Confused single-band reference and the first BOLD volume — common heuristic bug.

Run [`bids-validator`](https://bids-standard.github.io/bids-validator/) — see [validation.md](../validation.md). It catches the structural class of these.

## Common pitfalls

- **TR in milliseconds.** `2000` instead of `2.0`. The validator does not enforce magnitude; downstream HRF convolution silently misaligns by 1000×.
- **Onsets relative to trigger, not first volume.** Many stimulus presentation tools (PsychoPy, E-Prime) log absolute times. Subtract `t_first_volume` before writing the TSV.
- **Resting state with a `task-rest_events.tsv`.** Don't write an empty events file for rest. Either omit it or include only a single 0-duration `rest` row.
- **Missing `sbref` after MB acquisition.** fMRIPrep uses `sbref` as the BOLD reference when present, and it is *much* better than averaging the first N volumes. If your scanner produces it, keep it.
- **Two BOLD runs without `run-` entity.** Will overwrite each other in `dcm2niix` output; the validator catches it as `DUPLICATE_SCAN`.
- **Wrong `PhaseEncodingDirection` after a protocol edit.** When the tech rotates the slab or flips PE, the sidecar lags. Re-derive from DICOM on every conversion; don't copy from a template.
- **Slice timing as fraction-of-TR.** Some old protocols stored `[0, 0.5, ...]` as fractions. BIDS requires absolute seconds.

## Disease-specific & special use cases

- **Multi-echo BOLD (ME-fMRI)** — three or more echoes per TR. Use `echo-1` / `echo-2` / `echo-3` and a single `EchoTime` per file. Pipelines: [`tedana`](https://tedana.readthedocs.io/) for ME-ICA, or [`fMRIPrep`](https://fmriprep.org/) with `--me-output-echos`. See [fundamentals/sequences/epi.md](../../fundamentals/sequences/epi.md).
- **Complex-valued BOLD (SWI-style, phase-regression denoising)** — pair `part-mag` and `part-phase` files for the same `echo-`. The validator requires both to be present.
- **Naturalistic / movie watching** — `task-movie` with the stimulus file under `stimuli/` and a row per scene change in `events.tsv`. [The Cam-CAN movie protocol](https://camcan-archive.mrc-cbu.cam.ac.uk/dataaccess/) is a reference layout.
- **Real-time fMRI (rt-fMRI)** — `task-rt` plus a separate `task-rt_events.tsv` with the per-volume neurofeedback signal. Some studies use a `desc-rt` derivative for the feedback time-series.
- **Pediatric / sleep fMRI** — `task-rest_acq-sleep` is one convention. Document in the study README.
- **Task-rest hybrids** — when subjects do a resting block then a task block in one acquisition, *split* into two runs at conversion if possible; if not, store as one BOLD and document the design in the events file.
- **CBV studies (VASO, MION-CBV)** — use `cbv` suffix instead of `bold`. Animal MION studies often combine `ce-mion_cbv` with task entities.

## Software & resources

| Tool / resource | Purpose |
| --- | --- |
| [BIDS spec — func](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#task-including-resting-state-imaging-data) | Authoritative reference |
| [`dcm2niix`](https://github.com/rordenlab/dcm2niix) | DICOM → NIfTI |
| [HeuDiConv](https://heudiconv.readthedocs.io/) | Heuristic-driven BIDS routing |
| [`bids-validator`](https://bids-standard.github.io/bids-validator/) | Validate the result |
| [fMRIPrep](https://fmriprep.org/) | The canonical BOLD preprocessing BIDS-app |
| [tedana](https://tedana.readthedocs.io/) | Multi-echo ICA |
| [HED](https://www.hed-resources.org/) | Hierarchical event description |
| [OpenNeuro `ds002785`, `ds000114`, `ds001734`](https://openneuro.org/) | Reference BOLD datasets — task + rest |

## References & spec links

- BIDS spec — [Task (including resting state) imaging data](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#task-including-resting-state-imaging-data).
- Esteban O, Markiewicz CJ, Blair RW, et al. fMRIPrep: a robust preprocessing pipeline for functional MRI. *Nat Methods.* 2019;16:111–116. [doi:10.1038/s41592-018-0235-4](https://doi.org/10.1038/s41592-018-0235-4)
- Kundu P, Voon V, Balchandani P, Lombardo MV, Poser BA, Bandettini PA. Multi-echo fMRI: A review. *NeuroImage.* 2017;154:59–80. [doi:10.1016/j.neuroimage.2017.03.033](https://doi.org/10.1016/j.neuroimage.2017.03.033)
- Setsompop K, Gagoski BA, Polimeni JR, Witzel T, Wedeen VJ, Wald LL. Blipped-controlled aliasing in parallel imaging for simultaneous multislice EPI with reduced g-factor penalty. *Magn Reson Med.* 2012;67(5):1210–1224. [doi:10.1002/mrm.23097](https://doi.org/10.1002/mrm.23097)

## Where to next

- Physics: [fundamentals/sequences/epi.md](../../fundamentals/sequences/epi.md).
- Analysis: [analysis/functional.md](../../analysis/functional.md), [analysis/resting-state.md](../../analysis/resting-state.md), [analysis/design.md](../../analysis/design.md).
- Related modalities: [fmap.md](./fmap.md) (distortion correction), [dwi.md](./dwi.md) (EPI cousin).
