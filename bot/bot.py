import logging
import re
import uuid

import requests
from ptbcontrib.postgres_persistence import PostgresPersistence
from telegram import ReplyKeyboardMarkup, Update, KeyboardButton, KeyboardButtonRequestChat, KeyboardButtonRequestUser, \
    MenuButtonWebApp, WebAppInfo, InlineKeyboardButton, ReplyKeyboardRemove, InlineKeyboardMarkup
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

from utils import permission
from database.models import ExceptionModel, User
from text import get_text, Language
from settings import ACTION_START_DATE, ACTION_END_DATE
from database.utils import create_check, calculate_chance, get_checks_count, get_products_count, \
    create_user_from_contact, get_or_create_user, update_from_contact, set_user_first_name, set_user_phone, get_user, \
    create_media, delete_media, create_exception, create_check_errored
from database.settings import init_db, DEBUG, DATABASE_URL, DB_URL
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


if DEBUG:
    TOKEN = '6630982782:AAFJkEFJvpot1u2VrSjIWq3-xQMUbmhJJ5o' # test
else:
    TOKEN = '6797074619:AAEwFO66WB-WzT13_t6qG4x7c0V2ilVl86k'


async def get_menu(update):
    user_db = await get_user(update)
    info_button = MenuButtonWebApp(get_text(Language.MENU_3, user_db.language), WebAppInfo(url="https://uz.splatglobal.com/havas2024"))
    rules_button = MenuButtonWebApp(get_text(Language.MENU_4, user_db.language), WebAppInfo(url="https://uz.splatglobal.com/havas2024/pravila"))
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
            await get_menu(update), one_time_keyboard=True,
        ),
    )

    return PHOTO_OR_INFO


