"""
ForgeMind 0.12 — Structural Explanation Benchmark.
"""

import json

from forgemind.core import Node
from forgemind.rules import explain_pair


PAIRS = [
    (
        [Node("U", "rev"), Node("U", "sort")],
        [Node("U", "sort")],
    ),
    (
        [Node("U", "sort"), Node("U", "sort")],
        [Node("U", "sort")],
    ),
    (
        [Node("U", "rev"), Node("U", "neg")],
        [Node("U", "neg"), Node("U", "rev")],
    ),
    (
        [Node("U", "rev"), Node("U", "rev")],
        [],
    ),
    (
        [Node("U", "neg"), Node("U", "neg")],
        [],
    ),
    (
        [Node("U", "rev")],
        [Node("U", "neg")],
    ),
]


def serialize(program):
    return [
        [n.kind, n.name, n.arg]
        for n in program
    ]


def main():
    explained = 0
    unexplained = 0
    rows = []

    for left, right in PAIRS:
        rule = explain_pair(left, right)

        row = {
            "left": serialize(left),
            "right": serialize(right),
            "rule": rule.name if rule else None,
            "family": rule.family if rule else None,
            "explanation": rule.explanation if rule else None,
        }

        rows.append(row)

        if rule:
            explained += 1
        else:
            unexplained += 1

    result = {
        "version": "0.12",
        "pairs": len(PAIRS),
        "explained": explained,
        "unexplained": unexplained,
        "explanation_rate": explained / len(PAIRS),
        "rules": rows,
    }

    print("===== FORGEMIND 0.12 STRUCTURAL EXPLANATION =====")
    print(f"pairs       = {len(PAIRS)}")
    print(f"explained   = {explained}")
    print(f"unexplained = {unexplained}")
    print(f"rate        = {result['explanation_rate']:.4f}")

    path = "benchmarks/rules/results.json"

    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print()
    print(f"results: {path}")


if __name__ == "__main__":
    main()
