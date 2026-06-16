# Containers (Docker, Apptainer)

> Every modern neuroimaging pipeline ships as a container. Knowing how to use them is non-negotiable.

## Why containers won

Neuroimaging tools have ugly dependencies: specific Python versions, specific FreeSurfer or FSL versions, specific glibc compatibility. Installing them by hand on every machine wastes days. **Containers** ship a frozen filesystem + binaries that runs identically everywhere.

## Docker on a laptop ([docs here](https://docs.docker.com/))

```bash
# Pull a BIDS app image
docker pull nipreps/fmriprep:24.0.0

# Run it on a BIDS dataset
docker run --rm \
  -v $PWD/bids:/data:ro \
  -v $PWD/derivatives:/out \
  -v $PWD/fs_license.txt:/opt/freesurfer/license.txt:ro \
  nipreps/fmriprep:24.0.0 \
  /data /out participant --participant-label 001
```

`-v host:container` mounts a host path into the container. `--rm` deletes the container after exit; the image remains.

## Apptainer on HPC ([docs here](https://apptainer.org/docs/user/latest/))

HPC sites don't allow Docker (it needs root). **Apptainer** (formerly Singularity) is the rootless alternative:

```bash
# Build a SIF from a Docker image
apptainer build fmriprep_24.0.0.sif docker://nipreps/fmriprep:24.0.0

# Run it
apptainer run \
  -B $PWD/bids:/data \
  -B $PWD/derivatives:/out \
  -B $PWD/fs_license.txt:/opt/freesurfer/license.txt \
  fmriprep_24.0.0.sif \
  /data /out participant --participant-label 001
```

A SIF is a single file; copy it to the cluster once, point Slurm at it.

## Image tagging discipline

- **Always tag explicitly** (`fmriprep:24.0.0`, not `fmriprep:latest`). `latest` is not reproducible.
- **Pin the digest** for high-stakes work: `nipreps/fmriprep@sha256:...`.
- **Record the tag** in your output manifest (the `Manifest` class in this repo has a `container_digest` field for exactly this).

## Building your own

A minimal `Dockerfile` for a Python project:

```dockerfile
FROM python:3.12-slim
RUN apt-get update && apt-get install -y --no-install-recommends \
    git build-essential && rm -rf /var/lib/apt/lists/*
WORKDIR /app
COPY pyproject.toml uv.lock ./
RUN pip install uv && uv sync --frozen --no-dev
COPY src/ src/
ENTRYPOINT ["uv", "run", "my_pipeline"]
```

For BIDS apps, follow the [BIDS Apps template](https://github.com/bids-apps/bids-apps.github.io) (spec [here](https://bids-apps.neuroimaging.io)) which prescribes the CLI shape and entrypoint.

## Where to next

[HPC and Slurm](hpc-slurm.md) — the scheduler that runs your container at scale.
