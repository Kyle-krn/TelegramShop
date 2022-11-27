from keyboards.inline.catalog import product_catalog_keyboard
from loader import dp
from aiogram.types import CallbackQuery, Message
from utils.misc import api
from keyboards.inline import filtering_products_keyboard, back_keyboard
from models.models import SearchUserData, User
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext
from tortoise.queryset import Q


class Price(StatesGroup):
    """Состояния для введения суммы стоймости"""

    min_price = State()
    max_price = State()


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "filtering_catalog")
@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "back_filters_category")
async def filtering_catalog_handler(call: CallbackQuery):
    """Отдает список отфильтрованных товаров в категории"""
    category_id = int(call.data.split(":")[2])
    search_data = await SearchUserData.get(Q(user__tg_id=call.message.chat.id) & Q(category_id=category_id))
    search_data.search = True
    if search_data.attrs == []:
        search_data.attrs = None
    await search_data.save()
    data = {
        "min_price": float(search_data.min_price) if search_data.min_price else None,
        "max_price": float(search_data.max_price) if search_data.max_price else None,
        "attributes": search_data.attrs,
    }

    page = int(call.data.split(":")[1])
    limit = 5
    offset = (page - 1) * limit
    category = await api.get_category_light_info(category_id, parent_id=True)
    products = await api.get_products_queryset(category_id, body=data, offset=offset, limit=limit)
    max_page = (products["count"] // limit) + 1 if products["count"] % limit else products["count"] // limit
    reply_markup = await product_catalog_keyboard(
        products["products"],
        parent_id=category["parent_id"],
        category_id=category_id,
        page=page,
        max_page=max_page,
        filters=True,
    )
    text = "Выберите товар"
    if call.data.split(":")[0] == "back_filters_category":
        await call.message.delete()
        return await call.message.answer(text=text, reply_markup=reply_markup)
    return await call.message.edit_text(text=text, reply_markup=reply_markup)


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "settings_filters")
async def setting_filters_handler(call: CallbackQuery):
    """Настройки фильтров"""
    category = await api.get_category_light_info(category_id=call.data.split(":")[1], filters=True, products=True)
    user = await User.get(tg_id=call.message.chat.id)
    search_data = await SearchUserData.get_or_create(user=user, category_id=category["id"])
    search_data = search_data[0]
    amount_list = [i["price"] for i in category["products"]]
    try:
        kwargs = {
            "category_id": category["id"],
            "min_price": min(amount_list) if not search_data.min_price else search_data.min_price,
            "max_price": max(amount_list) if not search_data.max_price else search_data.max_price,
            "filters": category["filters"],
            "user_data_attrs": search_data.attrs,
        }
    except ValueError:
        return await call.message.edit_text("Произошла ошибка.")
    keyboard = await filtering_products_keyboard(**kwargs)
    await call.message.delete()
    await call.message.answer(text="Вы можете выбрать параметры ниже", reply_markup=keyboard)


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "min_price")
@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "max_price")
async def min_price_handler(call: CallbackQuery):
    """Указать мин/макс цену товара"""
    if call.data.split(":")[0] == "min_price":
        await Price.min_price.set()
        text = "<b>Введите минимальную цену:</b>"
    else:
        await Price.max_price.set()
        text = "<b>Введите максимальную цену:</b>"
    state = dp.get_current().current_state()
    await state.update_data(category_id=int(call.data.split(":")[1]))
    await call.message.edit_text(
        text=text, reply_markup=await back_keyboard(callback=f"cancel_state_filtering:{call.data.split(':')[1]}")
    )


@dp.message_handler(state=Price)
async def process_price_invalid(message: Message, state: FSMContext):
    """Валидация введеных данных и если успешно то устанавливает новые значения в фильтре"""
    user_data = await state.get_data()
    keyboard = await back_keyboard(callback=f"cancel_state_filtering:{user_data['category_id']}")
    try:
        price = float(message.text)
    except (TypeError, ValueError):
        return await message.reply("Введите число.", reply_markup=keyboard)

    min_max = await api.get_min_max_for_category(category_id=user_data["category_id"])
    if price <= 0:
        return await message.reply("Цена не может быть отрицательной или нулем.", reply_markup=keyboard)
    if (min_max["min_price"] <= price <= min_max["max_price"]) is False:
        return await message.reply(
            f"От {min_max['min_price']} руб. до  {min_max['max_price']} руб.", reply_markup=keyboard
        )
    search_data = await SearchUserData.get(Q(user__tg_id=message.chat.id) & Q(category_id=user_data["category_id"]))

    current_state = await state.get_state()
    if current_state.split(":")[1] == "min_price":
        search_data.min_price = price
        text = f"Ищем цены от {'%.2f' % price} 👀\n"
    elif current_state.split(":")[1] == "max_price":
        search_data.max_price = price
        text = f"Ищем цены до {'%.2f' % price} 👀\n"
    await search_data.save()
    await state.finish()
    return await message.answer(
        text + "Что бы продолжить нажмите кнопку ниже 👇",
        reply_markup=await back_keyboard(
            callback=f"settings_filters:{user_data['category_id']}", text="К настройкам поиска 🔎"
        ),
    )


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "delete_filter")
async def delete_category_filter(call: CallbackQuery):
    """Обнуляет фильтры в выбранной категории"""
    category_id = int(call.data.split(":")[1])
    search_data = await SearchUserData.get(Q(user__tg_id=call.message.chat.id) & Q(category_id=category_id))
    await search_data.delete()
    await call.answer("Настройки поиска успешно изменены.")
    call.data = f"settings_filters:{category_id}"
    return await setting_filters_handler(call)


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "cancel_state_filtering", state=Price)
async def cancel_state(call: CallbackQuery, state: FSMContext):
    """Позоволяет скинуть состояние и не вводить данные"""
    await state.finish()
    call.data = f"settings_filters:{call.data.split(':')[1]}"
    return await setting_filters_handler(call)
