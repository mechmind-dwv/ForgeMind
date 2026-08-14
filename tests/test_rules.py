from forgemind.core import Node
from forgemind.rules import explain_pair


def test_sort_idempotence():
    left = [
        Node("U", "sort"),
        Node("U", "sort"),
    ]
    right = [
        Node("U", "sort"),
    ]

    rule = explain_pair(left, right)

    assert rule is not None
    assert rule.name == "sort-idempotence"


def test_sort_after_reversal():
    left = [
        Node("U", "rev"),
        Node("U", "sort"),
    ]
    right = [
        Node("U", "sort"),
    ]

    rule = explain_pair(left, right)

    assert rule is not None
    assert rule.name == "sort-after-reversal"


def test_commutation():
    left = [
        Node("U", "rev"),
        Node("U", "neg"),
    ]
    right = [
        Node("U", "neg"),
        Node("U", "rev"),
    ]

    rule = explain_pair(left, right)

    assert rule is not None
    assert rule.name == "rev-neg-commutation"


def test_unknown_equivalence_has_no_forced_explanation():
    left = [
        Node("U", "rev"),
    ]
    right = [
        Node("U", "neg"),
    ]

    assert explain_pair(left, right) is None
