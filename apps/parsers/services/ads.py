from __future__ import annotations

from .common import ConfigurableSourceParser


class AvitoParser(ConfigurableSourceParser):
    source = "avito"
    risk_flags = ("duplicate_ads", "fake_listing", "price_anomaly")


class CianParser(ConfigurableSourceParser):
    source = "cian"
    risk_flags = ("duplicate_ads", "multiple_sales", "price_anomaly")


class DomclickParser(ConfigurableSourceParser):
    source = "domclick"
    risk_flags = ("duplicate_ads", "seller_mismatch", "price_anomaly")
