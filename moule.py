import lxml.html
import requests
import fake_useragent

session = requests.Session()

URL = "https://siriust.ru/"
login = "gamemade152@gmail.com"
password = "445566112233"

user = fake_useragent.UserAgent().random

header = {"user-agent": user}

payload = {"user_login": login, "password": password, "dispatch[auth.login]": ""}

response = session.post(URL, data=payload, headers=header)

html_wishlist = session.get("https://siriust.ru/wishlist/", headers=header).text
tree = lxml.html.document_fromstring(html_wishlist)

product_elements = tree.xpath('//div[@class="col-tile"]')

products = []
for element in product_elements:
    try:
        name = element.xpath('.//a[@class="product-title"]/text()')
        price_roz, price_opt = [
            float(el.replace("\xa0", ""))
            for el in element.xpath('.//span[@class="ty-price-num"]/text()')
        ]

        link = element.xpath('.//span[@class="ty-nowrap ty-stars"]//@href')
        html_product = session.get(link[0], headers=header).text
        product_page = lxml.html.document_fromstring(html_product)
        rating = product_page.xpath(
            './/div[@itemprop="aggregateRating"]/meta[@itemprop="ratingValue"]/@content'
        )
        reviewCount = product_page.xpath(
            './/div[@itemprop="aggregateRating"]/meta[@itemprop="reviewCount"]/@content'
        )

        store_count = int(
            product_page.xpath('count(//*[@id="content_features"]/div/div)')
        )

        reviews = product_page.xpath(
            '//div[@id="content_discussion_block"]//div[@class="ty-discussion-post__message"]/text()'
        )
        reviews = [it.replace("\r\n", "") for it in reviews]

        product_data = {
            "Название": name,
            "Цена розница": price_roz,
            "Цена оптовая": price_opt,
            "Рейтинг": rating,
            "Количество оценок": reviewCount,
            "Количество магазинов с товаром": store_count,
            "Отзывы": reviews,
        }
        products.append(product_data)

    except Exception as e:
        print(e)  # Отладочное сообщение

html_user = session.get("https://siriust.ru/profiles-update/", headers=header).text
tree = lxml.html.document_fromstring(html_user)

userMail = tree.xpath('//*[@id="email"]/@value')
userName = tree.xpath('//*[@id="elm_15"]/@value')
userSurname = tree.xpath('//*[@id="elm_17"]/@value')
userCity = tree.xpath('//*[@id="elm_23"]/@value')

