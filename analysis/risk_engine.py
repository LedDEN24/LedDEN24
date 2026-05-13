from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum
from typing import Any


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass(frozen=True)
class RiskFinding:
    code: str
    title: str
    severity: Severity
    score_impact: int
    explanation: str
    evidence: dict[str, Any] = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)


class RiskEngine:
    """Deterministic baseline risk model; LLM output is advisory and never replaces it."""

    def evaluate(self, aggregated: dict[str, Any]) -> tuple[int, list[RiskFinding]]:
        findings: list[RiskFinding] = []
        debts = aggregated.get("debts", [])
        court_cases = aggregated.get("court_cases", [])
        bankruptcy_records = aggregated.get("bankruptcy_records", [])
        encumbrances = aggregated.get("encumbrances", [])
        ownership_transitions = aggregated.get("ownership_transitions", [])
        ads = aggregated.get("ads", [])
        fraud_matches = aggregated.get("fraud_matches", [])
        matches = aggregated.get("matches", [])

        if debts:
            total_debt = sum(float(item.get("amount") or 0) for item in debts)
            findings.append(
                RiskFinding(
                    code="seller_debts_found",
                    title="Найдены долги продавца",
                    severity=Severity.HIGH if total_debt >= 500_000 else Severity.MEDIUM,
                    score_impact=22 if total_debt >= 500_000 else 12,
                    explanation="Исполнительные производства могут привести к оспариванию сделки или аресту активов.",
                    evidence={"count": len(debts), "total_amount": total_debt},
                    recommendations=["Запросить актуальные справки ФССП", "Проверить отсутствие ареста перед расчетами"],
                )
            )

        if court_cases:
            findings.append(
                RiskFinding(
                    code="court_cases_found",
                    title="Найдены судебные споры",
                    severity=Severity.HIGH,
                    score_impact=min(25, 8 + len(court_cases) * 4),
                    explanation="Судебные дела с участием продавца или объекта повышают риск последующего спора.",
                    evidence={"count": len(court_cases)},
                    recommendations=["Изучить предмет каждого дела", "Получить юридическое заключение по активным делам"],
                )
            )

        if bankruptcy_records:
            findings.append(
                RiskFinding(
                    code="bankruptcy_found",
                    title="Найдены признаки банкротства",
                    severity=Severity.CRITICAL,
                    score_impact=35,
                    explanation="Сделки должника могут быть оспорены арбитражным управляющим или кредиторами.",
                    evidence={"count": len(bankruptcy_records)},
                    recommendations=["Не проводить сделку без анализа банкротного дела", "Проверить дату и цену прошлых сделок"],
                )
            )

        if encumbrances:
            findings.append(
                RiskFinding(
                    code="property_encumbrances",
                    title="Найдены обременения объекта",
                    severity=Severity.CRITICAL,
                    score_impact=30,
                    explanation="Обременения ограничивают распоряжение объектом и могут блокировать регистрацию перехода права.",
                    evidence={"encumbrances": encumbrances},
                    recommendations=["Получить свежую выписку ЕГРН", "Закрыть обременения до подписания договора"],
                )
            )

        if len(ownership_transitions) >= 3:
            findings.append(
                RiskFinding(
                    code="multiple_recent_sales",
                    title="Множественные переходы права",
                    severity=Severity.HIGH,
                    score_impact=18,
                    explanation="Частая перепродажа объекта может указывать на транзитную сделку или схему сокрытия рисков.",
                    evidence={"transitions_count": len(ownership_transitions)},
                    recommendations=["Проверить основания всех переходов права", "Сравнить цены прошлых сделок"],
                )
            )

        suspicious_ads = [ad for ad in ads if ad.get("is_suspicious")]
        if suspicious_ads:
            findings.append(
                RiskFinding(
                    code="suspicious_ads",
                    title="Подозрительные объявления",
                    severity=Severity.MEDIUM,
                    score_impact=min(18, 6 + len(suspicious_ads) * 3),
                    explanation="Дубли, нереалистичная цена или несоответствие контактов могут быть признаком мошенничества.",
                    evidence={"count": len(suspicious_ads)},
                    recommendations=["Сверить контакты продавца", "Проверить историю публикаций объявления"],
                )
            )

        if fraud_matches:
            findings.append(
                RiskFinding(
                    code="fraud_match",
                    title="Совпадения с мошенническими признаками",
                    severity=Severity.CRITICAL,
                    score_impact=40,
                    explanation="Найдены совпадения по открытым базам мошенничества или судебных споров.",
                    evidence={"matches": fraud_matches},
                    recommendations=["Прекратить дистанционные авансы", "Провести расширенную идентификацию контрагента"],
                )
            )

        if matches:
            findings.append(
                RiskFinding(
                    code="cross_source_match",
                    title="Совпадения в нескольких источниках",
                    severity=Severity.HIGH,
                    score_impact=min(20, len(matches) * 5),
                    explanation="Один и тот же субъект найден в нескольких риск-источниках.",
                    evidence={"matches": matches},
                    recommendations=["Проверить совпадение персональных данных", "Запросить документы, подтверждающие отсутствие рисков"],
                )
            )

        score = min(100, sum(finding.score_impact for finding in findings))
        return score, findings
