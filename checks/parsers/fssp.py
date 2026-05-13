from __future__ import annotations

from .base import KeywordHtmlParser, ParserQuery


class FSSPParser(KeywordHtmlParser):
    source_name = "fssp"
    base_url = "https://fssp.gov.ru/iss/ip/"
    risk_keywords = ("исполнительное производство", "задолженность", "розыск", "арест")
    result_selector = "body"

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        return {
            "is": "1",
            "region": "-1",
            "lastname": query.full_name,
            "inn": query.inn,
        }
