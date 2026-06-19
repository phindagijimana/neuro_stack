# CI/CD for data pipelines

> CI/CD for data does not mean "auto-deploy production data jobs on every commit". It means catching schema, logic, and data-quality regressions before they touch real cohorts — using DAG dry-runs, fixture subjects, schema diffs, ephemeral environments, and gates that block bad merges.

A web service's CI/CD is straightforward: test the code, build the artifact, deploy. A data pipeline's CI/CD has a second dimension — the *data* — that can break independently of the code. That's why the pattern below looks different from a typical microservice workflow.

## 10.1 What CI actually means for data

Six checks, in roughly increasing cost order. Run the cheap ones on every PR, the expensive ones on a nightly schedule or a merge to main.

| Check | What it catches | Cost | When |
| --- | --- | --- | --- |
| **Lint** (`ruff`, `shellcheck`, `yamllint`) | Style, simple bugs | Seconds | Every PR, every push |
| **Unit tests** (`pytest`) | Helper / parser / config bugs | Seconds | Every PR |
| **DAG dry-run** (`snakemake -n`, `dagster job execute --mode dry`) | Wiring errors, missing rules | Seconds | Every PR |
| **Integration test on a fixture subject** | End-to-end logic regressions | Minutes | Every PR |
| **Schema diff** | Breaking changes to gold outputs | Seconds | Every PR |
| **Container build + scan** (`docker build`, `trivy fs`) | CVE creep, dependency drift | Minutes | Every PR (cached) |
| **Data-quality checks on prod-shaped data** | Distribution drift, freshness | Hours | Nightly + pre-deploy |

GitHub Actions, GitLab CI, or Buildkite handle this for free. A `Makefile` with `make lint test integration` keeps the same commands runnable locally so the PR experience matches the CI experience.

## 10.2 The fixture subject — your most important asset

The single move that makes neuroimaging CI possible is a **fixture subject**: a tiny, cropped, public-data BIDS dataset that the entire pipeline can run on in under five minutes. Without it, "test the pipeline" means "wait six hours" and nobody tests anything.

Build it once:

- Pick a public dataset (OpenNeuro, HCP demo).
- Crop volumes to `(32, 32, 32)` or a single slice.
- Trim DWI to ~6 directions.
- Commit it under `tests/fixtures/sub-tiny/`.
- The integration test runs the whole DAG against this subject and asserts the gold artifact exists with the right shape.

```python
# tests/test_integration.py
import subprocess, pathlib, duckdb

def test_pipeline_on_fixture(tmp_path):
    out = tmp_path / "out"
    subprocess.check_call([
        "snakemake", "--use-conda", "-j", "1",
        "--directory", "tests/fixtures",
        "--config", f"results_root={out}", "all",
    ])
    edges = out / "gold" / "connectome_edges.parquet"
    assert edges.exists()
    df = duckdb.sql(f"SELECT * FROM read_parquet('{edges}')").df()
    assert df.shape[1] == 7
    assert df["streamline_count"].min() >= 0
```

This single test catches more regressions than every unit test combined.

## 10.3 A GitHub Actions workflow that pulls its weight

```yaml
# .github/workflows/ci.yml
name: ci
on:
  pull_request:
  push:
    branches: [main]

jobs:
  lint:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install ruff
      - run: ruff check .
      - run: |
          sudo apt-get update && sudo apt-get install -y shellcheck
          shellcheck $(git ls-files '*.sh')

  unit:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -e ".[dev]"
      - run: pytest tests/unit -q

  dag-dryrun:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - run: pip install snakemake
      - run: snakemake -n --directory tests/fixtures all

  integration:
    runs-on: ubuntu-latest
    needs: [unit, dag-dryrun]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with: { python-version: "3.11" }
      - run: pip install -e ".[dev]"
      - run: pytest tests/integration -q --timeout=600

  schema-diff:
    runs-on: ubuntu-latest
    needs: integration
    steps:
      - uses: actions/checkout@v4
        with: { fetch-depth: 0 }
      - run: pip install -e ".[dev]"
      - name: Compute schema of gold artifact
        run: python scripts/dump_schema.py tests/fixtures/out/gold/connectome_edges.parquet > /tmp/new_schema.json
      - name: Diff against main
        run: |
          git show main:schemas/connectome_edges.json > /tmp/old_schema.json || echo "{}" > /tmp/old_schema.json
          python scripts/schema_diff.py /tmp/old_schema.json /tmp/new_schema.json --comment-on-pr

  container:
    runs-on: ubuntu-latest
    needs: lint
    steps:
      - uses: actions/checkout@v4
      - uses: docker/setup-buildx-action@v3
      - run: docker build -t dwi-pipeline:pr-${{ github.event.pull_request.number }} .
      - uses: aquasecurity/trivy-action@master
        with:
          image-ref: dwi-pipeline:pr-${{ github.event.pull_request.number }}
          severity: HIGH,CRITICAL
          exit-code: 1
```

