# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy.item import Item, Field

class Tag(Item):
    _id = Field()
    tag_name = Field()
    date_parse = Field(required=True)
    data = Field()
    images = Field()

class Post(Item):
    _id = Field()
    date_parse = Field(required=True)
    data = Field()
    images = Field()
