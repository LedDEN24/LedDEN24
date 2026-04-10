import html as html_lib
import re
import requests
from bs4 import BeautifulSoup

from .images import collect_images


def parse_price(text: str) -> int:
    digits = re.sub(r"[^\d]", "", text or "")
    return int(digits) if digits else 0


def normalize_multiline(text: str) -> str:
    lines = [html_lib.unescape(x).strip() for x in (text or "").splitlines()]
    lines = [x for x in lines if x]
    return "\n".join(lines)


def parse_title_from_meta(soup: BeautifulSoup) -> str:
    meta = soup.select_one('meta[name="description"]')
    if not meta or not meta.get("content"):
        return ""
    content = html_lib.unescape(meta["content"]).strip()
    parts = content.split(" - ", 2)
    return parts[0].strip() if parts else ""


def parse_item_page(url: str) -> dict:
    r = requests.get(url, timeout=30, headers={"User-Agent": "AtriumParser/1.0"})
    r.raise_for_status()
    soup = BeautifulSoup(r.text, "html.parser")

    # Текст страницы целиком (для эвристик наличия)
    page_text = soup.get_text(" ", strip=True).lower()

    # 1) цена (точный селектор)
    price_el = soup.select_one('div.service-item-page-exp__price[data-name="info-price"]')
    price = parse_price(price_el.get_text(" ", strip=True) if price_el else "")

    # 2) название (meta fallback + alt)
    title = parse_title_from_meta(soup)
    if not title:
        img = soup.select_one('img[data-name="item-image"], img[data-name="services-item-filled-image"]')
        title = (img.get("alt") or "").strip() if img else ""

    # 3) состав (точный селектор)
    comp_el = soup.select_one('div.service-item-page-exp__description-inner[data-name="item-description-inner"]')
    composition = normalize_multiline(comp_el.get_text("\n", strip=True) if comp_el else "")

    # 4) картинки
    images = collect_images(soup)

    # 5) наличие (best effort)
    # На clients.site обычно нет явного "склада", поэтому используем текстовые признаки.
    # Если на странице встречается "нет в наличии"/"закончился"/"распродано" — считаем, что товара нет.
    out_markers = [
        "нет в наличии",
        "не в наличии",
        "распродано",
        "законч",
        "временно нет",
        "недоступ",
    ]
    in_stock = not any(m in page_text for m in out_markers)

    return {
        "price": price,
        "title": title,
        "composition": composition,
        "images": images,
        "in_stock": in_stock,
    }
