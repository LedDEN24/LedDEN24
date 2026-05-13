from __future__ import annotations

from .base import KeywordHtmlParser, ParserQuery


class CianParser(KeywordHtmlParser):
    source_name = "cian"
    base_url = "https://www.cian.ru/search/"
    risk_keywords = ("срочная продажа", "ниже рынка", "обременение", "ипотека")

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        return {"query": query.address}
