"""Render a minimal cohort QC HTML report from the aggregated cohort table."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

import pandas as pd

HTML_TEMPLATE = """<!doctype html>
<html><head>
<title>DWI cohort report</title>
<style>
body {{ font-family: -apple-system, sans-serif; margin: 2rem; max-width: 60rem; }}
table {{ border-collapse: collapse; }}
th, td {{ border: 1px solid #ddd; padding: 6px 12px; text-align: right; }}
th {{ background: #f6f6f6; }}
.ok {{ color: #2a9d2a; }}
.bad {{ color: #c0392b; }}
</style>
</head><body>
<h1>DWI cohort report</h1>
<p>{n} subjects, {ok} succeeded, {bad} failed.</p>
<h2>Summary statistics</h2>
{summary_html}
<h2>Per-subject manifests</h2>
{manifests_html}
</body></html>
"""


def parse_args() -> argparse.Namespace:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--cohort", type=Path, required=True)
    p.add_argument("--manifests", type=Path, nargs="+", required=True)
    p.add_argument("--out", type=Path, required=True)
    return p.parse_args()


def main() -> int:
    args = parse_args()
    df = pd.read_parquet(args.cohort)
    manifests = []
    ok = bad = 0
    for p in args.manifests:
        m = json.loads(p.read_text())
        manifests.append(m)
        if m.get("success") is True:
            ok += 1
        else:
            bad += 1

    summary = df.describe().to_html(classes="summary")
    rows = "\n".join(
        f"<tr><td>{m['subject_id']}</td><td>{m['pipeline']}</td>"
        f"<td>{m.get('git_sha','')}</td>"
        f"<td class='{'ok' if m.get('success') else 'bad'}'>"
        f"{'OK' if m.get('success') else 'FAIL'}</td></tr>"
        for m in manifests
    )
    manifest_html = (
        "<table><tr><th>Subject</th><th>Pipeline</th><th>SHA</th><th>Status</th></tr>"
        f"{rows}</table>"
    )

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(HTML_TEMPLATE.format(
        n=len(df), ok=ok, bad=bad,
        summary_html=summary, manifests_html=manifest_html,
    ))
    print(f"wrote {args.out}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
