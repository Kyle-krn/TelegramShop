from gc import callbacks
from models.models import FavoriteProduct, UserCart
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

    return keyboard

# call = "product:{product_id}:{"desc" or "attr"}:{photo_index}"
async def product_catalog_keyboard(products: list, parent_id: int, category_id: int, page: int, max_page: int, filters: bool = False):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton(text="Фильтрация 🔍", callback_data=f"settings_filters:{category_id}"))
    for product in products:            
        keyboard.add(InlineKeyboardButton(text=product["name"], callback_data=f"product:{product['id']}:desc:0:{page}"))

    if filters:
        callback = 'filtering_catalog'
    else:
        callback = 'all_products_page'
    prev_button = InlineKeyboardButton(text="⬅", callback_data=f"{callback}:{page-1}:{category_id}")
    page_button = InlineKeyboardButton(text=f"{page}/{max_page} 📄", callback_data=f"{callback}:{page}:{category_id}")
    next_button = InlineKeyboardButton(text="➡", callback_data=f"{callback}:{page+1}:{category_id}")
    prev = page - 1 > 0
    next = page + 1 <= max_page
    
    if prev and next:
        keyboard.add(prev_button, page_button, next_button)
    elif prev:
        keyboard.add(prev_button, page_button)
    elif next:
        keyboard.add(page_button, next_button)

    if parent_id:
        keyboard.add(InlineKeyboardButton(text="🔙 К категории", callback_data=f"category:{parent_id}"))
    else:
        keyboard.add(InlineKeyboardButton(text="🔙 К категории", callback_data=f"main_category:"))
    return keyboard



async def product_keyboard(category_id: int,
                           photo_index: int, 
                           photo_list: list, 
                           desc_or_attr: str, 
                           cart: UserCart,
                           favorite: FavoriteProduct,
                           quantity_max: int,
                           product_id: int,
                           page: int,
                           search_user: bool):
    keyboard = InlineKeyboardMarkup()
    
    prev_photo = InlineKeyboardButton(text="⬅️", callback_data=f"list_photo:{product_id}:{desc_or_attr}:{photo_index-1}:{page}") if photo_index > 0 else None
    photo_button = InlineKeyboardButton(text=f"{photo_index+1}/{len(photo_list)} 📸", callback_data="empty_call:")
    next_photo = InlineKeyboardButton(text="➡️", callback_data=f"list_photo:{product_id}:{desc_or_attr}:{photo_index+1}:{page}") if photo_index + 1 < len(photo_list) else None
    if prev_photo and next_photo:
        keyboard.add(prev_photo, photo_button, next_photo)
    elif prev_photo:
        keyboard.add(prev_photo, photo_button)
    elif next_photo:
        keyboard.add(photo_button, next_photo)
    
    if favorite:
        favorite_button = InlineKeyboardButton(text="Из избранного ⭐", callback_data=f"remove_favorite:{product_id}:{desc_or_attr}:{photo_index}:{page}")
    else:
        favorite_button = InlineKeyboardButton(text="В избранное ⭐", callback_data=f"add_favorite:{product_id}:{desc_or_attr}:{photo_index}:{page}")
    
    if not cart:
        add_to_cart_button = InlineKeyboardButton(text="В корзину 🛒", callback_data=f"add_in_cart:{product_id}:{desc_or_attr}:{photo_index}:{page}")
        
        keyboard.add(add_to_cart_button, favorite_button)
    else:
        # quantity = cart[0].quantity
        minus_button = InlineKeyboardButton(text="➖", callback_data=f"minus_c:{product_id}:{desc_or_attr}:{photo_index}:{page}") if cart[0].quantity > 0 else None
        quantity_button = InlineKeyboardButton(text=f"{cart[0].quantity} шт. 🛒", callback_data=f"add_in_cart:{product_id}:{page}") 
        plus_button = InlineKeyboardButton(text="➕", callback_data=f"plus_c:{product_id}:{desc_or_attr}:{photo_index}:{page}") if cart[0].quantity < quantity_max else None
        if minus_button and plus_button:
            keyboard.add(minus_button, quantity_button, plus_button)
        elif minus_button:
            keyboard.add(minus_button, quantity_button)
        elif plus_button:
            keyboard.add(quantity_button, plus_button)
        keyboard.add(favorite_button)

    if desc_or_attr == "desc":
        attr_desc_button = InlineKeyboardButton(text="Характеристики товара 📜", callback_data=f"product:{product_id}:attr:{photo_index}:{page}")
    elif desc_or_attr == "attr":
        attr_desc_button = InlineKeyboardButton(text="Описание товара 📜", callback_data=f"product:{product_id}:desc:{photo_index}:{page}")
    keyboard.add(attr_desc_button)

    if search_user:
        callback = "back_filters_category"
    else:
        callback = "back_category"
    keyboard.add(InlineKeyboardButton(text="🔙 Назад", callback_data=f"{callback}:{page}:{category_id}"))
    return keyboard



async def back_button(category):
    if category["parent_id"] :
        return InlineKeyboardButton(text="🔙 Назад", callback_data=f"category:{category['parent_id']}")
    else:
        return InlineKeyboardButton(text="🔙 Назад", callback_data=f"main_category:")