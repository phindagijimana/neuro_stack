# Quantitative MRI in BIDS

> Source acquisitions go in `anat/` as *file collections*; derived parametric maps (T1map, R2*map, ...) go in `derivatives/`. Conflate the two and your pipeline silently re-quantifies a quantified map.

**Primary spec:** [BIDS — Quantitative MRI (qMRI) appendix](https://bids-specification.readthedocs.io/en/latest/appendices/qmri.html) (BEP001).

Course map: where source vs derived live → source-data file collections (MP2RAGE, VFA, MPM, MTS, MESE, MEGRE, IRT1) → B1+ / B1- transmit-receive correction (TB1*, RB1COR) → required entities and JSON per collection → derived parametric maps → conversion (hMRI, qMRLab, mrQA) → pitfalls → tools → references → where to next.

The physics of qMRI (variable flip angle, IR T1, multi-echo T2*, MT modelling, MP2RAGE) lives in [fundamentals/sequences/qmri.md](../../fundamentals/sequences/qmri.md) and [mrf.md](../../fundamentals/sequences/mrf.md). The MRF-specific analysis lives in [analysis/mrf.md](../../analysis/mrf.md). This page is the BIDS-layout reference for qMRI source data and derivative maps.

## Where things live

The qMRI BEP makes a clean split:

| Data class | Where | Example |
| --- | --- | --- |
| **Source** (the multi-flip / multi-TI / multi-TE / multi-TE+MT NIfTIs needed to compute a map) | `sub-XX/[ses-XX/]anat/` | `sub-01_acq-MP2RAGE_inv-1_MP2RAGE.nii.gz` |
| **Scanner-computed maps** (the console already quantified, you just store) | `sub-XX/[ses-XX/]anat/` | `sub-01_T1map.nii.gz` |
| **Pipeline-computed maps** (you fit the model offline) | `derivatives/<pipeline>/sub-XX/[ses-XX/]anat/` | `derivatives/hMRI/sub-01/anat/sub-01_desc-MT_R1map.nii.gz` |
| **B1+ transmit / B1- receive correction** | `sub-XX/[ses-XX/]fmap/` | `sub-01_TB1AFI.nii.gz` |

This split matters: a pipeline that scans `anat/` for `T1w` will quietly include `MP2RAGE` source files unless you filter by suffix.

## Source-data file collections

A *file collection* is a set of NIfTI files that share most entities but differ in one (flip angle, inversion time, echo time, MT state). The collection suffix names the collection; each file in it shares the same suffix and differs by one varying entity.

| Suffix | Varies on | Required JSON | What it computes |
| --- | --- | --- | --- |
| `VFA` | `flip-` | `FlipAngle`, `PulseSequenceType`, `RepetitionTimeExcitation` | T1, M0 from variable-flip-angle SPGR |
| `IRT1` | `inv-` | `InversionTime` | T1 from inversion-recovery |
| `MP2RAGE` | `inv-` | `FlipAngle`, `InversionTime`, `RepetitionTimeExcitation`, `RepetitionTimePreparation`, `NumberShots`, `MagneticFieldStrength` | T1, UNIT1 from MP2RAGE |
| `MESE` | `echo-` | `EchoTime` | T2 from multi-echo spin-echo |
| `MEGRE` | `echo-` | `EchoTime` | T2*, R2*, χ (QSM) from multi-echo gradient-echo |
| `MTR` | `mt-` | `MTState` | Magnetisation-transfer ratio |
| `MTS` | `echo-`, `flip-`, `mt-` | `FlipAngle`, `MTState`, `RepetitionTimeExcitation` | T1, MTsat from MT-saturation |
| `MPM` | `echo-`, `flip-`, `mt-` | `FlipAngle`, `MTState`, `RepetitionTimeExcitation` | T1, PD, MT, R2* — full multi-parameter map |

Optional entities across all collections: `ses-`, `task-`, `acq-`, `ce-`, `rec-`, `run-`, `dir-`, `part-`, `chunk-`.

### B1+ transmit-field calibration (in `fmap/`)

| Suffix | Method | Required JSON |
| --- | --- | --- |
| `TB1DAM` | Dual-angle method | `FlipAngle` (array of 2) |
| `TB1EPI` | EPI-based B1 mapping | `EchoTime`, `MixingTime` |
| `TB1AFI` | Actual flip-angle imaging ([Yarnykh 2007](https://doi.org/10.1002/mrm.21120)) | `RepetitionTime` (array of 2) |
| `TB1TFL` | Turbo-FLASH B1 (Siemens) | vendor-specific |
| `TB1SRGE` | Saturation-recovery GRE | per spec |
| `TB1map` | Pre-computed B1+ map (unit: percentage of nominal) | `Units` |
| `RB1COR` | Receive-coil bias correction | per spec |
| `RB1map` | Pre-computed B1- (receive) map | `Units` |

B1+ calibration is essential for *quantitative* T1 / MT mapping at 3 T and mandatory at 7 T. Pair the B1+ acquisition with the source collection it corrects via `IntendedFor` — see [fmap.md](./fmap.md).

## Filename entities — qMRI-specific

```
sub- ses- task- acq- ce- rec- dir- run- echo- flip- inv- mt- part- chunk-
```

| Entity | Used when | Example |
| --- | --- | --- |
| `flip-` | Varies flip angle (VFA, MTS, MPM) | `flip-1`, `flip-2`, ..., `flip-N` |
| `inv-` | Inversion-prepared (IRT1, MP2RAGE) | `inv-1`, `inv-2` |
| `mt-` | MT-on / MT-off (MTR, MTS, MPM) | `mt-on`, `mt-off` |
| `echo-` | Multi-echo (MESE, MEGRE, MTS, MPM) | `echo-1`, `echo-8` |
| `part-` | Complex data (MEGRE for QSM) | `part-mag`, `part-phase` |

The order is enforced. A common pattern: `sub-01_acq-MPM_echo-1_flip-1_mt-off_MPM.nii.gz`.

## Required JSON sidecar fields by collection

### MP2RAGE source

```json
{
  "MagneticFieldStrength": 3,
  "FlipAngle": [4, 5],
  "InversionTime": 0.7,
  "RepetitionTimeExcitation": 0.0059,
  "RepetitionTimePreparation": 5.0,
  "NumberShots": [150, 150],
  "EchoTime": 0.00229
}
```

Pair `inv-1` and `inv-2` files. The `UNIT1` (combined T1-weighted) image lives alongside in `anat/`.

### VFA source (one file per flip angle)

```json
{
  "MagneticFieldStrength": 3,
  "FlipAngle": 5,
  "RepetitionTimeExcitation": 0.025,
  "EchoTime": 0.00229,
  "PulseSequenceType": "Spoiled Gradient Echo"
}
```

### MPM source (per echo / flip / MT combination)

```json
{
  "MagneticFieldStrength": 3,
  "FlipAngle": 21,
  "RepetitionTimeExcitation": 0.025,
  "MTState": false,
  "EchoTime": 0.00246
}
```

A full MPM acquisition typically produces ~24 NIfTIs (3 contrasts × 8 echoes per contrast), all sharing the `MPM` suffix and differing in `echo-`, `flip-`, `mt-`.

### TB1AFI

```json
{
  "RepetitionTime": [0.020, 0.100],
  "FlipAngle": 60,
  "EchoTime": 0.00229,
  "IntendedFor": [
    "bids::sub-01/anat/sub-01_acq-MPM_echo-1_flip-1_mt-off_MPM.nii.gz",
    "bids::sub-01/anat/sub-01_acq-MPM_echo-1_flip-2_mt-off_MPM.nii.gz"
  ]
}
```

The `IntendedFor` array lists every source file the B1+ calibration corrects.

## Derived parametric maps

Pipeline-computed maps live under `derivatives/<pipeline>/`. Standard suffixes ([Karakuzu et al. 2022](https://doi.org/10.1038/s41597-022-01571-4)):

| Suffix | What it is | Units | Computed from |
| --- | --- | --- | --- |
| `T1map` | Longitudinal relaxation time | s | IRT1, VFA, MP2RAGE |
| `T2map` | Transverse relaxation time | s | MESE |
| `T2starmap` | Apparent T2 | s | MEGRE |
| `R1map` | 1/T1 | 1/s | Same as `T1map` (relaxation-rate convention) |
| `R2map` | 1/T2 | 1/s | MESE |
| `R2starmap` | 1/T2* | 1/s | MEGRE |
| `M0map` | Equilibrium magnetisation | a.u. | VFA |
| `S0map` | Signal at TE=0 | a.u. | MEGRE |
| `MTRmap` | MT ratio | percent | MTR |
| `MTsat` | MT saturation | a.u. | MTS, MPM |
| `MWFmap` | Myelin water fraction | percent | mcDESPOT, MESE |
| `MTVmap` | Macromolecular tissue volume | percent | VFA + B1 |
| `PDmap` | Proton density | a.u. | VFA, MPM |
| `Chimap` | Magnetic susceptibility | ppm | QSM from MEGRE phase |

Each derived map needs the standard derivative sidecar (`Sources`, `SoftwareName`, `SoftwareVersion`) — see [derivatives.md](../derivatives.md).

```text
derivatives/
└── hMRI/
    ├── dataset_description.json
    └── sub-01/
        └── anat/
            ├── sub-01_desc-MPM_T1map.nii.gz
            ├── sub-01_desc-MPM_T1map.json
            ├── sub-01_desc-MPM_R2starmap.nii.gz
            ├── sub-01_desc-MPM_MTsat.nii.gz
            └── sub-01_desc-MPM_PDmap.nii.gz
```

## Conversion recipes

### `dcm2niix` for MP2RAGE

```bash
dcm2niix -b y -ba y -z y -f "sub-%i_acq-MP2RAGE_inv-%t_MP2RAGE" \
    -o anat/ raw/dicom/mp2rage/
```

`-f` placeholder `%t` for inversion-time index works on recent Siemens. Verify on first subject; some sites need a custom rename.

### `dcm2niix` for MEGRE / MPM

```bash
dcm2niix -b y -ba y -z y \
    -f "sub-%i_acq-MPM_echo-%e_flip-%f_part-%p_MPM" \
    -o anat/ raw/dicom/mpm/
```

`%e` = echo index, `%f` = flip index, `%p` = phase/mag. MT-on vs MT-off is typically two separate DICOM series — wrap with HeuDiConv to inject the `mt-` entity.

### Pipeline-side conversion

The actual fitting tools:

- [hMRI toolbox](https://hmri-group.github.io/hMRI-toolbox/) ([Tabelow 2019](https://doi.org/10.1016/j.neuroimage.2019.01.029)) — MATLAB / SPM, MPM-focused.
- [qMRLab](https://qmrlab.org/) ([Karakuzu 2020](https://doi.org/10.21105/joss.02343)) — MATLAB / Octave; broad model library.
- [`pymp2rage`](https://github.com/Donders-Institute/pymp2rage) — MP2RAGE T1 maps in Python.
- [mrQA](https://github.com/Open-Minds-Lab/mrQA) — qMRI-protocol QA at scale.

All consume BIDS-compliant source data and write derivative maps in the derivative layout.

## Validation checks

- **Every `flip-`/`inv-`/`mt-`/`echo-` index exists end-to-end.** A 4-flip VFA collection must have `flip-1`, `flip-2`, `flip-3`, `flip-4` — no gaps.
- **`FlipAngle` and `InversionTime` in JSON match the entity value across files.** A file named `_inv-1_MP2RAGE.nii.gz` with `InversionTime: 2.5` and another `_inv-2_MP2RAGE.nii.gz` with `InversionTime: 0.7` is suspicious — usually a converter bug.
- **`IntendedFor` on B1 maps points to existing source files.**
- **Source vs derived not mixed.** `T1map.nii.gz` directly in `anat/` is allowed *only* if the scanner exported it; if you computed it offline, it belongs in `derivatives/`.
- **MP2RAGE has `inv-1`, `inv-2`, AND `UNIT1`.** Some pipelines (`pymp2rage`) want all three.

Run [`bids-validator`](https://bids-standard.github.io/bids-validator/) with a pin on a version that supports BEP001 (≥ v1.13).

## Common pitfalls

- **Storing computed maps in `anat/`.** Easy to do, breaks downstream. Computed maps go to `derivatives/`. Only console-quantified maps belong in raw `anat/`.
- **Missing B1+ calibration.** At 7 T this makes T1 maps unreliable; at 3 T it inflates inter-site variance. Acquire `TB1AFI` or `TB1TFL` and link with `IntendedFor`.
- **MP2RAGE `INV1` and `INV2` mislabelled.** Some Siemens products export `INV1` first, others `INV2` first. Inspect — TI for `inv-1` should be the *short* TI (~0.7 s), `inv-2` the long TI (~2.5 s).
- **MTS / MPM file-collection cardinality.** A typical MPM is 3 contrasts (PDw, T1w, MTw) × ~8 echoes = 24 files. A collection with 23 files is almost always a converter bug.
- **`run-` collisions.** Different MPM contrasts share the same `acq-MPM` but differ in `flip-` and `mt-`. Don't mistakenly bump `run-` to disambiguate — that hides the structure.
- **B1+ map units.** `TB1map.nii.gz` is the percentage of nominal flip angle (`100` = nominal). Some vendors export in `[0, 1]` instead. Always set `Units`.
- **Pipeline version not pinned.** Two hMRI versions can produce subtly different MPM T1 maps from the same source. Pin in `GeneratedBy` — see [derivatives.md](../derivatives.md).

## Disease-specific & special use cases

- **Multiple sclerosis — myelin imaging.** MPM-derived MTsat is a leading non-conventional myelin biomarker. Acquire 1 mm isotropic, full MPM with B1+ calibration. See [clinical/multiple-sclerosis.md](../../clinical/multiple-sclerosis.md).
- **Iron mapping (Parkinson's, ageing).** R2* + χ (QSM) from MEGRE — see [swi.md](./swi.md) for the underlying acquisition.
- **Cortical mapping (7 T).** MP2RAGE T1 maps drive cortical-laminar segmentation ([Trampel 2019](https://doi.org/10.1016/j.neuroimage.2017.09.037)). Pair with B1+ calibration.
- **MR fingerprinting.** Source data is a long dictionary-matched series; the derived T1 / T2 / PD maps land in `derivatives/`. See [fundamentals/sequences/mrf.md](../../fundamentals/sequences/mrf.md) and [analysis/mrf.md](../../analysis/mrf.md).
- **Paediatric ageing.** Multi-site qMRI requires harmonisation (ComBat); the BIDS layout is identical, but the pipeline must report `SoftwareVersion` and `MagneticFieldStrength` per session.
- **Brain tumour pre-/post-op.** T1map + ADC + CBF as quantitative tumour biomarkers; T1map sits here, ADC in `derivatives/`, CBF in `perf/`-derived.

## Software & resources

| Tool / resource | Purpose |
| --- | --- |
| [BIDS spec — qMRI appendix](https://bids-specification.readthedocs.io/en/latest/appendices/qmri.html) | Authoritative reference |
| [BIDS spec — file collections](https://bids-specification.readthedocs.io/en/latest/appendices/file-collections.html) | The general file-collection grammar |
| [hMRI toolbox](https://hmri-group.github.io/hMRI-toolbox/) | MPM / VFA / MTsat fitting |
| [qMRLab](https://qmrlab.org/) | Broad qMRI model library |
| [`pymp2rage`](https://github.com/Donders-Institute/pymp2rage) | MP2RAGE T1 maps in Python |
| [mrQA](https://github.com/Open-Minds-Lab/mrQA) | qMRI protocol QA |
| [SEPIA](https://sepia-documentation.readthedocs.io/) | QSM pipeline |
| [`bids-validator`](https://bids-standard.github.io/bids-validator/) | Validate (≥ v1.13 for BEP001) |
| [OpenNeuro `ds002868`, `ds003392`](https://openneuro.org/) | Reference MP2RAGE / MPM datasets |

## References & spec links

- BIDS qMRI appendix — [qmri.html](https://bids-specification.readthedocs.io/en/latest/appendices/qmri.html).
- Karakuzu A, Appelhoff S, Auer T, et al. qMRI-BIDS: an extension to the brain imaging data structure for quantitative magnetic resonance imaging data. *Sci Data.* 2022;9:517. [doi:10.1038/s41597-022-01571-4](https://doi.org/10.1038/s41597-022-01571-4)
- Tabelow K, Balteau E, Ashburner J, et al. hMRI — A toolbox for quantitative MRI in neuroscience and clinical research. *NeuroImage.* 2019;194:191–210. [doi:10.1016/j.neuroimage.2019.01.029](https://doi.org/10.1016/j.neuroimage.2019.01.029)
- Weiskopf N, Suckling J, Williams G, et al. Quantitative multi-parameter mapping of R1, PD*, MT and R2* at 3 T: a multi-center validation. *Front Neurosci.* 2013;7:95. [doi:10.3389/fnins.2013.00095](https://doi.org/10.3389/fnins.2013.00095)
- Marques JP, Kober T, Krueger G, et al. MP2RAGE, a self bias-field corrected sequence for improved segmentation and T1-mapping at high field. *NeuroImage.* 2010;49(2):1271–1281. [doi:10.1016/j.neuroimage.2009.10.002](https://doi.org/10.1016/j.neuroimage.2009.10.002)
- Yarnykh VL. Actual flip-angle imaging in the pulsed steady state: a method for rapid three-dimensional mapping of the transmitted radiofrequency field. *Magn Reson Med.* 2007;57(1):192–200. [doi:10.1002/mrm.21120](https://doi.org/10.1002/mrm.21120)

## Where to next

- Physics: [fundamentals/sequences/qmri.md](../../fundamentals/sequences/qmri.md), [mrf.md](../../fundamentals/sequences/mrf.md).
- Analysis: [analysis/mrf.md](../../analysis/mrf.md), [analysis/structural.md](../../analysis/structural.md).
- Related modalities: [anat.md](./anat.md) (where source files live), [swi.md](./swi.md) (the MEGRE-for-QSM cousin), [fmap.md](./fmap.md) (where B1 calibration lives).
- Derivatives layout: [derivatives.md](../derivatives.md).
