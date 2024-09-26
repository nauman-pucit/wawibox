try:
    import pkg_resources.py2_warn
except ImportError:
    pass

import json
import csv
import random

import scrapy
from scrapy.crawler import CrawlerProcess

csv_columns = ["name", "image", "sku", "url", "brand", "lowest_price", "supplier", "supplier_rating", "supplier_reviews"]
csvfile = open('wawibox_new.csv', 'a', newline='', encoding="utf-8")
writer = csv.DictWriter(csvfile, fieldnames=csv_columns)
writer.writeheader()

done_file = open('done_products.txt', 'r', encoding='utf-8')
done_products = done_file.read().split('\n')
done_products = [v for v in done_products if v.strip()]
done_file = open('done_products.txt', 'a', encoding='utf-8')

cookies = {
    '_ALGOLIA': 'anonymous-b4e9fffe-dda1-414d-8792-a5c88c1a2d75',
    'wb-opened-login-modal': 'true',
    '_gcl_au': '1.1.734605861.1726395730',
    'hubspotutk': '72a4474a84b1864627d62fa61dabf2dc',
    '__hssrc': '1',
    'intercom-id-40wd3nut': 'dda7ce86-ad0e-4d85-879d-ac1c05cbc278',
    'intercom-session-40wd3nut': '',
    'intercom-device-id-40wd3nut': '0e27950b-031a-4e60-adb7-cd30c7c11dc2',
    'wb-search-query-id': '6b0c61f929567b413a4ec3c58e96d285',
    '_gid': 'GA1.2.2043776519.1726912255',
    '_gat_UA-46436347-3': '1',
    '_ga_VV0KHC78VJ': 'GS1.1.1726912255.21.0.1726912255.0.0.0',
    '_ga': 'GA1.1.1776988884.1726395730',
    '_uetsid': 'fef879d077fe11efbff4c9215875c5ed',
    '_uetvid': '5dff8cc0734c11ef993fa5e62cb92b71',
    '__hstc': '2592495.72a4474a84b1864627d62fa61dabf2dc.1726395731065.1726819665399.1726912256297.14',
    '__hssc': '2592495.1.1726912256297',
}

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-language': 'en-US,en;q=0.9,zh-TW;q=0.8,zh;q=0.7',
    'cache-control': 'max-age=0',
    # 'cookie': '_ALGOLIA=anonymous-b4e9fffe-dda1-414d-8792-a5c88c1a2d75; wb-opened-login-modal=true; _gcl_au=1.1.734605861.1726395730; hubspotutk=72a4474a84b1864627d62fa61dabf2dc; __hssrc=1; intercom-id-40wd3nut=dda7ce86-ad0e-4d85-879d-ac1c05cbc278; intercom-session-40wd3nut=; intercom-device-id-40wd3nut=0e27950b-031a-4e60-adb7-cd30c7c11dc2; wb-search-query-id=6b0c61f929567b413a4ec3c58e96d285; _gid=GA1.2.2043776519.1726912255; _gat_UA-46436347-3=1; _ga_VV0KHC78VJ=GS1.1.1726912255.21.0.1726912255.0.0.0; _ga=GA1.1.1776988884.1726395730; _uetsid=fef879d077fe11efbff4c9215875c5ed; _uetvid=5dff8cc0734c11ef993fa5e62cb92b71; __hstc=2592495.72a4474a84b1864627d62fa61dabf2dc.1726395731065.1726819665399.1726912256297.14; __hssc=2592495.1.1726912256297',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Chromium";v="128", "Not;A=Brand";v="24", "Google Chrome";v="128"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0.0.0 Safari/537.36',
}


class Wawibox(scrapy.Spider):
    name = 'wawibix'
    title = 'wawibix'

    all_cars = []
    custom_settings = {'ROBOTSTXT_OBEY': False, 'DOWNLOAD_TIMEOUT': 10,
                       # 'CONCURRENT_REQUESTS': 1, 'DOWNLOAD_DELAY': 1,
                       'RETRY_TIMES': 5, 'RETRY_HTTP_CODES': [403]}


    @staticmethod
    def get_dict_value(data, key_list, default=''):
        """
        gets a dictionary and key_list, apply key_list sequentially on dictionary and return value
        :param data: dictionary
        :param key_list: list of key
        :param default: return value if key not found
        :return:
        """
        for key in key_list:
            if data and isinstance(data, dict):
                data = data.get(key, default)
            else:
                return default
        return data

    def start_requests(self):

        p_file = open('products.txt', 'r', encoding='utf-8')
        product_urls = p_file.read().split('\n')
        for p_url in product_urls:
            if p_url in done_products:
                continue
            yield scrapy.Request(p_url,
                                 # meta={'proxy': "http://{}".format(random.choice(proxy))},
                                 headers=headers,
                                 cookies=cookies)

    def parse(self, response):
        done_file.write('{}\n'.format(response.url))
        done_file.flush()
        try:
            data = json.loads([v.css('::text').extract_first('') for v in response.css('script') if 'image' in v.css('::text').extract_first('')][0].replace('\n', ' ').replace('\r', ''))
            data2 = json.loads([v.css('::text').extract_first('') for v in response.css('script') if 'image' in v.css('::text').extract_first('')][1])
            data2 = json.loads(data2[5])
        except Exception as e:
            print(str(e))
            return
        item = dict()
        item['name'] = data['name']
        item['image'] = data['image']
        item['sku'] = data['sku']
        item['url'] = response.url
        item['brand'] = self.get_dict_value(data, ['manufacturer', 'name'])
        try:
            item['lowest_price'] = data2['offers'][0]['price']
            item['supplier'] = data2['offers'][0]['supplier']['name']
            item['supplier_rating'] = data2['offers'][0]['supplier']['rating']
            item['supplier_reviews'] = data2['offers'][0]['supplier']['ratings']
        except:
            return
        writer.writerow(item)
        csvfile.flush()
        yield item


process = CrawlerProcess({
    'USER_AGENT': 'Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 5.1)'
})

process.crawl(Wawibox)
process.start()
