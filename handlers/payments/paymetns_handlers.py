from aiogram import types
import aiohttp
from loader import dp, bot
from models.models import UserCart
from tortoise.queryset import Q
from utils.misc import api, delivery_api

PAYMENTS_PROVIDER_TOKEN = '1744374395:TEST:99c4b6aa13a82ba0ae17' # maestro
PAYMENTS_PROVIDER_TOKEN = '1832575495:TEST:67cf43fa6193a3a6fe9766e7434713dfea0174453e9cf9eeca756d64cf36c717' # sbp
PAYMENTS_PROVIDER_TOKEN = '401643678:TEST:a032022f-9d57-4664-acfe-49318e37bfcf' # sbp
# PAYMENTS_PROVIDER_TOKEN = '381764678:TEST:35960' # sbp

RUSSIAN_POST_SHIPPING_OPTION = types.ShippingOption(id='ru_post', title='Почтой России')

COURIER_SHIPPING_OPTION = types.ShippingOption(id='courier', title='Курьером')


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'payments_order')
async def payments_order(call: types.CallbackQuery):
    cart = await UserCart.filter(Q(user__tg_id=call.message.chat.id) & Q(active=True))
    prices = []
    weight = 0
    for item in cart:
        product = await api.get_product_info(item.product_id)
        weight += product['weight'] * item.quantity
        amount = (int(product['price']*100) - int(product['discount'] * 100)) * item.quantity
        prices.append(types.LabeledPrice(label=product['name'], amount=amount))

    await bot.send_invoice(call.message.chat.id,
                           title='Ваша корзина',
                           description='Ваша корзина',
                           provider_token=PAYMENTS_PROVIDER_TOKEN,
                           currency='rub',
                           photo_url='https://i.pinimg.com/originals/90/2e/10/902e10dffa86c69228da40b642d8b6c6.png',
                           photo_height=512,  # !=0/None or picture won't be shown
                           photo_width=512,
                           photo_size=512,

                           # need_shipping_address=True,
                           is_flexible=True,  # True If you need to set up Shipping Fee
                           prices=prices,
                           start_parameter='example',
                           need_name=True,
                           need_shipping_address=True,
                           need_phone_number=True,
                           payload=f'{weight}')



@dp.pre_checkout_query_handler(lambda query: True)
async def checkout(pre_checkout_query: types.PreCheckoutQuery):
    await bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True,
                                        error_message="Aliens tried to steal your card's CVV,"
                                                      " but we successfully protected your credentials,"
                                                      " try to pay again in a few minutes, we need a small rest.")



@dp.shipping_query_handler(lambda query: True)
async def process_shipping_query(shipping_query: types.ShippingQuery):
    print('shipping_query.shipping_address')
    # print(shipping_query)
    weight = int(shipping_query.invoice_payload)
    shipping_query.invoice_payload = 4
    if shipping_query.shipping_address.country_code != 'RU':
        return await bot.answer_shipping_query(
            shipping_query.id,
            ok=False,
            error_message="Отправление товара происходит только по территории РФ."
        )
    
    if shipping_query.shipping_address.post_code.isdigit() is False or len(shipping_query.shipping_address.post_code) != 6:
        return await bot.answer_shipping_query(
            shipping_query.id,
            ok=False,
            error_message="Почтовый индекс состоит из 6 цифр."
        )

    # if shipping_query.shipping_address.name

    resp = await delivery_api.pochta_rf(postcode=shipping_query.shipping_address.post_code, weight=weight)
    if 'detail' in resp:
        return await bot.answer_shipping_query(
            shipping_query.id,
            ok=False,
            error_message=resp['detail']
        )
    shipping_options = [RUSSIAN_POST_SHIPPING_OPTION]
    RUSSIAN_POST_SHIPPING_OPTION.prices.clear()
    COURIER_SHIPPING_OPTION.prices.clear()
    RUSSIAN_POST_SHIPPING_OPTION.add(types.LabeledPrice('Почта РФ', resp['amount'] * 100))

    result_city = await api.get_city_courier(shipping_query.shipping_address.city)
    if 'amount' in result_city:
        COURIER_SHIPPING_OPTION.add(types.LabeledPrice(f"Курьер г. {result_city['city']}", result_city['amount'] * 100))
        shipping_options.append(COURIER_SHIPPING_OPTION)
    # if 'amount' in result_city:
    # if shipping_query.shipping_address.city == 'Москва':
    #     COURIER_SHIPPING_OPTION.add(types.LabeledPrice('Курьером по Москве', 500 * 100))
    #     shipping_options.append(COURIER_SHIPPING_OPTION)

    await bot.answer_shipping_query(
        shipping_query.id,
        ok=True,
        shipping_options=shipping_options
    )



@dp.message_handler(content_types=types.ContentType.SUCCESSFUL_PAYMENT)
async def process_successful_payment(message: types.Message):
    print('successful_payment:')
    pmnt = message.successful_payment
    print(pmnt)
    # print(pmnt.shipping_address)
    # for key, val in pmnt.items():
    #     print(f'{key} = {val}')
    if pmnt.shipping_option_id == 'ru_post':
        shipping_option = "Почта РФ"
        weight = int(pmnt.invoice_payload)
        shipping_amount = await delivery_api.pochta_rf(postcode=pmnt.order_info.shipping_address.post_code, weight=weight)
        
    elif pmnt.shipping_option_id == 'courier':
        shipping_option = "Курьер"
        shipping_amount = await api.get_city_courier(pmnt.order_info.shipping_address.city)
    shipping_amount = shipping_amount['amount']
    order_amount = pmnt.total_amount - (shipping_amount * 100)
    cart = await UserCart.filter(Q(user__tg_id=message.chat.id) & Q(active=True))
    resp = await api.create_order(shipping_amount=shipping_amount, 
                                  order_amount= order_amount / 100,
                                  shipping_option=shipping_option,
                                  order_info=pmnt.order_info,
                                  tg_id=message.chat.id,
                                  username=message.chat.username,
                                  cart=cart)
    for item in cart:
        await item.delete()
    
    await bot.send_message(
        message.chat.id,
        resp['message']
        )
    