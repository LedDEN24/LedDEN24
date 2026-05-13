from __future__ import annotations

from .base import KeywordHtmlParser, ParserQuery


class RussianCourtsParser(KeywordHtmlParser):
    source_name = "russian_courts"
    base_url = "https://sudrf.ru/"
    risk_keywords = ("ответчик", "должник", "взыскание", "арест", "залог")

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        return {"text": query.full_name or query.address}
