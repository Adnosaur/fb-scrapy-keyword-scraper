import scrapy
import json

def connect():
    auth = 'Bearer 9b811603-b8e8-42d5-60c4-63c34af1'
    content_type = 'application/json'
    headers = {'Authorization': auth, 'Content-Type': content_type}
    url = 'https://storeleads.app/json/api/v1/all/list/keywordscraper/add-domains'

    return url, headers

def send(store_urls_item, keyItem, countryItem, spider):
    url, headers = connect()

    data = {'domains': store_urls_item}
    store_urls_count = len(store_urls_item)
    request = scrapy.Request(url, method='PUT', headers=headers, body=json.dumps(data), callback=parse_response, cb_kwargs={'spider': spider, 'store_urls_count': store_urls_count, 'keyItem': keyItem, 'countryItem': countryItem})
    return request

def parse_response(response, spider, store_urls_count, keyItem, countryItem):
    if response.status == 200:
        spider.logger.info(f'RESPONSE: {response.json()}')
        spider.logger.info(f'Successfully sent {store_urls_count} domain names to StoreLeads for {keyItem} in {countryItem}')
    else:
        spider.logger.error(f'Failed to send data to StoreLeads for {keyItem} in {countryItem}')
