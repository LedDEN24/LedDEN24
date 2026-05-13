from __future__ import annotations

from .base import KeywordHtmlParser, ParserQuery


class ProblemDevelopersParser(KeywordHtmlParser):
    source_name = "problem_developers"
    base_url = "https://наш.дом.рф/"
    risk_keywords = ("проблемный", "банкрот", "срыв сроков", "обманутые дольщики", "наблюдение")

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        return {"search": query.address or query.inn or query.full_name}
