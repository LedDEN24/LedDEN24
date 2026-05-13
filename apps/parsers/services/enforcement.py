from __future__ import annotations

from apps.checks.models import Source

from .common import ConfigurableSourceParser


class FsspParser(ConfigurableSourceParser):
    source = Source.FSSP
    risk_flags = ("debts", "enforcement_proceedings", "asset_seizure")


class EnforcementDatabaseParser(ConfigurableSourceParser):
    source = Source.ENFORCEMENT
    risk_flags = ("debts", "active_proceedings")
