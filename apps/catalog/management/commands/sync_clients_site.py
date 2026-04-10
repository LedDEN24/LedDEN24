from __future__ import annotations

from django.core.management.base import BaseCommand
from django.db import transaction
from django.utils.text import slugify
from django.core.files.base import ContentFile

import requests

from apps.catalog.models import Category, Product, ProductImage
from apps.catalog.parsers.clients_site import parse_clients_site


class Command(BaseCommand):
    help = "Синхронизация каталога с atrium-art.clients.site (через Playwright)."

    def add_arguments(self, parser):
        parser.add_argument("--url", default="https://atrium-art.clients.site/", help="URL сайта clients.site")
        parser.add_argument("--headless", action="store_true", default=False,
                            help="Headless режим (по умолчанию False для отладки)")
        parser.add_argument("--clicks", type=int, default=20, help="Сколько раз нажимать 'Показать ещё'")
        parser.add_argument("--dry-run", action="store_true", default=False, help="Только показать, ничего не писать в БД")
        parser.add_argument("--reset-images", action="store_true", default=False, help="Пересоздавать ProductImage из парсинга")
        parser.add_argument("--download-images", action="store_true", default=False,
                            help="Скачивать изображения в MEDIA (а не хранить только URL)")
        parser.add_argument("--prices-only", action="store_true", default=False,
                            help="Обновить только цену/наличие (не трогать описания и фото)")

    def handle(self, *args, **opts):
        url = opts["url"]
        headless = opts["headless"]
        clicks = opts["clicks"]
        dry = opts["dry_run"]
        reset_images = opts["reset_images"]
        download_images = opts["download_images"]
        prices_only = opts["prices_only"]

        # В режиме prices-only не трогаем галерею даже если reset-images включили случайно
        if prices_only:
            reset_images = False

        if download_images and prices_only:
            self.stdout.write(self.style.WARNING("--download-images игнорируется в режиме --prices-only"))
            download_images = False

        def _guess_ext(url_: str, content_type: str = "") -> str:
            u = (url_ or "").lower()
            ct = (content_type or "").lower()
            if ".png" in u or "png" in ct:
                return "png"
            if ".webp" in u or "webp" in ct:
                return "webp"
            if ".jpeg" in u or ".jpg" in u or "jpeg" in ct or "jpg" in ct:
                return "jpg"
            return "jpg"

        def _download_bytes(img_url: str) -> tuple[bytes, str]:
            r = requests.get(img_url, timeout=30, headers={"User-Agent": "AtriumParser/1.0"})
            r.raise_for_status()
            ext = _guess_ext(img_url, r.headers.get("content-type", ""))
            return r.content, ext

        # ---- Категории: канонический маппинг под твой каталог ----
        CANON = {
            # Срезка
            "срезка": "srezka",
            "срезанные": "srezka",
            "cut": "srezka",
            "srezka": "srezka",

            # Букеты
            "букеты": "bukety",
            "букет": "bukety",
            "bouquets": "bukety",
            "bukety": "bukety",

            # Композиции
            "композиции": "kompozicii",
            "композиция": "kompozicii",
            "kompozicii": "kompozicii",

            # Цветы в коробке
            "цветы в коробке": "cvety-v-korobke",
            "в коробке": "cvety-v-korobke",
            "коробке": "cvety-v-korobke",
            "box": "cvety-v-korobke",
            "cvety-v-korobke": "cvety-v-korobke",
        }

        def _norm(s: str) -> str:
            return (s or "").strip().lower()

        self.stdout.write(self.style.NOTICE(f"Парсю: {url} (clicks={clicks}, headless={headless})"))
        items = parse_clients_site(url, show_more_clicks=clicks, headless=headless)
        self.stdout.write(self.style.SUCCESS(f"Найдено товаров: {len(items)}"))

        if dry:
            for p in items[:30]:
                self.stdout.write(f"- {p.slug} | {p.title} | {p.price} | {p.category_name or ''} | photos={len(p.images)}")
            return

        created = 0
        updated = 0
        images_written = 0
        errors = 0

        # ---- Гарантируем наличие 4 категорий + fallback ----
        cat_srezka, _ = Category.objects.get_or_create(
            slug="srezka", defaults={"name": "Срезка", "icon": "🌿", "order": 10}
        )
        cat_bukety, _ = Category.objects.get_or_create(
            slug="bukety", defaults={"name": "Букеты", "icon": "💐", "order": 20}
        )
        cat_komp, _ = Category.objects.get_or_create(
            slug="kompozicii", defaults={"name": "Композиции", "icon": "🌸", "order": 30}
        )
        cat_box, _ = Category.objects.get_or_create(
            slug="cvety-v-korobke", defaults={"name": "Цветы в коробке", "icon": "🎁", "order": 40}
        )
        fallback_cat, _ = Category.objects.get_or_create(
            slug="other", defaults={"name": "Прочее", "icon": "🧺", "order": 999}
        )

        slug_to_cat = {
            "srezka": cat_srezka,
            "bukety": cat_bukety,
            "kompozicii": cat_komp,
            "cvety-v-korobke": cat_box,
        }

        def resolve_category(p) -> Category:
            key = _norm(getattr(p, "category", "")) or _norm(getattr(p, "category_name", ""))
            key_slug = slugify(key) if key else ""
            canon_slug = CANON.get(key) or CANON.get(key_slug) or CANON.get(_norm(getattr(p, "category_name", "")))
            if canon_slug and canon_slug in slug_to_cat:
                return slug_to_cat[canon_slug]
            return fallback_cat

        def make_safe_slug(p) -> str:
            raw_slug = (getattr(p, "slug", "") or "").strip()
            if not raw_slug:
                raw_slug = (getattr(p, "title", "") or "").strip()
            raw_slug = raw_slug.replace("/", "-").replace("\\", "-")
            safe = slugify(raw_slug)[:120] or slugify(getattr(p, "title", "") or "")[:120] or "product"
            return safe

        for p in items:
            try:
                with transaction.atomic():
                    cat_obj = resolve_category(p)
                    safe_slug = make_safe_slug(p)

                    obj, was_created = Product.objects.get_or_create(
                        slug=safe_slug,
                        defaults={
                            "title": p.title,
                            "price": p.price or 0,
                            "image_url": p.image_url or "",
                            "category": cat_obj,
                            "description": p.description or "",
                            "is_active": True,
                            "in_stock": True if p.in_stock is None else bool(p.in_stock),
                            "quantity": p.quantity or 9999,
                        },
                    )

                    if was_created:
                        created += 1
                    else:
                        changed_fields: list[str] = []
                        if prices_only:
                            fields = {
                                "price": p.price if p.price is not None else obj.price,
                                "in_stock": obj.in_stock if p.in_stock is None else bool(p.in_stock),
                                "quantity": obj.quantity if p.quantity is None else int(p.quantity),
                                "is_active": True,
                            }
                        else:
                            fields = {
                                "title": p.title,
                                "price": p.price if p.price is not None else obj.price,
                                "image_url": p.image_url or obj.image_url,
                                "category": cat_obj,
                                "description": p.description or obj.description,
                                "is_active": True,
                                "in_stock": obj.in_stock if p.in_stock is None else bool(p.in_stock),
                                "quantity": obj.quantity if p.quantity is None else int(p.quantity),
                            }

                        for field, value in fields.items():
                            if value is not None and getattr(obj, field) != value:
                                setattr(obj, field, value)
                                changed_fields.append(field)

                        if changed_fields:
                            obj.save(update_fields=changed_fields)
                            updated += 1

                    # При необходимости скачиваем главное фото
                    if download_images and (p.image_url or ""):
                        if not obj.image:
                            try:
                                content, ext = _download_bytes(p.image_url)
                                fname = f"{slugify(obj.slug) or 'product'}.{ext}"
                                obj.image.save(fname, ContentFile(content), save=True)
                            except Exception as e:
                                self.stdout.write(self.style.WARNING(f"Не смог скачать image для {obj.slug}: {e}"))

                    # Save gallery images as ProductImage (URLs or downloaded)
                    if reset_images:
                        ProductImage.objects.filter(product=obj).delete()
                        extras = (p.images or [])[1:13]
                        for idx, u in enumerate(extras):
                            if not u:
                                continue
                            if download_images:
                                try:
                                    content, ext = _download_bytes(u)
                                    fname = f"{slugify(obj.slug) or 'product'}-{idx + 1}.{ext}"
                                    pi = ProductImage.objects.create(product=obj, sort=idx, image_url=u)
                                    pi.image.save(fname, ContentFile(content), save=True)
                                except Exception as e:
                                    self.stdout.write(self.style.WARNING(f"Не смог скачать gallery image для {obj.slug}: {e}"))
                                    ProductImage.objects.create(product=obj, sort=idx, image_url=u)
                                images_written += 1
                            else:
                                ProductImage.objects.create(product=obj, sort=idx, image_url=u)
                                images_written += 1

            except Exception as e:
                errors += 1
                self.stdout.write(self.style.ERROR(f"ОШИБКА на товаре slug={getattr(p,'slug',None)} title={getattr(p,'title',None)}: {e}"))
                continue

        self.stdout.write(self.style.SUCCESS(
            f"Готово. Создано: {created}, обновлено: {updated}, ошибок: {errors}, фото (ProductImage): {images_written}"
        ))
