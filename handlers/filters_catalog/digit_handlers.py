from loader import dp
from aiogram.types import CallbackQuery, Message
from aiogram.dispatcher import FSMContext
from utils.misc import api
from models.models import ArchiveStringAttrs, SearchUserData
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.inline import back_keyboard, digit_keyboard
from tortoise.queryset import Q

class DigitAttr(StatesGroup):
    min = State()  
    max = State()


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'digit_filter')
async def digit_filter_handler(call: CallbackQuery):
    '''Фильтр для типов значений int float, позволяет указать диапазон поиска от мин до макс'''
    attr_name_id = call.data.split(':')[1]
    attr_name = await ArchiveStringAttrs.get(id=int(attr_name_id))
    # attr_name = attr_name.string
    category_id = int(call.data.split(':')[2])
    search_data = await SearchUserData.get(Q(user__tg_id=call.message.chat.id) & Q(category_id=category_id))
    category = await api.get_category_light_info(category_id=category_id, filters=True)
    attr_in_category = [i for i in category['filters'] if i['name'] == attr_name.string]
    if len(attr_in_category) == 0:
        raise IndexError(f"Атрибут с таким именем не найден")
    if type(attr_in_category[0]['value']) not in [int, float]:
        raise IndexError(f"Атрибут {attr_name.string} не является числом.")
    min_max = await api.get_min_max_digit_attr(category_id=category_id, attr_name=attr_name.string)
    attr_in_data = [i for i in search_data.attrs if i['name'] == attr_name.string] if search_data.attrs is not None else []
    if attr_in_data:
        attr_in_data = attr_in_data[0]
        attr_in_data['min'] = min_max['min'] if attr_in_data['min'] is None else attr_in_data['min']
        attr_in_data['max'] = min_max['max'] if attr_in_data['max'] is None else attr_in_data['max']
    else:
        attr_in_data = {'name': attr_name.string, 'value': None, 'min': min_max['min'], 'max': min_max['max']}
        if type(attr_in_category[0]['value']) == int:
            attr_in_data['min'] = int(attr_in_data['min'])
            attr_in_data['max'] = int(attr_in_data['max'])
    
    keyboard = await digit_keyboard(attr_name_id=attr_name.id, 
                                    category_id=category_id, 
                                    user_value=attr_in_data, 
                                    prefix=attr_in_category[0]['prefix'])
    await call.message.delete()
    return await call.message.answer(text='Вы можете изменить диапазон поиска ниже ⬇️', reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'reset_digit')
async def reset_filter_handler(call: CallbackQuery):
    '''Устанавливает стандартный диапазон'''
    attr_name_id = call.data.split(':')[1]
    attr_name = await ArchiveStringAttrs.get(id=int(attr_name_id))
    attr_name = attr_name.string
    category_id = int(call.data.split(':')[2])
    search_data = await SearchUserData.get(Q(user__tg_id=call.message.chat.id) & Q(category_id=category_id))
    search_data.attrs = [i for i in search_data.attrs if i['name'] != attr_name]
    await search_data.save()
    call.data = "digit_filter:" + ":".join(call.data.split(':')[1:])
    return await digit_filter_handler(call)

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'min_attr')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'max_attr')
async def min_price_handler(call: CallbackQuery):  
    '''Выбор между мин и макс'''  
    if call.data.split(':')[0] == 'min_attr':
        await DigitAttr.min.set()
        text='<b>Введите минимальное значение:</b>'
    else:
        await DigitAttr.max.set()
        text='<b>Введите максимальное значение:</b>'    
    state = dp.get_current().current_state()
    
    kwargs = {
    "attr_name_id": call.data.split(':')[1],
    "category_id": int(call.data.split(':')[2])
    }
    await state.update_data(**kwargs)
    await call.message.edit_text(text=text, reply_markup=await back_keyboard(callback=f"cds:digit_filter:{kwargs['attr_name_id']}:{kwargs['category_id']}"))


@dp.message_handler(state=DigitAttr)
async def process_price_invalid(message: Message, state: FSMContext):
    '''Валидация и установка новых значений при успешной валидации'''
    user_data = await state.get_data()          #cds - cancel_digit_state
    attr_name = await ArchiveStringAttrs.get(id=int(user_data['attr_name_id']))
    keyboard = await back_keyboard(callback=f"cds:digit_filter:{attr_name.id}:{user_data['category_id']}")
    category = await api.get_category_light_info(category_id=user_data['category_id'], filters=True)
    attr_in_category = [i for i in category['filters'] if i['name'] == attr_name.string]
    try:
        value = float(message.text) if type(attr_in_category[0]['value']) == float else int(message.text)
    except (TypeError, ValueError):
        return await message.reply("Введите число.", reply_markup=keyboard)
    min_max = await api.get_min_max_digit_attr(category_id=user_data['category_id'], attr_name=attr_name.string)
    if (min_max['min'] <= value <= min_max['max']) is False:
        min_max['min'] = int(min_max['min']) if type(attr_in_category[0]['value']) == int else min_max['min']
        min_max['max'] = int(min_max['max']) if type(attr_in_category[0]['value']) == int else min_max['max']
        return await message.reply(f"От {min_max['min']} {attr_in_category[0]['prefix']} до  {min_max['max']} {attr_in_category[0]['prefix']}" ,reply_markup=keyboard)
    search_data = await SearchUserData.get(Q(user__tg_id=message.chat.id) & Q(category_id=category['id']))
    
    current_state = await state.get_state()

    attr_in_data = [i for i in search_data.attrs if i['name'] == attr_name.string] if search_data.attrs is not None else []
    if not attr_in_data:
        attr_in_data = [
                        {'name': attr_name.string, 
                         'value': None, 
                         'min': int(min_max['min']) if type(attr_in_category[0]['value']) == int else min_max['min'], 
                         'max': int(min_max['max']) if type(attr_in_category[0]['value']) == int else min_max['max']
                         }
                         ]

    if current_state.split(":")[1] == 'min':
        attr_in_data[0]['min'] = value 
        text = f"Ищем от {value} {attr_in_category[0]['prefix']} 👀\n"
    
    elif current_state.split(":")[1] == 'max':
        attr_in_data[0]['max'] = value
        text = f"Ищем до {value} {attr_in_category[0]['prefix']} 👀\n"
    search_data.attrs = [i for i in search_data.attrs if i['name'] != attr_name.string] + attr_in_data if search_data.attrs else attr_in_data
    await search_data.save()
    await state.finish()

    return await message.answer(text=text + "Что бы продолжить нажмите кнопку ниже 👇", 
                                reply_markup=await back_keyboard(callback=f"digit_filter:{attr_name.id}:{user_data['category_id']}", 
                                                                                              text="К настройкам поиска 🔎"))
    
    


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'cds', state=DigitAttr)
async def cancel_state(call: CallbackQuery, state: FSMContext):
    '''Позоволяет скинуть состояние и вернуться к настройкам'''
    await state.finish()
    call.data = ":".join(call.data.split(':')[1:])
    return await digit_filter_handler(call)