# Arterial spin labeling (perfusion) in BIDS

> The only modality where you must ship a TSV that labels every volume. Miss `aslcontext.tsv` and the dataset is unprocessable.

**Primary spec:** [BIDS — Magnetic Resonance Imaging Data → Arterial Spin Labeling perfusion data](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#arterial-spin-labeling-perfusion-data).

Course map: folder layout → suffixes → `aslcontext.tsv` → entities → required + recommended sidecar by labeling type (CASL / PCASL / PASL) → M0 → conversion → validation → pitfalls → multi-PLD / Hadamard → tools → references → where to next.

The physics of ASL (labeling, BSP, kinetic models) lives in [fundamentals/sequences/asl.md](../../fundamentals/sequences/asl.md). The CBF-quantification pipeline lives in [ASLPrep](https://aslprep.readthedocs.io/). This page is about getting the files into BIDS shape that ASLPrep can consume.

## Folder layout (one-glance)

```text
sub-01/
└── ses-01/
    └── perf/
        ├── sub-01_ses-01_asl.nii.gz
        ├── sub-01_ses-01_asl.json
        ├── sub-01_ses-01_aslcontext.tsv
        ├── sub-01_ses-01_m0scan.nii.gz          # if M0Type = "Separate"
        ├── sub-01_ses-01_m0scan.json
        └── sub-01_ses-01_sbref.nii.gz
```

Note the folder is `perf/`, not `asl/`. The suffix `asl` carries the modality identity; the folder name is the BIDS data-type.

## Allowed suffixes

| Suffix | What it is | When to use |
| --- | --- | --- |
| `asl` | The 4D ASL time-series (label / control / m0 interleaved) | Every ASL acquisition |
| `m0scan` | Separately-acquired equilibrium-magnetisation calibration | When `M0Type = "Separate"` |
| `sbref` | Single-band reference | Multi-band ASL protocols |

`aslcontext.tsv` is a *required companion file*, not a suffix.

## `aslcontext.tsv` — required companion

A single-column TSV labelling every volume in the 4D `_asl.nii.gz`:

```text
volume_type
m0scan
control
label
control
label
control
label
...
```

| `volume_type` value | Meaning |
| --- | --- |
| `control` | Blood magnetisation NOT inverted |
| `label` | Blood magnetisation inverted (tagged) |
| `m0scan` | Equilibrium-magnetisation calibration volume embedded in the time-series |
| `deltam` | Perfusion-weighted difference (control − label), already subtracted by scanner |
| `cbf` | Quantitative CBF map (mL / 100 g / min), already computed by scanner — requires `Units` in the sidecar |
| `noRF` | No-RF reference, vendor-specific |
| `n/a` | Unsupported / unknown |

**Row count must equal the 4th dimension of the NIfTI.** Pipelines (ASLPrep) split the volumes by this column.

## Filename entities — in order

```
sub- ses- acq- rec- run- echo- part- chunk- split-
```

Note: ASL does *not* use `task-` or `dir-` in the standard form. Multi-PLD protocols typically encode the PLDs in the `PostLabelingDelay` array, not in filename entities.

| Entity | Used when | Example |
| --- | --- | --- |
| `acq-` | Distinguish labeling schemes (PCASL vs PASL on the same subject) | `acq-pcasl`, `acq-pasl` |
| `rec-` | Different reconstructions | `rec-online` |
| `run-` | Repeats | `run-01` |

## Required JSON sidecar fields

### Common (every ASL acquisition)

| Field | Type | Example | Why |
| --- | --- | --- | --- |
| `MagneticFieldStrength` | number (T) | `3` | T1blood depends on B0; CBF math needs it |
| `MRAcquisitionType` | `"1D"` / `"2D"` / `"3D"` | `"3D"` | 3D-GRASE vs 2D-EPI changes preprocessing |
| `EchoTime` | number (s) | `0.0103` | T2/T2* weighting affects M0 fit |
| `RepetitionTimePreparation` | number or array (s) | `4.0` | The TR of the labeling+readout cycle |
| `FlipAngle` | number (deg) | `90` | Required if `LookLocker` is true |
| `M0Type` | `"Separate"` / `"Included"` / `"Estimate"` / `"Absent"` | `"Separate"` | Tells ASLPrep where M0 comes from |
| `SliceTiming` | array (s) | `[0.0, 0.04, ...]` | Required if `MRAcquisitionType = "2D"` |

### PCASL / CASL — required-if

| Field | When required | Example |
| --- | --- | --- |
| `LabelingDuration` | If `ArterialSpinLabelingType = "PCASL"` or `"CASL"` | `1.8` (s) |

### PASL — required-if

| Field | When required | Example |
| --- | --- | --- |
| `BolusCutOffFlag` | Always for PASL | `true` |
| `BolusCutOffDelayTime` | If `BolusCutOffFlag = true` | `0.8` (s) |
| `BolusCutOffTechnique` | If `BolusCutOffFlag = true` | `"QUIPSSII"` |

### M0 (when `M0Type = "Estimate"`)

| Field | Required |
| --- | --- |
| `M0Estimate` | A single numeric estimate of M0 |

## Recommended fields

| Field | Why |
| --- | --- |
| `ArterialSpinLabelingType` | `"CASL"` / `"PCASL"` / `"PASL"` — strictly recommended but ASLPrep refuses to run without it |
| `PostLabelingDelay` | number or array (s) — single PLD or multi-PLD list |
| `BackgroundSuppression` | boolean |
| `BackgroundSuppressionPulseTime` | array (s) — times of BSP inversion pulses |
| `VascularCrushing` | boolean |
| `LabelingPlane` | string — where the labeling plane sits |
| `LabelingFrequency` | number (MHz) |
| `LabelingMagnitude` | number (mT) |
| `LookLocker` | boolean — Look-Locker readout |
| `TotalAcquiredPairs` | integer — number of label/control pairs |
| `PhaseEncodingDirection` `TotalReadoutTime` | for distortion correction |
| `B0FieldIdentifier` `B0FieldSource` | linking to fieldmaps in `fmap/` |

The [Alsop et al. 2015 ISMRM ASL consensus](https://doi.org/10.1002/mrm.25197) is the source of truth for *which* fields a clinical ASL protocol must report; BIDS-ASL ([Clement et al. 2022](https://doi.org/10.1016/j.neuroimage.2022.119025)) is the BIDS encoding of those fields.

## Conversion recipes

### `dcm2niix`

`dcm2niix` has ASL support since v1.0.20201102; for newer protocols upgrade to ≥ v1.0.20220720. It writes the 4D NIfTI plus a partial sidecar; the ASL-specific fields and the `aslcontext.tsv` typically need a post-processing step.

```bash
dcm2niix -b y -ba y -z y -f "sub-%i_asl" -o perf/ raw/dicom/asl/
```

For Siemens product PCASL: `dcm2niix` populates `ArterialSpinLabelingType`, `LabelingDuration`, `PostLabelingDelay` from the protocol's CSA header. For Philips / GE the coverage varies; verify on your first subject.

### Writing `aslcontext.tsv` from vendor convention

Most vendors interleave `control, label, control, label, ...` with an optional leading `m0scan`. After conversion:

```python
import nibabel as nib, pathlib
nii = pathlib.Path("perf/sub-01_ses-01_asl.nii.gz")
n_vol = nib.load(nii).shape[3]
# Siemens product PCASL: 1 M0, then control/label pairs
rows = ["m0scan"] + ["control" if i % 2 == 0 else "label" for i in range(n_vol - 1)]
ctx = nii.with_name(nii.name.replace("_asl.nii.gz", "_aslcontext.tsv"))
ctx.write_text("volume_type\n" + "\n".join(rows) + "\n")
```

This is vendor-specific. Read the protocol PDF and confirm the interleave on the first subject.

### Minimal `asl.json` (PCASL, separate M0)

```json
{
  "Manufacturer": "Siemens",
  "ManufacturersModelName": "Prisma_fit",
  "MagneticFieldStrength": 3,
  "MRAcquisitionType": "3D",
  "EchoTime": 0.0103,
  "RepetitionTimePreparation": 4.0,
  "FlipAngle": 90,
  "ArterialSpinLabelingType": "PCASL",
  "LabelingDuration": 1.8,
  "PostLabelingDelay": 1.8,
  "BackgroundSuppression": true,
  "BackgroundSuppressionPulseTime": [1.75, 2.71, 3.31],
  "M0Type": "Separate",
  "TotalAcquiredPairs": 30,
  "VascularCrushing": false,
  "AcquisitionVoxelSize": [3.0, 3.0, 3.0]
}
```

### Minimal `m0scan.json`

```json
{
  "MagneticFieldStrength": 3,
  "EchoTime": 0.0103,
  "RepetitionTimePreparation": 10.0,
  "FlipAngle": 90
}
```

## Validation checks

- **Row count in `aslcontext.tsv` matches the 4th dimension of `_asl.nii.gz`.** Bids-validator catches this.
- **`M0Type = "Separate"` ⇒ `_m0scan.nii.gz` exists in `perf/`.**
- **`M0Type = "Included"` ⇒ at least one `m0scan` row in `aslcontext.tsv`.**
- **`M0Type = "Estimate"` ⇒ `M0Estimate` field in the sidecar.**
- **`ArterialSpinLabelingType` matches the labeling-specific required fields.** PCASL ⇒ `LabelingDuration`; PASL ⇒ `BolusCutOffFlag`.
- **Times in seconds.** `PostLabelingDelay`, `LabelingDuration`, `BolusCutOffDelayTime` all in seconds. Vendor PDFs often quote ms.

Run [`bids-validator`](https://bids-standard.github.io/bids-validator/) and then [`aslprep --boilerplate-only`](https://aslprep.readthedocs.io/) — the latter dry-runs the consume-side and fails loudly on missing fields.

## Common pitfalls

- **PLD in ms, not seconds.** Siemens / GE PDFs quote `PLD = 1800 ms`; BIDS wants `1.8`. A 1000× error in CBF.
- **Missing `aslcontext.tsv`.** Dataset will validate as long as everything else is right; ASLPrep refuses to run. Generate it at conversion.
- **Wrong interleave.** Some Philips protocols are `label, control, label, control, ...` not `control, label, ...`. The polarity error inverts the perfusion-weighted image (and the resulting CBF is negative-where-it-should-be-positive). Always inspect the first M0-subtracted image after conversion.
- **`M0Type` lies.** Sidecar says `"Separate"` but no `_m0scan.nii.gz` on disk. ASLPrep errors; fix by either acquiring the M0 or switching `M0Type` to `"Estimate"` + `M0Estimate`.
- **Multi-PLD encoded as separate runs.** Don't — encode PLDs as an *array* in `PostLabelingDelay` and label each volume's PLD in the order it appears in the 4D file.
- **Background-suppression pulses not reported.** Without `BackgroundSuppression: true` and `BackgroundSuppressionPulseTime`, ASLPrep applies the wrong M0 correction.
- **`acq-` label conflated with labeling type.** Use `ArterialSpinLabelingType` for the type; reserve `acq-` for protocol variants (e.g. `acq-3D` vs `acq-2D`).

## Disease-specific & special use cases

- **Multi-PLD (Hadamard-encoded) ASL** — `PostLabelingDelay` is an array, one entry per volume in acquisition order. Use the appropriate Hadamard decoding in ASLPrep.
- **Pediatric ASL** — same layout; higher PLD (≥ 2.0 s) because T1blood is longer. Document age explicitly.
- **Cerebrovascular reactivity (CO₂ challenge ASL)** — encode the CO₂ challenge as separate runs with `acq-baseline` and `acq-hypercap`; pair with `events.tsv` describing the gas-mixture timing.
- **Tumour perfusion (clinical)** — `acq-tumour_ce-gad_asl` for post-Gd ASL (rare; not all centres do this).
- **Dementia cohorts** — protocols typically pair `acq-3D_PCASL` with structural T1w; CBF is computed downstream. See [clinical/alzheimers-and-dementia.md](../../clinical/alzheimers-and-dementia.md).
- **Stroke / vasospasm** — bilateral PLD comparison or multi-PLD; ASL transit-time becomes the marker rather than CBF alone.

## Software & resources

| Tool / resource | Purpose |
| --- | --- |
| [BIDS spec — perf](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#arterial-spin-labeling-perfusion-data) | Authoritative reference |
| [ASLPrep](https://aslprep.readthedocs.io/) | The canonical BIDS-app for ASL preprocessing + CBF quantification |
| [BASIL / FSL](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/BASIL) | Bayesian ASL fitting (kinetic model) |
| [`dcm2niix`](https://github.com/rordenlab/dcm2niix) | ASL-aware DICOM conversion |
| [`bids-validator`](https://bids-standard.github.io/bids-validator/) | Validate |
| [Alsop 2015 ISMRM consensus paper](https://doi.org/10.1002/mrm.25197) | Required-reporting fields for clinical ASL |
| [OpenNeuro `ds002785`, `ds003610`](https://openneuro.org/) | Reference ASL datasets |

## References & spec links

- BIDS spec — [Arterial Spin Labeling perfusion data](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#arterial-spin-labeling-perfusion-data).
- Alsop DC, Detre JA, Golay X, et al. Recommended implementation of arterial spin-labeled perfusion MRI for clinical applications: a consensus of the ISMRM perfusion study group and the European consortium for ASL in dementia. *Magn Reson Med.* 2015;73(1):102–116. [doi:10.1002/mrm.25197](https://doi.org/10.1002/mrm.25197)
- Clement P, Castellaro M, Okell TW, et al. ASL-BIDS, the brain imaging data structure extension for arterial spin labeling. *Sci Data.* 2022;9:543. [doi:10.1038/s41597-022-01615-9](https://doi.org/10.1038/s41597-022-01615-9)
- Adebimpe A, Bertolero M, Mehta K, et al. ASLPrep: a generalizable platform for processing of arterial spin labeled MRI. *Nat Methods.* 2022;19:683–686. [doi:10.1038/s41592-022-01458-7](https://doi.org/10.1038/s41592-022-01458-7)

## Where to next

- Physics: [fundamentals/sequences/asl.md](../../fundamentals/sequences/asl.md).
- Related modalities: [fmap.md](./fmap.md) for SDC, [func.md](./func.md) for BOLD-perfusion combined acquisitions.
- Pipelines: [analysis/qc.md](../../analysis/qc.md) for ASL-specific QC checks.
