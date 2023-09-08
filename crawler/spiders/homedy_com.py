import scrapy
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from typing import Literal

class HomedyComSpider(CrawlSpider):
    name = "homedy_com"
    collection_name = "homedy_com"
    allowed_domains = ["homedy.com"]
    start_urls = ["https://homedy.com/"]

    rules = (Rule(LinkExtractor(allow=r"Items/"), callback="parse_item", follow=True),)

    def __init__(self, type: Literal["ban"] | Literal["thue"] = "ban", **kw):
        if type == "ban":
            self.start_urls = ["https://homedy.com/ban-nha-dat"]
        elif type == "thue":
            self.start_urls = ["https://homedy.com/cho-thue-nha-dat"]
        super().__init__(**kw)

    def parse_item(self, response):
        item = {}
        #item["domain_id"] = response.xpath('//input[@id="sid"]/@value').get()
        #item["name"] = response.xpath('//div[@id="name"]').get()
        #item["description"] = response.xpath('//div[@id="description"]').get()
        return item
