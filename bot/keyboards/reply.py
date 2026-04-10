from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

def main_menu():
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text="Каталог"), KeyboardButton(text="🛒 Корзина")],
            [KeyboardButton(text="🔥 Хиты"), KeyboardButton(text="🆕 Новинки")],
            [KeyboardButton(text="✉️ Написать админу")],
        ],
        resize_keyboard=True
    )
