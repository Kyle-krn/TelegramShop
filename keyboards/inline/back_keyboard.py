from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def back_keyboard(callback: str, text: str = "🔙 Назад"):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text=text, callback_data=callback))
    return keyboard