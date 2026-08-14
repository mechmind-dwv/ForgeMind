import math
import random

import pytest

from forgemind.active import (
    _prediction_signature,
    _safe_output,
    build_distractors,
    falsify_once,
    information_gain,
    partition_hypotheses,
    passive_experiment,
    select_experiment,
    select_informative_probe,
    run_active_protocol,
    run_passive_protocol,
)
from forgemind.core import Hyp, Node, TARGETS, canon, run


def test_partition_hypotheses_separates_predictions():
    pool = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "neg")]),
    ]

    partitions = partition_hypotheses(pool, [1, 2, 3])

    assert len(partitions) == 2


def test_information_gain_is_positive_when_predictions_disagree():
    pool = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "neg")]),
    ]

    gain = information_gain(pool, [1, 2, 3])

    assert gain > 0.0


def test_select_experiment_is_deterministic():
    pool = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "neg")]),
    ]

    a = select_experiment(
        pool,
        random.Random(123),
        budget=20,
    )

    b = select_experiment(
        pool,
        random.Random(123),
        budget=20,
    )

    assert a == b


def test_distractors_do_not_include_target():
    target = TARGETS[0]

    pool = build_distractors(
        target,
        seed=123,
        count=20,
    )

    from forgemind.core import canon

    target_repr = canon(target)

    for h in pool:
        assert canon(h.p) != target_repr


def test_active_protocol_is_reproducible():
    a = run_active_protocol(
        target_index=0,
        seed=123,
        rounds=10,
        population=20,
        candidate_budget=16,
    )

    b = run_active_protocol(
        target_index=0,
        seed=123,
        rounds=10,
        population=20,
        candidate_budget=16,
    )

    assert a == b


def test_active_protocol_performs_queries():
    result = run_active_protocol(
        target_index=0,
        seed=123,
        rounds=8,
        population=20,
        candidate_budget=16,
    )

    assert result.oracle_queries > 0
    assert result.eliminations >= 0


def test_passive_protocol_performs_queries():
    result = run_passive_protocol(
        target_index=0,
        seed=123,
        rounds=8,
        population=20,
    )

    assert result.oracle_queries > 0
    assert result.eliminations >= 0


def test_active_search_prefers_information_gain():
    from forgemind.core import Node, run
    from forgemind.active import select_informative_probe

    hypotheses = [
        [Node("U", "rev")],
        [Node("U", "neg")],
        [Node("U", "sort")],
    ]

    candidates = [
        [1, 2, 3],
        [3, 1, 2],
        [-2, 7, 0],
    ]

    probe = select_informative_probe(
        hypotheses,
        candidates,
    )

    assert probe in candidates


def test_semantically_equivalent_programs_have_same_signature():
    from forgemind.core import Node, run

    probes = [
        [1, 2, 3],
        [-5, 0, 4],
        [9, -2],
    ]

    a = [
        Node("U", "rev"),
    ]

    # rev -> rev -> rev == rev
    b = [
        Node("U", "rev"),
        Node("U", "rev"),
        Node("U", "rev"),
    ]

    assert [
        run(a, x)
        for x in probes
    ] == [
        run(b, x)
        for x in probes
    ]


# ---------------------------------------------------------------------------
# _safe_output() / _prediction_signature()
# ---------------------------------------------------------------------------


def test_safe_output_converts_nested_lists_to_tuples():
    assert _safe_output([1, 2, [3, 4]]) == (1, 2, (3, 4))


def test_safe_output_converts_tuples_recursively():
    assert _safe_output((1, (2, 3))) == (1, (2, 3))


def test_safe_output_normalizes_dicts_to_sorted_tuples():
    assert _safe_output({"b": 2, "a": 1}) == (("a", 1), ("b", 2))


def test_safe_output_passes_through_scalars():
    assert _safe_output(5) == 5


def test_prediction_signature_captures_exception_details():
    bad = Hyp([Node("U", "not-a-real-op")])

    signature = _prediction_signature(bad, [1, 2, 3])

    assert signature == ("__ERROR__", "ValueError", "not-a-real-op")


def test_prediction_signature_matches_direct_run_for_valid_program():
    h = Hyp([Node("U", "rev")])

    assert _prediction_signature(h, [1, 2, 3]) == _safe_output(
        run(h.p, [1, 2, 3])
    )


# ---------------------------------------------------------------------------
# partition_hypotheses() / information_gain()
# ---------------------------------------------------------------------------


def test_partition_hypotheses_groups_identical_predictions_together():
    pool = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "rev"), Node("U", "rev"), Node("U", "rev")]),
        Hyp([Node("U", "neg")]),
    ]

    partitions = partition_hypotheses(pool, [1, 2, 3])

    assert len(partitions) == 2
    assert sum(len(group) for group in partitions.values()) == 3


def test_information_gain_is_zero_when_pool_fully_agrees():
    pool = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "rev")]),
    ]

    assert information_gain(pool, [1, 2, 3]) == 0.0


def test_information_gain_is_zero_for_empty_pool():
    assert information_gain([], [1, 2, 3]) == 0.0


def test_information_gain_matches_shannon_entropy_for_fully_split_pool():
    pool = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "neg")]),
        Hyp([Node("U", "sort")]),
        Hyp([Node("U", "abs")]),
    ]

    # This input makes all four programs disagree, producing four
    # equally sized partitions and maximal entropy of log2(4).
    x = [1, -2, 3]

    assert information_gain(pool, x) == pytest.approx(math.log2(4))


