# Diffusion MRI in BIDS

> The 4D NIfTI is the easy part. The `.bvec` / `.bval` orientation is what bites you.

**Primary spec:** [BIDS — Magnetic Resonance Imaging Data → Diffusion imaging data](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#diffusion-imaging-data).

Course map: folder layout → suffixes → companion files → entities → required + recommended sidecar → conversion → b-table validation → pitfalls → multi-shell / HARDI / QSM → tools → references → where to next.

The physics, q-space sampling, and tractography theory live in [fundamentals/sequences/dwi.md](../../fundamentals/sequences/dwi.md) and [advanced-diffusion.md](../../fundamentals/sequences/advanced-diffusion.md). Preprocessing and tractography pipelines live in [analysis/diffusion.md](../../analysis/diffusion.md). This page is about getting the files into BIDS.

## Folder layout (one-glance)

```text
sub-01/
└── ses-01/
    └── dwi/
        ├── sub-01_ses-01_dir-AP_dwi.nii.gz
        ├── sub-01_ses-01_dir-AP_dwi.bval
        ├── sub-01_ses-01_dir-AP_dwi.bvec
        ├── sub-01_ses-01_dir-AP_dwi.json
        ├── sub-01_ses-01_dir-AP_sbref.nii.gz
        ├── sub-01_ses-01_dir-AP_sbref.json
        ├── sub-01_ses-01_dir-PA_dwi.nii.gz       # short reversed-PE for topup
        ├── sub-01_ses-01_dir-PA_dwi.bval
        ├── sub-01_ses-01_dir-PA_dwi.bvec
        └── sub-01_ses-01_dir-PA_dwi.json
```

For a single-shell DTI with no reversed-PE, drop the `dir-PA` files; for multi-shell HARDI, the 4D NIfTI holds all shells and the `.bval` enumerates them.

## Allowed suffixes

| Suffix | What it is | When to use |
| --- | --- | --- |
| `dwi` | The 4D diffusion-weighted series (b=0 volumes interleaved) | Every DWI acquisition |
| `sbref` | Single-band reference image | Multi-band DWI protocols |
| `bval` | Text file of b-values, one per volume | Mandatory companion to every `_dwi.nii.gz` |
| `bvec` | Text file of unit gradient directions, one column per volume | Mandatory companion to every `_dwi.nii.gz` |

`bval` and `bvec` are not images — they are sidecars in the spec sense but on disk as plain text. The validator treats them as required companions.

## Companion files — the b-table

Two text files, both required:

```text
# sub-01_ses-01_dir-AP_dwi.bval  (1 row, N columns)
0 0 1000 1000 1000 ... 2000 2000 ... 3000 3000

# sub-01_ses-01_dir-AP_dwi.bvec  (3 rows, N columns)
0.0  0.0  0.234 -0.187  0.561  ...
0.0  0.0  0.501  0.812 -0.323  ...
0.0  0.0  0.832  0.553  0.762  ...
```

Hard constraints:

- **Both files must have exactly N columns** where N is the 4th dimension of the NIfTI.
- **`bval` is one row, space- or tab-separated**, in s/mm².
- **`bvec` is three rows** (x, y, z), each unit-norm (or zero for b=0 volumes).
- **Coordinate frame is image (voxel) space.** Not scanner, not world. `dcm2niix` does this correctly; rolling your own conversion is the most common source of bugs.

After eddy / motion correction, the gradient table must be *rotated* to match — see [Pitfalls](#common-pitfalls).

## Filename entities — in order

```
sub- ses- acq- ce- rec- dir- run- echo- part- chunk- split-
```

| Entity | Used when | Example |
| --- | --- | --- |
| `acq-` | Distinguish protocols (single-shell vs multi-shell) | `acq-MS`, `acq-singleshell` |
| `ce-` | Contrast-enhanced DWI (uncommon) | `ce-gad` |
| `rec-` | Different reconstructions | `rec-online`, `rec-offline` |
| `dir-` | Phase-encoding direction label | `dir-AP`, `dir-PA`, `dir-LR` |
| `run-` | Repeats | `run-01`, `run-02` |
| `part-` | Complex data for QSM-from-DWI | `part-mag`, `part-phase` |

`dir-` is critical for topup: the AP and PA acquisitions both go in `dwi/` and are paired via matching `acq-`/`run-` (or via the new `B0FieldIdentifier`). See [fmap.md](./fmap.md) for the PEPOLAR alternative when the reversed-PE is acquired as a fieldmap rather than a full DWI.

## Required JSON sidecar fields

| Field | Type | Example | Why it matters |
| --- | --- | --- | --- |
| `EchoTime` | number (s) | `0.087` | Required if fieldmap-based distortion correction is present |
| `RepetitionTime` | number (s) | `5.3` | Standard |
| `FlipAngle` | number (deg) | `90` | Standard |

Required *for distortion / eddy correction*:

| Field | Type | Example | Why |
| --- | --- | --- | --- |
| `PhaseEncodingDirection` | string | `"j-"` | `topup` and `eddy` need it; QSIPrep refuses to run without |
| `TotalReadoutTime` | number (s) | `0.0568` | `eddy` math depends on this |

## Recommended fields

| Field | Why |
| --- | --- |
| `EffectiveEchoSpacing` | Alternative to `TotalReadoutTime` |
| `SliceTiming` | Slice-timing correction for DTI is rare but possible |
| `MultibandAccelerationFactor` | Documentation |
| `ParallelReductionFactorInPlane` | GRAPPA factor |
| `DiffusionScheme` | `"PGSE"`, `"STEAM"`, `"OGSE"` — biophysical models need it |
| `DiffusionTime` | The Δ in Stejskal–Tanner — required for NODDI / SMT / restricted models |
| `B0FieldIdentifier` / `B0FieldSource` | Modern way to link this DWI to its fieldmap |
| `MagneticFieldStrength` `Manufacturer` `ReceiveCoilName` | Multi-site harmonisation |

## Conversion recipes

### `dcm2niix`

`dcm2niix` writes `.nii.gz`, `.bval`, `.bvec`, and `.json` together; bvecs are in the correct (image-space) frame for Siemens, GE, and Philips out of the box.

```bash
dcm2niix -b y -ba y -z y -f "sub-%i_dir-%p_dwi" -o dwi/ raw/dicom/dwi/
```

### HeuDiConv heuristic snippet

```python
def infotodict(seqinfo):
    dwi_ap = create_key("sub-{subject}/[ses-{session}/]dwi/"
                        "sub-{subject}[_ses-{session}]_dir-AP_run-{item:02d}_dwi")
    dwi_pa = create_key("sub-{subject}/[ses-{session}/]dwi/"
                        "sub-{subject}[_ses-{session}]_dir-PA_run-{item:02d}_dwi")
    info = {dwi_ap: [], dwi_pa: []}
    for s in seqinfo:
        pn = s.protocol_name.lower()
        if "diff" in pn or "dti" in pn or "dwi" in pn:
            if "_pa" in pn or "rev" in pn:
                info[dwi_pa].append(s.series_id)
            else:
                info[dwi_ap].append(s.series_id)
    return info
```

### Minimal `dwi.json`

```json
{
  "Manufacturer": "Siemens",
  "ManufacturersModelName": "Prisma_fit",
  "MagneticFieldStrength": 3,
  "RepetitionTime": 5.3,
  "EchoTime": 0.087,
  "FlipAngle": 90,
  "PhaseEncodingDirection": "j-",
  "TotalReadoutTime": 0.0568,
  "EffectiveEchoSpacing": 0.000545,
  "MultibandAccelerationFactor": 4,
  "DiffusionScheme": "PGSE",
  "B0FieldIdentifier": "pepolar1",
  "ReceiveCoilName": "HeadNeck_64"
}
```

## Validation checks

The validator (see [validation.md](../validation.md)) enforces the structural rules; you must enforce the *semantic* ones:

```python
import numpy as np, nibabel as nib, pathlib
for nii in pathlib.Path("bids").rglob("*_dwi.nii.gz"):
    n_vols = nib.load(nii).shape[3]
    bval = np.loadtxt(nii.with_suffix("").with_suffix(".bval"))
    bvec = np.loadtxt(nii.with_suffix("").with_suffix(".bvec"))
    assert bval.size == n_vols, f"{nii}: bval has {bval.size}, NIfTI 4th dim {n_vols}"
    assert bvec.shape == (3, n_vols), f"{nii}: bvec shape {bvec.shape}, expected (3, {n_vols})"
    nz = bval > 50
    norms = np.linalg.norm(bvec[:, nz], axis=0)
    assert np.allclose(norms, 1.0, atol=1e-2), f"{nii}: bvec not unit-norm"
```

If any assertion fires, the conversion is broken — do not run topup / eddy on it.

## Common pitfalls

- **bvec rotation after eddy.** `eddy` rewrites bvecs to account for inter-volume rotation. If you copy the original `.bvec` into the eddy-corrected derivative folder, every tensor fit is misoriented. Use the `eddy_rotated_bvecs` file that `eddy` produces.
- **bval / bvec column count ≠ NIfTI 4th dim.** Most often when a scout / calibration volume gets concatenated into the series. Re-run conversion; do not edit the b-table by hand.
- **Wrong PE direction.** `j-` vs `j` flips topup's correction; the resulting EPI is *more* distorted. Cross-check against the scanner protocol on the first subject of every site.
- **Missing reversed-PE b0.** Without a reversed-PE acquisition (either as `dir-PA_dwi` or as `fmap/epi`), you cannot run topup. Schedule it at acquisition time; you cannot reconstruct it.
- **Vendor b-vector frame confusion.** Most converters now do the right thing, but historical Philips bvecs were in scanner frame. Test with a phantom or trust a recent `dcm2niix` (≥ v1.0.20220720). If FA images look like they are oriented along the slice axis, the b-vectors are wrong.
- **Trace / ADC volumes treated as raw DWI.** Some scanners auto-export a `TRACE_DWI` and an `ADC` map. Those are derived; route them to `derivatives/` with `desc-trace_dwi` / `desc-ADC_dwi`, not into the raw `dwi/` folder.
- **`b=5` reported as b=0.** Some Connectom protocols use a tiny minimum b for crusher reasons. The convention is to treat anything `b < 50` as a b=0 for QC purposes — but keep the original number in the `.bval`.

## Disease-specific & special use cases

- **Clinical stroke DWI** — three orthogonal gradients + b=0, trace-weighted, ADC. The scanner already produces `TRACE_DWI` and `ADC`. For research, route the raw DWI to `dwi/` and the trace / ADC to `derivatives/`. See [clinical/stroke-and-tbi.md](../../clinical/stroke-and-tbi.md).
- **Single-shell DTI** — typically `b=0` + `b=1000` × 30 directions. Set `acq-DTI` to distinguish from multi-shell protocols if you keep both.
- **HARDI / CSD-ready** — `b=0` + `b=2000` or `b=3000` with 60–90 directions on one shell. Set `acq-HARDI`.
- **Multi-shell (NODDI, MSMT-CSD, DKI)** — `b=0` + multiple non-zero shells. Encode shells in the single `.bval` row; pipelines split by b-value on read. `acq-MS` is a convention.
- **Connectome-grade (HCP / MGH-Connectom)** — `b=0` + `b=1000` + `b=2000` + `b=3000` × ≥90 directions per shell, reversed-PE pair. Often split across two PE-direction runs (`dir-AP_dwi`, `dir-PA_dwi`) that each carry the full b-table.
- **Multi-band DWI** — same DWI layout; just populate `MultibandAccelerationFactor`. Pair with the appropriate `sbref`.
- **Complex / QSM-from-DWI** — pair `part-mag` and `part-phase` files.
- **Pediatric / sleep DWI** — same layout; only difference is shorter protocols (`acq-clinical`).

## Software & resources

| Tool / resource | Purpose |
| --- | --- |
| [BIDS spec — dwi](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#diffusion-imaging-data) | Authoritative reference |
| [`dcm2niix`](https://github.com/rordenlab/dcm2niix) | Writes NIfTI + bval + bvec + JSON in one shot |
| [HeuDiConv](https://heudiconv.readthedocs.io/) | Heuristic routing |
| [`bids-validator`](https://bids-standard.github.io/bids-validator/) | Validate |
| [QSIPrep](https://qsiprep.readthedocs.io/) | The canonical BIDS-app preprocessing pipeline for DWI |
| [MRtrix3](https://mrtrix.readthedocs.io/) | CSD, ACT, SIFT2 — reads BIDS-ish input |
| [FSL `topup` / `eddy`](https://fsl.fmrib.ox.ac.uk/fsl/fslwiki/eddy) | Distortion + motion + eddy-current correction |
| [DIPY](https://docs.dipy.org/) | DTI / DKI / NODDI / CSD in Python |
| [OpenNeuro `ds000114`, `ds001226`, `ds003397`](https://openneuro.org/) | Reference DWI datasets |

## References & spec links

- BIDS spec — [Diffusion imaging data](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#diffusion-imaging-data).
- Cieslak M, Cook PA, He X, et al. QSIPrep: an integrative platform for preprocessing and reconstructing diffusion MRI data. *Nat Methods.* 2021;18:775–778. [doi:10.1038/s41592-021-01185-5](https://doi.org/10.1038/s41592-021-01185-5)
- Andersson JLR, Sotiropoulos SN. An integrated approach to correction for off-resonance effects and subject movement in diffusion MR imaging. *NeuroImage.* 2016;125:1063–1078. [doi:10.1016/j.neuroimage.2015.10.019](https://doi.org/10.1016/j.neuroimage.2015.10.019)
- Caruyer E, Lenglet C, Sapiro G, Deriche R. Design of multishell sampling schemes with uniform coverage in diffusion MRI. *Magn Reson Med.* 2013;69(6):1534–1540. [doi:10.1002/mrm.24736](https://doi.org/10.1002/mrm.24736)
- Tournier J-D, Smith RE, Raffelt D, et al. MRtrix3: A fast, flexible and open software framework for medical image processing and visualisation. *NeuroImage.* 2019;202:116137. [doi:10.1016/j.neuroimage.2019.116137](https://doi.org/10.1016/j.neuroimage.2019.116137)

## Where to next

- Physics: [fundamentals/sequences/dwi.md](../../fundamentals/sequences/dwi.md), [advanced-diffusion.md](../../fundamentals/sequences/advanced-diffusion.md).
- Analysis: [analysis/diffusion.md](../../analysis/diffusion.md), [analysis/wm-stats.md](../../analysis/wm-stats.md), [analysis/network-metrics.md](../../analysis/network-metrics.md).
- Related modalities: [fmap.md](./fmap.md) for the reversed-PE pair, [swi.md](./swi.md) for the complex-valued cousin.
