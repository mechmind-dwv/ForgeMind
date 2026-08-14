import random

from forgemind.core import Node, run
from benchmarks.adversarial.arena import (
    CaseResult,
    accuracy,
    adversarial_inputs,
    first_counterexample,
    random_inputs,
    run_case,
)


def test_accuracy_perfect_program():
    target = [Node("U", "rev")]
    inputs = [[1, 2, 3], [4, 5], [-1, 7, 9]]

    assert accuracy(target, target, inputs) == 1.0


def test_counterexample_is_found():
    target = [Node("U", "rev")]
    wrong = [Node("U", "neg")]

    inputs = [
        [1, 2, 3],
        [-4, 5],
    ]

    assert first_counterexample(wrong, target, inputs) == 0


def test_accuracy_detects_failure():
    target = [Node("U", "rev")]
    wrong = [Node("U", "neg")]

    inputs = [[1, 2, 3]]

    assert accuracy(wrong, target, inputs) == 0.0


def test_accuracy_on_empty_input_set_is_perfect_by_convention():
    target = [Node("U", "rev")]
    wrong = [Node("U", "neg")]

    assert accuracy(wrong, target, []) == 1.0


def test_first_counterexample_returns_none_when_programs_agree():
    target = [Node("U", "rev")]

    assert first_counterexample(target, target, [[1, 2, 3], [4, 5]]) is None


def test_random_inputs_returns_requested_count():
    rng = random.Random(1)

    inputs = random_inputs(rng, count=15)

    assert len(inputs) == 15


def test_adversarial_inputs_returns_only_mismatching_inputs():
    target = [Node("U", "rev")]
    wrong = [Node("U", "neg")]

    found, tested = adversarial_inputs(
        wrong,
        target,
        random.Random(2),
        count=10,
        candidates=20,
    )

    assert len(found) == 10
    assert tested > 0
    assert all(run(wrong, x) != run(target, x) for x in found)


def test_adversarial_inputs_finds_nothing_for_identical_programs():
    target = [Node("U", "rev")]

    found, tested = adversarial_inputs(
        target,
        target,
        random.Random(3),
        count=5,
        candidates=10,
    )

    assert found == []
    # The search stops once `tested` reaches count * 20, rounded up to
    # the nearest multiple of `candidates`.
    assert tested == 100


def test_run_case_returns_case_result_with_expected_fields():
    result = run_case(3, 0)

    assert isinstance(result, CaseResult)
    assert result.seed == 3
    assert result.target == 0
    assert 0.0 <= result.random_accuracy <= 1.0
    assert 0.0 <= result.adversarial_accuracy <= 1.0
    assert result.discovery_tested > 0
    assert 0 <= result.discovery_found <= result.discovery_tested
    assert 0.0 <= result.discovery_rate <= 1.0


def test_run_case_is_deterministic_given_seed_and_target():
    a = run_case(11, 1)
    b = run_case(11, 1)

    assert a == b


def test_main_writes_results_json(tmp_path, monkeypatch):
    import json

    import benchmarks.adversarial.arena as arena

    # Shrink the search space so the full CLI entrypoint stays fast.
    monkeypatch.setattr(arena, "TARGETS", arena.TARGETS[:1])

    monkeypatch.chdir(tmp_path)
    (tmp_path / "benchmarks" / "adversarial").mkdir(parents=True)

    arena.main()

    output = tmp_path / "benchmarks" / "adversarial" / "results.json"
    assert output.exists()

    data = json.loads(output.read_text())

    assert data["version"] == "0.9.1-adversarial"
    assert data["cases"] == 4  # 4 seeds x 1 target
    assert len(data["results"]) == 4
    assert 0.0 <= data["discovery_rate"] <= 1.0
