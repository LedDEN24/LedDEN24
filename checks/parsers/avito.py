from __future__ import annotations

from .base import KeywordHtmlParser, ParserQuery


class AvitoParser(KeywordHtmlParser):
    source_name = "avito"
    base_url = "https://www.avito.ru/"
    risk_keywords = ("срочно", "торг", "ниже рынка", "проблем", "обремен")

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        return {"q": query.address}
