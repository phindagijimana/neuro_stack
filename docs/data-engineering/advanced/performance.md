# Performance — queues, percentiles, skew

> Little's law, latency percentiles, hot keys, locality.

## Little's law

For any stable queue:

```
L = λ × W
```

L = items in system, λ = arrival rate, W = time in system.

Practical: fMRIPrep queue averages 50 jobs at 6 h each → throughput 8.3 jobs/h. To double throughput, halve per-job time *or* double concurrency.

## Latency percentiles

Average lies. Always report p50, p95, p99, p99.9. A system with p50 = 50 ms and p99 = 30 s is broken even if average is "fine".

## Hot partition / hot key detection

Symptoms:

- One Spark task runs 100× longer than median.
- One Kafka partition lags.
- One database shard at 100% CPU while others idle.

Mitigation: salt the key (`key + rand(0, N)`), pre-aggregate, or repartition.

## Vertical vs horizontal

- **Vertical** — bigger machine. Cheaper engineering; limited by hardware.
- **Horizontal** — more machines. Scales further; needs shardable workload.

Analytics → horizontal. OLTP → vertical until you can't.

## Locality

Data movement is the dominant cost.

- Co-locate compute and data (same region).
- Cache hot working set in RAM.
- Batch writes to amortise overhead.
- Compress for cross-network transfers.

## References

1. **Little JDC.** A proof for the queuing formula. *Operations Research.* 1961;9(3):383-387. [doi:10.1287/opre.9.3.383](https://doi.org/10.1287/opre.9.3.383)
2. **Dean J, Barroso LA.** The tail at scale. *Commun ACM.* 2013;56(2):74-80. [doi:10.1145/2408776.2408794](https://doi.org/10.1145/2408776.2408794)
3. **Gregg B.** *Systems Performance.* 2nd ed. Addison-Wesley; 2020. ISBN 978-0136820154.

## Where to next

[Concurrency, transactions, isolation levels](concurrency.md).
