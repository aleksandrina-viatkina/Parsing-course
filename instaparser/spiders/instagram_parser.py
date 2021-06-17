# ПО API

import scrapy
from ..items import Tag, Post
from datetime import datetime
import json
import requests
from instaparser import settings

class InstagramParserSpider(scrapy.Spider):
    name = 'instagram_parser'
    allowed_domains = ['www.instagram.com', 'instagram.com']
    start_urls = ['https://www.instagram.com/accounts/login/']
    _login_url = "https://www.instagram.com/accounts/login/ajax/"
    _tags_path = '/explore/tags/{tag}'


    def __init__(self, login, password, tags, *args, **kwargs):
        super(InstagramParserSpider, self).__init__(*args, **kwargs)
        self.login = login
        self.password = password
        self.tags = tags

    def parse(self, response):
        try:
            js_data = self.js_data_extract(response)
            yield scrapy.FormRequest(
                self._login_url,
                method="POST",
                callback=self.parse,
                formdata={"username": self.login, "enc_password": self.password},
                headers={"X-CSRFToken": js_data["config"]["csrf_token"]}
            )
        except AttributeError:
            r_data = response.json()
            if r_data.get("authenticated"):
                for tag in self.tags:
                    url = self._tags_path.format(tag=tag)
                    callbacks = [self.tag_parse, self.post_parse]
                    for callback in callbacks:
                        yield response.follow(url, callback=callback)


    def tag_parse(self, response):
        js_data = self.js_data_extract(response)
        tag_data = js_data['entry_data']['TagPage'][0]['data']
        yield Tag(
            date_parse= datetime.now(),
            data={'id': tag_data['id'],
                  'name': tag_data['name'],
                  'description': tag_data['description'],
                  'post_counts': tag_data['formatted_media_count']},
            images = f'{response.url}{tag_data["profile_pic_url"]}')

    def post_parse(self, response):
        page = 1
        while page:
            js_data = self.js_data_extract(response)
            for i in range(0, 3):
                for j in range(0, 3):
                    post_data = js_data['entry_data']['TagPage'][0]['data']['top']['sections'][i]['layout_content']['medias'][j]['media']
                    yield Post(
                        date_parse = datetime.now(),
                        data = {'id': post_data['id'],
                                'username': post_data['user']['full_name'],
                                'is_private': post_data['user']['is_private'],
                                'taken_at': post_data['taken_at'],
                                'likes': post_data['like_count'],
                                },
                        images = post_data["code"])

            next_max_id = js_data['entry_data']['TagPage'][0]['data']['top']['next_max_id']
            tag = js_data['entry_data']['TagPage'][0]['data']['name']
            page += 1
            params = {'page': page,
                      'max_id': next_max_id}
            headers = {
                'USER_AGENT': settings.USER_AGENT
            }
            r = requests.post(f'https://i.instagram.com/api/v1/tags/{tag}/sections/', params=params, headers = headers)
            yield response.follow(r.url, callback=self.post_parse)

    def js_data_extract(self, response):
        js = response.xpath(
            "//script[contains(text(), 'window._sharedData = ')]/text()").extract_first()
        start_idx = js.index('{')
        data = json.loads(js[start_idx:-1])
        return data



