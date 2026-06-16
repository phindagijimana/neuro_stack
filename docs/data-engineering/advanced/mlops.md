# MLOps overlap — feature stores, vector stores

> Why DEs care about MLOps, feature stores, training-serving skew, vector stores in the RAG era.

## Why DEs care

The boundary between DE and ML engineering is fuzzy and DE increasingly owns more of the ML stack:

- The **feature store** — features used by both training and inference.
- The **labelled training set** — curated, versioned, lineaged.
- The **vector store** — embeddings as a queryable index.

## Feature store (Feast architecture)

[Feast](https://docs.feast.dev/) is the open-source default; Tecton and SageMaker Feature Store are commercial.

Two access patterns share one feature definition:

- **Offline store** (BigQuery, Snowflake, Iceberg) — for training; point-in-time joins.
- **Online store** (Redis, DynamoDB, Cassandra) — for inference; low-latency lookups.

```python
from feast import Feature, FeatureView, Entity

subject = Entity(name="subject_id", value_type=ValueType.STRING)
qc_features = FeatureView(
    name="qc_features",
    entities=["subject_id"],
    features=[Feature("fd_mean", ValueType.FLOAT), Feature("dvars_mean", ValueType.FLOAT)],
    source=BigQuerySource(...),
    online=True,
)
```

## Training-serving skew

The bug class that ruined the previous decade of ML projects: features computed differently at training vs inference. A feature store **is** the fix.

## Vector stores (RAG-era)

For LLM-augmented systems: embed documents → vectors → ANN-indexed store → retrieve top-k → feed into LLM context.

| Tool | When |
|---|---|
| [**PGVector**](https://github.com/pgvector/pgvector) | Already on Postgres; small-to-medium |
| [**Qdrant**](https://qdrant.tech) | Open source, Rust, fast |
| **Pinecone** | Managed; production-ready |
| [**Weaviate**](https://weaviate.io) | Open source; schema-aware |
| [**Milvus**](https://milvus.io) | Open source; very large indexes |

For neuroimaging: a vector store of papers, BIDS-app docs, and runbook entries powers a useful "ask the docs" RAG agent.

## References

1. **Feast Documentation.** [https://docs.feast.dev/](https://docs.feast.dev/)
2. **Lewis P, Perez E, Piktus A, et al.** Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks. *NeurIPS.* 2020. [arXiv:2005.11401](https://doi.org/10.48550/arXiv.2005.11401)
3. **Huyen C.** *Designing Machine Learning Systems.* O'Reilly; 2022. ISBN 978-1098107963.

## Where to next

[Backup, disaster recovery, RTO/RPO](disaster-recovery.md).
