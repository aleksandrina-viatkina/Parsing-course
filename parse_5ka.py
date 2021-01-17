import json
import time
from pathlib import Path
import requests
'''
url = 'https://5ka.ru/api/v2/special_offers/'
response: requests.Response = requests.get(url)
#print(response.status_code)
#print(response.headers)
print(response.request.headers)
'''


class ParseError(Exception):
    def __init__(self, text):
        self.text = text


class Parse5ka:
    _headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.60 YaBrowser/20.12.0.963 Yowser/2.5 Safari/537.36",
    }
    _params = {
        "records_per_page": 50,
    }

    def __init__(self, start_url: str, result_path: Path):
        self.start_url = start_url
        self.result_path = result_path

    @staticmethod
    def _get_response(url: str, *args, **kwargs) -> requests.Response:
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

    def run(self):
        for product in self.parse(self.start_url):
            file_path = self.result_path.joinpath(f'{product["id"]}.json')
            self.save(product, file_path)

    def parse(self, url: str) -> dict:
        while url:
            response = self._get_response(
                url, params=self._params, headers=self._headers
            )
            data = response.json()
            url = data["next"]
            for product in data["results"]:
                yield product

    @staticmethod
    def save(data: dict, file_path: Path):
        with file_path.open("w", encoding="utf-8") as file:
            json.dump(data, file, ensure_ascii=False)

'''
if __name__ == "__main__":
    url = "https://5ka.ru/api/v2/special_offers/"
    result_path = Path(__file__).parent.joinpath("products")
    parser = Parse5ka(url, result_path)
    parser.run()
'''

# ***** Домашнее задание к уроку №1 *****

#создаем наследующий класс. Класс будет наследовать характеристики класса-родителя
#добавляется параметр categories_start_url, по этой ссылке будем парсить категории

class ParseCatalogs5ka(Parse5ka):

    def __init__(self, categories_start_url, start_url, result_path):
        super().__init__(start_url, result_path)
        self.categories_start_url = categories_start_url

    def parse_categories(self, url) -> list:
        response = self._get_response(url)
        return response.json()

    '''
    переопределяем метод run таким, образом, чтобы при парсинге каждая категория создавалась отдельной директорией
    с именем "код - наименование"
    '''

    def run(self):
        for category in self.parse_categories(self.categories_start_url):
            category_path = self.result_path.joinpath(
                f'{category["parent_group_code"]} - {category["parent_group_name"]}.json')
            self.save(category, category_path)

    '''
    Парсим продукты, распределяя их по категориями(в параметры добавляем ключ "имя категории"
    '''

    def get_products_into_categories(self):
        for category in self.parse_categories(self.categories_start_url):
            self._params['category'] = category['parent_group_code']
            category['products'] = list(self.parse(self.start_url))
            self.save(category, self.category_path)


if __name__ == "__main__":
    url = "https://5ka.ru/api/v2/special_offers/"
    result_path = Path(__file__).parent.joinpath("products")
    parser = ParseCatalogs5ka('https://5ka.ru/api/v2/categories/', url, result_path)
    parser.run()

