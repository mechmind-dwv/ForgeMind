from __future__ import annotations

from dataclasses import dataclass, field
from itertools import product
from typing import Iterable

from forgemind.core import Node, canon, complexity, run
from forgemind.equivalence import bounded_equivalence


@dataclass(frozen=True)
class Rule:
    rule_id: str
    pattern: tuple[str, ...]
    replacement: tuple[str, ...]
    family: str
    explanation: str
    evidence: str
    validation_method: str = "bounded"
    validated_cases: int = 0
    status: str = "CANDIDATE"

    @property
    def validated(self) -> bool:
        return self.status == "VALIDATED"


@dataclass
class RuleRegistry:
    rules: list[Rule] = field(default_factory=list)

    def add(self, rule: Rule) -> None:
        if any(r.rule_id == rule.rule_id for r in self.rules):
            return
        self.rules.append(rule)

    def validated_rules(self) -> list[Rule]:
        return [r for r in self.rules if r.validated]

    def __len__(self) -> int:
        return len(self.rules)


def _ops(program: Iterable[Node]) -> tuple[str, ...]:
    return tuple(n.name for n in program)


def _nodes(names: Iterable[str]) -> list[Node]:
    return [Node("U", name) for name in names]


def validate_rule(
    rule: Rule,
    domain: Iterable[Iterable[int]],
) -> Rule:
    """
    Validate a local rewrite rule by exhaustive bounded equivalence.

    The rule is interpreted as:
        pattern(x) == replacement(x)
    """
    left = _nodes(rule.pattern)
    right = _nodes(rule.replacement)

    result = bounded_equivalence(left, right, domain)

    if result.status in {"BOUNDED_EQUIVALENT", "EQUIVALENT"}:
        return Rule(
            **{
                **rule.__dict__,
                "validated_cases": result.cases_checked,
                "status": "VALIDATED",
            }
        )

    return Rule(
        **{
            **rule.__dict__,
            "validated_cases": result.cases_checked,
            "status": "REJECTED",
        }
    )


def discover_rules(
    equivalence_pairs: Iterable[tuple[list[Node], list[Node]]],
    domain: Iterable[Iterable[int]],
) -> RuleRegistry:
    """
    Convert surviving semantic equivalences into operational rules.

    Only equivalences that survive bounded validation enter the registry.
    """
    registry = RuleRegistry()

    for index, (left, right) in enumerate(equivalence_pairs):
        l = _ops(left)
        r = _ops(right)

        if l == r:
            continue

        # Prefer the shorter representation as the rewrite target.
        if len(l) >= len(r):
            pattern, replacement = l, r
        else:
            pattern, replacement = r, l

        rule = Rule(
            rule_id=f"discovered-{index}",
            pattern=pattern,
            replacement=replacement,
            family="discovered",
            explanation=f"{pattern} == {replacement}",
            evidence="semantic-equivalence-survivor",
        )

        validated = validate_rule(rule, domain)

        if validated.validated:
            registry.add(validated)

    return registry


def _replace_once(
    program: list[Node],
    rule: Rule,
) -> tuple[list[Node], bool]:
    pattern = rule.pattern
    replacement = rule.replacement

    if not pattern:
        return program, False

    names = _ops(program)
    width = len(pattern)

    for i in range(len(names) - width + 1):
        if names[i:i + width] == pattern:
            new_names = (
                names[:i]
                + replacement
                + names[i + width:]
            )
            return _nodes(new_names), True

    return program, False


def rewrite(
    program: list[Node],
    registry: RuleRegistry,
    max_steps: int = 32,
) -> tuple[list[Node], list[str]]:
    """
    Repeatedly apply validated rewrite rules.

    Returns:
        normalized_program, applied_rule_ids
    """
    current = list(program)
    applied: list[str] = []

    for _ in range(max_steps):
        changed = False

        # Shorter rules first: compression takes priority.
        rules = sorted(
            registry.validated_rules(),
            key=lambda r: (
                -(len(r.pattern) - len(r.replacement)),
                r.rule_id,
            ),
        )

        for rule in rules:
            candidate, did_change = _replace_once(current, rule)

            if did_change and complexity(candidate) <= complexity(current):
                current = candidate
                applied.append(rule.rule_id)
                changed = True
                break

        if not changed:
            break

    return current, applied


def compose(
    left: list[Node],
    right: list[Node],
) -> list[Node]:
    """Compose programs sequentially."""
    return list(left) + list(right)


def compress(
    program: list[Node],
    registry: RuleRegistry,
) -> tuple[list[Node], list[str]]:
    return rewrite(program, registry)


def compositional_candidates(
    programs: list[list[Node]],
    registry: RuleRegistry,
    max_length: int = 6,
) -> list[list[Node]]:
    """
    Compose existing programs and immediately normalize them.
    """
    candidates: dict[tuple, list[Node]] = {}

    for program in programs:
        normalized, _ = compress(program, registry)
        if len(normalized) <= max_length:
            candidates[canon(normalized)] = normalized

    base = list(candidates.values())

    for left in base:
        for right in base:
            composed = compose(left, right)

            if len(composed) > max_length:
                continue

            normalized, _ = compress(composed, registry)

            if len(normalized) <= max_length:
                candidates[canon(normalized)] = normalized

    return list(candidates.values())


def generate_basic_rules(
    domain: Iterable[Iterable[int]],
) -> RuleRegistry:
    """
    Bootstrap registry from semantic identities already discoverable
    by ForgeMind's equivalence machinery.

    These are not trusted blindly: every rule is validated first.
    """
    candidates = [
        Rule(
            "sort-idempotence",
            ("sort", "sort"),
            ("sort",),
            "idempotence",
            "Applying sort twice has the same effect as applying it once.",
            "0.12-semantic-equivalence",
        ),
        Rule(
            "rev-involution",
            ("rev", "rev"),
            (),
            "involution",
            "Reversal is its own inverse.",
            "0.12-semantic-equivalence",
        ),
        Rule(
            "neg-involution",
            ("neg", "neg"),
            (),
            "involution",
            "Negation is its own inverse.",
            "0.12-semantic-equivalence",
        ),
        Rule(
            "rev-neg-commutation",
            ("rev", "neg"),
            ("neg", "rev"),
            "commutation",
            "Reversal acts on positions while negation acts on values.",
            "0.12-semantic-equivalence",
        ),
        Rule(
            "sort-after-reversal",
            ("rev", "sort"),
            ("sort",),
            "permutation-invariance",
            "Sorting removes the ordering information introduced by reversal.",
            "0.12-semantic-equivalence",
        ),
    ]

    registry = RuleRegistry()

    for candidate in candidates:
        validated = validate_rule(candidate, domain)
        if validated.validated:
            registry.add(validated)

    return registry
