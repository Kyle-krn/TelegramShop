import re
from loader import dp
from aiogram.types import CallbackQuery
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.types import Message
from models.models import Profile
from aiogram.dispatcher import FSMContext
from keyboards.inline import back_keyboard, successful_input_data_keyboard
from handlers.cart.cart_handlers import delivery_handler
from utils.misc import delivery_api

class ProfileState(StatesGroup):
    first_name = State()
    last_name = State()
    phone_number = State()
    postcode = State()
    city = State()
    address = State()


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'profile')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'profile_in_cart')
async def change_profile_handler(call: CallbackQuery):
    service = call.data.split(':')[1]
    value = call.data.split(':')[2]

        
    keyboard = await back_keyboard(callback=f'cancel_profile_state:{call.data.split(":")[0]}:{service}')
    if value == 'first_name':
        await ProfileState.first_name.set()
        await call.message.edit_text('<b>Введите ваше имя:</b>', reply_markup=keyboard)
    elif value == 'last_name':
        await ProfileState.last_name.set()
        await call.message.edit_text('<b>Введите вашу фамилию:</b>', reply_markup=keyboard)
    elif value == 'phone_number':
        await ProfileState.phone_number.set()
        await call.message.edit_text('<b>Введите ваш номер телефона в формате 79004564312:</b>', reply_markup=keyboard)
    elif value == 'postcode':
        await ProfileState.postcode.set()
        await call.message.edit_text('<b>Введите ваш почтовый идекс (6 цифр):</b>', reply_markup=keyboard)
    elif value == 'city':
        await ProfileState.city.set()
        await call.message.edit_text('<b>Введите ваш город:</b>', reply_markup=keyboard)
    elif value == 'address':
        await ProfileState.address.set()
        await call.message.edit_text('<b>Введите ваш адрес:</b>', reply_markup=keyboard)
    state = dp.get_current().current_state()
    if call.data.split(':')[0] == 'profile_in_cart':
        cart = True
    else:
        cart = False
    await state.update_data(cart=cart, service=service)


@dp.message_handler(state=ProfileState.first_name)
@dp.message_handler(state=ProfileState.last_name)
async def check_value_first_name(message: Message, state: FSMContext):
    current_state = await state.get_state()
    user_data = await state.get_data()
    back_callback = "profile_in_cart" if user_data['cart'] else "profile"
    keyboard = await back_keyboard(callback=f'cancel_profile_state:{back_callback}:{user_data["service"]}')
    if len(message.text.split(' ')) > 1:
        text = "<b>Введите имя без пробелов</b>" if current_state.split(':')[1] == 'first_name' else "<b>Введите фамилию без пробелов</b>"
        return await message.answer(text, reply_markup=keyboard)
    name = message.text
    for s in name:
        if s.isdigit():
            text = "<b>Имя не может содержать цифры</b>" if current_state.split(':')[1] == 'first_name' else "<b>Фамилия не может содержать цифры</b>"
            return await message.answer(text, reply_markup=keyboard)
    profile = await Profile.get(user__tg_id=message.chat.id)
    if current_state.split(':')[1] == 'first_name':
        profile.first_name = name.capitalize()
    if current_state.split(':')[1] == 'last_name':
        profile.last_name = name.capitalize()
    await profile.save()
    await state.finish()
    text = "Имя успешно изменено!"  if current_state.split(':')[1] == 'first_name' else "Фамилия успешно изменена!"
    return await message.answer(text + '\nНажмите кнопку ниже что бы продолжить ⬇️', 
                                reply_markup=await successful_input_data_keyboard(user_data['cart'], service=user_data['service']))



@dp.message_handler(state=ProfileState.phone_number)
async def check_value_phone_number(message: Message, state: FSMContext):
    valid_phone = re.search(r'^((8|\+7)[\- ]?)?(\(?\d{3}\)?[\- ]?)?[\d\- ]{7,10}$', message.text)
    user_data = await state.get_data()
    back_callback = "profile_in_cart" if user_data['cart'] else "profile"
    keyboard = await back_keyboard(callback=f'cancel_profile_state:{back_callback}:{user_data["service"]}')
    if not valid_phone:
        return await message.answer('Введите корректный номер телефона', reply_markup=keyboard)
    profile  = await Profile.get(user__tg_id=message.chat.id)
    profile.phone_number = valid_phone[0]
    await profile.save()
    await state.finish()
    return await message.answer('Номер телефона успешно изменен!\nНажмите кнопку ниже что бы продолжить ⬇️', 
                                reply_markup=await successful_input_data_keyboard(user_data['cart'], service=user_data['service']))


@dp.message_handler(state=ProfileState.postcode)
async def check_value_postcode(message: Message, state: FSMContext):
    user_data = await state.get_data()
    back_callback = "profile_in_cart" if user_data['cart'] else "profile"
    keyboard = await back_keyboard(callback=f'cancel_profile_state:{back_callback}:{user_data["service"]}')
    if message.text.isdigit() is False or len(message.text) != 6:
        return await message.answer('<b>Почтовый индекс состоит из 6 цифр.</b>', reply_markup=keyboard)
    postcode = int(message.text)
    resp = await delivery_api.pochta_rf(postcode=postcode, weight=1)
    if 'detail' in resp:
        return await message.answer(resp['detail'], reply_markup=keyboard)
    # if resp.status == 200:
    # print(await resp.json())
    # Валидация индекса нужна
    profile = await Profile.get(user__tg_id=message.chat.id)
    profile.postcode = postcode
    await profile.save()
    await state.finish()
    return await message.answer('Почтовый индекс успешно изменен!\nНажмите кнопку ниже что бы продолжить ⬇️', 
                                reply_markup=await successful_input_data_keyboard(user_data['cart'], service=user_data['service']))


@dp.message_handler(state=ProfileState.city)
async def check_value_city(message: Message, state: FSMContext):
    user_data = await state.get_data()
    back_callback = "profile_in_cart" if user_data['cart'] else "profile"
    keyboard = await back_keyboard(callback=f'cancel_profile_state:{back_callback}:{user_data["service"]}')
    city = message.text
    # Здесь можно сделать валидацию города через Dadata
    profile = await Profile.get(user__tg_id=message.chat.id)
    profile.city = city
    await profile.save()
    await state.finish()
    return await message.answer('Город успешно изменен!\nНажмите кнопку ниже что бы продолжить ⬇️', 
                                reply_markup=await successful_input_data_keyboard(user_data['cart'], service=user_data['service']))


@dp.message_handler(state=ProfileState.address)
async def check_value_address(message: Message, state: FSMContext):
    user_data = await state.get_data()
    back_callback = "profile_in_cart" if user_data['cart'] else "profile"
    keyboard = await back_keyboard(callback=f'cancel_profile_state:{back_callback}:{user_data["service"]}')
    address = message.text
    # Здесь можно сделать валидацию города через Dadata
    profile = await Profile.get(user__tg_id=message.chat.id)
    profile.address = address
    await profile.save()
    await state.finish()
    return await message.answer('Адрес успешно изменен!\nНажмите кнопку ниже что бы продолжить ⬇️', 
                                reply_markup=await successful_input_data_keyboard(user_data['cart'], service=user_data['service']))


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'cancel_profile_state', state=ProfileState)
async def cancel_state(call: CallbackQuery, state: FSMContext):
    '''Позоволяет скинуть состояние и вернуться к настройкам'''
    await state.finish()
    if call.data.split(':')[1] == 'profile_in_cart':
        service = call.data.split(':')[2]
        call.data = f'delivery:{service}'
        return await delivery_handler(call)
    # else:
    #     call.data = 'profile_main:'
    