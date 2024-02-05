from bot.database.models import ExceptionModel
from bot.read_qr import scan


def add_check():
    error_checks = await ExceptionModel.filter(
        solved=False
    )
    for check in error_checks:
        result, success = scan(check.path)

        if not success:
            await update.message.reply_markdown(
                get_text(Language.CHECK_1, user_db.language),
                reply_markup=ReplyKeyboardMarkup(
                    nosuccess_reply_keyboard, one_time_keyboard=True
                ),
            )
            await delete_media(media)
            return TECH
        logger.info(f"URL: {result}")

        if not result or not (type(result) is str):
            await update.message.reply_markdown(
                get_text(Language.CHECK_2, user_db.language),
                reply_markup=ReplyKeyboardMarkup(
                    nosuccess_reply_keyboard, one_time_keyboard=True
                ),
            )
            await delete_media(media)
            return TECH

        match = re.search(r'^https://ofd\.soliq\.uz', result)
        if not match:
            await update.message.reply_markdown(
                get_text(Language.CHECK_2, user_db.language),
                reply_markup=ReplyKeyboardMarkup(
                    nosuccess_reply_keyboard, one_time_keyboard=True
                ),
            )
            await delete_media(media)
            return TECH

        try:
            page = requests.get(result)
        except:
            await update.message.reply_markdown(
                get_text(Language.CHECK_2, user_db.language),
                reply_markup=ReplyKeyboardMarkup(
                    nosuccess_reply_keyboard, one_time_keyboard=True
                ),
            )
            return TECH

        if page.status_code not in [200, 201]:
            await update.message.reply_markdown(
                get_text(Language.CHECK_2, user_db.language),
                reply_markup=ReplyKeyboardMarkup(
                    nosuccess_reply_keyboard, one_time_keyboard=True
                ),
            )
            await delete_media(media)
            return TECH

        logger.info(page)

        try:
            products, check_id, products_not_exist, incorrect_inn, incorrect_date = parse_products(page.text, result)
        except:
            message_text = f"*Username*: BOT\n*Datetime*: {update.message.date}\n\n*Error*: Ofd не доступен"
            await context.bot.send_message(
                chat_id='-1002127130018',
                text=message_text,
                parse_mode=ParseMode.MARKDOWN
            )
            logger.info('OFD Error')
            await update.message.reply_markdown(
                get_text(Language.CHECK_7, user_db.language),
                reply_markup=ReplyKeyboardMarkup(
                    nosuccess_reply_keyboard, one_time_keyboard=True
                ),
            )
            exception = await create_exception(update, user_db, filename, ExceptionModel.ErrorTypes.OFD)
            logging.info(f"Exception created for:\n user: {user_db.first_name}\n ref: {result}\n filename: {filename}")
            return TECH

        logger.info(products)
        if products_not_exist:
            await update.message.reply_markdown(
                get_text(Language.CHECK_3, user_db.language),
                reply_markup=ReplyKeyboardMarkup(
                    nosuccess_reply_keyboard, one_time_keyboard=True
                ),
            )
            await delete_media(media)
            return TECH

        if incorrect_inn:
            await update.message.reply_markdown(
                get_text(Language.CHECK_4, user_db.language),
                reply_markup=ReplyKeyboardMarkup(
                    nosuccess_reply_keyboard, one_time_keyboard=True
                ),
            )
            await delete_media(media)
            return TECH

        if incorrect_date:
            await update.message.reply_markdown(
                get_text(Language.CHECK_5, user_db.language),
                reply_markup=ReplyKeyboardMarkup(
                    nosuccess_reply_keyboard, one_time_keyboard=True
                ),
            )
            await delete_media(media)
            return TECH

        created, check, bot_user = await create_check(check_id, user, products, media)
        if not created:
            await update.message.reply_markdown(
                get_text(Language.CHECK_6, user_db.language),
                reply_markup=ReplyKeyboardMarkup(
                    reply_keyboard, one_time_keyboard=True
                ),
            )
            await delete_media(media)
            return PHOTO_OR_INFO

