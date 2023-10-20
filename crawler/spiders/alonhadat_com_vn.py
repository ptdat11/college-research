from scrapy.http import Response
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from crawler.items import AlonhadatComVnItem
from bs4 import BeautifulSoup
import bs4
from typing import Literal

class AlonhadatComVnSpider(CrawlSpider):
    name = "alonhadat_com_vn"
    collection_name = "alonhadat_com_vn"
    allowed_domains = ["alonhadat.com.vn"]

    rules = [
        Rule(LinkExtractor(allow=r"/trang--\d+.html$")),
        Rule(
            LinkExtractor(allow=r"-\d+.html$", deny=r"/trang--\d+.html$"), 
            callback="parse_item"
        )
    ]

    info_map = {
        "Mã tin": "_id",
        "Loại tin": "news_type",
        "Loại BDS": "category",
        "Chiều ngang": "width",
        "Chiều dài": "height",
        "Hướng": "facing_dir",
        "Đường trước nhà": "entrance_length",
        "Pháp lý": "legal_status",
        "Số lầu": "floor",
        "Số phòng ngủ": "bedroom",
        "Phòng ăn": "dining_room",
        "Nhà bếp": "kitchen",
        "Sân thượng": "terrace",
        "Chổ để xe hơi": "car_storage",
        "Chính chủ": "verified_owner"
    }

    def __init__(self, type: Literal["mua"] | Literal["thue"] = "mua", **kw):
        if type == "mua":
            self.start_urls = ["https://alonhadat.com.vn/nha-dat/can-ban/trang--1.html"]
        elif type == "thue":
            self.start_urls = ["https://alonhadat.com.vn/nha-dat/cho-thue/trang--1.html"]
        super().__init__(**kw)

    def parse_item(self, response: Response):
        loader = ItemLoader(
            item=AlonhadatComVnItem(),
            response=response
        )
        soup = BeautifulSoup(response.text, "lxml")

        address = soup.find("div", {"class": "address"}).find("span", {"class": "value"})
        price = soup.find("span", {"class": "price"}).find("span", {"class": "value"})
        area = soup.find("span", {"class": "square"}).find("span", {"class": "value"})
        description = soup.find("div", {"class": "detail"})
        info_table = soup.find("div", {"class": "infor"}).table
        infos = self.extract_table_info(info_table)

        loader.add_value("title", soup.h1.string)
        loader.add_value("url", response.url)
        loader.add_value("address", address.string)
        loader.add_value("price", price.string)
        loader.add_value("area", area.get_text())
        loader.add_value("description", description.get_text())
        for key, value in infos.items():
            loader.add_value(key, value)

        item = loader.load_item()
        return item

    def extract_table_info(self, info_table: bs4.Tag | None):
        infos = {}
        for row in info_table.children:
            cells = list(row)
            names = cells[0::2]
            values = cells[1::2]
            for name, value in zip(names, values):
                name = name.string.strip()
                if next(value.children).name == "img":
                    value = True
                elif name in ["Phòng ăn", "Nhà bếp", "Chổ để xe hơi", "Sân thượng", "Chính chủ"]:
                    value = False
                else: value = value.string

                if name in self.info_map and value != "_":
                    print(name)
                    mapped_name = self.info_map[name]
                    infos[mapped_name] = value
        return infos