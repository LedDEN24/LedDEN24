from __future__ import annotations

from .common import ConfigurableSourceParser


class NewsMediaParser(ConfigurableSourceParser):
    source = "media"
    risk_flags = ("negative_news", "legal_conflict", "developer_reputation")
