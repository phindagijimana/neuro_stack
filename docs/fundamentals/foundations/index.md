# Computational & math foundations

> Everything you need to *think* about neuroimaging before you can do it well.

The rest of the Fundamentals section explains what a neuroimaging dataset is. This sub-section explains the toolkit you need to manipulate it: a programming language, a shell, a statistics vocabulary, the math underneath, and a working grasp of the physics that produced the signal in the first place.

Each page is written for a research-track newcomer — someone who knows *some* programming or statistics and needs the gaps filled with the right depth for research work, not introductory snippets.

## Pages

<div class="grid cards" markdown>

-   :fontawesome-brands-python: **[Python](python.md)**

    ---

    The default glue language: NumPy, pandas, Matplotlib, `pathlib`, argparse, logging, and the neuroimaging stack (NIfTI, BIDS, fMRIPrep derivatives).

-   :material-bash: **[Bash](bash.md)**

    ---

    Bash as a programming language: strict mode, variables, control flow, functions, arrays, traps, Slurm script patterns, when to stop.

-   :material-console-line: **[CLI commands](cli.md)**

    ---

    The command reference: `ls`, `pwd`, `cp`, `find`, `grep`, `chmod`, `ps`. Local↔remote transfers (`scp`, `rsync`, `ssh`, `sftp`, `aws s3`). Text processing (`awk`, `sed`).

-   :material-language-matlab: **[MATLAB](matlab.md)**

    ---

    Arrays, scripts vs functions, tables, statistics, SPM / EEGLAB / FieldTrip ecosystem, and when to leave MATLAB for Python.

-   :material-table-search: **[Data analysis](data-analysis.md)**

    ---

    Cohort tables, EDA, missing data, ComBat harmonisation, confound regression, paper-ready figure recipes, reproducibility audit.

-   :material-chart-bell-curve-cumulative: **[Statistics](statistics.md)**

    ---

    Probability, GLM, mixed models, multiple comparisons, permutation, effect sizes, power analysis, Bayesian thinking.

-   :material-function-variant: **[Mathematics](mathematics.md)**

    ---

    Linear algebra, calculus, optimisation, signal processing, Fourier transforms, geometry of the brain, and the math underneath neuroimaging AI (backprop, attention, diffusion models, graph nets).

-   :material-atom: **[Medical imaging physics](physics.md)**

    ---

    MRI Bloch / k-space deep dive, plus CT, PET kinetic modelling, ultrasound, NIRS / OCT, EEG/MEG biophysics, MRS — every modality you'll meet.

-   :material-brain: **[Neuroscience & neurology](neuroscience.md)**

    ---

    Macroscale anatomy, cells and circuits, large-scale functional networks, the clinical conditions neuroimaging studies (stroke, AD, PD, MS, epilepsy, TBI, tumours, psychiatric, paediatric), atlases.

</div>

## How to read this section

Pick the page that matches the gap you feel. Each is self-contained. If you're brand new, the natural sequence is **Neuroscience → Medical imaging physics → Mathematics → Statistics → Data analysis → Python → Bash → CLI commands → MATLAB** — every later page assumes the earlier ones. But for an experienced engineer arriving from outside neuroimaging, **Neuroscience → Medical imaging physics → MATLAB ↔ Python ↔ Data analysis** is usually the right shortcut.

Each page ends with a references block of canonical textbooks (with ISBN) and primary papers (with DOI). Treat the references as the next mile after the chapter.

## Recommended readings

External anchors per sub-topic. Each list is short on purpose — pick one book, one course, and one review and you will be ahead of most newcomers.

### Python

