# File formats

> DICOM, NIfTI, GIFTI / CIFTI, and the BIDS standard that turns a folder of files into a dataset.

## DICOM

**DICOM** (Digital Imaging and Communications in Medicine) is the clinical-imaging file *and* network protocol. Every modern scanner produces DICOM; every clinical PACS speaks DICOM.

A DICOM file looks like:

- A series of **tags** (each a 4-byte hex code like `(0010,0010)` for Patient Name).
- Optional **pixel data** (the image itself).
- Series-level grouping: one *study* contains many *series*; one *series* contains many *instances* (slices or frames).

DICOM documentation lives [here](https://www.dicomstandard.org/current). For research, you almost always convert DICOM to NIfTI on ingestion using `dcm2niix` [Li et al., 2016](https://doi.org/10.1016/j.jneumeth.2016.03.001)[^dcm2niix]. The conversion drops DICOM-specific metadata you don't need and produces:

- A `.nii.gz` volume.
- A `.json` sidecar that preserves the parameters you *do* need (TR, TE, sequence name, etc.).
- For DWI: `.bval` and `.bvec` files.

The handbook ships a thin wrapper around `dcm2niix` at `neuro_handbook.dicom.dicom_to_nifti`.

## NIfTI

**NIfTI** is the research-imaging format. A NIfTI file is:

- A **header** (~350 bytes) — array dimensions, voxel sizes, the affine matrix, units, intent code.
- A **data block** — the raw voxel array, typed `uint8` / `int16` / `float32` / etc.

Extensions:

- `.nii` — uncompressed.
- `.nii.gz` — gzip-compressed. The default in research; ~3–5× smaller for typical structural / functional data.

Two NIfTI flavours: **NIfTI-1** (the original) and **NIfTI-2** (allows datasets larger than 2³¹ voxels). Most tools speak both.

Read with [`nibabel`](https://nipy.org/nibabel/) (full docs [here](https://nipy.org/nibabel/)):

```python
import nibabel as nib
img = nib.load("sub-001_T1w.nii.gz")
data = img.get_fdata()  # numpy array
print(data.shape, data.dtype)
print(img.affine)
print(img.header)
```

## GIFTI and CIFTI

When you reconstruct the cortical surface (with FreeSurfer or HCP-style tools), the data isn't a 3D grid anymore — it's a 2D mesh.

- **GIFTI** (`.surf.gii`, `.func.gii`, `.shape.gii`) — XML-based format for a single surface or per-vertex data array.
- **CIFTI** (`.dscalar.nii`, `.dtseries.nii`, `.pscalar.nii`) — the [CIFTI-2 specification](https://www.nitrc.org/projects/cifti/) — combines surface (left + right hemispheres) **and** subcortical volume in one file. The HCP standard.

CIFTI files are technically NIfTI-2 files with a special intent code; tools that don't understand them will see a tiny weird array. Use `nibabel.cifti2` to read them.

## BIDS — the standard

**BIDS** (Brain Imaging Data Structure) [Gorgolewski et al., 2016](https://doi.org/10.1038/sdata.2016.44)[^bids] prescribes:

1. **A folder layout.**

    ```text
    dataset/
    ├── dataset_description.json
    ├── participants.tsv
    └── sub-001/
        ├── anat/
        │   ├── sub-001_T1w.nii.gz
        │   └── sub-001_T1w.json
        └── dwi/
            ├── sub-001_dwi.nii.gz
            ├── sub-001_dwi.json
            ├── sub-001_dwi.bval
            └── sub-001_dwi.bvec
    ```

2. **A filename grammar.** Each filename is a chain of `key-value` **entities** joined by underscores: `sub-001_ses-01_task-rest_run-01_bold.nii.gz`. Order matters; the spec defines it.

3. **JSON sidecars** for everything. A `.nii.gz` always has a sibling `.json` recording the parameters that would otherwise be lost (TR, TE, slice timing, etc.).

4. **A `participants.tsv`** at the root listing subject metadata.

5. **A `derivatives/` subtree** for everything you produce from the raw data, structured the same way.

### Why BIDS exists

Before BIDS, every lab had a folder naming scheme, and every pipeline had glob patterns that worked at the lab that wrote them. BIDS fixed that:

- A **BIDS app** (e.g., fMRIPrep, QSIPrep) takes any BIDS dataset and runs without per-dataset configuration.
- A **BIDS validator** checks a dataset against the spec before you waste compute on broken inputs.
- A **BIDS sub-spec** (BIDS-EEG, BIDS-PET, BIDS-MEG, BIDS-microscopy) extends the same grammar to new modalities.

If you're starting a new project, start with BIDS. The walker in this repo (`neuro_handbook.bids.walk_bids`) shows the minimum you need to understand the layout, and the `fixtures/sub-tiny/` dataset is a tiny but valid BIDS tree.

### When BIDS hurts

- Vendor file formats that don't map cleanly (some MEG vendors, some PET reconstructions).
- Datasets with thousands of derived files per subject — file-count explosion is real.
- Sessions with branching acquisitions where the BIDS naming can't express the relationship.

For these, BIDS-derivatives or the BIDS extensions in development are usually the answer. Stay close to the spec; don't invent ad-hoc folder schemes.

## References

[^bids]: Gorgolewski KJ, Auer T, Calhoun VD, et al. The brain imaging data structure, a format for organizing and describing outputs of neuroimaging experiments. *Sci Data.* 2016;3:160044. [doi:10.1038/sdata.2016.44](https://doi.org/10.1038/sdata.2016.44)
[^dcm2niix]: Li X, Morgan PS, Ashburner J, Smith J, Rorden C. The first step for neuroimaging data analysis: DICOM to NIfTI conversion. *J Neurosci Methods.* 2016;264:47-56. [doi:10.1016/j.jneumeth.2016.03.001](https://doi.org/10.1016/j.jneumeth.2016.03.001)

## Where to next

[Preprocessing overview](preprocessing.md) — what a typical BIDS app does to raw data before you analyse it.
