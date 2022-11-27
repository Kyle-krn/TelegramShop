from typing import List
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from utils.misc import api


async def main_cart_handler(products: list, user_cart: list, page: int, max_page: int, checkout: bool = False):
    """Клавитаура корзины"""
    keyboard = InlineKeyboardMarkup()
    count = 0
    for product in products:
        count += 1
        product_in_cart = [i for i in user_cart if i.product_id == product["id"]]
        product_in_cart = product_in_cart[0]
        text = (
            f"{product['name']} || {product_in_cart.quantity} шт. || {product_in_cart.quantity * product['price']} руб."
        )
        if checkout:
            if product_in_cart.active:
                text = "✅ " + text
            callback = f"checkout_product:{product_in_cart.product_id}"
        else:
            callback = f"product:{product['id']}:desc:0:{page}:cart"
        keyboard.add(InlineKeyboardButton(text=text, callback_data=callback))

    if checkout:
        callback = "checkout"
    else:
        callback = "cart"

    prev_button = InlineKeyboardButton(text="⬅", callback_data=f"{callback}:{page-1}")
    page_button = InlineKeyboardButton(text=f"{page}/{max_page} 📄", callback_data=f"{callback}:{page}")
    next_button = InlineKeyboardButton(text="➡", callback_data=f"{callback}:{page+1}")
    prev = page - 1 > 0
    next = page + 1 <= max_page

    if checkout:
        keyboard.add(InlineKeyboardButton(text="Доставка 📦", callback_data=f"payments_shipping_order:"))
        city = await api.get_distinct_city_pick_up()
        if city:
            keyboard.add(InlineKeyboardButton(text="Пункт самовывоза 📦", callback_data=f"pickup_order:"))

        keyboard.add(InlineKeyboardButton(text="Назад", callback_data=f"cart:1"))
    else:
        if count > 0:
            keyboard.add(InlineKeyboardButton(text="К оформлению 📮", callback_data=f"checkout:None"))
    if prev and next:
        keyboard.add(prev_button, page_button, next_button)
    elif prev:
        keyboard.add(prev_button, page_button)
    elif next:
        keyboard.add(page_button, next_button)
    return keyboard


async def pickup_city_keyboard(cities: List[str]):
    keyboard = InlineKeyboardMarkup()
    for city in cities:  # pp - pickup-point
        keyboard.add(InlineKeyboardButton(text=city, callback_data=f"pp_city:{city}"))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"checkout:"))
    return keyboard


async def pickup_address_keyboard(addresses: List[dict]):
    keyboard = InlineKeyboardMarkup()
    for address in addresses:  # pp - pickup-point
        keyboard.add(
            InlineKeyboardButton(text=f"г.{address['city']} {address['address']}", callback_data=f"pp:{address['id']}")
        )
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"pickup_order:"))
    return keyboard


async def pickup_keyboard(pp_id: int, yandex_url: str, city: str):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="📦 Заказать", callback_data=f"payments_pp_order:{pp_id}"))
    keyboard.add(InlineKeyboardButton(text="🗺️ Пункт самовывоза на картах", url=yandex_url))
    keyboard.add(InlineKeyboardButton(text="⬅️ Назад", callback_data=f"pp_city:{city}"))
    return keyboard
