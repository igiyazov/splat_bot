import logging
import re
import uuid

import requests
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton, KeyboardButtonRequestChat, KeyboardButtonRequestUser, \
    MenuButtonWebApp, WebAppInfo
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)
from tortoise import run_async

from text import get_text, Language
from settings import ACTION_START_DATE, ACTION_END_DATE
from database.utils import create_check, calculate_chance, get_checks_count, get_products_count, \
    create_user_from_contact, get_or_create_user, update_from_contact, set_user_first_name, set_user_phone, get_user, \
    create_media, delete_media
from database.settings import init_db
from parse import parse_products
from read_qr import scan

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
# set higher logging level for httpx to avoid all GET and POST requests being logged
logging.getLogger("httpx").setLevel(logging.WARNING)

logger = logging.getLogger(__name__)

LANGUAGE, PHOTO_OR_INFO, PHOTO, PROGRESS, CONTACT, PHONE_NUMBER, NAME, TECH = range(8)


# TOKEN = '6630982782:AAFJkEFJvpot1u2VrSjIWq3-xQMUbmhJJ5o' # test
TOKEN = '6797074619:AAEwFO66WB-WzT13_t6qG4x7c0V2ilVl86k'


async def get_menu(update):
    user_db = await get_user(update)
    info_button = MenuButtonWebApp(get_text(Language.MENU_3, user_db.language), WebAppInfo(url="https://ya.ru/"))
    rules_button = MenuButtonWebApp(get_text(Language.MENU_4, user_db.language), WebAppInfo(url="https://ya.ru/"))
    MENU_BUTTONS = [[get_text(Language.MENU_1, user_db.language)], [get_text(Language.MENU_2, user_db.language)], [info_button], [rules_button]]
    return MENU_BUTTONS


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    reply_keyboard = [["🇺🇿O'zbek", "🇷🇺Русский"]]
    await update.message.reply_text(
        "Выберити язык:\nTilni tanlang:",
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True, input_field_placeholder="O'zbek | Русский?"
        ),
    )

    return CONTACT


