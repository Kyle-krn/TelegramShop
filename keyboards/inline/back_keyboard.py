from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def back_keyboard(callback: str):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data=callback))
    return keyboard