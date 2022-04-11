from unicodedata import category
from loader import dp
from utils.misc import api
from aiogram.types import CallbackQuery
from models.models import SearchUserData
from keyboards.inline import boolean_keyboard
from aiogram.utils.exceptions import MessageNotModified
from tortoise.queryset import Q

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'bool_filter')
async def boolean_filter_handlers(call: CallbackQuery):
    name_attr = call.data.split(':')[1]
    category_id = int(call.data.split(':')[2])
    search_data = await SearchUserData.get(Q(user__tg_id=call.message.chat.id) & Q(category_id=category_id))
    # print(name_attr, category_id)
    category = await api.get_category_light_info(category_id=category_id, filters=True)
    attr_in_data = [i for i in search_data.attrs if i['name'] == name_attr] if search_data.attrs is not None else None
    if attr_in_data:
        attr_in_data = attr_in_data[0]['value']
    attr_in_category = [i for i in category['filters'] if i['name'] == name_attr]
    
    if len(attr_in_category) == 0:
        raise IndexError(f"Атрибут с таким именем не найден")
    if type(attr_in_category[0]['value']) != bool:
        raise TypeError(f"Вместо bool {type(attr_in_category)}")
    try:
        await call.message.edit_text(text=f"<b>{name_attr}</b>", reply_markup=await boolean_keyboard(attr_name=name_attr, 
                                                                                                                     value=attr_in_data,
                                                                                                                 category_id=category_id))
    except MessageNotModified:
        await call.answer()

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'bool_true')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'bool_false')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'bool_none')
async def bool_yes_handler(call: CallbackQuery):
    category_id = int(call.data.split(':')[2])
    search_data = await SearchUserData.get(Q(user__tg_id=call.message.chat.id) & Q(category_id=category_id))
    name_attr = call.data.split(':')[1]
    attr_in_data = [i for i in search_data.attrs if i['name'] == name_attr] if search_data.attrs is not None else None
    if call.data.split(':')[0] == 'bool_true':
        value = True
    elif call.data.split(':')[0] == 'bool_false':
        value = False
    elif call.data.split(':')[0] == 'bool_none':
        search_data.attrs = [i for i in search_data.attrs if i['name'] != name_attr] if search_data.attrs is not None else None
        await search_data.save()
        call.data = 'bool_filter:' + ":".join(call.data.split(":")[1:])
        return await boolean_filter_handlers(call)
    
    if attr_in_data is None:

        search_data.attrs = [{'name': name_attr, 'value': value, 'min': None, 'max': None}]
        # await 
    if attr_in_data == []:
        search_data.attrs.append({'name': name_attr, 'value': value, 'min': None, 'max': None})
    else:
        # value = attr_in_data[0]['value']
        attrs = [{'name': name_attr, 'value': value, 'min': None, 'max': None}] + [i for i in search_data.attrs if i['name'] != name_attr]
        search_data.attrs = attrs
    await search_data.save()
    call.data = 'bool_filter:' + ":".join(call.data.split(":")[1:])
    return await boolean_filter_handlers(call)
        # attrs = {'name': name_attr, 'value': True, 'min': None, 'max': None} 
        




    



