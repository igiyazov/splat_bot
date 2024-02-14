class Language:
    MENU_1 = 'menu_1'
    MENU_2 = 'menu_2'
    MENU_3 = 'menu_3'
    MENU_4 = 'menu_4'
    MENU_5 = 'menu_5'
    REPLY_KEYBOARD_1 = 'reply_keyboard_1'
    REPLY_KEYBOARD_2 = 'reply_keyboard_2'
    CONTACT_SHARE_MENU_1 = 'contact_menu_1'
    CONTACT_SHARE_MENU_2 = 'contact_menu_2'
    PHONE_NUMBER = 'phone_number'
    PHONE_NUMBER_INCORRECT = 'phone_number_incorrect'
    ACQUAINTANCE = 'acquaintance'
    SUCCESS_SIGNUP = 'success_signup'
    CHECK_PHOTO_SEND = 'check_photo_send'
    CHECK_1 = 'check_1'
    CHECK_2 = 'check_2'
    CHECK_3 = 'check_3'
    CHECK_4 = 'check_4'
    CHECK_5 = 'check_5'
    CHECK_6 = 'check_6'
    CHECK_7 = 'check_7'
    SUCCESS = 'success'
    LK = 'lk'
    TECH = 'tech'
    TECH_ANSWER = 'tech_answer'
    INCORRECT_COMMAND = 'incorrect_command'
    BUTTON = 'button'
    NAME = 'name'
    CHECK_ADDED = 'check_added'
    ADDED_CHECK_SUCCESS = 'added_check_success'
    TECH_ANSWER_1 = 'tech_answer_1'
    TECH_ANSWER_2 = 'tech_answer_2'





