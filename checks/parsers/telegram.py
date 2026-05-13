from __future__ import annotations

from .base import KeywordHtmlParser, ParserQuery


class TelegramOpenSourcesParser(KeywordHtmlParser):
    source_name = "telegram_open_sources"
    base_url = "https://tgstat.ru/search"
    risk_keywords = ("скам", "мошенник", "проблемный объект", "обманутые дольщики")

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        subject = " ".join(value for value in (query.address, query.full_name, query.phone, query.inn) if value)
        return {"q": subject}
