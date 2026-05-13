from __future__ import annotations

from .common import ConfigurableSourceParser


class PublicTelegramForumParser(ConfigurableSourceParser):
    source = "telegram_forums"
    risk_flags = ("fraud_mentions", "seller_reputation", "public_complaints")
