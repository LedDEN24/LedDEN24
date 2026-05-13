from __future__ import annotations

from apps.checks.models import Source

from .common import ConfigurableSourceParser


class FraudRegistryParser(ConfigurableSourceParser):
    source = Source.FRAUD_REGISTRIES
    risk_flags = ("fraud_pattern", "blacklist_match", "document_forgery")
