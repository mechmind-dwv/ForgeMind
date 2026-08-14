import random

import pytest

from forgemind.core import (
    Hyp,
    Node,
    TARGETS,
    apply,
    benchmark,
    canon,
    complexity,
    crossover,
    disagreement,
    evolve,
    falsify,
    generator,
    mutate,
    rand_node,
    run,
    xgen,
)
def test_compose():
    p = [Node("U", "rev"), Node("U", "neg")]
    assert run(p, [1, -2, 3]) == [-3, 2, -1]


def test_param():
    assert run([Node("P", "add", 2)], [1, 3]) == [3, 5]


def test_deterministic():
    a = evolve(
        5,
        [Node("U", "rev")],
        8,
        25,
    )[1]

    b = evolve(
        5,
        [Node("U", "rev")],
        8,
        25,
    )[1]

    assert a == b


def test_evolution_returns_evaluated_hypothesis():
    best, history = evolve(
        5,
        [Node("U", "rev")],
        8,
        25,
    )

    assert best.evaluated
    assert best.evaluations > 0


def test_exact_target_can_survive():
    target = [
        Node("U", "abs"),
        Node("P", "add", 1),
    ]

    best, history = evolve(
        29 * 100 + 4,
        target,
        42,
        70,
    )

    probes = [
        [0, 1, 2],
        [-3, -1, 4],
        [5, 0, -2, 7],
    ]

    assert best.evaluated
    assert all(run(best.p, x) == run(target, x) for x in probes)


def test_elite_evaluation_is_preserved():
    target = [Node("U", "rev")]

    best, history = evolve(
        5,
        target,
        8,
        25,
    )

    assert best.evaluated
    assert best.evaluations > 0
    assert best.support + best.failures == best.evaluations


def test_adversarial_accuracy_is_not_failure_only():
    from benchmarks.adversarial.arena import accuracy

    target = [Node("U", "rev")]
    program = [Node("U", "neg")]

    inputs = [
        [1, 2, 3],
        [3, 2, 1],
    ]

    # The suite is an independent evaluation set.
    # It must not be constructed by filtering only mismatches.
    assert accuracy(program, target, inputs) == 0.0


def test_behavior_distance_exact():
    from forgemind.core import behavior_distance

    assert behavior_distance([1, 2, 3], [1, 2, 3]) == 0.0


def test_behavior_distance_prefers_closer_output():
    from forgemind.core import behavior_distance

    close = behavior_distance(
        [1, 2, 4],
        [1, 2, 3],
    )

    far = behavior_distance(
        [10, 20, 30],
        [1, 2, 3],
    )

    assert close < far


def test_behavior_distance_detects_length_difference():
    from forgemind.core import behavior_distance

    assert behavior_distance(
        [1, 2],
        [1, 2, 3],
    ) > 0.0

def test_discovery_rate_records_zero_when_nothing_found():
    from benchmarks.adversarial.arena import adversarial_inputs

    target = [Node("U", "rev")]
    program = target

    found, tested = adversarial_inputs(
        program,
        target,
        random.Random(123),
        count=10,
        candidates=5,
    )

    assert found == []
    assert tested > 0


def test_behaviorally_correct_solution_prefers_lower_complexity():
    from forgemind.core import complexity, behavior_distance

    target = [
        Node("U", "abs"),
        Node("P", "add", 1),
    ]

    redundant = [
        Node("U", "abs"),
        Node("U", "abs"),
        Node("P", "add", 1),
    ]

    assert behavior_distance(
        run(target, [-3, -1, 4]),
        run(redundant, [-3, -1, 4]),
    ) == 0.0

    assert complexity(target) < complexity(redundant)


def test_behaviorally_equivalent_neg_and_mul_minus_one():
    from forgemind.core import behavior_distance

    a = [
        Node("U", "neg"),
    ]

    b = [
        Node("P", "mul", -1),
    ]

    probes = [
        [0, 1, 2],
        [-3, -1, 4],
        [5, 0, -2, 7],
    ]

    assert all(
        behavior_distance(run(a, x), run(b, x)) == 0.0
        for x in probes
    )


def test_parsimony_prefers_simpler_equivalent_program():
    target = [
        Node("U", "rev"),
    ]

    best, history = evolve(
        3,
        target,
        42,
        70,
    )

    assert best.accuracy == 1.0
    assert run(best.p, [1, 2, 3]) == [3, 2, 1]

    # The synthesized solution should not contain gratuitous
    # operations when a simpler equivalent program exists.
    assert complexity(best.p) <= complexity(target) + 0.2


