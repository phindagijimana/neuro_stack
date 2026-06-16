# HPC and Slurm

> The scheduler every academic neuroimaging shop uses, and the parts you actually need to know.

## Mental model

Slurm is a queue. You submit a job (a script + a resource request); Slurm finds nodes that match; your script runs; the output goes into a log file. Everything else is variations.

## A minimal job

```bash
#!/bin/bash
#SBATCH --job-name=qsiprep_sub001
#SBATCH --partition=cpu
#SBATCH --cpus-per-task=8
#SBATCH --mem=32G
#SBATCH --time=24:00:00
#SBATCH --output=logs/%x_%j.out

set -euo pipefail
apptainer run qsiprep.sif /data /out participant --participant-label 001
```

Submit: `sbatch jobs/qsiprep_sub001.sh`.
Status: `squeue -u $USER`.
Cancel: `scancel <jobid>`.

## Array jobs — your friend

Don't write 100 sbatch scripts; write one and submit it as an array:

```bash
#SBATCH --array=1-100%20

subjects=( $(cat subjects.txt) )
sub=${subjects[$SLURM_ARRAY_TASK_ID - 1]}
apptainer run qsiprep.sif /data /out participant --participant-label $sub
```

`%20` limits concurrent tasks (be a good citizen on a shared cluster).

## GPU jobs

```bash
#SBATCH --partition=gpu
#SBATCH --gres=gpu:1
#SBATCH --cpus-per-task=8
#SBATCH --mem=64G
```

Specify the GPU type when it matters: `--gres=gpu:a100:1`. Otherwise the scheduler picks whatever's free.

## Sizing requests honestly

`seff <jobid>` after a job finishes shows actual CPU efficiency and peak memory. Use it to right-size future runs:

```text
$ seff 12345
Job ID: 12345
State: COMPLETED (exit code 0)
Cores: 8
CPU Utilized: 02:14:30
CPU Efficiency: 18.7% of 12:00:00 core-walltime
Memory Utilized: 12.3 GB
Memory Efficiency: 38.4% of 32.00 GB
```

18% CPU efficiency means you asked for 8 cores and used ~1.5. Drop to 2 cores, queue faster, free up resources for others.

## Etiquette

- Use `--mem` and `--time` as low as you reliably can.
- Don't run heavy work on the login node. Use `srun --pty bash` for interactive sessions.
- Cap concurrent array tasks (`%N`) so you don't monopolise the queue.
- Email yourself on failure: `--mail-type=FAIL --mail-user=you@example.com`.

## Exemplar — fMRIPrep on Slurm + Apptainer

A production-grade template for running a BIDS app under Slurm with a containerised image and a bound-in FreeSurfer license. Read the [Slurm docs](https://slurm.schedmd.com/sbatch.html) and the [Apptainer guide](https://apptainer.org/docs/user/latest/) for the canonical reference.

```bash
#!/usr/bin/env bash
# Submit with: sbatch run_fmriprep.sh
# Reads BIDS + writes derivatives. Pin the container tag; never use :latest.

#SBATCH --job-name=fmriprep
#SBATCH --partition=cpu        # set your partition (sinfo -s lists them)
#SBATCH --time=24:00:00        # walltime cap
#SBATCH --cpus-per-task=8      # threads fMRIPrep / FSL / FreeSurfer can use
#SBATCH --mem=32G              # 32 GB; raise if you see OOM kills
#SBATCH --output=logs/fmriprep_%j.out
#SBATCH --error=logs/fmriprep_%j.err

set -euo pipefail   # -e: exit on error; -u: unset = error; pipefail = strict pipes

# --- inputs you edit ---
BIDS=/path/to/bids                                # raw BIDS dataset
DERIV=/path/to/derivatives                        # where fMRIPrep writes
WORK=${SCRATCH:-/tmp}/${USER}/fmriprep_work       # scratch, fast disk preferred
IMG=/path/to/fmriprep_24.0.0.sif                  # pre-pulled .sif image
FS_LICENSE=/path/to/freesurfer/license.txt        # FreeSurfer license file
SUB="${1:?usage: sbatch run_fmriprep.sh <subject-label>}"

mkdir -p "$DERIV" "$WORK"
test -f "$IMG"        || { echo "missing image: $IMG"; exit 1; }
test -f "$FS_LICENSE" || { echo "missing FS license: $FS_LICENSE"; exit 1; }

apptainer run --cleanenv \
  -B "$BIDS":/data:ro \
  -B "$DERIV":/out \
  -B "$WORK":/work \
  -B "$FS_LICENSE":/license.txt:ro \
  "$IMG" \
    /data /out participant \
    --participant-label "$SUB" \
    --work-dir /work \
    --fs-license-file /license.txt \
    --nthreads "$SLURM_CPUS_PER_TASK" --mem-mb 30000 \
    --skip-bids-validation        # disable if you already ran the validator separately
```

Three details that make this a real template, not a toy:

- **`set -euo pipefail`** at the top — silent failures are the most expensive thing on HPC.
- **`-B host:container:ro`** read-only bind for inputs and the license — defends against accidental writes into raw data.
- **`SLURM_CPUS_PER_TASK`** propagated into `--nthreads` — keeps the container's parallelism aligned with what Slurm allocated.

Drop in the equivalent block for any other BIDS app (QSIPrep, MRIQC, sMRIPrep) by swapping the image and the CLI; the rest is identical. The [Apptainer manual](https://apptainer.org/docs/user/latest/) covers binds, GPU passthrough, and overlay images in depth.

## Where to next

[Cloud](cloud.md) — when HPC isn't the right substrate.
