from ast import List
from decimal import Decimal
from loader import dp
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from models.models import UserCart, Profile
from utils.misc import api, delivery_api
from keyboards.inline import main_cart_handler
from tortoise.queryset import Q
from keyboards.inline import profile_keyboard, choice_delivery

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
    edit_product = ''
    for item in user_cart:
        product = await api.get_product_info(item.product_id)
        if 'detail' in product:
            edit_product += "<b></b>"
            user_cart_count -= 1
            await item.delete()
            continue
        if item.quantity > product['quantity']:
            edit_product += f"<b>{product['name']} - максимальное кол-во {product['quantity']} шт.</b>\n"
            item.quantity = product['quantity']
            await item.save()
        if item.quantity <= 0 or product['is_active'] is False:
            edit_product += f"<b>{product['name']} больше не доступен.</b>\n"
            await item.delete()
            user_cart_count -= 1
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
    if edit_product:
        kwargs['text'] += "\n\n" + edit_product
    
    if isinstance(message, Message):
        return await message.answer(**kwargs)
    elif isinstance(message, CallbackQuery):
        if message.message.photo:
            await message.message.delete()
            return await message.message.answer(**kwargs)
        return await message.message.edit_text(**kwargs)



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'checkout')
async def checkout_in_cart_handler(call: CallbackQuery):
    # print(call.message.date.replace(tzinfo=None))
    user_cart = await UserCart.filter(user__tg_id=call.message.chat.id).order_by('id')
    products = []
    text = ''
    text += fixed_lenght('Товар', 15) + ' '
    text += fixed_lenght('Кол-во', 7)
    text += fixed_lenght('Цена', 15)
    text = text + "\n\n"
    total_price = 0
    discount = 0
    edit_product = ''
    for item in user_cart:
        product = await api.get_product_info(item.product_id)
        if 'detail' in product:
            await item.delete()
            continue
        if item.quantity > product['quantity']:
            edit_product += f"<b>{product['name']} - максимальное кол-во {product['quantity']} шт.</b>\n"
            item.quantity = product['quantity']
            await item.save()
        if item.quantity <= 0 or product['is_active'] is False:
            edit_product += f"<b>{product['name']} больше не доступен.</b>\n"
            await item.delete()
            continue

        if item.active:
            total_price += product['price'] * item.quantity
            text += fixed_lenght(product['name'], 15) + ' '
            text += fixed_lenght(str(item.quantity), 7)
            text += fixed_lenght(str((product['price'] - product['discount']) * item.quantity), 15)
            text += '\n'
            discount += product['discount'] * item.quantity
        products.append(product)
    text += '\n\n'
    text +='Общая сумма: ' + str(total_price) + 'руб.\n'
    text +='Скидка: ' + str(discount) + 'руб.\n'
    text +='Цена со скидкой: ' + str(total_price - discount) + 'руб.\n'

    if edit_product:
        text += '\n' + edit_product 
    # text += "\n"
    # text += " " * 10 + 'Общая сумма:\n'
    # if discount:
    #     text += " " * 10 + str(total_price - discount) + 'руб.'
    # else:
    #     text += " " * 10 + str(total_price) + 'руб.'
    

    keyboard = await main_cart_handler(products=products,
                                    user_cart=user_cart,
                                    page=1,
                                    max_page=1,
                                    checkout=True)


    text = '<pre>' + text + '</pre>'
    return await call.message.edit_text(text=text, reply_markup=keyboard)


def fixed_lenght(text, lenght):
    if len(text) > lenght:
        text = text[:lenght-3] + "..."
    elif len(text) < lenght:
        text = (text + " " * lenght)[:lenght]
    return text

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'checkout_product')
async def checkouts_product(call: CallbackQuery):
    product_in_cart = await UserCart.get(Q(user__tg_id=call.message.chat.id) & Q(product_id=int(call.data.split(':')[1])))
    product_in_cart.active = not product_in_cart.active # reverse bool
    await product_in_cart.save()
    call.data = 'checkout:1'
    return await checkout_in_cart_handler(call)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'choice_delivery')
async def choice_delivery_handler(call: CallbackQuery):
    return await call.message.edit_text("Выберите способ доставки 🚚", reply_markup=await choice_delivery())


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'delivery')
async def delivery_handler(call: CallbackQuery):
    user_cart = await UserCart.filter(Q(user__tg_id=call.message.chat.id) & Q(active=True)).order_by('id')
    edit_product = ''
    weight_cart = 0
    total_price = 0
    discount = 0
    for item in user_cart:
        product = await api.get_product_info(item.product_id)
        if 'detail' in product:
            edit_product += "<b></b>"
            user_cart_count -= 1
            await item.delete()
            continue
        if item.quantity > product['quantity']:
            edit_product += f"<b>{product['name']} - максимальное кол-во {product['quantity']} шт.</b>\n"
            item.quantity = product['quantity']
            await item.save()
        if item.quantity <= 0 or product['is_active'] is False:
            edit_product += f"<b>{product['name']} больше не доступен.</b>\n"
            await item.delete()
            user_cart_count -= 1
            continue
        weight_cart += product['weight'] * item.quantity
        total_price += product['price'] * item.quantity
        discount += product['discount'] * item.quantity
    service = call.data.split(':')[1]
    # if service == 'pochta_rf':
    text, allowed_buy, coast_delivery = await delivery_data_handler(call.message.chat.id, service, weight_cart)
    
    if edit_product:
        text += edit_product
    if coast_delivery:
        total_price += coast_delivery
    text += '<b>Общая сумма: ' + str(total_price) + 'руб.\n'
    text += 'Скидка: ' + str(discount) + 'руб.\n'
    text += 'Цена со скидкой: ' + str(total_price - discount) + 'руб.</b>\n'

    return await call.message.edit_text(text=text, reply_markup=await profile_keyboard(allowed_buy=allowed_buy, cart=True, service=service))




# @dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'delivery_data')
async def delivery_data_handler(chat_id: int, service: str, weight: int,):
    profile = await Profile.get(user__tg_id=chat_id)
    text = '<b>Имя</b> - '
    allowed_buy = True
    coast_delivery = None
    if profile.first_name:
        text += profile.first_name + "\n"
    else:
        allowed_buy = False
        text += "Не указано\n"
    text += '<b>Фамилия</b> - '
    if profile.last_name:
        text += profile.last_name + "\n"
    else:
        allowed_buy = False
        text += "Не указано\n"
    text += '<b>Номер телефона</b> - '
    if profile.phone_number:
        text += profile.phone_number + "\n"
    else:
        allowed_buy = False
        text += "Не указано\n" 
    
    text += '<b>Город</b> - '
    if profile.city:
        text += profile.city + "\n"
    else:
        allowed_buy = False
        text += "Не указано\n"
    text += '<b>Адрес</b> - '
    if profile.address:
        text += profile.address + "\n"
    else:
        allowed_buy = False
        text += "Не указано\n"

    if service == 'pochta_rf':
        text += '<b>Почтовый индекс</b> - '
        if profile.postcode:
            coast_delivery = await delivery_api.pochta_rf(postcode=profile.postcode, weight=weight)
            text += str(profile.postcode) + "\n"
            text += f"\n<b>Стоймость доставки {coast_delivery['amount']} руб.</b>\n"
        else:
            allowed_buy = False
            text += "Не указано\n"    
    
    if allowed_buy is False:
        text += '\n\n<b>Заполните недостающие данные что бы продолжить.</b>\n'
    return text, allowed_buy, coast_delivery
