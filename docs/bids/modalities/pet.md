# PET in BIDS

> One scanner emits photons in coincidence; one tracer carries the signal; one clock ties activity to time. BIDS for PET is mostly about getting that clock and that tracer right.

Course map: spec link → folder layout → suffixes → entities → required JSON → recommended JSON → blood TSV companion → conversion recipes → validation → pitfalls → disease use → tools → refs → next.

**Primary spec.** [BIDS — Positron Emission Tomography](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/positron-emission-tomography.html) (BEP009, merged). The PET extension grew out of [Norgaard 2022, *NeuroImage* 252:119027](https://doi.org/10.1016/j.neuroimage.2022.119027) and the [Knudsen 2020](https://doi.org/10.1177/0271678X20905433) reporting guideline.

## Folder layout — one-glance

```text
ds-pet/
├── dataset_description.json
├── participants.tsv
└── sub-01/
    ├── ses-baseline/
    │   ├── anat/
    │   │   └── sub-01_ses-baseline_T1w.nii.gz   # AC + PVC anchor
    │   └── pet/
    │       ├── sub-01_ses-baseline_trc-pib_pet.nii.gz        # 4D dynamic
    │       ├── sub-01_ses-baseline_trc-pib_pet.json
    │       ├── sub-01_ses-baseline_trc-pib_recording-manual_blood.tsv
    │       ├── sub-01_ses-baseline_trc-pib_recording-manual_blood.json
    │       └── sub-01_ses-baseline_trc-pib_events.tsv        # task PET only
    └── ses-followup/
        └── pet/
            └── sub-01_ses-followup_trc-pib_pet.nii.gz
```

The `pet/` folder always sits next to `anat/` because attenuation-corrected MR + partial-volume correction need the T1w. Cross-link: [fundamentals/sequences/pet.md](../../fundamentals/sequences/pet.md) for the underlying physics and quantification.

## Allowed suffixes

| Suffix | What it is |
|---|---|
| `pet` | 4D (dynamic frames) or 3D (single static frame) NIfTI; chronologically ordered |
| `events` | REQUIRED for task-based PET (stimulus-locked activation studies) |
| `blood` | Arterial / venous sampling time-activity curve; pairs with `recording-<label>` |
| `physio` / `stim` | Inline cardiac / respiratory / scanner-trigger / stim presentation |

## Filename entities — in order

```
sub-<label>[_ses-<label>][_task-<label>][_trc-<label>][_rec-<label>][_run-<index>]_pet.<ext>
```

| Entity | Required? | Notes |
|---|---|---|
| `sub-` | always | subject label |
| `ses-` | if longitudinal | each visit = new injection |
| `task-` | only for task-PET | activation paradigm |
| `trc-` | if >1 tracer | tracer label (e.g. `trc-pib`, `trc-fdg`) |
| `rec-` | optional | reserved values: `acdyn`, `acstat`, `nacdyn`, `nacstat` |
| `run-` | if >1 run | within-session repeat |

## Required JSON sidecar fields

The spec splits required fields into four blocks. Skip none of them — `n/a` is acceptable in a handful of places (noted).

### Radiochemistry

| Field | Type | Example |
|---|---|---|
| `TracerName` | string | `"pib"` |
| `TracerRadionuclide` | string | `"C11"` |
| `InjectedRadioactivity` | number | `370` |
| `InjectedRadioactivityUnits` | string | `"MBq"` |
| `InjectedMass` | number or `"n/a"` | `5.0` (FDG: `"n/a"`) |
| `InjectedMassUnits` | string or `"n/a"` | `"ug"` |
| `SpecificRadioactivity` | number or `"n/a"` | `73000` |
| `SpecificRadioactivityUnits` | string or `"n/a"` | `"MBq/ug"` |
| `ModeOfAdministration` | string | `"bolus"` / `"infusion"` / `"bolus-infusion"` |

### Time

| Field | Type | Notes |
|---|---|---|
| `TimeZero` | string (`HH:MM:SS`) | the anchor — every other timestamp is relative |
| `ScanStart` | number | seconds from `TimeZero` to first frame |
| `InjectionStart` | number | seconds from `TimeZero` to bolus start |
| `FrameTimesStart` | array of numbers | per-frame start, seconds, length = N frames |
| `FrameDuration` | array of numbers | per-frame duration, seconds, length = N frames |

### Reconstruction

| Field | Type | Notes |
|---|---|---|
| `AcquisitionMode` | string | `"list mode"` / `"sinogram"` / `"static"` / `"dynamic"` |
| `ImageDecayCorrected` | boolean | `true` if already decay-corrected |
| `ImageDecayCorrectionTime` | number | seconds from `TimeZero` |
| `ReconMethodName` | string | e.g. `"OSEM-PSF-TOF"` |
| `ReconMethodParameterLabels` | array | e.g. `["iterations", "subsets"]` |
| `ReconMethodParameterUnits` | array or `"none"` | match labels |
| `ReconMethodParameterValues` | array or `"none"` | match labels |
| `ReconFilterType` | string | e.g. `"Gaussian"` |
| `ReconFilterSize` | number or `"none"` | mm FWHM |
| `AttenuationCorrection` | string | `"CT"` / `"MR Dixon"` / `"MR UTE"` / `"None"` |

### Hardware

| Field | Type |
|---|---|
| `Manufacturer` | `"Siemens"` |
| `ManufacturersModelName` | `"Biograph mMR"` |
| `Units` | `"Bq/mL"` |

### Minimal sidecar — copy-paste

```json
{
  "TracerName": "pib",
  "TracerRadionuclide": "C11",
  "InjectedRadioactivity": 370,
  "InjectedRadioactivityUnits": "MBq",
  "InjectedMass": 5.0,
  "InjectedMassUnits": "ug",
  "SpecificRadioactivity": 73000,
  "SpecificRadioactivityUnits": "MBq/ug",
  "ModeOfAdministration": "bolus",
  "TimeZero": "10:32:00",
  "ScanStart": 0,
  "InjectionStart": 0,
  "FrameTimesStart": [0, 15, 30, 60, 120, 240, 480, 960, 1800, 3300],
  "FrameDuration":   [15, 15, 30, 60, 120, 240, 480, 840, 1500, 1500],
  "AcquisitionMode": "list mode",
  "ImageDecayCorrected": true,
  "ImageDecayCorrectionTime": 0,
  "ReconMethodName": "OSEM-PSF-TOF",
  "ReconMethodParameterLabels": ["iterations", "subsets"],
  "ReconMethodParameterUnits": ["none", "none"],
  "ReconMethodParameterValues": [8, 21],
  "ReconFilterType": "Gaussian",
  "ReconFilterSize": 5.0,
  "AttenuationCorrection": "CT",
  "Manufacturer": "Siemens",
  "ManufacturersModelName": "Biograph mMR",
  "Units": "Bq/mL"
}
```

## Recommended JSON fields

| Block | Field | Use |
|---|---|---|
| Pharmaceuticals | `PharmaceuticalName`, `PharmaceuticalDoseAmount`, `PharmaceuticalDoseUnits`, `PharmaceuticalDoseRegimen`, `PharmaceuticalDoseTime` | unblinded drug arm |
| Time | `InjectionEnd` | bolus end seconds from `TimeZero` |
| Reconstruction | `ScatterCorrection`, `RandomsCorrection`, `DecayCorrectionFactor` | full provenance |
| Subject | `BodyWeight`, `BodyPart` | SUV normalisation |

## Blood TSV — the kinetic modelling companion

Dynamic-PET kinetic modelling needs an input function. The blood TSV carries the time-activity curve and lives next to the `_pet.nii.gz`:

```text
sub-01_ses-baseline_trc-pib_recording-manual_blood.tsv
sub-01_ses-baseline_trc-pib_recording-manual_blood.json
```

The `recording-<label>` distinguishes manual arterial sampling, automated blood sampler (ABSS), image-derived input, or a venous draw.

**Required TSV columns** (in order):

| Column | When |
|---|---|
| `time` | always — seconds from `TimeZero` |
| `plasma_radioactivity` | if `PlasmaAvail: true` |
| `whole_blood_radioactivity` | if `WholeBloodAvail: true` |
| `metabolite_parent_fraction` | if `MetaboliteAvail: true` |
| `hplc_recovery_fractions` | if `MetaboliteRecoveryCorrectionApplied: true` |

**Required JSON sidecar fields** for the blood file: `PlasmaAvail`, `MetaboliteAvail`, `WholeBloodAvail`, `DispersionCorrected`, plus `MetaboliteMethod` and `MetaboliteRecoveryCorrectionApplied` whenever metabolites are tracked.

## Conversion recipes

The canonical converter is [`PET2BIDS`](https://github.com/openneuropet/PET2BIDS) ([Norgaard 2022](https://doi.org/10.1016/j.neuroimage.2022.119027)) — Python and MATLAB wrappers around `dcm2niix`, Siemens ECAT, Philips PAR/REC, GE RDS / DICOM-MF, and blood-curve spreadsheets. It writes a fully populated sidecar from the scanner export.

```bash
# Siemens DICOM → BIDS-PET
pip install pypet2bids
dcm2niix4pet \
    /raw/sub-01/PET \
    --destination-path bids/sub-01/ses-baseline/pet \
    --kwargs TracerName=pib TracerRadionuclide=C11 \
             InjectedRadioactivity=370 InjectedRadioactivityUnits=MBq \
             ModeOfAdministration=bolus TimeZero=ScanStart \
    --silent
```

For ECAT (still common at Turku, NIMH):

```bash
ecatpet2bids /raw/sub-01/pib_dyn.v --destination-path bids/sub-01/...
```

Cross-link: [bids/dicom-to-bids.md](../dicom-to-bids.md) for the heuristics-file mental model that also applies here, and [PETPrep](https://github.com/nipreps/petprep_hmc) for downstream BIDS-app preprocessing (head-motion correction, MR co-registration, partial-volume correction).

## Validation checks

The standard [`bids-validator`](https://bids-standard.github.io/bids-validator/) (≥ 1.8) covers PET. Beyond schema:

- Check `len(FrameTimesStart) == len(FrameDuration) == N_frames_in_nifti`.
- Check `ImageDecayCorrected` is consistent with what your reconstruction actually did — mismatching here silently doubles or halves your kBq/mL.
- Check the blood TSV `time` column is monotonic and starts at or after the injection.

## Common pitfalls

1. **`TimeZero` ambiguity.** Most labs set `TimeZero` = `ScanStart`; some set it = `InjectionStart`. Pick one and write the same anchor for every subject in the study. If `ScanStart` ≠ `InjectionStart`, set both fields explicitly and don't hand-derive timing.
2. **Frame *duration* vs cumulative frame *time*.** `FrameDuration[i]` is the length of frame *i*, not the elapsed time to frame *i*. Many vendor exports give the latter — convert with `np.diff(frame_end_times)`.
3. **Decay correction double-counting.** If `ImageDecayCorrected: true`, do not re-decay-correct downstream. PETPrep and PMOD assume the sidecar is authoritative.
4. **Tracer label collisions.** `trc-fdg` and `trc-FDG` are different. Pick lowercase (BIDS convention) and stick with it.
5. **Missing blood file in dynamic studies.** A 90-minute `_pet.nii.gz` without an input function is useful only for SUV, not for $V_T$ / $BP_{ND}$. If you sampled blood, store it; if you didn't, document `_pet.json: "ReferenceRegion"` and use a reference-tissue model — see [fundamentals/sequences/pet.md §5.5](../../fundamentals/sequences/pet.md).
6. **Attenuation-correction string drift.** `"CT"` ≠ `"CT-based"` ≠ `"CTAC"`. The spec doesn't enumerate but downstream tools (PETPrep) match on case-sensitive substrings — pick one form per dataset.
7. **Static vs dynamic in the same session.** Use `_rec-acstat` / `_rec-acdyn` to keep them apart, not `_run-` (which implies same protocol).

## Disease-specific use cases

- **Alzheimer's amyloid PET** (florbetapir, florbetaben, flutemetamol, PIB). Static late-frame, SUVR with cerebellar reference, then Centiloid rescaling. See [clinical/alzheimers-and-dementia.md](../../clinical/alzheimers-and-dementia.md).
- **Tau PET** (flortaucipir, MK-6240, PI-2620). SUVR + PVC mandatory in atrophic cortex.
- **FDG metabolism**. Static SUV for oncology; dynamic Patlak $K_i$ in research and pre-surgical epilepsy ([clinical/epilepsy.md](../../clinical/epilepsy.md)).
- **Dopamine receptor / transporter PET** (raclopride, DOPA, DTBZ, FP-CIT). Dynamic with reference-tissue SRTM → $BP_{ND}$. See [clinical/parkinsons-and-movement.md](../../clinical/parkinsons-and-movement.md).
- **TSPO neuroinflammation** (PBR28, DPA-714). Arterial input mandatory; stratify by TSPO genotype in `participants.tsv` (`group: HAB/MAB/LAB`).

## Software & resources

| Tool | Role | Link |
|---|---|---|
| **PET2BIDS** | DICOM / ECAT / PAR-REC → BIDS-PET, sidecar + blood TSV | [openneuropet/PET2BIDS](https://github.com/openneuropet/PET2BIDS) |
| **PETPrep** | BIDS-app: head-motion correction, MR co-registration, PVC | [nipreps/petprep_hmc](https://github.com/nipreps/petprep_hmc) |
| **PMOD** | Commercial kinetic-modelling suite | [pmod.com](https://www.pmod.com/web/) |
| **Turku PET Centre scripts** | Open-source kinetic + Logan + Patlak | [turkupetcentre.fi](https://www.turkupetcentre.fi/) |
| **NiftyPET** | Python reconstruction + kinetic | [NiftyPET/NiftyPET](https://github.com/NiftyPET/NiftyPET) |
| **PETPVC** | Partial-volume-correction toolbox | [UCL/PETPVC](https://github.com/UCL/PETPVC) |
| **OpenNeuro PET datasets** | Real BIDS-PET corpora for testing | [openneuro.org](https://openneuro.org/search/modality/pet) |

## References

- BIDS PET extension spec — [bids-specification.readthedocs.io](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/positron-emission-tomography.html)
- Norgaard M, Matheson GJ, Hansen HD, et al. PET-BIDS: an extension to the Brain Imaging Data Structure for positron emission tomography. *NeuroImage.* 2022;252:119027. [doi:10.1016/j.neuroimage.2022.119027](https://doi.org/10.1016/j.neuroimage.2022.119027)
- Knudsen GM, Ganz M, Appelhoff S, et al. Guidelines for content and format of PET brain data in publications and archives. *J Cereb Blood Flow Metab.* 2020;40(8):1576-1585. [doi:10.1177/0271678X20905433](https://doi.org/10.1177/0271678X20905433)
- Innis RB, Cunningham VJ, Delforge J, et al. Consensus nomenclature for in vivo imaging of reversibly binding radioligands. *J Cereb Blood Flow Metab.* 2007;27(9):1533-1539. [doi:10.1038/sj.jcbfm.9600493](https://doi.org/10.1038/sj.jcbfm.9600493)

## Where to next

- Physics + quantification: [fundamentals/sequences/pet.md](../../fundamentals/sequences/pet.md)
- Co-registered MR for AC + PVC: anat / qmri pages (sibling MR-modalities chapter)
- Clinical context: [clinical/alzheimers-and-dementia.md](../../clinical/alzheimers-and-dementia.md), [clinical/parkinsons-and-movement.md](../../clinical/parkinsons-and-movement.md)
- Once your dataset is BIDS-PET-valid: [bids/derivatives.md](../derivatives.md) for the PETPrep output layout.