async def photo_or_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    user_db: User = await get_user(update)
    nosuccess_reply_keyboard = [[get_text(Language.REPLY_KEYBOARD_1, user_db.language)],
                                [get_text(Language.MENU_5, user_db.language)]]

    if not user_db.is_instruction_sended:
        await update.message.reply_video(
            video=f'video/{user_db.language}.MP4',
            caption=get_text(Language.INSTRUCTION, user_db.language),
            reply_markup=ReplyKeyboardMarkup(
                nosuccess_reply_keyboard, one_time_keyboard=True,
            ),
        )
        user_db.is_instruction_sended = True
        await user_db.save()


    await update.message.reply_text(
        get_text(Language.CHECK_PHOTO_SEND, user_db.language),
        reply_markup=ReplyKeyboardMarkup(
            nosuccess_reply_keyboard, one_time_keyboard=True,
        ),
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
    except Exception as e:
        logger.info(e)
        logger.info("Exception work")
        message_text = f"*Username*: BOT\n*Datetime*: {update.message.date}\n*Link*: {result}\n\n*Error*: Ofd не доступен"
        await context.bot.send_message(
            chat_id='-1002079896743',
            text=message_text,
            parse_mode=ParseMode.MARKDOWN
        )
        logger.info('OFD Error')
        await update.message.reply_markdown(
            get_text(Language.CHECK_ADDED, user_db.language),
            reply_markup=ReplyKeyboardMarkup(
                nosuccess_reply_keyboard, one_time_keyboard=True
            ),
        )
        exception = await create_exception(update, user_db, media, ExceptionModel.ErrorTypes.OFD)
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
    nosuccess_reply_keyboard = [[get_text(Language.REPLY_KEYBOARD_1, user_db.language)],
                                [get_text(Language.MENU_5, user_db.language)]]
    await update.message.reply_text(
        get_text(Language.TECH_ANSWER_1, user_db.language),
        reply_markup=ReplyKeyboardMarkup(
            nosuccess_reply_keyboard, one_time_keyboard=True
        )
    )
    user = update.message.from_user
    link = f"https://t.me/+{user_db.phone_number}"
    message_text = f"*Username*: @{user.username if user.username else link}\n*TG_ID*: {user_db.tg_id}\n*Datetime*: {update.message.date}\n*Language*: {user_db.language}\n*Text*: {update.message.text}\n\n@splatuz_support"
    await context.bot.send_message(
        chat_id='-1002079896743',
        text=message_text,
        parse_mode=ParseMode.MARKDOWN
    )
    return PHOTO_OR_INFO


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
    link = f"https://t.me/+{user_db.phone_number}"
    message_text = f"*Username*: @{user.username if user.username else link}\n*TG_ID*: {user_db.tg_id}\n*Datetime*: {update.message.date}\n*Language*: {user_db.language}\n*Text*: {update.message.text}\n\n@splatuz_support"
    await context.bot.send_message(
        chat_id='-1002079896743' if DEBUG else '-1002127130018',
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
    nosuccess_reply_keyboard = [[get_text(Language.REPLY_KEYBOARD_1, user_db.language)],
                                [get_text(Language.MENU_5, user_db.language)]]
    await update.message.reply_markdown(
        get_text(Language.INCORRECT_COMMAND, user_db.language),
        reply_markup=ReplyKeyboardMarkup(
            nosuccess_reply_keyboard, one_time_keyboard=True
        )
    )
    return PHOTO_OR_INFO


async def incorrect_for_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
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


async def incorrect_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_db = await get_user(update)
    nosuccess_reply_keyboard = [[get_text(Language.REPLY_KEYBOARD_1, user_db.language)],
                                [get_text(Language.MENU_5, user_db.language)]]
    await update.message.reply_markdown(
        get_text(Language.CHECK_PHOTO_SEND, user_db.language),
        reply_markup=ReplyKeyboardMarkup(
            nosuccess_reply_keyboard, one_time_keyboard=True
        )
    )
    return PHOTO_OR_INFO


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


async def restart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_db = await get_user(update)
    if user_db:
        return await menu(update, context)
    return await start(update, context)

async def checkallcheckserrors(update: Update, context: ContextTypes.DEFAULT_TYPE):
    print("WOOOORK")
    # user_db = await get_user(update)
    user = update.message.from_user.to_dict()
    error_checks = await ExceptionModel.filter(
        solved=False
    )
    users_for_update_errors = []
    users_for_update_success = []
    for check in error_checks:
        user_db: User = await User.filter(id=check.user_id).first()
        nosuccess_reply_keyboard = [[get_text(Language.REPLY_KEYBOARD_1, user_db.language)],
                                    [get_text(Language.MENU_5, user_db.language)]]
        result, success = scan(check.path)

        if not success:
            check.result = Language.CHECK_1
            check.solved = True
            await check.save()
            users_for_update_errors.append(check)
            await delete_media(check.path)
            continue

        if not result or not (type(result) is str):
            check.result = Language.CHECK_2
            check.solved = True
            await check.save()
            users_for_update_errors.append(check)
            await delete_media(check.path)
            continue

        match = re.search(r'^https://ofd\.soliq\.uz', result)
        if not match:
            check.result = Language.CHECK_2
            check.solved = True
            await check.save()
            users_for_update_errors.append(check)
            await delete_media(check.path)
            continue

        try:
            page = requests.get(result)
        except:
            check.result = Language.CHECK_2
            check.solved = True
            await check.save()
            users_for_update_errors.append(check)
            await delete_media(check.path)
            continue

        if page.status_code not in [200, 201]:
            check.result = Language.CHECK_2
            check.solved = True
            await check.save()
            users_for_update_errors.append(check)
            await delete_media(check.path)
            continue

        logger.info(page)

        try:
            products, check_id, products_not_exist, incorrect_inn, incorrect_date = parse_products(page.text, result)
        except:
            continue

        logger.info(products)
        if products_not_exist:
            check.result = Language.CHECK_3
            check.solved = True
            await check.save()
            users_for_update_errors.append(check)
            await delete_media(check.path)
            continue

        if incorrect_inn:
            check.result = Language.CHECK_4
            check.solved = True
            await check.save()
            users_for_update_errors.append(check)
            await delete_media(check.path)
            continue

        if incorrect_date:
            check.result = Language.CHECK_5
            check.solved = True
            users_for_update_errors.append(check)
            await delete_media(check.path)
            await check.save()
            continue


        created, checkl, bot_user = await create_check_errored(check_id, user_db, products, check.media_id)
        if not created:
            check.result = Language.CHECK_6
            check.solved = True
            users_for_update_errors.append(check)
            await delete_media(check.path)
            await check.save()
            continue

        check.solved = True
        check.success = True
        users_for_update_success.append(check)
        await check.save()

    # await ExceptionModel.bulk_update(users_for_update_success, fields=['solved', 'success'])
    # await ExceptionModel.bulk_update(users_for_update_errors, fields=['solved', 'result'])

    # success_button_text = get_text(Language.MENU_5, user_db.language)
    # error_button_text = get_text(Language.REPLY_KEYBOARD_2, user_db.language)
    # keyboard_success = [
    #     [
    #         InlineKeyboardButton(f"^{success_button_text}$", callback_data=success_button_text),
    #     ]
    # ]
    #
    # keyboard_error = [
    #     [
    #         InlineKeyboardButton(f"^{error_button_text}$", callback_data=error_button_text),
    #     ]
    # ]

    for check in users_for_update_success:
        user_db: User = await User.filter(id=check.user_id).first()
        await context.bot.send_photo(
            chat_id=check.user_tg,
            photo=f'{check.path}',
            caption=f"{get_text(Language.SUCCESS, user_db.language)}",
            parse_mode=ParseMode.MARKDOWN
        )
    # breakpoint()
    for check in users_for_update_errors:
        user_db: User = await User.filter(id=check.user_id).first()
        await context.bot.send_photo(
            chat_id=check.user_tg,
            photo=f'{check.path}',
            caption=get_text(check.result, user_db.language),
            parse_mode=ParseMode.MARKDOWN,
        )

    await update.message.reply_text(
        f'Количество исправленных: {len(users_for_update_success) + len(users_for_update_errors)}\n\tУспешные - {len(users_for_update_success)}\n\tОшибочные - {len(users_for_update_errors)}'
    )


@permission
async def send_to_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await context.bot.send_message(
        chat_id='373533031',
        text="Assalomu aleykum! ❤️\n\nSiz haftalik tanlovimizda muzlatgich yutib oldingiz!\n\n🎉Lekin biz siz bilan bog'lana olmaymiz, chunki siz telefon raqamingizni ko'rsatmagansiz, iltimos, texnik yordam bo'limiga yozing - @splatuz_support va biz siz bilan bog'lanamiz 😊",
    )


@permission
async def send_segmented_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):

    # TEXT1_RU = "Возможно, вас отвлекли? 🤔\n\nВы зарегистрировались в боте, но так и не стали участником акции 🎁\n\nЧтобы принять участие и получить возможность выиграть бытовую технику или поездку в Таиланд, выполните следующие шаги:\n\n1️⃣ Приобретите любой продукт SPLAT или Biomed в магазинах Havas.\n\n2️⃣ Отправьте полученный чек этому боту.\n\n3️⃣ Теперь вы участник акции! Розыгрыш призов каждую неделю 🎉\n\nНе упустите свой шанс, розыгрыш призов уже близко. Счастливчики прошлой недели уже получили свои подарки. Попробуйте удачу и вы! ❤️"
    # TEXT1_UZ = "Ehtimol, sizni chalg‘itishgandir? 🤔\n\nSiz botda ro‘yxatdan o‘tdingiz, lekin shunga qaramay aksiya ishtirokchisi bo‘lmadingiz 🎁\n\nIshtirok etish va maishiy texnika yoki Tailandga sayohat yutib olish imkoniyatiga ega bo‘lish uchun quyidagi harakatlarni bajaring:\n\n1️⃣ Istalgan SPLAT yoki Biomed mahsulotini Havas do‘konlaridan xarid qiling.\n\n2️⃣ Qabul qilingan chekni ushbu botga yuboring.\n\n3️⃣ Endi siz aksiya ishtirokchisiga aylandingiz! Sovrinlar har hafta o‘ynaladi 🎉\n\nImkoniyatingizni qo‘ldan boy bermang, sovrinlar yaqin kunlarda o‘ynaladi. O‘tgan haftaning omadli g‘oliblari sovg‘alarni ham olishdi. Siz ham omadingizni sinab ko'ring! ❤️"
    # TEXT2_RU = "Увеличивайте свои шансы на победу! 🤩\n\nНапоминаем, что чем больше продуктов вы зарегистрируете, тем больше шансов выиграть один из призов: холодильник, стиральная машина, кондиционер, телевизор или робот-пылесос.\n\nА также, в конце акции среди всех участников мы разыграем главный приз - поездку в Таиланд на двоих!\n\nРозыгрыш призов каждую неделю! 🎉"
    # TEXT2_UZ = "G‘alaba qozonish imkoniyatingizni oshiring! 🤩\n\nEslatib o‘tamiz, qancha ko‘p mahsulot ro‘yxatdan o‘tkazsangiz, muzlatgich, kir yuvish mashinasi, konditsioner, televizor yoki robot changyutgich kabi sovrinlardan birini yutib olish imkoniyati shunchalik yuqori bo‘ladi.\n\nShuningdek, aksiya yakunida biz barcha ishtirokchilar o‘rtasida bosh sovrin – Tailandga ikki kishilik sayohatni o‘ynaymiz!\n\nSovrinlar har hafta o‘ynaladi 🎉"


    TEXT_UZ = "Bugun SPLAT va BIOMED aksiyalari tugashining oxirgi kuni. Ishtirok etishga ulguring! 😍🏝️\n\nTailandga chiptalar va uyingiz uchun maishiy texnika yutib olish imkoniyatini boy bermang! 🤩\n\nHavas do‘konlarida istalgan SPLAT yoki BIOMED mahsulotini xarid qiling, chekni @splatuz_bot telegram-botida ro‘yxatdan o‘tkazing va siz aksiya ishtirokchisisiz. ❤️"
    TEXT_RU = "Сегодня последний день до завершения акции от SPLAT и BIOMED. Успейте принять участие! 😍🏝️\n\nНе упустите шанс выиграть билеты в Таиланд и бытовую технику для вашего дома! 🤩\n\nКупите любой продукт SPLAT или BIOMED в магазинах Havas, зарегистрируйте чек в телеграм боте @splatuz_bot и вы участник акции. ❤️"

    users = await User.all()
    # breakpoint()

    for user in users:
        try:
            if user.language == 'ru':
                await context.bot.send_photo(
                    photo=open('ru2.jpg', 'rb'),
                    chat_id=user.tg_id,
                    caption=TEXT_RU
                )
            elif user.language == 'uz':
                await context.bot.send_photo(
                    photo=open('uz2.jpg', 'rb'),
                    chat_id=user.tg_id,
                    caption=TEXT_UZ
                )
        except Exception as e:
            print(f"Error: {e}")
            pass


    # users = await User.all()
    #
    # for user in users:
    #     try:
    #         if await user.checks.all().exists():
    #             if user.language == 'ru':
    #                 await context.bot.send_message(
    #                     chat_id=user.tg_id,
    #                     text=TEXT2_RU
    #                 )
    #             elif user.language == 'uz':
    #                 await context.bot.send_message(
    #                     chat_id=user.tg_id,
    #                     text=TEXT2_UZ
    #                 )
    #         else:
    #             if user.language == 'ru':
    #                 await context.bot.send_message(
    #                     chat_id=user.tg_id,
    #                     text=TEXT1_RU
    #                 )
    #             elif user.language == 'uz':
    #                 await context.bot.send_message(
    #                     chat_id=user.tg_id,
    #                     text=TEXT1_UZ
    #                 )
    #     except Exception:
    #         pass


def main() -> None:
    application = Application.builder().token(TOKEN).persistence(PostgresPersistence(url=DB_URL)).build()

    application.add_handler(CommandHandler("help", menu))
    application.add_handler(CommandHandler("checkallcheckserrors", checkallcheckserrors))
    application.add_handler(CommandHandler("sendtousermessage", send_to_user_message))
    application.add_handler(CommandHandler("sendsegmentedmessage", send_segmented_messages))

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start), CommandHandler("restart", restart)],
        states={
            NAME: [
                MessageHandler(filters.CONTACT, name),
                MessageHandler(filters.Regex("^Ввести имя$"), name),
                MessageHandler(filters.Regex("^Ismni kiritish$"), name),
                MessageHandler(filters.ALL, incorrect_for_name)
            ],
            TECH: [
                MessageHandler(filters.PHOTO, photo),
                MessageHandler(filters.Regex("^👨‍💻 Тех. поддержка"), tech),
                MessageHandler(filters.Regex("^👨‍💻 Texnik yordam"), tech),
                MessageHandler(filters.Regex("^🧾 Загрузить новый чек"), photo_or_info),
                MessageHandler(filters.Regex("^🧾 Yangi check yuklash"), photo_or_info),
                MessageHandler(filters.Regex("^Меню$"), menu),
                MessageHandler(filters.Regex("^Menu$"), menu),
                # MessageHandler(filters.Regex("^.*"), tech),
                MessageHandler(filters.ALL, incorrect)
            ],
            LANGUAGE: [
                MessageHandler(filters.Regex("^.*"), language),
                MessageHandler(filters.ALL, incorrect)
            ],
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
                MessageHandler(filters.PHOTO, photo),
                MessageHandler(filters.Regex("^🧾 Загрузить новый чек$"), photo_or_info),
                MessageHandler(filters.Regex("^🧾 Yangi check yuklash"), photo_or_info),
                MessageHandler(filters.Regex("^Меню$"), menu),
                MessageHandler(filters.Regex("^Menu$"), menu),
                MessageHandler(filters.ALL, incorrect_photo)
            ],
        },
        fallbacks=[CommandHandler("cancel", cancel)],
        persistent=True,
        name='splat'
    )

    application.add_handler(conv_handler)

    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    run_async(init_db())
    main()
