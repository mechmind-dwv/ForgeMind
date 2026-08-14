# ForgeMind 0.10 — Large-Scale Search Benchmark

This benchmark evaluates the first scalable search layer of ForgeMind.

## Configuration

- Population: 256
- Generations: 25
- Beam width: 64
- Active candidate probes: 32
- Maximum program length: 6
- Seeds: 3, 11, 29, 47
- Hidden probes: 32

## Metrics

The benchmark records:

- hidden accuracy
- discovery rate
- oracle queries
- hypothesis evaluations
- cache hit rate
- falsifications
- discovered program
- program complexity

## Important

This benchmark is an engineering and research baseline.

It does **not** establish that active search is statistically superior
to passive search.

That claim belongs to the later large-scale statistical evaluation
phase of the ForgeMind roadmap.
