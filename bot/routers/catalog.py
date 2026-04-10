from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from bot.keyboards.inline import categories_kb, product_kb
import os
from bot.db import list_products, list_hits, list_news

router = Router()

@router.message(F.text.lower() == "каталог")
async def catalog(m: Message):
    await m.answer("Выберите категорию:", reply_markup=await categories_kb())


def _product_text(p) -> str:
    badges = []
    if getattr(p, "is_hit", False):
        badges.append("🔥 Хит")
    if getattr(p, "is_new", False):
        badges.append("🆕 Новый")
    badge_line = (" ".join(badges) + "\n") if badges else ""
    desc = (p.description or "").strip()
    if len(desc) > 350:
        desc = desc[:350] + "…"
    return f"{badge_line}**{p.title}**\nЦена: {p.price} ₽\n\n{desc or '—'}"


@router.message(F.text == "🔥 Хиты")
async def hits(m: Message):
    items = await list_hits(limit=10)
    if not items:
        return await m.answer("Пока нет товаров в разделе 🔥 Хиты.")
    for p in items:
        await m.answer(_product_text(p), reply_markup=product_kb(p.slug), parse_mode="Markdown")


@router.message(F.text == "🆕 Новинки")
async def news(m: Message):
    items = await list_news(limit=10)
    if not items:
        return await m.answer("Пока нет товаров в разделе 🆕 Новинки.")
    for p in items:
        await m.answer(_product_text(p), reply_markup=product_kb(p.slug), parse_mode="Markdown")

@router.callback_query(F.data.startswith("cat:"))
async def cat_pick(c: CallbackQuery):
    cat = c.data.split(":",1)[1]
    items = await list_products(cat, limit=10)
    if not items:
        await c.message.answer("В этой категории пока нет товаров.")
        await c.answer()
        return

    for p in items:
        await c.message.answer(_product_text(p), reply_markup=product_kb(p.slug), parse_mode="Markdown")
    await c.answer()
