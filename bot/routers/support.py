from __future__ import annotations

from aiogram import Router, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

from bot.config import is_admin, TG_ADMIN_IDS


router = Router()


class SupportFlow(StatesGroup):
    waiting_text = State()


@router.message(F.text.contains("админу"))
async def start_support(m: Message, state: FSMContext):
    await state.set_state(SupportFlow.waiting_text)
    await m.answer("Напишите сообщение для администратора.\n\nОтмена: /cancel")


@router.message(Command("cancel"))
async def cancel_support(m: Message, state: FSMContext):
    await state.clear()
    await m.answer("Отменено ✅")


@router.message(SupportFlow.waiting_text)
async def send_support(m: Message, state: FSMContext):
    text = (m.text or "").strip()
    if not text:
        return await m.answer("Пришлите текст сообщением (или /cancel).")

    user = m.from_user
    header = (
        "✉️ Сообщение с сайта/бота\n"
        f"От: {user.full_name} (@{user.username or '-'})\n"
        f"ID: {user.id}\n\n"
    )
    payload = header + text

    sent = 0
    for admin_id in TG_ADMIN_IDS:
        try:
            await m.bot.send_message(chat_id=int(admin_id), text=payload)
            await m.bot.send_message(
                chat_id=int(admin_id),
                text=f"Ответить: /reply {user.id} <текст>",
            )
            sent += 1
        except Exception:
            pass

    await state.clear()
    if sent:
        await m.answer("✅ Отправлено админу. Мы скоро ответим.")
    else:
        await m.answer("⚠️ Не удалось отправить администратору. Проверь TG_ADMIN_IDS в .env")


@router.message(Command("reply"))
async def admin_reply(m: Message):
    if not is_admin(m.from_user.id):
        return

    parts = (m.text or "").split(maxsplit=2)
    if len(parts) < 3:
        return await m.answer("Формат: /reply <user_id> <текст>")

    try:
        user_id = int(parts[1])
    except Exception:
        return await m.answer("user_id должен быть числом")

    text = parts[2].strip()
    if not text:
        return await m.answer("Пустое сообщение")

    try:
        await m.bot.send_message(chat_id=user_id, text=f"✉️ Ответ администратора:\n\n{text}")
        await m.answer("Отправлено ✅")
    except Exception as e:
        await m.answer(f"Не получилось отправить: {e}")
