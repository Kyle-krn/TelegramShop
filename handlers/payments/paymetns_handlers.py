from aiogram import types
from loader import dp, bot
from models.models import UserCart
from tortoise.queryset import Q
from utils.misc import api
PAYMENTS_PROVIDER_TOKEN = '1744374395:TEST:99c4b6aa13a82ba0ae17' # maestro

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'payments_order')
async def payments_order(call: types.CallbackQuery):
    cart = await UserCart.filter(Q(user__tg_id=call.message.chat.id) & Q(active=True))
    prices = []
    for item in cart:
        product = await api.get_product_info(item.product_id)
        prices.append(types.LabeledPrice(label=product['name'], amount=int(product['price']*100)))

    await bot.send_invoice(call.message.chat.id,
                           title='Ваша корзина',
                           description='tm_description',
                           provider_token=PAYMENTS_PROVIDER_TOKEN,
                           currency='rub',
                           photo_url='https://i.pinimg.com/originals/90/2e/10/902e10dffa86c69228da40b642d8b6c6.png',
                           photo_height=512,  # !=0/None or picture won't be shown
                           photo_width=512,
                           photo_size=512,

                           # need_shipping_address=True,
                           is_flexible=True,  # True If you need to set up Shipping Fee
                           prices=prices,
                           start_parameter='time-machine-example',
                           payload='some-invoice-payload-for-our-internal-use')