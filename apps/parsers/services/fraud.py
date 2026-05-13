from __future__ import annotations

from .common import ConfigurableSourceParser


class FraudRegistryParser(ConfigurableSourceParser):
    source = "fraud_registries"
    risk_flags = ("fraud_pattern", "blacklist_match", "document_forgery")
