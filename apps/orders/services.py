from apps.catalog.models import Product
from .models import Lead
from .notifications import notify_admins

def create_lead_from_site(name: str, phone: str, product_slug: str | None = None, comment: str = ""):
    product = None
    if product_slug:
        product = Product.objects.filter(slug=product_slug).first()
    lead = Lead.objects.create(source="site", name=name, phone=phone, product=product, comment=comment)

    # Уведомляем админов в Telegram напрямую через Bot API (requests)
    p_title = (product.title if product else "—")
    p_url = f"/product/{product.slug}/" if product else ""
    text = (
        "<b>💬 Новое сообщение с сайта</b>\n"
        f"Имя: <b>{lead.name or '—'}</b>\n"
        f"Телефон: <b>{lead.phone or '—'}</b>\n"
        f"Товар: <b>{p_title}</b> {p_url}\n"
        f"Комментарий: {lead.comment or '—'}"
    )
    notify_admins(text)
    return lead

def create_lead_from_tg(tg_user_id: str, name: str = "", phone: str = "", product_slug: str | None = None, comment: str = ""):
    product = None
    if product_slug:
        product = Product.objects.filter(slug=product_slug).first()
    return Lead.objects.create(source="tg", tg_user_id=tg_user_id, name=name, phone=phone, product=product, comment=comment)
