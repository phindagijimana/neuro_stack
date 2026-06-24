# iEEG in BIDS

> The skull is no longer in the way. Spatial resolution drops to millimetres, sampling rates climb to tens of kHz, and the dataset's most important file becomes the T1w + CT registration that places each electrode.

Course map: spec link → folder layout → suffixes → entities → required JSON → recommended JSON → companion TSVs → conversion recipes → validation → pitfalls → disease use → tools → refs → next.

**Primary spec.** [BIDS — Intracranial Electroencephalography](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/intracranial-electroencephalography.html) (BEP010, merged). Source paper: [Holdgraf 2019, *Sci Data* 6:102](https://doi.org/10.1038/s41597-019-0105-7).

## Folder layout — one-glance

```text
ds-ieeg/
├── dataset_description.json
├── participants.tsv
└── sub-01/
    ├── ses-implantation/
    │   ├── anat/
    │   │   ├── sub-01_ses-implantation_T1w.nii.gz   # pre-op
    │   │   └── sub-01_ses-implantation_CT.nii.gz    # post-op (BEP024)
    │   └── ieeg/
    │       ├── sub-01_ses-implantation_task-rest_ieeg.edf
    │       ├── sub-01_ses-implantation_task-rest_ieeg.json
    │       ├── sub-01_ses-implantation_task-rest_channels.tsv
    │       ├── sub-01_ses-implantation_electrodes.tsv
    │       ├── sub-01_ses-implantation_coordsystem.json
    │       ├── sub-01_ses-implantation_acq-render_photo.png
    │       └── sub-01_ses-implantation_acq-xray_photo.jpg
    └── ses-monitoring/
        └── ieeg/
            ├── sub-01_ses-monitoring_task-rest_run-01_ieeg.edf
            └── sub-01_ses-monitoring_task-language_run-01_ieeg.edf
```

The post-op CT or T1w that anchors the electrode coordinates is **mandatory** in practice — without it the `_electrodes.tsv` numbers are unmoored.

## Allowed suffixes

| Suffix | Role |
|---|---|
| `ieeg` | raw recording |
| `events` | trial markers and seizure onsets |
| `channels` | per-channel metadata (type = `ECOG` / `SEEG` / `DBS`) |
| `electrodes` | 3D electrode positions in a declared coordinate frame |
| `coordsystem` | which coordinate system the electrodes live in |
| `photo` | operative photo, x-ray, drawing, render (`acq-photo`, `acq-xray`, `acq-drawing`, `acq-render`) |

## Allowed raw file formats

| Format | Extensions | Note |
|---|---|---|
| **European Data Format** | `.edf` (lowercase) | RECOMMENDED |
| **BrainVision Core** | `.vhdr` + `.vmrk` + `.eeg` | RECOMMENDED |
| **EEGLAB** | `.set` (+ `.fdt`) | OK |
| **NWB** | `.nwb` | Cortical-physiology-friendly; for very long / high-rate recordings |
| **MEF3** | `.mefd` (directory) | Used at Mayo, Stanford for multi-day continuous |

## Filename entities — in order

```
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_<suffix>.<ext>
```

`task-rest` is the common label for the long monitoring blocks between active task runs.

## Required JSON sidecar fields

| Field | Type | Example |
|---|---|---|
| `TaskName` | string | `"rest"` |
| `SamplingFrequency` | number (Hz) | `2048` |
| `PowerLineFrequency` | number or `"n/a"` | `60` |
| `SoftwareFilters` | object or `"n/a"` | `{"HighPass": {"Frequency": 0.1}}` |
| `iEEGReference` | string | `"intracranial reference contact RC1"` |

### Minimal sidecar — copy-paste

```json
{
  "TaskName": "rest",
  "SamplingFrequency": 2048,
  "PowerLineFrequency": 60,
  "SoftwareFilters": "n/a",
  "iEEGReference": "intracranial white-matter contact LWM1",
  "RecordingType": "continuous",
  "RecordingDuration": 3600.0,
  "ECOGChannelCount": 64,
  "SEEGChannelCount": 0,
  "EEGChannelCount": 2,
  "EOGChannelCount": 2,
  "ECGChannelCount": 1,
  "TriggerChannelCount": 1,
  "MiscChannelCount": 0,
  "iEEGGround": "scalp electrode placed on mastoid",
  "iEEGPlacementScheme": "left frontal subdural 8x8 grid + temporal 1x6 strip",
  "iEEGElectrodeGroups": "grid: G01..G64; strip: S01..S06",
  "Manufacturer": "Natus",
  "ManufacturersModelName": "Quantum Amplifier",
  "HardwareFilters": {"HighPass": {"Frequency": 0.016}, "LowPass": {"Frequency": 1000}},
  "ElectrodeManufacturer": "Ad-Tech",
  "ElectrodeManufacturersModelName": "FG64C-MP03X-000"
}
```

## Recommended JSON fields

- Channel counts split by type: `ECOGChannelCount`, `SEEGChannelCount`, `EEGChannelCount` (scalp), `EOGChannelCount`, `ECGChannelCount`, `EMGChannelCount`, `TriggerChannelCount`, `MiscChannelCount`.
- `iEEGGround` — return path; needed for re-referencing reasoning.
- `iEEGPlacementScheme` — free-text but be specific (`"left fronto-temporal 8x8 subdural grid + 4 anteromedial temporal strip electrodes"`).
- `iEEGElectrodeGroups` — naming convention so downstream tools can split grids from strips from depths.
- `Manufacturer`, `ManufacturersModelName`, `HardwareFilters`, `ElectrodeManufacturer`, `ElectrodeManufacturersModelName`.

## Companion files

### `_channels.tsv` — required columns

`name`, `type` (uppercase: `ECOG`, `SEEG`, `DBS`, `EEG`, `EOG`, `ECG`, `EMG`, `TRIG`, `AUDIO`, `MISC`), `units` (`V`, `µV`), `low_cutoff` (Hz, high-pass), `high_cutoff` (Hz, low-pass).

Recommended: `reference`, `group`, `sampling_frequency`, `description`, `notch`, `status` (`good` / `bad`), `status_description`.

```tsv
name	type	units	low_cutoff	high_cutoff	reference	group	status	status_description
G01	ECOG	uV	0.1	1000	G64	grid_left_frontal	good	n/a
G02	ECOG	uV	0.1	1000	G64	grid_left_frontal	bad	persistent line noise after re-prep
S01	ECOG	uV	0.1	1000	G64	strip_temporal	good	n/a
LD1	SEEG	uV	0.1	1000	LD12	depth_left_amygdala	good	n/a
ECG	ECG	uV	0.5	200	n/a	n/a	good	n/a
STI 014	TRIG	n/a	n/a	n/a	n/a	n/a	good	n/a
```

### `_electrodes.tsv` — required columns

`name`, `x`, `y`, `z`, `size` (contact area, mm²).

Recommended: `material`, `manufacturer`, `group`, `hemisphere` (`L` / `R`), `type` (`grid`, `strip`, `depth`, `microwire`), `impedance` (kΩ), `dimension` (e.g. `"[8x8]"`, `"[1x6]"`).

```tsv
name	x	y	z	size	hemisphere	type	group
G01	-58.2	36.1	22.8	4.2	L	grid	grid_left_frontal
G02	-54.1	36.4	23.0	4.2	L	grid	grid_left_frontal
LD1	-22.7	-3.4	-21.1	2.0	L	depth	depth_left_amygdala
```

### `_coordsystem.json` — required when `_electrodes.tsv` exists

```json
{
  "iEEGCoordinateSystem": "ACPC",
  "iEEGCoordinateUnits": "mm",
  "iEEGCoordinateSystemDescription": "ACPC-aligned native T1w; electrodes registered from post-op CT via SPM coregistration then mapped to T1w.",
  "iEEGCoordinateProcessingDescription": "Manual contact localisation in iElectrodes; brain-shift correction applied for subdural grids (Hermes 2010).",
  "iEEGCoordinateProcessingReference": "doi:10.1016/j.jneumeth.2009.10.005",
  "IntendedFor": [
    "bids::sub-01/ses-implantation/anat/sub-01_ses-implantation_T1w.nii.gz"
  ]
}
```

Allowed `iEEGCoordinateSystem` keywords: `ACPC`, `MNI152Lin`, `Talairach`, `Pixels`, `Other`. Use `ACPC` for native pre-op T1w; `MNI152Lin` only if you've also normalised the electrodes into MNI space.

## Conversion recipes

[`mne-bids`](https://mne.tools/mne-bids/) is the canonical writer. The wrinkle in iEEG is that the raw data is the easy half — the *electrode coordinates* come from a separate localisation step (iElectrodes / [Lead-DBS](https://www.lead-dbs.org/) / Freesurfer + post-op CT).

```python
import mne
from mne_bids import BIDSPath, write_raw_bids

# 1. Read native EDF and tell MNE which channels are intracranial
raw = mne.io.read_raw_edf("raw/sub-01/run-01.edf", preload=False)
raw.set_channel_types({c: "ecog" for c in raw.ch_names if c.startswith("G")})
raw.set_channel_types({c: "seeg" for c in raw.ch_names if c.startswith("LD")})
raw.info["line_freq"] = 60

# 2. Attach precomputed electrode positions (from iElectrodes etc.)
import numpy as np
montage = mne.channels.make_dig_montage(
    ch_pos={"G01": np.array([-58.2, 36.1, 22.8]) / 1000.0,
            "G02": np.array([-54.1, 36.4, 23.0]) / 1000.0},
    coord_frame="mri",   # ACPC-aligned T1w
)
raw.set_montage(montage, on_missing="ignore")

# 3. Write BIDS
bids_path = BIDSPath(subject="01", session="implantation", task="rest",
                     run="01", root="bids", datatype="ieeg")
write_raw_bids(raw, bids_path, overwrite=True, allow_preload=False)
```

For NWB-native shops use [`pynwb`](https://pynwb.readthedocs.io/) + a custom writer; for MEF3 the [Mayo MEF tools](https://github.com/MultimodalNeuroimagingLab/mef_tools) export to EDF.

Cross-link: [bids/dicom-to-bids.md](../dicom-to-bids.md) for the broader converter mental model.

## Validation

`bids-validator` ≥ 1.10 covers iEEG. Beyond the schema:

- `ECOGChannelCount + SEEGChannelCount + …` must equal the actual channel count in the raw header.
- Every `_channels.tsv` `type == ECOG/SEEG/DBS` row must have a matching `_electrodes.tsv` row.
- `coordsystem.json: IntendedFor` must resolve to an existing T1w / CT.

## Common pitfalls

1. **Electrode coordinate frame ambiguity.** The most common silent bug: `_electrodes.tsv` in native T1w space but `coordsystem.json` declaring `MNI152Lin`. Source-localisation packages then unproject and your contacts land in the wrong gyrus. Declare the frame explicitly and verify by overlaying.
2. **Brain shift for subdural grids.** Post-op subdural grids shift 5–15 mm relative to pre-op MRI. Either correct (Hermes-style projection back to cortex) or document the shift in `iEEGCoordinateProcessingDescription`.
3. **Bipolar vs monopolar re-reference confusion.** `iEEGReference: "intracranial white-matter contact LWM1"` means *monopolar against LWM1*; bipolar pairs are usually stored after re-reference and must be flagged in `channels.tsv: reference`.
4. **Sampling-rate truncation in EDF.** Some iEEG amplifiers run at 8–32 kHz; EDF stores 16-bit and may force a downsample. Use BrainVision or NWB if your acquisition exceeded 16-bit dynamic range or > 30 kHz.
5. **Contact size missing.** `size` (mm²) is required and determines spatial integration assumptions — Ad-Tech 4.2 mm² ≠ micro 0.5 mm². Pull from the electrode datasheet, don't guess.
6. **Group labels collide.** Two grids called `"grid"` are indistinguishable downstream. Use `grid_left_frontal`, `grid_right_temporal`, `depth_left_amygdala`.
7. **`task-` for monitoring vs task blocks.** Long inter-task monitoring = `task-rest`; active behavioural runs = `task-stroop` / `task-naming` / etc. Don't lump them into one giant `_ieeg.edf` — split into `run-` per task.

## Disease-specific use cases

- **Pre-surgical epilepsy mapping.** sEEG + ECoG. Mark interictal spikes and seizure onsets in `events.tsv` (`trial_type` = `spike`, `seizure_onset`, `seizure_offset`). See [clinical/epilepsy.md](../../clinical/epilepsy.md), [analysis/eeg.md](../../analysis/eeg.md).
- **Cognitive iEEG.** Memory / language / decision tasks during the monitoring period; `task-language`, `task-memorymatch`, etc.
- **Closed-loop responsive stimulation (RNS).** Stimulation events flagged in `events.tsv` (`trial_type` = `stim_pulse`) with parameters in `events.json` or a sibling `_stim.tsv.gz`.
- **DBS recordings.** `channels.tsv: type = DBS`, with the four contacts of a Medtronic / Boston lead enumerated and `group` set per lead.

## Software & resources

| Tool | Role | Link |
|---|---|---|
| **mne-bids** | Read/write BIDS-iEEG | [mne.tools/mne-bids](https://mne.tools/mne-bids/) |
| **pybids** | Query BIDS-iEEG layouts from Python | [bids-standard.github.io/pybids](https://bids-standard.github.io/pybids/) |
| **iElectrodes** | Manual electrode localisation from post-op CT | [iElectrodes on GitHub](https://github.com/aojeda/iElectrodes) |
| **Lead-DBS** | DBS-lead reconstruction + atlases | [lead-dbs.org](https://www.lead-dbs.org/) |
| **fieldtrip-ieeg tutorial** | MATLAB workflow end-to-end | [fieldtriptoolbox.org/tutorial/human_ecog](https://www.fieldtriptoolbox.org/tutorial/human_ecog/) |
| **pynwb** | NWB I/O for very long recordings | [pynwb.readthedocs.io](https://pynwb.readthedocs.io/) |
| **mef_tools** | MEF3 ↔ EDF conversion | [MultimodalNeuroimagingLab/mef_tools](https://github.com/MultimodalNeuroimagingLab/mef_tools) |
| **OpenNeuro iEEG datasets** | Real BIDS-iEEG corpora | [openneuro.org](https://openneuro.org/search/modality/ieeg) |

## References

- BIDS iEEG extension spec — [bids-specification.readthedocs.io](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/intracranial-electroencephalography.html)
- Holdgraf C, Appelhoff S, Bickel S, et al. iEEG-BIDS, extending the Brain Imaging Data Structure specification to human intracranial electrophysiology. *Sci Data.* 2019;6:102. [doi:10.1038/s41597-019-0105-7](https://doi.org/10.1038/s41597-019-0105-7)
- Hermes D, Miller KJ, Noordmans HJ, Vansteensel MJ, Ramsey NF. Automated electrocorticographic electrode localization on individually rendered brain surfaces. *J Neurosci Methods.* 2010;185(2):293-298. [doi:10.1016/j.jneumeth.2009.10.005](https://doi.org/10.1016/j.jneumeth.2009.10.005)
- Appelhoff S, Sanderson M, Brooks TL, et al. MNE-BIDS. *J Open Source Softw.* 2019;4(44):1896. [doi:10.21105/joss.01896](https://doi.org/10.21105/joss.01896)

## Where to next

- Surface EEG sibling: [bids/modalities/eeg.md](eeg.md)
- Analysis deep dive: [analysis/eeg.md](../../analysis/eeg.md) (iEEG-specific sections), [analysis/eeg-meg.md](../../analysis/eeg-meg.md)
- Clinical: [clinical/epilepsy.md](../../clinical/epilepsy.md)
- BIDS dataset versioning for multi-day continuous recordings: [bids/datalad.md](../datalad.md)
