# Common errors cheatsheet

> The bugs that bite every new neuroimager in the first six months. How they show up, what's actually wrong, how to fix, how to prevent.

Most of these errors are not in the spec or the code — they're at the seams between conventions. The viewer renders something, you accept it, and three weeks later your group statistic is wrong by 5 mm. This page is a triage list.

## Affine mismatch — image looks rotated or shifted

**How it shows up.** Two NIfTIs that should overlap (e.g. T1w and a mask) appear shifted, rotated, or flipped in the viewer; `nilearn.plotting.plot_roi(mask, bg_img=t1)` shows the mask floating off the brain.

**What's wrong.** The two files have different affines. NumPy arrays alone are not enough — the affine maps voxel indices to world (scanner) coordinates. If you resample by index without going through the affine, you're stacking two different worlds.

**Fix.** Resample one to the other through the affine: `nilearn.image.resample_to_img(mask, t1, interpolation="nearest")`. Never resample masks with linear interpolation.

**Prevent.** Always check `img.affine` (or `nib.aff2axcodes(img.affine)`) before assuming two images share a grid. See [Fundamentals → Coordinate systems](../fundamentals/coordinate-systems.md).

## Voxel-to-world vs world-to-voxel — RAS+ / LPS / qform vs sform

**How it shows up.** Coordinates from a FreeSurfer label come out in the wrong hemisphere when overlaid on an SPM result. Or: a clicked MNI coordinate (e.g. `[-42, 18, 24]`) lands on the wrong side.

**What's wrong.** NIfTI uses RAS+ (right, anterior, superior positive); DICOM and many surgical systems use LPS. A NIfTI also carries *two* potential transforms — `qform` and `sform` — and tools disagree about which to use.

**Fix.** Flip the first two axes (`x → -x, y → -y`) to convert RAS↔LPS. For NIfTI, prefer `sform` when both exist (it represents post-acquisition alignment); check with `img.header.get_sform()` and `get_qform()`.

**Prevent.** Pick one convention per project (RAS+ is the safest for Python tooling) and convert at the boundary. Cross-link: [Fundamentals → File formats](../fundamentals/file-formats.md).

## Slice-timing direction wrong

**How it shows up.** Task fMRI activation maps look smeared along the z-axis, or the HRF peak in a single voxel is offset by ~1 TR.

**What's wrong.** Your slice-timing correction assumed *ascending* (1, 2, 3, …) but the scanner used *interleaved* (1, 3, 5, …, 2, 4, 6, …) — or descending. The order is in the JSON sidecar as `SliceTiming` (an array of times per slice) — *use it*, don't guess.

**Fix.** Pass `SliceTiming` directly to fMRIPrep / SPM. If the sidecar is missing, look up the protocol; never guess from the slice index.

**Prevent.** Trust the JSON sidecar. If your converter (`dcm2niix`) didn't write `SliceTiming`, treat that as a bug, not a feature.

## Phase-encoding direction confusion — topup / eddy fails

**How it shows up.** `topup` outputs a fieldmap that warps the brain *more* rather than correcting distortion. EPI looks stretched / squashed in the anterior-posterior axis.

**What's wrong.** `PhaseEncodingDirection: j-` and `j` are opposites. A single sign flip means topup pushes voxels the wrong way.

**Fix.** Verify against the scanner protocol once per sequence. For Siemens, AP usually = `j-` and PA = `j` (but verify). Re-run topup with corrected directions.

