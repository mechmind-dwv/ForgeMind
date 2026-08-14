from forgemind.cegar import (
    check_pair,
    generate_domains,
)
from forgemind.core import Node


def test_cegar_finds_known_semantic_equivalence():
    left = [
        Node("U", "rev"),
        Node("U", "sort"),
    ]

    right = [
        Node("U", "sort"),
    ]

    result = check_pair(left, right)

    assert result.status == "BOUNDED_SURVIVOR"
    assert result.first_counterexample is None
    assert result.levels_checked == 4
    assert result.explanation_rule == "sort-after-reversal"


def test_cegar_finds_counterexample():
    left = [
        Node("U", "rev"),
    ]

    right = [
        Node("U", "neg"),
    ]

    result = check_pair(left, right)

    assert result.status == "NOT_EQUIVALENT"
    assert result.first_counterexample is not None
    assert result.falsification_cost > 0


def test_domain_ladder_is_progressive():
    domains = generate_domains()

    assert len(domains) == 4

    assert domains[0].size < domains[1].size
    assert domains[1].size < domains[2].size
    assert domains[2].size < domains[3].size


def test_counterexample_is_recorded_once():
    left = [
        Node("U", "rev"),
    ]

    right = [
        Node("U", "neg"),
    ]

    result = check_pair(left, right)

    assert result.first_counterexample is not None
    assert result.left_output is not None
    assert result.right_output is not None
    assert result.left_output != result.right_output
