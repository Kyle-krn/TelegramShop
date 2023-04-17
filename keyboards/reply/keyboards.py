from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


async def main_keyborad():
    keyboard = ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.add(KeyboardButton(text="📙 Каталог"), KeyboardButton(text="🛒 Корзина"))
    keyboard.add(KeyboardButton(text="🔎 Поиск"), KeyboardButton(text="🌟 Избранное"), KeyboardButton(text="📔 Заказы"))
    keyboard.add(KeyboardButton(text="❓ FAQ"), KeyboardButton(text="✒ Контакты"))
    keyboard.add(KeyboardButton(text="⚙ Настройки"))
    return keyboard
