# Fundamentals

> What a "neuroimaging dataset" actually is, and how it gets onto your disk.

```mermaid
flowchart LR
    A[Subject in scanner] -->|raw scanner output| B[DICOM]
    B -->|dcm2niix| C[NIfTI + JSON sidecar]
    C -->|organise| D[BIDS dataset]
    D -->|BIDS app<br/>fMRIPrep / QSIPrep| E[derivatives/]
    E -->|extract features<br/>register, segment| F[Analysis-ready data]
    F --> G[Statistics / ML / Figure]
    style A fill:#fff,stroke:#888
    style G fill:#e0e0ff,stroke:#444
```

*<small>The neuroimaging-data lifecycle these chapters cover. Original figure.</small>*

If you've never touched neuroimaging data before, this is where to start. The section is in four layers:

## Layer 1 — What the data is

1. **[Modalities](modalities.md)** — what MRI, DWI, fMRI, PET, and EEG actually measure, and what their data looks like as files.
2. **[Coordinate systems](coordinate-systems.md)** — RAS vs LPS vs voxel space, world coordinates, and why "the same point" can have ten different addresses.
3. **[File formats](file-formats.md)** — DICOM, NIfTI, GIFTI/CIFTI, and the BIDS standard that ties them into a dataset.
4. **[Preprocessing overview](preprocessing.md)** — the steps almost every pipeline performs before analysis: denoising, motion correction, registration, normalisation.

## Layer 2 — How the scanner makes it

5. **[MRI sequences](sequences/index.md)** — the physics-and-parameters layer underneath every acquisition. MPRAGE, DWI, EPI, FLAIR, GRE, SWI, spin echo — each gets its own deep dive with peer-reviewed references.

## Layer 3 — The toolkit to think with

6. **[Computational & math foundations](foundations/index.md)** — Python, Bash, CLI commands, MATLAB, data analysis, statistics, mathematics, medical imaging physics, neuroscience & neurology. The programming languages, the command toolbox, the inferential machinery, the math vocabulary, the cross-modality physics, and the brain biology you need to *think* about neuroimaging at PhD level.

## Layer 4 — The image-processing engineering layer

7. **[Medical imaging](medical-imaging/index.md)** — acquisition, reconstruction, segmentation, registration, enhancement & quality. The methodological pipeline that turns raw measurements into the volumes, surfaces, and labels every downstream analysis depends on. Each chapter is structured as *Theory → Mathematics → Steps → Practical example → References*.

By the end of this section you'll be able to look at a folder you've never seen, identify what's inside, choose tools for it, and reason quantitatively about every step that produced it.

## Recommended readings

External anchors for the whole Fundamentals section. The textbook list is roughly "what a graduate student should own"; the MOOC and review-paper lists are ordered as "where to go for free, online, in priority order".

### Textbooks

