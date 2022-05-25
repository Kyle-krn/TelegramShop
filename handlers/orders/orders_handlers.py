from datetime import datetime
from loader import dp
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from utils.misc import api
from keyboards.inline import orders_keyboard, back_keyboard
from utils import fixed_lenght


@dp.message_handler(Text(equals=["📔 Заказы"]))
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'back_order')
async def get_user_orders(message: Message):
    if isinstance(message, CallbackQuery):
        chat_id = message.message.chat.id
    else:
        chat_id = message.chat.id
    orders = await api.get_user_order(chat_id)
    keyboard = await orders_keyboard(orders)
    if isinstance(message, CallbackQuery):
        return await message.message.edit_text(text="Ваши заказы:", reply_markup=keyboard)
    await message.answer(text="Ваши заказы:", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'order')
async def get_order(call: CallbackQuery):
    order_id = call.data.split(':')[1]
    order = await api.get_order(order_id)
    text = f"<b>Заказ #{order['id']}</b>\n"  \
           f"<b>Дата создания: </b> {datetime.fromisoformat(order['created_at']).strftime('%m/%d/%Y %H:%M:%S')}\n"  \
           f"<b>Статус заказа: </b> {order['status']}\n"  \
           f"<b>Метод доставки: </b> {order['shipping_type']}\n"  \
           f"<b>Стоймость доставки: </b> {order['shipping_amount']} руб. \n"  \
           f"<b>Стоймость заказа: </b> {order['amount']} руб.\n"
    
    if order['shipping_type'] == 'Пункт самовывоза':
        yandex_url = f"https://yandex.ru/maps/?text={order['pickup_point']['latitude']},{order['pickup_point']['longitude']}"
        text += f'<b>Пункт самовывоза: </b> <a href="{yandex_url}">Click</a>\n'  \
                f'<b>Код для получения:</b> <b>{order["pickup_code"]}</b>\n\n'
    else:
        order['address2'] = '' if order['address2'] is None else order['address2']
        text += f"<b>Регион: </b> {order['region']}\n"  \
                f"<b>Город: </b> {order['city']}\n"  \
                f"<b>Адрес: </b> {order['address1'] + order['address2']}\n"  \
                f"<b>Почтовый индекс: </b> {order['postcode']}\n\n"
    table_text = ''
    table_text += fixed_lenght('Товар', 15) + ' '
    table_text += fixed_lenght('Кол-во', 7)
    table_text += fixed_lenght('Цена', 15)
    table_text += "\n"
    for product in order['products']:
        table_text += fixed_lenght(product['name'], 15) + ' '
        table_text += fixed_lenght(str(product['quantity']), 7)
        table_text += fixed_lenght(str((product['price'] - product['discount']) * product['quantity']), 15)
        table_text += '\n'
    text += f"<pre>{table_text}</pre>"
    return await call.message.edit_text(text, reply_markup=await back_keyboard('back_order:'))