**Prevent.** Document the PE direction per sequence in the protocol PDF. See [BIDS → Pitfalls](../bids/pitfalls.md#phase-encoding-direction).

## bvec rotation not applied after eddy / topup

**How it shows up.** Your DTI principal direction map (V1) looks correct overall, but tractography misses the corpus callosum or has crossing-fibre artefacts along the AP axis.

**What's wrong.** `eddy` and `topup` apply rigid + non-rigid corrections to volumes. The b-vectors live in voxel space and *must* be rotated by the same transform; many wrappers don't do this automatically.

**Fix.** Use `eddy`'s rotated bvecs output (`*.eddy_rotated_bvecs`), not the original ones.

**Prevent.** When in doubt, use QSIPrep — it handles this correctly.

## bvec normalisation — zeros for b=0, unit vectors otherwise

**How it shows up.** Tensor fit fails or returns NaNs; FA map is all zeros in some voxels.

**What's wrong.** Non-zero bvecs must be unit length (norm = 1). The b=0 (non-diffusion-weighted) volumes should have bvec `[0, 0, 0]` and bval `0`. Tools differ in how they handle near-unit vectors (`0.9999` vs `1.0001`).

**Fix.** Normalise non-b0 vectors; force b0 vectors to exactly `[0, 0, 0]`. `dipy.core.gradients.gradient_table` will validate.

**Prevent.** Use a converter (`dcm2niix`) that produces clean `.bvec` / `.bval` files and check norms in your QC step.

## JSON sidecar missing — BIDS validator complains

**How it shows up.** `bids-validator` errors with "Missing required field" or "Sidecar not found". Or: a BIDS app crashes with an unhelpful `KeyError: 'RepetitionTime'`.

**What's wrong.** The sidecar JSON next to every `.nii.gz` is mandatory for many fields (`RepetitionTime`, `EchoTime`, `TaskName` for BOLD, `PhaseEncodingDirection` for fieldmaps).

**Fix.** Re-run `dcm2niix` if you have the DICOMs; otherwise write the sidecar by hand from the protocol.

**Prevent.** Don't delete sidecars to "clean up". They are the data.

## Defacing destroys downstream surface reconstruction

**How it shows up.** FreeSurfer's `recon-all` errors out at `mri_em_register` or produces wildly wrong surface meshes around the orbits / cerebellum.

**What's wrong.** Aggressive defacing tools (e.g. older `pydeface`) clip into the cerebellum or orbitofrontal cortex.

**Fix.** Use `mri_deface` or modern `afni_refacer` with a conservative mask, and *always* QC the defaced volume.

**Prevent.** Compare the defaced T1 against the raw T1 in three orthogonal slices before releasing the dataset.

## FreeSurfer subject ID mismatch

**How it shows up.** `recon-all` outputs land in the wrong subject folder, or a downstream tool can't find `lh.aparc.annot`.

**What's wrong.** You ran `recon-all -s sub-001 ...` then later `-s sub-1` — FreeSurfer treats them as different subjects.

**Fix.** Symlink or re-run with the canonical ID.

**Prevent.** Mirror the BIDS subject label exactly: `sub-001` everywhere.

## SUBJECTS_DIR not set

**How it shows up.** `recon-all` writes to the wrong place; `mris_convert` says "subject not found"; visualisation tools (Freeview) can't find surfaces.

**What's wrong.** `SUBJECTS_DIR` defaults to FreeSurfer's `$FREESURFER_HOME/subjects` — usually not where you want.

**Fix.** `export SUBJECTS_DIR=/path/to/derivatives/freesurfer` in your shell or job script.

**Prevent.** Set it in every batch submission and every notebook. Treat it like `PATH`.

## Python pickle of NIfTI — don't

**How it shows up.** You pickle a NumPy array from `img.get_fdata()` for "speed". A year later, no one knows what the affine was. Or: you pickle the `Nifti1Image` itself, and reloading on a different Python version segfaults.

**What's wrong.** Pickle is not a data format — it's a Python-version-bound serialisation. NIfTI is the source of truth.

**Fix.** Save with `nib.save(img, "out.nii.gz")`. If you want to cache, cache the array *and* the affine in `.npz` — but prefer NIfTI.

**Prevent.** No pickled NIfTIs in code review.

## Off-by-one slice indexing — z=0 is bottom or top?

**How it shows up.** Your "middle axial slice" is empty, or shows the neck instead of the brain.

**What's wrong.** Depending on viewer / orientation, `data[:, :, 0]` may be the most inferior or most superior slice. `imshow` flips y by default.

**Fix.** Always call `nib.as_closest_canonical(img)` first; then `data[:, :, data.shape[2] // 2]` is the middle in RAS.

**Prevent.** Document orientation per file in your QC pipeline.

## Image / mask shape mismatch

**How it shows up.** `mask * image` raises a broadcast error, or worse, silently produces garbage because shapes happen to be broadcast-compatible.

**What's wrong.** The mask was resampled at a different resolution or to a different field of view.

**Fix.** `nilearn.image.resample_to_img(mask, image, interpolation="nearest")`.

**Prevent.** Assert `mask.shape == image.shape` and `np.allclose(mask.affine, image.affine)` at the top of every script.

## Wrong intensity normalisation — fMRI scaled like structural

**How it shows up.** A model trained on T1w MPRAGE behaves bizarrely on BOLD; or fMRI signal change values come out in the millions.

**What's wrong.** Structural MRI is often z-scored or min-max scaled per volume. fMRI signal is usually expressed as percent signal change (PSC) relative to the baseline mean.

**Fix.** Match the normalisation to the modality. PSC for fMRI; z-score per subject for structural ML inputs.

**Prevent.** Codify normalisation per modality in your dataloader; don't apply a global `StandardScaler` blindly.

## Skull-stripping too aggressive vs too lax

**How it shows up.** Cortex is clipped (too aggressive) or large chunks of dura / muscle remain (too lax). Downstream surface reconstruction fails or volume measurements are biased.

**What's wrong.** BET defaults rarely fit clinical or paediatric data. SynthStrip, HD-BET, and antsBrainExtraction generalise better but still need QC.

**Fix.** Use SynthStrip or HD-BET as a first pass; visually inspect every subject; tune the threshold.

**Prevent.** Build a 3-slice QC sheet per subject as part of preprocessing.

## Registration with wrong cost function

**How it shows up.** Cross-modal alignment (T1↔BOLD, T1↔CT) looks decent but small deep-grey structures (thalamus, basal ganglia) are misregistered by 1-2 mm.

**What's wrong.** **NCC** (normalised cross-correlation) assumes linear intensity relationship — fine for intra-modal (T1↔T1) but wrong for cross-modal. **NMI** (normalised mutual information) handles arbitrary intensity relationships and is the cross-modal default.

**Fix.** Use NMI for any cross-modal registration; NCC or LCC for intra-modal.

**Prevent.** Default to NMI when modalities differ. ANTs `antsRegistration` lets you specify per-stage.

## Atlas in wrong space — MNI152NLin2009cAsym vs MNI152NLin6Asym

**How it shows up.** You compute network-level fMRI features using a Schaefer atlas; results don't replicate against the published value.

**What's wrong.** "MNI" is a family. fMRIPrep ≥ 20 default is `MNI152NLin2009cAsym`. FSL / older studies use `MNI152NLin6Asym` (FSL's `MNI152_T1_2mm.nii.gz`). The templates differ by ~3-5 mm in some regions.

