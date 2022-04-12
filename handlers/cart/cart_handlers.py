from loader import dp
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from models.models import UserCart
from utils.misc import api
from keyboards.inline import main_cart_handler
from tortoise.queryset import Q
import prettytable

@dp.message_handler(Text(equals=["🛒 Корзина"]))
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'cart')
async def cart_handler(message: Message or CallbackQuery):
    if isinstance(message, Message):
        page = 1
        chat_id = message.chat.id
    elif isinstance(message, CallbackQuery):
        page = int(message.data.split(":")[1])
        chat_id = message.message.chat.id
    limit = 15
    offset = (page - 1) * limit
    products = []
    user_cart = await UserCart.filter(user__tg_id=chat_id).offset(offset).limit(limit).order_by('id')
    user_cart_count = await UserCart.filter(user__tg_id=chat_id).count()
    max_page = (user_cart_count // limit) + 1 if user_cart_count % limit else  user_cart_count // limit
    for item in user_cart:
        product = await api.get_product_info(item.product_id)
        if 'detail' in product:
            await item.delete()
            continue
        if item.quantity > product['quantity']:
            item.quantity = product['quantity']
            await item.save()
        if item.quantity <= 0 or product['is_active'] is False:
            await item.delete()
            continue
        products.append(product)
    keyboard = await main_cart_handler(products=products,
                                       user_cart=user_cart,
                                       page=page,
                                       max_page=max_page)
    kwargs = {
        'text': f"В вашей коризне {user_cart_count} товаров.",
        "reply_markup": keyboard
    }
    
    if isinstance(message, Message):
        return await message.answer(**kwargs)
    elif isinstance(message, CallbackQuery):
        if message.message.photo:
            await message.message.delete()
            return await message.message.answer(**kwargs)
        return await message.message.edit_text(**kwargs)



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'checkout')
async def checkout_in_cart_handler(call: CallbackQuery):
    user_cart = await UserCart.filter(user__tg_id=call.message.chat.id).order_by('id')
    products = []
    text = ''
    text += fixed_lenght('Товар', 15) + ' '
    text += fixed_lenght('Кол-во', 7)
    text += fixed_lenght('Цена', 15)
    text = text + "\n\n"
    total_price = 0
    for item in user_cart:
        product = await api.get_product_info(item.product_id)
        if item.active:
            total_price += product['price']
            text += fixed_lenght(product['name'], 15) + ' '
            text += fixed_lenght(str(item.quantity), 7)
            text += fixed_lenght(str(product['price'] * item.quantity), 15)
            text += '\n'
        if 'detail' in product:
            await item.delete()
            continue
        if item.quantity > product['quantity']:
            item.quantity = product['quantity']
            await item.save()
        if item.quantity <= 0 or product['is_active'] is False:
            await item.delete()
            continue
        products.append(product)

    text += "\n"
    text += " " * 10 + 'Общая сумма:\n'
    text += " " * 10 + str(total_price) + 'руб.'
        

    keyboard = await main_cart_handler(products=products,
                                    user_cart=user_cart,
                                    page=1,
                                    max_page=1,
                                    checkout=True)


    text = '<pre>' + text + '</pre>'
    return await call.message.edit_text(text=text, reply_markup=keyboard)



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'checkout_product')
async def checkouts_product(call: CallbackQuery):
    product_in_cart = await UserCart.get(Q(user__tg_id=call.message.chat.id) & Q(product_id=int(call.data.split(':')[1])))
    product_in_cart.active = not product_in_cart.active # reverse bool
    await product_in_cart.save()
    call.data = 'checkout:1'
    return await checkout_in_cart_handler(call)


def fixed_lenght(text, lenght):
    if len(text) > lenght:
        text = text[:lenght-3] + "..."
    elif len(text) < lenght:
        text = (text + " " * lenght)[:lenght]
    return text
