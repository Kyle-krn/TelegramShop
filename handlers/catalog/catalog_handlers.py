from email import message
from handlers import catalog
from loader import dp
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery
from models.models import User
from keyboards.inline import category_keyboard, start_catalog_keyboard, product_catalog_keyboard
from utils.misc import api
import pprint

pp = pprint.PrettyPrinter(indent=4)

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'main_category')
@dp.message_handler(Text(equals=["📙 Каталог"]))
async def start_catalog_handler(message: Message or CallbackQuery):
    # user = await User.get(tg_id=message.chat.id)
    categories = await api.get_main_category_info()
    # pp.pprint(categories)
    kwargs = {
        "text": "Выберите категорию" if categories else "К сожалению нет ни одной категории.",
        "reply_markup": await start_catalog_keyboard(categories) if categories else None
    }
    if isinstance(message, CallbackQuery):
        return await message.message.edit_text(**kwargs)
    return await message.answer(**kwargs)
    # return await message.answer(text="Выберите категорию", reply_markup=await start_catalog_keyboard(categories))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'back_category')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'category')
async def category_handler(call: CallbackQuery):
    category = await api.get_category_info(call.data.split(':')[1])
    # pp.pprint(category)
    # c = await api.get_category_info(6)
    if category["children"]:
        reply_markup = await category_keyboard(category)
        text = "Выберите категорию"
        # await call.message.edit_text(text="Выберите категорию", reply_markup=await category_keyboard(category))
    elif category["products"]:
        reply_markup = await product_catalog_keyboard(category)
        text = "Выберите товар"
        # await call.message.edit_text(text="Выберите товар", reply_markup=await product_catalog_keyboard(category))
    if call.data.split(':')[0] == 'category':
        await call.message.edit_text(text=text, reply_markup=reply_markup)
    else:
        await call.message.delete()
        await call.message.answer(text=text, reply_markup=reply_markup)

