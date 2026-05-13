from __future__ import annotations

from .common import ConfigurableSourceParser


class TaxDataParser(ConfigurableSourceParser):
    source = "tax"
    risk_flags = ("tax_debt", "invalid_inn", "business_affiliation")
