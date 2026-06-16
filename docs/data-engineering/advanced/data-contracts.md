# Data contracts and schema evolution

> Producer–consumer agreements, compatibility modes, schema registries.

## The producer-consumer problem

Schemas drift. A producer adds a column "to support a new dashboard"; the consumer that joined on the previous schema breaks two days later, in production, with no warning.

A **data contract** specifies:

- The **schema** (fields, types, nullability, constraints).
- The **semantics** (units, allowed values, business meaning).
- The **SLA** (freshness, ownership, deprecation notice).
- The **compatibility policy** (below).

## Compatibility modes

| Mode | Producer can | Consumer can |
|---|---|---|
| **Backward** | Drop optional fields, add nullable | Keep old schema running |
| **Forward** | Add fields | Read old data with new schema |
| **Full** | Either | Either direction works |
| **None** | Anything | Must coordinate releases |

Confluent's reference table is [here](https://docs.confluent.io/platform/current/schema-registry/avro.html).

## Schema registries

Centralised registry with compatibility check on every write:

- **Confluent Schema Registry** — de-facto for Kafka/Avro/Protobuf.
- **AWS Glue Schema Registry** — AWS-native.
- **Apicurio Registry** — open source alternative.

Workflow: producer registers schema v1 → adds field for v2 → registry checks compatibility → producer sends `[schema_id][payload]` → consumer looks up schema by id.

## dbt contracts (analytics-side enforcement)

```yaml
- name: cohort_qc_summary
  config:
    contract:
      enforced: true
    access: public
  columns:
    - name: subject_id
      data_type: text
      constraints: [{type: not_null}]
```

## The deprecation workflow

When you need a breaking change:

1. Announce a deprecation date in the contract.
2. Ship v2 alongside v1.
3. Notify consumers; help them migrate.
4. Sunset v1 after announced date (three months is polite).

## References

1. **Confluent — Schema Registry overview.** [https://docs.confluent.io/platform/current/schema-registry/index.html](https://docs.confluent.io/platform/current/schema-registry/index.html)
2. **dbt contracts.** [https://docs.getdbt.com/docs/collaborate/govern/model-contracts](https://docs.getdbt.com/docs/collaborate/govern/model-contracts)

## Where to next

[Security & governance](security.md).
