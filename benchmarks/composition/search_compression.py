"""
ForgeMind 0.13.1
Search-space compression through validated compositional rules.

Pipeline:

    semantic equivalences
            ↓
      RuleRegistry
            ↓
       normalization
            ↓
     search compression
            ↓
   candidate-space reduction

The benchmark deliberately uses the public composition API.
"""

from __future__ import annotations

import itertools
import json
from pathlib import Path

from forgemind.core import Node, canon, complexity, run
from forgemind.composition import (
    RuleRegistry,
    compress,
    generate_basic_rules,
)


OPS = ("rev", "sort", "neg")
PROGRAM_LENGTHS = (1, 2, 3)
VALUES = (-1, 0, 1)


def build_domain() -> list[list[int]]:
    return [
        list(values)
        for length in (2, 3)
        for values in itertools.product(VALUES, repeat=length)
    ]


def generate_programs() -> list[list[Node]]:
    programs: list[list[Node]] = []

    for length in PROGRAM_LENGTHS:
        for ops in itertools.product(OPS, repeat=length):
            programs.append(
                [Node("U", op) for op in ops]
            )

    return programs


def program_key(program: list[Node]) -> tuple:
    return canon(program)


def semantic_key(
    program: list[Node],
    domain: list[list[int]],
) -> tuple:
    return tuple(
        tuple(run(program, x))
        for x in domain
    )


def main() -> None:
    domain = build_domain()
    programs = generate_programs()

    print("===== FORGEMIND 0.13.1 — SEARCH COMPRESSION =====")
    print(f"programs generated = {len(programs)}")
    print(f"domain size        = {len(domain)}")
    print()

    # ------------------------------------------------------------
    # 1. Build validated rule registry
    # ------------------------------------------------------------

    registry = generate_basic_rules(domain)

    print("validated rules    =", len(registry.rules))

    for rule in registry.rules:
        print(
            f"  {rule.rule_id}: "
            f"{rule.pattern} -> {rule.replacement}"
        )

    print()

    # ------------------------------------------------------------
    # 2. Normalize every candidate
    # ------------------------------------------------------------

    normalized: list[list[Node]] = []
    rewrite_counts: list[int] = []
    applied_rules: dict[str, int] = {}

    for program in programs:
        compressed, rules = compress(program, registry)

        normalized.append(compressed)
        rewrite_counts.append(len(rules))

        for rule_id in rules:
            applied_rules[rule_id] = applied_rules.get(rule_id, 0) + 1

    # ------------------------------------------------------------
    # 3. Syntactic search-space compression
    # ------------------------------------------------------------

    raw_keys = {
        program_key(program)
        for program in programs
    }

    normalized_keys = {
        program_key(program)
        for program in normalized
    }

    raw_count = len(raw_keys)
    normalized_count = len(normalized_keys)

    reduction = (
        1.0 - normalized_count / raw_count
        if raw_count
        else 0.0
    )

    # ------------------------------------------------------------
    # 4. Semantic classes
    #
    # This is deliberately measured independently from the
    # rewrite engine. It prevents the benchmark from assuming
    # that normalization itself proves semantic equivalence.
    # ------------------------------------------------------------

    semantic_classes_before = {
        semantic_key(program, domain)
        for program in programs
    }

    semantic_classes_after = {
        semantic_key(program, domain)
        for program in normalized
    }

    # ------------------------------------------------------------
    # 5. Check that normalization preserves behaviour
    # ------------------------------------------------------------

    behavior_preserved = True

    for original, compressed_program in zip(programs, normalized):
        for x in domain:
            if run(original, x) != run(compressed_program, x):
                behavior_preserved = False
                print()
                print("ERROR: normalization changed behavior")
                print("original :", canon(original))
                print("compressed:", canon(compressed_program))
                print("input    :", tuple(x))
                print("before   :", run(original, x))
                print("after    :", run(compressed_program, x))
                raise SystemExit(1)

    # ------------------------------------------------------------
    # 6. Complexity statistics
    # ------------------------------------------------------------

    raw_complexity = sum(
        complexity(program)
        for program in programs
    )

    normalized_complexity = sum(
        complexity(program)
        for program in normalized
    )

    complexity_reduction = (
        1.0 - normalized_complexity / raw_complexity
        if raw_complexity
        else 0.0
    )

    total_rewrites = sum(rewrite_counts)

    print("===== RESULTS =====")
    print(f"raw candidates             = {raw_count}")
    print(f"normalized candidates      = {normalized_count}")
    print(f"syntactic reduction        = {reduction:.4f}")
    print(f"semantic classes before    = {len(semantic_classes_before)}")
    print(f"semantic classes after     = {len(semantic_classes_after)}")
    print(f"total rewrites             = {total_rewrites}")
    print(f"mean rewrites/candidate    = {total_rewrites / raw_count:.4f}")
    print(f"complexity reduction       = {complexity_reduction:.4f}")
    print(f"behavior preserved         = {behavior_preserved}")
    print()

    print("===== RULE USAGE =====")

    for rule_id, count in sorted(applied_rules.items()):
        print(f"{rule_id:30s} {count}")

    print()

    results = {
        "version": "0.13.1",
        "program_lengths": list(PROGRAM_LENGTHS),
        "operators": list(OPS),
        "domain_size": len(domain),
        "raw_candidates": raw_count,
        "normalized_candidates": normalized_count,
        "syntactic_reduction": reduction,
        "semantic_classes_before": len(semantic_classes_before),
        "semantic_classes_after": len(semantic_classes_after),
        "total_rewrites": total_rewrites,
        "mean_rewrites_per_candidate": (
            total_rewrites / raw_count if raw_count else 0.0
        ),
        "raw_complexity": raw_complexity,
        "normalized_complexity": normalized_complexity,
        "complexity_reduction": complexity_reduction,
        "behavior_preserved": behavior_preserved,
        "validated_rules": [
            {
                "rule_id": rule.rule_id,
                "pattern": list(rule.pattern),
                "replacement": list(rule.replacement),
                "family": rule.family,
                "validation_method": rule.validation_method,
                "validated_cases": rule.validated_cases,
                "status": rule.status,
            }
            for rule in registry.rules
        ],
        "rule_usage": applied_rules,
    }

    output = Path("benchmarks/composition/search_compression_results.json")
    output.write_text(
        json.dumps(results, indent=2),
        encoding="utf-8",
    )

    print(f"results: {output}")
    print()
    print("OK: compositional compression benchmark passed")


if __name__ == "__main__":
    main()
