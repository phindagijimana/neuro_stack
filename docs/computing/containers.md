# Containers (Docker, Apptainer)

> Every modern neuroimaging pipeline ships as a container. Knowing how to use them is non-negotiable.

## Why containers won

Neuroimaging tools have ugly dependencies: specific Python versions, specific FreeSurfer or FSL versions, specific glibc compatibility. Installing them by hand on every machine wastes days. **Containers** ship a frozen filesystem + binaries that runs identically everywhere.

Docker was introduced by [Merkel, 2014](https://www.linuxjournal.com/content/docker-lightweight-linux-containers-consistent-development-and-deployment), popularising OS-level virtualisation built on Linux cgroups + namespaces (which existed since ~2008 but were complicated to use directly).

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

## Apptainer vs Docker for neuroimaging on HPC

A laptop runs [Docker](https://docs.docker.com/); a cluster runs [Apptainer](https://apptainer.org/docs/user/latest/). The two are similar enough to be confusing and different enough to break your pipeline at the worst moment. This section pins down the divergences.

### Why HPC uses Apptainer (not Docker)

Docker needs a root-owned daemon (`dockerd`) and gives every container user effective root via the docker socket. No sysadmin running a multi-tenant cluster will accept that. [Apptainer](https://apptainer.org/docs/user/latest/security/security.html) runs rootless from a single binary, processes inside the container run as the calling Unix user, and an image is a single immutable `.sif` ([Singularity Image Format](https://apptainer.org/docs/user/latest/definition_files.html#sif)) file that lives on the shared filesystem. You can `cp`, `scp`, or `rsync` an SIF the same way you'd move a NIfTI. Apptainer is the [community fork](https://apptainer.org/news/community-announcement-20211130/) of Singularity after the project split from [Sylabs](https://sylabs.io/) in 2021; the two CLIs are still command-compatible.

### Mounts, paths, and environment

| Behaviour | Docker | Apptainer |
| --- | --- | --- |
| Default bind mounts | none | `$HOME`, `/tmp`, `$PWD`, and `/proc`/`/sys` |
| Add a bind | `-v host:container[:ro]` | `-B host:container[:ro]` (or `--bind`) |
| Pass environment | `-e VAR=val` (allow-list) | `--env VAR=val`; host env passed by default unless `--cleanenv` |
| User inside | typically `root` | the calling user |
| Working dir | `/` unless `WORKDIR` set | `$PWD` of the host, when it exists in the image |
| GPU passthrough | `--gpus all` (needs [NVIDIA Container Toolkit](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html)) | `--nv` |

A Docker pipeline that works on your laptop because you mounted `/data` will fail on HPC if you ran it on Apptainer expecting `/data` to magically exist — Apptainer mounts `$HOME` and `$PWD` instead. Either pass `-B /scratch/proj:/data` or refactor your scripts to use the auto-mounted paths.

### Building and pulling images

```bash
# Pull a Docker Hub / Quay image straight into an SIF (no Docker required)
apptainer build fmriprep_24.0.0.sif docker://nipreps/fmriprep:24.0.0

# Build from an .def file (Apptainer's native recipe format)
apptainer build my_tool.sif my_tool.def

# Rootless build on a cluster that exposes the fakeroot feature
apptainer build --fakeroot my_tool.sif my_tool.def
```

The recommended workflow: iterate on a `Dockerfile` locally (Docker's layer cache makes rebuilds fast), push to a registry ([Quay](https://quay.io/), [Docker Hub](https://hub.docker.com/), or [GHCR](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)), then `apptainer build` from `docker://` on the cluster on first use and cache the resulting SIF on shared storage. [NIH HPC's notes](https://hpc.nih.gov/apps/singularity.html) describe the same pattern with concrete Slurm examples.

### GPU passthrough

```bash
# Laptop
docker run --rm --gpus all nvidia/cuda:12.4.0-base-ubuntu22.04 nvidia-smi

# HPC
apptainer exec --nv fmriprep_24.0.0.sif nvidia-smi
```

`--nv` injects the host driver libraries into the container — which is why the [host driver version must be ≥ the CUDA runtime](https://docs.nvidia.com/deploy/cuda-compatibility/) inside the image. Mismatch shows up as `CUDA driver version is insufficient`.

### Common divergences and bugs

- **"Works on my laptop, fails on HPC."** You used absolute host paths inside the Docker container (`-v /Users/me/data:/data`) and didn't bind them on Apptainer. Fix: either add `-B /scratch/proj:/data` to the Apptainer call or reference `$PWD`/`$HOME` paths that Apptainer mounts automatically.
- **"Permission denied writing output."** Apptainer's image is read-only by default, and overlays aren't writable in stock builds. Write to a bind-mounted host path, or build with [`--writable-tmpfs`](https://apptainer.org/docs/user/latest/persistent_overlays.html) / `--overlay` for genuine in-container persistence.
- **"MPI hangs or segfaults."** Apptainer expects the host's [MPI](https://www.open-mpi.org/) version to match the one inside the image (the [hybrid model](https://apptainer.org/docs/user/latest/mpi.html)). Build the container against the same Open MPI / MPICH series the cluster uses, or use the bind model and inject the host's libraries.
- **"My environment variable didn't make it in."** Docker only forwards what `-e` allows; Apptainer forwards most of the host env unless you set `--cleanenv`, but it strips anything starting with `APPTAINERENV_` prefixes. Be explicit with `--env`.
- **"`docker pull` works, `apptainer build docker://` 404s."** Private registries: set `SINGULARITY_DOCKER_USERNAME` / `SINGULARITY_DOCKER_PASSWORD` (or the `APPTAINER_*` equivalents) before the build.

### Recommended workflow

1. Develop and iterate locally with [Docker](https://docs.docker.com/get-started/) — fast layer cache, `docker compose` for multi-service test rigs.
2. Tag deliberately (`myorg/tool:1.2.3`, never `latest`) and push to a registry.
3. On HPC, `apptainer build` from `docker://` once and store the SIF on shared scratch.
4. Run via Slurm with `apptainer exec --nv --bind /scratch/proj:/data ...`.
5. Record the image digest (Apptainer prints `Image SIF: sha256:...` on build) in your output manifest, exactly as you would the Docker digest.

This split — Docker for dev, Apptainer for deploy — is the path the [NeuroDesk](https://www.neurodesk.org/), [fMRIPrep](https://fmriprep.org/), and [QSIPrep](https://qsiprep.readthedocs.io/) communities all converged on.

## References

1. **Kurtzer GM, Sochat V, Bauer MW.** Singularity: scientific containers for mobility of compute. *PLOS ONE.* 2017;12(5):e0177459. [doi:10.1371/journal.pone.0177459](https://doi.org/10.1371/journal.pone.0177459)
2. **Apptainer Project.** [User guide](https://apptainer.org/docs/user/latest/) and [admin guide](https://apptainer.org/docs/admin/latest/).
3. **Sylabs / Apptainer community announcement, 2021** — [renaming Singularity to Apptainer](https://apptainer.org/news/community-announcement-20211130/) and joining the Linux Foundation.
4. **Docker Inc.** [Docker docs](https://docs.docker.com/) — engine, build, and Compose.
4a. **Merkel D.** Docker: lightweight Linux containers for consistent development and deployment. *Linux Journal.* 2014;239:2. [Free article](https://www.linuxjournal.com/content/docker-lightweight-linux-containers-consistent-development-and-deployment) — the introductory Docker paper.
5. **NVIDIA.** [Container Toolkit install guide](https://docs.nvidia.com/datacenter/cloud-native/container-toolkit/latest/install-guide.html) and [CUDA compatibility](https://docs.nvidia.com/deploy/cuda-compatibility/).
6. **NIH HPC.** [Singularity/Apptainer on Biowulf](https://hpc.nih.gov/apps/singularity.html) — concrete cluster-side examples.
7. **BIDS Apps.** [Specification](https://bids-apps.neuroimaging.io) and [templates](https://github.com/bids-apps/bids-apps.github.io).

## Where to next

[HPC and Slurm](hpc-slurm.md) — the scheduler that runs your container at scale.
