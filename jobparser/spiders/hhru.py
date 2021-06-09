import scrapy
from jobparser.loaders import VacancyLoader, EmployerLoader
from jobparser.spiders.xpath_selectors import PAGE_XPATH, VACANCY_DATA_XPATH, EMPLOYER_DATA_XPATH


from copy import copy
from urllib.parse import urlencode

class HhruSpider(scrapy.Spider):
    name = 'hhru'
    allowed_domains = ['hh.ru']
    start_urls = ['https://hh.ru/search/vacancy?schedule=remote&L_profession_id=0&area=113']
    api_vacancy_list_path = "/shards/employerview/vacancies"
    api_vacancy_list_params = {
        "page": 0,
        "currentEmployerId": None,
        "json": True,
        "regionType": "OTHER",
        "disableBrowserCache": True,
    }

    def _get_follow(self, response, xpath, callback):
        for a_link in response.xpath(xpath):
            yield response.follow(a_link, callback=callback)

    def parse(self, response):
        yield from self._get_follow(response, PAGE_XPATH['pagination_button'], self.parse)
        yield from self._get_follow(response, PAGE_XPATH['vacancy_page'], self.vacancy_parse)

    def vacancy_parse(self, response):
        loader = VacancyLoader(response=response)
        for key, xpath in VACANCY_DATA_XPATH.items():
            loader.add_xpath(key, xpath)
        data = loader.load_item()
        yield response.follow(data['employer_url'], callback=self.employer_parse)
        yield data

    def employer_parse(self, response):
        loader = EmployerLoader(response=response)
        for key, xpath in EMPLOYER_DATA_XPATH.items():
            loader.add_xpath(key, xpath)
        data = loader.load_item()

        #соберем список вакансий работодателя по api
        employer_id = response.url.split("/")[-1]
        params = copy(self.api_vacancy_list_params)
        params["currentEmployerId"] = employer_id
        yield response.follow(
            self.api_vacancy_list_path + "?" + urlencode(params),
            callback=self.api_vacancy_list_parse,
            cb_kwargs=params
        )
        yield data

    def api_vacancy_list_parse(self, response, **params):
        data = response.json()
        if data['@hasNextPage']:
            params["page"] += 1
            yield response.follow(
                self.api_vacancy_list_path + "?" + urlencode(params),
                callback=self.api_vacancy_list_parse,
                cb_kwargs=params
            )
        for vacancy in data['vacancies']:
            yield response.follow(
                vacancy["links"]["desktop"],
                callback=self.vacancy_parse
            )





