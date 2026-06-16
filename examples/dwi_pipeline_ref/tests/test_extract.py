"""Smoke tests for the reference pipeline helpers."""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

HERE = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(HERE / "scripts"))

import aggregate_cohort  # noqa: E402
import extract_metrics  # noqa: E402


def test_extract_synth_row_shape():
    row = extract_metrics.extract_synth("sub-001")
    expected = {"subject_id", "fa_mean", "md_mean_mm2_s",
                "n_streamlines", "dk_density"}
    assert expected <= set(row.keys())
    assert 0 < row["fa_mean"] < 1


def test_extract_synth_is_deterministic():
    a = extract_metrics.extract_synth("sub-001")
    b = extract_metrics.extract_synth("sub-001")
    assert a == b


def test_aggregate_concatenates(tmp_path):
    rows = [
        extract_metrics.extract_synth("sub-001"),
        extract_metrics.extract_synth("sub-002"),
    ]
    parts = []
    for r in rows:
        p = tmp_path / f"{r['subject_id']}.parquet"
        pd.DataFrame([r]).to_parquet(p, index=False)
        parts.append(str(p))

    out = tmp_path / "cohort.parquet"
    sys.argv = ["aggregate_cohort", "--inputs", *parts, "--out", str(out)]
    aggregate_cohort.main()
    df = pd.read_parquet(out)
    assert len(df) == 2
    assert "fa_mean" in df.columns
