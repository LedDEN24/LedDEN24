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
    context = {
        **_base_context(),
        "project": sources_payload.get("project", "Legal Checks RF"),
        "version": sources_payload.get("version", ""),
        "updated_at": sources_payload.get("updated_at", ""),
        "rules_of_use": sources_payload.get("rules_of_use", []),
        "sources_preview": sources_payload.get("sources", [])[:3],
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
