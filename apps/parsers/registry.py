from __future__ import annotations

from collections.abc import Iterable

from .base import BaseParser
from .infrastructure import CaptchaService, build_default_dependency
from .services import (
    AvitoParser,
    CadastralMapParser,
    CianParser,
    DomclickParser,
    EfrsbParser,
    EnforcementDatabaseParser,
    FraudRegistryParser,
    FsspParser,
    KadArbitrParser,
    NewsMediaParser,
    ProblemDevelopersParser,
    PublicTelegramForumParser,
    RosreestrParser,
    RussianCourtsParser,
    TaxDataParser,
)

type ParserClass = type[BaseParser]


DEFAULT_PARSERS: tuple[ParserClass, ...] = (
    FsspParser,
    EfrsbParser,
    KadArbitrParser,
    RussianCourtsParser,
    RosreestrParser,
    CadastralMapParser,
    TaxDataParser,
    EnforcementDatabaseParser,
    AvitoParser,
    CianParser,
    DomclickParser,
    PublicTelegramForumParser,
    ProblemDevelopersParser,
    FraudRegistryParser,
    NewsMediaParser,
)


def build_parsers(parser_classes: Iterable[ParserClass] = DEFAULT_PARSERS) -> list[BaseParser]:
    dependency = build_default_dependency()
    captcha_service = CaptchaService()
    return [parser_class(dependency=dependency, captcha_solver=captcha_service) for parser_class in parser_classes]
