import json
from datetime import datetime

import psycopg2
from psycopg2 import Error
from scrapy.exceptions import DropItem
from scrapy.pipelines.files import FilesPipeline
from scrapy.pipelines.images import ImagesPipeline

from w3lib.url import url_query_cleaner

from .items import *


class StoreLeadsPipeline:
    def __init__(self):
        auth = 'Bearer 9b811603-b8e8-42d5-60c4-63c34af1'
        content_type = 'application/json'
        self.headers = {'Authorization': auth, 'Content-Type': content_type}
        self.url = 'https://storeleads.app/json/api/v1/all/list/keywordscraper/add-domains'

    def open_spider(self, spider):
        spider.logger.info('Sending found domain names to StoreLeads')

    def close_spider(self, spider):
        spider.logger.info('Finished sending found domain names to StoreLeads')

    def process_item(self, item, spider):
        store_urls_item = item['store_urls']
        store_urls_count = len(store_urls_item)
        keyItem = item['keyword']
        countryItem = item['country']

        data = {'domains': store_urls_item}
        request = scrapy.Request(self.url, method='PUT', headers=self.headers, body=json.dumps(data), callback=self.parse_response, cb_kwargs={'store_urls_count': store_urls_count, 'keyItem': keyItem, 'countryItem': countryItem})
        spider.logger.info(f"URL: {request.url}")
        spider.logger.info(f"Method: {request.method}")
        spider.logger.info(f"Headers: {request.headers}")
        spider.logger.info(f"Body: {request.body}")
        spider.logger.info(f'Successfully sent {store_urls_count} domain names to StoreLeads for {keyItem} in {countryItem}')
        return item

    def parse_response(self, response, store_urls_count, keyItem, countryItem):
        if response.status == 200:
            self.logger.info(f'Successfully sent {store_urls_count} domain names to StoreLeads for {keyItem} in {countryItem}')
        else:
            self.logger.error('Failed to send domain name to StoreLeads')