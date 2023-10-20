from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Response
from scrapy.loader import ItemLoader
from crawler.items import BatdongsanVnItem
from bs4 import BeautifulSoup
import bs4
from typing import Literal

class BatdongsanVnSpider(CrawlSpider):
    name = "batdongsan_vn"
    collection_name = "batdongsan_vn"
    allowed_domains = ["batdongsan.vn"]

    rules = [
        Rule(LinkExtractor(allow=r"/p\d+?$")),
        Rule(
            LinkExtractor(
                allow=r"-r\d+$",
                deny=r"/p\d+?$"
            ),
            callback="parse_item",
        )
    ]

    map_info_keys = {
        "Phòng ngủ": "bedroom",
        "Phòng WC": "wc",
        "Diện tích": "area",
        "Hướng nhà": "facing_dir",
        "Hướng ban công": "balcony_dir",
        "Địa chỉ": "address"
    }

    def __init__(self, type: Literal["ban"] | Literal["thue"] = "ban", **kw):
        if type == "ban":
            self.start_urls = [
                "https://batdongsan.vn/ban-nha",
                "https://batdongsan.vn/ban-dat",
                "https://batdongsan.vn/ban-biet-thu",
                "https://batdongsan.vn/ban-bds-thuong-mai",
                "https://batdongsan.vn/ban-can-ho-chung-cu",
                "https://batdongsan.vn/ban-van-phong",
                "https://batdongsan.vn/ban-bds-cong-nghiep",
                "https://batdongsan.vn/ban-bds-nong-nghiep",
                "https://batdongsan.vn/ban-bds-tam-linh",
                "https://batdongsan.vn/ban-bds-khac"
            ]
        elif type == "thue":
            self.start_urls = [
                "https://batdongsan.vn/cho-thue-nha",
                "https://batdongsan.vn/cho-thue-dat",
                "https://batdongsan.vn/cho-thue-can-ho-chung-cu",
                "https://batdongsan.vn/cho-thue-van-phong",
                "https://batdongsan.vn/cho-thue-biet-thu",
                "https://batdongsan.vn/cho-thue-bds-thuong-mai",
                "https://batdongsan.vn/cho-thue-bds-cong-nghiep",
                "https://batdongsan.vn/cho-thue-bds-nong-nghiep",
                "https://batdongsan.vn/cho-thue-bds-tam-linh",
            ]
        super().__init__(**kw)

    def parse_item(self, response: Response, **kwargs):
        loader = ItemLoader(
            item=BatdongsanVnItem(),
            response=response
        )
        soup = BeautifulSoup(response.text, "lxml")

        stats_html, publish_html = soup.find_all("div", {"class": "param"})
        stats = self.extract_stats(stats_html)
        author = self.extract_author(soup)

        loader.add_value("_id", publish_html.span.get_text())
        loader.add_value("url", response.url)
        loader.add_value("title", soup.h1.span.string)
        loader.add_value("price", soup.find("strong", {"class": "price"}).string)
        loader.add_value("description", soup.find("div", {"class": "content"}).get_text())
        for key, value in stats.items():
            loader.add_value(key, value)
        for key, value in author.items():
            loader.add_value(key, value)
        loader.add_value("publish_date", publish_html.find_all("span")[-1].get_text())

        item = loader.load_item()
        yield item
    
    def extract_stats(self, infos_html: bs4.Tag | None) -> dict[str, str]:
        info_dict = {}
        for li in infos_html.find_all("li"):
            key, value = li.get_text().split(": ")
            if key in self.map_info_keys:
                mapped_key = self.map_info_keys[key]
                info_dict[mapped_key] = value
        return info_dict

    def extract_author(self, soup: bs4.BeautifulSoup) -> dict[str, str]:
        name = soup.find("div", {"class": "name"}).a.string
        email = soup.find("div", {"class": "email"}).a["href"].split(":")[-1]
        phone = soup.find("div", {"class": "phone"}).a["href"].split(":")[-1]
        return {
            "author_name": name,
            "author_email": email,
            "author_phone": phone
        }