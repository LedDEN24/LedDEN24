import urllib.parse
from playwright.sync_api import sync_playwright


def _abs(base: str, href: str) -> str:
    return urllib.parse.urljoin(base, href)


def parse_catalog_item_links_playwright(page_url: str) -> list[str]:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(page_url, wait_until="networkidle", timeout=60000)

        # скролл к секции (если есть)
        try:
            page.locator("#services").scroll_into_view_if_needed(timeout=5000)
        except Exception:
            pass

        page.wait_for_selector('a[href*="/service/"]', timeout=30000)
        hrefs = page.eval_on_selector_all(
            'a[href*="/service/"]',
            "els => els.map(e => e.getAttribute('href')).filter(Boolean)"
        )
        browser.close()

    base = page_url.split("#", 1)[0]
    links = [_abs(base, h) for h in hrefs]

    seen, out = set(), []
    for u in links:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out
