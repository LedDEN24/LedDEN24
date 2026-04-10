from aiogram import Router, F

router = Router()

import asyncio
from aiogram.filters import Command
from aiogram.types import Message
from bot.config import is_admin
from bot.db import set_order_status


@router.message(Command("sync_site"))
async def sync_site(m: Message):
    if not is_admin(m.from_user.id):
        await m.answer("Нет доступа.")
        return
    await m.answer("Стартую синхронизацию каталога…")
    proc = await asyncio.create_subprocess_exec(
        "python", "manage.py", "sync_clients_site",
        "--url", "https://atrium-art.clients.site/",
        "--headless", "--clicks", "30",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    out, _ = await proc.communicate()
    text = (out or b"").decode("utf-8", errors="ignore")
    tail = text[-3500:] if len(text) > 3500 else text
    await m.answer("Готово ✅\n\n" + (tail or "(нет вывода)"))

from bot.keyboards.inline import admin_menu_kb

from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery
from bot.config import is_admin
import asyncio

@router.message(Command("admin"))
async def admin_menu(m: Message):
    if not is_admin(m.from_user.id):
        await m.answer("Нет доступа.")
        return
    await m.answer("Админ-меню:", reply_markup=admin_menu_kb())

@router.callback_query(F.data == "admin_close")
async def admin_close(c: CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    try:
        await c.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass
    await c.answer()

@router.callback_query(F.data == "admin_sync")
async def admin_sync(c: CallbackQuery):
    if not is_admin(c.from_user.id):
        await c.answer(); return
    await c.message.answer("Стартую синхронизацию каталога…")
    proc = await asyncio.create_subprocess_exec(
        "python", "manage.py", "sync_clients_site",
        "--url", "https://atrium-art.clients.site/",
        "--headless", "--clicks", "30",
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.STDOUT,
    )
    out, _ = await proc.communicate()
    text = (out or b"").decode("utf-8", errors="ignore")
    tail = text[-3500:] if len(text) > 3500 else text
    await c.message.answer("Готово ✅\n\n" + (tail or "(нет вывода)"))
    await c.answer()


@router.callback_query(F.data.startswith("ordset:"))
async def order_set_status(c: CallbackQuery):
    """Admin: change order status and notify customer if possible."""
    if not is_admin(c.from_user.id):
        await c.answer();
        return
    try:
        _, oid, status = c.data.split(":", 2)
        order_id = int(oid)
    except Exception:
        await c.answer("Некорректные данные", show_alert=True)
        return

    o = await set_order_status(order_id, status)
    if not o:
        await c.answer("Заказ не найден", show_alert=True)
        return

    await c.answer("Готово ✅")
    try:
        await c.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    history = getattr(o, "status_history", None)
    history_note = ""
    try:
        latest = o.status_history.order_by("-created_at", "-id").first()
        history_note = latest.comment if latest else ""
    except Exception:
        history_note = ""

    slot_txt = o.delivery_slot.label if getattr(o, "delivery_slot", None) else "—"
    await c.message.answer(
        f"Заказ №{o.pk} обновлён\nНовый статус: {o.get_workflow_status_display()}\nСлот: {slot_txt}\n{history_note}".strip()
    )
