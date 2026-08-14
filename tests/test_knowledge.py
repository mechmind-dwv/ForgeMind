from forgemind.core import Node
from forgemind.knowledge import KnowledgeBase, KnowledgeRecord


def test_knowledge_base_deduplicates_records():
    kb = KnowledgeBase()

    program = [Node("U", "rev")]

    kb.remember_equivalence(
        program,
        evidence="bounded",
        validated_cases=36,
    )

    kb.remember_equivalence(
        program,
        evidence="bounded",
        validated_cases=36,
    )

    assert len(kb.records) == 1
    assert len(kb.survivors()) == 1


def test_knowledge_base_tracks_refutations():
    kb = KnowledgeBase()

    kb.remember_falsification(
        [Node("U", "rev")],
        (-1, -1),
    )

    assert len(kb.refuted()) == 1
    assert kb.refuted()[0].counterexamples == ((-1, -1),)


def test_rule_memory_is_operational():
    kb = KnowledgeBase()

    kb.remember_rule(
        [
            Node("U", "rev"),
            Node("U", "sort"),
        ],
        rule_id="sort-after-reversal",
        family="permutation-invariance",
        validated_cases=36,
    )

    related = kb.related_rules(
        [Node("U", "sort")]
    )

    assert len(related) == 1
    assert related[0].rule_id == "sort-after-reversal"


def test_summary():
    kb = KnowledgeBase()

    kb.remember_equivalence([Node("U", "sort")])
    kb.remember_falsification(
        [Node("U", "rev")],
        (-1, -1),
    )

    assert kb.summary() == {
        "records": 2,
        "survivors": 1,
        "refuted": 1,
        "rules": 0,
        "equivalences": 1,
    }


def test_rule_memory_detects_structural_overlap():
    kb = KnowledgeBase()

    kb.remember_rule(
        [
            Node("U", "rev"),
            Node("U", "sort"),
        ],
        rule_id="sort-after-reversal",
        family="permutation-invariance",
        validated_cases=36,
    )

    related = kb.related_rules(
        [
            Node("U", "sort"),
        ]
    )

    assert len(related) == 1
    assert related[0].rule_id == "sort-after-reversal"
