from __future__ import annotations

from .common import ConfigurableSourceParser


class FsspParser(ConfigurableSourceParser):
    source = "fssp"
    risk_flags = ("debts", "enforcement_proceedings", "asset_seizure")


class EnforcementDatabaseParser(ConfigurableSourceParser):
    source = "enforcement"
    risk_flags = ("debts", "active_proceedings")
