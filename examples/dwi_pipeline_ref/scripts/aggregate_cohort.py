"""Aggregate per-subject Parquet rows into one cohort table."""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--inputs", type=Path, nargs="+", required=True)
    p.add_argument("--out", type=Path, required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    df = pd.concat([pd.read_parquet(p) for p in args.inputs], ignore_index=True)
    df.to_parquet(args.out, index=False)
    print(f"wrote {args.out} with {len(df)} subjects, {df.shape[1]} columns")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
