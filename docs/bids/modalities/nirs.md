# NIRS / fNIRS in BIDS

> Near-infrared light in, near-infrared light out, optical-density change as the signal, hemoglobin concentration as the inference. BIDS for NIRS is short: one SNIRF file, one optodes table, one coordinate system — done.

Course map: spec link → folder layout → suffixes → entities → required JSON → recommended JSON → companion files → conversion recipes → validation → pitfalls → disease use → tools → refs → next.

**Primary spec.** [BIDS — Near-Infrared Spectroscopy](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/near-infrared-spectroscopy.html) (BEP030, merged 2024). Source paper: [Luke 2023, *Sci Data* 10:580](https://doi.org/10.1038/s41597-023-02437-z).

## Folder layout — one-glance

```text
ds-nirs/
├── dataset_description.json
├── participants.tsv
└── sub-01/
    └── ses-01/
        ├── anat/
        │   └── sub-01_ses-01_T1w.nii.gz                 # for light-transport model
        └── nirs/
            ├── sub-01_ses-01_task-tapping_nirs.snirf
            ├── sub-01_ses-01_task-tapping_nirs.json
            ├── sub-01_ses-01_task-tapping_channels.tsv
            ├── sub-01_ses-01_task-tapping_events.tsv
            ├── sub-01_ses-01_optodes.tsv
            ├── sub-01_ses-01_coordsystem.json
            └── sub-01_ses-01_acq-NAS_photo.jpg
```

T1w is optional in principle — many NIRS-only studies skip it — but mandatory if you intend to do anatomically informed source modelling or atlas-based parcellation.

## Allowed suffixes

| Suffix | Role |
|---|---|
| `nirs` | raw recording (SNIRF only) |
| `events` | trial markers |
| `channels` | source-detector pair metadata |
| `optodes` | physical source / detector positions |
| `coordsystem` | coordinate frame of optodes + landmarks |
| `photo` | cap-placement / landmark photos |

## Allowed raw file format

| Format | Extension | Note |
|---|---|---|
| **Shared Near-Infrared Spectroscopy Format** | `.snirf` | **The only allowed format.** One run per SNIRF file. |

SNIRF is HDF5 under the hood, vendor-neutral, supported by NIRx, Artinis, Hitachi, Shimadzu via their exporters. Vendor proprietary (NIRx `.nirs`, Artinis `.oxy3`, Hitachi `.csv`) must be converted to SNIRF before BIDS-ification.

## Filename entities — in order

```
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_<suffix>.<ext>
```

## Required JSON sidecar fields

| Field | Type | Example |
|---|---|---|
| `TaskName` | string | `"tapping"` |
| `SamplingFrequency` | number (Hz) or `"n/a"` | `5.1` |
| `NIRSChannelCount` | integer | `40` |
| `NIRSSourceOptodeCount` | integer | `8` |
| `NIRSDetectorOptodeCount` | integer | `8` |
| `ACCELChannelCount` | integer | required only if ACCEL channels are present |
| `GYROChannelCount` | integer | required only if GYRO channels are present |
| `MAGNChannelCount` | integer | required only if MAGN channels are present |

### Minimal sidecar — copy-paste

```json
{
  "TaskName": "tapping",
  "SamplingFrequency": 5.1,
  "NIRSChannelCount": 40,
  "NIRSSourceOptodeCount": 8,
  "NIRSDetectorOptodeCount": 8,
  "RecordingDuration": 360.0,
  "Manufacturer": "NIRx",
  "ManufacturersModelName": "NIRSport2",
  "CapManufacturer": "EasyCap",
  "CapManufacturersModelName": "EasyCap M1-NIRS-64",
  "HardwareFilters": {"AntiAliasing": {"Order": 4, "Frequency": 5.0}},
  "ShortChannelCount": 8,
  "SubjectArtefactDescription": "Subject moved at ~120s; epoch flagged.",
  "SoftwareVersions": "Aurora 2024.1.0"
}
```

## Recommended JSON fields

| Field | Why it matters |
|---|---|
| `RecordingDuration` | seconds |
| `Manufacturer` / `ManufacturersModelName` | hardware provenance |
| `CapManufacturer` / `CapManufacturersModelName` | optode-holder provenance |
| `HardwareFilters` / `SoftwareFilters` | filter chain |
| `ShortChannelCount` | short-separation channels for systemic-signal regression — best-practice NIRS |
| `SubjectArtefactDescription` | free-text |
| `SoftwareVersions`, `DeviceSerialNumber` | full provenance |

## Companion files

### `_channels.tsv` — required columns

`name`, `type`, `source`, `detector`, `wavelength_nominal`, `units`.

Allowed `type` values: `NIRSCWAMPLITUDE` (continuous-wave raw amplitude), `NIRSCWFLUORESCENCEAMPLITUDE`, `NIRSCWOPTICALDENSITY` (after Modified Beer-Lambert step 1), `NIRSCWHBO` (oxy-Hb after step 2), `NIRSCWHBR` (deoxy-Hb), `NIRSCWMUA`, `ACCEL`, `GYRO`, `MAGN`, `MISC`.

```tsv
name	type	source	detector	wavelength_nominal	units
S1_D1 760	NIRSCWAMPLITUDE	S1	D1	760	V
S1_D1 850	NIRSCWAMPLITUDE	S1	D1	850	V
S1_D2 760	NIRSCWAMPLITUDE	S1	D2	760	V
S1_D2 850	NIRSCWAMPLITUDE	S1	D2	850	V
```

Recommended: `sampling_frequency`, `component` (for `ACCEL`/`GYRO`/`MAGN`: `x` / `y` / `z`), `wavelength_actual`, `low_cutoff`, `high_cutoff`, `description`, `short_channel` (boolean), `status`, `status_description`.

### `_optodes.tsv` — required columns

`name`, `type` (`source` / `detector`), `x`, `y`, `z` (numbers or `"n/a"`).

```tsv
name	type	x	y	z
S1	source	-42.1	36.5	74.2
S2	source	-32.4	48.1	78.0
D1	detector	-37.2	42.3	81.5
D2	detector	-29.0	38.2	84.0
```

Recommended: `template_x`, `template_y`, `template_z` (required if measured coordinates unavailable — fallback to standard cap template), `description`, `detector_type`, `source_type`.

### `_coordsystem.json` — required when `_optodes.tsv` exists

```json
{
  "NIRSCoordinateSystem": "Other",
  "NIRSCoordinateUnits": "mm",
  "NIRSCoordinateProcessingDescription": "Photogrammetry capture; co-registered to subject T1w via NAS/LPA/RPA fiducials.",
  "AnatomicalLandmarkCoordinates": {
    "NAS": [0.0, 88.5, -15.0],
    "LPA": [-77.0, 0.0, -25.0],
    "RPA": [ 77.0, 0.0, -25.0],
    "Iz":  [0.0, -90.0, -40.0]
  },
  "AnatomicalLandmarkCoordinateSystem": "Other",
  "AnatomicalLandmarkCoordinateUnits": "mm",
  "FiducialsDescription": "Anatomical landmarks digitised with Polhemus Patriot at start of session."
}
```

If no anatomical T1w exists, set `NIRSCoordinateSystem: "Other"` with `template_*` columns in `optodes.tsv` (10-10 standard positions are the usual fallback).

### `_events.tsv`

Standard BIDS columns; trial-locked stimulus paradigm onsets in seconds from recording start.

## Conversion recipes

The canonical Python path is [`mne-nirs`](https://mne.tools/mne-nirs/) + [`mne-bids`](https://mne.tools/mne-bids/).

```python
import mne
from mne_nirs.io.snirf import write_raw_snirf
from mne_bids import BIDSPath, write_raw_bids

# 1. Read vendor format (NIRx example)
raw = mne.io.read_raw_nirx("raw/sub-01/2026-06-23_001/", preload=False)
raw.annotations.set_durations(5.0)

# 2. Convert to SNIRF if needed
write_raw_snirf(raw, "raw/sub-01_tapping.snirf")
raw = mne.io.read_raw_snirf("raw/sub-01_tapping.snirf", preload=False)

# 3. BIDS-ify
bids_path = BIDSPath(subject="01", session="01", task="tapping",
                     root="bids", datatype="nirs")
write_raw_bids(raw, bids_path, overwrite=True, allow_preload=False)
```

For Artinis (`.oxy3`) data: open in Oxysoft, export to SNIRF, then run the same `read_raw_snirf` + `write_raw_bids` pipeline.

Cross-link: [bids/dicom-to-bids.md](../dicom-to-bids.md) for the broader converter pattern.

## Validation

`bids-validator` ≥ 1.10 covers NIRS. Beyond schema:

- Every `(source, detector, wavelength)` row in `_channels.tsv` should have matching `source` and `detector` entries in `_optodes.tsv`.
- `NIRSChannelCount` must equal the SNIRF channel count.
- `NIRSSourceOptodeCount + NIRSDetectorOptodeCount` must equal `len(optodes.tsv)`.
- If `_optodes.tsv` has all-`n/a` xyz, `template_*` columns must be populated.

## Common pitfalls

1. **Vendor format committed instead of SNIRF.** `.nirs`, `.oxy3`, `.csv`, `.wl1` files are *not* valid BIDS-NIRS — only `.snirf`. Convert with vendor software first.
2. **Wavelength stored as a string.** `wavelength_nominal` is numeric (nm). `"760nm"` breaks the validator.
3. **Short-separation channels unflagged.** Short channels (~8 mm source-detector) record systemic blood-flow / scalp signal, used for regression. Mark them with `short_channel: true` in `channels.tsv`; otherwise downstream pipelines treat them as cortical.
4. **Optode coordinates on the template cap, not the subject.** Most cap manufacturers sell template positions. They're a *fallback* — use them in `template_x/y/z`. Real per-subject positions belong in `x/y/z` and require digitisation (Polhemus, photogrammetry).
5. **Age / skull-thickness ignored.** Light penetrates ~1.5 cm in adults but only ~0.5 cm in neonates, with completely different scalp/skull/CSF proportions. The fluence model is age-specific — document subject age and use age-appropriate Monte Carlo (e.g. [mcxyz / NIRFAST / MCX](https://mcx.space/)) for source localisation.
6. **CW vs FD vs TD recording mixed in one dataset.** Continuous-wave, frequency-domain, and time-domain NIRS produce different channel types (`NIRSCWAMPLITUDE` vs frequency / phase outputs). The current BIDS-NIRS spec covers CW well; FD/TD are accommodated via `Other` channel types — document explicitly.
7. **Coordinate system unspecified.** Without `NIRSCoordinateSystem` + `NIRSCoordinateUnits`, MNE-NIRS and Homer3 silently assume the wrong units (m vs mm) — channel positions land 1000× off.

## Disease-specific use cases

- **Neonatal hemodynamics.** Bedside fNIRS for hypoxic-ischaemic encephalopathy monitoring; tiny optode separations (~1 cm), short channels for skin regression. See [clinical/stroke-and-tbi.md](../../clinical/stroke-and-tbi.md).
- **Stroke recovery / motor rehabilitation.** Sensorimotor cortex HbO during tapping; longitudinal `ses-pre` / `ses-post` design.
- **Hyperscanning.** Two subjects, two NIRS systems, one task. The spec accommodates via parallel `sub-01` / `sub-02` folders with matched `task-` and synchronised `events.tsv` onsets.
- **BCI.** NIRS-BCI for motor-imagery or P300-NIRS — `task-motorimagery_acq-fnirs`.
- **Wearable / ambulatory.** Long continuous recordings, accelerometer co-channels for motion regression (`ACCELChannelCount`, `GYROChannelCount`).

## Software & resources

| Tool | Role | Link |
|---|---|---|
| **mne-nirs** | Python NIRS analysis + SNIRF + BIDS | [mne.tools/mne-nirs](https://mne.tools/mne-nirs/) |
| **mne-bids** | BIDS writer (handles NIRS) | [mne.tools/mne-bids](https://mne.tools/mne-bids/) |
| **Homer3** | MATLAB NIRS analysis (NIRx / Artinis lineage) | [openfnirs.org/software/homer/](https://openfnirs.org/software/homer/) |
| **NIRSToolbox** | MATLAB / GLM-style analysis | [github.com/huppertt/nirs-toolbox](https://github.com/huppertt/nirs-toolbox) |
| **fNIRS Optodes' Location Decider (fOLD)** | Optode-placement planning | [github.com/nirx/fOLD-public](https://github.com/nirx/fOLD-public) |
| **AtlasViewer** | Cap-to-atlas registration | [github.com/BUNPC/AtlasViewer](https://github.com/BUNPC/AtlasViewer) |
| **MCX / NIRFAST** | Light-transport Monte Carlo for fluence | [mcx.space](https://mcx.space/) |
| **SNIRF spec** | Format reference | [github.com/fNIRS/snirf](https://github.com/fNIRS/snirf) |
| **OpenNeuro NIRS datasets** | Real BIDS-NIRS corpora | [openneuro.org](https://openneuro.org/search/modality/nirs) |

## References

- BIDS NIRS extension spec — [bids-specification.readthedocs.io](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/near-infrared-spectroscopy.html)
- Luke R, Shader MJ, Larson E, et al. fNIRS-BIDS, an extension to the Brain Imaging Data Structure for functional near-infrared spectroscopy. *Sci Data.* 2023;10:580. [doi:10.1038/s41597-023-02437-z](https://doi.org/10.1038/s41597-023-02437-z)
- Tucker SM, Boas DA, Dehghani H, et al. Shared Near Infrared Spectroscopy Format (SNIRF). [github.com/fNIRS/snirf](https://github.com/fNIRS/snirf)
- Yücel MA, Lühmann AV, Scholkmann F, et al. Best practices for fNIRS publications. *Neurophotonics.* 2021;8(1):012101. [doi:10.1117/1.NPh.8.1.012101](https://doi.org/10.1117/1.NPh.8.1.012101)

## Where to next

- Neural-recording physics parallels: [fundamentals/sequences/eeg.md](../../fundamentals/sequences/eeg.md)
- EEG sibling (the electrical-vs-optical contrast): [bids/modalities/eeg.md](eeg.md)
- Motion co-recording (accelerometer, IMU): [bids/modalities/motion.md](motion.md)
- Hemodynamics analogy on the MR side: see the perf / func MR pages
- Clinical context: [clinical/stroke-and-tbi.md](../../clinical/stroke-and-tbi.md)
