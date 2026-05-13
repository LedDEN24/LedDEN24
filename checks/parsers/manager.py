from __future__ import annotations

import asyncio
import logging
from collections.abc import Iterable

from .avito import AvitoParser
from .base import BaseParser, ParsedSourceResult, ParserQuery
from .cadastral_map import CadastralMapParser
from .cian import CianParser
from .courts import RussianCourtsParser
from .developers import ProblemDevelopersParser
from .domclick import DomclickParser
from .efrsb import EFRSBParser
from .fssp import FSSPParser
from .kad_arbitr import KadArbitrParser
from .news_media import NewsMediaParser
from .rosreestr import RosreestrParser
from .telegram import TelegramOpenSourcesParser

logger = logging.getLogger(__name__)


def default_parser_classes() -> list[type[BaseParser]]:
    return [
        FSSPParser,
        EFRSBParser,
        KadArbitrParser,
        RussianCourtsParser,
        RosreestrParser,
        CadastralMapParser,
        AvitoParser,
        CianParser,
        DomclickParser,
        NewsMediaParser,
        TelegramOpenSourcesParser,
        ProblemDevelopersParser,
    ]


class ParserManager:
    def __init__(self, parser_classes: Iterable[type[BaseParser]] | None = None) -> None:
        self.parser_classes = list(parser_classes or default_parser_classes())

    async def run_all(self, query: ParserQuery) -> list[ParsedSourceResult]:
        parsers = [parser_class() for parser_class in self.parser_classes]
        logger.info("starting parsers", extra={"sources": [parser.source_name for parser in parsers]})
        results = await asyncio.gather(*(parser.parse(query) for parser in parsers))
        logger.info("parsers finished", extra={"count": len(results)})
        return list(results)

    async def run_selected(self, query: ParserQuery, sources: Iterable[str]) -> list[ParsedSourceResult]:
        selected = set(sources)
        parser_classes: list[type[BaseParser]] = [
            parser_class
            for parser_class in self.parser_classes
            if getattr(parser_class, "source_name", "") in selected
        ]
        return await ParserManager(parser_classes).run_all(query)
