import scrapy
import re
import pymongo
import base64

class AutoyoulaSpider(scrapy.Spider):
    name = 'autoyoula'
    allowed_domains = ['auto.youla.ru']
    start_urls = ['http://auto.youla.ru/']
    client_db = pymongo.MongoClient("mongodb://localhost:27017")

    def _get_follow(self, response, selector_str, callback):
        for a_link in response.css(selector_str):
            url = a_link.attrib.get("href")
            yield response.follow(url, callback=callback)

    # метод для извлечения страниц брендов авто
    def parse(self, response):
        yield from self._get_follow(
            response,
            ".TransportMainFilters_brandsList__2tIkv a.blackLink",
            self.brand_parse
        )

    #метод для извлечения страниц пагинации в каждом бренде авто
    def brand_parse(self, response):
        yield from self._get_follow(
            response,
            ".Paginator_block__2XAPy a.Paginator_button__u1e7D",
            self.brand_parse
        )
        yield from self._get_follow(
            response,
            "a.SerpSnippet_name__3F7Yu.blackLink",
            self.adv_parse
        )


    #метод для перехода из страниц пагинации в страницы автомобилей
    #переименовала метод который был дан на уроке под названием car_parse
    def adv_parse(self, response):
       adv_data = {
           'url': response.url,
           'title': response.css('.AdvertCard_advertTitle__1S1Ak::text').get(),
           'photos_list': [itm.attrib.get("src") for itm in response.css("figure.PhotoGallery_photo__36e_r img")],
           'characterictics': [{
               "name": itm.css(".AdvertSpecs_label__2JHnS::text").extract_first(),
               "value": itm.css(".AdvertSpecs_data__xK2Qx::text").extract_first()}
                for itm in response.css("div.AdvertCard_specs__2FEHc .AdvertSpecs_row__ljPcX")],
           "description": response.css('.AdvertCard_descriptionInner__KnuRi::text').get(),
           "author_url": self.author_info_parse(response),
       }
       self.client_db['gb_hw4']['autoyoula_parse'].insert_one(adv_data)



    def author_info_parse(self, response):
        scripts = response.css('script')
        # Из всех скриптов отберем только скрипт с transitState
        transit_state = '<script>window.transitState'
        for script in scripts:
            script_code = script.get()
            if script.get().startswith(transit_state):
            # часть скрипта с id автора - youlaId%22%2C%226085fdd0f2c79a6f1142292c%22%2C%22
                pattern = re.compile('youlaId%22%2C%22(\w{1,})%22%2C%22')
                author_id = re.findall(pattern, script_code)[1]
                author = f"https://youla.ru/user/{author_id}"
                #часть скрипта с телефоном - phone%22%2C%22(S3pjZ0tEZ3hNaWtnTkRJMkxUVTRMVGsyXw%3D%3D)%22%2C%22
                #pattern = re.compile('phone%22%2C%22(\w{1,}%3D%3D)%22%2C%22')
                #phone_code = re.findall(pattern, script_code)
                #phones = [(phone.replace("%3D", "")) for phone in phone_code]
                #phone = base64.b64decode(base64.b64decode(phones))
        return author


    #def decode_phone(self,phone):
     #   base64.b64decode(base64.b64decode(phone)
      #  return phone



