import os
import requests
from urllib.parse import urljoin
import bs4
import datetime
import pymongo
from dotenv import load_dotenv


class MagnitParser:
    def __init__(self, start_url, data_client):
        self.start_url = start_url
        self.data_client = data_client
        self.data_base = self.data_client["gb_parse_13_01_2021"]

    @staticmethod
    def _get_response(url, *args, **kwargs):
        while True:
            try:
                response = requests.get(url, *args, **kwargs)
                if response.status_code > 399:
                    raise ParseError(response.status_code)
                time.sleep(0.1)
                return response
            except (requests.RequestException, ParseError):
                time.sleep(0.5)
                continue

    @staticmethod
    def _get_soup(response):
        return bs4.BeautifulSoup(response.text, "lxml")

    def run(self):
        for product in self.parse(self.start_url):
            self.save(product)

    def parse(self, url) -> dict:
        soup = self._get_soup(self._get_response(url))
        catalog_main = soup.find("div", attrs={"class": "сatalogue__main"})
        for product_tag in catalog_main.find_all("a", attrs={"class": "card-sale"}):
            yield self._get_product_data(product_tag)

    ''' классы необходимых полей:

        promo_name =  card-sale__header
        old_price = label__price_old:
            label__price-integer
            label__price-decimal
        new_price =label__price_new: 
            label__price-integer
            label__price-decimal

        image_url = card-sale__col_img
        data_from: ...card-sale__date).findChildren[0]
        data_to: ....card-sale__date).findChildren[1]
'''

    @property
    def data_template(self):
        return {
            "url": lambda tag: urljoin(self.start_url, tag.attrs.get("href")),
            "promo_name": lambda tag: tag.find('div', {'class': 'card-sale__header'}),
            "title": lambda tag: tag.find('div', attrs={"class": "card-sale__title"}).text,
            "old_price": lambda tag: '.'.join (item for item in tag.find("div", attrs={"class": "label__price_old"}).text.split()),
            "new_price": lambda tag: '.'.join (item for item in tag.find("div", attrs={"class": "label__price_new"}).text.split()),
            "image_url": urljoin(self.start_url, tag.find("img").attrs.get("data-src")),
            'date_from': lambda tag: self.get_date(tag, 0),
            'date_to': lambda tag: self.get_date(tag, 1)
        }

    @staticmethod
    def get_date(product_tag, binary: bin) -> datetime:
        try:
            date = product_tag.find('div', class_='card-sale__date').findChildren()[binary].text[2:].strip()
            return datetime.strptime(f"{date} {datetime.now().year}", "%d %B %Y")
        except:
            pass

    def _get_product_data(self, product_tag: bs4.Tag) -> dict:
        data = {}
        for key, pattern in self.data_template.items():
            try:
                data[key] = pattern(product_tag)
            except AttributeError:
                pass
        return data

    def save(self, data):
        collection = self.data_base["magnit"]
        collection.insert_one(data)
        pass
'''
if __name__ == '__main__':
    load_dotenv(".env")
    data_base_url = os.getenv("DATA_BASE_URL")
    data_client = pymongo.MongoClient(data_base_url)
    url = "https://magnit.ru/promo/?geo=moskva"
    parser = MagnitParser(url, data_client)
    parser.run()
'''