# Event-driven architectures

> Event sourcing, CQRS, outbox, sagas, dead-letter queues.

## Event sourcing

Persist the events; derive state from them.

```text
Event log:
  2026-01-01  subject_enrolled  {id: "001"}
  2026-01-15  scan_acquired     {id: "001", session: "ses-01", modality: "T1w"}
  2026-01-15  scan_acquired     {id: "001", session: "ses-01", modality: "DWI"}

Derived: subject 001 has 2 scans in ses-01
```

Pros: full audit, time-travel, multiple read models from one write model. Cons: more thinking; event schema evolution is harder.

## CQRS — Command Query Responsibility Segregation

Commands mutate state; queries read it. Write model is normalised; read model is denormalised. Pairs naturally with event sourcing.

## The outbox pattern — the dual-write fix

The classic bug: "I wrote to the database and tried to publish to Kafka, but Kafka was down, so they diverged."

The fix:

1. Within the same DB transaction, write to your domain table **and** to an `outbox` table.
2. A separate process tails the outbox and publishes to Kafka, marking rows as published on ack.

DB is source of truth; publish is idempotent. Debezium can read the outbox via CDC.

## Saga pattern

Long-lived "transaction" = chain of local transactions + compensating actions.

- **Choreographed** — services listen and decide. Simpler at small scale.
- **Orchestrated** — a coordinator (Camunda, [Temporal](https://docs.temporal.io)) drives the chain. Better for complex flows.

## Dead-letter queues

A message that fails repeatedly shouldn't block the queue. After N retries → DLQ → alert → manual triage.

```python
def process(record):
    try:
        do_work(record)
    except RecoverableError:
        raise  # let the broker retry
    except Exception:
        publish_to_dlq(record, traceback.format_exc())
```

Treat DLQ growth rate as an SLI.

## References

1. **Young G.** CQRS Documents. [pdf](https://cqrs.files.wordpress.com/2010/11/cqrs_documents.pdf)
2. **Richardson C.** *Microservices Patterns.* Manning; 2018. ISBN 978-1617294549.
3. **Hohpe G, Woolf B.** *Enterprise Integration Patterns.* Addison-Wesley; 2003. ISBN 978-0321200686.

## Where to next

[MLOps overlap](mlops.md).
