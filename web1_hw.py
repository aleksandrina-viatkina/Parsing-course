import json
import time
from pathlib import Path
import requests

class Parse5ka:
    headers = {
        'User-Agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:88.0) Gecko/20100101 Firefox/88.0'
    }

    def __init__(self, start_url, save_path: Path):
        self.start_url = start_url
        self.save_path = save_path

    def _get_response(self, url):
        while True:
            response = requests.get(url, headers=self.headers)
            if response.status_code == 200:
                return response
            time.sleep(0.5)

    def run(self):
        for product in self.parse(self.start_url):
            file_path = self.save_path.joinpath(f"{product['id']}.json")
            self.save(product, file_path)

    # метод, который складывает каждый продукт (который вернул метод parse)
    # в файл .json и сохраняет (с помощью метода save)

    def parse(self, url):
        while url:
            response = self._get_response(url)
            data: dict = response.json()
            url = data["next"]
            for product in data['results']:
                yield product

    # получает из метода get_response ответ на url (пока в next не появится None)
    # возвращает генратор, состоящий из продуктов на странице

    def save(self, data: dict, file_path: Path):
        file_path.write_text(json.dumps(data, ensure_ascii=False))


def get_save_path(dir_name: str) -> Path:
    save_path = Path(__file__).parent.joinpath(dir_name)
    if not save_path.exists():
        save_path.mkdir()
    return save_path

'''
if __name__ == '__main__':
    url = "https://5ka.ru/api/v2/special_offers/"
    product_path = get_save_path('products')
    parser = Parse5ka(url, product_path)
    parser.run()
'''


class ParseCatalog5ka(Parse5ka):

    def __init__(self, start_url, save_path, category_url):
        super().__init__(start_url, save_path)
        self.category_url = category_url

    def category_parse(self, url):
        response = requests.get(url)
        return response.json()

    def run(self):
       # переопределим метод run
        for category in self.category_parse(self.category_url):

            #сложим в каждую категорию продукты

            params = f"?categories={category['parent_group_code']}"
            url = f"{self.start_url}{params}"
            data = {
                "name": category['parent_group_name'],
                "code": category['parent_group_code'],
                "products": list(self.parse(self.start_url))  # список словарей товаров соответсвующих данной категории
            }

            # Создадим директории с названиями "код - название категории"
            category_path = save_path.joinpath(f'{category["parent_group_code"]} - {category["parent_group_name"]}')
            self.save(data, category_path)

if __name__ == '__main__':
    start_url = 'https://5ka.ru/api/v2/special_offers/'
    save_path = get_save_path('catalog')
    category_url = 'https://5ka.ru/api/v2/categories/'
    parser = ParseCatalog5ka(start_url, save_path, category_url)
    parser.run()