- [McKinney — *Python for Data Analysis*](https://wesmckinney.com/book/) — free online; the pandas / NumPy reference written by pandas's author.
- [VanderPlas — *Python Data Science Handbook*](https://jakevdp.github.io/PythonDataScienceHandbook/) — free online; NumPy, pandas, Matplotlib, scikit-learn in one volume.
- [Scientific Python Lectures](https://scipy-lectures.org/) — community lecture notes covering the scientific stack end to end.
- [Real Python tutorials](https://realpython.com/) — the best searchable how-to library for day-to-day Python questions.

### Bash / CLI

- [MIT "The Missing Semester of Your CS Education"](https://missing.csail.mit.edu/) — shell, editors, version control, tooling; the course every researcher wishes existed.
- [The Linux Documentation Project — Bash Guide for Beginners](https://tldp.org/LDP/Bash-Beginners-Guide/html/) — free, long-form, complete.
- [ExplainShell](https://explainshell.com/) — paste any command, get every flag explained; keep open in a tab.

### Statistics

- [Hernán & Robins — *Causal Inference: What If*](https://www.hsph.harvard.edu/miguel-hernan/causal-inference-book/) — free PDF; the modern causal-inference reference.
- [Gelman et al. — *Bayesian Data Analysis*](http://www.stat.columbia.edu/~gelman/book/) — free PDF of the third edition; the Bayesian standard.
- [StatQuest with Josh Starmer](https://www.youtube.com/@statquest) — short videos; the friendliest intuition-builder for stats and ML basics.
- [Nichols & Holmes 2002 — *Nonparametric permutation tests for functional neuroimaging*](https://doi.org/10.1002/hbm.1058) — the canonical neuroimaging-statistics review.

### Mathematics

- [MIT OCW 18.06 — Strang's *Linear Algebra*](https://ocw.mit.edu/courses/18-06-linear-algebra-spring-2010/) — the lectures, assignments, and exams behind the textbook.
- [Strang — *Introduction to Linear Algebra*](https://math.mit.edu/~gs/linearalgebra/) — the textbook itself; companion to the OCW course.
- [3Blue1Brown — Essence of Linear Algebra](https://www.3blue1brown.com/topics/linear-algebra) — short geometric videos; do these before or alongside Strang.
- [Boyd & Vandenberghe — *Convex Optimization*](https://web.stanford.edu/~boyd/cvxbook/) — free PDF; the optimisation reference behind most image-reconstruction and ML algorithms.

### Physics

- [Levitt — *Spin Dynamics*](https://www.wiley.com/en-us/Spin+Dynamics%3A+Basics+of+Nuclear+Magnetic+Resonance%2C+2nd+Edition-p-9780470511183) — the textbook for NMR / MR physics at quantum-mechanical depth.
- [Bernstein, King & Zhou — *Handbook of MRI Pulse Sequences*](https://www.elsevier.com/books/handbook-of-mri-pulse-sequences/bernstein/978-0-12-092861-3) — the encyclopaedia of pulse-sequence design.
- [ISMRM online education](https://www.ismrm.org/online-education/) — the field's own MR-physics video tracks.
- [Hennig 1999 — *Echoes — how to generate, recognize, use or avoid them*](https://doi.org/10.1002/cmr.1820030302) — the classic teaching review on echo formation.

### Neuroscience

- [Kandel et al. — *Principles of Neural Science*](https://www.mhprofessional.com/principles-of-neural-science-sixth-edition-9781259642234-usa) — the single reference work; keep on the desk.
- [Purves et al. — *Neuroscience*](https://global.oup.com/academic/product/neuroscience-9781605353807) — gentler companion, strong on systems.
- [Squire et al. — *Fundamental Neuroscience*](https://www.elsevier.com/books/fundamental-neuroscience/squire/978-0-12-385870-2) — strongest on cellular and molecular layers.
- [HarvardX "Fundamentals of Neuroscience"](https://www.edx.org/learn/neuroscience/harvard-university-fundamentals-of-neuroscience-part-1-the-electrical-properties-of-the-neuron) — free edX series; the best video intro to systems neuroscience.
- [Bassett & Sporns 2017 — *Network neuroscience*](https://doi.org/10.1038/nn.4502) — the modern-connectomics review every imaging student should read.
