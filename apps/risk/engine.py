from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field
from decimal import Decimal
from typing import Any

from apps.checks.models import ParserResult


@dataclass(frozen=True)
class RiskRule:
    category: str
    severity: str
    score: Decimal
    title: str
    description: str


@dataclass
class RiskAnalysis:
    score: int
    summary: str
    findings: list[dict[str, Any]] = field(default_factory=list)
    timeline: list[dict[str, Any]] = field(default_factory=list)
    matches: list[dict[str, Any]] = field(default_factory=list)


RULES: dict[str, RiskRule] = {
    "debts": RiskRule(
        "financial",
        "high",
        Decimal("18"),
        "Найдены долги",
        "Обнаружены признаки долговой нагрузки продавца.",
    ),
    "enforcement_proceedings": RiskRule(
        "financial",
        "high",
        Decimal("20"),
        "Исполнительные производства",
        "Найдены активные или исторические исполнительные производства.",
    ),
    "asset_seizure": RiskRule(
        "encumbrance",
        "critical",
        Decimal("30"),
        "Возможный арест имущества",
        "Источник указывает на аресты или ограничения.",
    ),
    "bankruptcy": RiskRule(
        "bankruptcy",
        "critical",
        Decimal("28"),
        "Риск банкротства",
        "Найдены признаки банкротства или процедуры несостоятельности.",
    ),
    "transaction_challenge": RiskRule(
        "legal",
        "critical",
        Decimal("24"),
        "Риск оспаривания сделки",
        "Есть признаки споров, которые могут затронуть сделку.",
    ),
    "arbitration_cases": RiskRule(
        "court",
        "medium",
        Decimal("12"),
        "Арбитражные дела",
        "Найдены арбитражные дела, связанные с участником.",
    ),
    "civil_cases": RiskRule(
        "court",
        "medium",
        Decimal("10"),
        "Судебные дела",
        "Найдены судебные дела общей юрисдикции.",
    ),
    "criminal_cases": RiskRule(
        "court",
        "critical",
        Decimal("25"),
        "Уголовно-правовые риски",
        "Найдены признаки уголовных споров или материалов.",
    ),
    "ownership_disputes": RiskRule(
        "ownership",
        "high",
        Decimal("20"),
        "Споры о праве",
        "Возможны споры о праве собственности.",
    ),
    "encumbrances": RiskRule(
        "encumbrance",
        "high",
        Decimal("20"),
        "Обременения",
        "Найдены обременения или ограничения регистрации.",
    ),
    "arrests": RiskRule(
        "encumbrance",
        "critical",
        Decimal("30"),
        "Арест объекта",
        "Найдены признаки ареста объекта недвижимости.",
    ),
    "ownership_history": RiskRule(
        "ownership",
        "medium",
        Decimal("10"),
        "История собственников требует проверки",
        "История переходов права содержит значимые события.",
    ),
    "cadastral_mismatch": RiskRule(
        "property",
        "high",
        Decimal("18"),
        "Несовпадение кадастровых данных",
        "Адрес или кадастровые сведения расходятся.",
    ),
    "invalid_cadastral_number": RiskRule(
        "property",
        "critical",
        Decimal("25"),
        "Некорректный кадастровый номер",
        "Кадастровый номер не подтвержден источником.",
    ),
    "tax_debt": RiskRule(
        "financial",
        "medium",
        Decimal("10"),
        "Налоговая задолженность",
        "Есть признаки налоговой задолженности.",
    ),
    "duplicate_ads": RiskRule(
        "ads",
        "medium",
        Decimal("8"),
        "Дубли объявлений",
        "Найдены похожие объявления в открытых источниках.",
    ),
    "fake_listing": RiskRule(
        "fraud",
        "high",
        Decimal("18"),
        "Признаки поддельного объявления",
        "Объявление похоже на мошенническое или вводящее в заблуждение.",
    ),
    "multiple_sales": RiskRule(
        "fraud",
        "high",
        Decimal("16"),
        "Множественные продажи",
        "Найдены признаки параллельных или повторных продаж.",
    ),
    "seller_mismatch": RiskRule(
        "fraud",
        "medium",
        Decimal("12"),
        "Несовпадение продавца",
        "Данные продавца не совпадают между источниками.",
    ),
    "fraud_mentions": RiskRule(
        "fraud",
        "high",
        Decimal("20"),
        "Упоминания мошенничества",
        "Открытые источники содержат негативные упоминания.",
    ),
    "blacklist_match": RiskRule(
        "fraud",
        "critical",
        Decimal("30"),
        "Совпадение с базой мошенников",
        "Найдено совпадение с риск-реестром.",
    ),
    "document_forgery": RiskRule(
        "fraud",
        "critical",
        Decimal("26"),
        "Риск подделки документов",
        "Есть признаки поддельных документов.",
    ),
    "problem_developer": RiskRule(
        "developer",
        "high",
        Decimal("18"),
        "Проблемный застройщик",
        "Объект связан с проблемным застройщиком.",
    ),
    "negative_news": RiskRule(
        "media",
        "medium",
        Decimal("8"),
        "Негативные публикации",
        "СМИ содержат негативные публикации о связанной стороне.",
    ),
}


class RiskEngine:
    def analyse(self, parser_results: Iterable[ParserResult]) -> RiskAnalysis:
        findings: list[dict[str, Any]] = []
        matches: list[dict[str, Any]] = []
        timeline: list[dict[str, Any]] = []
        total = Decimal("0")

        for parser_result in parser_results:
            payload = parser_result.normalized_payload or {}
            if payload.get("configured") is False:
                continue
            records = payload.get("records", [])
            matches_count = int(payload.get("matches_count") or len(records or []))
            if matches_count <= 0:
                continue
            matches.append({"source": parser_result.source, "count": matches_count, "records": records})
            for record in records:
                if isinstance(record, dict) and (record.get("date") or record.get("published_at")):
                    timeline.append({"source": parser_result.source, **record})
            for flag in payload.get("risk_flags", []):
                rule = RULES.get(flag)
                if not rule:
                    continue
                total += rule.score
                findings.append(
                    {
                        "source": parser_result.source,
                        "category": rule.category,
                        "severity": rule.severity,
                        "score": str(rule.score),
                        "title": rule.title,
                        "description": rule.description,
                        "evidence": {"flag": flag, "records": records[:5]},
                    }
                )

        score = min(int(total), 100)
        summary = self._summary(score, findings)
        return RiskAnalysis(score=score, summary=summary, findings=findings, timeline=timeline, matches=matches)

    @staticmethod
    def _summary(score: int, findings: list[dict[str, Any]]) -> str:
        critical = sum(1 for item in findings if item["severity"] == "critical")
        high = sum(1 for item in findings if item["severity"] == "high")
        if score >= 70 or critical:
            return f"Высокий риск: критических факторов {critical}, высоких факторов {high}."
        if score >= 35 or high:
            return f"Средний риск: высоких факторов {high}, требуется ручная юридическая проверка."
        if findings:
            return "Низкий или умеренный риск: найдены факторы, требующие уточнения."
        return "Существенные риски по подключенным источникам не обнаружены."
