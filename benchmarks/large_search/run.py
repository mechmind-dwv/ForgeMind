"""
ForgeMind 0.10 benchmark.

Large-scale active search versus a passive random-probe baseline.

This first benchmark intentionally measures infrastructure and scaling
behavior. It does not claim superiority until statistical evaluation
across a larger task suite is available.
"""

from __future__ import annotations

import json
import statistics
from pathlib import Path

from forgemind.active import run_passive_protocol
from forgemind.large_search import (
    SearchConfig,
    large_search,
)
from forgemind.core import TARGETS


SEEDS = (
    3,
    11,
    29,
    47,
)

CONFIG = SearchConfig(
    population=256,
    generations=25,
    beam_width=64,
    candidate_budget=32,
    max_program_length=6,
)

HIDDEN_PROBES = 32


def main():
    rows = []

    print(
        "===== FORGEMIND 0.10 LARGE-SCALE SEARCH ====="
    )
    print()

    print(
        "population =",
        CONFIG.population,
    )
    print(
        "generations =",
        CONFIG.generations,
    )
    print(
        "beam_width =",
        CONFIG.beam_width,
    )
    print(
        "candidate_budget =",
        CONFIG.candidate_budget,
    )

    print()

    for seed in SEEDS:
        for target_index in range(
            len(TARGETS)
        ):
            active = large_search(
                target_index=target_index,
                seed=seed * 1000 + target_index,
                config=CONFIG,
                hidden_probes=HIDDEN_PROBES,
            )

            passive = run_passive_protocol(
                target_index=target_index,
                seed=seed * 1000 + target_index,
                rounds=CONFIG.generations,
                population=CONFIG.population,
            )

            row = {
                "seed": seed,
                "target": target_index,

                "active_found":
                    active.found,

                "active_accuracy":
                    active.hidden_accuracy,

                "active_complexity":
                    active.complexity,

                "active_queries":
                    active.metrics.oracle_queries,

                "active_evaluations":
                    active.metrics.hypothesis_evaluations,

                "active_cache_hit_rate":
                    active.metrics.cache_hit_rate,

                "active_falsifications":
                    active.metrics.falsifications,

                "active_program":
                    active.program,

                "passive_survivors":
                    passive.survivor_count,

                "passive_eliminations":
                    passive.eliminations,

                "passive_queries":
                    passive.oracle_queries,
            }

            rows.append(row)

            print(
                f"seed={seed:2d} "
                f"target={target_index:2d} "
                f"active_accuracy="
                f"{active.hidden_accuracy:.3f} "
                f"active_cache="
                f"{active.metrics.cache_hit_rate:.3f}"
            )

    accuracies = [
        row["active_accuracy"]
        for row in rows
    ]

    found = [
        row["active_found"]
        for row in rows
    ]

    cache_rates = [
        row["active_cache_hit_rate"]
        for row in rows
    ]

    falsifications = [
        row["active_falsifications"]
        for row in rows
    ]

    result = {
        "version": "0.10.0",
        "protocol": {
            "seeds": list(SEEDS),
            "population": CONFIG.population,
            "generations": CONFIG.generations,
            "beam_width": CONFIG.beam_width,
            "candidate_budget":
                CONFIG.candidate_budget,
            "max_program_length":
                CONFIG.max_program_length,
            "hidden_probes":
                HIDDEN_PROBES,
        },
        "rows": rows,
        "summary": {
            "trials": len(rows),
            "mean_hidden_accuracy":
                statistics.mean(accuracies),
            "discovery_rate":
                statistics.mean(found),
            "mean_cache_hit_rate":
                statistics.mean(cache_rates),
            "mean_falsifications":
                statistics.mean(falsifications),
        },
    }

    output = Path(
        "benchmarks/large_search/results.json"
    )

    output.write_text(
        json.dumps(
            result,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print()
    print(
        "===== SUMMARY ====="
    )

    print(
        "mean hidden accuracy =",
        f"{statistics.mean(accuracies):.4f}",
    )

    print(
        "discovery rate =",
        f"{statistics.mean(found):.4f}",
    )

    print(
        "mean cache hit rate =",
        f"{statistics.mean(cache_rates):.4f}",
    )

    print(
        "mean falsifications =",
        f"{statistics.mean(falsifications):.2f}",
    )

    print()
    print(
        "results:",
        output,
    )


if __name__ == "__main__":
    main()
