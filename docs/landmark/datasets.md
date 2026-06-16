# Reference datasets

> The public datasets that anchor most modern neuroimaging method development, with full citations and access notes.

## Adult, healthy

| Dataset | Description | Size | Access | Reference |
|---|---|---|---|---|
| **HCP Young Adult** | 3T multimodal, behavioural + genetic | ~1100 | Free + DUA | [Van Essen et al., 2013](https://doi.org/10.1016/j.neuroimage.2013.05.041)[^1] |
| **HCP Lifespan** | Same protocol across age | ~1000+ | Free + DUA | [Bookheimer et al., 2019](https://doi.org/10.1016/j.neuroimage.2018.10.009)[^2] |
| **UK Biobank** | Population-scale multimodal | 100 000+ | Application + fee | [Miller et al., 2016](https://doi.org/10.1038/nn.4393)[^3] |
| **OASIS-3** | Aging, longitudinal | ~1000 | Free + DUA | [LaMontagne et al., 2019](https://doi.org/10.1101/2019.12.13.19014902)[^4] |
| **Cam-CAN** | Lifespan, 18–88 yr | ~700 | Open registration | [Shafto et al., 2014](https://doi.org/10.1186/s12883-014-0204-1)[^5] |
| **MICA-MICs** | High-resolution structural + functional | ~50 | Open | [Royer et al., 2022](https://doi.org/10.1038/s41597-022-01682-y)[^6] |

## Developmental

| Dataset | Description | Size | Reference |
|---|---|---|---|
| **ABCD** | Adolescent longitudinal, 10-year follow-up | 12 000+ | [Casey et al., 2018](https://doi.org/10.1016/j.dcn.2018.03.001)[^7] |
| **HCP-Development** | 5–21 years | ~1500 | [Somerville et al., 2018](https://doi.org/10.1016/j.neuroimage.2018.04.038)[^8] |
| **dHCP** | Neonatal | ~800 | [Edwards et al., 2022](https://doi.org/10.1016/j.neuroimage.2022.119085)[^9] |

## Clinical

| Dataset | Description | Size | Reference |
|---|---|---|---|
| **ADNI** | Alzheimer's longitudinal | ~2000 | [Jack et al., 2008](https://doi.org/10.1002/jmri.21049)[^10] |
| **PPMI** | Parkinson's longitudinal | ~1000+ | [Marek et al., 2011](https://doi.org/10.1016/j.pneurobio.2011.09.005)[^11] |
| **ENIGMA cohorts** | Meta-analytic across disorders | varies | [Thompson et al., 2020](https://doi.org/10.1038/s41398-020-0705-1)[^12] |

## Open repositories

- **OpenNeuro** ([portal](https://openneuro.org), [docs](https://docs.openneuro.org)) — open BIDS datasets, versioned, browser + CLI. [Markiewicz et al., 2021](https://doi.org/10.7554/eLife.71774)[^13]. <https://openneuro.org>
- **NeuroVault** ([portal](https://neurovault.org)) — derived statistical maps and atlases. [Gorgolewski et al., 2015](https://doi.org/10.3389/fninf.2015.00008)[^14]. <https://neurovault.org>
- **OpenfMRI** (legacy) — preceded OpenNeuro; most datasets migrated.

## Access patterns

Three tiers:

- **Open** — clone from OpenNeuro [here](https://openneuro.org), no application needed. Start your method development here.
- **Data-use agreement (DUA)** — HCP ([portal](https://www.humanconnectome.org)), OASIS ([portal](https://www.oasis-brains.org)). Sign a form, get credentials, download via AWS S3 or `aws s3 sync`.
- **Application + IRB** — UK Biobank ([portal](https://www.ukbiobank.ac.uk)), ABCD ([portal](https://abcdstudy.org)). Months of paperwork. Worth it for production-scale work.

## Why use a reference dataset

- **Pipeline validation.** If your pipeline produces sensible numbers on HCP, it's probably correct.
- **Generalisation tests.** Train on your cohort, test on HCP, report both.
- **Baseline comparisons.** Most methods papers benchmark on these datasets; you should too.

## References

[^1]: Van Essen DC, Smith SM, Barch DM, Behrens TEJ, Yacoub E, Ugurbil K. The WU-Minn Human Connectome Project: an overview. *NeuroImage.* 2013;80:62-79.
[^2]: Bookheimer SY, Salat DH, Terpstra M, et al. The Lifespan Human Connectome Project in Aging. *NeuroImage.* 2019;185:335-348.
[^3]: Miller KL, Alfaro-Almagro F, Bangerter NK, et al. Multimodal population brain imaging in the UK Biobank. *Nat Neurosci.* 2016;19(11):1523-1536.
[^4]: LaMontagne PJ, Benzinger TLS, Morris JC, et al. OASIS-3: longitudinal neuroimaging, clinical, and cognitive dataset for normal aging and Alzheimer disease. *medRxiv.* 2019.
[^5]: Shafto MA, Tyler LK, Dixon M, et al. The Cambridge Centre for Ageing and Neuroscience (Cam-CAN) study protocol. *BMC Neurol.* 2014;14:204.
[^6]: Royer J, Rodríguez-Cruces R, Tavakol S, et al. An open MRI dataset for multiscale neuroscience. *Sci Data.* 2022;9:569.
[^7]: Casey BJ, Cannonier T, Conley MI, et al. The Adolescent Brain Cognitive Development (ABCD) study. *Dev Cogn Neurosci.* 2018;32:43-54.
[^8]: Somerville LH, Bookheimer SY, Buckner RL, et al. The Lifespan Human Connectome Project in Development. *NeuroImage.* 2018;183:456-468.
[^9]: Edwards AD, Rueckert D, Smith SM, et al. The Developing Human Connectome Project Neonatal Data Release. *NeuroImage.* 2022;253:119085.
[^10]: Jack CR Jr, Bernstein MA, Fox NC, et al. The Alzheimer's Disease Neuroimaging Initiative (ADNI): MRI methods. *J Magn Reson Imaging.* 2008;27(4):685-691.
[^11]: Marek K, Jennings D, Lasch S, et al. The Parkinson Progression Marker Initiative (PPMI). *Prog Neurobiol.* 2011;95(4):629-635.
[^12]: Thompson PM, Jahanshad N, Ching CRK, et al. ENIGMA and global neuroscience: a decade of large-scale studies. *Transl Psychiatry.* 2020;10:100.
[^13]: Markiewicz CJ, Gorgolewski KJ, Feingold F, et al. The OpenNeuro resource for sharing of neuroscience data. *eLife.* 2021;10:e71774.
[^14]: Gorgolewski KJ, Varoquaux G, Rivera G, et al. NeuroVault.org: a web-based repository for collecting and sharing unthresholded statistical maps of the human brain. *Front Neuroinform.* 2015;9:8.

## Where to next

[Major pipelines](pipelines.md) — the tools that emit the derivatives these datasets ship with.
