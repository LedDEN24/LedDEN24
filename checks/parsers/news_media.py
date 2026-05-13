from __future__ import annotations

from .base import KeywordHtmlParser, ParserQuery


class NewsMediaParser(KeywordHtmlParser):
    source_name = "news_media"
    base_url = "https://news.google.com/search"
    risk_keywords = ("мошенничество", "обманутые дольщики", "суд", "банкротство", "задержан")

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        subject = " ".join(value for value in (query.address, query.full_name, query.inn) if value)
        return {"q": subject, "hl": "ru", "gl": "RU", "ceid": "RU:ru"}
