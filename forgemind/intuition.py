from __future__ import annotations

from dataclasses import dataclass

from forgemind.core import Node, canon, complexity
from forgemind.knowledge import KnowledgeBase


@dataclass(frozen=True)
class IntuitionScore:
    total: float
    novelty: float
    similarity: float
    compression: float
    falsification_value: float
    failure_penalty: float
    complexity_penalty: float

    def as_dict(self) -> dict:
        return {
            "total": self.total,
            "novelty": self.novelty,
            "similarity": self.similarity,
            "compression": self.compression,
            "falsification_value": self.falsification_value,
            "failure_penalty": self.failure_penalty,
            "complexity_penalty": self.complexity_penalty,
        }


def _novelty(
    program: list[Node],
    kb: KnowledgeBase,
) -> float:
    key = canon(program)

    if any(r.program == key for r in kb.records):
        return 0.0

    return 1.0


def _compression(
    program: list[Node],
    kb: KnowledgeBase,
) -> float:
    """
    Estimate how much known structural knowledge can compress a candidate.

    The score is based on validated rewrite patterns that occur in the
    candidate. A two-operator rule contributes one unit of compression;
    a three-operator rule contributes two, etc.
    """
    rules = kb.related_rules(program)

    if not rules:
        return 0.0

    names = tuple(n.name for n in program)
    potential = 0

    for record in rules:
        pattern = tuple(
            item[1]
            for item in record.program
            if len(item) > 1
        )

        if len(pattern) < 2:
            continue

        width = len(pattern)

        if any(
            names[i:i + width] == pattern
            for i in range(len(names) - width + 1)
        ):
            potential += width - 1

    return min(
        1.0,
        potential / max(1, len(program)),
    )


def _failure_penalty(
    program: list[Node],
    kb: KnowledgeBase,
) -> float:
    return min(
        1.0,
        0.25 * len(kb.failed_patterns(program)),
    )


def _falsification_value(
    program: list[Node],
    kb: KnowledgeBase,
) -> float:
    similarity = kb.similarity(program)
    novelty = _novelty(program, kb)

    return min(
        1.0,
        0.6 * similarity + 0.4 * novelty,
    )


def intuition_score(
    program: list[Node],
    kb: KnowledgeBase,
) -> IntuitionScore:
    novelty = _novelty(program, kb)
    similarity = kb.similarity(program)
    compression = _compression(program, kb)
    falsification = _falsification_value(program, kb)
    failure = _failure_penalty(program, kb)

    complexity_penalty = min(
        1.0,
        complexity(program) / 8.0,
    )

    total = (
        0.20 * novelty
        + 0.20 * similarity
        + 0.25 * compression
        + 0.25 * falsification
        - 0.10 * failure
        - 0.10 * complexity_penalty
    )

    return IntuitionScore(
        total=max(0.0, min(1.0, total)),
        novelty=novelty,
        similarity=similarity,
        compression=compression,
        falsification_value=falsification,
        failure_penalty=failure,
        complexity_penalty=complexity_penalty,
    )


def rank_candidates(
    programs: list[list[Node]],
    kb: KnowledgeBase,
) -> list[tuple[list[Node], IntuitionScore]]:
    ranked = [
        (program, intuition_score(program, kb))
        for program in programs
    ]

    return sorted(
        ranked,
        key=lambda item: item[1].total,
        reverse=True,
    )


def explain(
    program: list[Node],
    kb: KnowledgeBase,
) -> str:
    score = intuition_score(program, kb)
    reasons = []

    if score.similarity > 0:
        reasons.append(
            f"structural similarity={score.similarity:.2f}"
        )

    if score.compression > 0:
        reasons.append(
            f"compression potential={score.compression:.2f}"
        )

    if score.novelty > 0:
        reasons.append("novel candidate")

    if score.falsification_value > 0:
        reasons.append(
            f"falsification value={score.falsification_value:.2f}"
        )

    if score.failure_penalty > 0:
        reasons.append(
            f"failure penalty={score.failure_penalty:.2f}"
        )

    return (
        f"intuition={score.total:.3f}: "
        + ", ".join(reasons)
    )
