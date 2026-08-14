from forgemind.core import Node
from forgemind.equivalence import (
    bounded_equivalence,
    canonical_equivalence,
    integer_domain,
    prove_equivalence,
)


def test_identical_programs_are_canonically_equivalent():
    p = [Node("U", "rev")]

    result = canonical_equivalence(p, list(p))

    assert result.status == "EQUIVALENT"
    assert result.method == "canonical"


def test_different_programs_are_not_claimed_formally_equivalent():
    left = [Node("U", "rev")]
    right = [Node("U", "neg")]

    result = canonical_equivalence(left, right)

    assert result.status == "UNKNOWN"


def test_bounded_equivalence_detects_counterexample():
    left = [Node("U", "rev")]
    right = [Node("U", "neg")]

    domain = integer_domain(
        values=(-1, 0, 1),
        lengths=(3,),
    )

    result = bounded_equivalence(
        left,
        right,
        domain,
    )

    assert result.status == "NOT_EQUIVALENT"
    assert result.counterexample is not None
    assert result.cases_checked > 0


def test_bounded_equivalence_accepts_identical_behavior():
    left = [Node("U", "rev")]
    right = [Node("U", "rev")]

    domain = integer_domain(
        values=(-1, 0, 1),
        lengths=(2, 3),
    )

    result = bounded_equivalence(
        left,
        right,
        domain,
    )

    assert result.status == "BOUNDED_EQUIVALENT"
    assert result.cases_checked == 36


def test_prove_equivalence_uses_bounded_search():
    left = [Node("U", "rev")]
    right = [Node("U", "neg")]

    result = prove_equivalence(
        left,
        right,
        domain=[
            [1, 2, 3],
            [-1, 0, 2],
        ],
    )

    assert result.status == "NOT_EQUIVALENT"
    assert result.method == "bounded"


def test_unknown_without_proof_or_domain():
    left = [Node("U", "rev")]
    right = [Node("U", "sort")]

    result = prove_equivalence(left, right)

    assert result.status == "UNKNOWN"


def test_semantically_equivalent_programs_can_differ_syntactically():
    # sort(rev(x)) == sort(x) on this integer-list domain.
    # The programs are syntactically different but semantically equivalent.
    left = [
        Node("U", "rev"),
        Node("U", "sort"),
    ]

    right = [
        Node("U", "sort"),
    ]

    assert left != right

    domain = integer_domain(
        values=(-1, 0, 1),
        lengths=(2, 3),
    )

    result = bounded_equivalence(
        left,
        right,
        domain,
    )

    assert result.status == "BOUNDED_EQUIVALENT"
    assert result.cases_checked == 36


def test_sort_is_idempotent_over_bounded_domain():
    left = [
        Node("U", "sort"),
    ]

    right = [
        Node("U", "sort"),
        Node("U", "sort"),
    ]

    assert left != right

    domain = integer_domain(
        values=(-1, 0, 1),
        lengths=(2, 3),
    )

    result = bounded_equivalence(
        left,
        right,
        domain,
    )

    assert result.status == "BOUNDED_EQUIVALENT"
    assert result.cases_checked == 36


def test_reverse_then_sort_matches_sort_over_bounded_domain():
    left = [
        Node("U", "sort"),
    ]

    right = [
        Node("U", "rev"),
        Node("U", "sort"),
    ]

    domain = integer_domain(
        values=(-1, 0, 1),
        lengths=(2, 3),
    )

    result = bounded_equivalence(
        left,
        right,
        domain,
    )

    assert result.status == "BOUNDED_EQUIVALENT"
    assert result.cases_checked == 36
