from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from bot.keyboards.reply import main_menu
from bot.texts import START_TEXT

router = Router()

@router.message(CommandStart())
async def start(m: Message):
    await m.answer(START_TEXT, reply_markup=main_menu())
