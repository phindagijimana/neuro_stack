# MEG in BIDS

> Five vendors, five native formats, three coordinate systems, one cryogenic dewar. The BIDS spec hides the chaos behind a single `meg/` folder — but only if you populate `coordsystem.json` correctly.

Course map: spec link → folder layout → suffixes → entities → required JSON → recommended JSON → companion files → conversion recipes → validation → pitfalls → disease use → tools → refs → next.

**Primary spec.** [BIDS — Magnetoencephalography](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetoencephalography.html) (BEP002, merged). Source paper: [Niso 2018, *Sci Data* 5:180110](https://doi.org/10.1038/sdata.2018.110).

## Folder layout — one-glance

```text
ds-meg/
├── dataset_description.json
├── participants.tsv
└── sub-01/
    └── ses-01/
        ├── anat/
        │   └── sub-01_ses-01_T1w.nii.gz                    # for BEM + source space
        └── meg/
            ├── sub-01_ses-01_task-rest_meg.fif             # Elekta/Neuromag/MEGIN
            ├── sub-01_ses-01_task-rest_meg.json
            ├── sub-01_ses-01_task-rest_channels.tsv
            ├── sub-01_ses-01_task-rest_events.tsv
            ├── sub-01_ses-01_coordsystem.json
            ├── sub-01_ses-01_headshape.pos                 # Polhemus head digitisation
            ├── sub-01_ses-01_acq-emptyroom_meg.fif         # noise covariance
            └── sub-01_ses-01_acq-NAS_photo.jpg
```

`anat/T1w.nii.gz` is in practice always required — BEM head models, cortical source space, and individual MRI co-registration all start there. The empty-room recording belongs in the **same** subject folder under `acq-emptyroom`.

## Allowed suffixes

| Suffix | Role |
|---|---|
| `meg` | raw recording in vendor-native format |
| `events` | trial markers — onsets in seconds from recording start |
| `channels` | per-channel metadata (`MEGMAG`, `MEGGRADAXIAL`, `MEGGRADPLANAR`, `MEGREFMAG`, ...) |
| `coordsystem` | which coordinate frame digitised landmarks live in |
| `headshape` | Polhemus / FastSCAN head-surface points |
| `markers` | KIT/Yokogawa coil-position file |
| `photo` | fiducial-placement photos |
| `physio` / `stim` | inline cardiac, respiratory, eye-tracker, stimulus track |

## Allowed raw file formats

| Vendor | Extensions | Note |
|---|---|---|
| **Elekta / Neuromag / MEGIN** | `.fif` | single-file; MNE-Python native |
| **CTF** | `.ds/` (directory) | folder is the "file" |
| **4D / BTi** | `pdf` + `config` (no extensions) | directory contents matter |
| **KIT / Yokogawa** | `.con`, `.sqd`, `.mrk` | coil-position marker file is mandatory |
| **KRISS** | `.kdf` | |
| **ITAB** | `.raw` + `.mhd` | |

"Unprocessed MEG data MUST be stored in the native file format of the MEG instrument."

## Filename entities — in order

```
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>][_proc-<label>][_split-<index>]_<suffix>.<ext>
```

- `acq-emptyroom` is the spec-encouraged label for the noise-only recording.
- `proc-sss` / `proc-tsss` flag Maxfilter SSS / tSSS pre-processed `.fif` files (Elekta).
- `split-` is for Elekta `.fif` files that exceed 2 GB and are auto-split by the acquisition software.

## Required JSON sidecar fields

| Field | Type | Example |
|---|---|---|
| `TaskName` | string | `"rest"` |
| `SamplingFrequency` | number (Hz) | `1000` |
| `PowerLineFrequency` | number or `"n/a"` | `60` |
| `SoftwareFilters` | object or `"n/a"` | `{"HighPass": {"Frequency": 0.1}}` |
| `DewarPosition` | string | `"upright"` / `"supine"` / `"60deg"` |
| `DigitizedLandmarks` | boolean | `true` if NAS/LPA/RPA digitised |
| `DigitizedHeadPoints` | boolean | `true` if head-surface digitised |

### Minimal sidecar — copy-paste

```json
{
  "TaskName": "rest",
  "SamplingFrequency": 1000,
  "PowerLineFrequency": 60,
  "SoftwareFilters": "n/a",
  "DewarPosition": "upright",
  "DigitizedLandmarks": true,
  "DigitizedHeadPoints": true,
  "RecordingType": "continuous",
  "RecordingDuration": 600.0,
  "MEGChannelCount": 306,
  "MEGREFChannelCount": 0,
  "EEGChannelCount": 64,
  "EOGChannelCount": 2,
  "ECGChannelCount": 1,
  "EMGChannelCount": 0,
  "TriggerChannelCount": 1,
  "MiscChannelCount": 0,
  "ContinuousHeadLocalization": true,
  "HeadCoilFrequency": [293, 307, 314, 321, 328],
  "MaxMovement": 4.2,
  "AssociatedEmptyRoom": "bids::sub-01/ses-01/meg/sub-01_ses-01_acq-emptyroom_meg.fif",
  "Manufacturer": "Elekta",
  "ManufacturersModelName": "Neuromag TRIUX",
  "SoftwareVersions": "Neuromag 3.4.1"
}
```

## Recommended JSON fields

- Channel counts: `MEGChannelCount`, `MEGREFChannelCount` (reference sensors), plus the EEG / EOG / ECG / EMG / trigger / misc counts as for EEG.
- `RecordingType`, `RecordingDuration`.
- `ContinuousHeadLocalization` — Elekta cHPI / CTF CHL flag.
- `HeadCoilFrequency` — drive frequencies of the HPI coils (typically 293–321 Hz).
- `MaxMovement` — peak head displacement (mm) computed by Maxfilter / equivalent.
- `AssociatedEmptyRoom` — BIDS URI to the noise-covariance recording.
- `Manufacturer`, `ManufacturersModelName`, `SoftwareVersions`, `DeviceSerialNumber`.

## Companion files

### `_coordsystem.json` — required

```json
{
  "MEGCoordinateSystem": "ElektaNeuromag",
  "MEGCoordinateUnits": "m",
  "MEGCoordinateSystemDescription": "Sensor positions in dewar/device space; landmarks digitised in subject-head coordinates.",
  "EEGCoordinateSystem": "ElektaNeuromag",
  "EEGCoordinateUnits": "m",
  "HeadCoilCoordinates": {
    "coil1": [-0.075, 0.072, 0.000],
    "coil2": [ 0.075, 0.072, 0.000],
    "coil3": [-0.075,-0.045, 0.000],
    "coil4": [ 0.075,-0.045, 0.000],
    "coil5": [ 0.000, 0.082, 0.030]
  },
  "HeadCoilCoordinateSystem": "ElektaNeuromag",
  "HeadCoilCoordinateUnits": "m",
  "AnatomicalLandmarkCoordinates": {
    "NAS": [0.000, 0.0885, -0.015],
    "LPA": [-0.077, 0.000, -0.025],
    "RPA": [ 0.077, 0.000, -0.025]
  },
  "AnatomicalLandmarkCoordinateSystem": "ElektaNeuromag",
  "AnatomicalLandmarkCoordinateUnits": "m",
  "DigitizedHeadPoints": "sub-01_ses-01_headshape.pos",
  "IntendedFor": ["bids::sub-01/ses-01/anat/sub-01_ses-01_T1w.nii.gz"]
}
```

Allowed `MEGCoordinateSystem` keywords: `CTF`, `ElektaNeuromag`, `4DBti`, `KitYokogawa`, `ChietiItab`, `Other`. The convention is **dewar / device space** for sensor positions and **subject head space** for the fiducials, with the link encoded by the cHPI coils.

### `_channels.tsv` — required columns

`name`, `type` (uppercase: `MEGMAG`, `MEGGRADAXIAL`, `MEGGRADPLANAR`, `MEGREFMAG`, `MEGREFGRADAXIAL`, `MEGREFGRADPLANAR`, `EEG`, `EOG`, `ECG`, `EMG`, `TRIG`, `MISC`, ...), `units` (`T`, `fT`, `fT/cm`, `V`).

Recommended: `description`, `sampling_frequency`, `low_cutoff`, `high_cutoff`, `notch`, `status`, `status_description`.

### `_headshape.<ext>` — Polhemus / FastSCAN

The free-form head-surface digitisation (~200–2000 points). Common extensions: `.pos`, `.txt`, `.elp`, `.hsp`. Referenced from `coordsystem.json: DigitizedHeadPoints`.

### `_markers.<ext>` — KIT / Yokogawa coil positions

`.mrk` files alongside the `_meg.sqd` — required for KIT data so the sensor-to-head transform is recoverable.

### `_events.tsv`

Standard BIDS columns; `onset` in seconds from recording start.

## Conversion recipes

[`mne-bids`](https://mne.tools/mne-bids/) is the canonical writer for all five vendor formats — it preserves the native file in place and only writes the sidecars + companion TSVs.

```python
import mne
from mne_bids import BIDSPath, write_raw_bids

raw = mne.io.read_raw_fif("raw/sub-01/rest_raw.fif", preload=False, allow_maxshield=True)
raw.info["line_freq"] = 60

events = mne.find_events(raw, stim_channel="STI 014")
event_id = {"standard": 1, "deviant": 2}

bids_path = BIDSPath(subject="01", session="01", task="rest",
                     root="bids", datatype="meg")
write_raw_bids(raw, bids_path, events=events, event_id=event_id,
               empty_room="raw/sub-01/empty_raw.fif",
               overwrite=True, allow_preload=False)
```

For CTF, point `read_raw_ctf` at the `.ds/` directory. For KIT pass the `.sqd` + `.mrk` + an `mrk_pre` / `mrk_post` pair. For 4D/BTi use `read_raw_bti`.

Cross-link: [bids/dicom-to-bids.md](../dicom-to-bids.md) for the converter-choice heuristic; [fundamentals/sequences/eeg.md](../../fundamentals/sequences/eeg.md) for the EEG-vs-MEG forward-problem comparison.

## Validation

`bids-validator` ≥ 1.10 handles MEG. Beyond schema:

- `_coordsystem.json: MEGCoordinateSystem` must be one of the allowed vendor keywords.
- Every `_meg.fif` > 2 GB should have `split-` siblings.
- `AssociatedEmptyRoom` URI must resolve and have the same `Manufacturer` + `SamplingFrequency`.

## Common pitfalls

1. **Dewar vs head coordinate confusion.** Sensors live in dewar/device space; subject anatomy lives in head space. The `cHPI / coil` transform is what links them. If your `_electrodes.tsv` puts EEG sensors in device space, source localisation in MNE will silently project to the wrong cortex.
2. **Fiducial mismatch with the T1w.** `NAS / LPA / RPA` must be the *same* points you pick on the MRI for co-registration. Mark them with vitamin-E capsules during the MRI scan if possible.
3. **`acq-emptyroom` recorded on a different day.** Noise covariance drifts with environment changes (passing trucks, helium fills). Record empty-room *the same session* if quantitative source amplitudes matter.
4. **Maxfilter SSS applied without flagging.** `proc-sss` / `proc-tsss` must label SSS-processed files — Maxfilter rotates the data and a downstream tool expecting raw will mis-handle it.
5. **Continuous head localisation flag missing.** `ContinuousHeadLocalization: true` lets downstream tools compensate for movement; default `false` leaves you blind to a moving subject.
6. **Split `.fif` files concatenated by hand.** Don't. Let MNE handle `split-1` / `split-2` / ... via `mne.io.read_raw_fif` — it stitches automatically and respects internal offsets.
7. **KIT data without `.mrk`.** The marker file *is* the sensor-to-head transform for Yokogawa. Without it, head modelling is impossible. Always copy both `.sqd` and `.mrk`.

## Disease-specific use cases

- **Pre-surgical epilepsy MEG.** Interictal spike localisation, especially MRI-negative cases. `task-rest_acq-clinical` is the convention. See [clinical/epilepsy.md](../../clinical/epilepsy.md).
- **Cognitive neuroscience.** Sensory / motor / language paradigms — the [HCP-MEG](https://www.humanconnectome.org/study/hcp-young-adult/data-releases) and [Cam-CAN](https://www.cam-can.org/) corpora are BIDS-MEG canonical examples.
- **MEG biomarkers in dementia.** Spectral slowing in AD; the [BioFIND](https://www.cam-can.org/index.php?content=biofind) MCI/AD MEG resource follows BIDS-MEG.
- **OPM-MEG (optically pumped magnetometers).** Wearable MEG. The spec accommodates it via `MEGCoordinateSystem: Other` and a descriptive sidecar; native standards still settling.

## Software & resources

| Tool | Role | Link |
|---|---|---|
| **mne-bids** | Canonical read/write for all vendor formats | [mne.tools/mne-bids](https://mne.tools/mne-bids/) |
| **MNE-Python** | MEG analysis (forward + inverse + connectivity) | [mne.tools](https://mne.tools) |
| **FieldTrip** | MATLAB MEG/EEG analysis with strong CTF support | [fieldtriptoolbox.org](https://www.fieldtriptoolbox.org/) |
| **Brainstorm** | MATLAB GUI-first MEG analysis | [neuroimage.usc.edu/brainstorm](https://neuroimage.usc.edu/brainstorm/) |
| **Maxfilter / MNE-Maxwell** | Elekta signal-space separation (SSS / tSSS) | [mne.preprocessing.maxwell_filter](https://mne.tools/stable/generated/mne.preprocessing.maxwell_filter.html) |
| **bids-validator** | Schema + structural checks | [bids-standard/bids-validator](https://github.com/bids-standard/bids-validator) |
| **OpenNeuro MEG datasets** | Real BIDS-MEG corpora | [openneuro.org](https://openneuro.org/search/modality/meg) |

## References

- BIDS MEG extension spec — [bids-specification.readthedocs.io](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetoencephalography.html)
- Niso G, Gorgolewski KJ, Bock E, et al. MEG-BIDS, the brain imaging data structure extended to magnetoencephalography. *Sci Data.* 2018;5:180110. [doi:10.1038/sdata.2018.110](https://doi.org/10.1038/sdata.2018.110)
- Appelhoff S, Sanderson M, Brooks TL, et al. MNE-BIDS. *J Open Source Softw.* 2019;4(44):1896. [doi:10.21105/joss.01896](https://doi.org/10.21105/joss.01896)
- Pernet C, Garrido MI, Gramfort A, et al. COBIDAS MEEG. *Nat Neurosci.* 2020;23(12):1473-1483. [doi:10.1038/s41593-020-00709-0](https://doi.org/10.1038/s41593-020-00709-0)

## Where to next

- EEG/MEG analysis: [analysis/eeg-meg.md](../../analysis/eeg-meg.md)
- EEG fundamentals + biophysics (forward problem): [fundamentals/sequences/eeg.md](../../fundamentals/sequences/eeg.md)
- Scalp EEG sibling: [bids/modalities/eeg.md](eeg.md)
- Intracranial sibling: [bids/modalities/ieeg.md](ieeg.md)
- Clinical: [clinical/epilepsy.md](../../clinical/epilepsy.md), [clinical/alzheimers-and-dementia.md](../../clinical/alzheimers-and-dementia.md)
