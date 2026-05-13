from __future__ import annotations

from .base import KeywordHtmlParser, ParserQuery


class DomclickParser(KeywordHtmlParser):
    source_name = "domclick"
    base_url = "https://domclick.ru/search"
    risk_keywords = ("залог", "ипотека", "срочно", "снижение цены")

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        return {"q": query.address}
