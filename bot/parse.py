from datetime import datetime
from urllib import parse

from bs4 import BeautifulSoup

from settings import ACTION_START_DATE, ACTION_END_DATE

COMPANY_INN = '305645847'
# COMPANY_NAME = "ООО \"AFZAL\""

SPLAT_PRODUCTS = [
    "TISH PASTASI KUNLIK CHOY DARAXTI VA YALPIZ YOG'LI 100GR SPLAT",
    "TISH PASTASI KUNLIK COMPLEX ALOE-LIMON YOG'LI 100GR SPLAT",
    "TISH PASTASI PROFESSIONAL BIOKALSIY 100ML SPLAT",
    "TISH PASTASI PROFESSIONAL OQARTIRUVCHI 100ML SPLAT",
    "TISH PASTASI PROFESSIONAL SHIFOBAXSH O'TLAR 100ML SPLAT",
    "TISH YUVISH CHO'TKASI KO'MIRLI MEDIUM 1DONA BIOMED",
    "TISH YUVISH CHO'TKASI MEDIUM 1DONA BIOMED",
]


def parse_products(html_text, url):
    soup = BeautifulSoup(html_text, 'html.parser')

    all_i = soup.find_all('i')

    company_inn = all_i[0].text
    product_purchase_date = datetime.strptime(all_i[1].text.split(',')[0], '%d.%m.%Y')

    if product_purchase_date.date() < ACTION_START_DATE or product_purchase_date.date() >= ACTION_END_DATE:
        return [], None, False, False, True

    check_number = parse.parse_qs(parse.urlparse(url).query)['s'][0]
    check_id = (soup.find_all('b')[0].text + check_number)
    print(check_id)
    print(company_inn)
    if COMPANY_INN != company_inn:
        return [], check_id, False, True, False

    products = []
    for row in soup.find_all('tr', class_='products-row'):
        children = row.find_all('td')
        name = children[0].text.strip()
        count = int(children[1].text)
        if name in SPLAT_PRODUCTS:
            products.append({
                'name': name,
                'count': count
            })
    product_not_exist = True if not products else False
    return products, check_id, product_not_exist, False, False






