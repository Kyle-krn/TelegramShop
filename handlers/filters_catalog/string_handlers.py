from loader import dp
from aiogram.types import CallbackQuery
from models.models import SearchUserData
from utils.misc import api
from keyboards.inline import string_keyboard
from tortoise.queryset import Q

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'str_filter')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'list_filter')
async def string_filter_handler(call: CallbackQuery):
    name_attr = call.data.split(':')[1]
    category_id = int(call.data.split(':')[2])
    search_data = await SearchUserData.get(Q(user__tg_id=call.message.chat.id) & Q(category_id=category_id))
    category = await api.get_category_light_info(category_id=category_id, filters=True)
    attr_in_data = [i for i in search_data.attrs if i['name'] == name_attr] if search_data.attrs is not None else []
    if attr_in_data:
        attr_in_data = attr_in_data[0]['value']
    attr_in_category = [i for i in category['filters'] if i['name'] == name_attr]
    if len(attr_in_category) == 0:
        raise IndexError(f"Атрибут с таким именем не найден")
    # if type(attr_in_category) != list:
    #     raise TypeError(f"Вместо list {type(attr_in_category)}")
    if attr_in_data:
        for item in attr_in_data:
            if type(item) != str:
                raise TypeError(f"Вместо str {type(item)}")
    
    if call.data.split(':')[0] == 'str_filter':
        list_or_str = 'str'
    elif call.data.split(':')[0] == 'list_filter':
        list_or_str = 'str'
    distinct_values = await api.get_distinct_string_value(category_id=category_id, attr_name=name_attr)
    keyboard = await string_keyboard(attr_name=name_attr, category_id=category_id, distinct_value_list=distinct_values, list_or_str=list_or_str, user_values=attr_in_data)
    await call.message.edit_text(text="Выберите параметр ⬇", reply_markup=keyboard)



@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'str_append')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'str_remove')
async def control_string_filter(call: CallbackQuery):
    search_data = await SearchUserData.get(user__tg_id=call.message.chat.id)
    name_attr = call.data.split(':')[1]
    value = call.data.split(':')[2]
    category_id = int(call.data.split(':')[3])
    attr_in_data = [i for i in search_data.attrs if i['name'] == name_attr] if search_data.attrs is not None else None
    if attr_in_data is None:
        search_data.attrs = [{'name': name_attr, 'value': [value], 'min': None, 'max': None}]
    elif attr_in_data == []:
        search_data.attrs.append({'name': name_attr, 'value': [value], 'min': None, 'max': None})
    else:
        # attr_in_data = attr_in_data
        if call.data.split(':')[0] == 'str_append':
            attr_in_data[0]['value'].append(value)
        elif call.data.split(':')[0] == 'str_remove':
            attr_in_data[0]['value'].remove(value)
            if len(attr_in_data[0]['value']) == 0:
                attr_in_data = None
        search_data.attrs = [i for i in search_data.attrs if i['name'] != name_attr] 
        if attr_in_data:
            search_data.attrs += attr_in_data
    await search_data.save()
    call.data = f'str_filter:{name_attr}:{category_id}'
    return await string_filter_handler(call)
