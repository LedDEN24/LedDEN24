import re
import time
from dataclasses import dataclass
from typing import Optional

from playwright.sync_api import sync_playwright, TimeoutError as PWTimeoutError
from apps.catalog.parsers.clients_site_parts.item_page import parse_item_page


@dataclass
class ParsedProduct:
    title: str
    slug: str
    price: Optional[int]
    image_url: Optional[str]           # главное фото
    images: list[str]                  # все фото (включая главное, первым)
    category: Optional[str]            # slug категории
    category_name: Optional[str]       # имя категории
    description: Optional[str]
    in_stock: Optional[bool]
    quantity: Optional[int]
    detail_url: str


def _clean_price(text: str) -> Optional[int]:
    if not text:
        return None
    digits = re.sub(r"[^\d]", "", text)
    return int(digits) if digits else None


def _slug_from_url(url: str) -> str:
    m = re.search(r"/service/(.+)$", url)
    if m:
        return m.group(1).strip("/")
    return url.rstrip("/").split("/")[-1]


def _abs_url(base_url: str, href: str) -> str:
    if href.startswith("/"):
        return base_url.rstrip("/") + href
    if href.startswith("http"):
        return href
    return base_url.rstrip("/") + "/" + href.lstrip("/")


def _looks_like_photo(url: str) -> bool:
    if not url:
        return False
    u = url.lower()
    if "svg" in u:
        return False
    if any(x in u for x in ["icon", "logo", "sprite", "favicon"]):
        return False
    if re.search(r"\.(jpg|jpeg|png|webp)(\?|$)", u):
        return True
    # CDN-URL without ext (yandex avatars) — keep if contains get- and seems image-ish
    if "avatars" in u or "mds.yandex" in u or "/get-" in u:
        return True
    return False


def _collect_gallery_images(page) -> list[str]:
    # Собираем все img.src на странице товара и фильтруем на "похоже на фото"
    srcs = []
    try:
        imgs = page.locator("img")
        n = imgs.count()
        for i in range(n):
            try:
                src = imgs.nth(i).get_attribute("src") or imgs.nth(i).get_attribute("data-src") or ""
                src = (src or "").strip()
                if _looks_like_photo(src):
                    srcs.append(src)
            except Exception:
                continue
    except Exception:
        pass
    # уникализируем, сохраняя порядок
    out = []
    for s in srcs:
        if s and s not in out:
            out.append(s)
    return out


def _find_filter_buttons(page):
    """Пытаемся найти кнопки фильтров категорий на главной (best effort)."""
    # Часто это кнопки/ссылки с data-cat
    candidates = []
    for sel in ["[data-cat]", ".filters button", ".filters a", "button:has-text('Все')"]:
        try:
            loc = page.locator(sel)
            if loc.count() > 0:
                candidates.append(loc)
        except Exception:
            continue

    # берем самый "богатый" набор
    best = None
    best_n = 0
    for loc in candidates:
        try:
            n = loc.count()
            if n > best_n:
                best_n = n
                best = loc
        except Exception:
            continue
    return best


