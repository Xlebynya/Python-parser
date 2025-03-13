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
        product_html = session.get(link[0], headers=header).text
        product_page = lxml.html.document_fromstring(product_html)
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
            "name": name,
            "price_roz": price_roz,
            "price_opt": price_opt,
            "rating": rating,
            "review_count": reviewCount,
            "store_count": store_count,
            "reviews": reviews,
        }
        products.append(product_data)

    except Exception as e:
        print(e)  # Отладочное сообщение

for prod in products:
    print(prod)
