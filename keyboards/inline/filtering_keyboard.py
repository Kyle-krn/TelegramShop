from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from models.models import ArchiveStringAttrs


async def filtering_products_keyboard(
    category_id: int, min_price: int, max_price: int, filters: list, user_data_attrs: list
):
    keyboard = InlineKeyboardMarkup()
    min_price_button = InlineKeyboardButton(
        text=f"Мин. цена: {min_price} руб.", callback_data=f"min_price:{category_id}"
    )
    max_price_button = InlineKeyboardButton(
        text=f"Макс. цена: {max_price} руб.", callback_data=f"max_price:{category_id}"
    )
    keyboard.add(min_price_button, max_price_button)

    for item in filters:
        attr_name_archive = await ArchiveStringAttrs.get_or_create(string=item["name"])
        callback = None
        if type(item["value"]) == bool:
            callback = f"bool_filter:{attr_name_archive[0].id}:{category_id}"
        elif type(item["value"]) in [int, float]:
            callback = f"digit_filter:{attr_name_archive[0].id}:{category_id}"
        elif type(item["value"]) in [str, list]:
            callback = f"str_filter:{attr_name_archive[0].id}:{category_id}"

        if callback:
            user_attr = [i for i in user_data_attrs if i["name"] == item["name"]] if user_data_attrs else []
            text = item["name"] if len(user_attr) == 0 else f"{item['name']} ✅"
            keyboard.add(InlineKeyboardButton(text=text, callback_data=callback))

    keyboard.add(InlineKeyboardButton(text=f"Найти товары 🔎", callback_data=f"filtering_catalog:1:{category_id}"))
    keyboard.add(InlineKeyboardButton(text=f"Фильтры по умолчанию", callback_data=f"delete_filter:{category_id}"))
    keyboard.add(InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"category:{category_id}"))
    return keyboard
    # keyboard.add(InlineKeyboardButton())


async def boolean_keyboard(attr_name_id: int, category_id: int, value: bool = None):
    keyboard = InlineKeyboardMarkup()
    # attr_name_archive = await ArchiveStringAttrs.get_or_create(string=attr_name)

    keyboard.add(
        InlineKeyboardButton(
            text="Да  ✅" if value is True else "Да", callback_data=f"bool_true:{attr_name_id}:{category_id}"
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            text="Нет  ✅" if value is False else "Нет", callback_data=f"bool_false:{attr_name_id}:{category_id}"
        )
    )

    keyboard.add(
        InlineKeyboardButton(
            text="Неважно ✅" if value in [None, []] else "Неважно",
            callback_data=f"bool_none:{attr_name_id}:{category_id}",
        )
    )

    keyboard.add(InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"settings_filters:{category_id}"))

    return keyboard


async def string_keyboard(attr_name_id: int, category_id: int, distinct_value_list: list, user_values: list = []):
    """Сюда идет еще list_filter"""
    keyboard = InlineKeyboardMarkup()
    for value in distinct_value_list:
        value_archive = await ArchiveStringAttrs.get_or_create(string=value)
        if [i for i in user_values if i == value]:
            kwargs = {
                "text": f"{value} ✅",
                "callback_data": f"sf_r:{attr_name_id}:{value_archive[0].id}:{category_id}",
            }  # sf_r - strfilter_remove
        else:
            kwargs = {
                "text": value,
                "callback_data": f"sf_a:{attr_name_id}:{value_archive[0].id}:{category_id}",
            }  # sf_a - strfilter_append

        keyboard.add(InlineKeyboardButton(**kwargs))

    keyboard.add(InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"settings_filters:{category_id}"))
    return keyboard


# {attr_name}:{category_id}
async def digit_keyboard(attr_name_id: int, category_id: int, user_value: dict, prefix: str = None):
    keyboard = InlineKeyboardMarkup()
    prefix = "" if prefix is None else prefix
    min_price_button = InlineKeyboardButton(
        text=f"Мин.: {user_value['min']} {prefix}", callback_data=f"min_attr:{attr_name_id}:{category_id}"
    )
    max_price_button = InlineKeyboardButton(
        text=f"Макс.: {user_value['max']} {prefix}", callback_data=f"max_attr:{attr_name_id}:{category_id}"
    )
    reset_digit = InlineKeyboardButton(
        text=f"Диапазон по умолчанию", callback_data=f"reset_digit:{attr_name_id}:{category_id}"
    )
    keyboard.add(min_price_button, max_price_button)
    keyboard.add(reset_digit)
    keyboard.add(InlineKeyboardButton(text=f"🔙 Назад", callback_data=f"settings_filters:{category_id}"))
    return keyboard
