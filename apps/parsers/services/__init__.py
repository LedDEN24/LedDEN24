from __future__ import annotations

from .ads import AvitoParser, CianParser, DomclickParser
from .bankruptcy import EfrsbParser
from .courts import KadArbitrParser, RussianCourtsParser
from .developers import ProblemDevelopersParser
from .enforcement import EnforcementDatabaseParser, FsspParser
from .fraud import FraudRegistryParser
from .media import NewsMediaParser
from .property import CadastralMapParser, RosreestrParser
from .social import PublicTelegramForumParser
from .tax import TaxDataParser

__all__ = (
    "AvitoParser",
    "CadastralMapParser",
    "CianParser",
    "DomclickParser",
    "EfrsbParser",
    "EnforcementDatabaseParser",
    "FraudRegistryParser",
    "FsspParser",
    "KadArbitrParser",
    "NewsMediaParser",
    "ProblemDevelopersParser",
    "PublicTelegramForumParser",
    "RosreestrParser",
    "RussianCourtsParser",
    "TaxDataParser",
)
