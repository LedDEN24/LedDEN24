from django.contrib import messages
from django.db.models import Count, Q
from django.http import JsonResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST, require_GET
from apps.content.models import Review
from apps.orders.services import create_lead_from_site
from apps.orders.tracking import track_event, get_or_create_cart_session
from .selectors import product_list
from .models import Category, Product


def _catalog_categories():
    categories = Category.objects.annotate(
        active_products_count=Count("products", filter=Q(products__is_active=True), distinct=True)
    ).order_by("order", "name")
    active_categories = categories.filter(active_products_count__gt=0)
    return active_categories if active_categories.exists() else categories


def index(request):
    get_or_create_cart_session(request)
    cat = request.GET.get("cat", "all")
    page_num = request.GET.get("page", 1)
    page = product_list(cat, page=page_num, per_page=12)
    categories = _catalog_categories()
    products = Product.objects.filter(is_active=True).select_related("category")
    page_items = list(page.object_list)

    hits = list(products.filter(is_hit=True).order_by("-created_at")[:4])
    news = list(
        products.filter(is_new=True)
        .exclude(pk__in=[p.pk for p in hits])
        .order_by("-created_at")[:4]
    )
    hero_product = hits[0] if hits else (page_items[0] if page_items else None)

    ctx = {
        "categories": categories,
        "page": page,
        "selected_cat": cat,
        "hits": hits,
        "news": news,
        "reviews": Review.objects.order_by("-created_at")[:6],
        "total_products": products.count(),
        "hero_product": hero_product,
    }
    return render(request, "catalog/index.html", ctx)


def _norm_q(q: str) -> str:
    return (q or "").strip()


@require_GET
def search_api(request):
    """Live-поиск (подсказки) как в маркетплейсе."""
    q = _norm_q(request.GET.get("q", ""))
    try:
        limit = int(request.GET.get("limit", 8))
    except Exception:
        limit = 8

    if len(q) < 2:
        return JsonResponse({"q": q, "items": []})

    qs = (
        Product.objects
        .filter(is_active=True)
        .filter(Q(title__icontains=q) | Q(description__icontains=q))
        .select_related("category")
        .order_by("-is_hit", "-is_new", "title")[: max(1, min(limit, 20))]
    )

    items = []
    for p in qs:
        img = ""
        if getattr(p, "image", None):
            try:
                img = p.image.url
            except Exception:
                img = ""
        if not img:
            img = p.image_url or ""

        items.append({
            "id": p.id,
            "slug": p.slug,
            "title": p.title,
            "price": int(p.price),
            "in_stock": bool(getattr(p, "in_stock", True)),
            "category": p.category.name if p.category_id else "",
            "url": f"/product/{p.slug}/",
            "img": img,
            "is_hit": bool(getattr(p, "is_hit", False)),
            "is_new": bool(getattr(p, "is_new", False)),
        })

    return JsonResponse({"q": q, "items": items})


@require_GET
def search_page(request):
    """Страница результатов поиска."""
    q = _norm_q(request.GET.get("q", ""))
    products = Product.objects.none()
    if len(q) >= 2:
        products = (
            Product.objects
            .filter(is_active=True)
            .filter(Q(title__icontains=q) | Q(description__icontains=q))
            .select_related("category")
            .order_by("-is_hit", "-is_new", "title")
        )
    return render(request, "catalog/search.html", {"q": q, "products": products})

def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    track_event(request, event_type="product_view", product=product)
    related_products = (
        Product.objects.filter(is_active=True, category=product.category)
        .exclude(pk=product.pk)
        .order_by("-is_hit", "-is_new", "-created_at")[:4]
    )
    return render(
        request,
        "catalog/product_detail.html",
        {
            "product": product,
            "related_products": related_products,
        },
    )


def contact(request):
    """Страница контактов + форма 'Написать админу'."""
    if request.method == "POST":
        name = request.POST.get("name", "").strip()
        phone = request.POST.get("phone", "").strip()
        comment = request.POST.get("comment", "").strip()
        create_lead_from_site(name=name, phone=phone, product_slug=None, comment=comment)
        messages.success(request, "Спасибо! Мы получили сообщение и скоро свяжемся с вами.")
        return redirect("contact")

    return render(request, "catalog/contact.html")

@require_POST
def lead_create(request):
    # простая форма заявки с сайта
    name = request.POST.get("name","").strip()
    phone = request.POST.get("phone","").strip()
    product_slug = request.POST.get("product_slug","").strip() or None
    comment = request.POST.get("comment","").strip()
    create_lead_from_site(name=name, phone=phone, product_slug=product_slug, comment=comment)
    messages.success(request, "Заявка отправлена. Мы свяжемся с вами в ближайшее время.")
    return redirect("index")
