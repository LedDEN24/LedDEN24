from .models import Category, Product

def categories():
    return Category.objects.all().order_by("name")

def get_product_by_slug(slug: str):
    return Product.objects.filter(slug=slug, is_active=True).first()
