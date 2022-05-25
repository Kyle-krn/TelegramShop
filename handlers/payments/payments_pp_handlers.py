from loader import dp, bot
from aiogram import types
from models.models import UserCart
from tortoise.queryset import Q
from utils.misc import api
from data.config import PAYMENTS_PROVIDER_TOKEN
from keyboards.inline import back_keyboard

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'payments_pp_order')
async def payments_order(call: types.CallbackQuery):
    await call.message.delete()
    cart = await UserCart.filter(Q(user__tg_id=call.message.chat.id) & Q(active=True))
    pp_id = call.data.split(':')[1]
    pp = await api.get_pick_up(pp_id)
    prices = []
    amount_for_button = 0
    for item in cart:
        product = await api.get_product_info(item.product_id)
        amount_for_button += (product['price'] - product['discount']) * item.quantity
        amount = (int(product['price']*100) - int(product['discount'] * 100)) * item.quantity
        prices.append(types.LabeledPrice(label=product['name'], amount=amount))
    prices.append(types.LabeledPrice(label=f"Самовывоз: {pp['city']} {pp['address']}", amount=0))
    keyboard = await back_keyboard(callback='back_checkout:', pay_text=f"Оплатить {amount_for_button} руб.")
    await bot.send_invoice(call.message.chat.id,
                           title='Ваша корзина',
                           description='Ваша корзина',
                           provider_token=PAYMENTS_PROVIDER_TOKEN,
                           currency='rub',
                           photo_url='https://thumbs.dreamstime.com/b/happy-shop-logo-design-template-shopping-designs-stock-134743566.jpg',
                           photo_height=512,  # !=0/None or picture won't be shown
                           photo_width=512,
                           photo_size=512, 
                           is_flexible=False,  # True If you need to set up Shipping Fee
                           prices=prices,
                           start_parameter='example',
                           need_name=True,
                           need_shipping_address=False,
                           need_phone_number=True,
                           payload=f"pp:{pp_id}",
                           reply_markup=keyboard)
