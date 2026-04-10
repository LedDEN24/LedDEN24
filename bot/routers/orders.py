import re
from aiogram import Router, F
from aiogram.types import CallbackQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from aiogram import Bot

from bot.config import TG_ADMIN_IDS
from bot.db import create_order_single_item
from bot.keyboards.inline import order_admin_kb

PHONE_RE = re.compile(r"\+?\d[\d\s\-\(\)]{7,}")

router = Router()

class OrderFlow(StatesGroup):
    waiting_phone = State()
    waiting_address = State()

@router.callback_query(F.data.startswith("order:"))
async def order(c: CallbackQuery, state: FSMContext):
    slug = c.data.split(":",1)[1]
    await state.update_data(product_slug=slug)
    await state.set_state(OrderFlow.waiting_phone)
    await c.message.answer("Ок ✅ Напиши номер телефона (можно в формате +7...)")
    await c.answer()

@router.message(OrderFlow.waiting_phone)
async def got_phone(m: Message, state: FSMContext):
    phone = (m.text or "").strip()
    if not PHONE_RE.fullmatch(phone):
        await m.answer("Не похоже на номер телефона. Попробуй ещё раз, например: +7 999 123-45-67")
        return
    await state.update_data(phone=phone)
    await state.set_state(OrderFlow.waiting_address)
    await m.answer("Отлично. Напиши адрес доставки (или напиши 'самовывоз').")


@router.message(OrderFlow.waiting_address)
async def got_address(m: Message, bot: Bot, state: FSMContext):
    address = (m.text or "").strip()
    if len(address) < 3:
        await m.answer("Адрес слишком короткий. Попробуй ещё раз.")
        return

    data = await state.get_data()
    product_slug = data.get("product_slug")
    phone = data.get("phone")
    if not product_slug or not phone:
        await state.clear()
        await m.answer("Что-то пошло не так. Попробуй снова открыть товар и нажать 'Заказать'.")
        return

    order_id = await create_order_single_item(
        product_slug=product_slug,
        qty=1,
        name=m.from_user.full_name or "",
        phone=phone,
        address=address,
        comment="Заказ из Telegram",
        tg_user_id=str(m.from_user.id),
        tg_chat_id=str(m.chat.id),
    )

    # Уведомим админов с кнопками смены статуса
    admin_text = (
        f"<b>Новый заказ #{order_id}</b>\n"
        f"Товар: {product_slug}\n"
        f"Имя: {m.from_user.full_name or '-'}\n"
        f"Тел: {phone}\n"
        f"Адрес: {address}"
    )
    for aid in TG_ADMIN_IDS:
        try:
            await bot.send_message(chat_id=int(aid), text=admin_text, parse_mode="HTML", reply_markup=order_admin_kb(order_id))
        except Exception:
            pass

    await state.clear()
    await m.answer(f"Спасибо! Заказ №{order_id} принят ✅\nМы свяжемся с вами для подтверждения.")
