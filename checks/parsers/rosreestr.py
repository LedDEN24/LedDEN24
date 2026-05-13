from __future__ import annotations

from .base import KeywordHtmlParser, ParserQuery


class RosreestrParser(KeywordHtmlParser):
    source_name = "rosreestr"
    base_url = "https://rosreestr.gov.ru/"
    risk_keywords = ("обременение", "запрещение", "ипотека", "арест")

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        return {"text": query.cadastral_number or query.address}
