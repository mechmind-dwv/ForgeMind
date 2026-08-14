from __future__ import annotations

import json
from itertools import product
from pathlib import Path

from forgemind.core import Node, canon
from forgemind.composition import generate_basic_rules
from forgemind.intuition import explain, intuition_score, rank_candidates
from forgemind.knowledge import KnowledgeBase


def domain():
    return [
        list(x)
        for n in (2, 3)
        for x in product((-1, 0, 1), repeat=n)
    ]


def bootstrap_knowledge():
    d = domain()
    registry = generate_basic_rules(d)

    kb = KnowledgeBase()

    for rule in registry.validated_rules():
        kb.remember_rule(
            [
                Node("U", name)
                for name in rule.pattern
            ],
            rule_id=rule.rule_id,
            family=rule.family,
            evidence=rule.evidence,
            validated_cases=rule.validated_cases,
        )

    return kb


def candidates():
    ops = ("rev", "sort", "neg", "abs")

    programs = []

    for length in (1, 2, 3):
        for names in product(ops, repeat=length):
            programs.append(
                [Node("U", name) for name in names]
            )

    return programs


def main():
    kb = bootstrap_knowledge()
    programs = candidates()

    ranked = rank_candidates(programs, kb)

    payload = {
        "version": "0.14",
        "knowledge": kb.summary(),
        "candidate_count": len(programs),
        "top_candidates": [
            {
                "program": canon(program),
                "score": score.as_dict(),
                "explanation": explain(program, kb),
            }
            for program, score in ranked[:10]
        ],
    }

    output = Path(
        "benchmarks/intuition/intuition_results.json"
    )

    output.write_text(
        json.dumps(
            payload,
            indent=2,
        ),
        encoding="utf-8",
    )

    print("===== FORGEMIND 0.14 INTUITION ENGINE =====")
    print(f"knowledge records = {payload['knowledge']['records']}")
    print(f"validated rules  = {payload['knowledge']['rules']}")
    print(f"candidates       = {len(programs)}")
    print()
    print("===== TOP INTUITIVE CANDIDATES =====")

    for item in payload["top_candidates"]:
        print(
            f"{item['score']['total']:.3f} "
            f"{item['program']}"
        )
        print(
            f"  {item['explanation']}"
        )

    print()
    print(f"results: {output}")


if __name__ == "__main__":
    main()
