import re

_BG_RE = re.compile(r"background-image\s*:\s*url\((.*?)\)", re.IGNORECASE)


def extract_bg_url(style: str) -> str:
    if not style:
        return ""
    m = _BG_RE.search(style)
    if not m:
        return ""
    return m.group(1).strip().strip('"').strip("'")


def extract_img_urls(img_tag) -> list[str]:
    urls: list[str] = []

    src = img_tag.get("src")
    if src:
        urls.append(src.strip())

    srcset = img_tag.get("srcset") or ""
    for part in srcset.split(","):
        part = part.strip()
        if not part:
            continue
        url = part.split()[0].strip()
        if url:
            urls.append(url)

    # unique preserving order
    seen = set()
    out = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out


def collect_images(soup) -> list[str]:
    images: list[str] = []

    # item page
    for img in soup.select('img[data-name="item-image"], img.service-item-page-exp__image'):
        images.extend(extract_img_urls(img))
    for div in soup.select('.service-item-page-exp__image-background[style]'):
        bg = extract_bg_url(div.get('style', ''))
        if bg:
            images.append(bg)

    # filled card
    for img in soup.select('img[data-name="services-item-filled-image"]'):
        images.extend(extract_img_urls(img))
    for div in soup.select('.services-item-filled__photo-background[style]'):
        bg = extract_bg_url(div.get('style', ''))
        if bg:
            images.append(bg)

    # unique
    seen = set()
    out = []
    for u in images:
        if u not in seen:
            seen.add(u)
            out.append(u)
    return out
