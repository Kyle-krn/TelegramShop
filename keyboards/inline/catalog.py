from utils.misc import api
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def start_catalog_keyboard(category_list):
    keyboard = InlineKeyboardMarkup()
    for category in category_list:
        if category["children"] or category["products"]:
            keyboard.add(InlineKeyboardButton(text=category["name"], callback_data=f"category:{category['id']}"))
    return keyboard

async def category_keyboard(category):
    keyboard = InlineKeyboardMarkup()
    for children in category["children"]:
        if children["children"] or children["products"]:
            button_text = children["name"]
            if children["products"]:
                button_text += f" ({len(children['products'])})"
            keyboard.add(InlineKeyboardButton(text=button_text, callback_data=f"category:{children['id']}"))
    keyboard.add(await back_button(category))
    # if category["parent"]:
    #     keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"category:{category['parent']['id']}"))
    # else:
    #     keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"main_category:"))
    return keyboard

async def product_keyboard(category):
    keyboard = InlineKeyboardMarkup()
    # print(category)
    for product in category["products"]:
        keyboard.add(InlineKeyboardButton(text=product["name"], callback_data=f"product:{product['id']}"))
    keyboard.add(await back_button(category))
    # keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data="category:"))
    return keyboard


async def back_button(category):
    if category["parent"]:
        return InlineKeyboardButton(text="🔙 Назад", callback_data=f"category:{category['parent']['id']}")
    else:
        return InlineKeyboardButton(text="🔙 Назад", callback_data=f"main_category:")