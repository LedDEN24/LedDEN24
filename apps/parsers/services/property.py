from __future__ import annotations

from apps.checks.models import Source

from .common import ConfigurableSourceParser


class RosreestrParser(ConfigurableSourceParser):
    source = Source.ROSREESTR
    risk_flags = ("encumbrances", "arrests", "ownership_history", "registration_restrictions")


class CadastralMapParser(ConfigurableSourceParser):
    source = Source.CADASTRAL_MAP
    risk_flags = ("cadastral_mismatch", "boundary_disputes", "invalid_cadastral_number")
