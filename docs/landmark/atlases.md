# Atlases and templates

> The standard parcellations and template spaces you'll see in papers and pipelines, with primary references.

## Cortical parcellations

| Atlas | Granularity | Source | Reference |
|---|---|---|---|
| **Desikan-Killiany (DK)** | 68 regions | FreeSurfer; gyral-based | [Desikan et al., 2006](https://doi.org/10.1016/j.neuroimage.2006.01.021)[^dk] |
| **Destrieux** (`aparc.a2009s`) | 148 regions | FreeSurfer; finer gyral | [Destrieux et al., 2010](https://doi.org/10.1016/j.neuroimage.2010.06.010)[^destrieux] |
| **HCP-MMP1 (Glasser)** | 360 regions | HCP multi-modal | [Glasser et al., 2016](https://doi.org/10.1038/nature18933)[^glasser] |
| **Schaefer** | 100 / 200 / 400 / 600 / 800 / 1000 | Functional rsfMRI | [Schaefer et al., 2018](https://doi.org/10.1093/cercor/bhx179)[^schaefer] |
| **AAL** | 116 regions | SPM volumetric | [Tzourio-Mazoyer et al., 2002](https://doi.org/10.1006/nimg.2001.0978)[^aal] |
| **Yeo 7 / 17 networks** | Resting-state networks | Functional | [Yeo et al., 2011](https://doi.org/10.1152/jn.00338.2011)[^yeo] |
| **Power-264** | 264 nodes | Meta-analytic | [Power et al., 2011](https://doi.org/10.1016/j.neuron.2011.09.006)[^power] |

## Subcortical parcellations

- **FreeSurfer `aseg`** — 16+ subcortical structures. The default. [Fischl et al., 2002](https://doi.org/10.1016/S0896-6273(02)00569-X)[^aseg].
- **Tian S1–S4** — fine-grained subcortical, designed to pair with Schaefer cortex. [Tian et al., 2020](https://doi.org/10.1038/s41593-020-00711-6)[^tian].
- **CIT168** — high-resolution subcortical atlas. [Pauli et al., 2018](https://doi.org/10.1038/sdata.2018.63)[^cit168].

## White-matter atlases

- **JHU ICBM-DTI-81** — white-matter tracts; volumetric default. [Mori et al., 2008](https://doi.org/10.1016/j.neuroimage.2007.07.053)[^jhu].
- **HCP1065 tractogram atlas** — major bundles defined on HCP. [Yeh et al., 2018](https://doi.org/10.1016/j.neuroimage.2018.05.027)[^hcp1065].
- **TractSeg atlas** — DL-defined bundles; current state-of-the-art for fast bundle segmentation. [Wasserthal et al., 2018](https://doi.org/10.1016/j.neuroimage.2018.07.070)[^tractseg].

## Standard template spaces

| Template | Space | When | Reference |
|---|---|---|---|
| **MNI152NLin2009cAsym** | Volumetric | fMRIPrep / QSIPrep default | [Fonov et al., 2011](https://doi.org/10.1016/j.neuroimage.2010.07.033)[^fonov] |
| **MNI152NLin6Asym** | Volumetric | FSL legacy default | [Grabner et al., 2006](https://doi.org/10.1007/11866565_8)[^grabner] |
| **fsaverage** | Surface | FreeSurfer; 163 842 vertices / hemi | [Fischl et al., 1999](https://doi.org/10.1002/(SICI)1097-0193(1999)8:4%3C272::AID-HBM10%3E3.0.CO;2-4)[^fsaverage] |
| **fsLR (32k_fs_LR)** | Surface | HCP default; 32 492 vertices / hemi | [Van Essen et al., 2012](https://doi.org/10.1093/cercor/bhr291)[^fslr] |
| **Colin27** | Single subject | Legacy high-res | [Holmes et al., 1998](https://doi.org/10.1097/00004728-199803000-00032)[^colin] |

Different MNI templates are **not interchangeable**. Always record which one your derivatives are in.

## TemplateFlow

[TemplateFlow](https://www.templateflow.org) (full docs and template browser [here](https://www.templateflow.org/browse/)) distributes versioned templates as a pip-installable archive. Use it instead of bundling templates in your repo. [Ciric et al., 2022](https://doi.org/10.1038/s41592-022-01681-2)[^templateflow].

```python
from templateflow import api as tflow
img = tflow.get("MNI152NLin2009cAsym", resolution=1, desc="brain", suffix="T1w")
```

Templates have version numbers; pin them in your manifest alongside container digests.

## Naming derivatives accordingly

When you write a derivative into MNI space, the filename should carry the `space-` entity:

```text
sub-001_space-MNI152NLin2009cAsym_desc-preproc_T1w.nii.gz
```

This is what makes BIDS-derivatives self-describing.

## References

[^dk]: Desikan RS, Ségonne F, Fischl B, et al. An automated labeling system for subdividing the human cerebral cortex on MRI scans into gyral based regions of interest. *NeuroImage.* 2006;31(3):968-980.
[^destrieux]: Destrieux C, Fischl B, Dale A, Halgren E. Automatic parcellation of human cortical gyri and sulci using standard anatomical nomenclature. *NeuroImage.* 2010;53(1):1-15.
[^glasser]: Glasser MF, Coalson TS, Robinson EC, et al. A multi-modal parcellation of human cerebral cortex. *Nature.* 2016;536(7615):171-178.
[^schaefer]: Schaefer A, Kong R, Gordon EM, et al. Local-global parcellation of the human cerebral cortex from intrinsic functional connectivity MRI. *Cereb Cortex.* 2018;28(9):3095-3114.
[^aal]: Tzourio-Mazoyer N, Landeau B, Papathanassiou D, et al. Automated anatomical labeling of activations in SPM using a macroscopic anatomical parcellation of the MNI MRI single-subject brain. *NeuroImage.* 2002;15(1):273-289.
[^yeo]: Yeo BTT, Krienen FM, Sepulcre J, et al. The organization of the human cerebral cortex estimated by intrinsic functional connectivity. *J Neurophysiol.* 2011;106(3):1125-1165.
[^power]: Power JD, Cohen AL, Nelson SM, et al. Functional network organization of the human brain. *Neuron.* 2011;72(4):665-678.
[^aseg]: Fischl B, Salat DH, Busa E, et al. Whole brain segmentation: automated labeling of neuroanatomical structures in the human brain. *Neuron.* 2002;33(3):341-355.
[^tian]: Tian Y, Margulies DS, Breakspear M, Zalesky A. Topographic organization of the human subcortex unveiled with functional connectivity gradients. *Nat Neurosci.* 2020;23:1421-1432.
[^cit168]: Pauli WM, Nili AN, Tyszka JM. A high-resolution probabilistic in vivo atlas of human subcortical brain nuclei. *Sci Data.* 2018;5:180063.
[^jhu]: Mori S, Oishi K, Jiang H, et al. Stereotaxic white matter atlas based on diffusion tensor imaging in an ICBM template. *NeuroImage.* 2008;40(2):570-582.
[^hcp1065]: Yeh F-C, Panesar S, Fernandes D, et al. Population-averaged atlas of the macroscale human structural connectome and its network topology. *NeuroImage.* 2018;178:57-68.
[^tractseg]: Wasserthal J, Neher P, Maier-Hein KH. TractSeg — Fast and accurate white matter tract segmentation. *NeuroImage.* 2018;183:239-253.
[^fonov]: Fonov V, Evans AC, Botteron K, et al. Unbiased average age-appropriate atlases for pediatric studies. *NeuroImage.* 2011;54(1):313-327.
[^grabner]: Grabner G, Janke AL, Budge MM, Smith D, Pruessner J, Collins DL. Symmetric atlasing and model based segmentation. *MICCAI.* 2006.
[^fsaverage]: Fischl B, Sereno MI, Tootell RBH, Dale AM. High-resolution intersubject averaging and a coordinate system for the cortical surface. *Hum Brain Mapp.* 1999;8(4):272-284.
[^fslr]: Van Essen DC, Glasser MF, Dierker DL, Harwell J, Coalson T. Parcellations and hemispheric asymmetries of human cerebral cortex analyzed on surface-based atlases. *Cereb Cortex.* 2012;22(10):2241-2262.
[^colin]: Holmes CJ, Hoge R, Collins L, Woods R, Toga AW, Evans AC. Enhancement of MR images using registration for signal averaging. *J Comput Assist Tomogr.* 1998;22(2):324-333.
[^templateflow]: Ciric R, Thompson WH, Lorenz R, et al. TemplateFlow: FAIR-sharing of multi-scale, multi-species brain models. *Nat Methods.* 2022;19(12):1568-1571.

## Where to next

That closes the Landmark work section. Loop back to the [Home page](../index.md) for an overview.
