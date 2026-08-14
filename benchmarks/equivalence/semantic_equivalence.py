from __future__ import annotations

import json
from itertools import product
from pathlib import Path

from forgemind.core import Node, canon, run
from forgemind.equivalence import bounded_equivalence, integer_domain


OPS = ("rev", "neg", "sort")


def make_programs():
    programs = []

    for length in (1, 2):
        for ops in product(OPS, repeat=length):
            programs.append([Node("U", op) for op in ops])

    return programs


def main():
    programs = make_programs()

    domain = integer_domain(
        values=(-1, 0, 1),
        lengths=(2, 3),
    )

    canonical_pairs = 0
    semantic_pairs = 0
    non_equivalent_pairs = 0
    bounded_cases = 0
    discovered_pairs = []

    for i, left in enumerate(programs):
        for right in programs[i + 1:]:

            if canon(left) == canon(right):
                canonical_pairs += 1
                continue

            result = bounded_equivalence(
                left,
                right,
                domain,
            )

            bounded_cases += result.cases_checked

            if result.status == "BOUNDED_EQUIVALENT":
                semantic_pairs += 1

                discovered_pairs.append({
                    "left": canon(left),
                    "right": canon(right),
                    "cases_checked": result.cases_checked,
                })

            elif result.status == "NOT_EQUIVALENT":
                non_equivalent_pairs += 1

    total_pairs = len(programs) * (len(programs) - 1) // 2

    output = {
        "version": "0.11",
        "programs": len(programs),
        "domain_size": len(domain),
        "total_pairs": total_pairs,
        "canonical_pairs": canonical_pairs,
        "semantic_pairs": semantic_pairs,
        "non_equivalent_pairs": non_equivalent_pairs,
        "bounded_cases_checked": bounded_cases,
        "semantic_discovery_rate": (
            semantic_pairs / total_pairs
            if total_pairs
            else 0.0
        ),
        "examples": discovered_pairs[:25],
    }

    path = Path("benchmarks/equivalence/results.json")
    path.write_text(
        json.dumps(output, indent=2),
        encoding="utf-8",
    )

    print("===== FORGEMIND 0.11 FORMAL EQUIVALENCE =====")
    print(f"programs = {len(programs)}")
    print(f"domain   = {len(domain)}")
    print(f"pairs    = {total_pairs}")
    print(f"canonical equivalent = {canonical_pairs}")
    print(f"semantic equivalent  = {semantic_pairs}")
    print(f"not equivalent       = {non_equivalent_pairs}")
    print(f"cases checked        = {bounded_cases}")
    print(
        "semantic discovery rate = "
        f"{output['semantic_discovery_rate']:.4f}"
    )
    print()
    print(f"results: {path}")


if __name__ == "__main__":
    main()
