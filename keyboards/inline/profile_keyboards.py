from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from models.models import Profile

async def profile_keyboard(allowed_buy: bool = False, cart: bool = False, service: str = None):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text='Изменить имя', callback_data=f"profile_in_cart:{service}:first_name"))
    keyboard.add(InlineKeyboardButton(text='Изменить фамилию', callback_data=f"profile_in_cart:{service}:last_name"))
    keyboard.add(InlineKeyboardButton(text='Изменить номер', callback_data=f"profile_in_cart:{service}:phone_number"))
    keyboard.add(InlineKeyboardButton(text='Изменить почтовый индекс', callback_data=f"profile_in_cart:{service}:postcode"))
    keyboard.add(InlineKeyboardButton(text='Изменить город', callback_data=f"profile_in_cart:{service}:city"))
    keyboard.add(InlineKeyboardButton(text='Изменить адрес', callback_data=f"profile_in_cart:{service}:address"))
    if allowed_buy:
        keyboard.add(InlineKeyboardButton(text='Оформить и оплатить 💳', callback_data="profile_in_cart:address"))
    if cart:
        keyboard.add(InlineKeyboardButton(text='Назад', callback_data="choice_delivery:"))
    return keyboard


async def successful_input_data_keyboard(cart: bool, service: str = None):
    keyboard = InlineKeyboardMarkup()
    if cart:
        keyboard.add(InlineKeyboardButton(text='К оформлению заказа 📦', callback_data=f"delivery:{service}"))
    else:
        keyboard.add(InlineKeyboardButton(text='К профилю', callback_data="profile_main:"))
    return keyboard