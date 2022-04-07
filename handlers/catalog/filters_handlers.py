from loader import dp
from aiogram.types import CallbackQuery, Message
from utils.misc import api
from keyboards.inline import filtering_products_keyboard, back_keyboard
from models.models import SearchUserData
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

class Price(StatesGroup):
    min_price = State()  
    max_price = State()


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'filtering_catalog')
async def filtering_catalog_handler(call: CallbackQuery):
    data_search = await SearchUserData.get(user__tg_id=call.message.chat.id)
    print(data_search)



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'settings_filters')
async def setting_filters_handler(call: CallbackQuery):
    category = await api.get_category_light_info(category_id=call.data.split(':')[1], filters=True, products=True)
    # await state.finish()
    search_data = await SearchUserData.get(user__tg_id=call.message.chat.id)
    amount_list = [i["price"] for i in category["products"]]
    kwargs = {
        'category_id': category['id'],
        'min_price': min(amount_list) if not search_data.min_price else search_data.min_price,
        'max_price': max(amount_list) if not search_data.max_price else search_data.max_price,
    }
    keyboard = await filtering_products_keyboard(**kwargs)
    await call.message.edit_text(text='Вы можете выбрать параметры ниже', reply_markup=keyboard)




@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'min_price')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'max_price')
async def min_price_handler(call: CallbackQuery):
    if call.data.split(':')[0] == 'min_price':
        await Price.min_price.set()
        text='<b>Введите минимальную цену:</b>'
    else:
        await Price.max_price.set()
        text='<b>Введите максимальную цену:</b>'    
    state = dp.get_current().current_state()
    await state.update_data(category_id=int(call.data.split(':')[1]))
    # print(f"filter_catalog:{call.data.split(':')[1]}")
    await call.message.edit_text(text=text, reply_markup=await back_keyboard(callback=f"cancel_state_filtering:{call.data.split(':')[1]}"))


@dp.message_handler(state=Price)
async def process_price_invalid(message: Message, state: FSMContext):
    current_state = await state.get_state()
    try:
        price = float(message.text)
        if price <= 0:
            return await message.reply("Цена не может быть отрицательной или нулем.")
        search_data = await SearchUserData.get(user__tg_id=message.chat.id)
        current_state = await state.get_state()
        if current_state.split(":")[1] == 'min_price':
            search_data.min_price = price
            text = f"Ищем цены от {'%.2f' % price} 👀\n"
        elif current_state.split(":")[1] == 'max_price':
            search_data.max_price = price
            text = f"Ищем цены до {'%.2f' % price} 👀\n"
        await search_data.save()
        
        user_data = await state.get_data()
        await state.finish()
        return await message.answer(text + "Что бы продолжить нажмите кнопку ниже 👇", reply_markup=await back_keyboard(callback=f"settings_filters:{user_data['category_id']}", 
                                                                                                  text="К настройкам поиска 🔎"))
        
    except (TypeError, ValueError):
        return await message.reply("Введите число.")




@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'cancel_state_filtering', state=Price)
async def dffrj(call: CallbackQuery, state: FSMContext):
    await state.finish()
    call.data = f"settings_filters:{call.data.split(':')[1]}"
    return await setting_filters_handler(call)