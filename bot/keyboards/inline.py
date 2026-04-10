from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from asgiref.sync import sync_to_async

from apps.catalog.models import Category, Product


@sync_to_async
def _list_categories(limit: int = 30):
    return list(Category.objects.order_by("order", "name")[: int(limit)])


async def categories_kb():
    rows = [[InlineKeyboardButton(text="Все", callback_data="cat:all")]]
    for c in await _list_categories(30):
        icon = (c.icon or "").strip()
        text = f"{icon} {c.name}".strip()
        rows.append([InlineKeyboardButton(text=text, callback_data=f"cat:{c.slug}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def product_kb(slug: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Заказать", callback_data=f"order:{slug}")],
    ])



@sync_to_async
def _products_page(page: int, per_page: int):
    qs = Product.objects.filter(is_active=True).order_by("-created_at")
    total = qs.count()
    start = (page - 1) * per_page
    items = list(qs[start : start + per_page])
    return total, items


async def products_kb(page: int = 1, per_page: int = 10):
    page = max(int(page or 1), 1)
    total, items = await _products_page(page, per_page)
    start = (page - 1) * per_page

    rows = []
    for p in items:
        rows.append([InlineKeyboardButton(text=p.title[:40], callback_data=f"upl_pick:{p.slug}")])

    nav = []
    if start > 0:
        nav.append(InlineKeyboardButton(text="←", callback_data=f"upl_page:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page}", callback_data="noop"))
    if start + per_page < total:
        nav.append(InlineKeyboardButton(text="→", callback_data=f"upl_page:{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="Отмена", callback_data="upl_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


async def upload_categories_kb():
    rows = []
    # "Все"
    rows.append([InlineKeyboardButton(text="Все товары", callback_data="upl_cat:all")])
    for c in await _list_categories(50):
        icon = (c.icon or "").strip()
        text = f"{icon} {c.name}".strip()[:40]
        rows.append([InlineKeyboardButton(text=text, callback_data=f"upl_cat:{c.slug}")])
    rows.append([InlineKeyboardButton(text="Отмена", callback_data="upl_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)


@sync_to_async
def _products_by_category_page(category_slug: str, page: int, per_page: int):
    qs = Product.objects.filter(is_active=True).order_by("-created_at")
    if category_slug != "all":
        qs = qs.filter(category__slug=category_slug)
    total = qs.count()
    start = (page - 1) * per_page
    items = list(qs[start : start + per_page])
    return total, items


async def products_by_category_kb(category_slug: str, page: int = 1, per_page: int = 10):
    page = max(int(page or 1), 1)
    total, items = await _products_by_category_page(category_slug, page, per_page)
    start = (page - 1) * per_page

    rows = []
    for p in items:
        rows.append([InlineKeyboardButton(text=p.title[:40], callback_data=f"upl_pick:{p.slug}")])

    nav = []
    if start > 0:
        nav.append(InlineKeyboardButton(text="←", callback_data=f"upl_pcat:{category_slug}:{page-1}"))
    nav.append(InlineKeyboardButton(text=f"{page}", callback_data="noop"))
    if start + per_page < total:
        nav.append(InlineKeyboardButton(text="→", callback_data=f"upl_pcat:{category_slug}:{page+1}"))
    if nav:
        rows.append(nav)

    rows.append([InlineKeyboardButton(text="← Категории", callback_data="upl_back_cats")])
    rows.append([InlineKeyboardButton(text="Отмена", callback_data="upl_cancel")])
    return InlineKeyboardMarkup(inline_keyboard=rows)



def upload_manage_kb(product_slug: str, last_image_id: int | None = None):
    rows = []
    rows.append([InlineKeyboardButton(text="Загрузить 1 фото главным", callback_data=f"upl_upload_main:{product_slug}")])
    if last_image_id:
        rows.append([InlineKeyboardButton(text="Сделать последнее фото главным", callback_data=f"upl_make_main:{last_image_id}")])
    rows.append([InlineKeyboardButton(text="Удалить последнее фото", callback_data=f"upl_del_last:{product_slug}")])
    rows.append([InlineKeyboardButton(text="Очистить все фото товара", callback_data=f"upl_clear_ask:{product_slug}")])
    rows.append([InlineKeyboardButton(text="Выгрузить фото ZIP", callback_data=f"upl_export_zip:{product_slug}")])
    return InlineKeyboardMarkup(inline_keyboard=rows)

def upload_clear_confirm_kb(product_slug: str):
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Да, очистить", callback_data=f"upl_clear_yes:{product_slug}")],
        [InlineKeyboardButton(text="Отмена", callback_data="upl_clear_no")],
    ])


def admin_menu_kb():
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="Синхронизировать каталог", callback_data="admin_sync")],
        [InlineKeyboardButton(text="Закрыть", callback_data="admin_close")],
    ])


def order_admin_kb(order_id: int):
    oid = int(order_id)
    return InlineKeyboardMarkup(inline_keyboard=[
        [
            InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"ordset:{oid}:confirmed"),
            InlineKeyboardButton(text="🌿 Сборка", callback_data=f"ordset:{oid}:assembling"),
        ],
        [
            InlineKeyboardButton(text="🚚 В пути", callback_data=f"ordset:{oid}:delivering"),
            InlineKeyboardButton(text="📦 Доставлен", callback_data=f"ordset:{oid}:delivered"),
        ],
        [InlineKeyboardButton(text="❌ Отменён", callback_data=f"ordset:{oid}:canceled")],
    ])
