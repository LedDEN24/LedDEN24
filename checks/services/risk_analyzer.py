from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from checks.models import Check, ParserResult, RiskSeverity
from checks.services.matching import MatchService


@dataclass(frozen=True)
class SuspiciousRule:
    code: str
    title: str
    severity: str
    weight: int
    keywords: tuple[str, ...]
    sources: tuple[str, ...] = ()


SUSPICIOUS_RULES = (
    SuspiciousRule(
        code="bankruptcy",
        title="Найдены признаки банкротства",
        severity=RiskSeverity.CRITICAL,
        weight=35,
        keywords=("банкрот", "конкурсное производство", "наблюдение", "реализация имущества"),
        sources=("efrsb", "kad_arbitr", "news_media", "problem_developers"),
    ),
    SuspiciousRule(
        code="enforcement_debt",
        title="Найдены признаки исполнительных производств или долгов",
        severity=RiskSeverity.HIGH,
        weight=25,
        keywords=("исполнительное производство", "задолженность", "должник", "взыскание"),
        sources=("fssp", "russian_courts", "kad_arbitr"),
    ),
    SuspiciousRule(
        code="property_encumbrance",
        title="Найдены признаки обременений объекта",
        severity=RiskSeverity.HIGH,
        weight=25,
        keywords=("обременение", "ипотека", "арест", "запрещение", "залог"),
        sources=("rosreestr", "cadastral_map", "domclick", "cian"),
    ),
    SuspiciousRule(
        code="below_market_listing",
        title="Объявления содержат признаки срочной или проблемной продажи",
        severity=RiskSeverity.MEDIUM,
        weight=15,
        keywords=("ниже рынка", "срочно", "торг", "проблем", "снижение цены"),
        sources=("avito", "cian", "domclick"),
    ),
    SuspiciousRule(
        code="negative_media",
        title="Найдены негативные публикации в СМИ или Telegram",
        severity=RiskSeverity.MEDIUM,
        weight=15,
        keywords=("мошенничество", "скам", "обманутые дольщики", "задержан", "проблемный объект"),
        sources=("news_media", "telegram_open_sources"),
    ),
)


class RiskAnalyzer:
    def analyze(self, check: Check, parser_results: list[ParserResult]) -> tuple[int, list[dict[str, Any]]]:
        risks: list[dict[str, Any]] = []
        seen_codes: set[tuple[str, int | None]] = set()

        for parser_result in parser_results:
            payload_text = str(parser_result.payload or {}).lower()
            matches = MatchService.find_matches(check, parser_result)
            if matches and parser_result.source in {"fssp", "efrsb", "kad_arbitr", "russian_courts"}:
                risk = self._build_risk(
                    parser_result,
                    code="identity_match_in_risk_source",
                    title="Совпадение персональных данных в риск-источнике",
                    severity=RiskSeverity.HIGH,
                    weight=20,
                    evidence={"matches": [match.__dict__ for match in matches]},
                )
                self._append_once(risks, seen_codes, risk)

            for rule in SUSPICIOUS_RULES:
                if rule.sources and parser_result.source not in rule.sources:
                    continue
                found = [keyword for keyword in rule.keywords if keyword in payload_text]
                if found:
                    risk = self._build_risk(
                        parser_result,
                        code=rule.code,
                        title=rule.title,
                        severity=rule.severity,
                        weight=rule.weight,
                        evidence={"source": parser_result.source, "keywords": found},
                    )
                    self._append_once(risks, seen_codes, risk)

            if parser_result.status == "failed":
                risk = self._build_risk(
                    parser_result,
                    code=f"source_unavailable_{parser_result.source}",
                    title=f"Источник {parser_result.source} недоступен",
                    severity=RiskSeverity.LOW,
                    weight=5,
                    evidence={"error": parser_result.error},
                )
                self._append_once(risks, seen_codes, risk)

        score = min(100, sum(risk["weight"] for risk in risks))
        return score, risks

    @staticmethod
    def _build_risk(
        parser_result: ParserResult,
        *,
        code: str,
        title: str,
        severity: str,
        weight: int,
        evidence: dict[str, Any],
    ) -> dict[str, Any]:
        return {
            "parser_result": parser_result,
            "code": code,
            "title": title,
            "description": _description_for(code, title),
            "severity": severity,
            "weight": weight,
            "evidence": evidence,
        }

    @staticmethod
    def _append_once(
        risks: list[dict[str, Any]],
        seen_codes: set[tuple[str, int | None]],
        risk: dict[str, Any],
    ) -> None:
        key = (risk["code"], getattr(risk["parser_result"], "pk", None))
        if key not in seen_codes:
            seen_codes.add(key)
            risks.append(risk)


def _description_for(code: str, title: str) -> str:
    descriptions = {
        "bankruptcy": "В открытых источниках обнаружены маркеры процедур банкротства или несостоятельности.",
        "enforcement_debt": "Найдены маркеры долгов, исполнительных производств или судебного взыскания.",
        "property_encumbrance": "В данных по объекту или объявлениях обнаружены признаки обременений.",
        "below_market_listing": "Объявления по объекту похожи на срочную или проблемную продажу.",
        "negative_media": "Найдены негативные публикации, которые требуют ручной проверки.",
        "identity_match_in_risk_source": "Персональные данные из запроса совпали с данными в риск-источнике.",
    }
    return descriptions.get(code, title)
