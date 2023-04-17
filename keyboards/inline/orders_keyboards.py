from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from datetime import datetime


async def orders_keyboard(orders: list):
    keyboard = InlineKeyboardMarkup()
    for order in orders:
        date_time_obj = datetime.fromisoformat(order["created_at"]).strftime("%m/%d/%Y")
        text = f"Заказ #{order['id']} от {date_time_obj}"
        keyboard.add(InlineKeyboardButton(text=text, callback_data=f"order:{order['id']}"))
    return keyboard
