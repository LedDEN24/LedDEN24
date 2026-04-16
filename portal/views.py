from django.http import Http404, JsonResponse
from django.shortcuts import render

from .content import get_document, get_document_sections, get_sources_payload


def _base_context() -> dict[str, object]:
    sources_payload = get_sources_payload()
    return {
        "document_sections": get_document_sections(),
        "sources_count": len(sources_payload.get("sources", [])),
    }


def home(request):
    sources_payload = get_sources_payload()
    base_context = _base_context()
    document_sections = base_context["document_sections"]
    section_counts = {
        section["slug"]: len(section["documents"])
        for section in document_sections
    }
    hero_points = [
        "Только официальные судебные и государственные источники.",
        "Отдельный сценарий для самопроверки и проверки по согласию.",
        "Кредитная история вынесена в законный закрытый контур через БКИ.",
    ]
    feature_blocks = [
        {
            "title": "Проверка физлиц",
            "description": "Самопроверка перед сделкой, трудоустройством, поездкой или крупной финансовой заявкой.",
            "items": [
                "ФССП и действующие исполнительные производства",
                "Суды общей юрисдикции и движение дел",
                "Арбитраж, банкротство, Федресурс",
            ],
        },
        {
            "title": "Проверка по согласию",
            "description": "Легальный сценарий для кандидатов, контрагентов и заемщиков с фиксацией цели и объема данных.",
            "items": [
                "Согласие на работу с открытыми реестрами",
                "Минимизация идентификаторов и сроков хранения",
                "Карточка запуска и документированный вывод",
            ],
        },
        {
            "title": "Шаблоны для процесса",
            "description": "Готовые документы, чтобы сразу встроить проверку в кадровый, договорной или комплаенс-процесс.",
            "items": [
                "Согласие на проверку по открытым реестрам",
                "Согласие на передачу кредитного отчета самим субъектом",
                "Внутренняя форма запуска проверки",
            ],
        },
    ]
    trust_highlights = [
        {
            "title": "Без серых баз",
            "text": "Комплект прямо отделяет открытые источники от закрытых данных и не предполагает несанкционированный доступ к персональным данным.",
        },
        {
            "title": "Подходит для B2B и внутреннего комплаенса",
            "text": "Можно использовать как стартовую точку для кадровой, договорной, кредитной и контрагентской проверки при понятной цели.",
        },
        {
            "title": "Контент и API в одном проекте",
            "text": "Есть визуальный каталог источников, документы в markdown и JSON-реестр, который можно использовать в автоматизации.",
        },
    ]
    context = {
        **base_context,
        "project": sources_payload.get("project", "Legal Checks RF"),
        "version": sources_payload.get("version", ""),
        "updated_at": sources_payload.get("updated_at", ""),
        "rules_of_use": sources_payload.get("rules_of_use", []),
        "sources_preview": sources_payload.get("sources", [])[:3],
        "sources_full": sources_payload.get("sources", []),
        "documents_total": sum(section_counts.values()),
        "checklists_total": section_counts.get("checklist", 0),
        "templates_total": section_counts.get("template", 0),
        "hero_points": hero_points,
        "feature_blocks": feature_blocks,
        "trust_highlights": trust_highlights,
    }
    return render(request, "portal/home.html", context)


def document_detail(request, slug: str):
    document = get_document(slug)
    if document is None:
        raise Http404("Document not found")

    context = {
        **_base_context(),
        "document": document["meta"],
        "html_content": document["html_content"],
    }
    return render(request, "portal/document_detail.html", context)


def sources(request):
    sources_payload = get_sources_payload()
    context = {
        **_base_context(),
        "project": sources_payload.get("project", "Legal Checks RF"),
        "rules_of_use": sources_payload.get("rules_of_use", []),
        "sources": sources_payload.get("sources", []),
    }
    return render(request, "portal/sources.html", context)


def sources_api(request):
    return JsonResponse(get_sources_payload())