def test_parsimony_prefers_minimal_add():
    target = [
        Node("P", "add", 2),
    ]

    best, history = evolve(
        3 * 100 + 2,
        target,
        42,
        70,
    )

    assert best.accuracy == 1.0
    assert run(best.p, [1, 3, -2]) == [3, 5, 0]
    assert complexity(best.p) <= complexity(target) + 0.2


def test_target_behavior_is_preserved_after_synthesis():
    probes = [
        [-5, -2, 0, 3, 7],
        [-3, -1, 4],
        [0, 1, 2],
        [1, 2, 3],
        [5, 0, -2, 7],
        [9, -4, 2, 6],
    ]

    for i, target in enumerate(TARGETS):
        best, history = evolve(
            3 * 100 + i,
            target,
            42,
            70,
        )

        assert best.accuracy == 1.0

        for x in probes:
            assert run(best.p, x) == run(target, x)


# ---------------------------------------------------------------------------
# apply() / run() for individual operations
# ---------------------------------------------------------------------------


def test_apply_id_returns_unchanged_copy():
    x = [1, 2, 3]
    y = apply(Node("U", "id"), x)

    assert y == x
    assert y is not x


def test_apply_rev_reverses_sequence():
    assert apply(Node("U", "rev"), [1, 2, 3]) == [3, 2, 1]


def test_apply_neg_negates_all_values():
    assert apply(Node("U", "neg"), [1, -2, 3]) == [-1, 2, -3]


def test_apply_abs_takes_absolute_value():
    assert apply(Node("U", "abs"), [-1, 2, -3]) == [1, 2, 3]


def test_apply_sort_orders_ascending():
    assert apply(Node("U", "sort"), [3, 1, 2]) == [1, 2, 3]


def test_apply_diff_computes_consecutive_deltas():
    assert apply(Node("U", "diff"), [1, 3, 6]) == [2, 3]


def test_apply_diff_on_empty_list_returns_empty():
    assert apply(Node("U", "diff"), []) == []


def test_apply_rot_rotates_by_arg():
    assert apply(Node("P", "rot", 2), [1, 2, 3, 4, 5]) == [3, 4, 5, 1, 2]


def test_apply_rot_on_empty_list_returns_empty():
    assert apply(Node("P", "rot", 2), []) == []


def test_apply_rot_zero_arg_falls_back_to_one():
    # `n.arg or 1` treats an explicit 0 argument as falsy, so rot(0)
    # behaves the same as rot(1). This documents current behavior.
    assert apply(Node("P", "rot", 0), [1, 2, 3]) == apply(
        Node("P", "rot", 1), [1, 2, 3]
    )


def test_apply_add_shifts_values_by_arg():
    assert apply(Node("P", "add", 2), [1, 3]) == [3, 5]


def test_apply_add_zero_arg_is_identity():
    assert apply(Node("P", "add", 0), [1, 2, 3]) == [1, 2, 3]


def test_apply_mul_scales_values_by_arg():
    assert apply(Node("P", "mul", -1), [1, -2, 3]) == [-1, 2, -3]


def test_apply_mul_zero_arg_falls_back_to_one():
    # `n.arg or 1` treats an explicit 0 argument as falsy, so mul(0)
    # behaves like multiplying by 1 rather than zeroing the values.
    assert apply(Node("P", "mul", 0), [1, 2, 3]) == [1, 2, 3]


def test_apply_clip_bounds_values_symmetrically():
    assert apply(Node("P", "clip", 2), [1, 5, -5, 0]) == [1, 2, -2, 0]


def test_apply_clip_zero_arg_falls_back_to_one():
    assert apply(Node("P", "clip", 0), [1, 2, 3, -5]) == [1, 1, 1, -1]


def test_apply_unknown_operation_raises_value_error():
    with pytest.raises(ValueError):
        apply(Node("U", "not-a-real-op"), [1, 2, 3])


def test_run_composes_operations_in_order():
    p = [Node("U", "sort"), Node("U", "rev"), Node("P", "add", 1)]
    assert run(p, [3, 1, 2]) == [4, 3, 2]


def test_run_empty_program_returns_input_copy():
    x = [1, 2, 3]
    y = run([], x)

    assert y == x
    assert y is not x


# ---------------------------------------------------------------------------
# canon() / complexity()
# ---------------------------------------------------------------------------


def test_canon_removes_identity_nodes():
    p = [Node("U", "id"), Node("U", "rev"), Node("U", "id")]

    assert canon(p) == (("U", "rev", None),)


