from __future__ import annotations

from .common import ConfigurableSourceParser


class KadArbitrParser(ConfigurableSourceParser):
    source = "kad_arbitr"
    risk_flags = ("arbitration_cases", "financial_disputes", "transaction_challenge")


class RussianCourtsParser(ConfigurableSourceParser):
    source = "courts"
    risk_flags = ("civil_cases", "criminal_cases", "ownership_disputes")
