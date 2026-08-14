import random

from forgemind.core import Node, Hyp, TARGETS, canon
from forgemind.large_search import (
    LargeSearchEngine,
    SearchConfig,
    large_search,
)


def test_large_search_is_reproducible():
    config = SearchConfig(
        population=32,
        generations=5,
        beam_width=8,
        candidate_budget=8,
    )

    a = large_search(
        target_index=0,
        seed=123,
        config=config,
        hidden_probes=8,
    )

    b = large_search(
        target_index=0,
        seed=123,
        config=config,
        hidden_probes=8,
    )

    assert a.program == b.program
    assert a.hidden_accuracy == b.hidden_accuracy
    assert a.metrics.oracle_queries == b.metrics.oracle_queries


def test_large_search_uses_active_queries():
    config = SearchConfig(
        population=24,
        generations=4,
        beam_width=8,
        candidate_budget=8,
    )

    result = large_search(
        target_index=0,
        seed=7,
        config=config,
    )

    assert result.metrics.oracle_queries == 4
    assert result.observations == 4


def test_prediction_cache_reuses_evaluations():
    engine = LargeSearchEngine(
        seed=1,
        config=SearchConfig(
            population=8,
            generations=1,
        ),
    )

    program = [
        Node("U", "rev"),
    ]

    x = [1, 2, 3]

    first = engine.predict(
        program,
        x,
    )

    misses = engine.metrics.cache_misses

    second = engine.predict(
        program,
        x,
    )

    assert first == second
    assert engine.metrics.cache_misses == misses
    assert engine.metrics.cache_hits == 1


def test_large_search_never_exceeds_population():
    config = SearchConfig(
        population=32,
        generations=3,
        beam_width=8,
        candidate_budget=8,
    )

    engine = LargeSearchEngine(
        seed=99,
        config=config,
    )

    result = engine.search(
        target_index=0,
        hidden_probes=4,
    )

    assert all(
        row["population"] <= 32
        for row in result.history
    )


def test_large_search_has_bounded_program_complexity():
    config = SearchConfig(
        population=32,
        generations=3,
        beam_width=8,
        candidate_budget=8,
        max_program_length=6,
    )

    result = large_search(
        target_index=0,
        seed=42,
        config=config,
    )

    assert result.complexity <= 7.0


def test_all_targets_are_searchable():
    config = SearchConfig(
        population=16,
        generations=2,
        beam_width=4,
        candidate_budget=4,
    )

    for target_index in range(len(TARGETS)):
        result = large_search(
            target_index=target_index,
            seed=100 + target_index,
            config=config,
            hidden_probes=2,
        )

        assert result.generations == 2
        assert result.metrics.oracle_queries == 2
