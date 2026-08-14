import random

from forgemind.core import Hyp, Node, TARGETS, run
from benchmarks.discovery.active_vs_passive_v2 import (
    _program,
    choose_active,
    choose_passive,
    disagreement,
    eliminate,
    run_trial,
    signature,
)


def test_signature_is_stable_for_the_same_program():
    program = [Node("U", "rev")]
    probes = [[1, 2, 3], [4, 5]]

    assert signature(program, probes) == signature(program, probes)


def test_signature_differs_for_different_programs():
    probes = [[1, 2, 3], [4, 5]]

    a = signature([Node("U", "rev")], probes)
    b = signature([Node("U", "neg")], probes)

    assert a != b


def test_program_extracts_p_attribute_from_hyp():
    h = Hyp([Node("U", "rev")])

    assert _program(h) == h.p


def test_program_returns_raw_list_when_not_a_hyp():
    program = [Node("U", "rev")]

    assert _program(program) is program


def test_disagreement_counts_unique_outputs_minus_one():
    programs = [
        [Node("U", "rev")],
        [Node("U", "neg")],
        [Node("U", "sort")],
    ]

    # For x = [1, -2, 3] all three programs disagree, so there are
    # 3 unique outputs -> disagreement == 3 - 1 == 2.
    assert disagreement(programs, [1, -2, 3]) == 2


def test_disagreement_is_zero_when_all_programs_agree():
    programs = [
        [Node("U", "rev")],
        [Node("U", "rev")],
    ]

    assert disagreement(programs, [1, 2, 3]) == 0


def test_disagreement_accepts_hyp_instances():
    programs = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "neg")]),
    ]

    assert disagreement(programs, [1, -2, 3]) == 1


def test_choose_active_selects_the_most_discriminative_candidate():
    programs = [
        [Node("U", "rev")],
        [Node("U", "neg")],
        [Node("U", "sort")],
        [Node("U", "abs")],
    ]

    candidates = [
        [1, 1, 1],   # no disagreement
        [1, -2, 3],  # full disagreement
    ]

    assert choose_active(programs, candidates) == [1, -2, 3]


def test_choose_passive_returns_a_candidate_from_the_list():
    candidates = [[1, 2, 3], [4, 5]]

    probe = choose_passive(random.Random(1), candidates)

    assert probe in candidates


def test_choose_passive_is_deterministic_given_seed():
    candidates = [[1, 2, 3], [4, 5], [6, 7, 8]]

    a = choose_passive(random.Random(7), candidates)
    b = choose_passive(random.Random(7), candidates)

    assert a == b


def test_eliminate_keeps_only_programs_matching_the_target():
    target = [Node("U", "rev")]

    programs = [
        [Node("U", "rev")],
        [Node("U", "neg")],
    ]

    survivors = eliminate(programs, target, [1, 2, 3])

    assert survivors == [[Node("U", "rev")]]


def test_eliminate_keeps_all_when_every_program_matches():
    target = [Node("U", "neg")]

    programs = [
        [Node("U", "neg")],
        [Node("P", "mul", -1)],
    ]

    survivors = eliminate(programs, target, [1, 2, 3])

    assert len(survivors) == 2


def test_run_trial_returns_expected_keys_and_bounds():
    result = run_trial(seed=3, target_index=0, budget=3)

    expected_keys = {
        "seed",
        "target",
        "budget",
        "initial_hypotheses",
        "active_survivors",
        "passive_survivors",
        "active_eliminations",
        "passive_eliminations",
        "active_isolated",
        "passive_isolated",
        "active_trace",
        "passive_trace",
    }

    assert set(result.keys()) == expected_keys
    assert result["seed"] == 3
    assert result["target"] == 0
    assert result["budget"] == 3
    assert 0 <= result["active_survivors"] <= result["initial_hypotheses"]
    assert 0 <= result["passive_survivors"] <= result["initial_hypotheses"]
    assert (
        result["active_eliminations"]
        == result["initial_hypotheses"] - result["active_survivors"]
    )
    assert (
        result["passive_eliminations"]
        == result["initial_hypotheses"] - result["passive_survivors"]
    )


def test_run_trial_is_deterministic_given_seed():
    a = run_trial(seed=11, target_index=1, budget=4)
    b = run_trial(seed=11, target_index=1, budget=4)

    assert a == b


def test_run_trial_includes_target_in_initial_pool():
    # The target itself is always included alongside the distractors,
    # so the initial pool size is always at least 1.
    result = run_trial(seed=29, target_index=2, budget=1)

    assert result["initial_hypotheses"] >= 1


def test_run_trial_active_isolated_flag_matches_survivor_count():
    result = run_trial(seed=3, target_index=0, budget=8)

    assert result["active_isolated"] == (result["active_survivors"] == 1)
    assert result["passive_isolated"] == (result["passive_survivors"] == 1)