- [Huettel, Song & McCarthy — *Functional Magnetic Resonance Imaging*](https://global.oup.com/academic/product/functional-magnetic-resonance-imaging-9781605356549) — the standard graduate fMRI textbook; physics, acquisition, analysis, design.
- [Buxton — *Introduction to Functional Magnetic Resonance Imaging*](https://www.cambridge.org/core/books/introduction-to-functional-magnetic-resonance-imaging/3151AF5E2C56D81F1C1A0B6E5C1D4B0B) — deeper on BOLD biophysics and the haemodynamic response.
- [Bernstein, King & Zhou — *Handbook of MRI Pulse Sequences*](https://www.elsevier.com/books/handbook-of-mri-pulse-sequences/bernstein/978-0-12-092861-3) — the reference for every pulse-sequence question you will ever ask.
- [Brown, Cheng, Haacke, Thompson & Venkatesan — *MRI: Physical Principles and Sequence Design*](https://www.wiley.com/en-us/MRI%3A+Physical+Principles+and+Sequence+Design%2C+2nd+Edition-p-9780471720850) — rigorous MR physics with worked sequence design.
- [Jones — *Diffusion MRI*](https://global.oup.com/academic/product/diffusion-mri-9780195369779) — the canonical edited volume on diffusion theory and practice.
- [Mori — *Introduction to Diffusion Tensor Imaging*](https://www.elsevier.com/books/introduction-to-diffusion-tensor-imaging/mori/978-0-444-52828-5) — short, readable on-ramp to DTI before reading Jones.
- [Kandel et al. — *Principles of Neural Science*](https://www.mhprofessional.com/principles-of-neural-science-sixth-edition-9781259642234-usa) — the neuroscience reference; if you only buy one, this one.
- [Purves et al. — *Neuroscience*](https://global.oup.com/academic/product/neuroscience-9781605353807) — the standard upper-undergraduate / early-graduate text, more accessible than Kandel.

### MOOCs / video courses

- [HarvardX "Fundamentals of Neuroscience"](https://www.edx.org/learn/neuroscience/harvard-university-fundamentals-of-neuroscience-part-1-the-electrical-properties-of-the-neuron) — three-part edX series; best free intro to systems neuroscience.
- [Coursera "Computational Neuroscience" (UW)](https://www.coursera.org/learn/computational-neuroscience) — Rao & Fairhall; the standard online course on neural coding and dynamics.
- [MIT OCW 9.13 "The Human Brain"](https://ocw.mit.edu/courses/9-13-the-human-brain-spring-2019/) — Nancy Kanwisher's lectures; cognitive neuroscience with imaging examples.
- [ISMRM online education](https://www.ismrm.org/online-education/) — the field's own teaching tracks for MR physics, acquisition, and reconstruction.
- [3Blue1Brown — Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra) — the visual refresher to do before any imaging-math course.

### Canonical review papers

- [Logothetis 2008 — *What we can do and what we cannot do with fMRI*](https://doi.org/10.1038/nature06976) — the honest boundary of what BOLD measures.
- [Power et al. 2012 — *Spurious but systematic correlations from subject motion*](https://doi.org/10.1016/j.neuroimage.2011.10.018) — the paper that changed how the field handles motion.
- [Glasser et al. 2016 — *A multi-modal parcellation of human cerebral cortex*](https://doi.org/10.1038/nature18933) — HCP cortical parcellation; the modern atlas reference.
- [Jenkinson et al. 2012 — *FSL*](https://doi.org/10.1016/j.neuroimage.2011.09.015) — the toolbox overview review for FSL.
- [Cox 1996 — *AFNI*](https://doi.org/10.1006/cbmr.1996.0014) — original AFNI paper; still the standard citation.
- [Fischl 2012 — *FreeSurfer*](https://doi.org/10.1016/j.neuroimage.2012.01.021) — the surface-based-analysis review.
- [Esteban et al. 2019 — *fMRIPrep*](https://doi.org/10.1038/s41592-018-0235-4) — the BIDS-app preprocessing reference.
- [Cieslak et al. 2021 — *QSIPrep*](https://doi.org/10.1038/s41592-021-01185-5) — the diffusion-preprocessing counterpart.

### Web tutorials & teaching sites

- [Andy's Brain Book](https://andysbrainbook.readthedocs.io/) — the most readable end-to-end fMRI / DWI tutorial collection online.
- [MRIQuestions](https://www.mriquestions.com/) — searchable MR-physics Q&A; the go-to for "why does this artefact appear?"
- [Radiopaedia](https://radiopaedia.org/) — the radiology reference for anatomy, pathology, and modality-specific appearances.
- [NITRC — Neuroimaging Tools & Resources Collaboratory](https://www.nitrc.org/) — catalogue of tools, atlases, and training material.
- [OHBM Educational Course materials](https://www.humanbrainmapping.org/) — annual society course slides covering the methodological frontier.

## Where this material lives in the bigger picture

The fundamentals section answers **what is the data and how do I think about it** questions. The [BIDS toolkit](../bids/index.md) shows how to manipulate it. [Analysis](../analysis/index.md) is what you compute. [Data engineering](../data-engineering/index.md) is how to do it at scale. [AI / ML](../ai/index.md) is the modern modelling layer. Each later section assumes you've internalised the foundations.