Six independent jobs, each fast. Failed lint blocks unit; failed unit blocks integration. The container build runs in parallel with everything else because its only dependency is lint passing.

## 10.4 Schema diff as a PR comment

The single most useful piece of bespoke CI is a schema-diff bot. It reads the schema of the gold Parquet on `main` and on the PR head, diffs them, and posts the result as a PR comment. Reviewers see breaking changes in their inbox before they merge.

```python
# scripts/schema_diff.py
import json, sys, os, requests

def diff(old, new):
    added   = set(new) - set(old)
    removed = set(old) - set(new)
    changed = {k for k in set(old) & set(new) if old[k] != new[k]}
    return added, removed, changed

def format_comment(added, removed, changed, old, new):
    lines = ["## Schema diff for `connectome_edges.parquet`"]
    if not (added or removed or changed):
        lines.append("No changes.")
        return "\n".join(lines)
    if removed:
        lines.append("### Removed (breaking)")
        lines += [f"- `{c}` (was `{old[c]}`)" for c in sorted(removed)]
    if changed:
        lines.append("### Type changed (breaking)")
        lines += [f"- `{c}`: `{old[c]}` -> `{new[c]}`" for c in sorted(changed)]
    if added:
        lines.append("### Added")
        lines += [f"- `{c}`: `{new[c]}`" for c in sorted(added)]
    return "\n".join(lines)

def post_pr_comment(body):
    pr   = os.environ["GITHUB_REF"].split("/")[-2]
    repo = os.environ["GITHUB_REPOSITORY"]
    tok  = os.environ["GITHUB_TOKEN"]
    requests.post(
        f"https://api.github.com/repos/{repo}/issues/{pr}/comments",
        headers={"Authorization": f"Bearer {tok}"},
        json={"body": body},
    ).raise_for_status()

if __name__ == "__main__":
    old = json.load(open(sys.argv[1]))
    new = json.load(open(sys.argv[2]))
    body = format_comment(*diff(old, new), old, new)
    print(body)
    if "--comment-on-pr" in sys.argv and os.environ.get("GITHUB_TOKEN"):
        post_pr_comment(body)
    if "Removed (breaking)" in body or "Type changed (breaking)" in body:
        sys.exit(1)
```

This is dbt's `dbt-checkpoint` and Datafold's `data-diff` in spirit — surface schema changes where the reviewer is already looking.

## 10.5 Ephemeral environments

For a PR that changes a non-trivial stage, you want a *real* environment that mirrors prod but is disposable. Two patterns:

- **PR-namespaced buckets** — every PR gets `s3://cohort-staging/pr-{number}/` and a Dagster code location named `pr-{number}`. Closing the PR deletes the namespace. The reviewer can poke at a real run.
- **Fixture cohorts** — a tiny "shadow cohort" of 3 subjects runs end-to-end against the PR build. Cheaper, faster, almost as informative.

```yaml
# part of the integration job
- name: Run PR against shadow cohort
  if: github.event_name == 'pull_request'
  env:
    PR_NS: pr-${{ github.event.pull_request.number }}
  run: |
    aws s3 sync s3://cohort/silver/fixtures/ s3://cohort-staging/${PR_NS}/silver/
    snakemake --config results_root=s3://cohort-staging/${PR_NS}/ all
    python scripts/qc_summary.py s3://cohort-staging/${PR_NS}/ > qc.md
    gh pr comment ${{ github.event.pull_request.number }} -F qc.md
```

The PR comment now contains a QC summary computed from a real (tiny) pipeline run on the PR's code. Reviewers approve based on data, not just diff.