async def contact(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    lang = 'ru' if update.message.text == "🇷🇺Русский" else 'uz'
    user = update.message.from_user.to_dict()
    await get_or_create_user(user, lang)
    user_db = await get_user(update)
    g = [[KeyboardButton(
        get_text(Language.CONTACT_SHARE_MENU_1, user_db.language),
        request_contact=True,
        request_user=KeyboardButtonRequestUser(2),
    ), get_text(Language.CONTACT_SHARE_MENU_2, user_db.language)]]

    await update.message.reply_text(
        get_text(Language.ACQUAINTANCE, user_db.language),
        reply_markup=ReplyKeyboardMarkup(
            g, one_time_keyboard=True
        )
    )


    return NAME


async def name(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    if update.message.contact:
        user = await update_from_contact(update)
        return await language(update, context)
    user_db = await get_user(update)
    await update.message.reply_text(
        get_text(Language.NAME, user_db.language)
    )

    return PHONE_NUMBER


async def phone_number(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_db = await set_user_first_name(update)
    await update.message.reply_text(
        get_text(Language.PHONE_NUMBER, user_db.language)
    )
    return LANGUAGE


async def language(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_db = await get_user(update)
    if update.message.text:
        match = re.search(r'^\+998\d{9}$', update.message.text)
        if not match:
            await update.message.reply_text(
                get_text(Language.PHONE_NUMBER_INCORRECT, user_db.language)
            )
            return LANGUAGE

        await set_user_phone(update)

    await update.message.reply_markdown(
        get_text(Language.SUCCESS_SIGNUP, user_db.language),
        reply_markup=ReplyKeyboardMarkup(
            await get_menu(update), one_time_keyboard=True, resize_keyboard=True,
        ),
    )

    return PHOTO_OR_INFO


async def photo_or_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_db = await get_user(update)
    await update.message.reply_text(
        get_text(Language.CHECK_PHOTO_SEND, user_db.language),
    )

    return PHOTO


async def photo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_db = await get_user(update)
    reply_keyboard = [[get_text(Language.REPLY_KEYBOARD_1, user_db.language)], [get_text(Language.REPLY_KEYBOARD_2, user_db.language)], [get_text(Language.MENU_5, user_db.language)]]
    nosuccess_reply_keyboard = [[get_text(Language.REPLY_KEYBOARD_1, user_db.language)], [get_text(Language.REPLY_KEYBOARD_2, user_db.language)], [get_text(Language.MENU_5, user_db.language)]]
    user = update.message.from_user.to_dict()
    logger.info(user)
    photo_file = await update.message.photo[-1].get_file()

    filename = f"media/{str(uuid.uuid4())}.jpg"

    await photo_file.download_to_drive(filename)
    media = await create_media(filename)
    result, success = scan(filename)

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
            get_text(Language.CHECK_2, user_db.language),
            reply_markup=ReplyKeyboardMarkup(
                nosuccess_reply_keyboard, one_time_keyboard=True
            ),
        )
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

    await update.message.reply_markdown(
        get_text(Language.SUCCESS, user_db.language),
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )

    return PHOTO_OR_INFO


async def lk(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_db = await get_user(update)
    reply_keyboard = [[get_text(Language.MENU_5, user_db.language)]]
    user = update.message.from_user.to_dict()
    products_count = await get_products_count(user)
    await update.message.reply_markdown(
        get_text(Language.LK, user_db.language).format(
            first_name=user_db.first_name,
            phone_number=user_db.phone_number,
            products_count=products_count
        ),
        reply_markup=ReplyKeyboardMarkup(
            reply_keyboard, one_time_keyboard=True
        ),
    )
    return PHOTO_OR_INFO


async def tech(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_db = await get_user(update)
    match1 = re.search(r'Тех\. поддержка$', update.message.text)
    match2 = re.search(r'Texnik yordam$', update.message.text)
    if match1 or match2:
        await update.message.reply_text(
            get_text(Language.TECH, user_db.language)
        )
        return TECH

    # TODO: send message
    # 1002127130018
    user = update.message.from_user
    message_text = f"*Username*: @{user.username}\n*Datetime*: {update.message.date}\n*Language*: {user_db.language}\n*Text*: {update.message.text}"
    await context.bot.send_message(
        chat_id='-1002127130018',
        text=message_text,
        parse_mode=ParseMode.MARKDOWN
    )
    await update.message.reply_text(
        get_text(Language.TECH_ANSWER, user_db.language),
        reply_markup=ReplyKeyboardMarkup(
            await get_menu(update), one_time_keyboard=True
        ),
    )
    return PHOTO_OR_INFO


async def incorrect(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_db = await get_user(update)
    await update.message.reply_markdown(
        get_text(Language.INCORRECT_COMMAND, user_db.language),
    )


async def incorrect_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_db = await get_user(update)
    await update.message.reply_markdown(
        get_text(Language.CHECK_PHOTO_SEND, user_db.language),
    )


async def menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_db = await get_user(update)
    await update.message.reply_text(
            get_text(Language.BUTTON, user_db.language),
            allow_sending_without_reply=True,
            reply_markup=ReplyKeyboardMarkup(
                await get_menu(update), one_time_keyboard=True
            )
    )
    return PHOTO_OR_INFO


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    pass


def main() -> None:
    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("help", menu))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("restart", start)],
        states={
            NAME: [
                MessageHandler(filters.CONTACT, name),
                MessageHandler(filters.Regex("^Ввести имя$"), name),
                MessageHandler(filters.Regex("^Ismni kiritish$"), name),
                MessageHandler(filters.ALL, incorrect)
            ],
            TECH: [
                MessageHandler(filters.PHOTO, photo),
                MessageHandler(filters.Regex("^👨‍💻 Тех. поддержка"), tech),
                MessageHandler(filters.Regex("^👨‍💻 Texnik yordam"), tech),
                MessageHandler(filters.Regex("^🧾 Загрузить новый чек"), photo_or_info),
                MessageHandler(filters.Regex("^🧾 Yangi check yuklash"), photo_or_info),
                MessageHandler(filters.Regex("^Меню$"), menu),
                MessageHandler(filters.Regex("^Menu$"), menu),
                MessageHandler(filters.Regex("^.*"), tech),
                MessageHandler(filters.ALL, incorrect)
            ],
            LANGUAGE: [MessageHandler(filters.Regex("^.*"), language), MessageHandler(filters.ALL, incorrect)],
            PHONE_NUMBER: [
                MessageHandler(filters.Regex("^\w+"), phone_number),
                MessageHandler(filters.ALL, incorrect),
            ],
            PHOTO_OR_INFO: [
                MessageHandler(filters.PHOTO, photo),
                MessageHandler(filters.Regex("^🧾 Загрузить новый чек$"), photo_or_info),
                MessageHandler(filters.Regex("^🧾 Yangi check yuklash"), photo_or_info),
                MessageHandler(filters.Regex("^🧾 Загрузить чек$"), photo_or_info),
                MessageHandler(filters.Regex("^🧾 Chekni yuklash$"), photo_or_info),
                MessageHandler(filters.Regex("^👤️ Личный кабинет$"), lk),
                MessageHandler(filters.Regex("^👤️ Shaxsiy kabinet$"), lk),
                MessageHandler(filters.Regex("^Меню$"), menu),
                MessageHandler(filters.Regex("^Menu$"), menu),
                MessageHandler(filters.ALL, incorrect)
            ],
            CONTACT: [MessageHandler(filters.Regex("^(🇺🇿O'zbek|🇷🇺Русский)$"), contact), MessageHandler(filters.ALL, incorrect)],
            PHOTO: [
                MessageHandler(filters.PHOTO, photo), MessageHandler(filters.ALL, incorrect_photo)
            ],
            PROGRESS: [
                MessageHandler(filters.Regex("Прогресс"), photo),
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_async(init_db())
    main()
