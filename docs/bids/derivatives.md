# Derivatives layout

> How to lay out your own pipeline's outputs so the next BIDS app can use them.

## The rule

The BIDS-Derivatives specification lives [here](https://bids-specification.readthedocs.io/en/stable/derivatives/introduction.html). It's BIDS, with three extras:

1. Outputs live under `derivatives/<pipeline-name>/`.
2. That folder has its own `dataset_description.json` declaring the pipeline.
3. Filenames carry a `desc-` entity describing what's been done.

That's it.

## A minimal derivatives folder

```text
bids/
├── dataset_description.json          # raw
└── derivatives/
    └── my_pipeline/
        ├── dataset_description.json  # derivative
        └── sub-001/
            └── anat/
                ├── sub-001_desc-preproc_T1w.nii.gz
                └── sub-001_desc-preproc_T1w.json
```

The `dataset_description.json` for a derivative looks like:

```json
{
  "Name": "my_pipeline",
  "BIDSVersion": "1.8.0",
  "DatasetType": "derivative",
  "GeneratedBy": [{
    "Name": "my_pipeline",
    "Version": "0.3.1",
    "Container": {"Type": "apptainer", "Tag": "my_pipeline:0.3.1"},
    "CodeURL": "https://github.com/me/my_pipeline"
  }],
  "SourceDatasets": [{
    "DOI": "doi:10.18112/openneuro.ds00xxxx.v1.0.0",
    "URL": "https://openneuro.org/datasets/ds00xxxx",
    "Version": "1.0.0"
  }]
}
```

`GeneratedBy` makes your output traceable. `SourceDatasets` lets downstream tools find the raw data.

## Naming derivatives

The grammar that matters:

- Keep the BIDS entities of the source: `sub-001_ses-01_task-rest_run-01`...
- Add a `desc-XYZ` to describe what's been done: `..._desc-preproc_bold.nii.gz`.
- Add `space-XYZ` if you've changed coordinate system: `..._space-MNI152NLin2009cAsym_desc-preproc_bold.nii.gz`.
- For atlases / masks, use the `*_dseg.nii.gz` and `*_mask.nii.gz` suffixes.

## Sidecars are not optional

Every derived `.nii.gz` needs a sibling `.json` recording at minimum:

```json
{
  "Sources": ["bids::sub-001/anat/sub-001_T1w.nii.gz"],
  "SoftwareName": "my_pipeline",
  "SoftwareVersion": "0.3.1"
}
```

The `Sources` field is essentially row-level lineage — what input(s) produced this output. Pipelines like fMRIPrep produce far richer sidecars (motion summary, registration metrics, QC) but `Sources` is the minimum.

## Why this matters

BIDS-Derivatives is what makes multi-pipeline workflows tractable:

```text
DICOM → HeuDiConv → BIDS raw
                       └→ fMRIPrep → derivatives/fmriprep
                                       └→ Nilearn analysis → derivatives/nilearn_first_level
```

Each downstream tool only needs to know "give me a BIDS layout, point it at the upstream derivative folder". No bespoke globbing, no path-juggling.

## Where to next

[Versioning with DataLad](datalad.md) — when the dataset is going to outlive a single project.
