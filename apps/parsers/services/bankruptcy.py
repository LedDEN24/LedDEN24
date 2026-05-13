from __future__ import annotations

from .common import ConfigurableSourceParser


class EfrsbParser(ConfigurableSourceParser):
    source = "efrsb"
    risk_flags = ("bankruptcy", "creditor_claims", "transaction_challenge")
