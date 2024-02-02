import os

from database.models import User, Check, Product, Media


async def get_or_create_user(user: dict, lang: str = None):
    print(user)
    user_qs = await User.filter(tg_id=user.get('id'))
    if user_qs:
        user_db = user_qs[0]
        if lang:
            user_db.language = lang
            await user_db.save()
        return user_db

    user = await User.create(
        tg_id=user.get('id'),
        first_name=user.get('first_name'),
        last_name=user.get('last_name'),
        username=user.get('username'),
        language=lang
    )
    return user

async def create_user_from_contact(update):
    user = update.message.contact.to_dict()
    sender_user = update.message.from_user.to_dict()
    user = await User.create(
        tg_id=user.get('user_id'),
        first_name=user.get('first_name'),
        last_name=user.get('last_name'),
        username=sender_user.get('username'),
        phone_number=user.get('phone_number')
    )
    return user


async def set_user_first_name(update):
    user_db = await get_user(update)
    user_db.first_name = update.message.text
    await user_db.save()
    return user_db


async def set_user_phone(update):
    user_db = await get_user(update)
    user_db.phone_number = update.message.text
    await user_db.save()


async def get_user(update):
    sender_user = update.message.from_user.to_dict()
    user_db = await User.filter(tg_id=sender_user.get('id')).first()
    return user_db


async def update_from_contact(update):
    user_db = await get_user(update)
    user_contact = update.message.contact.to_dict()

    user_db.first_name = user_contact.get('first_name')
    user_db.last_name = user_contact.get('last_name')
    user_db.phone_number = user_contact.get('phone_number')

    await user_db.save()

    return user_db


async def is_check_exists(check_id: str):
    return await Check.filter(lg=check_id).exists()


async def create_product(check: Check, product: dict):
    await Product.create(
        bill=check,
        **product
    )


async def create_media(photo_path: str):
    return await Media.create(
        path=photo_path
    )


async def delete_media(media: Media):
    try:
        os.remove(media.path)
        await media.delete()
    except:
        pass


async def create_check(check_id: str, user: dict, products: list, media: Media):
    if await is_check_exists(check_id):
        return False, None, None
    user = await get_or_create_user(user)
    check = await Check.create(
        user=user,
        lg=check_id,
        media=media,
    )
    for product in products:
        await create_product(check, product)

    return True, check, user


async def calculate_chance(user: User):
    all_checks = await Check.all().count()
    user_checks = await Check.filter(user=user).count()

    return user_checks/all_checks


async def get_checks_count(user: dict) -> int:
    return await Check.filter(user__tg_id=user.get("id")).count()


async def get_products_count(user: dict) -> int:
    return await Product.filter(bill__user__tg_id=user.get("id")).count()
