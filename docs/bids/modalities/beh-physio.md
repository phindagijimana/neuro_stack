# Behaviour, physiology, and stimulus in BIDS

> The "everything else" page. Three small but load-bearing patterns: **beh/** for behaviour without imaging, **`_physio`** for cardiac / respiratory / pulse-ox alongside imaging, **`_stim`** for the stimuli that drove the task.

Course map: spec links → beh/ subsection → physio subsection → stim subsection → recipes → validation → pitfalls → use cases → tools → refs → next.

**Primary specs.**
- [BIDS — Behavioural experiments](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/behavioral-experiments.html) for `beh/`.
- [BIDS — Physiological recordings](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/physiological-recordings.html) for `_physio` and `_stim` inside imaging-modality folders.

---

## 1. `beh/` — behaviour without imaging

Psychophysics, computer-based cognitive paradigms, questionnaires-with-timing, anything that produces a behavioural trace without a concurrent neural recording.

### Folder layout

```text
ds-beh/
├── dataset_description.json
├── participants.tsv
└── sub-01/
    └── ses-01/
        └── beh/
            ├── sub-01_ses-01_task-stroop_events.tsv      # discrete trials
            ├── sub-01_ses-01_task-stroop_events.json
            ├── sub-01_ses-01_task-tracking_beh.tsv.gz    # continuous samples
            ├── sub-01_ses-01_task-tracking_beh.json
            └── sub-01_ses-01_task-tracking_physio.tsv.gz # heart rate, etc.
```

### Allowed suffixes

| Suffix | Use |
|---|---|
| `events` | discrete trial table with `onset`, `duration`, `trial_type` |
| `beh` | continuous behavioural samples (`.tsv` or `.tsv.gz`) |
| `physio` | gzipped TSV of continuous physiological signals (cardiac, respiratory, gsr, ...) |
| `stim` | gzipped TSV of continuous stimulus signal (audio envelope, video frame index, ...) |

### Filename entities

```
sub-<label>[_ses-<label>]_task-<label>[_acq-<label>][_run-<index>]_<suffix>.<ext>
```

`task-` is mandatory.

### JSON sidecar fields

**Recommended:** `TaskName`, `TaskDescription`, `Instructions`, `CogAtlasID`, `CogPOID`, `InstitutionName`, `InstitutionAddress`, `InstitutionalDepartmentName`.

**Required when applicable:** `SamplingFrequency` (for continuous `_beh` / `_physio` / `_stim`), `StartTime` (relative to the start of the run).

```json
{
  "TaskName": "stroop",
  "TaskDescription": "Colour-word interference; 4 colours x 2 congruency = 8 conditions.",
  "Instructions": "Press the key matching the ink colour, ignore the word.",
  "CogAtlasID": "https://www.cognitiveatlas.org/task/id/trm_550b54a8b30f4/"
}
```

### When `beh/` vs `func/`

| Scenario | Folder |
|---|---|
| Behaviour with **no** concurrent neural recording | `beh/` |
| Behaviour concurrent with fMRI | `func/sub-XX_task-XX_events.tsv` |
| Behaviour concurrent with EEG / MEG / iEEG | inside that modality folder's `_events.tsv` |
| Pre-scan training session (no scanner) | `beh/` |

### Example `events.tsv`

```tsv
onset	duration	trial_type	stim_word	stim_color	response	rt
0.50	0.25	congruent	RED	red	1	0.412
2.13	0.25	incongruent	BLUE	red	1	0.683
4.07	0.25	congruent	GREEN	green	1	0.395
```

Columns beyond `onset`/`duration` are dataset-defined; document them in a sibling `_events.json` (`response`, `rt`, etc.).

---

## 2. `_physio` — physiology paired with imaging

Lives **inside the imaging modality folder** (`func/`, `pet/`, `eeg/`, `ieeg/`, `meg/`, `anat/`, `dwi/`, `perf/`, `nirs/`, `motion/`) — never in its own top-level folder. Pairs trivially with the imaging file via shared `sub-` / `ses-` / `task-` / `run-` entities plus the `recording-` suffix when multiple devices are running.

### Folder layout

```text
ds-fmri-physio/
└── sub-01/
    └── func/
        ├── sub-01_task-rest_run-1_bold.nii.gz
        ├── sub-01_task-rest_run-1_bold.json
        ├── sub-01_task-rest_run-1_events.tsv
        ├── sub-01_task-rest_run-1_recording-cardiac_physio.tsv.gz
        ├── sub-01_task-rest_run-1_recording-cardiac_physio.json
        ├── sub-01_task-rest_run-1_recording-respiratory_physio.tsv.gz
        └── sub-01_task-rest_run-1_recording-respiratory_physio.json
```

### File format

`_physio.tsv.gz` is a **headerless** gzipped TSV. Column names live in the JSON `Columns` array, in order.

### Filename entities

```
sub-<label>[_ses-<label>][_task-<label>][_acq-<label>][_ce-<label>][_rec-<label>][_run-<index>][_recording-<label>]_physio.tsv.gz
```

`recording-<label>` distinguishes multiple physio streams with different sampling rates / hardware (e.g. `recording-cardiac` at 1 kHz vs `recording-respiratory` at 50 Hz).

### Required JSON sidecar fields

| Field | Type | Example |
|---|---|---|
| `SamplingFrequency` | number (Hz) | `1000` |
| `StartTime` | number (seconds) | `-22.5` (negative = physio started before imaging) |
| `Columns` | array of strings | `["cardiac", "respiratory", "trigger"]` |

### Minimal sidecar — copy-paste

```json
{
  "SamplingFrequency": 1000,
  "StartTime": -22.5,
  "Columns": ["cardiac", "respiratory", "trigger"],
  "Manufacturer": "BIOPAC",
  "ManufacturersModelName": "MP160",
  "cardiac": {
    "Description": "Pulse oximeter, fingertip.",
    "Units": "V"
  },
  "respiratory": {
    "Description": "Chest belt, abdominal.",
    "Units": "V"
  },
  "trigger": {
    "Description": "Scanner TR pulse, 5 V TTL.",
    "Units": "V"
  }
}
```

### Standard column names

- `cardiac` — pulse-ox / ECG
- `respiratory` — chest belt
- `trigger` — scanner TR pulse, used to align physio time to volume index

These three are the BIDS-recommended labels; downstream tools (fMRIPrep, [RETROICOR](https://www.fmrib.ox.ac.uk/datasets/techrep/tr05jc1/tr05jc1.pdf) implementations, [aCompCor](https://doi.org/10.1016/j.neuroimage.2007.04.042)) match on these strings.

### Typical use

- **RETROICOR cardiac + respiratory regression** during fMRI clean-up. See [analysis/functional.md](../../analysis/functional.md).
- **Cardiac-gated fMRI / PET**.
- **Respiration-volume-per-time (RVT) regressors** for breath-hold or hypercapnia paradigms.
- **Scanner-trigger alignment** between EEG / MEG and fMRI in simultaneous acquisitions.

---

## 3. `_stim` — stimulus presentation

Same machinery as `_physio` but the columns describe the *stimulus* track (audio envelope, video frame index, contrast level, motion energy ...) instead of physiology. Lives in the same imaging-modality folder.

### Example

```text
sub-01/func/
├── sub-01_task-movie_bold.nii.gz
├── sub-01_task-movie_events.tsv
├── sub-01_task-movie_recording-audio_stim.tsv.gz
├── sub-01_task-movie_recording-audio_stim.json
└── stimuli/
    └── movie_clip.mp4                          # raw stimulus media
```

`stim/` entries live next to the imaging file; the raw media (mp4, wav, png) goes in a `/stimuli/` folder at the dataset root and is referenced from `_events.tsv` via the `stim_file` column:

```tsv
onset	duration	trial_type	stim_file
0.0	120.0	movie_clip	stimuli/movie_clip.mp4
```

### Required JSON sidecar fields

Same as `_physio`: `SamplingFrequency`, `StartTime`, `Columns`. Sampling rate of `_stim` is typically much lower (24/30/60 fps for video, 100 Hz for envelope features) than `_physio` — give it its own `recording-` label so they don't collide.

### Minimal sidecar — copy-paste

```json
{
  "SamplingFrequency": 24,
  "StartTime": 0.0,
  "Columns": ["frame_index", "luminance", "motion_energy"],
  "frame_index": {"Description": "0-indexed video frame number.", "Units": "n/a"},
  "luminance":   {"Description": "Mean frame luminance.",         "Units": "n/a"},
  "motion_energy":{"Description": "Frame-to-frame Lucas-Kanade flow magnitude.", "Units": "n/a"}
}
```

### Typical use

- **Naturalistic stimuli (movie / audiobook fMRI).** Continuous stimulus features as encoding-model regressors.
- **Auditory tasks.** Speech envelope, F0, spectral features for TRF / encoding-model analysis with EEG / MEG.
- **Continuous-tracking psychophysics.** Cursor / paddle position over time.

---

## Conversion recipes

For BIOPAC / ADInstruments PowerLab data:

```python
# AcqKnowledge .acq → BIDS physio
import bioread, json, gzip, numpy as np
from pathlib import Path

acq = bioread.read("raw/sub-01_run-1.acq")
fs = acq.samples_per_second
cardiac = acq.channels[0].data
resp = acq.channels[1].data
trig = acq.channels[2].data

# StartTime: align using trigger - first trigger pulse marks volume 1
first_trig = np.argmax(trig > 2.5) / fs
start_time = -first_trig            # physio started this many s BEFORE imaging

data = np.column_stack([cardiac, resp, trig])
out = Path("bids/sub-01/func/sub-01_task-rest_run-1_recording-cardiac_physio.tsv.gz")
with gzip.open(out, "wt") as f:
    np.savetxt(f, data, delimiter="\t", fmt="%.6f")

sidecar = {
    "SamplingFrequency": fs,
    "StartTime": float(start_time),
    "Columns": ["cardiac", "respiratory", "trigger"],
}
out.with_suffix("").with_suffix(".json").write_text(json.dumps(sidecar, indent=2))
```

For Siemens scanner-side `.puls` / `.resp` (CMRR / PMU) files: [`bidsphysio`](https://github.com/cbinyu/bidsphysio) is the canonical converter.

```bash
pip install bidsphysio
acq2bids -i raw/sub-01_pulse.puls raw/sub-01_resp.resp \
         -b bids/sub-01/func/sub-01_task-rest_run-1_bold.nii.gz
```

Cross-link: [bids/dicom-to-bids.md](../dicom-to-bids.md).

## Validation

- `bids-validator` checks JSON schema and the file-exists / pairing rules.
- **Check the alignment.** Plot the trigger column against the imaging TR — first sustained pulse should be at index `-StartTime * SamplingFrequency` from the start of the physio file.
- **Check `Columns` length** equals the column count in the `.tsv.gz`.

## Common pitfalls

1. **`_physio.tsv.gz` with a header row.** The format is headerless. A header line shifts every sample by one row and the validator does not catch it — RETROICOR fits noise.
2. **`StartTime` sign error.** Negative = physio started *before* imaging (the common case). Positive = physio started *after* imaging (rare). A flipped sign mis-aligns the regression by the offset, often catastrophically.
3. **Multiple physio streams without `recording-`.** Two devices with different sampling rates collide on the same filename. Add `recording-cardiac` / `recording-respiratory` / `recording-gsr` to disambiguate.
4. **Stimulus media checked into the imaging folder.** Raw `.mp4` / `.wav` belong in `/stimuli/` at the dataset root, referenced from `events.tsv: stim_file`. Don't put a 500 MB video next to the BOLD.
5. **Behaviour-only data dropped in `func/`.** A psychophysics session with no scanner belongs in `beh/`. Putting it in `func/` makes `bids-validator` look for a missing `_bold.nii.gz`.
6. **Continuous behaviour stored as `events.tsv`.** Sample-by-sample tracking (cursor position at 100 Hz for 5 min) is `_beh.tsv.gz` with `SamplingFrequency`, not 30 000 rows in `events.tsv`.
7. **`Columns` order mismatched with the TSV.** The order in the JSON `Columns` array must match the column order in the gzipped TSV. Off-by-one means cardiac becomes respiratory in your noise model.

## Use cases

- **RETROICOR / aCompCor cleanup in fMRI.** [analysis/functional.md](../../analysis/functional.md), [fundamentals/sequences/epi.md](../../fundamentals/sequences/epi.md). Requires `recording-cardiac` + `recording-respiratory`.
- **Movie / naturalistic fMRI.** `_stim` with continuous stimulus features; encoding models.
- **Encoding-model EEG with speech.** Speech envelope as `_stim`; TRF / mTRF fit.
- **Sleep PSG.** EEG + EOG + EMG + ECG + respiratory belt + pulse-ox all together; physio columns inside `eeg/` folder.
- **Online behaviour platforms (PsychoPy / jsPsych).** Export → `events.tsv`. PsychoPy 2024+ ships a BIDS-events exporter.
- **Pre-scan training session.** `beh/sub-XX_ses-prescan_task-XX_events.tsv` paired with a later `func/sub-XX_ses-scan_task-XX_events.tsv`. See [analysis/design.md](../../analysis/design.md).

## Software & resources

| Tool | Role | Link |
|---|---|---|
| **bidsphysio** | Siemens PMU `.puls`/`.resp` → BIDS physio | [cbinyu/bidsphysio](https://github.com/cbinyu/bidsphysio) |
| **phys2bids** | Multi-vendor physio → BIDS | [physiopy/phys2bids](https://github.com/physiopy/phys2bids) |
| **bioread** | Python BIOPAC `.acq` reader | [uwmadison-chm/bioread](https://github.com/uwmadison-chm/bioread) |
| **PsychoPy BIDS export** | task → `events.tsv` | [psychopy.org](https://www.psychopy.org/) |
| **jsPsych → BIDS** | browser experiments → BIDS | [bids-jspsych](https://github.com/bids-standard/bids-examples) |
| **fMRIPrep RETROICOR / aCompCor** | consumes `_physio` for nuisance regression | [fmriprep.org](https://fmriprep.org/) |
| **bids-validator** | Schema + structural checks | [bids-standard/bids-validator](https://github.com/bids-standard/bids-validator) |

## References

- BIDS behavioural-experiments spec — [bids-specification.readthedocs.io](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/behavioral-experiments.html)
- BIDS physiological-recordings spec — [bids-specification.readthedocs.io](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/physiological-recordings.html)
- Glover GH, Li TQ, Ress D. Image-based method for retrospective correction of physiological motion effects in fMRI: RETROICOR. *Magn Reson Med.* 2000;44(1):162-167. [doi:10.1002/1522-2594(200007)44:1<162::AID-MRM23>3.0.CO;2-E](https://doi.org/10.1002/1522-2594(200007)44:1%3C162::AID-MRM23%3E3.0.CO;2-E)
- Behzadi Y, Restom K, Liau J, Liu TT. A component based noise correction method (CompCor) for BOLD and perfusion based fMRI. *NeuroImage.* 2007;37(1):90-101. [doi:10.1016/j.neuroimage.2007.04.042](https://doi.org/10.1016/j.neuroimage.2007.04.042)

## Where to next

- fMRI nuisance regression with physio: [analysis/functional.md](../../analysis/functional.md)
- EPI physics underlying physio-locked artefacts: [fundamentals/sequences/epi.md](../../fundamentals/sequences/epi.md)
- Task design + events files: [analysis/design.md](../../analysis/design.md)
- Continuous-recording siblings: [bids/modalities/eeg.md](eeg.md), [bids/modalities/meg.md](meg.md), [bids/modalities/motion.md](motion.md)
