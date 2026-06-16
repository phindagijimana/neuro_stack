# Ingestion patterns

> Batch, CDC, webhooks vs polling, connector platforms.

## Batch

Read source on schedule, write into warehouse.

- **File drops** — most common for neuroimaging. PACS exports DICOM to watched folder.
- **Database snapshots** — `SELECT * WHERE ingested_at > last_run`. Misses deletes.
- **API pagination** — for SaaS sources (REDCap, OnCore, Stripe).

## CDC — Change Data Capture

- **Log-based** ([Debezium](https://debezium.io/)) — reads WAL/binlog. Captures deletes. Negligible source impact.
- **Trigger-based** — DB triggers fire on each change. Slows source writes.

Log-based + Kafka + sink is the modern default for real-time ingestion from OLTP.

## Webhooks vs polling

- **Webhooks** — source pushes. Lower latency; must accept HTTP + handle retries.
- **Polling** — you ask repeatedly. Higher latency, simpler.

Hybrid is common: webhook for low-latency, scheduled poll as safety net.

## Connector platforms

- [**Airbyte**](https://docs.airbyte.com) — open source; 350+ connectors.
- **Fivetran** — managed, commercial.
- **Stitch** — Singer-based.
- [**Meltano**](https://docs.meltano.com) — open source; build-your-own.

One-off sources → script + cron. Three+ sources → connector platform.

## For neuroimaging specifically

- **OpenNeuro / XNAT** — research-imaging ingest portals.
- **Flywheel** — commercial imaging ingest + organisation.
- [**DCM4CHEE**](https://github.com/dcm4che/dcm4chee-arc-light) — open source DICOM archive + router.

DICOM-native ingestion handles the scanner-to-BIDS layer.

## References

1. **Reis J, Housley M.** *Fundamentals of Data Engineering.* O'Reilly; 2022. ISBN 978-1098108304.
2. **Debezium Documentation.** [https://debezium.io/documentation/](https://debezium.io/documentation/)

## Where to next

[Event-driven architectures](event-driven.md).