**Fix.** Resample the atlas to the same template as your data, or warp your data to the atlas's template. TemplateFlow makes both available with explicit names.

**Prevent.** Always log the template name and version. "MNI space" is not specific enough.

## Censoring vs scrubbing in fMRI — using both

**How it shows up.** Your motion-corrected timecourse has too few usable volumes; nuisance regression is over-aggressive.

**What's wrong.** **Censoring** (also called scrubbing) removes high-motion volumes from regression. **Scrubbing** in the original [Power 2012](https://doi.org/10.1016/j.neuroimage.2011.10.018) sense is the same operation. If you apply both a censoring regressor *and* drop frames, you're double-counting.

**Fix.** Pick one strategy (typically: spike regressors at FD > 0.5 mm) and report the chosen threshold and number of censored volumes per subject.

**Prevent.** Use a single pipeline (e.g. XCP-D) that has one canonical scrubbing operation.

## DTI: motion correction that makes b-vectors meaningless

**How it shows up.** Tractography looks plausible but FA in the corpus callosum is implausibly low; quantitative diffusion metrics don't replicate.

**What's wrong.** Naive rigid motion correction rotates the volumes; the b-vectors are no longer aligned with the actual diffusion-encoding direction.

**Fix.** Use eddy with `--repol` (outlier replacement) and use rotated b-vectors. See bvec rotation entry above.

**Prevent.** Use QSIPrep.

## Eddy outliers not reported in supplement

**How it shows up.** Reviewer asks "how many outlier slices did eddy detect?" and you don't know.

