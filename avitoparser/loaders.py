from urllib.parse import urljoin
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join


#def employer_url(employer_id):
#    return urljoin("https://hh.ru/", employer_id)

def clean_output(item):
    return item.replace("\xa0", " ")

def to_float(item):
    item = float(item)
    return item

def clean_params(item):
    selector = Selector(text=item)
    data = {
        "name": selector.xpath("//span[@class='item-params-label']/text()").extract_first(),
        "value": selector.xpath("//a[contains(@class, 'item-params-link')]/text()").get(),
    }
    return data


class ApartLoader(ItemLoader):
    default_item_class = dict
    url_out = TakeFirst()
    title_in = MapCompose(clean_output)
    title_out = TakeFirst()
    price_out = TakeFirst()
    price_in = MapCompose(to_float)
    address_in = MapCompose(clean_output)
    address_out = Join('')
    apart_params_in = MapCompose(clean_params)
    author_url = TakeFirst()
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("response"):
            self.add_value("url", self.context["response"].url)
