# Concurrency, transactions, isolation levels

> ACID, isolation levels, MVCC, locks, deadlocks, connection pooling, Python concurrency.

## ACID

- **Atomicity** — all of a transaction commits or none does.
- **Consistency** — transactions preserve invariants.
- **Isolation** — concurrent transactions don't interfere.
- **Durability** — committed data survives crashes.

## Isolation levels and the anomalies they prevent

| Level | Prevents | Still allows |
|---|---|---|
| **Read uncommitted** | nothing | dirty reads |
| **Read committed** | dirty reads | non-repeatable, phantoms |
| **Repeatable read** | non-repeatable | phantoms (some engines) |
| **Snapshot** | dirty / non-repeatable / phantoms | write skew |
| **Serializable** | everything | (lower throughput) |

Postgres default is read-committed. Berenson et al.'s [classic paper](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-95-51.pdf) is the canonical reference.

## MVCC in one minute

Every row keeps a version; readers see the version committed when their transaction started. No reader-writer locks. Cost: storage bloat → vacuum reclaims.

## Locks

- **Row-level** — fine-grained, high concurrency.
- **Page-level** — coarser.
- **Table-level** — DDL ops; the "I broke production" lock.
- **Advisory** — application-coordinated.

## Deadlocks

Two transactions each hold a lock the other wants. Avoid by:

1. Always acquire locks in the same order.
2. Keep transactions short.
3. Use `SELECT ... FOR UPDATE SKIP LOCKED` for queues.

## Connection pooling

Connections are expensive (5-10 MB in Postgres). Use a pooler:

- **PgBouncer** — lightweight, transaction-mode.
- **SQLAlchemy pool** — application-side.
- **RDS Proxy / Cloud SQL** — managed.

## Python concurrency choices

| Choice | When |
|---|---|
| `threading` | I/O-bound (GIL allows it) |
| `multiprocessing` | CPU-bound |
| `asyncio` | Many concurrent I/O ops |
| `concurrent.futures` | Convenience wrapper |

Neuroimaging pipelines (mostly I/O + subprocess) → `asyncio` or thread pool. Numerical kernels in NumPy already release the GIL.

## Worked example — "claim next subject"

```sql
WITH next AS (
  SELECT subject_id FROM job_queue
  WHERE status = 'pending'
  ORDER BY created_at
  LIMIT 1
  FOR UPDATE SKIP LOCKED
)
UPDATE job_queue
SET status = 'running', claimed_at = now()
WHERE subject_id IN (SELECT subject_id FROM next)
RETURNING subject_id;
```

`SKIP LOCKED` lets N workers grab N different jobs without coordination.

## References

1. **Berenson H, Bernstein PA, Gray J, et al.** A critique of ANSI SQL isolation levels. *SIGMOD.* 1995. [link](https://www.microsoft.com/en-us/research/wp-content/uploads/2016/02/tr-95-51.pdf)
2. **Bernstein PA, Newcomer E.** *Principles of Transaction Processing.* 2nd ed. Morgan Kaufmann; 2009. ISBN 978-1558606234.

## Where to next

[Data quality deeply](data-quality.md).
