from __future__ import annotations

from apps.checks.models import Source

from .common import ConfigurableSourceParser


class TaxDataParser(ConfigurableSourceParser):
    source = Source.TAX
    risk_flags = ("tax_debt", "invalid_inn", "business_affiliation")
