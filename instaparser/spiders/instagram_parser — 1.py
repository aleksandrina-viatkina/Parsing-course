# ПО GRAPHQL

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
    api_url = '/api/v1/tags/'

    connections = []
    current_tag = ""
    database_collection = ""
    hash = {
        'pagination': '9b498c08113f1e09617a1703c22b2f32',
        'post': '2c4c2e343a8f64c625ba02b2aa12c7f8',
        'user_followers': '5aefa9893005572d237da5068082d8d5',
        'user_followings': '3dec7e2c57367ef3da3d987d89f9dbc8'}


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
                    self.current_tag = tag
                    url = self._tags_path.format(tag=tag)
                    yield response.follow(url, callback=self.tag_parse)

    def get_end_cursor(self, response):
        try:
            js_data = self.js_data_extractor(response)
            return js_data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']
        except AttributeError:
            js_data = response.json()
            return js_data['data']['hashtag']['edge_hashtag_to_media']['page_info']['end_cursor']

    def get_photos_data(self, data):
        try:
            return data['entry_data']['TagPage'][0]['graphql']['hashtag']['edge_hashtag_to_media']['edges']
        except KeyError:
            return data['data']['hashtag']['edge_hashtag_to_media']['edges']

    def tag_parse(self, response):
        # сначала вытаскиваем из первой страницы ссылки на картинки
        self.database_collection = 'Tags'
        try:
            page_data = self.js_data_extractor(response)['entry_data']['TagPage'][0]['graphql']['hashtag']
            yield Tag(
                date_parse=datetime.now(),
                data={'id': page_data['id'],
                      'name': page_data['name'],
                      'profile_pic_url': page_data['profile_pic_url'],
                      'post_counts': page_data['edge_hashtag_to_media']['count']},
                images=page_data['profile_pic_url'])
            posts = self.get_photos_data(self.js_data_extractor(response))
        except AttributeError:
            posts = self.get_photos_data(response.json())
        for post in posts:
            variables = {"shortcode": post['node']['shortcode']}
            url = f"/graphql/query/?query_hash={self.hash['post']}&variables={json.dumps(variables)}"
            yield response.follow(url, callback=self.post_parse)
        # потом добавляем новые файлы
        if self.get_end_cursor(response):
            print("self.get_end_cursor(response)", self.get_end_cursor(response))
            variables = {"tag_name": self.current_tag,
                         "first": 50,
                         "after": self.get_end_cursor(response)}
            url = f"/graphql/query/?query_hash={self.hash['pagination']}&variables={json.dumps(variables)}"
            # to to post page and return to
            yield response.follow(url, callback=self.tag_parse)

    def post_parse(self, response):
        self.database_collection = "Posts"
        post_data = response.json()['data']['shortcode_media']
        yield Post(
            tag_name=self.current_tag,
            date_parse=datetime.now(),
            data=post_data,
            images=post_data['display_url'])


    def js_data_extractor(self, response):
        js = response.xpath(
            "//script[contains(text(), 'window._sharedData = ')]/text()").extract_first()
        start_idx = js.index('{')
        data = json.loads(js[start_idx:-1])
        return data