from keyboards.inline.back_keyboard import back_keyboard
from loader import dp
from aiogram.types import CallbackQuery 
from utils.misc import api 
from data.config import API_URL
from keyboards.inline import product_keyboard
from models.models import FavoriteProduct, SearchUserData, UploadPhoto, User, UserCart
from tortoise.queryset import Q
from datetime import datetime, timedelta

@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'product')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'list_photo')
async def product_handler(call: CallbackQuery):
    '''Представление товара'''
    # if 
    product = await api.get_product_info(call.data.split(':')[1])
    print(product, "\n")
    if 'detail' in product:
        return await call.message.edit_text(text='<b>К сожалению товар был удален.</b>')
    user = await User.get(tg_id=call.message.chat.id)
    cart = await user.cart.filter(product_id=product['id'])

    favorite = await user.favorites.filter(product_id=product['id'])
    if product['quantity'] <= 0 or product['is_active'] is False:
        '''Не даем доступ юзерам к товару который нельзя купить'''
        await call.message.delete()
        if len(cart) > 0:
            await cart[0].delete()
        return await call.message.answer(text="К сожалению данный товар не доступен.", 
                                             reply_markup=await back_keyboard(callback=f"category:{product['category_id']}"))
    if len(cart) > 0 and cart[0].quantity > product['quantity']:
        cart[0].quantity = product['quantity']
        await call.answer(f"Максимальное кол-во товара - {product['quantity']} шт.")
        await cart[0].save()
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
        for item in product["attributes"]:
            if item['value'] is not None:
                if item['value'] is True:
                    item['value'] = "✅"
                elif item['value'] is False:
                    item['value'] = "❌"
                if isinstance(item['value'], list):
                    text += f"<b>{item['name']}</b> - {', '.join([i for i in item['value']])}\n"  
                else:
                    text += f"<b>{item['name']}</b> - {item['value']} {item['prefix']}\n"
    catalog_page = int(data[4]) # Для кнопки назад, что бы возвращало нужную страницу
    catalog_or_cart = data[5]
    search_data = await SearchUserData.get_or_none(user=user, category_id=product['category_id'])
    if search_data:
        '''Если true то идет поиск с фильтрами, для корректного возвращения на фильтрованный queryset'''
        search_bool = search_data.search
    else:
        search_bool = False
    keyboard = await product_keyboard(photo_index=photo_indx,
                                      photo_list=product['photo'],
                                      desc_or_attr=data[2],
                                      category_id=product['category_id'],
                                      cart=cart,
                                      favorite=favorite,
                                      quantity_max=product["quantity"],
                                      product_id=product['id'],
                                      page=catalog_page,
                                      search_user=search_bool,
                                      catalog_or_cart = catalog_or_cart)
    
    url = f"{API_URL}/static/" + photo[photo_indx]

    photo_id = await UploadPhoto.get_or_none(path=photo[photo_indx])
    
    if not call.message.photo or call.data.split(':')[0] == "list_photo":
        '''Для того что бы сообщения которые можно изменить изменялись, остальные удаляются и отправляются новыми'''
        await call.message.delete()
        if photo_id:
            '''Если мы уже отправляли это фото, у нас есть его id, мы передаем фото по нему'''
            await call.message.answer_photo(photo=photo_id.photo_id, caption=text, reply_markup=keyboard)
        else:
            '''Если не отправляли то отправляем и записываем photo_id'''
            response = await call.message.answer_photo(photo=url, caption=text, reply_markup=keyboard)
            await UploadPhoto.create(path=photo[photo_indx], photo_id=response.photo[-1].file_id,)
    else:
        await call.message.edit_caption(caption=text)
        await call.message.edit_reply_markup(keyboard)


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'remove_favorite')
@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'add_favorite')
async def add_favorite(call: CallbackQuery):
    '''Добавить/Удалить из избранного'''
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


@dp.callback_query_handler(lambda call: call.data.split(':')[0] == 'add_in_cart')
async def add_in_cart_handler(call: CallbackQuery):
    '''Первое добавление товара в корзину'''
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
    '''Упавление кол-во товара в корзине'''
    product_id = int(call.data.split(':')[1])
    callback_for_product_handler = "product:" + ":".join(call.data.split(':')[1:])
    product = await api.get_product_info(product_id)
    if 'detail' in product:
        return await call.message.edit_text(text='<b>К сожалению товар был удален.</b>')
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
    