"""Extract per-subject DTI / connectome metrics into a Parquet row.

Reads QSIRecon outputs (FA / MD maps, DK connectome) and writes a single-row
Parquet file with the cohort-level features. Real code would inspect the BIDS
derivatives directory; this template emits a synthetic row so the pipeline
runs without real data.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--recon", type=Path, required=True,
                   help="Path to QSIRecon output for one subject")
    p.add_argument("--out", type=Path, required=True,
                   help="Parquet file to write")
    return p.parse_args()


def extract_real(recon: Path) -> dict:
    """Read FA / MD / connectome from a real QSIRecon output tree."""
    # Replace with actual nibabel + numpy code on your derivatives layout.
    raise NotImplementedError("Wire up to your QSIRecon layout")


def extract_synth(subject_id: str) -> dict:
    """Synthetic features so the pipeline runs without real data."""
    rng = np.random.default_rng(hash(subject_id) % (2**32))
    return {
        "subject_id":       subject_id,
        "fa_mean":          float(rng.uniform(0.30, 0.50)),
        "md_mean_mm2_s":    float(rng.uniform(0.6e-3, 0.9e-3)),
        "n_streamlines":    int(rng.integers(2_000_000, 5_000_000)),
        "dk_density":       float(rng.uniform(0.10, 0.30)),
    }


def main(argv: list[str] | None = None) -> int:
    args = parse_args() if argv is None else parse_args()
    subject_id = args.recon.name
    args.out.parent.mkdir(parents=True, exist_ok=True)

    try:
        row = extract_real(args.recon)
    except (NotImplementedError, FileNotFoundError):
        row = extract_synth(subject_id)

    pd.DataFrame([row]).to_parquet(args.out, index=False)
    print(f"wrote {args.out} for {subject_id}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
