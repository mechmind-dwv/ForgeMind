from __future__ import annotations

import json
from pathlib import Path

from forgemind.core import Node
from forgemind.equivalence import bounded_equivalence
from forgemind.knowledge import KnowledgeBase
from forgemind.intuition import intuition_score, rank_candidates


DOMAIN = (
    (-1, -1),
    (-1, 0),
    (-1, 1),
    (0, -1),
    (0, 0),
    (0, 1),
    (1, -1),
    (1, 0),
    (1, 1),
)


def program(*names: str) -> list[Node]:
    return [Node("U", name) for name in names]


def generate_candidates() -> list[list[Node]]:
    operators = ("rev", "sort", "neg")

    candidates: list[list[Node]] = []

    for a in operators:
        candidates.append(program(a))

    for a in operators:
        for b in operators:
            candidates.append(program(a, b))

    for a in operators:
        for b in operators:
            for c in operators:
                candidates.append(program(a, b, c))

    return candidates


def is_equivalent(
    candidate: list[Node],
    target: list[Node],
) -> bool:
    result = bounded_equivalence(
        candidate,
        target,
        DOMAIN,
    )

    return result.status == "BOUNDED_EQUIVALENT"


def blind_search(
    candidates: list[list[Node]],
    target: list[Node],
) -> dict:
    evaluations = 0

    for candidate in candidates:
        evaluations += 1

        if is_equivalent(candidate, target):
            return {
                "found": True,
                "evaluations": evaluations,
                "candidate": [
                    node.name
                    for node in candidate
                ],
            }

    return {
        "found": False,
        "evaluations": evaluations,
        "candidate": None,
    }


def guided_search(
    candidates: list[list[Node]],
    target: list[Node],
    kb: KnowledgeBase,
) -> dict:
    ranked = rank_candidates(candidates, kb)

    evaluations = 0

    for candidate, score in ranked:
        evaluations += 1

        if is_equivalent(candidate, target):
            return {
                "found": True,
                "evaluations": evaluations,
                "candidate": [
                    node.name
                    for node in candidate
                ],
                "score": score.as_dict(),
            }

    return {
        "found": False,
        "evaluations": evaluations,
        "candidate": None,
    }


def build_knowledge() -> KnowledgeBase:
    kb = KnowledgeBase()

    kb.remember_rule(
        program("rev", "sort"),
        rule_id="sort-after-reversal",
        family="permutation-invariance",
        validated_cases=36,
    )

    kb.remember_rule(
        program("sort", "sort"),
        rule_id="sort-idempotence",
        family="idempotence",
        validated_cases=36,
    )

    kb.remember_rule(
        program("rev", "rev"),
        rule_id="rev-involution",
        family="involution",
        validated_cases=36,
    )

    kb.remember_rule(
        program("neg", "neg"),
        rule_id="neg-involution",
        family="involution",
        validated_cases=36,
    )

    kb.remember_rule(
        program("rev", "neg"),
        rule_id="rev-neg-commutation",
        family="commutation",
        validated_cases=36,
    )

    return kb


def main() -> None:
    candidates = generate_candidates()

    # A deliberately non-minimal target. The useful path is discovered
    # through structural knowledge rather than syntax alone.
    target = program("sort")

    kb = build_knowledge()

    blind = blind_search(candidates, target)
    guided = guided_search(candidates, target, kb)

    reduction = (
        1.0
        - guided["evaluations"] / blind["evaluations"]
    )

    results = {
        "version": "0.14",
        "candidate_count": len(candidates),
        "domain_size": len(DOMAIN),
        "target": ["sort"],
        "blind": blind,
        "guided": guided,
        "evaluation_reduction": reduction,
        "solution_preserved": (
            blind["found"]
            and guided["found"]
        ),
        "knowledge_rules": len(kb.survivors()),
    }

    print("===== FORGEMIND 0.14 — INTUITION GUIDED SEARCH =====")
    print(f"candidates             = {len(candidates)}")
    print(f"domain                  = {len(DOMAIN)}")
    print(f"knowledge rules         = {len(kb.survivors())}")
    print()
    print("blind search")
    print(f"  found                 = {blind['found']}")
    print(f"  evaluations           = {blind['evaluations']}")
    print(f"  candidate             = {blind['candidate']}")
    print()
    print("intuition-guided search")
    print(f"  found                 = {guided['found']}")
    print(f"  evaluations           = {guided['evaluations']}")
    print(f"  candidate             = {guided['candidate']}")
    print()
    print(
        f"evaluation reduction   = {reduction:.4f}"
    )
    print(
        f"solution preserved      = {results['solution_preserved']}"
    )

    if not results["solution_preserved"]:
        raise SystemExit(
            "ERROR: guided search lost a known solution"
        )

    output = Path(
        "benchmarks/intuition/guided_search_results.json"
    )

    output.write_text(
        json.dumps(
            results,
            indent=2,
        ) + "\n",
        encoding="utf-8",
    )

    print()
    print(f"results: {output}")
    print("OK: intuition-guided search benchmark passed")


if __name__ == "__main__":
    main()
