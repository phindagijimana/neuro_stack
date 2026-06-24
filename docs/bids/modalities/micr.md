# Microscopy in BIDS

> Tissue slices, optical sections, and gigapixel pyramids. The modality goes in the *suffix* (TEM vs CONF vs BF), the sample goes in the *entity* (`sample-`), and OME-TIFF / OME-ZARR carries the pixels.

Course map: spec link → folder layout → suffixes → entities → required JSON → recommended JSON → samples table → conversion recipes → validation → pitfalls → use cases → tools → refs → next.

**Primary spec.** [BIDS — Microscopy](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/microscopy.html) (BEP031, merged). Source paper: [Bourget 2022, *Sci Data* 9:406](https://doi.org/10.1038/s41597-022-01480-6) (Microscopy-BIDS).

## Folder layout — one-glance

```text
ds-microscopy/
├── dataset_description.json
├── participants.tsv
├── samples.tsv
└── sub-01/
    └── micr/
        ├── sub-01_sample-001_BF.ome.tif
        ├── sub-01_sample-001_BF.json
        ├── sub-01_sample-001_stain-DAPI_FLUO.ome.tif
        ├── sub-01_sample-001_stain-DAPI_FLUO.json
        ├── sub-01_sample-001_stain-GFAP_FLUO.ome.tif
        ├── sub-01_sample-001_stain-GFAP_FLUO.json
        ├── sub-01_sample-002_chunk-01_TEM.ome.tif
        ├── sub-01_sample-002_chunk-02_TEM.ome.tif
        ├── sub-01_sample-002_chunk-03_TEM.ome.tif
        └── sub-01_sample-001_photo.jpg                 # slice landmark photo
```

Microscopy folders sit under the subject directly (no `ses-` in most workflows; permissible if longitudinal). The `samples.tsv` at root maps every `sample-<label>` to a participant and a tissue type.

## Allowed suffixes — the modality lives here

| Suffix | Technique |
|---|---|
| `TEM` | Transmission electron microscopy |
| `SEM` | Scanning electron microscopy |
| `uCT` | Micro-CT |
| `BF` | Bright-field |
| `DF` | Dark-field |
| `PC` | Phase contrast |
| `DIC` | Differential interference contrast |
| `FLUO` | Fluorescence (wide-field) |
| `CONF` | Confocal |
| `MR` | Slice-photo paired with MR (e.g. histology-MR registration) |
| `2PE` | Two-photon excitation |
| `MPE` | Multi-photon excitation |
| `NLO` | Non-linear optical |
| `OCT` | Optical coherence tomography |
| `SPIM` | Selective plane illumination (light-sheet) |
| `SR` | Super-resolution |
| `PLI` | Polarised-light imaging |
| `XPCT` | X-ray phase-contrast tomography |
| `CARS` | Coherent anti-Stokes Raman scattering |

## Allowed file formats

| Format | Extensions | Note |
|---|---|---|
| **OME-TIFF** | `.ome.tif`, `.ome.btf` (BigTIFF) | RECOMMENDED — embedded XML metadata, multi-resolution pyramid |
| **OME-ZARR / NGFF** | `.ome.zarr/` (directory) | RECOMMENDED for very large multi-scale data; chunked + compressed N-D arrays |
| **TIFF** | `.tif` | Plain, no OME XML — acceptable but less rich |
| **PNG** | `.png` | For small previews / 2D-only |

OME-ZARR ([next-gen file format spec](https://ngff.openmicroscopy.org/latest/)) is the way forward for terabyte-scale pyramidal data; OME-TIFF remains the workhorse for slide-level whole-slide-imaging (WSI).

## Filename entities — in order

```
sub-<label>[_ses-<label>]_sample-<label>[_acq-<label>][_stain-<label>][_run-<index>][_chunk-<index>]_<suffix>.<ext>
```

| Entity | Required? | Notes |
|---|---|---|
| `sub-` | always | subject |
| `ses-` | if longitudinal | rare in pathology workflows |
| `sample-` | **always** | unique tissue sample per subject |
| `acq-` | optional | scanner setting / magnification preset |
| `stain-` | per stain | one file per `(sample, stain)` pair |
| `run-` | if >1 acquisition | re-scan same slide |
| `chunk-` | if tiled | each tile of a tiled acquisition |

## Required JSON sidecar fields

| Field | Type | Example |
|---|---|---|
| `PixelSize` | array of 2 or 3 numbers | `[0.5, 0.5]` (XY) or `[0.5, 0.5, 5.0]` (XYZ) |
| `PixelSizeUnits` | string | `"mm"`, `"um"`, or `"nm"` |

### Minimal sidecar — copy-paste

```json
{
  "PixelSize": [0.325, 0.325, 5.0],
  "PixelSizeUnits": "um",
  "Manufacturer": "Leica",
  "ManufacturersModelName": "Aperio AT2",
  "DeviceSerialNumber": "AT2-12345",
  "SoftwareVersions": "ScanScope 12.4.3",
  "InstitutionName": "URMC Pathology",
  "BodyPart": "BRAIN",
  "BodyPartDetails": "hippocampus",
  "SampleEnvironment": "ex vivo",
  "SampleEmbedding": "paraffin",
  "SampleFixation": "10% neutral-buffered formalin, 48 h",
  "SampleStaining": "H&E",
  "SliceThickness": 5,
  "Immersion": "Air",
  "NumericalAperture": 0.45,
  "Magnification": 20,
  "ImageAcquisitionProtocol": "Whole-slide brightfield at 20x, single-z, pyramidal."
}
```

## Recommended JSON fields

| Field | Use |
|---|---|
| `Manufacturer`, `ManufacturersModelName`, `DeviceSerialNumber`, `SoftwareVersions` | full provenance |
| `InstitutionName`, `InstitutionAddress`, `InstitutionalDepartmentName` | site |
| `BodyPart`, `BodyPartDetails` | anatomical region |
| `SampleEnvironment` | `"ex vivo"`, `"in vivo"`, `"in vitro"` |
| `SampleEmbedding`, `SampleFixation`, `SampleStaining` | preparation chain |
| `SamplePrimaryAntibody`, `SampleSecondaryAntibody` | IHC details |
| `SliceThickness` | µm; physical section thickness |
| `Immersion`, `NumericalAperture`, `Magnification` | objective |
| `TissueDeformationScaling` | shrinkage / expansion factor vs in-vivo |
| `ChunkTransformationMatrix` | tile → slide registration affine |
| `ImageAcquisitionProtocol`, `OtherAcquisitionParameters` | free-text |

## `samples.tsv` — required

Mandatory dataset-level file. Required column: `sample_id`. Recommended: `participant_id`, `sample_type` (`tissue`, `cell line`, `in vitro differentiated cells`, `primary cell`, `cell-free sample`, `cloning host`, `whole organisms`), `pathology`, `derived_from`, `sample_origin`.

```tsv
sample_id	participant_id	sample_type	pathology	sample_origin	derived_from
sample-001	sub-01	tissue	control	brain_hippocampus_left	n/a
sample-002	sub-01	tissue	control	brain_hippocampus_right	n/a
sample-003	sub-02	tissue	AD_Braak_VI	brain_entorhinal_left	n/a
```

## Photo / landmark companions

`*_photo.jpg` / `.png` / `.tif` capture slicing landmarks (block face, slide overview), with an optional sidecar:

```json
{
  "PhotoDescription": "Overview of slide with rule for scale.",
  "IntendedFor": ["bids::sub-01/micr/sub-01_sample-001_BF.ome.tif"]
}
```

## Conversion recipes

There is no single canonical converter — the field's tooling is converging. Common paths:

```python
# Whole-slide SVS → OME-TIFF → BIDS
import bioio                       # https://github.com/AllenCellModeling/bioio
img = bioio.BioImage("raw/sub-01/sample-001.svs")
img.save("bids/sub-01/micr/sub-01_sample-001_BF.ome.tif")
```

For OME-ZARR conversions of whole-slide / light-sheet data:

```bash
# bioformats2raw + raw2ometiff is the OME canonical pipeline
bioformats2raw raw/sub-01/sample-002.czi /tmp/sample002.zarr
raw2ometiff /tmp/sample002.zarr bids/sub-01/micr/sub-01_sample-002_CONF.ome.tif
```

Connectomics shops use [`webknossos-libs`](https://github.com/scalableminds/webknossos-libs) to export EM volumes to OME-ZARR. Digital-pathology shops use [`tifffile`](https://github.com/cgohlke/tifffile) or [`openslide-python`](https://openslide.org/) plus a custom writer for the BIDS sidecars.

Cross-link: [bids/dicom-to-bids.md](../dicom-to-bids.md) for the broader heuristic pattern; [fundamentals/medical-imaging/segmentation.md](../../fundamentals/medical-imaging/segmentation.md) for the digital-pathology side.

## Validation

`bids-validator` ≥ 1.10 covers microscopy. Beyond schema:

- `PixelSize` length must be 2 (XY) or 3 (XYZ); 3 only makes sense for stacks.
- `PixelSizeUnits` must be one of `mm` / `um` / `nm` — Unicode `µm` is **not** allowed.
- `samples.tsv` must list every `sample-<label>` that appears in filenames.
- `IntendedFor` paths in photo sidecars must resolve.

## Common pitfalls

1. **Pixel-size unit confusion.** `PixelSize: [0.5, 0.5], PixelSizeUnits: "mm"` says 500 µm pixels (a low-res macro photo). For typical 20× brightfield, write `[0.325, 0.325], "um"`. Off by 1000× and your downstream segmentations land at the wrong scale.
2. **OME-TIFF without OME XML.** A `.tif` renamed to `.ome.tif` is not OME-TIFF. Use `bioformats2raw` + `raw2ometiff` or [`pyometiff`](https://github.com/filippocastelli/pyometiff) to embed the XML metadata.
3. **Tile alignment unspecified.** Tiled WSI without a `ChunkTransformationMatrix` or OME-XML `Plate`/`Well` info can't be re-assembled. Either preserve OME-XML tile descriptors or write the affine in each `_chunk-` sidecar.
4. **Pyramid levels assumed.** OME-ZARR pyramid level 0 is full resolution; level 1 is downsampled. Tools default differently. Document the pyramid scheme in `OtherAcquisitionParameters` if it's non-standard.
5. **Sample collisions across subjects.** `sample-001` for sub-01 and sub-02 are different physical samples but identical labels. The `samples.tsv` row keyed by `(sample_id, participant_id)` distinguishes them; downstream tools that ignore the participant link will conflate.
6. **Stain encoding.** `stain-HE` vs `stain-h_e` vs `stain-haematoxylineosin` are all the same stain — pick one (lowercase, alphanumeric only; underscores not allowed in entity labels).
7. **Multi-channel fluorescence stored as one file.** Each `(sample, stain)` pair = one file with one `stain-` label. A 4-channel fluorescence acquisition becomes four files, not one file with 4 channels in OME-XML — the spec prefers the former for queryability.

## Use cases

- **Histology-MRI registration.** Match `MR`-suffix slice photos against `T1w` MRI for ex-vivo correlation. Cross-link [fundamentals/medical-imaging/segmentation.md](../../fundamentals/medical-imaging/segmentation.md).
- **Connectomics (EM).** TEM / SEM volumes of mm-scale tissue; OME-ZARR pyramid is mandatory. Allen Institute, FlyWire, MICrONS corpora.
- **Digital pathology.** Brightfield H&E + IHC at 20×–40×; whole-slide images in OME-TIFF; one `sample-` per slide.
- **Light-sheet / iDISCO+.** Whole-brain SPIM volumes; OME-ZARR pyramid. Use `SPIM` suffix, `SampleEmbedding: "iDISCO+"`.
- **Two-photon in vivo.** `2PE` suffix; chronic recordings with `ses-day01`, `ses-day14`, etc.
- **Super-resolution (STED / PALM / STORM).** `SR` suffix; `Magnification` and `NumericalAperture` are critical for resolution claims.

## Software & resources

| Tool | Role | Link |
|---|---|---|
| **bioio** | Python read/write OME-TIFF / OME-ZARR / vendor | [AllenCellModeling/bioio](https://github.com/AllenCellModeling/bioio) |
| **bioformats2raw / raw2ometiff** | Vendor → OME-ZARR → OME-TIFF | [glencoesoftware/bioformats2raw](https://github.com/glencoesoftware/bioformats2raw) |
| **tifffile** | Pure-Python TIFF / OME-TIFF | [cgohlke/tifffile](https://github.com/cgohlke/tifffile) |
| **openslide-python** | Whole-slide image read | [openslide.org](https://openslide.org/) |
| **napari** | Multi-scale OME-ZARR viewer | [napari.org](https://napari.org/) |
| **QuPath** | Digital-pathology analysis | [qupath.github.io](https://qupath.github.io/) |
| **OME-NGFF / OME-Zarr spec** | Next-gen file format | [ngff.openmicroscopy.org](https://ngff.openmicroscopy.org/latest/) |
| **bids-validator** | Schema + structural checks | [bids-standard/bids-validator](https://github.com/bids-standard/bids-validator) |
| **OpenNeuro / EBRAINS microscopy datasets** | Real BIDS-microscopy corpora | [openneuro.org](https://openneuro.org/), [search.kg.ebrains.eu](https://search.kg.ebrains.eu) |

## References

- BIDS microscopy extension spec — [bids-specification.readthedocs.io](https://bids-specification.readthedocs.io/en/latest/modality-specific-files/microscopy.html)
- Bourget M-H, Kamentsky L, Ghosh SS, et al. Microscopy-BIDS: an extension to the Brain Imaging Data Structure for microscopy data. *Sci Data.* 2022;9:406. [doi:10.1038/s41597-022-01480-6](https://doi.org/10.1038/s41597-022-01480-6)
- Moore J, Allan C, Besson S, et al. OME-NGFF: a next-generation file format for expanding bioimaging data-access strategies. *Nat Methods.* 2021;18:1496-1498. [doi:10.1038/s41592-021-01326-w](https://doi.org/10.1038/s41592-021-01326-w)
- Goldberg IG, Allan C, Burel J-M, et al. The Open Microscopy Environment (OME) Data Model and XML file: open tools for informatics and quantitative analysis in biological imaging. *Genome Biol.* 2005;6:R47. [doi:10.1186/gb-2005-6-5-r47](https://doi.org/10.1186/gb-2005-6-5-r47)

## Where to next

- Digital pathology + segmentation: [fundamentals/medical-imaging/segmentation.md](../../fundamentals/medical-imaging/segmentation.md)
- Co-registration to MR: see the MR-family anat / qmri pages
- Derivatives layout for whole-slide segmentation outputs: [bids/derivatives.md](../derivatives.md)
- For terabyte datasets and versioning: [bids/datalad.md](../datalad.md)
