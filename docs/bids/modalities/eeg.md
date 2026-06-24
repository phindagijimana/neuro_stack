# EEG in BIDS

> Scalp microvolts at millisecond resolution. The hardest BIDS conversion problems are coordinates and reference electrodes — the vendor formats are the easy part.

Course map: spec link → folder layout → suffixes → entities → required JSON → recommended JSON → companion TSVs → conversion recipes → validation → pitfalls → disease use → tools → refs → next.

**Primary spec.** [BIDS — Electroencephalography](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/electroencephalography.html) (BEP006, merged). Source paper: [Pernet 2019, *Sci Data* 6:103](https://doi.org/10.1038/s41597-019-0104-8).

## Folder layout — one-glance

```text
ds-eeg/
├── dataset_description.json
├── participants.tsv
└── sub-01/
    ├── ses-01/
    │   ├── anat/
    │   │   └── sub-01_ses-01_T1w.nii.gz             # for source localisation
    │   └── eeg/
    │       ├── sub-01_ses-01_task-oddball_run-1_eeg.vhdr
    │       ├── sub-01_ses-01_task-oddball_run-1_eeg.vmrk
    │       ├── sub-01_ses-01_task-oddball_run-1_eeg.eeg
    │       ├── sub-01_ses-01_task-oddball_run-1_eeg.json
    │       ├── sub-01_ses-01_task-oddball_run-1_channels.tsv
    │       ├── sub-01_ses-01_task-oddball_run-1_events.tsv
    │       ├── sub-01_ses-01_electrodes.tsv
    │       ├── sub-01_ses-01_coordsystem.json
    │       └── sub-01_ses-01_acq-NAS_photo.jpg      # fiducial photo
    └── ses-02/
        └── eeg/...
```

The `eeg/` folder lives alongside `anat/` only when source localisation is in scope; otherwise it's the only data-type folder.

## Allowed suffixes

| Suffix | Role |
|---|---|
| `eeg` | raw recording (one of the four formats below) |
| `events` | trial markers — `onset`, `duration`, `trial_type` |
| `channels` | per-channel metadata |
| `electrodes` | 3D electrode positions |
| `coordsystem` | which coordinate system electrodes live in |
| `photo` | fiducial-placement photos for QA |
| `physio` / `stim` | inline cardiac, respiratory, eye-tracker |

## Allowed raw file formats

| Format | Extensions | Note |
|---|---|---|
| **BrainVision Core** | `.vhdr` + `.vmrk` + `.eeg` (triplet) | RECOMMENDED — open spec, line-by-line readable |
| **European Data Format** | `.edf` (lowercase) | RECOMMENDED — most portable, but only 16-bit |
| **EEGLAB** | `.set` (+ `.fdt` if data are float) | OK if your shop is EEGLAB-native |
| **Biosemi** | `.bdf` (lowercase) | 24-bit; OK |

Anything else (`.cnt` from Neuroscan, `.mff` from EGI, vendor proprietary) must be converted first. [`mne-bids`](https://mne.tools/mne-bids/) does the conversion.

## Filename entities — in order

```
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_recording-<label>]_<suffix>.<ext>
```

`task-` is mandatory for `_eeg` files (rest counts: `task-rest`).

## Required JSON sidecar fields

| Field | Type | Example |
|---|---|---|
| `TaskName` | string | `"oddball"` |
| `SamplingFrequency` | number (Hz) | `1000` |
| `EEGReference` | string | `"linked mastoids"`, `"Cz"`, `"average"`, `"REST"` |
| `PowerLineFrequency` | number or `"n/a"` | `60` (Americas) or `50` (rest of world) |
| `SoftwareFilters` | object or `"n/a"` | `{"HighPass": {"Order": 4, "Frequency": 0.1}}` |

### Minimal sidecar — copy-paste

```json
{
  "TaskName": "oddball",
  "SamplingFrequency": 1000,
  "EEGReference": "average",
  "PowerLineFrequency": 60,
  "SoftwareFilters": "n/a",
  "EEGGround": "AFz",
  "RecordingType": "continuous",
  "RecordingDuration": 612.0,
  "EEGChannelCount": 64,
  "EOGChannelCount": 2,
  "ECGChannelCount": 1,
  "MiscChannelCount": 0,
  "TriggerChannelCount": 1,
  "EEGPlacementScheme": "10-10",
  "Manufacturer": "Brain Products",
  "ManufacturersModelName": "actiCHamp Plus",
  "CapManufacturer": "Brain Products",
  "CapManufacturersModelName": "actiCAP 64",
  "HardwareFilters": {"HighPass": {"Frequency": 0.016}, "LowPass": {"Frequency": 280}},
  "HeadCircumference": 56,
  "SubjectArtefactDescription": "Subject sneezed at ~250s; epochs around 245-255s flagged."
}
```

## Recommended JSON fields

| Field | Why it matters |
|---|---|
| `EEGGround` | needed for source modelling — current return path |
| `RecordingType` | `"continuous"`, `"epoched"`, or `"discontinuous"` |
| `RecordingDuration` | seconds, total continuous span |
| `EEGChannelCount` / `EOGChannelCount` / `ECGChannelCount` / `EMGChannelCount` / `MiscChannelCount` / `TriggerChannelCount` | per-type totals (consistency check with `channels.tsv`) |
| `EEGPlacementScheme` | `"10-20"`, `"10-10"`, `"10-5"`, or explicit list |
| `Manufacturer` / `ManufacturersModelName` | hardware provenance |
| `CapManufacturer` / `CapManufacturersModelName` | cap provenance |
| `HardwareFilters` | analog filter chain — informs offline filter choice |
| `HeadCircumference` | head-model fitting |
| `SubjectArtefactDescription` | free-text — saves the next analyst an hour |

## Companion files

### `_channels.tsv` — required columns

`name`, `type` (`EEG`, `EOG`, `ECG`, `EMG`, `MISC`, `TRIG`, ...), `units` (`V`, `µV`).

Recommended: `description`, `sampling_frequency`, `reference`, `low_cutoff`, `high_cutoff`, `notch`, `status` (`good` / `bad`), `status_description`.

```tsv
name	type	units	status
Fp1	EEG	uV	good
Fp2	EEG	uV	good
T7	EEG	uV	bad
HEOG	EOG	uV	good
STI 014	TRIG	n/a	good
```

### `_electrodes.tsv` — required columns

`name`, `x`, `y`, `z` (numbers; the coordinate frame is declared in `_coordsystem.json`). Recommended: `type` (`cup`, `ring`, `clip-on`), `material` (`Ag/AgCl`, `Gold`, `Tin`), `impedance` (kΩ).

### `_coordsystem.json` — required when `_electrodes.tsv` exists

```json
{
  "EEGCoordinateSystem": "CapTrak",
  "EEGCoordinateUnits": "mm",
  "EEGCoordinateSystemDescription": "Brain Products CapTrak photogrammetry, captured 2026-06-23.",
  "AnatomicalLandmarkCoordinates": {
    "NAS": [0.0, 88.5, -15.0],
    "LPA": [-77.0, 0.0, -25.0],
    "RPA": [ 77.0, 0.0, -25.0]
  },
  "AnatomicalLandmarkCoordinateSystem": "CapTrak",
  "AnatomicalLandmarkCoordinateUnits": "mm",
  "IntendedFor": ["bids::sub-01/ses-01/anat/sub-01_ses-01_T1w.nii.gz"]
}
```

The `IntendedFor` URI ties the electrodes to the T1w — mandatory for source localisation.

### `_events.tsv`

Standard BIDS — `onset`, `duration`, `trial_type`, plus any custom columns. Onsets are seconds from recording start (not from the first trigger pulse). Pitfall covered in [bids/pitfalls.md](../pitfalls.md#eventtsv-files).

## Conversion recipes

The canonical converter is [`mne-bids`](https://mne.tools/mne-bids/). It reads every format above and writes the full BIDS layout — including `electrodes.tsv` if positions are in the `Raw.info`.

```python
import mne
from mne_bids import BIDSPath, write_raw_bids

raw = mne.io.read_raw_brainvision("raw/sub-01_oddball.vhdr", preload=False)
raw.info["line_freq"] = 60  # mandatory before write_raw_bids
raw.set_channel_types({"HEOG": "eog", "ECG": "ecg", "STI 014": "stim"})

events, event_id = mne.events_from_annotations(raw)

bids_path = BIDSPath(subject="01", session="01", task="oddball", run="1",
                     root="bids", datatype="eeg")
write_raw_bids(raw, bids_path, events=events, event_id=event_id,
               overwrite=True, allow_preload=False)
```

`write_raw_bids` writes the JSON sidecar, `channels.tsv`, `events.tsv`, and (if `raw.info["dig"]` exists) `electrodes.tsv` + `coordsystem.json`. Re-running on a new subject produces a structurally identical tree.

For shops not on MNE, alternatives:

- [`bidskit`](https://github.com/jmtyszka/bidskit) — DICOM + EEG converter, lighter than HeuDiConv.
- [`eeglab.bids-matlab-tools`](https://github.com/sccn/bids-matlab-tools) — EEGLAB-native writer (`.set` → BIDS).
- [`BIDScoin`](https://github.com/Donders-Institute/bidscoin) — GUI editor with EEG plugins.

Cross-link: [bids/dicom-to-bids.md](../dicom-to-bids.md) for the converter-choice heuristic.

## Validation

`bids-validator` (≥ 1.10) handles EEG. Common errors:

- `CHANNELS_MISMATCH` — number of channels in `_channels.tsv` doesn't match the raw header.
- `EVENTS_TSV_MISSING` — task-EEG without an events file.
- `COORDSYS_MISSING` — `_electrodes.tsv` present but no `_coordsystem.json`.
- `INTENDED_FOR_MISSING` — `IntendedFor` path doesn't resolve.

Validate before and after re-referencing — `EEGReference` changes invalidate prior derivations.

## Common pitfalls

1. **`PowerLineFrequency` set wrong.** 50 Hz vs 60 Hz is geographic; using `60` in Europe means your notch filter sits on a peak that isn't there. Confirm against the recording country.
2. **`EEGReference` as a free-text string.** Use vocabulary — `"average"`, `"REST"`, `"Cz"`, `"linked mastoids"`, `"FCz"`. Downstream tools (MNE, EEGLAB) match on these strings.
3. **`electrodes.tsv` in T1w space without `IntendedFor`.** Co-registered positions are useless without a pointer to which T1w they're in.
4. **Sampling rate truncated by EDF.** EDF stores in 2-byte integers; high-res 24-bit (Biosemi) data quantises. Use BrainVision or BDF if your acquisition was 24-bit.
5. **`run-` instead of `task-` for repeated blocks of the same task.** Same task across runs = `run-1`, `run-2`; different tasks = different `task-`.
6. **Events in milliseconds.** BIDS requires seconds. A factor-of-1000 latency error usually surfaces as no significant ERPs.
7. **Inconsistent channel-type uppercase.** `channels.tsv` requires uppercase (`EEG`, `EOG`); MNE writes lowercase by default. `mne-bids` does the conversion — if you hand-write a TSV, capitalise.

## Disease-specific use cases

- **Epilepsy** — 24–72 h video-EEG, ICU continuous EEG. Use `task-rest_acq-vEEG_run-` per recording segment; markers in `events.tsv` (`trial_type` = `seizure_onset`, `spike`, `electrode_artifact`). See [clinical/epilepsy.md](../../clinical/epilepsy.md) and [analysis/eeg.md](../../analysis/eeg.md).
- **Sleep / PSG** — `task-sleep`, with `channels.tsv` covering EEG + EOG + EMG + ECG. AASM staging belongs in derivatives, not raw.
- **BCI corpora** — `task-motorimagery` / `task-p300speller` / `task-ssvep`. Benchmark suites: [MOABB](https://github.com/NeuroTechX/moabb).
- **Cognitive ERP** — N170, MMN, N2pc, N400, P3, ERN, LRP. Use the [ERP-CORE](https://erpinfo.org/erp-core) ([Kappenman 2021](https://doi.org/10.1016/j.neuroimage.2020.117465)) paradigm vocabulary in `task-` labels.

## Software & resources

| Tool | Role | Link |
|---|---|---|
| **mne-bids** | Canonical read/write for BIDS-EEG | [mne.tools/mne-bids](https://mne.tools/mne-bids/) |
| **bidskit** | Lightweight DICOM + EEG converter | [jmtyszka/bidskit](https://github.com/jmtyszka/bidskit) |
| **BIDScoin** | GUI mapping editor + plugins | [Donders-Institute/bidscoin](https://github.com/Donders-Institute/bidscoin) |
| **eeglab bids-matlab-tools** | EEGLAB `.set` → BIDS | [sccn/bids-matlab-tools](https://github.com/sccn/bids-matlab-tools) |
| **bids-validator** | Schema + structural checks | [bids-standard/bids-validator](https://github.com/bids-standard/bids-validator) |
| **OpenNeuro EEG datasets** | Real BIDS-EEG corpora | [openneuro.org](https://openneuro.org/search/modality/eeg) |

## References

- BIDS EEG extension spec — [bids-specification.readthedocs.io](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/electroencephalography.html)
- Pernet CR, Appelhoff S, Gorgolewski KJ, et al. EEG-BIDS, an extension to the brain imaging data structure for electroencephalography. *Sci Data.* 2019;6:103. [doi:10.1038/s41597-019-0104-8](https://doi.org/10.1038/s41597-019-0104-8)
- Appelhoff S, Sanderson M, Brooks TL, et al. MNE-BIDS: Organizing electrophysiological data into the BIDS format and facilitating their analysis. *J Open Source Softw.* 2019;4(44):1896. [doi:10.21105/joss.01896](https://doi.org/10.21105/joss.01896)
- Pernet C, Garrido MI, Gramfort A, et al. Issues and recommendations from the OHBM COBIDAS MEEG committee. *Nat Neurosci.* 2020;23(12):1473-1483. [doi:10.1038/s41593-020-00709-0](https://doi.org/10.1038/s41593-020-00709-0)

## Where to next

- Physics + preprocessing depth: [fundamentals/sequences/eeg.md](../../fundamentals/sequences/eeg.md)
- Analysis pipeline: [analysis/eeg.md](../../analysis/eeg.md), joint EEG/MEG: [analysis/eeg-meg.md](../../analysis/eeg-meg.md)
- Intracranial sibling: [bids/modalities/ieeg.md](ieeg.md)
- MEG sibling: [bids/modalities/meg.md](meg.md)
- Clinical: [clinical/epilepsy.md](../../clinical/epilepsy.md)
