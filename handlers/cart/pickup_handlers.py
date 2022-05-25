from loader import dp
from aiogram.types import CallbackQuery
from utils.misc import api
from keyboards.inline import pickup_city_keyboard, pickup_address_keyboard, pickup_keyboard

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'pickup_order')
async def pickup_handler(call: CallbackQuery):
    """Выбрать город ПП"""
    cities = await api.get_distinct_city_pick_up()
    return await call.message.edit_text(text='Выберите город:', reply_markup=await pickup_city_keyboard(cities))



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'pp_city')
async def choice_city(call: CallbackQuery):
    """Выбрать адрес ПП"""
    city = call.data.split(':')[1]
    addresses = await api.get_city_pick_up(city)
    return await call.message.edit_text(text='Выберите адрес:', reply_markup=await pickup_address_keyboard(addresses))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'pp')
async def gey_pickup_handler(call: CallbackQuery):
    """Оформить заказ в ПП"""
    pp_id = call.data.split(':')[1]
    pp = await api.get_pick_up(pp_id)
    yandex_url = f"https://yandex.ru/maps/?text={pp['latitude']},{pp['longitude']}"
    keyboard = await pickup_keyboard(pp_id=pp_id,
                                     city=pp['city'], 
                                     yandex_url=yandex_url)
    return await call.message.edit_text(f'''<a href="{yandex_url}">{pp['city']} {pp['address']}</a>''', reply_markup=keyboard)
