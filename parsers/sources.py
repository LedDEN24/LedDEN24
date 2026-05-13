from __future__ import annotations

import hashlib
from typing import Any

from bs4 import BeautifulSoup

from parsers.base import BaseParser, ParserInput
from parsers.manager import ParserRegistry


class FsspParser(BaseParser):
    source = "fssp"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        # The public service often uses captcha; the architecture supports passing the token here.
        return {
            "debts": [],
            "query": {"name": parser_input.seller_full_name, "inn": parser_input.inn},
            "captcha_token_used": bool(captcha_token),
        }


class EfrsbBankruptcyParser(BaseParser):
    source = "efrsb"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        return {
            "bankruptcy_records": [],
            "query": {"name": parser_input.seller_full_name, "inn": parser_input.inn},
        }


class KadArbitrParser(BaseParser):
    source = "kad_arbitr"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        return {
            "court_cases": [],
            "query": {"name": parser_input.seller_full_name, "inn": parser_input.inn},
        }


class GeneralCourtParser(BaseParser):
    source = "rf_courts"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        return {"court_cases": [], "query": {"name": parser_input.seller_full_name}}


class RosreestrParser(BaseParser):
    source = "rosreestr"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        return {
            "property": {
                "cadastral_number": parser_input.cadastral_number,
                "address": parser_input.address,
                "encumbrances": [],
                "ownership_transitions": [],
            }
        }


class PublicCadastralMapParser(BaseParser):
    source = "public_cadastral_map"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        return {
            "cadastral": {
                "number": parser_input.cadastral_number,
                "geometry_hash": _stable_hash(parser_input.cadastral_number),
                "land_category": None,
            }
        }


class TaxDataParser(BaseParser):
    source = "tax"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        return {"taxpayer": {"inn": parser_input.inn, "risk_flags": []}}


class AdsParser(BaseParser):
    source = "ads"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        return {
            "ads": [],
            "sources": ["avito", "cian", "domclick"],
            "duplicate_detection": {"address": parser_input.address, "cadastral_number": parser_input.cadastral_number},
        }


class TelegramForumsParser(BaseParser):
    source = "telegram_forums"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        return {"mentions": [], "query": {"address": parser_input.address, "phone": parser_input.phone}}


class ProblemDevelopersParser(BaseParser):
    source = "problem_developers"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        return {"developer_records": [], "query": {"address": parser_input.address}}


class FraudAndDisputesParser(BaseParser):
    source = "fraud_disputes"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        return {
            "fraud_matches": [],
            "query": {
                "name": parser_input.seller_full_name,
                "phone": parser_input.phone,
                "email": parser_input.email,
            },
        }


class NewsMediaParser(BaseParser):
    source = "news_media"

    async def parse(self, parser_input: ParserInput, *, captcha_token: str = "") -> dict[str, Any]:
        html = "<html><body></body></html>"
        soup = BeautifulSoup(html, "lxml")
        return {"mentions": [], "parsed_title": soup.title.text if soup.title else ""}


def _stable_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def default_registry() -> ParserRegistry:
    parsers: dict[str, type[BaseParser]] = {
        parser.source: parser
        for parser in [
            FsspParser,
            EfrsbBankruptcyParser,
            KadArbitrParser,
            GeneralCourtParser,
            RosreestrParser,
            PublicCadastralMapParser,
            TaxDataParser,
            AdsParser,
            TelegramForumsParser,
            ProblemDevelopersParser,
            FraudAndDisputesParser,
            NewsMediaParser,
        ]
    }
    return ParserRegistry(parsers=parsers)
