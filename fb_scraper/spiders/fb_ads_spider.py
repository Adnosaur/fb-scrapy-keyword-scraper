import json
import string
from urllib.parse import urlencode
import random

import scrapy
from scrapy.downloadermiddlewares.retry import get_retry_request
from w3lib.url import add_or_replace_parameter, add_or_replace_parameters

from ..helpers.get_data import get_country_keyword_combinations
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
    possible_proxies = [
        # 'http://customer-adnosaur:8nd7hUAzt4mjU@pr.oxylabs.io:7777',
        'http://proxy:O7wZ1J7@easyport-alt.mobilehop.com:38382',
        'http://proxy:O7wZ1J7@easyport.mobilehop.com:38382'
    ]
    proxy_domains = ['www.facebook.com']
    unique_stores_found = set()

    def generate_lsd_token(self):
        characters = list(string.ascii_lowercase + string.ascii_uppercase + string.digits)
        token = ''.join([random.choice(characters) for _ in range(9)])
        return f'AV{token}'

    def start_requests(self):
        while True:
            lsd_token = self.generate_lsd_token()

            for country, keyword, m_type, start_d, end_d, in get_country_keyword_combinations():
                keyword_params = dict()
                keyword_params['country'] = country
                keyword_params['keyword'] = keyword
                keyword_params['media_type'] = m_type
                keyword_params['start_date'] = start_d
                keyword_params['end_date'] = end_d
                parameters = {**self.parameters, 'q': f'"{keyword_params["keyword"]}"', 'media_type': m_type,
                              'start_date[min]': start_d, '&start_date[max]': end_d,
                              'country': f'"{keyword_params["country"]}"', 'search_type': 'keyword_unordered'}
                headers = {**self.headers, 'x-fb-lsd': lsd_token}
                payload = {**self.payload, 'lsd': lsd_token}
                url = add_or_replace_parameters(self.search_url, parameters)

                yield scrapy.Request(
                    url,
                    self.parse_keyword,
                    method='POST',
                    headers=headers,
                    body=urlencode(payload),
                    meta={'HTTPERROR_ALLOW_ALL': True, 'keyword_params': keyword_params}
                )

    def parse_keyword(self, response):
        self.logger.info(f'TOTAL UNIQUE STORES FOUND SO FAR: {len(self.unique_stores_found)}')
        raw_ads = self.get_raw_page(response)

        if not raw_ads:
            self.logger.error(f'Temporarily blocked when scraping store when making request with following params'
                              f'{json.dumps(response.meta["keyword_params"])}')
            # added the default retry for now
            new_request_or_none = get_retry_request(
                response.request,
                spider=self,
                reason='empty',
            )
            yield new_request_or_none
            return

        total_ads = self.get_total_ads(raw_ads)
        self.logger.info(f'{total_ads} ads found for the following params '
                         f'{json.dumps(response.meta["keyword_params"])}')

        store_urls = []
        for raw_ad in raw_ads['payload']['results']:
            try:
                store_url = raw_ad[0]['snapshot']['link_url'].split('/')[2] \
                    if raw_ad[0]['snapshot']['link_url'] else None
                if store_url and store_url not in store_urls:
                    self.unique_stores_found.add(store_url)
                    store_urls.append(store_url)
            except Exception as e:
                self.logger.error(f'Error parsing an ad {json.dumps(raw_ad[0])} for {e}')

        if store_urls:
            store_leads_request = send(store_urls, response.meta['keyword_params'], self)
            yield store_leads_request

        forward_cursor = raw_ads['payload'].get('forwardCursor')
        page_number = (response.meta.get('page') or 1) + 1
        if not forward_cursor:
            self.logger.info(f'Last Page Reached {page_number} for the request with the following params '
                             f'{json.dumps(response.meta["keyword_params"])}')
            return

        url = add_or_replace_parameter(response.url, 'forward_cursor', forward_cursor)
        url = add_or_replace_parameter(url, 'collation_token', raw_ads['payload']['collationToken'])
        self.logger.info(
            f'PAGINATION: Visiting Page {page_number} For params {json.dumps(response.meta["keyword_params"])}')
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
