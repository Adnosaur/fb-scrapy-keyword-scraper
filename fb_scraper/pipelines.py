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
        pass
        # if isinstance(item, DomainItem):
        #     data = {'domain': item['domain']}
        #     response = scrapy.Request(self.url, method='POST', body=json.dumps(data), headers=self.headers)
        #     if response.status_code == 200:
        #         spider.logger.info('Successfully sent domain name to StoreLeads')
        #     else:
        #         spider.logger.error('Failed to send domain name to StoreLeads')
        # return item