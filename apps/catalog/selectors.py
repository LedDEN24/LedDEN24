from django.core.paginator import Paginator
from .models import Product

def product_list(category_slug: str = "all", page: int = 1, per_page: int = 12):
    qs = Product.objects.filter(is_active=True).select_related("category").order_by("-created_at")
    if category_slug and category_slug != "all":
        qs = qs.filter(category__slug=category_slug)
    paginator = Paginator(qs, per_page)
    return paginator.get_page(page)
