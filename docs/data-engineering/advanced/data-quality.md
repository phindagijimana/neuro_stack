# Data quality deeply

> Six dimensions, where checks live, circuit breaker pattern, drift detection.

## Six dimensions

| Dimension | What it asks |
|---|---|
| **Completeness** | Are required fields populated? |
| **Uniqueness** | No accidental duplicates? |
| **Validity** | Conforms to format / range / enum? |
| **Consistency** | Cross-row / cross-table relationships hold? |
| **Accuracy** | Matches the real world? |
| **Timeliness** | Fresh enough? |

Schema tests cover completeness, uniqueness, validity. Accuracy and timeliness need separate machinery.

## Where checks live

| Layer | Tool |
|---|---|
| Ingest | Pydantic / dataclasses at API boundary |
| Storage | DB constraints (NOT NULL, CHECK, FK) |
| Transformation | dbt tests, [Great Expectations](https://greatexpectations.io) |
| Serving | Pandera, contract tests |

Defence in depth.

## Circuit breaker pattern

When downstream is degraded, stop calling for a while:

```python
class CircuitBreaker:
    def __init__(self, threshold=5, timeout_s=60):
        self.failures = 0
        self.opened_at = 0
        self.threshold = threshold
        self.timeout_s = timeout_s

    def call(self, fn, *args):
        if self.is_open():
            raise CircuitOpenError()
        try:
            result = fn(*args)
            self.failures = 0
            return result
        except Exception:
            self.failures += 1
            if self.failures >= self.threshold:
                self.opened_at = time.time()
            raise

    def is_open(self):
        return (time.time() - self.opened_at) < self.timeout_s
```

For data pipelines: trip the breaker when validation failure rate exceeds X% over Y minutes.

## Drift detection

- **Schema drift** — new columns, type changes. Schema-diff on every load.
- **Distribution drift** — column mean / variance shifts. KS test, PSI.
- **Volume drift** — row count outside expected band.
- **Concept drift** (ML) — relationship between features and labels changes.

Tools: Whylogs, Evidently, `nannyML`.

## Worked example — Great Expectations on DK CSV

```python
import great_expectations as gx
df = gx.read_csv("derivatives/dk_connectome.csv")

df.expect_column_value_count_to_equal("subject_id", 84)
df.expect_column_values_to_be_between("edge_weight", min_value=0, max_value=1e7)
df.expect_column_to_exist("source_region")

results = df.validate()
if not results.success:
    raise SystemExit("Connectome failed validation")
```

## References

1. **DAMA International.** *DAMA-DMBOK.* 2nd ed. Technics Publications; 2017. ISBN 978-1634622349.
2. **Moses B, Karpasas L, Densmore L.** *Data Quality Fundamentals.* O'Reilly; 2022. ISBN 978-1098112042.

## Where to next

[Catalogs, discovery, lineage](catalogs.md).
