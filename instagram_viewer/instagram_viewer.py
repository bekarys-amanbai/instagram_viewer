import json

from string import Template
from datetime import datetime

import requests

from .insta_obj import InstagramPost, InstagramPostItems


def find_slice(string: str, start_str: str, end_str: str) -> str:
    start = string.find(start_str) + len(start_str)
    end = string.find(end_str, start)

    return string[start:end]


def get_query_hash() -> str:
    url = 'https://www.instagram.com/static/bundles/es6/ConsumerLibCommons.js/ba94eb403c1d.js'
    js_code = requests.get(url).text
    start = 'o.pagination},queryId:"'
    end = '"'
    return find_slice(js_code, start, end)


class InstagramViewer:
    def __init__(self, url: str):
        self.url = url

        headers = {
            'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'
        }
        html_page = requests.get(self.url, headers=headers).text
        start = 'window._sharedData = '
        end = ';</script>'
        json_str = find_slice(html_page, start, end)

        raw_json = json.loads(json_str)
        raw_posts = (raw_json['entry_data']['ProfilePage'][0]['graphql']['user']
                             ['edge_owner_to_timeline_media']['edges'])

        self.last_12_posts = self._handler(raw_posts)

        self.biography = raw_json['entry_data']['ProfilePage'][0]['graphql']['user']['biography']
        self.full_name = raw_json['entry_data']['ProfilePage'][0]['graphql']['user']['full_name']
        self.username = raw_json['entry_data']['ProfilePage'][0]['graphql']['user']['username']
        self.id = raw_json['entry_data']['ProfilePage'][0]['graphql']['user']['id']
        self.avatar = raw_json['entry_data']['ProfilePage'][0]['graphql']['user']['profile_pic_url_hd']
        self.count_posts = (raw_json['entry_data']['ProfilePage'][0]['graphql']['user']
                                    ['edge_owner_to_timeline_media']['count'])

        self._has_next_page = (raw_json['entry_data']['ProfilePage'][0]['graphql']['user']
                                       ['edge_owner_to_timeline_media']['page_info']['has_next_page'])
        self._end_cursor = (raw_json['entry_data']['ProfilePage'][0]['graphql']['user']
                                    ['edge_owner_to_timeline_media']['page_info']['end_cursor'])

        query_hash = '02e14f6a7812a876f7d133c9555b1151'
        self._next_url_template = Template(f'https://www.instagram.com/graphql/query/?query_hash={query_hash}'
                                           f'&variables={{"id":"{self.id}","first":$count,"after":"$cursor"}}')

    def get_next_posts(self, count: int = 12) -> list[InstagramPost]:
        """ count max 50 """
        if self._has_next_page:
            headers = {
                'Accept-Language': 'ru-RU,ru;q=0.8,en-US;q=0.5,en;q=0.3',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:88.0) Gecko/20100101 Firefox/88.0'
            }
            url = self._next_url_template.substitute(count=count, cursor=self._end_cursor)
            r = requests.get(url, headers=headers)
            raw_json = r.json()

            raw_posts = raw_json['data']['user']['edge_owner_to_timeline_media']['edges']

            self._end_cursor = raw_json['data']['user']['edge_owner_to_timeline_media']['page_info']['end_cursor']
            self._has_next_page = raw_json['data']['user']['edge_owner_to_timeline_media']['page_info']['has_next_page']

            return self._handler(raw_posts)
        else:
            return []

    def get_all_posts(self) -> list[InstagramPost]:
        posts = self.last_12_posts
        while self._has_next_page:
            next_posts = self.get_next_posts(50)
            posts.extend(next_posts)
        return posts

    @staticmethod
    def _handler(raw_posts):
        posts = []
        for raw_post_node in raw_posts:
            raw_post = raw_post_node['node']
            if 'edge_sidecar_to_children' in raw_post:
                items = []
                for raw_post_item_node in raw_post['edge_sidecar_to_children']['edges']:
                    raw_post_item = raw_post_item_node['node']
                    item = {
                        'is_video': raw_post_item['is_video']
                    }
                    if raw_post_item['is_video']:
                        item['url'] = raw_post_item['video_url']
                        item['video_prev'] = raw_post_item['display_url']
                    else:
                        item['url'] = raw_post_item['display_url']
                        item['video_prev'] = ''
                    item_obj = InstagramPostItems(**item)
                    items.append(item_obj)
                post = {
                    'is_slider': True,
                    'items': items,
                }
            else:
                if raw_post['is_video']:
                    url = raw_post['video_url']
                    video_prev = raw_post['display_url']
                else:
                    url = raw_post['display_url']
                    video_prev = ''
                post = {
                    'is_slider': False,
                    'is_video': raw_post['is_video'],
                    'url': url,
                    'video_prev': video_prev,
                    'items': None,
                }
            post['datetime'] = datetime.fromtimestamp(raw_post['taken_at_timestamp'])
            post['post_id'] = raw_post['shortcode']
            post['post_url'] = f'https://www.instagram.com/p/{raw_post["shortcode"]}/'
            post['description'] = raw_post['edge_media_to_caption']['edges'][0]['node']['text']
            post_obj = InstagramPost(**post)
            posts.append(post_obj)

        return posts
