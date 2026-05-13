from checks.services.parsers.base import BaseParserService
from checks.services.parsers.sources import (
    AvitoParserService,
    CadastralMapParserService,
    CianParserService,
    DomclickParserService,
    EFRSBParserService,
    FSSPParserService,
    KadArbitrParserService,
    NewsParserService,
    ProblemDevelopersParserService,
    RFCourtsParserService,
    RosreestrParserService,
    TelegramParserService,
)


def get_parser_classes() -> list[type[BaseParserService]]:
    return [
        FSSPParserService,
        EFRSBParserService,
        KadArbitrParserService,
        RFCourtsParserService,
        RosreestrParserService,
        CadastralMapParserService,
        AvitoParserService,
        CianParserService,
        DomclickParserService,
        NewsParserService,
        TelegramParserService,
        ProblemDevelopersParserService,
    ]
