from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup

async def filtering_products_keyboard(category_id: int,min_price:int, max_price: int, filters: list):
    keyboard = InlineKeyboardMarkup()
    min_price_button = InlineKeyboardButton(text=f"Мин. цена: {min_price} руб.", callback_data=f"min_price:{category_id}")
    max_price_button = InlineKeyboardButton(text=f"Макс. цена: {max_price} руб.", callback_data=f"max_price:{category_id}")
    keyboard.add(min_price_button, max_price_button)

    for item in filters:
        callback = None
        if type(item['value']) == bool:
            callback = f"bool_filter:{item['name']}:{category_id}"
            # keyboard.add(InlineKeyboardButton(text=item['name'], callback_data="bool_filter" + callback))
        elif type(item['value']) in [int, float]:
            callback = f"digit_filter:{item['name']}:{category_id}"
        elif type(item['value']) == str:
            callback = f"str_filter:{item['name']}:{category_id}"
        elif type(item['value']) == list:
            callback = f"list_filter:{item['name']}:{category_id}"
        if callback:
            keyboard.add(InlineKeyboardButton(text=item['name'], callback_data=callback))
                                                                             # all_products_page:{page}:{product['category_id']}"
    keyboard.add(InlineKeyboardButton(text=f"Найти товары 🔎", callback_data=f"filtering_catalog:1:{category_id}"))
    keyboard.add(InlineKeyboardButton(text=f"Фильтры по умолчанию", callback_data=f"delete_filter:{category_id}"))
    keyboard.add(InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"category:{category_id}"))
    return keyboard
    # keyboard.add(InlineKeyboardButton())


async def boolean_keyboard(attr_name: str, category_id: int, value: bool = None):
    keyboard = InlineKeyboardMarkup()
    print(value)
    keyboard.add(InlineKeyboardButton(text="Да  ✅" if value is True else "Да", 
                                     callback_data=f"bool_true:{attr_name}:{category_id}"))

    keyboard.add(InlineKeyboardButton(text="Нет  ✅" if value is False else "Нет", 
                                      callback_data=f"bool_false:{attr_name}:{category_id}"))

    keyboard.add(InlineKeyboardButton(text="Неважно ✅" if value in [None, []] else "Неважно", 
                                      callback_data=f"bool_none:{attr_name}:{category_id}"))

    keyboard.add(InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"settings_filters:{category_id}"))

    return keyboard

async def string_keyboard(attr_name: str, category_id: int, distinct_value_list: list, list_or_str: str, user_values: list = []):
    '''Сюда идет еще list_filter'''
    keyboard = InlineKeyboardMarkup()
    for value in distinct_value_list:
        if [i for i in user_values if i == value]:
            kwargs = {
                'text': f"{value} ✅",
                'callback_data': f"{list_or_str}_remove:{attr_name}:{value}:{category_id}"
                }
        else:
            kwargs = {
                'text': value,
                'callback_data': f"{list_or_str}_append:{attr_name}:{value}:{category_id}"
                }
        
        keyboard.add(InlineKeyboardButton(**kwargs))
    
    keyboard.add(InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"settings_filters:{category_id}"))
    return keyboard


# {attr_name}:{category_id}
async def digit_keyboard(attr_name: str, category_id: int, user_value : dict, prefix: str = None):
    keyboard = InlineKeyboardMarkup()
    prefix = '' if prefix is None else prefix
    min_price_button = InlineKeyboardButton(text=f"Мин.: {user_value['min']} {prefix}", callback_data=f"min_attr:{attr_name}:{category_id}")
    max_price_button = InlineKeyboardButton(text=f"Макс.: {user_value['max']} {prefix}", callback_data=f"max_attr:{attr_name}:{category_id}")
    reset_digit = InlineKeyboardButton(text=f"Диапазон по умолчанию", callback_data=f"reset_digit:{attr_name}:{category_id}")
    keyboard.add(min_price_button, max_price_button)
    keyboard.add(reset_digit)
    keyboard.add(InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"settings_filters:{category_id}"))
    return keyboard