import lxml.html
import requests
import fake_useragent

URL = "https://siriust.ru/"


def create_session():
    session = requests.Session()
    user = fake_useragent.UserAgent().random
    header = {"user-agent": user}
    session.headers.update(header)
    return session


def login(session, login, password):
    payload = {"user_login": login, "password": password, "dispatch[auth.login]": ""}
    response = session.post(URL, data=payload)
    response.raise_for_status()


def parse_user_info(session):
    try:
        response = session.get("https://siriust.ru/profiles-update/")
        response.raise_for_status()
        html_user = response.text
        tree = lxml.html.document_fromstring(html_user)

        user_info = {
            "email": (
                tree.xpath('//*[@id="email"]/@value')[0]
                if tree.xpath('//*[@id="email"]/@value')
                else None
            ),
            "name": (
                tree.xpath('//*[@id="elm_15"]/@value')[0]
                if tree.xpath('//*[@id="elm_15"]/@value')
                else None
            ),
            "surname": (
                tree.xpath('//*[@id="elm_17"]/@value')[0]
                if tree.xpath('//*[@id="elm_17"]/@value')
                else None
            ),
            "city": (
                tree.xpath('//*[@id="elm_23"]/@value')[0]
                if tree.xpath('//*[@id="elm_23"]/@value')
                else None
            ),
        }
        return user_info
    except Exception as e:
        print(e)
        return None


def parse_wishlist(session):
    try:
        response = session.get("https://siriust.ru/wishlist/")
        response.raise_for_status()
        html_wishlist = response.text
        tree = lxml.html.document_fromstring(html_wishlist)

        product_elements = tree.xpath('//div[@class="col-tile"]')
        products = []

        for element in product_elements:
            try:
                name = (
                    element.xpath('.//a[@class="product-title"]/text()')[0]
                    if element.xpath('.//a[@class="product-title"]/text()')
                    else None
                )
                price_roz, price_opt = [
                    float(el.replace("\xa0", ""))
                    for el in element.xpath('.//span[@class="ty-price-num"]/text()')
                ]

                link = (
                    element.xpath('.//a[@class="product-title"]/@href')[0]
                    if element.xpath('.//a[@class="product-title"]/@href')
                    else None
                )

                if link:
                    product_data = get_product_details(session, link)
                    if product_data:
                        product_data["Название"] = name
                        product_data["Цена розница"] = price_roz
                        product_data["Цена оптовая"] = price_opt
                        products.append(product_data)
            except Exception as e:
                print(f"Error processing a product: {e}")
    except Exception as e:
        print(f"Error processing wishlist: {e}")
    return products


def get_product_details(session, product_url):
    try:
        response = session.get(product_url)
        response.raise_for_status()
        html_product = response.text
        product_page = lxml.html.document_fromstring(html_product)

        rating = (
            product_page.xpath(
                './/div[@itemprop="aggregateRating"]/meta[@itemprop="ratingValue"]/@content'
            )[0]
            if product_page.xpath(
                './/div[@itemprop="aggregateRating"]/meta[@itemprop="ratingValue"]/@content'
            )
            else None
        )
        reviewCount = (
            product_page.xpath(
                './/div[@itemprop="aggregateRating"]/meta[@itemprop="reviewCount"]/@content'
            )[0]
            if product_page.xpath(
                './/div[@itemprop="aggregateRating"]/meta[@itemprop="reviewCount"]/@content'
            )
            else None
        )

        store_count = int(
            product_page.xpath('count(//*[@id="content_features"]/div/div)')
        )

        reviews = product_page.xpath(
            '//div[@id="content_discussion_block"]//div[@class="ty-discussion-post__message"]/text()'
        )
        reviews = [it.replace("\r\n", "") for it in reviews]

        product_data = {
            "Рейтинг": rating,
            "Количество оценок": reviewCount,
            "Количество магазинов с товаром": store_count,
            "Отзывы": reviews,
        }
        return product_data

    except requests.exceptions.RequestException as e:
        print(f"Error retrieving product details: {e}")
        return None
    except lxml.etree.XPathError as e:
        print(f"Error parsing product details page: {e}")
        return None
    except Exception as e:
        print(f"Error processing product details: {e}")
        return None


if __name__ == "__main__":
    session = create_session()
    login(session, input("Введите логин: "), input("Введите пароль: "))

    user_info = parse_user_info(session)
    for key, value in user_info.items():
        print(f"{key}: {value}")

    wishlist_products = parse_wishlist(session)
    for product in wishlist_products:
        print(product)
