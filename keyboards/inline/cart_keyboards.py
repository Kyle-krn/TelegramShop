from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def main_cart_handler(products: list, user_cart:list, page: int, max_page: int, checkout: bool = False):
    keyboard = InlineKeyboardMarkup()
    for product in products:
        # pass
        product_in_cart = [i for i in user_cart if i.product_id == product['id']]
        product_in_cart = product_in_cart[0]
        text = f"{product['name']} || {product_in_cart.quantity} шт. || {product_in_cart.quantity * product['price']} руб."
        if checkout:
            if product_in_cart.active:
                text = "✅ " + text
            callback = f"checkout_product:{product_in_cart.product_id}"
        else:
            callback = f"product:{product['id']}:desc:0:{page}:cart"
        keyboard.add(InlineKeyboardButton(text=text, callback_data=callback))
            
    if checkout:
        callback = 'checkout'
    else:
        callback = 'cart'
    
    prev_button = InlineKeyboardButton(text="⬅", callback_data=f"{callback}:{page-1}")
    page_button = InlineKeyboardButton(text=f"{page}/{max_page} 📄", callback_data=f"{callback}:{page}")
    next_button = InlineKeyboardButton(text="➡", callback_data=f"{callback}:{page+1}")
    prev = page - 1 > 0
    next = page + 1 <= max_page

    if checkout:
        keyboard.add(InlineKeyboardButton(text="Назад", callback_data=f"cart:1"))
    else:
        keyboard.add(InlineKeyboardButton(text="К оформлению 📮", callback_data=f"checkout:None"))
    if prev and next:
        keyboard.add(prev_button, page_button, next_button)
    elif prev:
        keyboard.add(prev_button, page_button)
    elif next:
        keyboard.add(page_button, next_button)
    return keyboard

    