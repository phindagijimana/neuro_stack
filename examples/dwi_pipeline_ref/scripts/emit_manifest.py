"""Emit a per-subject observability manifest.

Records what ran, when, with what environment, with what outcome. Pairs with
the Manifest schema defined in neuro_handbook.qc.manifest.
"""
from __future__ import annotations

import argparse
import socket
import subprocess
from datetime import datetime, timezone
from pathlib import Path

from neuro_handbook.qc import Manifest, StageRecord, write_manifest


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--subject", required=True)
    p.add_argument("--inputs", type=Path, nargs="+", required=True)
    p.add_argument("--out", type=Path, required=True)
    return p.parse_args()


def git_sha() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "--short", "HEAD"], text=True,
            cwd=Path(__file__).parent,
        ).strip()
    except (FileNotFoundError, subprocess.CalledProcessError):
        return None


def main() -> int:
    args = parse_args()
    args.out.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(timezone.utc)
    m = Manifest(
        subject_id=args.subject,
        pipeline="dwi_pipeline_ref",
        pipeline_version="0.1.0",
        git_sha=git_sha(),
        host=socket.gethostname(),
        started_at=now,
    )
    m.add_stage(StageRecord(
        name="extract_metrics", started_at=now, ended_at=now, exit_code=0,
    ))
    m.finish(success=all(p.exists() for p in args.inputs))
    write_manifest(m, args.out)
    print(f"wrote manifest -> {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
