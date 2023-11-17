import json
import string
from urllib.parse import urlencode
import random

import scrapy
from scrapy.downloadermiddlewares.retry import get_retry_request
from w3lib.url import add_or_replace_parameter, add_or_replace_parameters

from ..helpers.get_data import get_country_keyword_combinations
from ..items import KeywordItem
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
    # possible_proxies = [
    #     'http://Poas12ik:z8ai12PP@169.197.83.74:6039',
    # ]
    proxy_domains = ['www.facebook.com']

    def generate_lsd_token(self):
        characters = list(string.ascii_lowercase + string.ascii_uppercase + string.digits)
        token = ''.join([random.choice(characters) for _ in range(9)])
        return f'AV{token}'

    def start_requests(self):
        lsd_token = self.generate_lsd_token()

        for country, keyword in get_country_keyword_combinations():
            keyword_item = KeywordItem()
            keyword_item['country'] = country
            keyword_item['keyword'] = keyword
            parameters = {**self.parameters, 'q': f'"{keyword_item["keyword"]}"',
                          'country': f'"{keyword_item["country"]}"', 'search_type': 'keyword_unordered'}
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

        # store_leads_request = send(store_urls, response.meta['keyword']['keyword'],
        #                            response.meta['keyword']['country'], self)
        # yield store_leads_request

        forward_cursor = raw_ads['payload'].get('forwardCursor')
        if not forward_cursor:
            self.logger.info(f'Last Page Reached for {response.meta["keyword"]["keyword"]} in {response.meta["keyword"]["country"]}')
            return

        url = add_or_replace_parameter(response.url, 'forward_cursor', forward_cursor)
        url = add_or_replace_parameter(url, 'collation_token', raw_ads['payload']['collationToken'])
        self.logger.info(
            f'PAGINATION: For {response.meta["keyword"]["keyword"]} in {response.meta["keyword"]["country"]}')
        yield scrapy.Request(
            url,
            self.parse_keyword,
            body=response.request.body.decode(),
            headers=response.request.headers,
            method='POST',
            meta=response.meta
        )

    def get_raw_page(self, response):
        try:
            raw_page = json.loads(response.text.replace('for (;;);', ''))
            if not raw_page.get('payload'):
                return {}

            return raw_page
        except:
            return {}

    def get_total_ads(self, raw_ads):
        return raw_ads['payload'].get('totalCount')

    def normalize_text(self, text):
        return text.encode('utf-8', 'ignore').decode()
