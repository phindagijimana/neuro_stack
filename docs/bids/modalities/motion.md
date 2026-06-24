# Motion in BIDS

> Accelerometers, gyroscopes, optical trackers, IMUs, eye-tracking samples. The `motion/` folder is where everything that moves in time gets a TSV row and a sampling rate.

Course map: spec link → folder layout → suffixes → entities → required JSON → recommended JSON → channels table → conversion recipes → validation → pitfalls → use cases → tools → refs → next.

**Primary spec.** [BIDS — Motion](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/motion.html) (BEP029, recently merged). Source paper: [Welzel 2023, *Sci Data* 10:127](https://doi.org/10.1038/s41597-023-02022-4).

## Folder layout — one-glance

```text
ds-motion/
├── dataset_description.json
├── participants.tsv
└── sub-01/
    └── ses-01/
        └── motion/
            ├── sub-01_ses-01_task-walking_tracksys-imu_motion.tsv.gz
            ├── sub-01_ses-01_task-walking_tracksys-imu_motion.json
            ├── sub-01_ses-01_task-walking_tracksys-imu_channels.tsv
            ├── sub-01_ses-01_task-walking_tracksys-imu_channels.json
            ├── sub-01_ses-01_task-walking_tracksys-optic_motion.tsv.gz
            ├── sub-01_ses-01_task-walking_tracksys-optic_motion.json
            ├── sub-01_ses-01_task-walking_tracksys-optic_channels.tsv
            └── sub-01_ses-01_task-walking_events.tsv
```

Two tracking systems (`tracksys-imu` and `tracksys-optic`) for the same task = two pairs of files. The `events.tsv` is shared across systems.

## Allowed suffixes

| Suffix | Role |
|---|---|
| `motion` | gzipped TSV time series (one column per channel, no header) |
| `events` | trial / phase markers |
| `channels` | per-channel metadata (type, axis component, tracked point, units) |

## Filename entities — in order

```
sub-<label>[_ses-<label>]_task-<label>[_tracksys-<label>][_acq-<label>][_run-<index>]_<suffix>.<ext>
```

`tracksys-<label>` is **mandatory** for `_motion` files when multiple tracking systems are recorded. Use it consistently even with one system (`tracksys-imu`, `tracksys-eyetracker`, `tracksys-polhemus`).

## Required JSON sidecar fields

| Field | Type | Example |
|---|---|---|
| `TaskName` | string | `"walking"` |
| `SamplingFrequency` | number (Hz) | `200` |

### Minimal sidecar — copy-paste

```json
{
  "TaskName": "walking",
  "SamplingFrequency": 200,
  "SamplingFrequencyEffective": 199.98,
  "TrackingSystemName": "Xsens MTw Awinda",
  "Manufacturer": "Xsens",
  "ManufacturersModelName": "MTw Awinda",
  "DeviceSerialNumber": "MTw-12345",
  "SoftwareVersions": "MT Manager 2023.0",
  "RecordingDuration": 300.0,
  "MotionChannelCount": 24,
  "ACCELChannelCount": 9,
  "GYROChannelCount": 9,
  "MAGNChannelCount": 0,
  "ORNTChannelCount": 4,
  "POSChannelCount": 0,
  "VELChannelCount": 0,
  "MISCChannelCount": 2,
  "TrackedPointsCount": 3,
  "MissingValues": "n/a",
  "SubjectArtefactDescription": "Subject paused at ~120s; epoch flagged."
}
```

## Recommended JSON fields

| Field | Use |
|---|---|
| `SamplingFrequencyEffective` | actual achieved rate when nominal differs |
| `TrackingSystemName` | descriptive (`"Vicon Vantage"`, `"Tobii Pro Glasses 3"`, `"Polhemus Liberty"`) |
| `Manufacturer`, `ManufacturersModelName`, `DeviceSerialNumber`, `SoftwareVersions` | provenance |
| `RecordingDuration` | seconds |
| Channel counts | `MotionChannelCount`, `ACCELChannelCount`, `ANGACCELChannelCount`, `GYROChannelCount`, `JNTANGChannelCount`, `LATENCYChannelCount`, `MAGNChannelCount`, `MISCChannelCount`, `ORNTChannelCount`, `POSChannelCount`, `VELChannelCount` |
| `TrackedPointsCount` | distinct body / object points instrumented |
| `MissingValues` | string representation of missing data (e.g. `"n/a"`, `"-999"`) |
| `SubjectArtefactDescription` | free-text |

For each `channels.tsv`, a sibling `channels.json` can declare reference-frame metadata:

```json
{
  "RotationOrder": "ZYX",
  "RotationRule": "right-hand",
  "SpatialAxes": "RAS",
  "Description": "Right-handed XYZ in subject-relative pelvis frame."
}
```

## Companion files

### `_channels.tsv` — required columns (in order)

`name`, `component`, `type`, `tracked_point`, `units`.

- `component` — spatial axis: `x`, `y`, `z`; quaternion: `quat_x`, `quat_y`, `quat_z`, `quat_w`; or `n/a`.
- `type` — uppercase: `ACCEL`, `ANGACCEL`, `GYRO`, `JNTANG`, `LATENCY`, `MAGN`, `MISC`, `ORNT`, `POS`, `VEL`.
- `tracked_point` — body or object identifier (`"LeftFoot"`, `"RightWrist"`, `"HeadCoil"`, `"Pelvis"`).
- `units` — `m/s^2`, `rad/s`, `rad`, `m`, `T`, `n/a` (quaternions).

```tsv
name	component	type	tracked_point	units
pelvis_accel_x	x	ACCEL	Pelvis	m/s^2
pelvis_accel_y	y	ACCEL	Pelvis	m/s^2
pelvis_accel_z	z	ACCEL	Pelvis	m/s^2
pelvis_gyro_x	x	GYRO	Pelvis	rad/s
pelvis_gyro_y	y	GYRO	Pelvis	rad/s
pelvis_gyro_z	z	GYRO	Pelvis	rad/s
pelvis_orient_w	quat_w	ORNT	Pelvis	n/a
pelvis_orient_x	quat_x	ORNT	Pelvis	n/a
pelvis_orient_y	quat_y	ORNT	Pelvis	n/a
pelvis_orient_z	quat_z	ORNT	Pelvis	n/a
```

Recommended additional columns: `placement`, `reference_frame`, `sampling_frequency`, `status`, `status_description`.

### `_motion.tsv.gz`

Gzipped TSV, no header row, one column per `channels.tsv` row, in the same order. Time is implicit — sample $i$ is at $i / f_s$ seconds.

## Conversion recipes

There is no single canonical converter — the field is too young. Common paths:

```python
# IMU example: Xsens .mtb → BIDS motion
import pandas as pd
import gzip, json
from pathlib import Path
import xsensdeviceapi as xda  # vendor SDK

doc = xda.XsDocument()
doc.load("raw/sub-01/walking.mtb")
df = pd.DataFrame(doc.exportToDataFrame())   # vendor-specific helper

# Rename columns to BIDS-style and write
df.to_csv("bids/sub-01/ses-01/motion/sub-01_ses-01_task-walking_tracksys-imu_motion.tsv.gz",
          sep="\t", header=False, index=False, compression="gzip")

sidecar = {
    "TaskName": "walking",
    "SamplingFrequency": 200,
    "TrackingSystemName": "Xsens MTw Awinda",
    "Manufacturer": "Xsens",
    "ManufacturersModelName": "MTw Awinda"
}
Path("bids/sub-01/ses-01/motion/sub-01_ses-01_task-walking_tracksys-imu_motion.json").write_text(json.dumps(sidecar, indent=2))
```

For eye-tracking, the [`pymovements`](https://github.com/aeye-lab/pymovements) library writes BIDS-Motion eye-tracking layouts. For optical (Vicon, OptiTrack), [`mocapy`](https://github.com/aeye-lab) and lab-specific exporters are the norm.

A community converter [`motion-bids-tools`](https://github.com/bids-standard/bids-examples/tree/master/motion-bids-tools) is in development; check the [BIDS examples](https://github.com/bids-standard/bids-examples) repo for current best practice.

Cross-link: [bids/dicom-to-bids.md](../dicom-to-bids.md) for the heuristic-file pattern that also applies to multi-system motion conversion.

## Validation

`bids-validator` ≥ 1.14 covers Motion. Beyond schema:

- Column count in the gzipped `_motion.tsv.gz` must equal the row count of `_channels.tsv`.
- `MotionChannelCount` should equal the sum of all type-specific counts in the sidecar.
- For each unique `tracked_point`, all `component`s should be present (no missing axes on an IMU).
- If `SamplingFrequencyEffective` differs by more than ~1% from `SamplingFrequency`, downstream analyses should use the effective rate.

## Common pitfalls

1. **Forgetting `tracksys-` entity.** Without it, two co-recorded systems (Vicon + IMU) collide on the same filename and only one survives.
2. **Quaternion sign-convention drift.** `quat_w, quat_x, quat_y, quat_z` ordering and the right-hand rule differ vendor-to-vendor. Document `RotationOrder` + `RotationRule` in `channels.json` and verify by integrating a known rotation.
3. **Time-zero ambiguity for co-recorded systems.** Motion streams must align to the *same* `t=0` as the imaging/EEG they accompany. Use a shared trigger pulse or sync line; otherwise mark the offset in `events.tsv` with a `trial_type = sync_pulse` row.
4. **Eye-tracking confused with stimulus.** Eye samples (gaze position, pupil size) are motion data and belong in `motion/` with `tracksys-eyetracker`; stimulus video/audio they're locked to belongs in `stim/`. See [bids/modalities/beh-physio.md](beh-physio.md).
5. **Missing values encoded inconsistently.** `NaN`, empty string, `-1`, `9999` all mean "missing" to different vendors. Pick one (`"n/a"`) and declare via `MissingValues`.
6. **No reference frame.** `ACCEL` in "earth frame" vs "subject pelvis frame" gives wildly different signals. The `reference_frame` column in `channels.tsv` plus the `channels.json` `SpatialAxes` are how you disambiguate.
7. **Units string drift.** `m/s^2` (BIDS) vs `m/s²` (Unicode superscript) vs `g` (gravity units) all break validators or silently corrupt downstream physics. Stick to ASCII `m/s^2` / `rad/s` / `rad`.

## Disease-specific & special use cases

- **Head motion during MRI.** Markerless or marker-based head tracking (Tracoline, KinetiCor); BIDS-Motion under the same `sub-/ses-/` as the MR run, with `task-rest` mirroring the `func/` task. Cross-link [analysis/qc.md](../../analysis/qc.md) for motion-as-artefact.
- **Gait / Parkinson's / freezing-of-gait.** IMUs on pelvis, ankles, wrists; `tracksys-imu`, multiple `tracked_point` values. See [clinical/parkinsons-and-movement.md](../../clinical/parkinsons-and-movement.md).
- **Eye-tracking during fMRI / EEG.** `tracksys-eyetracker`, channels = `gaze_x`, `gaze_y`, `pupil_diameter`; co-aligned to the imaging timeline.
- **Mocap during physical task.** Vicon / OptiTrack `tracksys-optic`; joint angles via `JNTANG`.
- **Wearable longitudinal data.** Multi-day accelerometry (sleep, activity) — `task-freeliving_acq-7day`, with `SamplingFrequency` typically 20–100 Hz.

## Software & resources

| Tool | Role | Link |
|---|---|---|
| **pymovements** | Eye-tracking → BIDS-Motion | [aeye-lab/pymovements](https://github.com/aeye-lab/pymovements) |
| **mne-bids** | Some motion sidecars (eyetracker via MNE) | [mne.tools/mne-bids](https://mne.tools/mne-bids/) |
| **opensim** | Mocap analysis | [simtk.org/projects/opensim](https://simtk.org/projects/opensim) |
| **BIDS Motion validator** | Schema checks | bundled in [bids-standard/bids-validator](https://github.com/bids-standard/bids-validator) |
| **bids-examples (motion)** | Reference layouts | [bids-standard/bids-examples](https://github.com/bids-standard/bids-examples) |
| **OpenNeuro Motion datasets** | Real BIDS-Motion corpora | [openneuro.org](https://openneuro.org/search/modality/motion) |

## References

- BIDS Motion extension spec — [bids-specification.readthedocs.io](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/motion.html)
- Welzel J, Wischnewski S, Schneider J, et al. Motion-BIDS, an extension to the Brain Imaging Data Structure to organise motion data for reproducible research. *Sci Data.* 2023;10:127. [doi:10.1038/s41597-023-02022-4](https://doi.org/10.1038/s41597-023-02022-4)
- Jeung S, Hilton C, Berg T, et al. Motion-BIDS: a wearable and multimodal motion-data standard. *J Open Source Softw.* 2024. (Companion tooling paper; see the spec for canonical reference.)

## Where to next

- Motion-as-artefact for MRI: [analysis/qc.md](../../analysis/qc.md)
- Eye-tracking + stimulus pairing: [bids/modalities/beh-physio.md](beh-physio.md)
- Disease context: [clinical/parkinsons-and-movement.md](../../clinical/parkinsons-and-movement.md)
- Physio companion files inside imaging folders: [bids/modalities/beh-physio.md](beh-physio.md)
