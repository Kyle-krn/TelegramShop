from aiogram import types
from aiogram.dispatcher.filters.builtin import CommandStart
from models.models import Profile, User, SearchUserData
from loader import dp
from utils.misc import api
from keyboards.reply import main_keyborad


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    user = await User.filter(tg_id=message.chat.id)
    if not user:
        user = await User.create(tg_id=message.chat.id, username=message.chat.username)
        await Profile.create(user=user)
        # await SearchUserData.create(user=user)
    await message.answer(text=f"Привет, {message.from_user.full_name}!", reply_markup=await main_keyborad())
