from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def back_keyboard(callback: str, text: str = "🔙 Назад", pay_text: str = None):
    keyboard = InlineKeyboardMarkup()
    if pay_text:
        keyboard.add(InlineKeyboardButton(text=pay_text,pay=True))
    keyboard.add(InlineKeyboardButton(text=text, callback_data=callback))
    return keyboard