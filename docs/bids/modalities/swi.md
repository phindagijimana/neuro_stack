# Susceptibility-weighted imaging in BIDS

> SWI lives in its own `swi/` folder. The contrast-image is just the start — the *useful* data is the magnitude+phase pair from the underlying multi-echo GRE.

**Primary spec:** [BIDS — Magnetic Resonance Imaging Data → Susceptibility Weighted Imaging](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#susceptibility-weighted-imaging) (BEP016).

Course map: folder layout → suffixes → entities → required + recommended sidecar → magnitude / phase pairs → QSM source data → conversion → pitfalls → CAA / MS PRL / iron mapping → tools → references → where to next.

The physics of GRE / SWI / QSM lives in [fundamentals/sequences/swi.md](../../fundamentals/sequences/swi.md) and [gre.md](../../fundamentals/sequences/gre.md). This page is about the BIDS layout for vendor SWI contrast images and the multi-echo GRE that powers QSM reconstruction.

## Folder layout (one-glance)

```text
sub-01/
└── ses-01/
    └── swi/
        ├── sub-01_ses-01_swi.nii.gz                       # combined contrast (vendor)
        ├── sub-01_ses-01_swi.json
        ├── sub-01_ses-01_acq-multiecho_echo-1_part-mag_GRE.nii.gz
        ├── sub-01_ses-01_acq-multiecho_echo-1_part-mag_GRE.json
        ├── sub-01_ses-01_acq-multiecho_echo-1_part-phase_GRE.nii.gz
        ├── sub-01_ses-01_acq-multiecho_echo-1_part-phase_GRE.json
        ├── sub-01_ses-01_acq-multiecho_echo-2_part-mag_GRE.nii.gz
        ├── sub-01_ses-01_acq-multiecho_echo-2_part-phase_GRE.nii.gz
        ├── ...
        ├── sub-01_ses-01_acq-multiecho_echo-5_part-mag_GRE.nii.gz
        └── sub-01_ses-01_acq-multiecho_echo-5_part-phase_GRE.nii.gz
```

The `swi.nii.gz` is the *console-combined* SWI contrast image. The underlying multi-echo magnitude + phase pairs are what QSM tools (SEPIA, QSMxT) actually need.

## Allowed suffixes

| Suffix | What it is | When to use |
| --- | --- | --- |
| `swi` | Combined SWI contrast image (vendor-rendered: magnitude × phase mask) | Routine clinical SWI |
| `GRE` | The underlying multi-echo gradient-echo data | When you intend to do QSM offline |
| `MWFmap` | Myelin water fraction map | mcDESPOT / multi-echo T2 derivative |
| `T2starmap` | Quantitative T2* map | Computed from multi-echo GRE |

For derived QSM maps (the χ map), use `Chimap` under `derivatives/` per BEP016 — see [qmri.md](./qmri.md) for the BEP-001/qMRI conventions that apply to all derived maps.

## Filename entities — in order

```
sub- ses- acq- rec- run- echo- part- chunk-
```

| Entity | Used when | Example |
| --- | --- | --- |
| `acq-` | Distinguish protocols (clinical SWI vs research multi-echo GRE) | `acq-clinical`, `acq-multiecho` |
| `rec-` | Different console reconstructions | `rec-mIP`, `rec-magnitude` |
| `run-` | Repeats | `run-01` |
| `echo-` | Multi-echo GRE | `echo-1` through `echo-8` |
| `part-` | Complex-data component | `part-mag`, `part-phase`, `part-real`, `part-imag` |

`echo-` and `part-` are the entities that matter for QSM. The combined `swi` contrast image has no `echo-` (it has already been combined).

## Required JSON sidecar fields

| Field | Type | Example | Why |
| --- | --- | --- | --- |
| `EchoTime` | number (s) | `0.020` | One TE per echo file; QSM dipole inversion needs the exact value |
| `RepetitionTime` | number (s) | `0.030` | Standard |
| `FlipAngle` | number (deg) | `15` | Standard for spoiled GRE |

For phase images (`part-phase`):

| Field | Type | Example | Why |
| --- | --- | --- | --- |
| `Units` | string | `"rad"` or `"arbitrary"` | Phase scaling — radians, degrees, or vendor-arbitrary units (typically `[-4096, 4095]`) |

## Recommended fields

| Field | Type | Why |
| --- | --- | --- |
| `Manufacturer` `MagneticFieldStrength` `ReceiveCoilName` | Multi-site harmonisation |
| `PulseSequenceType` `ScanningSequence` | `"GR"` for gradient echo |
| `MTState` | If magnetisation transfer applied |
| `B0FieldIdentifier` / `B0FieldSource` | Link to fieldmap for distortion correction (rare for SWI) |
| `EffectiveEchoSpacing` | For QSM laplacian-unwrapping pipelines |
| `ParallelReductionFactorInPlane` | GRAPPA factor |
| `AcquisitionVoxelSize` | mm — QSM noise depends on it |

## Magnitude / phase pairs — the QSM source

QSM dipole inversion needs *both* magnitude and phase at every echo, in image (voxel) space, with correct sign conventions:

| Pair | What it is |
| --- | --- |
| `part-mag` | Magnitude image (positive real-valued) |
| `part-phase` | Phase image, range `[-π, π]` (after rescaling) or vendor-arbitrary |
| `part-real` / `part-imag` | Less common; complex-component representation |

Storage rule: **one NIfTI per echo per part**. So a 5-echo GRE produces 10 NIfTIs (5 magnitude + 5 phase). `dcm2niix` produces this layout natively — pair them up via `_echo-N` + `_part-{mag,phase}`.

## Conversion recipes

### `dcm2niix`

For Siemens 3D GRE / SWI:

```bash
dcm2niix -b y -ba y -z y -f "sub-%i_acq-multiecho_echo-%e_part-%p_GRE" \
    -o swi/ raw/dicom/gre_3d/
```

`-f` placeholders: `%e` = echo number, `%p` = phase/mag tag. `dcm2niix` writes phase as `arbitrary` units (Siemens 12-bit `[-4096, 4095]`); QSM tools rescale to radians.

For the vendor SWI contrast image:

```bash
dcm2niix -b y -ba y -z y -f "sub-%i_swi" -o swi/ raw/dicom/swi_combined/
```

### HeuDiConv snippet (multi-echo GRE for QSM)

```python
def infotodict(seqinfo):
    swi_combined = create_key(
        "sub-{subject}/[ses-{session}/]swi/sub-{subject}[_ses-{session}]_swi")
    gre_mag = create_key(
        "sub-{subject}/[ses-{session}/]swi/sub-{subject}[_ses-{session}]"
        "_acq-multiecho_echo-{item:01d}_part-mag_GRE")
    gre_phase = create_key(
        "sub-{subject}/[ses-{session}/]swi/sub-{subject}[_ses-{session}]"
        "_acq-multiecho_echo-{item:01d}_part-phase_GRE")
    info = {swi_combined: [], gre_mag: [], gre_phase: []}
    for s in seqinfo:
        pn = s.protocol_name.lower()
        if "swi" in pn and "mip" not in pn and s.dim4 == 1:
            info[swi_combined].append(s.series_id)
        elif "gre" in pn and "_p" in s.image_type:
            info[gre_phase].append(s.series_id)
        elif "gre" in pn and "_m" in s.image_type:
            info[gre_mag].append(s.series_id)
    return info
```

### Minimal `GRE.json` (echo 1, magnitude)

```json
{
  "Manufacturer": "Siemens",
  "ManufacturersModelName": "Prisma_fit",
  "MagneticFieldStrength": 3,
  "RepetitionTime": 0.030,
  "EchoTime": 0.0046,
  "FlipAngle": 15,
  "PulseSequenceType": "GR",
  "ParallelReductionFactorInPlane": 2,
  "AcquisitionVoxelSize": [0.7, 0.7, 1.0]
}
```

### Minimal `GRE.json` (echo 1, phase)

```json
{
  "Manufacturer": "Siemens",
  "MagneticFieldStrength": 3,
  "RepetitionTime": 0.030,
  "EchoTime": 0.0046,
  "FlipAngle": 15,
  "PulseSequenceType": "GR",
  "Units": "arbitrary"
}
```

## Validation checks

- **Every `echo-N` has a matching `part-mag` and `part-phase`.** QSM tools refuse to start otherwise.
- **`EchoTime` is per-file and increasing across echoes.** A common bug: all echoes carry the same TE (typically TE1) because the converter copied the first sidecar.
- **`Units` on phase files.** Without it, downstream rescaling guesses — and guesses wrong for GE vs Siemens vs Philips.
- **`swi.nii.gz` is 3D, not 4D.** The vendor-combined SWI is a single volume.

Run [`bids-validator`](https://bids-standard.github.io/bids-validator/) — see [validation.md](../validation.md).

## Common pitfalls

- **Treating the vendor SWI as the QSM input.** The `swi.nii.gz` is a *display* image (magnitude × phase mask). QSM dipole inversion needs the per-echo magnitude *and* phase files; the combined SWI is useless for it.
- **Magnitude / phase mis-pairing.** The two share the same `echo-N` entity and differ only by `part-{mag,phase}`. `dcm2niix` gets this right; manual renaming often doesn't.
- **Phase wrap-around interpreted as flat.** Phase in `[-π, π]` looks like a noise pattern to the naive eye; the wrapped structure is what QSM unwraps. Don't apply any pre-processing before storage.
- **Different `echo-` counts across `part-`.** If the converter dropped one echo's phase but kept the magnitude, you have 5 magnitude + 4 phase. The QSM pipeline fails. Re-convert.
- **`Units` field guessed wrong on GE.** GE phase is often `[-π, π]` already (set `Units: "rad"`); Siemens is `[-4096, 4095]` (set `Units: "arbitrary"`). Confirm against the [`dcm2niix` notes](https://github.com/rordenlab/dcm2niix/blob/master/PHASE.md).
- **Long-TE artefacts not flagged.** Echoes beyond ~30 ms at 3 T have low SNR in tissue; QSM weights them less. Acquire 5–8 echoes spanning ~3–35 ms.
- **Mixing 2D-SWI and 3D-GRE in the same `swi/` folder without `acq-` labels.** Use `acq-2D_swi` and `acq-3D_GRE` to keep them apart.

## Disease-specific & special use cases

- **Cerebral amyloid angiopathy (CAA) — cortical microbleed detection.** Clinical SWI is the headline; 3D GRE at thin slice (1 mm) is the research standard. The Boston 2.0 criteria use SWI / T2*-GRE microbleed counts.
- **Multiple sclerosis — paramagnetic rim lesions (PRL).** [Sati 2016](https://doi.org/10.1148/radiol.2016151670) — PRLs on SWI / 7 T phase indicate chronic active lesions; clinical interest as a prognostic biomarker. Acquire at ≤ 1 mm isotropic, 3+ echoes for QSM. See [clinical/multiple-sclerosis.md](../../clinical/multiple-sclerosis.md).
- **Iron mapping (Parkinson's, Huntington's, ageing)** — substantia nigra and basal-ganglia QSM as iron biomarkers ([Langkammer 2012](https://doi.org/10.1148/radiol.12112320)). Multi-echo GRE → QSM via SEPIA / QSMxT.
- **Traumatic brain injury — DAI microhaemorrhages.** SWI detects shear-injury microbleeds invisible on T2-FLAIR.
- **Stroke — haemorrhagic transformation.** SWI sensitivity for parenchymal haemorrhage > GRE > CT.
- **7 T research** — SWI at 7 T has 4× phase-CNR vs 3 T; smaller voxels, longer echo trains. Same BIDS layout.

## Software & resources

| Tool / resource | Purpose |
| --- | --- |
| [BIDS spec — SWI](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#susceptibility-weighted-imaging) | Authoritative reference |
| [`dcm2niix`](https://github.com/rordenlab/dcm2niix) | Conversion (with PHASE notes) |
| [SEPIA](https://sepia-documentation.readthedocs.io/) | MATLAB QSM pipeline |
| [QSMxT](https://qsmxt.github.io/QSMxT/) | BIDS-app QSM pipeline (Python) |
| [STI Suite](https://people.eecs.berkeley.edu/~chunlei.liu/software.html) | Susceptibility tensor imaging |
| [`bids-validator`](https://bids-standard.github.io/bids-validator/) | Validate |
| [OpenNeuro `ds003097`, `ds004022`](https://openneuro.org/) | Reference SWI / QSM datasets |

## References & spec links

- BIDS spec — [Susceptibility Weighted Imaging](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#susceptibility-weighted-imaging).
- Haacke EM, Mittal S, Wu Z, Neelavalli J, Cheng Y-CN. Susceptibility-weighted imaging: technical aspects and clinical applications, part 1. *AJNR.* 2009;30(1):19–30. [doi:10.3174/ajnr.A1400](https://doi.org/10.3174/ajnr.A1400)
- Sati P, Oh J, Constable RT, et al. The central vein sign and its clinical evaluation for the diagnosis of multiple sclerosis: a consensus statement from the North American Imaging in Multiple Sclerosis Cooperative. *Nat Rev Neurol.* 2016;12:714–722. [doi:10.1038/nrneurol.2016.166](https://doi.org/10.1038/nrneurol.2016.166)
- Langkammer C, Schweser F, Krebs N, et al. Quantitative susceptibility mapping (QSM) as a means to measure brain iron? A post mortem validation study. *NeuroImage.* 2012;62(3):1593–1599. [doi:10.1016/j.neuroimage.2012.05.049](https://doi.org/10.1016/j.neuroimage.2012.05.049)
- Stewart AW, Robinson SD, O'Brien K, et al. QSMxT: Robust masking and artifact reduction for quantitative susceptibility mapping. *Magn Reson Med.* 2022;87(3):1289–1300. [doi:10.1002/mrm.29048](https://doi.org/10.1002/mrm.29048)

## Where to next

- Physics: [fundamentals/sequences/swi.md](../../fundamentals/sequences/swi.md), [gre.md](../../fundamentals/sequences/gre.md).
- Related modalities: [qmri.md](./qmri.md) for the BEP-001 derived-map conventions, [dwi.md](./dwi.md) for the other complex-valued cousin.
- Clinical: [clinical/multiple-sclerosis.md](../../clinical/multiple-sclerosis.md), [clinical/stroke-and-tbi.md](../../clinical/stroke-and-tbi.md).
