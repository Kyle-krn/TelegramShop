from loader import dp
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from models.models import SearchUserData
from keyboards.inline import category_keyboard, start_catalog_keyboard, product_catalog_keyboard
from utils.misc import api


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "main_category")
@dp.message_handler(Text(equals=["📙 Каталог"]))
async def start_catalog_handler(message: Message or CallbackQuery):
    """Главные категории"""
    categories = await api.get_main_category_info()
    kwargs = {
        "text": "Выберите категорию" if categories else "К сожалению нет ни одной категории.",
        "reply_markup": await start_catalog_keyboard(categories) if categories else None,
    }
    if isinstance(message, CallbackQuery):
        return await message.message.edit_text(**kwargs)
    return await message.answer(**kwargs)


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "category")
async def category_handler(call: CallbackQuery):
    """Категория"""
    category = await api.get_category_light_info(
        call.data.split(":")[1], children=True, products_count=True, parent_id=True
    )
    search_data = await SearchUserData.get_or_none(user__tg_id=call.message.chat.id, category_id=category["id"])
    if search_data:
        search_data.search = False
        await search_data.save()
    if category["children"]:
        """Если у категории есть подкатегории"""
        reply_markup = await category_keyboard(category)
        text = "Выберите категорию"
    elif category["products_count"] > 0:
        """Если у категории есть товар"""
        offset = 0
        limit = 5
        products = await api.get_products_queryset(category["id"], body={}, offset=offset, limit=limit)
        max_page = (products["count"] // limit) + 1 if products["count"] % limit else products["count"] // limit
        reply_markup = await product_catalog_keyboard(
            products["products"], parent_id=category["parent_id"], category_id=category["id"], page=1, max_page=max_page
        )
        text = "Выберите товар"
    else:
        text = "У данной категории отсутствуют товары и подкатегории"
        reply_markup = await category_keyboard(category)
    if call.data.split(":")[0] == "category":
        await call.message.edit_text(text=text, reply_markup=reply_markup)
    else:
        await call.message.delete()
        await call.message.answer(text=text, reply_markup=reply_markup)


@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "all_products_page")
@dp.callback_query_handler(lambda call: call.data.split(":")[0] == "back_category")
async def products_pagination(call: CallbackQuery):
    """Пагинация товаров"""
    category_id = int(call.data.split(":")[2])
    page = int(call.data.split(":")[1])
    limit = 5
    offset = (page - 1) * limit
    category = await api.get_category_light_info(category_id, parent_id=True)
    products = await api.get_products_queryset(category_id, body={}, offset=offset, limit=limit)

    max_page = (products["count"] // limit) + 1 if products["count"] % limit else products["count"] // limit
    reply_markup = await product_catalog_keyboard(
        products["products"], parent_id=category["parent_id"], category_id=category_id, page=page, max_page=max_page
    )
    text = "Выберите товар"
    if call.data.split(":")[0] == "back_category":
        await call.message.delete()
        return await call.message.answer(text=text, reply_markup=reply_markup)
    return await call.message.edit_text(text=text, reply_markup=reply_markup)
