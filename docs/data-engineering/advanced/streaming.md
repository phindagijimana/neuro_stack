# Streaming systems

> Kafka topology, watermarks, exactly-once across systems, CDC patterns.

## Kafka topology in one paragraph

[Apache Kafka](https://kafka.apache.org/documentation/) is a distributed append-only log. Producers write records to topics; topics are split into partitions; partitions live on brokers; consumers read at their own pace tracked by offsets.

## Producers

- **Partitioner** chooses which partition (round-robin, key-hash, custom).
- **`acks`** — `0` (fire-and-forget), `1` (leader only), `all` (leader + ISR). Production = `all`.
- **`enable.idempotence=true`** — per-producer-per-partition exactly-once writes.
- **`transactional.id`** — cross-partition transactional writes.

## Consumers

- **Consumer groups** — partitions split among instances; each partition is read by exactly one consumer in the group.
- **Offset commit** — controls "have I processed this record"; commit after processing.
- **Rebalancing** — when a member joins/leaves; cooperative rebalancing minimises pauses.

## Stream-table duality

Every stream of events implies a table state (latest value per key). Kafka Streams ([docs](https://kafka.apache.org/documentation/streams/)) and ksqlDB make this explicit:

```sql
CREATE TABLE subject_qc AS
  SELECT subject_id, LATEST_BY_OFFSET(fd_mean) AS fd_mean
  FROM qc_events
  GROUP BY subject_id;
```

## Event time vs processing time, watermarks, windows

- **Processing time** — when the consumer saw it.
- **Event time** — when it happened.
- **Watermark** — "events with timestamp ≤ W will not arrive late". Closes windows.

Window types: tumbling, hopping, session. [Apache Flink](https://flink.apache.org/) is the most expressive stream processor.

## Exactly-once across systems

Three pieces required:

1. **Producer** — idempotent writes.
2. **Processing** — checkpointed state.
3. **Sink** — transactional write to downstream.

Miss any one = at-least-once.

## CDC patterns

- **Log-based CDC** — [Debezium](https://debezium.io/) reads Postgres WAL / MySQL binlog. Low source impact. The right answer.
- **Polling** — `WHERE updated_at > last_seen`. Easy; misses deletes.

## References

1. **Kreps J, Narkhede N, Rao J.** Kafka: a distributed messaging system for log processing. *NetDB.* 2011.
2. **Akidau T, Bradshaw R, Chambers C, et al.** The Dataflow model. *VLDB.* 2015. [doi:10.14778/2824032.2824076](https://doi.org/10.14778/2824032.2824076)
3. **Carbone P, Katsifodimos A, Ewen S, et al.** Apache Flink: stream and batch processing in a single engine. *IEEE Data Eng Bull.* 2015.
4. **Confluent — Kafka the Definitive Guide.** 2nd ed. O'Reilly; 2021. ISBN 978-1492043089.

## Where to next

[dbt deeply](dbt.md) — the workhorse of warehouse-side transformation.
