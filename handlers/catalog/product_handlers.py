from typing import Awaitable
from keyboards.inline.back_keyboard import back_keyboard
from loader import dp
from aiogram.types import CallbackQuery 
from aiogram.types.input_media import InputMediaPhoto
from utils.misc import api 
from data.config import API_URL
from keyboards.inline import product_keyboard
from models.models import FavoriteProduct, UploadPhoto, User, UserCart
from tortoise.queryset import Q

# call = "product:{product_id}:{"desc" or "attr"}:{photo_index}:{count}"
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'product')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'list_photo')
async def product_handler(call: CallbackQuery):
    product = await api.get_product_info(call.data.split(':')[1])
    user = await User.get(tg_id=call.message.chat.id)
    cart = await user.cart.filter(product_id=product['id'])
    favorite = await user.favorites.filter(product_id=product['id'])
    if product['quantity'] <= 0 or product['is_active'] is False:
        await call.message.delete()
        return await call.message.answer(text="К сожалению данный товар не доступен.", reply_markup=await back_keyboard(callback=f"category:{product['category']['id']}"))

    photo = product["photo"]
    data = call.data.split(':')
    photo_indx = int(data[3])
    text = f"<b>Название</b> - {product['name']}\n\n"  \
           f"<b>Цена - </b>"
    if product['discount']:
        text += f"<s>{product['price']}</s> {product['price'] - product['discount']} руб.\n\n"
    else:
        text += f"{product['price']} руб.\n\n"
    text += f"<b>Кол-во товара</b> - {product['quantity']} шт.\n\n"
    if data[2] == 'desc':
        text += f"<b>Описание</b> - {product['description']}"
    elif data[2] == 'attr':
        print(product["attributes"])
    keyboard = await product_keyboard(photo_index=photo_indx,
                                      photo_list=product['photo'],
                                      desc_or_attr=data[2],
                                      category_id=product['category']['id'],
                                      cart=cart,
                                      favorite=favorite,
                                      quantity_max=product["quantity"],
                                      product_id=product['id'])
    
    url = "https://4926-178-155-4-127.ngrok.io/static/" + photo[photo_indx]

    photo_id = await UploadPhoto.get_or_none(path=photo[photo_indx])
    
    if not call.message.photo or call.data.split(':')[0] == "list_photo":
        await call.message.delete()
        if photo_id:
            await call.message.answer_photo(photo=photo_id.photo_id, caption=text, reply_markup=keyboard)
        else:
            response = await call.message.answer_photo(photo=url, caption=text, reply_markup=keyboard)
            await UploadPhoto.create(path=photo[photo_indx], photo_id=response.photo[-1].file_id,)
    else:
        await call.message.edit_caption(caption=text)
        await call.message.edit_reply_markup(keyboard)

# Переход из каталога в товар
# Смена фото
# remove_favorite
# add_f
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'remove_favorite')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'add_favorite')
async def add_favorite(call: CallbackQuery):
    user = await User.get(tg_id=call.message.chat.id)
    product_id = int(call.data.split(':')[1])
    if call.data.split(':')[0] == "add_favorite":
        await FavoriteProduct.create(user=user, product_id=product_id)
        await call.answer(text="Успешно добавлено в избранное!")
    elif call.data.split(':')[0] == "remove_favorite":
        await user.favorites.filter(product_id=product_id).delete()
        await call.answer(text="Успешно удалено из избранного!")
    
    call.data = "product:" + ":".join(call.data.split(':')[1:])
    return await product_handler(call)
    # product_id = int(call.data.split(':')[1])


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'add_in_cart')
async def add_in_cart_handler(call: CallbackQuery):
    user = await User.get(tg_id=call.message.chat.id)
    product_id = int(call.data.split(':')[1])
    if not await user.cart.filter(product_id=product_id):
        await UserCart.create(user=user, product_id=product_id)
        await call.answer(text="Товар добавлен в корзину!")
    
    call.data = "product:" + ":".join(call.data.split(':')[1:])
    return await product_handler(call)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'minus_c')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'plus_c')
async def control_quantity(call: CallbackQuery):
    product_id = int(call.data.split(':')[1])
    callback_for_product_handler = "product:" + ":".join(call.data.split(':')[1:])
    product = await api.get_product_info(product_id)
    quantity_max = product["quantity"]
    cart_item = await UserCart.get(Q(user__tg_id=call.message.chat.id) & Q(product_id=product_id))
    if call.data.split(':')[0] == 'plus_c':
        if cart_item.quantity < quantity_max:
            cart_item.quantity += 1
            await cart_item.save()
        else:
            await call.answer(text=f"Максимальное кол-во товара {quantity_max} шт.")
    if call.data.split(':')[0] == 'minus_c':
        cart_item.quantity -= 1
        if cart_item.quantity <= 0:
            await cart_item.delete()
        else:
            await cart_item.save()

    call.data = callback_for_product_handler
    return await product_handler(call)
        
        
    
    
    