**What's wrong.** `eddy_quad` produces per-subject QC PDFs. Not reporting them is a transparency gap.

**Fix.** Run `eddy_quad` and `eddy_squad`; include median/range of outlier slices in the supplement.

**Prevent.** Make `eddy_quad` a mandatory step in your QSIPrep wrapper.

!!! tip "Beginner takeaway"
    Nine of every ten "weird" results trace to one of three causes: a wrong affine, a wrong sidecar, or a wrong template. Check those first, always.

## Triage table — if you see X, check Y first

| Symptom | Check first |
|---|---|
| Two images don't overlap in the viewer | `img.affine` and `aff2axcodes` on both |
| Mask "floats" off the brain | Resample mask to image through affine; nearest-neighbour |
| Coordinates land on wrong hemisphere | RAS vs LPS — flip x, y signs |
| BIDS validator complains "missing field" | JSON sidecar next to the `.nii.gz` |
| Task fMRI activation smeared along z | `SliceTiming` array in sidecar |
| EPI distortion correction makes it worse | `PhaseEncodingDirection` sign |
| DTI principal direction wrong | Rotated bvecs from eddy |
| FA map full of NaNs | bvec norms; b0 must be `[0,0,0]` |
| recon-all crashes mid-run | Defacing too aggressive; `SUBJECTS_DIR` not set |
| FreeSurfer outputs in wrong folder | Subject ID mismatch with BIDS |
| Atlas-based results don't replicate | Template version — `2009cAsym` vs `6Asym` |
| fMRI signal in the millions | Normalisation — needs PSC or z-score |
| Cross-modal registration off in deep grey | Cost function — use NMI not NCC |
| Tractography misses corpus callosum | Unrotated bvecs after eddy |
| Too few usable fMRI volumes | Double-counted censoring + scrubbing |
| Cortex clipped in skull-strip | Threshold too aggressive; try SynthStrip |
| Pickled array no one can decode | Re-derive from NIfTI — pickle is not a format |

## Where to next

- [Your first NIfTI](first-nifti.md) — the basic load / inspect / plot loop where most of these errors first surface.
- [Fundamentals → Coordinate systems](../fundamentals/coordinate-systems.md) — the formal treatment of RAS, LPS, qform, sform.
- [Fundamentals → File formats](../fundamentals/file-formats.md) — NIfTI, JSON sidecars, BIDS layout.
- [BIDS → Pitfalls](../bids/pitfalls.md) — the same spirit, but specifically at the BIDS layer.

## References

1. **Power JD, Barnes KA, Snyder AZ, et al.** Spurious but systematic correlations in functional connectivity MRI networks arise from subject motion. *NeuroImage.* 2012;59(3):2142-2154. [doi:10.1016/j.neuroimage.2011.10.018](https://doi.org/10.1016/j.neuroimage.2011.10.018)
2. **Andersson JLR, Sotiropoulos SN.** An integrated approach to correction for off-resonance effects and subject movement in diffusion MR imaging. *NeuroImage.* 2016;125:1063-1078. [doi:10.1016/j.neuroimage.2015.10.019](https://doi.org/10.1016/j.neuroimage.2015.10.019) — eddy.
3. **Esteban O, Markiewicz CJ, Blair RW, et al.** fMRIPrep: a robust preprocessing pipeline for functional MRI. *Nat Methods.* 2019;16:111-116. [doi:10.1038/s41592-018-0235-4](https://doi.org/10.1038/s41592-018-0235-4)
4. **Cieslak M, Cook PA, He X, et al.** QSIPrep: an integrative platform for preprocessing and reconstructing diffusion MRI data. *Nat Methods.* 2021;18:775-778. [doi:10.1038/s41592-021-01185-5](https://doi.org/10.1038/s41592-021-01185-5)
5. **Ciric R, Wolf DH, Power JD, et al.** Benchmarking of participant-level confound regression strategies for the control of motion artifact in studies of functional connectivity. *NeuroImage.* 2017;154:174-187. [doi:10.1016/j.neuroimage.2017.03.020](https://doi.org/10.1016/j.neuroimage.2017.03.020)
