from __future__ import annotations

from apps.checks.models import Source

from .common import ConfigurableSourceParser


class NewsMediaParser(ConfigurableSourceParser):
    source = Source.MEDIA
    risk_flags = ("negative_news", "legal_conflict", "developer_reputation")
