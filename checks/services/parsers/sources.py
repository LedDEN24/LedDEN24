from __future__ import annotations

from typing import Any

from checks.models import ParserSource
from checks.services.parsers.base import BaseParserService, ParserInput


class FSSPParserService(BaseParserService):
    source = ParserSource.FSSP.value
    display_name = "ФССП"

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            **super().build_fallback_payload(parser_input),
            "debts": [
                {
                    "debtor_name": parser_input.full_name,
                    "amount": 0,
                    "proceeding_number": "",
                    "status": "not_found",
                }
            ],
            "risk_markers": ["enforcement_proceeding"],
        }


class EFRSBParserService(BaseParserService):
    source = ParserSource.EFRSB.value
    display_name = "ЕФРСБ"

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            **super().build_fallback_payload(parser_input),
            "bankruptcy_messages": [],
            "risk_markers": ["bankruptcy"],
        }


class KadArbitrParserService(BaseParserService):
    source = ParserSource.KAD_ARBITR.value
    display_name = "КАД Арбитр"

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            **super().build_fallback_payload(parser_input),
            "court_cases": [
                {
                    "case_number": "",
                    "court_name": "Арбитражные суды",
                    "participant": parser_input.full_name,
                    "status": "not_found",
                }
            ],
            "risk_markers": ["arbitration_case"],
        }


class RFCourtsParserService(BaseParserService):
    source = ParserSource.RF_COURTS.value
    display_name = "Суды РФ"

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            **super().build_fallback_payload(parser_input),
            "court_cases": [],
            "risk_markers": ["civil_or_criminal_case"],
        }


class RosreestrParserService(BaseParserService):
    source = ParserSource.ROSREESTR.value
    display_name = "Росреестр"

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            **super().build_fallback_payload(parser_input),
            "properties": [
                {
                    "address": parser_input.address,
                    "cadastral_number": parser_input.cadastral_number,
                    "registration_status": "requires_verification",
                }
            ],
            "owners": [
                {
                    "full_name": parser_input.full_name,
                    "inn": parser_input.inn,
                    "phone": parser_input.phone,
                    "email": parser_input.email,
                }
            ],
            "risk_markers": ["encumbrance", "ownership_mismatch"],
        }


class CadastralMapParserService(BaseParserService):
    source = ParserSource.CADASTRAL_MAP.value
    display_name = "Публичная кадастровая карта"

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            **super().build_fallback_payload(parser_input),
            "properties": [
                {
                    "address": parser_input.address,
                    "cadastral_number": parser_input.cadastral_number,
                    "property_type": "unknown",
                    "area": None,
                }
            ],
            "risk_markers": ["cadastral_absence"],
        }


class AvitoParserService(BaseParserService):
    source = ParserSource.AVITO.value
    display_name = "Avito"

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            **super().build_fallback_payload(parser_input),
            "listings": [],
            "risk_markers": ["price_anomaly", "duplicate_listing"],
        }


class CianParserService(BaseParserService):
    source = ParserSource.CIAN.value
    display_name = "Cian"

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            **super().build_fallback_payload(parser_input),
            "listings": [],
            "risk_markers": ["listing_mismatch"],
        }


class DomclickParserService(BaseParserService):
    source = ParserSource.DOMCLICK.value
    display_name = "Domclick"

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            **super().build_fallback_payload(parser_input),
            "listings": [],
            "risk_markers": ["mortgage_or_pledge_signal"],
        }


class NewsParserService(BaseParserService):
    source = ParserSource.NEWS.value
    display_name = "Новости и СМИ"

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            **super().build_fallback_payload(parser_input),
            "mentions": [],
            "risk_markers": ["negative_media"],
        }


class TelegramParserService(BaseParserService):
    source = ParserSource.TELEGRAM.value
    display_name = "Открытые Telegram-источники"

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            **super().build_fallback_payload(parser_input),
            "mentions": [],
            "risk_markers": ["telegram_complaint"],
        }


class ProblemDevelopersParserService(BaseParserService):
    source = ParserSource.DEVELOPERS.value
    display_name = "Базы проблемных застройщиков"

    def build_fallback_payload(self, parser_input: ParserInput) -> dict[str, Any]:
        return {
            **super().build_fallback_payload(parser_input),
            "developers": [],
            "risk_markers": ["problem_developer"],
        }
