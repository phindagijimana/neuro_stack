# Anatomical MRI in BIDS

> The reference for every other modality. Get `anat/` right or every coregistration downstream is wrong.

**Primary spec:** [BIDS — Magnetic Resonance Imaging Data → Anatomy imaging data](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#anatomy-imaging-data).

Course map: folder layout → allowed suffixes → entity order → required + recommended sidecar fields → conversion recipes → validation → pitfalls → special cases (qMRI variants, defacing) → tools → references → where to next.

For the physics behind T1w / FLAIR / qMRI, see [fundamentals/sequences/mprage.md](../../fundamentals/sequences/mprage.md), [flair.md](../../fundamentals/sequences/flair.md), and [qmri.md](../../fundamentals/sequences/qmri.md). This page is purely about getting the files into BIDS shape.

## Folder layout (one-glance)

```text
sub-01/
└── ses-01/
    └── anat/
        ├── sub-01_ses-01_T1w.nii.gz
        ├── sub-01_ses-01_T1w.json
        ├── sub-01_ses-01_T2w.nii.gz
        ├── sub-01_ses-01_T2w.json
        ├── sub-01_ses-01_FLAIR.nii.gz
        ├── sub-01_ses-01_FLAIR.json
        ├── sub-01_ses-01_acq-highres_run-01_T1w.nii.gz
        ├── sub-01_ses-01_acq-highres_run-01_T1w.json
        ├── sub-01_ses-01_acq-MP2RAGE_inv-1_MP2RAGE.nii.gz
        ├── sub-01_ses-01_acq-MP2RAGE_inv-2_MP2RAGE.nii.gz
        └── sub-01_ses-01_acq-MP2RAGE_UNIT1.nii.gz
```

Sessions are optional. If the study is single-visit, drop `ses-01/` and the corresponding entity in the filename.

## Allowed suffixes

The spec splits anat suffixes into *non-parametric* (weighted images) and *parametric* (already-quantitative maps that nonetheless live in `anat/` when produced at the console).

| Suffix | What it is | When to use |
| --- | --- | --- |
| `T1w` | T1-weighted | MPRAGE, MP-RAGE, SPGR, BRAVO — anything that gives a high-resolution T1 contrast |
| `T2w` | T2-weighted | TSE / FSE / SPACE / CUBE T2 |
| `FLAIR` | T2 with CSF nulled | 2D-FLAIR or 3D-FLAIR — see [flair.md](../../fundamentals/sequences/flair.md) |
| `FLASH` | Fast low-angle shot (spoiled GRE) | qMRI source for PD/T1 |
| `PDw` | Proton-density weighted | Dual-echo TSE first echo, or short-TE long-TR sequences |
| `inplaneT1` / `inplaneT2` | Low-res reference in the EPI plane | Older protocols that pair an in-plane T1 with BOLD for coreg |
| `angio` | TOF or PC angiography | MR-angio acquisitions |
| `T1map` `T2map` `T2starmap` | Quantitative relaxation-time maps | When the scanner exports the map directly (see [qmri.md](./qmri.md) for derivative-side maps) |
| `PDmap` `PDT2` | Quantitative PD, dual-echo PD/T2 | Console-exported quantitative PD |
| `T1rho` | T1ρ map | Spin-lock relaxation studies |
| `MTR` `MTsat` `MTS` | Magnetisation-transfer ratio / saturation | Pair with `mt-on` / `mt-off` entities |
| `MWF` | Myelin water fraction map | Multi-echo T2 / mcDESPOT output |
| `UNIT1` | MP2RAGE unified T1-weighted image | The bias-corrected combination of `inv-1` and `inv-2` |
| `MP2RAGE` | MP2RAGE source image | Use with `_inv-1` / `_inv-2` entities |
| `MTon` / `MToff` | MT-on / MT-off pair | Source for MTR computation |

When a suffix is *both* anatomical (lives in `anat/`) and quantitative (a map), it can show up either at the console (in `anat/`) or as a derivative (in `derivatives/<pipeline>/sub-XX/anat/`). The qMRI BEP rules ([qmri.md](./qmri.md)) tell you which.

## Filename entities — in order

The full ordered entity list for `anat/` is:

```
sub- ses- acq- ce- rec- run- echo- flip- inv- mt- part- chunk-
```

| Entity | Used when | Example |
| --- | --- | --- |
| `acq-` | Distinguish protocols sharing a suffix | `acq-mprage` vs `acq-spgr` |
| `ce-` | Contrast agent administered | `ce-gad` post-gadolinium T1w |
| `rec-` | Different reconstruction of the same raw data | `rec-norm` vs `rec-unnormalized` |
| `run-` | Repeated acquisitions, identical protocol | `run-01`, `run-02` |
| `echo-` | Multi-echo qMRI source | `echo-1` through `echo-8` for MEGRE |
| `flip-` | Variable-flip-angle qMRI (VFA, MPM) | `flip-1`, `flip-2` |
| `inv-` | Inversion-recovery / MP2RAGE | `inv-1`, `inv-2` |
| `mt-` | MT-on / MT-off pairs | `mt-on`, `mt-off` |
| `part-` | Complex-valued data | `part-mag`, `part-phase`, `part-real`, `part-imag` |
| `chunk-` | Multiple chunks of the same physical sample | High-res ex-vivo, microscopy-adjacent |

The order is enforced by the validator. `sub-01_run-01_acq-highres_T1w.nii.gz` will fail; the right name is `sub-01_acq-highres_run-01_T1w.nii.gz`.

## Required JSON sidecar fields

For plain anatomical scans (`T1w`, `T2w`, `FLAIR`, `PDw`, `FLASH`, `angio`, `inplaneT1`/`T2`), the spec lists **no strictly REQUIRED** fields — the file is interpretable from its suffix. In practice, downstream tools fail without the basics:

| Field | Type | Example | Why it matters |
| --- | --- | --- | --- |
| `MagneticFieldStrength` | number (T) | `3` | Most pipelines branch on this (1.5 T vs 3 T vs 7 T) |
| `Manufacturer` | string | `"Siemens"` | Vendor-specific bias-field correction |
| `ManufacturersModelName` | string | `"Prisma_fit"` | Scanner-specific QC |
| `RepetitionTime` | number (s) | `2.4` | Required for any parametric `*map` suffix |
| `EchoTime` | number (s) | `0.00229` | Required for multi-echo |
| `FlipAngle` | number (deg) | `8` | Required for VFA / MPM / MP2RAGE |
| `InversionTime` | number (s) | `1.1` | Required when `inv-` entity is present |

Quantitative parametric suffixes (`T1map`, `T2map`, etc.) and qMRI source collections (`MP2RAGE`, `MTS`, `MPM`) have their own hard requirements — see [qmri.md](./qmri.md).

## Recommended fields

| Field | Why |
| --- | --- |
| `ScanningSequence` `SequenceVariant` `SequenceName` `PulseSequenceType` | Vendor-agnostic sequence ID |
| `ReceiveCoilName` `ReceiveCoilActiveElements` | Coil-dependent SNR / bias |
| `SoftwareVersions` | Vendor pipeline bugs are version-specific |
| `InstitutionName` `StationName` | Multi-site harmonisation |
| `BodyPart` `BodyPartDetails` | Helps non-neuro pipelines skip whole-body scans |
| `AnatomicalLandmarkCoordinates` | Multimodal coreg with MEG / sEEG / TMS |
| `DeidentificationMethod` `DeidentificationMethodCodeSequence` | Audit trail for defacing / skull-strip |

## Conversion recipes

### `dcm2niix` direct call

```bash
dcm2niix -b y -ba y -z y -f "sub-%i_%d" -o anat/ raw/dicom/
```

`-b y` writes BIDS sidecars; `-ba y` anonymises; `-z y` gzip-compresses. `dcm2niix` does not BIDS-route on its own — wrap it with a heuristic.

### HeuDiConv heuristic snippet

```python
def infotodict(seqinfo):
    t1   = create_key("sub-{subject}/[ses-{session}/]anat/sub-{subject}[_ses-{session}]_T1w")
    t2   = create_key("sub-{subject}/[ses-{session}/]anat/sub-{subject}[_ses-{session}]_T2w")
    fl   = create_key("sub-{subject}/[ses-{session}/]anat/sub-{subject}[_ses-{session}]_FLAIR")
    mp2_inv1 = create_key("sub-{subject}/[ses-{session}/]anat/"
                          "sub-{subject}[_ses-{session}]_acq-MP2RAGE_inv-1_MP2RAGE")
    mp2_inv2 = create_key("sub-{subject}/[ses-{session}/]anat/"
                          "sub-{subject}[_ses-{session}]_acq-MP2RAGE_inv-2_MP2RAGE")
    info = {t1: [], t2: [], fl: [], mp2_inv1: [], mp2_inv2: []}
    for s in seqinfo:
        pn = s.protocol_name.upper()
        if "MPRAGE" in pn and "MP2" not in pn:
            info[t1].append(s.series_id)
        elif "T2_SPACE" in pn or "CUBE_T2" in pn:
            info[t2].append(s.series_id)
        elif "FLAIR" in pn:
            info[fl].append(s.series_id)
        elif "MP2RAGE" in pn and "_INV1" in pn:
            info[mp2_inv1].append(s.series_id)
        elif "MP2RAGE" in pn and "_INV2" in pn:
            info[mp2_inv2].append(s.series_id)
    return info
```

### Minimal `T1w.json`

```json
{
  "Manufacturer": "Siemens",
  "ManufacturersModelName": "Prisma_fit",
  "MagneticFieldStrength": 3,
  "RepetitionTime": 2.4,
  "EchoTime": 0.00229,
  "InversionTime": 1.06,
  "FlipAngle": 8,
  "ReceiveCoilName": "HeadNeck_64",
  "InstitutionName": "URMC",
  "SoftwareVersions": "syngo MR XA30"
}
```

## Validation checks

Run [`bids-validator`](https://bids-standard.github.io/bids-validator/) — see [validation.md](../validation.md). Anat-specific things to look for:

- `inplaneT1` vs `T1w` — `inplaneT1` is the *low-res EPI-plane* reference used by older fMRI protocols; do not promote it to `T1w` even if it's the only T1 you have.
- `acq-highres` vs `acq-lowres` — the validator does not police labels, but downstream tools (fMRIPrep) sometimes branch on them. Pick a convention and document it.
- Defacing — defaced T1w must still validate. If the validator complains about orientation after defacing, the defacing tool ([`pydeface`](https://github.com/poldracklab/pydeface), [`mri_deface`](https://surfer.nmr.mgh.harvard.edu/fswiki/mri_deface)) is rewriting headers — re-export with `--force-pixdims`.
- Single subject with two T1w in the same session — must carry `run-01` / `run-02`; the validator throws `DUPLICATE_SCAN` otherwise.

## Common pitfalls

- **Calling everything `T1w`.** A post-Gd T1 is `ce-gad_T1w`. An inversion-recovery prep T1 is still `T1w` (the contrast is what counts), but qMRI source files belong to `MP2RAGE` / `IRT1` collections — see [qmri.md](./qmri.md).
- **Missing `run-` on repeats.** A re-shot T1 because the first was motion-corrupted needs `run-01` *and* `run-02`. Decide upfront whether you keep both or only the second.
- **Defacing breaks orbital surfaces.** Defacing removes the eyes and a chunk of frontal cortex; cortical-surface pipelines ([FreeSurfer](https://surfer.nmr.mgh.harvard.edu/)) that look for orbital landmarks will misregister. Either skull-strip + share the brain, or use a more conservative defacer ([`mri_reface`](https://www.nitrc.org/projects/mri_reface)). See [governance/privacy-and-hipaa-gdpr.md](../../governance/privacy-and-hipaa-gdpr.md).
- **MP2RAGE without `inv-` entities.** `acq-MP2RAGE_inv-1_MP2RAGE.nii.gz` + `acq-MP2RAGE_inv-2_MP2RAGE.nii.gz` are the two source inversions; `acq-MP2RAGE_UNIT1.nii.gz` is the combined T1-weighted image. Tools (e.g. [`pymp2rage`](https://github.com/Donders-Institute/pymp2rage)) need all three.
- **`acq-` label inflation.** `acq-mprage_iso_norm_PROMO_v2` is a smell. Keep labels short and stable across the study.
- **Defaced and non-defaced co-existing.** Don't keep both in the raw dataset — share defaced as the raw dataset, optionally keep originals in `sourcedata/` per [BIDS source-data rules](https://bids-specification.readthedocs.io/en/latest/common-principles.html#source-vs-raw-vs-derived-data).
- **`ce-` label semantics.** `ce-gad` means gadolinium-enhanced; the validator does not check the agent's actual identity. Document in the dataset README.

## Disease-specific & special use cases

- **Multiple sclerosis** — protocols typically include 3D-FLAIR + post-Gd 3D-T1w. Lay out as `_FLAIR` and `_ce-gad_T1w`. The lesion-mask derivatives belong under `derivatives/<pipeline>/sub-XX/anat/sub-XX_space-T1w_desc-lesion_mask.nii.gz`. See [clinical/multiple-sclerosis.md](../../clinical/multiple-sclerosis.md).
- **Epilepsy presurgical** — 3D T1w + 3D FLAIR + post-Gd T1w + occasionally a 7 T MP2RAGE. Use `acq-7T` if mixing field strengths in one session.
- **Stroke** — DWI is the headline (see [dwi.md](./dwi.md)); ADC maps belong to derivatives, not raw `anat/`. T2-FLAIR for FLAIR-DWI mismatch is `FLAIR`.
- **Quantitative MRI cohorts** — use the qMRI source collections (`MP2RAGE`, `MTS`, `MPM`, `MEGRE`, `MESE`) per [qmri.md](./qmri.md), not bespoke `acq-` labels.
- **Defacing for sharing** — defaced T1w/FLAIR/T2w required for OpenNeuro upload. Document the defacing tool in `DeidentificationMethod`.

## Software & resources

| Tool / resource | Purpose |
| --- | --- |
| [BIDS spec — anat](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#anatomy-imaging-data) | Authoritative reference |
| [`dcm2niix`](https://github.com/rordenlab/dcm2niix) | DICOM → NIfTI conversion |
| [HeuDiConv](https://heudiconv.readthedocs.io/) | Heuristic-driven BIDS routing |
| [Dcm2Bids](https://unfmontreal.github.io/Dcm2Bids/) | JSON-config converter |
| [`bids-validator`](https://bids-standard.github.io/bids-validator/) | Validate the result |
| [`pydeface`](https://github.com/poldracklab/pydeface) | Defacing for sharing |
| [`mri_reface`](https://www.nitrc.org/projects/mri_reface) | Conservative reface |
| [OpenNeuro](https://openneuro.org/) — `ds002785`, `ds003097` | Reference T1w/T2w/FLAIR datasets |

## References & spec links

- BIDS specification — [Anatomy imaging data](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/magnetic-resonance-imaging-data.html#anatomy-imaging-data).
- Gorgolewski KJ, Auer T, Calhoun VD, et al. The brain imaging data structure, a format for organizing and describing outputs of neuroimaging experiments. *Sci Data.* 2016;3:160044. [doi:10.1038/sdata.2016.44](https://doi.org/10.1038/sdata.2016.44)
- Marques JP, Kober T, Krueger G, et al. MP2RAGE, a self bias-field corrected sequence for improved segmentation and T1-mapping at high field. *NeuroImage.* 2010;49(2):1271–1281. [doi:10.1016/j.neuroimage.2009.10.002](https://doi.org/10.1016/j.neuroimage.2009.10.002)
- Theyers AE, Goldstein BI, Metcalfe AWS, et al. Multisite comparison of MRI defacing software. *Front Psychiatry.* 2021;12:617997. [doi:10.3389/fpsyt.2021.617997](https://doi.org/10.3389/fpsyt.2021.617997)

## Where to next

- Physics: [fundamentals/sequences/mprage.md](../../fundamentals/sequences/mprage.md), [flair.md](../../fundamentals/sequences/flair.md), [qmri.md](../../fundamentals/sequences/qmri.md).
- Analysis: [analysis/structural.md](../../analysis/structural.md), [analysis/vbm.md](../../analysis/vbm.md), [analysis/surface.md](../../analysis/surface.md).
- Next modality: [func.md](./func.md) for BOLD, [qmri.md](./qmri.md) for quantitative collections.