# ---------------------------------------------------------------------------
# select_experiment() / passive_experiment()
# ---------------------------------------------------------------------------


def test_select_experiment_raises_on_empty_pool():
    with pytest.raises(ValueError):
        select_experiment([], random.Random(1), budget=4)


def test_select_experiment_returns_a_non_negative_gain():
    pool = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "neg")]),
    ]

    x, gain = select_experiment(pool, random.Random(42), budget=10)

    assert isinstance(x, list)
    assert gain >= 0.0


def test_passive_experiment_is_deterministic_given_seed():
    a = passive_experiment(random.Random(99))
    b = passive_experiment(random.Random(99))

    assert a == b


# ---------------------------------------------------------------------------
# falsify_once()
# ---------------------------------------------------------------------------


def test_falsify_once_eliminates_disagreeing_hypotheses():
    target = [Node("U", "rev")]
    pool = [
        Hyp(target),
        Hyp([Node("U", "neg")]),
    ]

    y, eliminated = falsify_once(pool, target, [1, 2, 3])

    assert y == [3, 2, 1]
    assert eliminated == 1
    assert len(pool) == 1
    assert pool[0].p == target


def test_falsify_once_keeps_all_hypotheses_when_all_agree():
    target = [Node("U", "neg")]
    pool = [
        Hyp([Node("U", "neg")]),
        Hyp([Node("P", "mul", -1)]),
    ]

    y, eliminated = falsify_once(pool, target, [1, 2, 3])

    assert eliminated == 0
    assert len(pool) == 2


def test_falsify_once_treats_raising_hypothesis_as_a_failure():
    target = [Node("U", "rev")]
    bad = Hyp([Node("U", "not-a-real-op")])
    pool = [bad]

    y, eliminated = falsify_once(pool, target, [1, 2, 3])

    assert eliminated == 1
    assert len(pool) == 0
    assert bad.failures == 1
    assert bad.evaluations == 1


def test_falsify_once_increments_evaluations_for_every_hypothesis():
    target = [Node("U", "rev")]
    survivor = Hyp(target)
    loser = Hyp([Node("U", "neg")])
    pool = [survivor, loser]

    falsify_once(pool, target, [1, 2, 3])

    assert survivor.evaluations == 1
    assert survivor.support == 1
    assert loser.evaluations == 1
    assert loser.failures == 1


# ---------------------------------------------------------------------------
# build_distractors()
# ---------------------------------------------------------------------------


def test_build_distractors_returns_requested_count():
    pool = build_distractors(TARGETS[0], seed=42, count=10)

    assert len(pool) == 10


def test_build_distractors_is_deterministic_given_seed():
    a = build_distractors(TARGETS[0], seed=42, count=10)
    b = build_distractors(TARGETS[0], seed=42, count=10)

    assert [canon(h.p) for h in a] == [canon(h.p) for h in b]


def test_build_distractors_produces_unique_programs():
    pool = build_distractors(TARGETS[0], seed=42, count=10)

    canon_forms = [canon(h.p) for h in pool]

    assert len(canon_forms) == len(set(canon_forms))


# ---------------------------------------------------------------------------
# run_active_protocol() / run_passive_protocol() edge cases
# ---------------------------------------------------------------------------


def test_active_protocol_returns_infinite_complexity_when_pool_is_exhausted():
    # A tiny population with many rounds reliably eliminates every
    # distractor for this seed/target combination, leaving no survivors.
    result = run_active_protocol(
        target_index=0,
        seed=5,
        rounds=20,
        population=3,
        candidate_budget=8,
    )

    assert result.survivor_count == 0
    assert result.program == ()
    assert result.complexity == float("inf")


def test_passive_protocol_is_reproducible():
    a = run_passive_protocol(
        target_index=1,
        seed=321,
        rounds=10,
        population=20,
    )

    b = run_passive_protocol(
        target_index=1,
        seed=321,
        rounds=10,
        population=20,
    )

    assert a == b


# ---------------------------------------------------------------------------
# select_informative_probe()
# ---------------------------------------------------------------------------


def test_select_informative_probe_chooses_highest_entropy_candidate():
    hypotheses = [
        [Node("U", "rev")],
        [Node("U", "neg")],
        [Node("U", "sort")],
        [Node("U", "abs")],
    ]

    # [1, 1, 1] produces identical output for every hypothesis (no
    # information). [1, -2, 3] fully separates all four hypotheses.
    candidates = [
        [1, 1, 1],
        [1, -2, 3],
    ]

    probe = select_informative_probe(hypotheses, candidates)

    assert probe == [1, -2, 3]


def test_select_informative_probe_accepts_raw_program_lists():
    hypotheses = [
        [Node("U", "rev")],
        [Node("U", "neg")],
    ]

    probe = select_informative_probe(hypotheses, [[1, 2, 3], [4, 5]])

    assert probe in [[1, 2, 3], [4, 5]]


def test_select_informative_probe_raises_on_empty_hypotheses():
    with pytest.raises(ValueError):
        select_informative_probe([], [[1, 2, 3]])


def test_select_informative_probe_raises_on_empty_candidates():
    with pytest.raises(ValueError):
        select_informative_probe([[Node("U", "rev")]], [])
