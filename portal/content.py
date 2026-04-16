from __future__ import annotations

import json
import re
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from django.conf import settings
from django.utils.html import escape
from django.utils.safestring import SafeString, mark_safe


@dataclass(frozen=True, slots=True)
class DocumentMeta:
    slug: str
    title: str
    summary: str
    category: str
    category_title: str
    relative_path: str
    nav_label: str


DOCUMENTS: tuple[DocumentMeta, ...] = (
    DocumentMeta(
        slug="overview",
        title="Обзор комплекта",
        summary="Краткая карта проекта, сценарии использования и ограничения легальной проверки.",
        category="guide",
        category_title="Обзор",
        relative_path="README.md",
        nav_label="Обзор",
    ),
    DocumentMeta(
        slug="self-check",
        title="Чеклист самопроверки",
        summary="Пошаговая самопроверка по ФССП, судам, банкротным публикациям и кредитной истории.",
        category="checklist",
        category_title="Чеклисты",
        relative_path="checklists/self-check.md",
        nav_label="Самопроверка",
    ),
    DocumentMeta(
        slug="third-party-check",
        title="Проверка третьего лица по согласию",
        summary="Безопасный сценарий проверки кандидата, контрагента или заемщика в открытом правовом контуре.",
        category="checklist",
        category_title="Чеклисты",
        relative_path="checklists/third-party-with-consent.md",
        nav_label="Проверка по согласию",
    ),
    DocumentMeta(
        slug="open-registries-consent",
        title="Согласие на проверку по открытым реестрам",
        summary="Шаблон согласия на обработку данных и поиск по открытым государственным источникам.",
        category="template",
        category_title="Шаблоны",
        relative_path="templates/open-registries-consent.md",
        nav_label="Согласие на реестры",
    ),
    DocumentMeta(
        slug="credit-report-consent",
        title="Передача кредитного отчета самим субъектом",
        summary="Шаблон, при котором субъект законно получает свою кредитную историю и сам передает отчет.",
        category="template",
        category_title="Шаблоны",
        relative_path="templates/credit-report-submission-consent.md",
        nav_label="Передача кредитного отчета",
    ),
    DocumentMeta(
        slug="screening-request-form",
        title="Карточка запуска проверки",
        summary="Внутренняя форма для фиксации цели, источников, результатов и срока хранения проверки.",
        category="template",
        category_title="Шаблоны",
        relative_path="templates/screening-request-form.md",
        nav_label="Карточка запуска",
    ),
)

DOCUMENTS_BY_SLUG = {document.slug: document for document in DOCUMENTS}

HEADING_PATTERN = re.compile(r"^(#{1,6})\s+(.*)$")
ORDERED_LIST_PATTERN = re.compile(r"^\s*\d+\.\s+(.*)$")
UNORDERED_LIST_PATTERN = re.compile(r"^\s*-\s+(.*)$")


def get_document_sections() -> list[dict[str, object]]:
    categories = ("guide", "checklist", "template")
    sections: list[dict[str, object]] = []

    for category in categories:
        documents = [document for document in DOCUMENTS if document.category == category]
        if not documents:
            continue

        sections.append(
            {
                "slug": category,
                "title": documents[0].category_title,
                "documents": documents,
            }
        )

    return sections


def get_document_meta(slug: str) -> DocumentMeta | None:
    return DOCUMENTS_BY_SLUG.get(slug)


def get_document(slug: str) -> dict[str, object] | None:
    document = get_document_meta(slug)
    if document is None:
        return None

    raw_content = _read_content_file(document.relative_path)
    return {
        "meta": document,
        "raw_content": raw_content,
        "html_content": markdown_to_html(raw_content),
    }


@lru_cache(maxsize=1)
def get_sources_payload() -> dict[str, object]:
    payload = _read_content_file("data/official_sources.json")
    return json.loads(payload)


def markdown_to_html(markdown_text: str) -> SafeString:
    html_lines: list[str] = []
    paragraph_lines: list[str] = []
    active_list: str | None = None

    def close_list() -> None:
        nonlocal active_list
        if active_list is not None:
            html_lines.append(f"</{active_list}>")
            active_list = None

    def flush_paragraph() -> None:
        if not paragraph_lines:
            return
        content = " ".join(line.strip() for line in paragraph_lines if line.strip())
        if content:
            html_lines.append(f"<p>{_format_inline(content)}</p>")
        paragraph_lines.clear()

    for line in markdown_text.splitlines():
        stripped = line.strip()

        if not stripped:
            flush_paragraph()
            close_list()
            continue

        heading_match = HEADING_PATTERN.match(stripped)
        if heading_match:
            flush_paragraph()
            close_list()
            level = len(heading_match.group(1))
            title = _format_inline(heading_match.group(2))
            html_lines.append(f"<h{level}>{title}</h{level}>")
            continue

        if stripped == "---":
            flush_paragraph()
            close_list()
            html_lines.append("<hr>")
            continue

        ordered_match = ORDERED_LIST_PATTERN.match(line)
        if ordered_match:
            flush_paragraph()
            if active_list != "ol":
                close_list()
                active_list = "ol"
                html_lines.append("<ol>")
            html_lines.append(f"<li>{_format_inline(ordered_match.group(1))}</li>")
            continue

        unordered_match = UNORDERED_LIST_PATTERN.match(line)
        if unordered_match:
            flush_paragraph()
            if active_list != "ul":
                close_list()
                active_list = "ul"
                html_lines.append("<ul>")
            html_lines.append(f"<li>{_format_inline(unordered_match.group(1))}</li>")
            continue

        close_list()
        paragraph_lines.append(stripped)

    flush_paragraph()
    close_list()

    return mark_safe("\n".join(html_lines))


def _content_root() -> Path:
    return Path(settings.LEGAL_CHECKS_CONTENT_DIR)


def _read_content_file(relative_path: str) -> str:
    return (_content_root() / relative_path).read_text(encoding="utf-8")


def _format_inline(text: str) -> str:
    parts = re.split(r"(`[^`]+`)", text)
    rendered: list[str] = []

    for part in parts:
        if not part:
            continue
        if part.startswith("`") and part.endswith("`"):
            rendered.append(f"<code>{escape(part[1:-1])}</code>")
        else:
            rendered.append(escape(part))

    return "".join(rendered)
