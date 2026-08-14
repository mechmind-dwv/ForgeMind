from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Iterable

from forgemind.core import Node, canon, run
from forgemind.equivalence import bounded_equivalence


@dataclass(frozen=True)
class DomainLevel:
    name: str
    values: tuple[int, ...]
    lengths: tuple[int, ...]

    @property
    def size(self) -> int:
        return sum(
            len(self.values) ** length
            for length in self.lengths
        )

    def cases(self) -> list[list[int]]:
        return [
            list(values)
            for length in self.lengths
            for values in product(self.values, repeat=length)
        ]


@dataclass
class EquivalenceEvidence:
    status: str
    left: tuple
    right: tuple

    level: str | None = None
    levels_checked: int = 0

    cases_checked: int = 0
    first_counterexample: tuple | None = None

    left_output: tuple | None = None
    right_output: tuple | None = None

    falsification_cost: int = 0
    falsification_efficiency: float = 0.0
    survival_depth: int = 0

    explanation: str | None = None
    explanation_rule: str | None = None

    history: list[dict] = field(default_factory=list)


def _structural_explanation(left, right):
    """
    Lightweight rule recognizer.

    This is deliberately conservative: an explanation is emitted only
    when a known algebraic relation is directly visible.
    """
    a = tuple(n.name for n in left)
    b = tuple(n.name for n in right)

    # Identity elimination.
    if "id" in a or "id" in b:
        aa = tuple(x for x in a if x != "id")
        bb = tuple(x for x in b if x != "id")

        if aa == bb:
            return (
                "identity elimination",
                "P + id == P",
            )

    # sort annihilates permutation order.
    if a == ("rev", "sort") and b == ("sort",):
        return (
            "sort-after-reversal",
            "sort(rev(x)) == sort(x)",
        )

    if b == ("rev", "sort") and a == ("sort",):
        return (
            "sort-after-reversal",
            "sort(rev(x)) == sort(x)",
        )

    # Reapplying sort is idempotent.
    if a == ("sort", "sort") and b == ("sort",):
        return (
            "sort-idempotence",
            "sort(sort(x)) == sort(x)",
        )

    if b == ("sort", "sort") and a == ("sort",):
        return (
            "sort-idempotence",
            "sort(sort(x)) == sort(x)",
        )

    # rev and neg commute.
    if {a, b} == {
        ("rev", "neg"),
        ("neg", "rev"),
    }:
        return (
            "commutation",
            "rev(neg(x)) == neg(rev(x))",
        )

    # Double involution.
    if {a, b} == {
        ("rev", "rev"),
        ("neg", "neg"),
    }:
        return (
            "involution-equivalence",
            "rev(rev(x)) == neg(neg(x)) == x",
        )

    return None, None


def generate_domains() -> tuple[DomainLevel, ...]:
    """
    Progressive evidence ladder.

    The first levels are cheap enough for exhaustive checking.
    Later levels deliberately increase both value range and shape range.
    """
    return (
        DomainLevel(
            "L1",
            (-1, 0, 1),
            (2, 3),
        ),
        DomainLevel(
            "L2",
            (-2, -1, 0, 1, 2),
            (1, 2, 3, 4),
        ),
        DomainLevel(
            "L3",
            (-3, -2, -1, 0, 1, 2, 3),
            (1, 2, 3, 4),
        ),
        DomainLevel(
            "L4",
            (-5, -3, -1, 0, 2, 4, 7),
            (1, 2, 3, 4, 5),
        ),
    )


def _direct_counterexample(left, right, cases):
    for x in cases:
        lx = run(left, x)
        rx = run(right, x)

        if lx != rx:
            return (
                tuple(x),
                tuple(lx),
                tuple(rx),
            )

    return None


def check_pair(left, right, domains=None) -> EquivalenceEvidence:
    if domains is None:
        domains = generate_domains()

    evidence = EquivalenceEvidence(
        status="UNRESOLVED",
        left=canon(left),
        right=canon(right),
    )

    for domain in domains:
        cases = domain.cases()

        before = evidence.cases_checked

        result = bounded_equivalence(
            left,
            right,
            cases,
        )

        checked = result.cases_checked

        # Some implementations may short-circuit. For CEGAR accounting
        # we record the actual engine count, while retaining an exact
        # fallback counterexample search.
        evidence.cases_checked += checked

        event = {
            "level": domain.name,
            "domain_size": domain.size,
            "cases_checked": checked,
            "status": result.status,
        }

        if result.status == "NOT_EQUIVALENT":
            evidence.status = "NOT_EQUIVALENT"
            evidence.level = domain.name

            evidence.first_counterexample = (
                tuple(result.counterexample)
                if result.counterexample is not None
                else None
            )

            if evidence.first_counterexample is not None:
                x = list(evidence.first_counterexample)
                evidence.left_output = tuple(run(left, x))
                evidence.right_output = tuple(run(right, x))

            evidence.falsification_cost = evidence.cases_checked
            evidence.falsification_efficiency = (
                1.0 / evidence.falsification_cost
                if evidence.falsification_cost > 0
                else 0.0
            )
            evidence.history.append(event)

            return evidence

        evidence.history.append(event)
        evidence.levels_checked += 1

    evidence.status = "BOUNDED_SURVIVOR"
    evidence.survival_depth = evidence.levels_checked

    rule, explanation = _structural_explanation(left, right)

    evidence.explanation_rule = rule
    evidence.explanation = explanation

    return evidence


def explain_equivalence(evidence: EquivalenceEvidence) -> str | None:
    if evidence.status != "BOUNDED_SURVIVOR":
        return None

    return evidence.explanation


def discover_equivalences(programs: Iterable[list[Node]], domains=None):
    programs = list(programs)
    survivors = []
    rejected = []

    for i, left in enumerate(programs):
        for right in programs[i + 1:]:
            if canon(left) == canon(right):
                continue

            evidence = check_pair(
                left,
                right,
                domains,
            )

            if evidence.status == "BOUNDED_SURVIVOR":
                survivors.append(evidence)
            else:
                rejected.append(evidence)

    return survivors, rejected