def parse_clients_site(
    base_url: str,
    show_more_clicks: int = 20,
    headless: bool = True,
    slow_mo_ms: int = 0,
) -> list[ParsedProduct]:
    """Best-effort парсер clients.site через Playwright + категории из фильтров + фото-галерея."""
    products: dict[str, ParsedProduct] = {}

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=headless, slow_mo=slow_mo_ms)
        page = browser.new_page(viewport={"width": 1280, "height": 800})
        page.goto(base_url, wait_until="domcontentloaded", timeout=60_000)

        # Scroll to catalog if possible
        try:
            page.get_by_text("Каталог", exact=True).first.scroll_into_view_if_needed(timeout=5_000)
        except Exception:
            pass

        filter_loc = _find_filter_buttons(page)
        filters = []  # list of dict {key, name}
        if filter_loc:
            for i in range(filter_loc.count()):
                try:
                    btn = filter_loc.nth(i)
                    name = (btn.inner_text(timeout=500) or "").strip()
                    if not name or len(name) > 60:
                        continue
                    # data-cat or fallback slugify-ish
                    key = (btn.get_attribute("data-cat") or "").strip()
                    if not key:
                        key = re.sub(r"\s+", "-", name.lower())
                        key = re.sub(r"[^a-z0-9\-а-яё]", "", key)
                    # normalize "all"
                    if name.lower() in ["все", "all"] or key.lower() in ["all", "все"]:
                        key = "all"
                        name = "Все"
                    if not any(f["key"] == key for f in filters):
                        filters.append({"key": key, "name": name, "locator_index": i})
                except Exception:
                    continue

        # If no filters found, fall back to single pass
        if not filters:
            filters = [{"key": "all", "name": "Все", "locator_index": None}]

        def expand_catalog():
            # Click 'Показать ещё' (if present)
            for _ in range(show_more_clicks):
                try:
                    btn = page.get_by_role("button", name=re.compile(r"Показать ещё", re.I)).first
                    if btn and btn.is_visible():
                        btn.click()
                        page.wait_for_timeout(400)
                    else:
                        break
                except Exception:
                    break

        def collect_cards(category_key: str, category_name: str):
            anchors = page.locator("a[href*='/service/']")
            count = anchors.count()
            for i in range(count):
                try:
                    a = anchors.nth(i)
                    href = a.get_attribute("href") or ""
                    if "/service/" not in href:
                        continue
                    detail_url = _abs_url(base_url, href)
                    slug = _slug_from_url(detail_url)

                    card = a.locator("xpath=ancestor::*[self::li or self::div][1]")

                    img_url = None
                    try:
                        img = card.locator("img").first
                        img_url = img.get_attribute("src") or img.get_attribute("data-src")
                    except Exception:
                        pass

                    title = None
                    for sel in ["h3", "h2", "div[class*='title']", "span[class*='title']"]:
                        try:
                            t = card.locator(sel).first.inner_text(timeout=500)
                            if t and len(t.strip()) >= 2:
                                title = t.strip()
                                break
                        except Exception:
                            continue
                    if not title:
                        try:
                            title = a.inner_text(timeout=500).strip()
                        except Exception:
                            title = slug

                    price = None
                    try:
                        price_txt = card.locator("text=/₽|руб/i").first.inner_text(timeout=500)
                        price = _clean_price(price_txt)
                    except Exception:
                        try:
                            price_txt = card.locator("[class*='price']").first.inner_text(timeout=500)
                            price = _clean_price(price_txt)
                        except Exception:
                            price = None

                    if slug not in products:
                        products[slug] = ParsedProduct(
                            title=title,
                            slug=slug,
                            price=price,
                            image_url=img_url,
                            images=[img_url] if img_url else [],
                            category=category_key if category_key != "all" else None,
                            category_name=category_name if category_key != "all" else None,
                            description=None,
                            in_stock=None,
                            quantity=None,
                            detail_url=detail_url,
                        )
                    else:
                        # if already exists but no category set, fill it
                        pr = products[slug]
                        if not pr.category and category_key != "all":
                            pr.category = category_key
                            pr.category_name = category_name
                            products[slug] = pr
                except Exception:
                    continue

        # Iterate categories (click filter -> expand -> collect)
        for f in filters:
            try:
                if f["key"] != "all" and filter_loc and f["locator_index"] is not None:
                    btn = filter_loc.nth(f["locator_index"])
                    if btn.is_visible():
                        btn.click()
                        page.wait_for_timeout(500)
                elif f["key"] == "all" and filter_loc and f["locator_index"] is not None:
                    btn = filter_loc.nth(f["locator_index"])
                    if btn.is_visible():
                        btn.click()
                        page.wait_for_timeout(400)
            except Exception:
                pass

            try:
                page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                page.wait_for_timeout(250)
            except Exception:
                pass

            expand_catalog()
            collect_cards(f["key"], f["name"])

        # Detail pages: точные данные со страницы товара (requests+bs4) + резервный сбор фото через Playwright
        for slug, pr in list(products.items()):
            # 1) Пытаемся спарсить страницу товара без браузера (быстрее и стабильнее)
            try:
                data = parse_item_page(pr.detail_url)
                if data.get('title'):
                    pr.title = data['title']
                if data.get('price'):
                    pr.price = data['price']
                if data.get('composition'):
                    pr.description = data['composition']
                if 'in_stock' in data:
                    pr.in_stock = bool(data['in_stock'])
                imgs = [u for u in (data.get('images') or []) if u]
                if pr.image_url and pr.image_url not in imgs:
                    imgs.insert(0, pr.image_url)
                if imgs:
                    pr.image_url = imgs[0]
                    pr.images = imgs
                products[slug] = pr
                time.sleep(0.06)
                continue
            except Exception:
                pass

            # 2) Если requests-парсинг не сработал — пробуем через Playwright (best effort)
            try:
                page.goto(pr.detail_url, wait_until='domcontentloaded', timeout=60_000)

                imgs = _collect_gallery_images(page)
                if pr.image_url and pr.image_url not in imgs:
                    imgs.insert(0, pr.image_url)
                if imgs:
                    pr.image_url = imgs[0]
                    pr.images = imgs

                # Description (fallback)
                desc = None
                try:
                    h = page.get_by_text(re.compile(r'Описание', re.I)).first
                    h.scroll_into_view_if_needed(timeout=3_000)
                    desc_el = h.locator('xpath=following::*[self::p or self::div][1]')
                    txt = desc_el.inner_text(timeout=2_000).strip()
                    if txt:
                        desc = txt
                except Exception:
                    pass

                if desc:
                    pr.description = desc
                    products[slug] = pr
                time.sleep(0.12)
            except PWTimeoutError:
                continue
            except Exception:
                continue

        browser.close()

    return list(products.values())
