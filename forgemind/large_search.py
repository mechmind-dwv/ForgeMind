"""
ForgeMind 0.10 — Large-Scale Search Engine.

Scalable experimental layer for active program synthesis.

Pipeline:

    population
        ↓
    active experiment proposal
        ↓
    oracle observation
        ↓
    cached evaluation
        ↓
    beam/parsimony selection
        ↓
    mutation + crossover
        ↓
    next generation

The engine is deliberately separated from core.py and active.py so that
large-scale search can be benchmarked independently.
"""

from __future__ import annotations

from dataclasses import dataclass, field
import random
from typing import Any

from .active import information_gain
from .core import (
    Hyp,
    Node,
    TARGETS,
    canon,
    complexity,
    crossover,
    mutate,
    rand_node,
    run,
    xgen,
)


@dataclass(frozen=True)
class SearchConfig:
    population: int = 256
    generations: int = 50
    beam_width: int = 64
    candidate_budget: int = 32
    max_program_length: int = 6


@dataclass
class SearchMetrics:
    oracle_queries: int = 0
    hypothesis_evaluations: int = 0
    cache_hits: int = 0
    cache_misses: int = 0
    generated: int = 0
    falsifications: int = 0

    @property
    def evaluations_per_query(self) -> float:
        if self.oracle_queries == 0:
            return 0.0
        return self.hypothesis_evaluations / self.oracle_queries

    @property
    def cache_hit_rate(self) -> float:
        total = self.cache_hits + self.cache_misses
        if total == 0:
            return 0.0
        return self.cache_hits / total


@dataclass
class SearchResult:
    target_index: int
    seed: int
    found: bool
    program: tuple
    complexity: float
    generations: int
    observations: int
    hidden_accuracy: float
    metrics: SearchMetrics
    history: list[dict[str, Any]] = field(default_factory=list)


