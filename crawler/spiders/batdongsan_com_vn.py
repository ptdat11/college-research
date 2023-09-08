import scrapy
from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor

class BatdongsanComVnSpider(scrapy.Spider):
    name = "batdongsan_com_vn"
    collection_name = "batdongsan_com_vn"
    allowed_domains = ["batdongsan.com.vn"]
    start_urls = ["https://batdongsan.com.vn/nha-dat-ban"]

    def parse(self, response):
        print(response)
        pass