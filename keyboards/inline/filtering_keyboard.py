from ast import keyword
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def filtering_products_keyboard(category_id: int,min_price:int, max_price: int):
    keyboard = InlineKeyboardMarkup()
    min_price_button = InlineKeyboardButton(text=f"Мин. цена: {min_price} руб.", callback_data=f"min_price:{category_id}")
    max_price_button = InlineKeyboardButton(text=f"Макс. цена: {max_price} руб.", callback_data=f"max_price:{category_id}")
    keyboard.add(min_price_button, max_price_button)
    
    keyboard.add(InlineKeyboardButton(text=f"Найти товары 🔎", callback_data=f"filtering_catalog:{category_id}"))
    keyboard.add(InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"category:{category_id}"))
    return keyboard
    # keyboard.add(InlineKeyboardButton())

