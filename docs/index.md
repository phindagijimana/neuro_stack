---
hide:
  - navigation
  - toc
---

# NeuroStack — the neuroimaging documentation hub

> Welcome to **NeuroStack** — the open documentation hub for everything you need to do credible neuroimaging work.

Here you'll find a tour of the **fundamentals** (modalities, file formats, MRI physics, the maths, the neuroscience), the **BIDS toolkit**, a deep **analysis** library, an opinionated **data-engineering** book, a focused **AI / ML** section, a **computing** environment guide, and a curated **landmark-work** reading list — together with a small companion **Python package** and runnable examples.

NeuroStack is written for **people getting started** in neuroimaging research, neuroscience research, and the engineering that supports them: graduate students, postdocs, research software engineers, data engineers arriving from outside the medical-imaging world, and developers building neuro-AI products. It tries to be the document we wish we had when we first walked into the field.

Found something missing, wrong, or out of date? We'd love to know — every page has an *edit-on-GitHub* link in the top right, and you can also open an issue or pull request on the [repo](https://github.com/phindagijimana/neuro_stack). Suggestions, corrections, and contributions are all welcome.

---

## New to neuroimaging? Start here

<div class="grid cards" markdown>

-   :material-rocket-launch: **[Getting started](getting-started/index.md)** — the 30-minute on-ramp. Install environment, load your first NIfTI, run your first BIDS app, render your first figure.

-   :material-map-marker-path: **[Reading paths](paths/index.md)** — four named paths through the handbook for new researchers, software engineers pivoting in, clinicians, and ML engineers.

-   :material-school-outline: **[Tutorials](tutorials/index.md)** — five end-to-end walkthroughs from data to figure, including a synthesis capstone.

</div>

---

## Browse by topic

<div class="grid cards" markdown>

-   :material-school:{ .lg .middle } **Fundamentals**

    ---

    What a "neuroimaging dataset" actually is. MRI, DWI, fMRI, PET, EEG; DICOM, NIfTI, BIDS; coordinate systems and preprocessing.

    [:octicons-arrow-right-24: Start here](fundamentals/index.md)

-   :material-file-tree:{ .lg .middle } **BIDS toolkit**

    ---

    Validate, convert from DICOM, query with PyBIDS, lay out derivatives, version with DataLad, dodge the common pitfalls.

    [:octicons-arrow-right-24: Open the toolkit](bids/index.md)

-   :material-chart-line:{ .lg .middle } **Analysis**

    ---

    Structural morphometry, diffusion tractography, functional connectivity, surface-based analysis, group statistics, multiple-comparison correction.

    [:octicons-arrow-right-24: Analyse data](analysis/index.md)

-   :material-pipe:{ .lg .middle } **Data engineering**

    ---

    DAGs, pipelines, idempotency, observability, testing — taught against a real DWI pipeline. Plus 25 advanced chapters on Spark, Kafka, dbt, MLOps, FinOps.

    [:octicons-arrow-right-24: Build pipelines](data-engineering/index.md)

-   :material-brain:{ .lg .middle } **AI / ML**

    ---

    Classical ML on volumetrics, deep learning architectures, foundation models, and the evaluation pitfalls that bite neuroimaging projects specifically.

    [:octicons-arrow-right-24: Train models](ai/index.md)

-   :material-server:{ .lg .middle } **Computing**

    ---

    Python scientific stack, containers, HPC + Slurm, cloud, GPUs, IDE setup, dependency management, the reproducibility checklist.

    [:octicons-arrow-right-24: Set up your env](computing/index.md)

-   :material-bookshelf:{ .lg .middle } **Landmark work**

    ---

    Foundational papers, reference datasets (HCP, UK Biobank, ABCD, ADNI), major pipelines (FreeSurfer, fMRIPrep, QSIPrep), atlases, BIDS-app workflows.

    [:octicons-arrow-right-24: Read the field](landmark/index.md)

-   :material-tools:{ .lg .middle } **Tools landscape**

    ---

    Opinionated map of orchestrators, storage, transformation, observability — pointers, not exhaustive lists.

    [:octicons-arrow-right-24: Pick a tool](tools/index.md)

</div>

---

## How to read it

Pick the entry point that matches your background:

- **New to neuroimaging?** Start with [Fundamentals → Modalities](fundamentals/modalities.md). Then [BIDS toolkit](bids/index.md) and [Computing](computing/index.md).
- **Software / data engineer coming in from outside?** Jump to [Fundamentals → File formats](fundamentals/file-formats.md), then go straight to [Data engineering → Foundations](data-engineering/foundations.md).
- **Neuroscientist who needs to scale a pipeline?** [Data engineering → Portfolio roadmap](data-engineering/portfolio-roadmap.md) is the action item.
- **Looking up something specific?** Use search (top bar) or the [Glossary](glossary.md).

## Companion code

This site is generated from a repository that also ships a small Python package, `neuro_handbook`, plus runnable examples:

```bash
git clone https://github.com/phindagijimana/neuro_stack.git
cd neuro_handbook
pip install -e ".[docs,dev,neuro]"
python examples/01_walk_bids.py fixtures/sub-tiny
mkdocs serve  # preview this site locally
```

The code is intentionally small and readable. If a page on this site refers to a snippet, the snippet exists in the repo and is tested in CI.

## Contributing

This is a community reference. The DWI-focused parts reflect one team's experience; broader coverage is welcome. See the [repo](https://github.com/phindagijimana/neuro_stack) for how to file issues and open PRs.

## Contact

Maintained by **Philbert Ndagijimana**.

- :material-linkedin: LinkedIn — [philbert-ndagijimana](https://www.linkedin.com/in/philbert-ndagijimana-319570188/)
- :material-email: Email — [phindagiji@gmail.com](mailto:phindagiji@gmail.com)
- :material-github: GitHub issues — [phindagijimana/neuro_stack](https://github.com/phindagijimana/neuro_stack/issues)

Reach out for collaborations, corrections, lab tours, or to flag a topic the handbook should cover. The links also appear as social icons at the bottom of every page.

## License

Content and code are released under the [MIT license](https://github.com/phindagijimana/neuro_stack/blob/main/LICENSE).
