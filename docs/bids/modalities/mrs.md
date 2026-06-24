# Magnetic Resonance Spectroscopy in BIDS

> The newest first-class BIDS modality. The format is NIfTI-MRS; the converter is `spec2nii`; the gotchas are vendor-specific.

**Primary spec:** [BIDS — Magnetic Resonance Spectroscopy data](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-spectroscopy.html).

Course map: folder layout → suffixes → entities → required + recommended sidecar → NIfTI-MRS file format → conversion with `spec2nii` → vendor-format intake → reference scans → pitfalls → editing / 2D MRS / MRSI → tools → references → where to next.

The physics of MRS (chemical shift, J-coupling, editing, PRESS / sLASER / MEGA) lives in [fundamentals/sequences/mrs.md](../../fundamentals/sequences/mrs.md). This page is about getting the spectra into BIDS shape so [Osprey](https://github.com/schorschinho/osprey), [FSL-MRS](https://open.win.ox.ac.uk/pages/wclarke/fsl_mrs/), and [LCModel](http://s-provencher.com/lcmodel.shtml)-via-wrappers can consume it.

## Folder layout (one-glance)

```text
sub-01/
└── ses-01/
    └── mrs/
        ├── sub-01_ses-01_nuc-1H_voi-pcc_svs.nii.gz
        ├── sub-01_ses-01_nuc-1H_voi-pcc_svs.json
        ├── sub-01_ses-01_nuc-1H_voi-pcc_mrsref.nii.gz   # water reference
        ├── sub-01_ses-01_nuc-1H_voi-pcc_mrsref.json
        ├── sub-01_ses-01_nuc-1H_voi-pfc_mrsi.nii.gz     # 2D-CSI grid
        └── sub-01_ses-01_nuc-1H_voi-pfc_mrsi.json
```

Note the new entities `nuc-` (resonant nucleus, e.g. `1H`, `31P`) and `voi-` (volume-of-interest label).

## Allowed suffixes

| Suffix | What it is | When to use |
| --- | --- | --- |
| `svs` | Single-voxel spectroscopy | PRESS, STEAM, sLASER, MEGA-PRESS — a single voxel of interest |
| `mrsi` | MR spectroscopic imaging (CSI) | 2D or 3D chemical-shift-imaging grids |
| `unloc` | Unlocalised acquisition (coil-sensitivity only) | Calibration scans, phantom QA |
| `mrsref` | Reference scan for concentration / calibration | Water-unsuppressed or metabolite-reference scan |

The suffix is the *modality-type* identifier; the entities below distinguish nucleus / VOI / echo / inversion.

## Filename entities — in order

```
sub- ses- task- acq- nuc- voi- rec- run- echo- inv-
```

| Entity | Used when | Example |
| --- | --- | --- |
| `task-` | Functional / activation MRS | `task-vischeckerboard` |
| `acq-` | Distinguish editing schemes | `acq-megapress`, `acq-press`, `acq-sLASER` |
| `nuc-` | Resonant nucleus | `nuc-1H`, `nuc-31P`, `nuc-13C` |
| `voi-` | Anatomical VOI label | `voi-pcc`, `voi-occ`, `voi-thalR` |
| `rec-` | Different reconstructions of the same FID | `rec-online`, `rec-coilcombined` |
| `run-` | Repeats | `run-01` |
| `echo-` | Multi-TE MRS (e.g. T2-of-metabolite mapping) | `echo-1`, `echo-2` |
| `inv-` | Inversion-recovery prepared MRS | `inv-1`, `inv-2` |

`nuc-` and `voi-` are MRS-specific and you will almost always use them.

## Required JSON sidecar fields

| Field | Type | Example | Why |
| --- | --- | --- | --- |
| `SpectrometerFrequency` | number or array (MHz) | `123.255` | Conversion from time-domain to ppm |
| `ResonantNucleus` | string or array | `"1H"` | Must match the `nuc-` entity |
| `EchoTime` | number or array (s) | `0.030` | Editing schemes have multiple TEs |
| `SpectralWidth` | number (Hz) | `2000` | Time-domain bandwidth — required for spectral reconstruction |

## Recommended fields

| Field | Type | Why |
| --- | --- | --- |
| `RepetitionTime` | number (s) | T1-weighting correction |
| `MixingTime` | number (s) | Required for STEAM |
| `FlipAngle` | number or array (deg) | Quantification needs it |
| `AcquisitionVoxelSize` | array of 3 numbers (mm) | The single-voxel volume in mm |
| `NumberOfSpectralPoints` | integer | FID length |
| `NumberOfTransients` | integer | Number of averaged shots (SNR ∝ √N) |
| `MRAcquisitionType` | `"1D"` / `"2D"` / `"3D"` | Required for MRSI |
| `MatrixSize` | array of 3 integers | MRSI grid size |
| `InversionTime` | number (s) | If `inv-` entity is present |
| `ReferenceSignal` | BIDS URI | Path to the paired `_mrsref` file |
| `AnatomicalImage` | BIDS URI | Path to the T1w used for voxel placement |
| `WaterSuppression` | string | `"VAPOR"`, `"WET"`, etc. |
| `EditingPulseFrequency` `EditingPulseDuration` | for MEGA-PRESS | Required by Gannet / Osprey |

## File format — NIfTI-MRS

The spec REQUIRES source data to be converted to **NIfTI-MRS** ([Clarke et al. 2022](https://doi.org/10.1002/mrm.29418)): a standard `.nii.gz` whose extended JSON header carries spectroscopy-specific metadata (sample rate, dwell time, frequency, dimensions). The 4D structure is `[x, y, z, time]` for SVS (1×1×1×N) and MRSI (Nx×Ny×Nz×N).

Vendor-native formats (Siemens TWIX `.dat`, RDA `.rda`, DICOM `.ima`; Philips SDAT/SPAR; GE P-file; Bruker JDF) belong in `sourcedata/`, **not** in `mrs/`. `mrs/` is NIfTI-MRS only.

## Conversion recipes

### `spec2nii` — the canonical converter

[`spec2nii`](https://github.com/wexeee/spec2nii) ([Clarke et al. 2022](https://doi.org/10.1002/mrm.29418)) is the BIDS-aware tool that converts vendor formats into NIfTI-MRS.

```bash
# Siemens TWIX
spec2nii twix -e image -f sub-01_ses-01_nuc-1H_voi-pcc_svs \
    -o bids/sub-01/ses-01/mrs/ raw/twix/meas_MID0042_FID0001_svs_pcc.dat

# Siemens RDA
spec2nii rda raw/rda/svs_pcc.rda \
    -f sub-01_ses-01_nuc-1H_voi-pcc_svs \
    -o bids/sub-01/ses-01/mrs/

# Philips SDAT/SPAR
spec2nii philips raw/spar/svs_pcc.SPAR raw/spar/svs_pcc.SDAT \
    -f sub-01_ses-01_nuc-1H_voi-pcc_svs \
    -o bids/sub-01/ses-01/mrs/

# GE P-file
spec2nii ge raw/pfile/P12345.7 \
    -f sub-01_ses-01_nuc-1H_voi-pcc_svs \
    -o bids/sub-01/ses-01/mrs/
```

`spec2nii` writes both the NIfTI-MRS file and the BIDS sidecar. The water-reference scan converts the same way with `-f ..._mrsref`.

### Minimal `svs.json` (1H PRESS at 3 T, PCC voxel)

```json
{
  "Manufacturer": "Siemens",
  "ManufacturersModelName": "Prisma_fit",
  "MagneticFieldStrength": 3,
  "SpectrometerFrequency": 123.255,
  "ResonantNucleus": "1H",
  "EchoTime": 0.030,
  "RepetitionTime": 3.0,
  "SpectralWidth": 2000,
  "NumberOfSpectralPoints": 2048,
  "NumberOfTransients": 64,
  "FlipAngle": 90,
  "AcquisitionVoxelSize": [20, 20, 20],
  "WaterSuppression": "VAPOR",
  "ReferenceSignal": "bids::sub-01/ses-01/mrs/sub-01_ses-01_nuc-1H_voi-pcc_mrsref.nii.gz",
  "AnatomicalImage": "bids::sub-01/ses-01/anat/sub-01_ses-01_T1w.nii.gz"
}
```

### MEGA-PRESS (edited 1H MRS) sidecar additions

```json
{
  "EditingPulseFrequency": [1.9, 7.5],
  "EditingPulseDuration": 0.020,
  "EditCondition": ["ON", "OFF"]
}
```

## Validation checks

- **Suffix vs file dimensionality.** `svs` ⇒ NIfTI shape `(1, 1, 1, N)`; `mrsi` ⇒ `(Nx, Ny, Nz, N)`. `spec2nii` does this correctly; hand-rolled converters often do not.
- **`ResonantNucleus` matches `nuc-` entity.** Validator catches mismatches.
- **`SpectrometerFrequency` consistent with field strength.** 1H at 3 T ≈ 123.25 MHz; 1H at 7 T ≈ 297.16 MHz; 31P at 3 T ≈ 49.89 MHz. Off-by-10× errors mean someone forgot the gyromagnetic-ratio conversion.
- **`SpectralWidth` in Hz, not ppm.** A common manual-edit bug.
- **Paired `mrsref` exists** when `ReferenceSignal` is set.
- **`MRAcquisitionType` set for MRSI.** Required for spatial reconstruction.

Run [`bids-validator`](https://bids-standard.github.io/bids-validator/) — MRS validation support is recent (≥ v1.13). Pin the validator version.

## Common pitfalls

- **Storing vendor files in `mrs/`.** `mrs/` is NIfTI-MRS only. Vendor `.dat` / `.SDAT` / `.SPAR` / `.IMA` / `.7` belong in `sourcedata/sub-XX/ses-YY/mrs/`.
- **Missing water reference (`mrsref`).** Concentration-quantification pipelines (Osprey, FSL-MRS) need a water-unsuppressed reference for absolute quantification. Without it you are stuck with creatine-ratio metabolites only.
- **Frequency drift not corrected.** Long acquisitions (MEGA-PRESS, 8–10 min) drift in B0 frequency. The drift correction happens at *reconstruction* (FSL-MRS, Osprey); the raw NIfTI-MRS keeps the unaligned shots. Don't pre-align before storing — keep the raw FID.
- **Coil-combination already done by scanner.** Siemens RDA exports coil-combined data; TWIX exports per-channel. NIfTI-MRS handles both via the `dim_N_type` header; `spec2nii twix -e image` does the right thing.
- **Voxel placement metadata missing.** `AnatomicalImage` pointing at the T1w used for placement is recommended. Without it, voxel-coregistration in Osprey degrades to bounding-box guesswork.
- **MEGA-PRESS ON/OFF interleave.** Conventional ON-OFF-OFF-ON-... order. Store as the raw interleave; the analysis tool subtracts.
- **31P MRS at clinical 3 T.** Use the correct gyromagnetic ratio (γ_31P ≈ 17.235 MHz/T → 51.7 MHz at 3 T). Many converters default to 1H.

## Disease-specific & special use cases

- **Brain tumour grading** — single-voxel 1H PRESS over the lesion, with `acq-tumour_voi-lesion_svs` and a `voi-NAWM_svs` contralateral control. Quantify Cho / Cr ratio.
- **Hepatic encephalopathy / Wilson disease** — basal-ganglia 1H SVS for Glx / mI; `voi-thalL_svs`.
- **Epilepsy** — hippocampal 1H SVS for NAA / Cr lateralisation; `voi-hippL_svs` / `voi-hippR_svs`.
- **GABA editing (MEGA-PRESS)** — `acq-megapress` with `EditingPulseFrequency` set; consume with [Gannet](https://www.gabamrs.com/) or Osprey.
- **31P MRS** — `nuc-31P` plus the appropriate `SpectrometerFrequency`. Lower SNR; longer acquisitions (~10 min).
- **2D-MRSI** — `mrsi` suffix, `MRAcquisitionType: "2D"`, `MatrixSize: [16, 16, 1]`. Used in brain tumour mapping.
- **Functional MRS (fMRS)** — task-evoked changes in Glu / Lac. Use `task-` entity and a sibling `events.tsv`.

## Software & resources

| Tool / resource | Purpose |
| --- | --- |
| [BIDS spec — MRS](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-spectroscopy.html) | Authoritative reference |
| [NIfTI-MRS](https://github.com/wexeee/mrs_nifti_standard) | The file-format standard |
| [`spec2nii`](https://github.com/wexeee/spec2nii) | Vendor → NIfTI-MRS converter |
| [Osprey](https://github.com/schorschinho/osprey) | End-to-end MRS analysis BIDS-app |
| [FSL-MRS](https://open.win.ox.ac.uk/pages/wclarke/fsl_mrs/) | Python/CLI MRS fitting |
| [Gannet](https://www.gabamrs.com/) | MEGA-PRESS GABA quantification |
| [LCModel](http://s-provencher.com/lcmodel.shtml) | Classic spectral fitting (still used) |
| [`bids-validator`](https://bids-standard.github.io/bids-validator/) | Validate (v1.13+ for MRS) |
| [MRSHub demo datasets](https://mrshub.org/) | Reference NIfTI-MRS data |

## References & spec links

- BIDS spec — [Magnetic Resonance Spectroscopy](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-spectroscopy.html).
- Lin A, Andronesi O, Bogner W, et al. Minimum reporting standards for in vivo magnetic resonance spectroscopy (MRSinMRS). *Magn Reson Med.* 2021;86(5):2391–2402. [doi:10.1002/mrm.28868](https://doi.org/10.1002/mrm.28868)
- Clarke WT, Bell TK, Emir UE, et al. NIfTI-MRS: A standard data format for magnetic resonance spectroscopy. *Magn Reson Med.* 2022;88(6):2358–2370. [doi:10.1002/mrm.29418](https://doi.org/10.1002/mrm.29418)
- Oeltzschner G, Zöllner HJ, Hui SCN, et al. Osprey: open-source processing, reconstruction & estimation of magnetic resonance spectroscopy data. *J Neurosci Methods.* 2020;343:108827. [doi:10.1016/j.jneumeth.2020.108827](https://doi.org/10.1016/j.jneumeth.2020.108827)

## Where to next

- Physics: [fundamentals/sequences/mrs.md](../../fundamentals/sequences/mrs.md).
- Related modalities: [anat.md](./anat.md) for the T1w used in voxel placement, [qmri.md](./qmri.md) for the BEP-family this sits alongside.
- Analysis: MRS-specific analysis lives in Osprey / FSL-MRS — no dedicated handbook page yet.
