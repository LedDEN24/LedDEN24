from __future__ import annotations

from .base import KeywordHtmlParser, ParserQuery


class KadArbitrParser(KeywordHtmlParser):
    source_name = "kad_arbitr"
    base_url = "https://kad.arbitr.ru/"
    risk_keywords = ("ответчик", "банкротство", "иск", "взыскание", "обеспечительные меры")

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        return {"q": query.inn or query.full_name or query.address}
