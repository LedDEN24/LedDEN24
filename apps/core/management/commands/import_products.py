import json
from pathlib import Path
from django.core.management.base import BaseCommand, CommandError
from django.utils.text import slugify
from apps.catalog.models import Category, Product
import requests

class Command(BaseCommand):
    help = "Импортирует товары из JSON. Опционально скачивает изображения по image_url."

    def add_arguments(self, parser):
        parser.add_argument("json_path", type=str, help="Путь к products.json")
        parser.add_argument("--download-images", action="store_true", help="Скачать картинки в MEDIA/products/")
        parser.add_argument("--limit", type=int, default=0, help="Лимит товаров (0 = без лимита)")

    def handle(self, *args, **opts):
        p = Path(opts["json_path"])
        if not p.exists():
            raise CommandError(f"Файл не найден: {p}")

        data = json.loads(p.read_text(encoding="utf-8"))
        if not isinstance(data, list):
            raise CommandError("Ожидается JSON-массив объектов")

        if opts["limit"] and opts["limit"] > 0:
            data = data[:opts["limit"]]

        created = 0
        updated = 0

        for item in data:
            cat_slug = (item.get("category") or "all").strip() or "all"
            cat_name = item.get("category_name") or cat_slug
            category, _ = Category.objects.get_or_create(slug=cat_slug, defaults={"name": cat_name})

            title = item.get("title") or "Без названия"
            slug = item.get("slug") or slugify(title)
            price = int(item.get("price") or 0)
            description = item.get("description") or ""
            image_url = item.get("image_url") or ""

            obj, is_created = Product.objects.update_or_create(
                slug=slug,
                defaults={
                    "category": category,
                    "title": title,
                    "price": price,
                    "description": description,
                    "image_url": image_url,
                    "is_active": True,
                }
            )
            if is_created:
                created += 1
            else:
                updated += 1

            if opts["download_images"] and image_url:
                try:
                    obj.download_image_from_url(image_url)
                except Exception as e:
                    self.stderr.write(self.style.WARNING(f"Не удалось скачать картинку для {obj.slug}: {e}"))

        self.stdout.write(self.style.SUCCESS(f"Готово. Создано: {created}, обновлено: {updated}"))
