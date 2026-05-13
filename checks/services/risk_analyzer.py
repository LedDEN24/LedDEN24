from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

from checks.models import ParserSource, RiskLevel


@dataclass(slots=True)
class RiskFinding:
    code: str
    title: str
    description: str
    level: str
    score: int
    source: str = ""
    evidence: dict[str, Any] = field(default_factory=dict)


@dataclass(slots=True)
class RiskSummary:
    score: int
    level: str
    text: str
    findings: list[RiskFinding]


class RiskAnalyzer:
    KEYWORD_RULES = {
        "банкрот": ("bankruptcy", "Признаки банкротства", RiskLevel.HIGH, 25),
        "исполнитель": ("debt", "Исполнительные производства", RiskLevel.HIGH, 20),
        "арбитраж": ("court_case", "Арбитражные споры", RiskLevel.MEDIUM, 15),
        "обремен": ("encumbrance", "Возможное обременение", RiskLevel.HIGH, 25),
        "дубликат": ("duplicate_listing", "Дублирующиеся объявления", RiskLevel.MEDIUM, 10),
        "жалоб": ("complaint", "Жалобы в открытых источниках", RiskLevel.MEDIUM, 10),
        "проблем": ("problem_developer", "Проблемный застройщик", RiskLevel.CRITICAL, 35),
    }

    SOURCE_WEIGHTS = {
        ParserSource.FSSP: 20,
        ParserSource.EFRSB: 25,
        ParserSource.KAD_ARBITR: 15,
        ParserSource.RF_COURTS: 15,
        ParserSource.ROSREESTR: 25,
        ParserSource.CADASTRAL_MAP: 10,
        ParserSource.AVITO: 8,
        ParserSource.CIAN: 8,
        ParserSource.DOMCLICK: 8,
        ParserSource.NEWS: 10,
        ParserSource.TELEGRAM: 10,
        ParserSource.DEVELOPERS: 35,
    }

    def analyze(self, results: list[dict]) -> RiskSummary:
        findings: list[RiskFinding] = []
        for result in results:
            findings.extend(self._find_source_risks(result))
            findings.extend(self._find_keyword_risks(result))
            findings.extend(self._find_structured_risks(result))

        deduplicated = self._deduplicate(findings)
        score = min(sum(finding.score for finding in deduplicated), 100)
        level = self._level_for_score(score)
        text = self._summary_text(score, level, deduplicated)
        return RiskSummary(score=score, level=level, text=text, findings=deduplicated)

    def _find_source_risks(self, result: dict) -> list[RiskFinding]:
        if not result.get("matched"):
            return []
        source = result.get("source", "")
        score = self.SOURCE_WEIGHTS.get(source, 5)
        return [
            RiskFinding(
                code=f"{source}_match",
                title=f"Совпадение в источнике {source}",
                description="Найдено совпадение по входным данным проверки.",
                level=self._level_for_score(score),
                score=score,
                source=source,
                evidence={"confidence": result.get("confidence", 0)},
            )
        ]

    def _find_keyword_risks(self, result: dict) -> list[RiskFinding]:
        payload_text = str(result.get("payload", {})).lower()
        source = result.get("source", "")
        findings = []
        for keyword, (code, title, level, score) in self.KEYWORD_RULES.items():
            if keyword in payload_text:
                findings.append(
                    RiskFinding(
                        code=code,
                        title=title,
                        description=f"В данных источника обнаружен маркер: {keyword}.",
                        level=level,
                        score=score,
                        source=source,
                        evidence={"source": source},
                    )
                )
        return findings

    def _find_structured_risks(self, result: dict) -> list[RiskFinding]:
        payload = result.get("payload") or {}
        source = result.get("source", "")
        findings = []
        if payload.get("debts"):
            active_debts = [
                item
                for item in payload["debts"]
                if item.get("amount") and item.get("status") != "not_found"
            ]
            if active_debts:
                findings.append(
                    RiskFinding(
                        code="active_debts",
                        title="Найдены задолженности",
                        description="По проверяемому лицу обнаружены активные задолженности.",
                        level=RiskLevel.HIGH,
                        score=20,
                        source=source,
                        evidence={"debts": active_debts},
                    )
                )
        for case in payload.get("court_cases", []):
            if case.get("case_number"):
                findings.append(
                    RiskFinding(
                        code="court_case_found",
                        title="Найдено судебное дело",
                        description="В судебных источниках найдено дело с участием проверяемого лица.",
                        level=RiskLevel.MEDIUM,
                        score=15,
                        source=source,
                        evidence=case,
                    )
                )
        return findings

    def _deduplicate(self, findings: list[RiskFinding]) -> list[RiskFinding]:
        seen = set()
        result = []
        for finding in findings:
            key = (finding.code, finding.source)
            if key in seen:
                continue
            seen.add(key)
            result.append(finding)
        return result

    def _level_for_score(self, score: int) -> str:
        if score >= 80:
            return RiskLevel.CRITICAL
        if score >= 50:
            return RiskLevel.HIGH
        if score >= 20:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _summary_text(self, score: int, level: str, findings: list[RiskFinding]) -> str:
        if not findings:
            return "Критичных совпадений и подозрительных признаков не найдено."
        titles = "; ".join(finding.title for finding in findings[:5])
        return f"Итоговый риск: {score}/100 ({level}). Ключевые признаки: {titles}."
