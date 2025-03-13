import lxml.html
import requests
import lxml
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


with open("site.html", "w", encoding="utf-8") as f:
    f.write(html_wishlist)
