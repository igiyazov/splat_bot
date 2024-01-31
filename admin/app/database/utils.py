from database.models import User, Check, Product


async def create_user(user: dict):
    print(user)
    user = await User.create(
        tg_id=user.get('id'),
        first_name=user.get('first_name'),
        last_name=user.get('last_name'),
        username=user.get('username'),
    )
    return user


async def is_check_exists(check_id: str):
    return await Check.filter(lg=check_id).exists()


async def create_product(check: Check, product: dict):
    await Product.create(
        bill=check,
        **product
    )


async def create_check(check_id: str, user: dict, products: list):
    if await is_check_exists(check_id):
        return False, None, None
    user = await create_user(user)
    check = await Check.create(
        user=user,
        lg=check_id,
    )
    for product in products:
        await create_product(check, product)

    return True, check, user


async def calculate_chance(user: User):
    all_checks = await Check.all().count()
    user_checks = await Check.filter(user=user).count()

    return user_checks/all_checks
