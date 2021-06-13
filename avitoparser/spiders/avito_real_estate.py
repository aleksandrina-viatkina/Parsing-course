import scrapy
from avitoparser.spiders.xpath_selectors import ADV_PAGE, CATEGORY_XPATH, ADV_LINK_XPATH

from avitoparser.loaders import ApartLoader

class AvitoRealEstateSpider(scrapy.Spider):
    name = 'avito_real_estate'
    allowed_domains = ['avito.ru']
    start_urls = ['https://www.avito.ru/krasnodar/nedvizhimost']


    def _get_follow(self, response, xpath, callback):
        for a_link in response.xpath(xpath):
            yield response.follow(a_link, callback=callback)

    #заходим в подраздел "все квартиры"
    def parse(self, response):
        yield from self._get_follow(response, CATEGORY_XPATH, self.pages_parse)

    def pages_parse(self, response, paginate = True):
        yield from self._get_follow(response, ADV_LINK_XPATH, self.adv_parse)

        for page_num in range(2, 101) if paginate else []:
            yield response.follow(f"?p={page_num}", callback=self.parse)

    def adv_parse(self, response):
        loader = ApartLoader(response=response)
        for key, xpath in ADV_PAGE.items():
            loader.add_xpath(key, xpath)
        data = loader.load_item()
        yield data

