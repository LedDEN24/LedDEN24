from __future__ import annotations

from apps.checks.models import Source

from .common import ConfigurableSourceParser


class EfrsbParser(ConfigurableSourceParser):
    source = Source.EFRSB
    risk_flags = ("bankruptcy", "creditor_claims", "transaction_challenge")
