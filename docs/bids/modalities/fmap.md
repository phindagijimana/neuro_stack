# Field maps in BIDS

> Four ways to encode the same B0 inhomogeneity. Pick one; `IntendedFor` (or `B0FieldIdentifier`) connects it to the BOLD / DWI it corrects.

**Primary spec:** [BIDS — Magnetic Resonance Imaging Data → Fieldmap data](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#fieldmap-data).

Course map: folder layout → suffixes → the 4 fieldmap cases → entities → required sidecar fields per case → `IntendedFor` / `B0FieldIdentifier` → conversion → validation → PEPOLAR best practice → pitfalls → tools → references → where to next.

The physics of EPI distortion and the math of `topup` / `eddy` live in [fundamentals/sequences/epi.md](../../fundamentals/sequences/epi.md). The QC consequences of distortion live in [analysis/qc.md](../../analysis/qc.md). This page is about laying out the fieldmap files.

## Folder layout (one-glance)

```text
sub-01/
└── ses-01/
    └── fmap/
        ├── sub-01_ses-01_dir-AP_run-01_epi.nii.gz        # PEPOLAR case
        ├── sub-01_ses-01_dir-AP_run-01_epi.json
        ├── sub-01_ses-01_dir-PA_run-01_epi.nii.gz
        ├── sub-01_ses-01_dir-PA_run-01_epi.json
        ├── sub-01_ses-01_phasediff.nii.gz                # phase-diff case
        ├── sub-01_ses-01_phasediff.json
        └── sub-01_ses-01_magnitude.nii.gz
```

You generally pick **one** fieldmap style per session — the four cases below are alternatives, not all-of-the-above.

## Allowed suffixes

| Suffix | What it is | Used in |
| --- | --- | --- |
| `epi` | A short EPI volume(s) acquired with reversed phase encoding | Case 4 (PEPOLAR / TOPUP) |
| `magnitude` | Magnitude image companion for phase fieldmap | Cases 1, 2, 3 |
| `magnitude1` / `magnitude2` | Per-echo magnitude images | Case 2 (two-phase) |
| `phasediff` | Single phase-difference map (TE2 − TE1) | Case 1 |
| `phase1` / `phase2` | Per-echo phase images | Case 2 |
| `fieldmap` | Pre-computed B0 fieldmap in Hz or rad/s | Case 3 |
| `TB1TFL` `TB1RFM` etc. | Vendor B1+ transmit calibration | qMRI (see [qmri.md](./qmri.md)) |

Suffixes are case-sensitive and exact.

## The four fieldmap cases

The spec calls them *Case 1* through *Case 4*. Pick by what your scanner exports.

### Case 1 — phase-difference map

```text
fmap/sub-01_ses-01_phasediff.nii.gz
fmap/sub-01_ses-01_phasediff.json     # has EchoTime1 + EchoTime2
fmap/sub-01_ses-01_magnitude1.nii.gz
fmap/sub-01_ses-01_magnitude2.nii.gz  # optional
```

Single phase-difference + magnitude(s). Scanner already subtracted the two TEs.

### Case 2 — two separate phase maps

```text
fmap/sub-01_ses-01_phase1.nii.gz
fmap/sub-01_ses-01_phase1.json        # has EchoTime
fmap/sub-01_ses-01_phase2.nii.gz
fmap/sub-01_ses-01_phase2.json        # has EchoTime
fmap/sub-01_ses-01_magnitude1.nii.gz
fmap/sub-01_ses-01_magnitude2.nii.gz
```

Per-echo phase and magnitude pairs. You (or the pipeline) compute the phase difference.

### Case 3 — direct fieldmap in Hz

```text
fmap/sub-01_ses-01_fieldmap.nii.gz
fmap/sub-01_ses-01_fieldmap.json      # has Units: "Hz" and EchoTime
fmap/sub-01_ses-01_magnitude.nii.gz
```

A pre-computed B0 fieldmap. The scanner (Siemens "GRE Field Mapping" with online recon) or a vendor pipeline produced this; you just store it. `Units` MUST be `Hz` (or `rad/s` for some derivative pipelines, but `Hz` is the BIDS default).

### Case 4 — PEPOLAR (TOPUP-style reversed-PE EPI)

```text
fmap/sub-01_ses-01_dir-AP_epi.nii.gz
fmap/sub-01_ses-01_dir-AP_epi.json    # PhaseEncodingDirection: "j-", TotalReadoutTime
fmap/sub-01_ses-01_dir-PA_epi.nii.gz
fmap/sub-01_ses-01_dir-PA_epi.json    # PhaseEncodingDirection: "j",  TotalReadoutTime
```

The modern default for BOLD and DWI distortion correction. Two short EPI acquisitions with opposing phase-encoding directions; [`topup`](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup) ([Andersson 2003](https://doi.org/10.1016/S1053-8119(03)00336-7)) estimates the field from the two. Pair via `dir-` entities and matching `acq-` / `run-`.

## Filename entities — in order

```
sub- ses- acq- ce- rec- dir- run- echo- part- chunk-
```

`dir-` is critical for Case 4 PEPOLAR. `echo-` distinguishes Case 2's two phase echoes (though the spec also accepts `phase1` / `phase2` suffixes). `acq-` lets you carry multiple fieldmap series (e.g. one for func, one for dwi) in the same session.

## Required JSON sidecar fields per case

### Case 1 (`phasediff`)

```json
{
  "EchoTime1": 0.00492,
  "EchoTime2": 0.00738,
  "IntendedFor": [
    "bids::sub-01/ses-01/func/sub-01_ses-01_task-rest_run-01_bold.nii.gz"
  ]
}
```

| Field | Type | Required |
| --- | --- | --- |
| `EchoTime1` | number (s) | yes |
| `EchoTime2` | number (s) | yes |
| `IntendedFor` | array of BIDS URIs | yes (or `B0FieldIdentifier`) |

### Case 2 (`phase1` / `phase2`)

Per-file `EchoTime`. `magnitude1` and `magnitude2` mirror the phase echoes.

```json
{
  "EchoTime": 0.00492,
  "IntendedFor": ["bids::sub-01/ses-01/func/sub-01_ses-01_task-rest_run-01_bold.nii.gz"]
}
```

### Case 3 (`fieldmap`)

```json
{
  "Units": "Hz",
  "EchoTime": 0.00492,
  "IntendedFor": ["bids::sub-01/ses-01/func/sub-01_ses-01_task-rest_run-01_bold.nii.gz"]
}
```

### Case 4 (`epi` PEPOLAR)

```json
{
  "PhaseEncodingDirection": "j-",
  "TotalReadoutTime": 0.0289,
  "IntendedFor": [
    "bids::sub-01/ses-01/func/sub-01_ses-01_task-rest_run-01_bold.nii.gz",
    "bids::sub-01/ses-01/dwi/sub-01_ses-01_dir-AP_dwi.nii.gz"
  ]
}
```

| Field | Type | Required |
| --- | --- | --- |
| `PhaseEncodingDirection` | string | yes |
| `TotalReadoutTime` | number (s) | yes |
| `IntendedFor` | array of BIDS URIs | yes (or `B0FieldIdentifier`) |

The PE direction of the PEPOLAR `epi` must be **opposite** that of the target BOLD/DWI. The two PEPOLAR files themselves must have opposite signs (`j-` and `j`).

## `IntendedFor` vs `B0FieldIdentifier`

Two ways to link a fieldmap to its target:

- **`IntendedFor`** (older, universal) — array of BIDS-URI paths in the fieldmap's JSON. The pre-1.8 form was a session-relative path (`"ses-01/func/sub-01_ses-01_task-rest_bold.nii.gz"`); BIDS 1.8 introduced the `bids::` URI form (`"bids::sub-01/ses-01/func/sub-01_ses-01_task-rest_bold.nii.gz"`) — clearer and dataset-relative.
- **`B0FieldIdentifier`** / **`B0FieldSource`** (BIDS 1.7+) — both the fieldmap and the target carry a matching string identifier. Cleaner for many-to-many cases (one PEPOLAR pair correcting multiple runs).

```json
// fmap sidecar
{ "B0FieldIdentifier": "pepolar_run1" }

// matching bold sidecar
{ "B0FieldSource": "pepolar_run1" }
```

Pick one mechanism per dataset; don't mix. fMRIPrep and QSIPrep support both.

## Conversion recipes

### `dcm2niix`

For PEPOLAR (Case 4):

```bash
dcm2niix -b y -ba y -z y -f "sub-%i_dir-%p_epi" -o fmap/ raw/dicom/se_epi/
```

For Siemens GRE phase-difference (Case 1), `dcm2niix` produces two magnitude files and one phase file; rename the phase to `_phasediff.nii.gz` and set `EchoTime1` + `EchoTime2` in the sidecar (`dcm2niix` already populates these as `EchoTime`).

### HeuDiConv snippet (PEPOLAR + IntendedFor)

```python
def infotodict(seqinfo):
    fmap_ap = create_key("sub-{subject}/[ses-{session}/]fmap/"
                         "sub-{subject}[_ses-{session}]_dir-AP_run-{item:02d}_epi")
    fmap_pa = create_key("sub-{subject}/[ses-{session}/]fmap/"
                         "sub-{subject}[_ses-{session}]_dir-PA_run-{item:02d}_epi")
    info = {fmap_ap: [], fmap_pa: []}
    for s in seqinfo:
        pn = s.protocol_name.lower()
        if "se_epi" in pn or "topup" in pn:
            if "_pa" in pn or "rev" in pn:
                info[fmap_pa].append(s.series_id)
            else:
                info[fmap_ap].append(s.series_id)
    return info
```

### Writing `IntendedFor` programmatically

```python
import json, pathlib
subj = pathlib.Path("bids/sub-01/ses-01")
fmaps = list((subj / "fmap").glob("*_epi.json"))
targets = [
    f"bids::sub-01/ses-01/func/{p.name.replace('.nii.gz','')}"
    for p in (subj / "func").glob("*_bold.nii.gz")
]
for fm in fmaps:
    meta = json.loads(fm.read_text())
    meta["IntendedFor"] = targets
    fm.write_text(json.dumps(meta, indent=2))
```

## Validation checks

- **Every `IntendedFor` target exists.** Validator catches typos and missing-file references (`INTENDED_FOR_MISSING`).
- **PEPOLAR files have opposite signs.** Both `epi` JSONs must have `PhaseEncodingDirection` of opposite sign on the same axis.
- **Case 1 has `EchoTime1` + `EchoTime2`, not `EchoTime`.** Most common conversion bug.
- **Case 3 has `Units`.** Without `Units: "Hz"`, fMRIPrep / QSIPrep cannot interpret the fieldmap.
- **No fieldmap with no `IntendedFor`** *and* no `B0FieldIdentifier`. Validator warns; downstream pipelines silently skip the fieldmap.

## Common pitfalls

- **`IntendedFor` path typos.** Pre-1.8 path is session-relative *to the subject directory* (i.e. starts with `ses-01/func/...`, not `sub-01/ses-01/func/...`). Easiest fix: use `bids::` URI form everywhere.
- **Sign of `PhaseEncodingDirection`.** `j-` vs `j` is the most common axis flip. Cross-check against the scanner protocol.
- **`EffectiveEchoSpacing` vs `TotalReadoutTime` confusion.** Either suffices for distortion math, but they are *not* the same number — TRT = (ETL − 1) × EES / (acceleration_factor). `dcm2niix` populates both correctly for Siemens; verify on first subject of every new protocol.
- **Reusing the same `magnitude.nii.gz` for two runs.** When you collect one phase-diff map and intend it to correct three BOLD runs, the *single* `phasediff` + `magnitude` pair must list all three runs in `IntendedFor`. Don't duplicate the magnitude file.
- **Mixing PEPOLAR `epi` and `phasediff` for the same run.** Pick one. Pipelines have to pick one and will silently prefer one over the other.
- **Wrong `dir-` label.** `dir-AP` is by convention anterior-to-posterior PE; `dir-PA` is PA. The validator does not check that the label matches the actual PE direction — your sidecar's `PhaseEncodingDirection` is the source of truth.
- **Renaming subjects after `IntendedFor` is written.** The path strings don't auto-update. Re-run the linker.

## Disease-specific & special use cases

- **Multi-session longitudinal** — acquire a fieldmap per session. Pipelines that pool sessions still want a per-session SDC. `IntendedFor` is session-scoped.
- **Multi-band BOLD / multi-shell DWI** — one PEPOLAR pair can correct many runs; list them all in `IntendedFor` or use a shared `B0FieldIdentifier`.
- **ASL** — when ASL uses a fieldmap, the same Case 1/3/4 mechanisms apply; list the ASL series in `IntendedFor`. See [perf.md](./perf.md).
- **B1+ transmit calibration (qMRI)** — vendor-specific `TB1TFL` / `TB1RFM` / `RB1COR` files live in `fmap/` per the qMRI BEP. See [qmri.md](./qmri.md).
- **Multi-PE protocols (HCP-Lifespan)** — collect both `dir-AP` and `dir-PA` full BOLD runs and list both reversed-PE `epi` pairs in `IntendedFor`. QSIPrep / fMRIPrep handle this.

## Software & resources

| Tool / resource | Purpose |
| --- | --- |
| [BIDS spec — fmap](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#fieldmap-data) | Authoritative reference |
| [`dcm2niix`](https://github.com/rordenlab/dcm2niix) | Conversion |
| [FSL `topup`](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/topup) | PEPOLAR fieldmap estimation |
| [`fmriprep` / `qsiprep`](https://fmriprep.org/) | Consume fieldmaps automatically |
| [`SDCFlows`](https://www.nipreps.org/sdcflows/) | NiPreps' susceptibility-distortion-correction library, all four cases |
| [`bids-validator`](https://bids-standard.github.io/bids-validator/) | Validate `IntendedFor` paths |
| [OpenNeuro `ds003097`, `ds001734`](https://openneuro.org/) | Reference datasets with PEPOLAR fmaps |

## References & spec links

- BIDS spec — [Fieldmap data](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#fieldmap-data).
- Andersson JLR, Skare S, Ashburner J. How to correct susceptibility distortions in spin-echo echo-planar images: application to diffusion tensor imaging. *NeuroImage.* 2003;20(2):870–888. [doi:10.1016/S1053-8119(03)00336-7](https://doi.org/10.1016/S1053-8119(03)00336-7)
- Jezzard P, Balaban RS. Correction for geometric distortion in echo planar images from B0 field variations. *Magn Reson Med.* 1995;34(1):65–73. [doi:10.1002/mrm.1910340111](https://doi.org/10.1002/mrm.1910340111)
- Esteban O, Markiewicz CJ, Goncalves M, et al. SDCFlows: susceptibility-distortion correction with NiPreps. *Zenodo.* [doi:10.5281/zenodo.10047769](https://doi.org/10.5281/zenodo.10047769)

## Where to next

- Physics: [fundamentals/sequences/epi.md](../../fundamentals/sequences/epi.md), [gre.md](../../fundamentals/sequences/gre.md).
- Analysis / QC: [analysis/qc.md](../../analysis/qc.md), [analysis/functional.md](../../analysis/functional.md), [analysis/diffusion.md](../../analysis/diffusion.md).
- Related modalities: [func.md](./func.md), [dwi.md](./dwi.md), [perf.md](./perf.md).
