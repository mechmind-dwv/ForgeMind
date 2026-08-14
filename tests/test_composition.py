from forgemind.composition import (
    Rule,
    RuleRegistry,
    compress,
    compose,
    generate_basic_rules,
    rewrite,
)
from forgemind.core import Node


def domain():
    return [
        list(x)
        for n in (2, 3)
        for x in __import__("itertools").product(
            (-1, 0, 1),
            repeat=n,
        )
    ]


def test_registry_contains_validated_rules():
    registry = generate_basic_rules(domain())

    assert len(registry) == 5
    assert all(rule.validated for rule in registry.rules)


def test_sort_idempotence_rewrites():
    registry = generate_basic_rules(domain())

    program = [
        Node("U", "sort"),
        Node("U", "sort"),
    ]

    normalized, applied = rewrite(program, registry)

    assert [n.name for n in normalized] == ["sort"]
    assert "sort-idempotence" in applied


def test_involution_rewrites_to_empty_program():
    registry = generate_basic_rules(domain())

    program = [
        Node("U", "rev"),
        Node("U", "rev"),
    ]

    normalized, applied = compress(program, registry)

    assert normalized == []
    assert "rev-involution" in applied


def test_sort_after_reverse_rewrites():
    registry = generate_basic_rules(domain())

    program = [
        Node("U", "rev"),
        Node("U", "sort"),
    ]

    normalized, applied = compress(program, registry)

    assert [n.name for n in normalized] == ["sort"]
    assert "sort-after-reversal" in applied


def test_commutation_rewrites():
    registry = generate_basic_rules(domain())

    program = [
        Node("U", "rev"),
        Node("U", "neg"),
    ]

    normalized, applied = compress(program, registry)

    assert [n.name for n in normalized] == ["neg", "rev"]
    assert "rev-neg-commutation" in applied


def test_composition_is_sequential():
    left = [Node("U", "rev")]
    right = [Node("U", "neg")]

    result = compose(left, right)

    assert [n.name for n in result] == ["rev", "neg"]