def test_canon_preserves_order_and_parameters():
    p = [Node("P", "add", 2), Node("U", "rev")]

    assert canon(p) == (
        ("P", "add", 2),
        ("U", "rev", None),
    )


def test_canon_of_empty_program_is_empty_tuple():
    assert canon([]) == ()


def test_complexity_counts_nodes_and_penalizes_parameters():
    assert complexity([Node("U", "rev")]) == 1
    assert complexity([Node("P", "add", 2)]) == 1.2
    assert complexity(
        [Node("U", "rev"), Node("P", "add", 2), Node("P", "mul", -1)]
    ) == 3.4


# ---------------------------------------------------------------------------
# rand_node() / mutate() / crossover()
# ---------------------------------------------------------------------------


def test_rand_node_produces_valid_node_kinds():
    rng = random.Random(1)

    for _ in range(50):
        node = rand_node(rng)

        assert node.kind in ("U", "P")

        if node.kind == "U":
            assert node.arg is None
        else:
            assert -3 <= node.arg <= 3


def test_mutate_never_exceeds_max_length():
    rng = random.Random(2)
    p = [Node("U", "rev")] * 10

    mutated = mutate(p, rng)

    assert len(mutated) <= 6


def test_mutate_of_empty_program_inserts_a_node():
    rng = random.Random(3)

    mutated = mutate([], rng)

    assert len(mutated) == 1
    assert isinstance(mutated[0], Node)


def test_mutate_never_returns_empty_program():
    rng = random.Random(4)
    p = [Node("U", "rev")]

    for _ in range(50):
        p = mutate(p, rng)
        assert len(p) >= 1


def test_crossover_respects_max_length():
    a = [Node("U", "rev")] * 4
    b = [Node("U", "neg")] * 4
    rng = random.Random(5)

    c = crossover(a, b, rng)

    assert len(c) <= 6


def test_crossover_of_two_empty_programs_returns_identity():
    rng = random.Random(6)

    c = crossover([], [], rng)

    assert c == [Node("U", "id")]


# ---------------------------------------------------------------------------
# xgen() / disagreement() / generator() / falsify()
# ---------------------------------------------------------------------------


def test_xgen_respects_length_and_value_bounds():
    rng = random.Random(7)

    for _ in range(20):
        x = xgen(rng)

        assert 3 <= len(x) <= 9
        assert all(-30 <= v <= 30 for v in x)


def test_disagreement_counts_unique_output_signatures():
    pool = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "neg")]),
        Hyp([Node("U", "rev")]),
    ]

    assert disagreement(pool, [1, 2, 3]) == 2


def test_disagreement_is_one_when_pool_agrees():
    pool = [
        Hyp([Node("U", "rev")]),
        Hyp([Node("U", "rev")]),
    ]

    assert disagreement(pool, [1, 2, 3]) == 1


def test_generator_creates_requested_pool_size():
    pool = generator(11, pop=15)

    assert len(pool) == 15
    assert all(isinstance(h, Hyp) for h in pool)
    assert all(1 <= len(h.p) <= 5 for h in pool)


def test_generator_is_deterministic_given_seed():
    a = generator(11, pop=15)
    b = generator(11, pop=15)

    assert [h.p for h in a] == [h.p for h in b]


def test_falsify_updates_support_and_failures_consistently():
    rng = random.Random(8)
    pool = generator(8, pop=6)
    target = TARGETS[0]

    x, y = falsify(pool, target, rng, budget=5)

    assert y == run(target, x)

    for h in pool:
        assert h.evaluations == 1
        assert h.support + h.failures == h.evaluations

        if run(h.p, x) == y:
            assert h.support == 1
        else:
            assert h.failures == 1


# ---------------------------------------------------------------------------
# Hyp dataclass helpers
# ---------------------------------------------------------------------------


def test_hyp_is_not_evaluated_before_any_falsification():
    h = Hyp([Node("U", "rev")])

    assert h.evaluated is False
    assert h.accuracy == 0.0


def test_hyp_accuracy_reflects_support_ratio():
    h = Hyp([Node("U", "rev")], support=3, failures=1, evaluations=4)

    assert h.evaluated is True
    assert h.accuracy == 0.75


# ---------------------------------------------------------------------------
# benchmark()
# ---------------------------------------------------------------------------


def test_benchmark_returns_a_row_per_seed_and_target():
    rows = benchmark(seeds=(3,))

    assert len(rows) == len(TARGETS)

    for row in rows:
        assert set(row.keys()) == {
            "seed",
            "target",
            "program",
            "support",
            "failures",
            "hidden",
        }
        assert row["seed"] == 3
        assert 0.0 <= row["hidden"] <= 1.0
