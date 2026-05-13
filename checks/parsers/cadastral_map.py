from __future__ import annotations

from .base import KeywordHtmlParser, ParserQuery


class CadastralMapParser(KeywordHtmlParser):
    source_name = "cadastral_map"
    base_url = "https://pkk.rosreestr.ru/"
    risk_keywords = ("границы не установлены", "снят с учета", "спор", "ограничение")

    def build_params(self, query: ParserQuery) -> dict[str, str]:
        return {"text": query.cadastral_number or query.address}
