from __future__ import annotations

from .base import KeywordHtmlParser, ParserQuery


class EFRSBParser(KeywordHtmlParser):
    source_name = "efrsb"
    base_url = "https://bankrot.fedresurs.ru/search"
    risk_keywords = ("банкрот", "наблюдение", "конкурсное производство", "реализация имущества")

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        return {"searchString": query.inn or query.full_name}
