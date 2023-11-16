import html
import json
import random
import string
from datetime import datetime
from urllib.parse import urlencode
import random

import scrapy
from scrapy.downloadermiddlewares.retry import get_retry_request
from w3lib.url import add_or_replace_parameter, add_or_replace_parameters

from ..helpers.get_data import get_keywords
from ..items import DomainItem, KeywordItem
from ..helpers.send_to_storeleads import send


class KeywordSpider(scrapy.Spider):
    name = 'keyword-spider'

    search_url = 'https://www.facebook.com/ads/library/async/search_ads/'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.2; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Chrome/36.0.1985.125 CrossBrowser/36.0.1985.138 Safari/537.36',
        'Accept': '*/*',
        'Connection': 'keep-alive',
        'Referer': 'https://www.facebook.com/ads/library/?active_status=all&ad_type=all&country=NL&sort_data[direction]=desc&sort_data[mode]=relevancy_monthly_grouped&search_type=keyword_unordered&media_type=all',
        'content-type': 'application/x-www-form-urlencoded'
    }
    payload = {'__a': '1'}
    parameters = {
        'count': '30',
        'active_status': 'all',
        'ad_type': 'all',
        'countries[0]': 'ALL',
        'media_type': 'all',
        'search_type': 'keyword_exact_phrase'
    }

    def generate_lsd_token(self):
        characters = list(string.ascii_lowercase + string.ascii_uppercase + string.digits)
        token = ''.join([random.choice(characters) for _ in range(9)])
        return f'AV{token}'

    def start_requests(self):
        lsd_token = self.generate_lsd_token()
        while True:
            keywords = get_keywords()
            keyword_item = KeywordItem()
            keyword_item['country'] = random.choice(list(keywords.keys()))
            keyword_item['keyword'] = random.choice(keywords[keyword_item['country']])
            parameters = {**self.parameters, 'q': f'"{keyword_item["keyword"]}"', 'country': f'"{keyword_item["country"]}"', 'search_type': 'keyword_unordered'}
            headers = {**self.headers, 'x-fb-lsd': lsd_token}
            payload = {**self.payload, 'lsd': lsd_token}
            url = add_or_replace_parameters(self.search_url, parameters)

            yield scrapy.Request(
                url,
                self.parse_keyword,
                method='POST',
                headers=headers,
                body=urlencode(payload),
                meta={'HTTPERROR_ALLOW_ALL': True, 'keyword': keyword_item}
            )

    def parse_keyword(self, response):
        raw_ads = self.get_raw_page(response)

        if not raw_ads:
            self.logger.error(f'Temporarily blocked when scraping store {response.meta["keyword"]["keyword"]} in {response.meta["keyword"]["country"]}')
            # added the default retry for now
            new_request_or_none = get_retry_request(
                response.request,
                spider=self,
                reason='empty',
            )
            return new_request_or_none

        total_ads = self.get_total_ads(raw_ads)
        self.logger.info(f'{total_ads} ads found for {response.meta["keyword"]["keyword"]} in {response.meta["keyword"]["country"]}')

        store_urls = []
        for raw_ad in raw_ads['payload']['results']:
            store_url = raw_ad[0]['snapshot']['link_url'].split('/')[2] if raw_ad[0]['snapshot']['link_url'] else None
            if store_url and store_url not in store_urls:
                store_urls.append(store_url)

        request = send(store_urls, response.meta['keyword']['keyword'], response.meta['keyword']['country'], self)
        yield request

    def get_raw_page(self, response):
        try:
            return json.loads(response.text.replace('for (;;);', ''))
        except:
            return {}

    def get_total_ads(self, raw_ads):
        return raw_ads['payload'].get('totalCount')

    def normalize_text(self, text):
        return text.encode('utf-8', 'ignore').decode()
