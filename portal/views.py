from django.contrib import messages
from django.http import Http404, JsonResponse
from django.shortcuts import redirect, render
from django.urls import reverse

from .content import get_document, get_document_sections, get_sources_payload
from .forms import DemoRequestForm
from .marketing import (
    CONTACT_DETAILS,
    DEMO_BENEFITS,
    HERO_INTERFACE_MOCKUPS,
    LEGAL_PAGES,
    PRICING_PLANS,
    TRUST_MARKERS,
)


def _marketing_context() -> dict[str, object]:
    return {
        "pricing_plans": PRICING_PLANS,
        "contact_details": CONTACT_DETAILS,
        "legal_pages": LEGAL_PAGES,
        "demo_benefits": DEMO_BENEFITS,
        "trust_markers": TRUST_MARKERS,
        "hero_interface_mockups": HERO_INTERFACE_MOCKUPS,
    }


def _base_context() -> dict[str, object]:
    sources_payload = get_sources_payload()
    return {
        "document_sections": get_document_sections(),
        "sources_count": len(sources_payload.get("sources", [])),
        **_marketing_context(),
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
        "demo_form": DemoRequestForm(),
    }
    return render(request, "portal/home.html", context)


def demo_request(request):
    success = request.GET.get("submitted") == "1"
    form = DemoRequestForm(request.POST or None)

    if request.method == "POST" and form.is_valid():
        form.save()
        messages.success(
            request,
            "Заявка принята. Демо-запрос сохранен, можно продолжать дорабатывать CRM или email-обработку позже.",
        )
        return redirect(f"{reverse('portal:demo-request')}?submitted=1")

    context = {
        **_base_context(),
        "form": form,
        "submitted": success,
    }
    return render(request, "portal/marketing/demo_request.html", context)


def tariffs(request):
    context = {
        **_base_context(),
    }
    return render(request, "portal/marketing/tariffs.html", context)


def privacy_policy(request):
    context = {
        **_base_context(),
        "page": LEGAL_PAGES["privacy"],
    }
    return render(request, "portal/marketing/privacy.html", context)


def personal_data_consent(request):
    context = {
        **_base_context(),
        "page": LEGAL_PAGES["consent"],
    }
    return render(request, "portal/marketing/personal_data_consent.html", context)


def contacts(request):
    context = {
        **_base_context(),
    }
    return render(request, "portal/marketing/contacts.html", context)


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
