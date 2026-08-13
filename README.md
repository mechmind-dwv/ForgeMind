# ForgeMind

**Experimental engine for compositional hypothesis discovery and falsification.**

ForgeMind explores a simple research question:

> Can a system discover compact programs by generating hypotheses, actively
> searching for informative counterexamples, and retaining hypotheses that
> survive falsification?

## Current status

**Research prototype — v0.8.0**

The project is experimental. Benchmark results are not presented as evidence
of general intelligence or real-world reasoning capability.

## Architecture

```text
                INPUT / TASK
                     |
                     v
            +------------------+
            | Hypothesis       |
            | Generator        |
            +--------+---------+
                     |
                     v
            +------------------+
            | Compositional    |
            | Program Space     |
            +--------+---------+
                     |
                     v
            +------------------+
            | Active           |
            | Experiment       |
            | Selection         |
            +--------+---------+
                     |
                     v
            +------------------+
            | Falsification     |
            | / Counterexample  |
            +--------+---------+
                     |
                     v
            +------------------+
            | Selection         |
            | + Evolution       |
            +------------------+

Repository layout

forgemind/       Core implementation
tests/           Automated tests
benchmarks/      Reproducible experiment outputs
experiments/     Future research experiments
examples/        Usage examples
docs/            Architecture and research notes
.github/         Continuous integration

Running

python -m pytest -q

Run the current experiment:

python -m forgemind.run

Research principles

ForgeMind follows several principles:

1. A benchmark result is not automatically evidence of intelligence.


2. Hidden tests are preferred over training-set performance.


3. Falsification is more informative than simple success counting.


4. Complexity should be penalized.


5. Experiments must be reproducible.


6. Failed experiments are retained as evidence rather than hidden.



License

MIT
