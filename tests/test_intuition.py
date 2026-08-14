from forgemind.core import Node
from forgemind.knowledge import KnowledgeBase
from forgemind.intuition import intuition_score, rank_candidates


def test_structural_knowledge_changes_score():
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

    score = intuition_score(
        [
            Node("U", "rev"),
            Node("U", "sort"),
        ],
        kb,
    )

    assert score.similarity > 0
    assert score.compression > 0
    assert score.total > 0


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


def test_rank_candidates_prefers_known_structure():
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

    candidates = [
        [
            Node("U", "neg"),
        ],
        [
            Node("U", "rev"),
            Node("U", "sort"),
        ],
    ]

    ranked = rank_candidates(candidates, kb)

    assert ranked[0][1].total >= ranked[1][1].total
