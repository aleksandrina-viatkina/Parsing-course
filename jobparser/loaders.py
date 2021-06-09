from urllib.parse import urljoin
from scrapy import Selector
from scrapy.loader import ItemLoader
from itemloaders.processors import TakeFirst, MapCompose, Join


def employer_url(employer_id):
    return urljoin("https://hh.ru/", employer_id)

def clean_output(item):
    return item.replace("\xa0", " ")

class VacancyLoader(ItemLoader):
    default_item_class = dict
    item_type_out = TakeFirst()
    url_out = TakeFirst()
    title_out = TakeFirst()
    salary_in = MapCompose(clean_output)
    salary_out = Join('')
    description_in = MapCompose(clean_output)
    description_out = Join(' ')
    skills_in = MapCompose(clean_output)
    employer_url_in = MapCompose(employer_url)
    employer_url_out = TakeFirst()

    #Добавили item_type, чтобы через pipeline сохранять вакансии и работодателей в разные коллекции
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("response"):
            self.add_value("url", self.context["response"].url)
        self.add_value("item_type", "vacancy")

class EmployerLoader(ItemLoader):
    default_item_class = dict
    item_type_out = TakeFirst()
    name_in = MapCompose(clean_output)
    site_out = TakeFirst()
    business_fields_out = MapCompose(lambda fields: [field.capitalize() for field in fields.split(', ')])
    description_in = MapCompose(clean_output)
    description_out = Join('')
    url_out = TakeFirst()

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.context.get("response"):
            self.add_value("url", self.context["response"].url)
        self.add_value("item_type", "company")