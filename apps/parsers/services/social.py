from __future__ import annotations

from apps.checks.models import Source

from .common import ConfigurableSourceParser


class PublicTelegramForumParser(ConfigurableSourceParser):
    source = Source.TELEGRAM_FORUMS
    risk_flags = ("fraud_mentions", "seller_reputation", "public_complaints")
