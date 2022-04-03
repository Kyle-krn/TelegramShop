from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart

from loader import dp
from utils.misc import api

@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    await api.get_category_info(1)
    await message.answer(f"Привет, {message.from_user.full_name}!")
