from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.dispatcher.filters.builtin import CommandHelp

from loader import dp, bot

# # PAYMENTS_PROVIDER_TOKEN = '381764678:TEST:35960' # yoo
# # # PAYMENTS_PROVIDER_TOKEN = '1832575495:TEST:67cf43fa6193a3a6fe9766e7434713dfea0174453e9cf9eeca756d64cf36c717' # sbp
# # PAYMENTS_PROVIDER_TOKEN = '1744374395:TEST:99c4b6aa13a82ba0ae17' # maestro

# # PRICES = [
# #     types.LabeledPrice(label='Настоящая Машина Времени', amount=4200000),
# #     types.LabeledPrice(label='Подарочная упаковка', amount=30000)
# # ]

# # TELEPORTER_SHIPPING_OPTION = types.ShippingOption(
# #     id='teleporter',
# #     title='Всемирный* телепорт'
# # ).add(types.LabeledPrice('Телепорт', 1000000))


# # RUSSIAN_POST_SHIPPING_OPTION = types.ShippingOption(
# #     id='ru_post', title='Почтой России')

# # RUSSIAN_POST_SHIPPING_OPTION.add(
# #     types.LabeledPrice(
# #         'Деревянный ящик с амортизирующей подвеской внутри', 100000)
# # )
# # RUSSIAN_POST_SHIPPING_OPTION.add(
# #     types.LabeledPrice('Срочное отправление (5-10 дней)', 500000)
# # )

# # PICKUP_SHIPPING_OPTION = types.ShippingOption(id='pickup', title='Самовывоз')
# # PICKUP_SHIPPING_OPTION.add(types.LabeledPrice('Самовывоз в Москве', 50000))


@dp.message_handler(CommandHelp())
async def bot_help(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    for i in range(1000):
        keyboard.add(InlineKeyboardButton(text=i, callback_data='4'))
    
    await message.answer(text='fgr', reply_markup=keyboard)


# @dp.message_handler(commands=['buy'])
# async def process_buy_command(message: types.Message):
#     if PAYMENTS_PROVIDER_TOKEN.split(':')[1] == 'TEST':
#         await bot.send_message(message.chat.id, 'pre_buy_demo_alert')

#     await bot.send_invoice(message.chat.id,
#                            title='tm_title',
#                            description='tm_description',
#                            provider_token=PAYMENTS_PROVIDER_TOKEN,
#                            currency='rub',
#                            photo_url='https://i.pinimg.com/originals/90/2e/10/902e10dffa86c69228da40b642d8b6c6.png',
#                            photo_height=512,  # !=0/None or picture won't be shown
#                            photo_width=512,
#                            photo_size=512,

#                            # need_shipping_address=True,
#                            is_flexible=True,  # True If you need to set up Shipping Fee
#                            prices=PRICES,
#                            start_parameter='time-machine-example',
#                            payload='some-invoice-payload-for-our-internal-use')




# successful_payment = '''
# Ура! Платеж на сумму `{total_amount} {currency}` совершен успешно! Приятного пользования новенькой машиной времени!
# Правила возврата средств смотрите в /terms
# Купить ещё одну машину времени своему другу - /buy
# '''


    