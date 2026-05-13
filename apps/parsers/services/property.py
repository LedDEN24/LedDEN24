from __future__ import annotations

from .common import ConfigurableSourceParser


class RosreestrParser(ConfigurableSourceParser):
    source = "rosreestr"
    risk_flags = ("encumbrances", "arrests", "ownership_history", "registration_restrictions")


class CadastralMapParser(ConfigurableSourceParser):
    source = "cadastral_map"
    risk_flags = ("cadastral_mismatch", "boundary_disputes", "invalid_cadastral_number")
