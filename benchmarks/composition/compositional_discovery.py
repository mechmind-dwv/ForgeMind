from __future__ import annotations

import json
from itertools import product
from pathlib import Path

from forgemind.composition import (
    compose,
    compress,
    generate_basic_rules,
)
from forgemind.core import Node, canon, complexity, run


def domain():
    return [
        list(x)
        for n in (2, 3)
        for x in product((-1, 0, 1), repeat=n)
    ]


def candidate_programs():
    ops = ("rev", "neg", "sort")

    programs = []

    for length in range(1, 5):
        for names in product(ops, repeat=length):
            programs.append([Node("U", name) for name in names])

    return programs


def find_target(programs):
    """
    Target behavior chosen from a non-minimal composition.

    target = sort(x)

    Several syntactically different programs implement it.
    """
    target = [Node("U", "sort")]
    target_outputs = [run(target, x) for x in domain()]

    for program in programs:
        outputs = [run(program, x) for x in domain()]

        if outputs == target_outputs:
            return target, program

    raise RuntimeError("target not found")


def baseline(programs, target):
    target_outputs = [run(target, x) for x in domain()]

    evaluations = 0

    for program in programs:
        evaluations += 1

        if [run(program, x) for x in domain()] == target_outputs:
            return {
                "found": True,
                "evaluations": evaluations,
                "complexity": complexity(program),
                "program": canon(program),
            }

    return {
        "found": False,
        "evaluations": evaluations,
    }


def compositional(programs, target, registry):
    target_outputs = [run(target, x) for x in domain()]

    evaluations = 0
    compressed = 0
    normalized_candidates = {}

    for program in programs:
        normalized, applied = compress(program, registry)
        normalized_candidates[canon(normalized)] = normalized

        if applied:
            compressed += 1

    for program in normalized_candidates.values():
        evaluations += 1

        if [run(program, x) for x in domain()] == target_outputs:
            return {
                "found": True,
                "evaluations": evaluations,
                "compressed_programs": compressed,
                "candidate_count": len(normalized_candidates),
                "complexity": complexity(program),
                "program": canon(program),
            }

    return {
        "found": False,
        "evaluations": evaluations,
        "compressed_programs": compressed,
        "candidate_count": len(normalized_candidates),
    }


def main():
    programs = candidate_programs()
    target, witness = find_target(programs)

    registry = generate_basic_rules(domain())

    base = baseline(programs, target)
    comp = compositional(programs, target, registry)

    composed = [
        compose(
            [Node("U", "rev")],
            [Node("U", "sort")],
        ),
        compose(
            [Node("U", "sort")],
            [Node("U", "sort")],
        ),
        compose(
            [Node("U", "rev")],
            [Node("U", "rev")],
        ),
    ]

    composition_results = []

    for program in composed:
        normalized, applied = compress(program, registry)

        composition_results.append(
            {
                "input": canon(program),
                "output": canon(normalized),
                "rules": applied,
                "complexity_before": complexity(program),
                "complexity_after": complexity(normalized),
            }
        )

    result = {
        "version": "0.13",
        "program_space": len(programs),
        "domain_size": len(domain()),
        "rules": len(registry),
        "validated_rules": len(registry.validated_rules()),
        "target": canon(target),
        "witness": canon(witness),
        "baseline": base,
        "compositional": comp,
        "search_reduction": (
            1.0
            - comp["evaluations"] / base["evaluations"]
        ),
        "composition_examples": composition_results,
    }

    path = Path("benchmarks/composition/results.json")
    path.write_text(
        json.dumps(result, indent=2),
        encoding="utf-8",
    )

    print("===== FORGEMIND 0.13 COMPOSITIONAL DISCOVERY =====")
    print(f"program space       = {len(programs)}")
    print(f"domain              = {len(domain())}")
    print(f"validated rules     = {len(registry.validated_rules())}")
    print()
    print(f"baseline found      = {base['found']}")
    print(f"baseline evaluations = {base['evaluations']}")
    print()
    print(f"compositional found = {comp['found']}")
    print(f"compositional evals = {comp['evaluations']}")
    print(f"candidate reduction  = {result['search_reduction']:.4f}")
    print(f"compressed programs  = {comp['compressed_programs']}")
    print()
    print(f"results: {path}")


if __name__ == "__main__":
    main()
