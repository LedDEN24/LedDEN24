from __future__ import annotations

from apps.checks.models import Source

from .common import ConfigurableSourceParser


class KadArbitrParser(ConfigurableSourceParser):
    source = Source.KAD_ARBITR
    risk_flags = ("arbitration_cases", "financial_disputes", "transaction_challenge")


class RussianCourtsParser(ConfigurableSourceParser):
    source = Source.COURTS
    risk_flags = ("civil_cases", "criminal_cases", "ownership_disputes")
