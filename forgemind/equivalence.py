"""
ForgeMind 0.11 — Formal Equivalence Engine.

The engine distinguishes:

    EQUIVALENT
        Proven by canonical representation.

    BOUNDED_EQUIVALENT
        Exhaustively equivalent over a finite test domain.

    NOT_EQUIVALENT
        A concrete counterexample was found.

    UNKNOWN
        No proof or counterexample was obtained.

The implementation deliberately separates semantic evidence
from formal proof claims.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable

from .core import Node, canon, run


@dataclass(frozen=True)
class EquivalenceResult:
    status: str
    method: str
    counterexample: tuple[int, ...] | None = None
    left_output: Any = None
    right_output: Any = None
    cases_checked: int = 0


def _safe(value: Any) -> Any:
    if isinstance(value, list):
        return tuple(_safe(v) for v in value)

    if isinstance(value, tuple):
        return tuple(_safe(v) for v in value)

    if isinstance(value, dict):
        return tuple(
            sorted(
                (k, _safe(v))
                for k, v in value.items()
            )
        )

    return value


def canonical_equivalence(
    left: list[Node],
    right: list[Node],
) -> EquivalenceResult:
    """
    Prove equivalence when both programs have identical
    canonical representations.
    """
    if canon(left) == canon(right):
        return EquivalenceResult(
            status="EQUIVALENT",
            method="canonical",
        )

    return EquivalenceResult(
        status="UNKNOWN",
        method="canonical",
    )


def bounded_equivalence(
    left: list[Node],
    right: list[Node],
    domain: Iterable[Iterable[int]],
) -> EquivalenceResult:
    """
    Exhaustively compare both programs over a finite domain.

    This is a bounded proof only. It does not establish
    unrestricted functional equivalence.
    """
    checked = 0

    for raw_x in domain:
        x = tuple(raw_x)

        try:
            left_output = _safe(run(left, list(x)))
        except Exception as exc:
            left_output = (
                "__ERROR__",
                type(exc).__name__,
                str(exc),
            )

        try:
            right_output = _safe(run(right, list(x)))
        except Exception as exc:
            right_output = (
                "__ERROR__",
                type(exc).__name__,
                str(exc),
            )

        checked += 1

        if left_output != right_output:
            return EquivalenceResult(
                status="NOT_EQUIVALENT",
                method="bounded",
                counterexample=x,
                left_output=left_output,
                right_output=right_output,
                cases_checked=checked,
            )

    return EquivalenceResult(
        status="BOUNDED_EQUIVALENT",
        method="bounded",
        cases_checked=checked,
    )


def integer_domain(
    values: Iterable[int],
    lengths: Iterable[int],
) -> list[tuple[int, ...]]:
    """
    Generate a finite integer input domain.
    """
    values = tuple(values)

    return [
        tuple(x)
        for length in lengths
        for x in product(values, repeat=length)
    ]


def prove_equivalence(
    left: list[Node],
    right: list[Node],
    domain: Iterable[Iterable[int]] | None = None,
) -> EquivalenceResult:
    """
    Main equivalence pipeline.

    1. Try canonical equivalence.
    2. If a finite domain is supplied, perform exhaustive checking.
    3. Otherwise return UNKNOWN.
    """
    canonical = canonical_equivalence(left, right)

    if canonical.status == "EQUIVALENT":
        return canonical

    if domain is None:
        return EquivalenceResult(
            status="UNKNOWN",
            method="no-proof",
        )

    return bounded_equivalence(
        left,
        right,
        domain,
    )
