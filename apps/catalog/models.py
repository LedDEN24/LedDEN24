from django.db import models
from django.core.files.base import ContentFile
from django.utils.text import slugify
import requests

class Category(models.Model):
    name = models.CharField(max_length=120)
    slug = models.SlugField(unique=True)

    # Внешний вид каталога
    icon = models.CharField(max_length=8, blank=True, default="")  # эмодзи
    image = models.ImageField(upload_to="categories/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order", "name"]

    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category, on_delete=models.PROTECT, related_name="products")
    title = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    price = models.PositiveIntegerField(default=0)

    # Можно хранить и локальную картинку, и URL (для импорта)
    image = models.ImageField(upload_to="products/", blank=True, null=True)
    image_url = models.URLField(blank=True, default="")

    description = models.TextField(blank=True, default="")
    is_active = models.BooleanField(default=True)

    # Маркеры для витрины
    is_hit = models.BooleanField("Хит", default=False, db_index=True)
    is_new = models.BooleanField("Новый", default=False, db_index=True)

    in_stock = models.BooleanField(default=True)
    quantity = models.PositiveIntegerField(default=9999)  # простой склад

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title

    def download_image_from_url(self, url: str):
        if not url:
            return
        r = requests.get(url, timeout=30)
        r.raise_for_status()
        fname = slugify(self.slug) or "product"
        # try ext
        ext = "jpg"
        ct = r.headers.get("content-type","")
        if "png" in ct:
            ext = "png"
        elif "webp" in ct:
            ext = "webp"
        self.image.save(f"{fname}.{ext}", ContentFile(r.content), save=True)


class ProductImage(models.Model):
    """Дополнительные фото товара (4–6 и больше)."""
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/gallery/", blank=True, null=True)
    image_url = models.URLField(blank=True, default="")
    sort = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ["sort", "id"]

    def __str__(self):
        return f"{self.product.title} фото #{self.pk}"
