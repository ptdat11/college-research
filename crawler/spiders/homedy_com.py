from scrapy.http import Response
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from crawler.items import HomedyVnItem
from bs4 import BeautifulSoup
import bs4
from typing import Literal

class HomedyComSpider(CrawlSpider):
    name = "homedy_com"
    collection_name = "homedy_com"
    allowed_domains = ["homedy.com"]

    rules = [
        Rule(LinkExtractor(allow=r"/p\d+?$")),
        Rule(
            LinkExtractor(allow=r"-es\d+$", deny=r"/p\d+?$"), 
            callback="parse_item", 
        ),
    ]

    attributes_map = {
        "Loại hình": "category",
        "Số phòng ngủ": "bedroom",
        "Tình trạng pháp lý": "legal_status",
        "Hướng nhà": "facing_dir",
        "Hướng ban công": "balcony_dir",
        "Nội thất": "furniture",
        "Số tầng": "floor"
    }

    def __init__(self, type: Literal["ban"] | Literal["thue"] = "ban", **kw):
        if type == "ban":
            self.start_urls = ["https://homedy.com/ban-nha-dat"]
        elif type == "thue":
            self.start_urls = ["https://homedy.com/cho-thue-nha-dat"]
        super().__init__(**kw)

    def parse_item(self, response: Response):
        loader = ItemLoader(
            item=HomedyVnItem(),
            response=response
        )
        soup = BeautifulSoup(response.text, "lxml")

        info = soup.find("div", {"class": "product-info"})
        publish, due, type, id = info.find_all("p", {"class": "code"})
        geolocation = soup.find("div", {"class": "address"}).find_all("span", recursive=False)
        description = soup.find("div", {"class": "description"}).get_text()
        price, area = soup.find("div", {"class": "product-short-info"}).find_all("strong")
        attr_html = soup.find("div", {"class": "product-attributes"})
        attrs = self.extract_attributes(attr_html)

        loader.add_value("_id", id.string)
        loader.add_value("title", soup.h1.string)
        loader.add_value("url", response.url)
        loader.add_value("publish_date", publish.string)
        loader.add_value("due_date", due.string)
        loader.add_value("info_type", type.string)
        for loc in geolocation:
            loader.add_value("geolocation", loc.string)
        loader.add_value("price", price.get_text())
        loader.add_value("area", area.get_text())
        loader.add_value("description", description)
        for key, value in attrs.items():
            loader.add_value(key, value)

        item = loader.load_item()
        return item
    
    def extract_attributes(self, attr_html: bs4.Tag | None):
        attrs = attr_html.find_all("div", {"class": "product-attributes--item"})
        attrs_dict = {}
        for attr in attrs:
            key, value = attr.find_all("span")
            key, value = key.string, value.string
            if key in self.attributes_map:
                mapped_key = self.attributes_map[key]
                attrs_dict[mapped_key] = value
        return attrs_dict