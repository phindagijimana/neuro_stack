# Distributed systems fundamentals

> CAP, consistency models, idempotency keys, quorums, consensus.

## CAP theorem in 60 seconds

In the face of a network **P**artition, you must choose between **C**onsistency and **A**vailability. Choose in advance:

- **CP** — refuse writes during a partition (Spanner, etcd, ZooKeeper).
- **AP** — accept writes everywhere; reconcile later (Cassandra, Dynamo).

CAP is a starting framework. **PACELC** extends it: absent a partition, do you prefer Latency or Consistency?

## Consistency models — weakest to strongest

| Model | Guarantee |
|---|---|
| Eventual | Replicas converge eventually |
| Read-your-writes | Reads see your own writes |
| Monotonic reads | Reads don't go backwards |
| Causal | Causally related ops are ordered |
| Snapshot | Reads see a consistent snapshot |
| Serializable | As if transactions ran one at a time |
| Linearizable | As if there was one node |

Linearizable + serializable = **strict serializable** — Spanner's default. Expensive; only ask for it when needed.

## Idempotency keys + exactly-once

Distributed systems deliver at-least-once. The fix is idempotent consumers + **idempotency keys**:

```http
PUT /v1/scans/{idempotency_key}
{ "subject": "sub-001", "modality": "DWI" }
```

The server stores `{key → response}` for ~24 h; repeated requests return the stored response. Stripe's pattern ([docs](https://stripe.com/docs/api/idempotent_requests)) is the public reference implementation.

## Distributed transactions

- **2PC (two-phase commit)** — coordinator-driven; blocks on coordinator failure.
- **Saga** — chain of local transactions + compensating actions; eventually consistent.
- **TCC (try-confirm-cancel)** — reservation-style.

Modern default: avoid distributed transactions; model as eventually consistent.

## Quorums and consensus

For replicated values: **reads + writes ≥ replicas + 1**.

For order consensus (state machine replication):

- **Paxos** — Lamport 1998; correct but hard to implement.
- **Raft** ([paper](https://raft.github.io/raft.pdf)) — designed for understandability; what etcd, Consul, CockroachDB use.

You almost never implement consensus yourself; you pick a system that runs it.

## References

1. **Kleppmann M.** *Designing Data-Intensive Applications.* O'Reilly; 2017. ISBN 978-1449373320.
2. **Brewer EA.** Towards robust distributed systems. *PODC.* 2000.
3. **Lamport L.** The part-time parliament. *ACM TOCS.* 1998;16(2):133-169.
4. **Ongaro D, Ousterhout J.** In search of an understandable consensus algorithm. *USENIX ATC.* 2014. [pdf](https://raft.github.io/raft.pdf)
5. **Abadi DJ.** Consistency tradeoffs in modern distributed database system design. *Computer.* 2012;45(2):37-42. [doi:10.1109/MC.2012.33](https://doi.org/10.1109/MC.2012.33)

## Where to next

[Spark](spark.md) — distributed compute on top of these primitives.