LANGUAGE_TEXT = {
    Language.MENU_1: {
        'ru': '🧾 Загрузить чек',
        'uz': '🧾 Chekni yuklash'
    },
    Language.MENU_2: {
        'ru': '👤️ Личный кабинет',
        'uz': '👤️ Shaxsiy kabinet'
    },
    Language.MENU_3: {
        'ru': '✨ Подробнее об акции',
        'uz': '✨ Aksiya haqida batafsil'
    },
    Language.MENU_4: {
        'ru': '📄 Правила акции',
        'uz': '📄 Aksiya qoidalari'
    },
    Language.MENU_5: {
        'ru': 'Меню',
        'uz': 'Menu'
    },
    Language.REPLY_KEYBOARD_1: {
        'ru': '🧾 Загрузить новый чек',
        'uz': '🧾 Yangi check yuklash'
    },
    Language.REPLY_KEYBOARD_2: {
        'ru': '👨‍💻 Тех. поддержка',
        'uz': '👨‍💻 Texnik yordam'
    },
    Language.CONTACT_SHARE_MENU_1: {
        'ru': 'Поделиться контактом',
        'uz': 'Contact yuborish'
    },
    Language.CONTACT_SHARE_MENU_2:{
        'ru': 'Ввести имя',
        'uz': 'Ismni kiritish'
    },
    Language.NAME: {
        'ru': 'Введите ваше имя',
        'uz': 'Ismingizni kiriting'
    },
    Language.ACQUAINTANCE: {
        'ru': 'Давайте познакомимся!\nПоделитесь вашим контактом или введите имя вручную.\n\nОбращаем ваше внимание - имя и фамилия должны соответствовать документам. В случае выигрыша приза, мы будем связываться с вами по введенным данным.',
        'uz': 'Keling tanishib olamiz!\nTelefon raqamingiz bilan ulashing yoki ismingizni qo‘lda kiriting.\n\nE’tiboringizni ism va familiya hujjatlarga mos kelishi kerakligiga qaratamiz. Sovrin yutib olingan taqdirda, siz bilan kiritilgan ma’lumotlar bo‘yicha bog‘lanamiz.'
    },
    Language.PHONE_NUMBER: {
        'ru': 'Для регистрации чека необходимо указать ваш актуальный номер телефона для связи с вами. \nУкажите номер в формате +998*********',
        'uz': 'Chekni ro‘yxatdan o‘tkazish hamda siz bilan bog‘lanish uchun ishlab turgan telefon raqamingizni ko‘rsatishingiz kerak. \n Kiritish formati +998*********'
    },
    Language.PHONE_NUMBER_INCORRECT: {
        'ru': '❌ Неправильно введён номер телефона.\nПопробуйте ещё раз!',
        'uz': '❌ Telefon raqami noto\'g\'ri kiritilgan. \nYana bir marta kiriting!'
    },
    Language.SUCCESS_SIGNUP: {
        'ru': '✅ Поздравляем!\nВы успешно зарегистрировались!\nДля участия в розыгрыше призов отправьте фотографию чека с покупкой любого продукта SPLAT или Biomed из магазинов Havas 👇\n*Обращаем ваше внимание, что на фото должен быть отображен QR код из нижней части чека*.',
        'uz': '✅ Tabriklaymiz!\nSiz ro‘yxatdan muvaffaqiyatli o‘tdingiz!\nSovrinlar o‘yinida ishtirok etish uchun Havas do‘konlaridan istalgan SPLAT yoki Biomed mahsulotini sotib olganda berilgan chek fotosuratini yuboring 👇\n*E’tiboringizni fotosuratda chekning pastki qismidagi QR kod aks ettirilishi kerakligiga qaratamiz*.'
    },
    Language.CHECK_PHOTO_SEND: {
        'ru': 'Отправьте фото чека',
        'uz': 'Checkni rasmini jo\'nating'
    },
    Language.CHECK_1: {
        'ru': '❌ *К сожалению, чек не прошел проверку!*\n\nВозможно, фотография сделана нечетко или на фото не попал QR код из нижней части чека. Сделайте фотографию еще раз и отправьте чек в ответном сообщении.\nВ случае сложностей вы можете связаться с тех. поддержкой👇',
        'uz': '❌ *Afsuski, chek tekshiruvdan o‘tmadi!*\n\nEhtimol, fotosurat aniq olinmagan yoki chekning pastki qismidagi QR-kod fotosuratga tushmagan. Yana bir bor suratga oling va chekni javob xabarida yuboring.\nQiyinchiliklar bo‘lgan taqdirda, texnik qo‘llab-quvvatlash xizmati bilan bog‘lanishingiz mumkin👇'
    },
    Language.CHECK_2: {
        'ru': '❌ *К сожалению, чек не прошел проверку!*\n\nВ предоставленном чеке QR-код не соответствует QR-коду магазина Хавас, в котором проходит акция.\n\nЗагрузите другой чек или свяжитесь с поддержкой👇',
        'uz': '❌ *Afsuski, chek tekshiruvdan o‘tmadi!*\n\nTaqdim etilgan chekdagi QR kod aksiya o‘tkazilayotgan Havas do‘konining QR kodiga mos kelmaydi.\n\nBoshqa chekni yuklang yoki qo‘llab-quvvatlash xizmati bilan bog‘laning👇'
    },
    Language.CHECK_3: {
        'ru': '❌ *К сожалению, чек не прошел проверку!*\n\nВ чеке отстуствуют продукты SPLAT или Biomed, среди которых проходит розыгрыш.\nПродукты SPLAT и Biomed это зубные пасты и щетки, которые вы можете найти в магазинах Хавас.\n\nЗагрузите другой чек с акционными продуктами или свяжитесь с поддержкой👇',
        'uz': '❌ *Afsuski, chek tekshiruvdan o‘tmadi!*\n\nChekda yutuqli o‘yin o‘tkazilayotgan SPLAT yoki Biomed mahsulotlari yo‘q.\n\nSPLAT va Biomed mahsulotlari - bu siz Havas do‘konlarida topishingiz mumkin bo‘lgan tish pastalari va cho‘tkalari.\n\nBoshqa aksiya mahsulotlari xarid chekini yuklang yoki qo‘llab-quvvatlash xizmati bilan bog‘laning👇'
    },
    Language.CHECK_4: {
        'ru': '❌ *К сожалению, чек не прошел проверку!*\n\nПокупка была совершена не в магазинах Хавас, в которых проходит акция.\n\nЗагрузите другой чек из магазинов Хавас или свяжитесь с поддержкой👇',
        'uz': '❌ *Afsuski, chek tekshiruvdan o‘tmadi!*\n\nXarid aksiya o‘tkazilayotgan Havas do‘konlarida amalga oshirilmagan.\n\nHavas do‘konlari boshqa chekini yuklang yoki qo‘llab-quvvatlash xizmati bilan bog‘laning👇'
    },
    Language.CHECK_5: {
        'ru': '❌ *К сожалению, чек не прошел проверку!*\n\nПокупка в данном чеке была совершена не в даты акции.\nДаты акции: 1.02.2024 - 31.03.2024\n\nЗагрузите другой чек с покупкой в период с *1.02.2024* по *31.03.2024* или свяжитесь с поддержкой👇',
        'uz': '❌ *Afsuski, chek tekshiruvdan o‘tmadi!*\n\nUshbu chekdagi xarid aksiya o‘tkazilgan sanada amalga oshirilmagan.\nAksiya o‘tkazilgan sana: 1.02.2024 - 31.03.2024\n\n*02.01.2024* dan *31.03.2024* gacha bo‘lgan davr boshqa xarid chekini yuklang yoki qoʻllab-quvvatlash xizmati bilan bog‘laning👇'
    },
    Language.CHECK_6: {
        'ru': '❌ *К сожалению, чек не прошел проверку!*\n\nДанный чек уже был зарегистрирован.\nЗагрузите другой чек или свяжитесь с поддержкой👇',
        'uz': '❌ *Afsuski, chek tekshiruvdan o‘tmadi!*\n\nUshbu chek oldin ro‘yxatdan o‘tkazilgan.\nBoshqa chekni yuklang yoki qo‘llab-quvvatlash xizmati bilan bog‘laning👇'
    },
    Language.SUCCESS:{
        'ru': '✅  *Ваш чек успешно зарегистрирован!*\n\n🤫 Говорим по секрету: Чем больше покупок вы регистрируете в боте, тем больше шансов на победу 😌',
        'uz': '✅  *Chekingiz ro‘yxatdan muvaffaqiyatli o‘tkazildi!*\n\n🤫 Sizga bir sirni ochamiz: Botda qancha ko‘p xaridni ro‘yxatdan o‘tkazsangiz, yutuqni qo‘lga kiritish imkoniyati shunchalik yuqori bo‘ladi 😌 '
    },
    Language.LK: {
        'ru': '*Имя*: {first_name}\n*Телефон номер*: {phone_number}\n*Купленные продукты*: {products_count}\n',
        'uz': '*Ism*: {first_name}\n*Telefon raqam*: {phone_number}\n*Harid qilingan maxsulot*: {products_count}\n'
    },
    Language.TECH:{
        'ru': '💬 Напишите  где у вас возникли проблемы?',
        'uz': '💬 Muammolar qayerda paydo bo‘lganini yozing.'
    },
    Language.TECH_ANSWER:{
        'ru': '🙌 Спасибо за обратную связь!\nМы ответим вам в ближайшее время.',
        'uz': '🙌 Bildirilgan fikr uchun rahmat!\nBiz sizga yaqin vaqt ichida javob beramiz.'
    },
    Language.INCORRECT_COMMAND:{
        'ru': '❌ *Неверная команда!\n\nВыберите пункт из меню* 👇',
        'uz': '❌ *Noto\'g\'ri!\n\nMenudan kerakli tugmani tanlang* 👇'
    },
    Language.BUTTON:{
        'ru': 'Выберите пункт из меню 👇',
        'uz': 'Menudan kerakli tugmani tanlang 👇'
    },
    Language.CHECK_7: {
        'ru': '🙁 К сожалению, база налоговой временно недоступна. Мы проверим чек и отправим вам оповещение о проверке как только сайт станет доступен.',
        'uz': '❌ *Soliq qo\'mitasining bazasi vaqtinchalik ishlamayapti!*\n\n Keyinroq qayta urinib ko\'ring.'
    },
    Language.CHECK_ADDED: {
        'ru': '🧾 Чек загружен!\n🧑‍💻Начинаем проверку чека…\n\nО результате проверки сообщим в этом чате в течение 24 часов 😊',
        'uz': '🧾 Chek yuklandi!\n🧑‍💻Chekni tekshirishni boshlayapmiz...\n\nTekshiruv natijasi haqida sizga 24 soat ichida ushbu chat orqali xabar beramiz 😊'
    },
    Language.ADDED_CHECK_SUCCESS: {
        'ru': 'Проверка чека завершена.\n\n✅ Поздравляем - ваш чек успешно зарегистрирован!',
        'uz': 'Chekni tekshirish tugallandi.\n\n✅ Tabriklaymiz - chekingiz ro‘yxatdan muvaffaqiyatli o‘tkazildi!'
    },
    Language.TECH_ANSWER_1: {
        'ru': '🧑‍💻 Решим все вопросы!\n\nКонтакты связи с тех. поддержкой: @splatuz_support\n\nНапишите ваш вопрос в личные сообщения по контактам указанным выше',
        'uz': '🧑‍💻 Barcha masalalarni hal qilamiz!\n\nTexnik qo‘llab-quvvatlash xizmati bilan bog‘lanish: @splatuz_support\n\nSavolingizni yuqorida ko‘rsatilgan bog‘lanish manzillariga shaxsiy xabar orqali yozing'
    },
    Language.TECH_ANSWER_2: {
        'ru': 'Для связи с тех. поддержкой необходимо обратиться по следующим контактам: @splatuz_support',
        'uz': 'Texnik qo‘llab-quvvatlash xizmati bilan bog‘lanish uchun quyidagi bog‘lanish manzillariga murojaat qilish kerak: @splatuz_support'
    }
}


def get_text(key, language='ru'):
    return LANGUAGE_TEXT.get(key).get(language)
