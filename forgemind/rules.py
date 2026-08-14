"""
ForgeMind 0.12 — Structural Explanation Engine.

Rules discovered here are explanations, not unrestricted proofs.
Every rule must ultimately be validated independently.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Optional

from .core import Node, canon


@dataclass(frozen=True)
class StructuralRule:
    name: str
    family: str
    pattern: str
    explanation: str


RULES = (
    StructuralRule(
        name="sort-idempotence",
        family="idempotence",
        pattern="sort(sort(x)) == sort(x)",
        explanation="Applying sort twice has the same effect as applying it once.",
    ),
    StructuralRule(
        name="sort-after-reversal",
        family="permutation-invariance",
        pattern="sort(rev(x)) == sort(x)",
        explanation="Sorting removes the ordering information introduced by reversal.",
    ),
    StructuralRule(
        name="rev-involution",
        family="involution",
        pattern="rev(rev(x)) == x",
        explanation="Reversal is its own inverse.",
    ),
    StructuralRule(
        name="neg-involution",
        family="involution",
        pattern="neg(neg(x)) == x",
        explanation="Negation is its own inverse.",
    ),
    StructuralRule(
        name="rev-neg-commutation",
        family="commutation",
        pattern="rev(neg(x)) == neg(rev(x))",
        explanation="Reversal acts on positions while negation acts on values.",
    ),
)


def _names(program: list[Node]) -> tuple[str, ...]:
    return tuple(node.name for node in program)


def explain_pair(
    left: list[Node],
    right: list[Node],
) -> Optional[StructuralRule]:
    """
    Return a structural explanation for a known equivalence pattern.

    This function deliberately does not claim mathematical completeness.
    Unknown equivalences return None.
    """

    a = _names(left)
    b = _names(right)

    # Idempotence.
    if a == ("sort", "sort") and b == ("sort",):
        return RULES[0]

    if b == ("sort", "sort") and a == ("sort",):
        return RULES[0]

    # Sorting destroys permutation information.
    if a == ("rev", "sort") and b == ("sort",):
        return RULES[1]

    if b == ("rev", "sort") and a == ("sort",):
        return RULES[1]

    # Involutions.
    if a == ("rev", "rev") and not b:
        return RULES[2]

    if b == ("rev", "rev") and not a:
        return RULES[2]

    if a == ("neg", "neg") and not b:
        return RULES[3]

    if b == ("neg", "neg") and not a:
        return RULES[3]

    # Commutation.
    if {
        a,
        b,
    } == {
        ("rev", "neg"),
        ("neg", "rev"),
    }:
        return RULES[4]

    return None


def explain_canonical_pair(
    left: list[Node],
    right: list[Node],
) -> Optional[StructuralRule]:
    """
    Convenience wrapper.

    Canonically identical programs need no structural explanation.
    """
    if canon(left) == canon(right):
        return None

    return explain_pair(left, right)