## 10.6 Blue/green and canary for data pipelines

Web services blue/green by routing traffic; data pipelines blue/green by routing *consumers*. The pattern:

- The pipeline writes to a versioned path: `s3://cohort/gold/connectome_edges/run_id=2026-06-18-v3/`.
- A pointer (`s3://cohort/gold/connectome_edges/_current` or an Iceberg table snapshot ID) tells consumers which version to read.
- Deploy = write the new run, validate it, then move the pointer.
- Rollback = move the pointer back. Old run is still on disk.

```python
def promote(run_id: str, gold_root: str):
    new = f"{gold_root}/connectome_edges/run_id={run_id}/"
    if not data_quality_passes(new):
        raise RuntimeError("DQ checks failed; not promoting")
    write_atomic(f"{gold_root}/connectome_edges/_current", run_id)
    notify("data-eng", f"connectome_edges promoted to {run_id}")
```

`data_quality_passes` runs the same checks (row count band, null rate, distribution drift) used in [Testing pipelines](testing.md). If they fail, the pointer doesn't move and consumers don't see the bad run. **The deploy is gated on the data, not just the code.**

A canary variant: route 10% of consumers (e.g., one analyst's notebook) to the new run for a day before flipping everyone.

## 10.7 What to gate on, what to warn on

A common mistake is making every check blocking. Two failure modes follow: nuisance failures train reviewers to "click through", or legitimate-but-marginal changes get stuck. A useful split:

| Check | Mode | Rationale |
| --- | --- | --- |
| Lint, unit, DAG dry-run | Blocking | Cheap and unambiguous. |
| Integration on fixture | Blocking | If the fixture pipeline is broken, nothing is safe. |
| Schema diff (removed / type-changed) | Blocking | Breaking changes require an explicit override label. |
| Schema diff (added columns) | Warning | Additive changes are usually fine. |
| Trivy HIGH/CRITICAL | Blocking with explicit ignore-list | Otherwise drift compounds. |
| Data-quality drift > 3σ | Warning + notify owner | Could be a real shift in the cohort. |
| Cost per run > N% above baseline | Warning | Surface, don't block. |

The blocking checks are the contract. The warnings are conversation starters.

## 10.8 Local parity

CI is only as useful as developers' ability to reproduce its results locally. A pattern that works:

```makefile
# Makefile
.PHONY: lint unit dag integration container all

lint:
	ruff check .
	shellcheck $$(git ls-files '*.sh')

unit:
	pytest tests/unit -q

dag:
	snakemake -n --directory tests/fixtures all

integration:
	pytest tests/integration -q --timeout=600

container:
	docker build -t dwi-pipeline:dev .

all: lint unit dag integration container
```

`make all` runs exactly what CI runs, in the same order. When CI fails and you can't reproduce locally, that's a bug in the test isolation — fix it; don't shrug.

## References

1. **Reis J, Housley M.** *Fundamentals of Data Engineering.* O'Reilly; 2022.
2. **Mølbak P, Beauchemin M.** Functional data engineering — a modern paradigm for batch data processing. *Maxime Beauchemin blog.* 2018.
3. **Petersohn D, et al.** dbt: a data build tool. [docs.getdbt.com](https://docs.getdbt.com/)
4. **Aquasecurity.** Trivy: comprehensive vulnerability scanner. [github.com/aquasecurity/trivy](https://github.com/aquasecurity/trivy)
5. **Humble J, Farley D.** *Continuous Delivery.* Addison-Wesley; 2010. ISBN 978-0321601919.
6. **Sambasivan N, Kapania S, Highfill H, et al.** "Everyone wants to do the model work, not the data work": data cascades in high-stakes AI. *CHI.* 2021. [doi:10.1145/3411764.3445518](https://doi.org/10.1145/3411764.3445518)

## Where to next

- [HPC → industry](hpc-to-industry.md) — translating these CI habits into the larger habit-set difference between HPC and industry.
- [Testing pipelines](testing.md) — the test-pyramid view and DE-specific test types referenced above.
- [Reliability & operations](reliability.md) — SLOs and runbooks that make the warnings here actionable.
- [DWI case study](dwi-case-study.md) — the pipeline these checks are protecting.
