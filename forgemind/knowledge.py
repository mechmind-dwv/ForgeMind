from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable

from forgemind.core import Node, canon


@dataclass(frozen=True)
class KnowledgeRecord:
    kind: str
    program: tuple
    status: str = "OBSERVED"
    evidence: str = ""
    validated_cases: int = 0
    counterexamples: tuple = ()
    rule_id: str | None = None
    family: str | None = None
    score: float = 0.0


@dataclass
class KnowledgeBase:
    records: list[KnowledgeRecord] = field(default_factory=list)

    def remember(self, record: KnowledgeRecord) -> None:
        key = (
            record.kind,
            record.program,
            record.rule_id,
        )

        if any(
            (
                r.kind,
                r.program,
                r.rule_id,
            ) == key
            for r in self.records
        ):
            return

        self.records.append(record)

    def remember_equivalence(
        self,
        program: list[Node],
        *,
        evidence: str = "",
        validated_cases: int = 0,
        score: float = 0.0,
    ) -> None:
        self.remember(
            KnowledgeRecord(
                kind="EQUIVALENCE",
                program=canon(program),
                status="VALIDATED",
                evidence=evidence,
                validated_cases=validated_cases,
                score=score,
            )
        )

    def remember_falsification(
        self,
        program: list[Node],
        counterexample: Iterable[int],
        *,
        evidence: str = "",
    ) -> None:
        self.remember(
            KnowledgeRecord(
                kind="FALSIFICATION",
                program=canon(program),
                status="REFUTED",
                evidence=evidence,
                counterexamples=(tuple(counterexample),),
            )
        )

    def remember_rule(
        self,
        program: list[Node],
        *,
        rule_id: str,
        family: str,
        evidence: str = "",
        validated_cases: int = 0,
    ) -> None:
        self.remember(
            KnowledgeRecord(
                kind="REWRITE_RULE",
                program=canon(program),
                status="VALIDATED",
                evidence=evidence,
                validated_cases=validated_cases,
                rule_id=rule_id,
                family=family,
            )
        )

    def survivors(self) -> list[KnowledgeRecord]:
        return [
            r for r in self.records
            if r.status == "VALIDATED"
        ]

    def refuted(self) -> list[KnowledgeRecord]:
        return [
            r for r in self.records
            if r.status == "REFUTED"
        ]

    @staticmethod
    def _names(program) -> tuple[str, ...]:
        if isinstance(program, KnowledgeRecord):
            program = program.program

        if program and isinstance(program[0], Node):
            return tuple(node.name for node in program)

        return tuple(
            item[1]
            for item in program
            if len(item) > 1
        )

    def related_rules(
        self,
        program: list[Node],
    ) -> list[KnowledgeRecord]:
        """
        Return validated rewrite rules structurally related to a program.

        A rule is related when its pattern:
        - exactly matches the candidate,
        - occurs contiguously inside the candidate, or
        - contains the candidate as a structural sub-pattern.

        This deliberately works on KnowledgeRecord rather than the
        composition.RuleRegistry: the KnowledgeBase is the memory layer.
        """
        names = self._names(program)
        related: list[KnowledgeRecord] = []

        for record in self.records:
            if (
                record.kind != "REWRITE_RULE"
                or record.status != "VALIDATED"
            ):
                continue

            pattern = self._names(record.program)

            if not pattern:
                continue

            if pattern == names:
                related.append(record)
                continue

            if len(pattern) <= len(names):
                width = len(pattern)

                if any(
                    names[i:i + width] == pattern
                    for i in range(len(names) - width + 1)
                ):
                    related.append(record)
                    continue

            if len(names) <= len(pattern):
                width = len(names)

                if any(
                    pattern[i:i + width] == names
                    for i in range(len(pattern) - width + 1)
                ):
                    related.append(record)

        return related

    def failed_patterns(
        self,
        program: list[Node],
    ) -> list[KnowledgeRecord]:
        names = set(self._names(program))

        return [
            r
            for r in self.refuted()
            if names.intersection(self._names(r.program))
        ]

    def similarity(
        self,
        program: list[Node],
    ) -> float:
        if not self.records:
            return 0.0

        target = set(self._names(program))
        best = 0.0

        for record in self.records:
            source = set(self._names(record.program))

            if not source:
                continue

            intersection = len(target & source)
            union = len(target | source)

            if union:
                best = max(best, intersection / union)

        return best

    def summary(self) -> dict:
        return {
            "records": len(self.records),
            "survivors": len(self.survivors()),
            "refuted": len(self.refuted()),
            "rules": sum(
                r.kind == "REWRITE_RULE"
                for r in self.records
            ),
            "equivalences": sum(
                r.kind == "EQUIVALENCE"
                for r in self.records
            ),
        }