class LargeSearchEngine:
    """
    Population-based active search.

    The oracle is queried once per generation. Hypothesis evaluations
    are cached by canonical program + input.
    """

    def __init__(
        self,
        seed: int,
        config: SearchConfig | None = None,
    ):
        self.seed = seed
        self.config = config or SearchConfig()
        self.rng = random.Random(seed)

        self.metrics = SearchMetrics()

        self.prediction_cache: dict[
            tuple[tuple, tuple[int, ...]],
            tuple,
        ] = {}

        self.observations: list[
            tuple[list[int], list[int]]
        ] = []

    def _cache_key(
        self,
        program: list[Node],
        x: list[int],
    ) -> tuple[tuple, tuple[int, ...]]:
        return canon(program), tuple(x)

    def predict(
        self,
        program: list[Node],
        x: list[int],
    ) -> list:
        key = self._cache_key(program, x)

        if key in self.prediction_cache:
            self.metrics.cache_hits += 1
            return list(self.prediction_cache[key])

        self.metrics.cache_misses += 1
        self.metrics.hypothesis_evaluations += 1

        try:
            value = tuple(run(program, x))
        except Exception:
            value = ("__ERROR__",)

        self.prediction_cache[key] = value

        return list(value)

    def _initial_population(self) -> list[Hyp]:
        population: list[Hyp] = []
        seen: set[tuple] = set()

        while len(population) < self.config.population:
            r = self.rng.random()

            if r < 0.30:
                length = 1
            elif r < 0.72:
                length = 2
            elif r < 0.94:
                length = 3
            else:
                length = self.rng.randint(
                    4,
                    self.config.max_program_length,
                )

            program = [
                rand_node(self.rng)
                for _ in range(length)
            ]

            key = canon(program)

            if key in seen:
                continue

            seen.add(key)
            population.append(Hyp(program))

        self.metrics.generated += len(population)

        return population

    def select_probe(
        self,
        population: list[Hyp],
    ) -> tuple[list[int], float]:
        candidates = [
            xgen(self.rng)
            for _ in range(self.config.candidate_budget)
        ]

        scored = [
            (
                information_gain(population, x),
                x,
            )
            for x in candidates
        ]

        gain, probe = max(
            scored,
            key=lambda item: item[0],
        )

        return probe, gain

    def _score(
        self,
        hypothesis: Hyp,
    ) -> tuple:
        exact = 0
        distance = 0.0

        for x, target_output in self.observations:
            prediction = self.predict(
                hypothesis.p,
                x,
            )

            if prediction == target_output:
                exact += 1
                continue

            n = min(
                len(prediction),
                len(target_output),
            )

            distance += sum(
                abs(prediction[i] - target_output[i])
                for i in range(n)
            )

            distance += (
                10
                * abs(
                    len(prediction)
                    - len(target_output)
                )
            )

        return (
            exact,
            -distance,
            -hypothesis.failures,
            hypothesis.support,
            -complexity(hypothesis.p),
        )

    def _rank(
        self,
        population: list[Hyp],
    ) -> list[Hyp]:
        ranked = sorted(
            population,
            key=self._score,
            reverse=True,
        )

        survivors: list[Hyp] = []
        seen: set[tuple] = set()

        for hypothesis in ranked:
            key = canon(hypothesis.p)

            if key in seen:
                continue

            seen.add(key)
            survivors.append(hypothesis)

            if len(survivors) >= self.config.beam_width:
                break

        return survivors

    def _observe(
        self,
        target: list[Node],
        population: list[Hyp],
    ) -> tuple[list[int], float, int]:
        probe, gain = self.select_probe(population)

        target_output = run(
            target,
            probe,
        )

        self.observations.append(
            (
                probe,
                target_output,
            )
        )

        self.metrics.oracle_queries += 1

        eliminated = 0

        for hypothesis in population:
            prediction = self.predict(
                hypothesis.p,
                probe,
            )

            hypothesis.evaluations += 1

            if prediction == target_output:
                hypothesis.support += 1
            else:
                hypothesis.failures += 1
                eliminated += 1

        self.metrics.falsifications += eliminated

        return (
            probe,
            gain,
            eliminated,
        )

    def _breed(
        self,
        elite: list[Hyp],
    ) -> list[Hyp]:
        population = [
            Hyp(
                list(h.p),
                h.support,
                h.failures,
                h.evaluations,
            )
            for h in elite
        ]

        while len(population) < self.config.population:
            parent = self.rng.choice(elite)

            child = list(parent.p)

            if self.rng.random() < 0.60:
                other = self.rng.choice(elite)

                child = crossover(
                    child,
                    other.p,
                    self.rng,
                )

            if self.rng.random() < 0.92:
                child = mutate(
                    child,
                    self.rng,
                )

            child = child[
                : self.config.max_program_length
            ]

            population.append(
                Hyp(child)
            )

            self.metrics.generated += 1

        return population

    def search(
        self,
        target_index: int,
        hidden_probes: int = 32,
    ) -> SearchResult:
        if not 0 <= target_index < len(TARGETS):
            raise IndexError(
                "target_index out of range"
            )

        target = TARGETS[target_index]

        population = self._initial_population()

        history: list[dict[str, Any]] = []

        best: Hyp | None = None

        for generation in range(
            self.config.generations
        ):
            if not population:
                break

            (
                probe,
                gain,
                eliminated,
            ) = self._observe(
                target,
                population,
            )

            elite = self._rank(
                population
            )

            best = elite[0]

            history.append(
                {
                    "generation": generation,
                    "population": len(population),
                    "elite": len(elite),
                    "oracle_query":
                        self.metrics.oracle_queries,
                    "eliminated": eliminated,
                    "information_gain": gain,
                    "best_program":
                        canon(best.p),
                    "best_complexity":
                        complexity(best.p),
                    "best_support":
                        best.support,
                    "best_failures":
                        best.failures,
                    "cache_hit_rate":
                        self.metrics.cache_hit_rate,
                }
            )

            population = self._breed(
                elite
            )

        if best is None:
            raise RuntimeError(
                "large search produced no hypothesis"
            )

        hidden_rng = random.Random(
            self.seed + 9_001_003
        )

        hidden = [
            xgen(hidden_rng)
            for _ in range(hidden_probes)
        ]

        correct = sum(
            self.predict(best.p, x)
            == run(target, x)
            for x in hidden
        )

        hidden_accuracy = (
            correct / len(hidden)
            if hidden
            else 0.0
        )

        return SearchResult(
            target_index=target_index,
            seed=self.seed,
            found=(
                hidden_accuracy == 1.0
            ),
            program=canon(best.p),
            complexity=complexity(best.p),
            generations=len(history),
            observations=len(
                self.observations
            ),
            hidden_accuracy=hidden_accuracy,
            metrics=self.metrics,
            history=history,
        )


def large_search(
    target_index: int,
    seed: int,
    config: SearchConfig | None = None,
    hidden_probes: int = 32,
) -> SearchResult:
    """
    Convenience API for one reproducible trial.
    """

    engine = LargeSearchEngine(
        seed=seed,
        config=config,
    )

    return engine.search(
        target_index=target_index,
        hidden_probes=hidden_probes,
    )
