from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.loader import ItemLoader
from crawler.items import Bds123VnItem
from scrapy.http import Response
from bs4 import BeautifulSoup
import bs4
from typing import Literal

class Bds123VnSpider(CrawlSpider):
    name = "bds123_vn"
    collection_name = "bds123_vn"
    allowed_domains = ["bds123.vn"]

    rules = [
        Rule(LinkExtractor(allow=r"\?page=\d+?$")),
        Rule(
            LinkExtractor(allow=r"-pr\d+\.html$", deny=r"\?page=\d+?$"), 
            callback="parse_item", 
        ),
    ]

    f_classes = {
        "post-price": "price",
        "post-acreage": "area",
        "post-bedroom": "bedroom",
        "post-bathroom": "wc",
        "post-direction": "facing_dir"
    }

    def __init__(self, type: Literal["mua"] | Literal["thue"] = "mua", **kw):
        if type == "mua":
            self.start_urls = ["https://bds123.vn/nha-dat-ban.html"]
        elif type == "thue":
            self.start_urls = ["https://bds123.vn/nha-dat-cho-thue.html"]
        super().__init__(**kw)

    def parse_item(self, response: Response):
        loader = ItemLoader(
            item=Bds123VnItem(),
            response=response
        )
        soup = BeautifulSoup(response.text, "lxml")

        id, *leftover, publish, due = soup.tbody.find_all("tr")
        address = soup.find("p", {"class": "post-address"}).span.string
        feature_html = soup.find("div", {"class": "post-features"})
        features = self.extract_features(feature_html)
        summary, description, *leftover = soup.find_all("div", {"class": "post-section"})
        author = soup.find("div", {"class": "author-name"})
        author_phone = soup.find("button", {"class": "btn-phone"})
        
        loader.add_value("_id", id.find_all("td")[1].string)
        loader.add_value("url", response.url)
        loader.add_value("title", soup.h1.get_text())
        loader.add_value("address", address)
        for feature, value in features.items():
            loader.add_value(feature, value)
        loader.add_value("desc_summary", summary.div.get_text())
        loader.add_value("description", description.div.get_text())
        loader.add_value("author", author.string)
        loader.add_value("author_phone", author_phone.get_text())
        loader.add_value("publish_date", publish.get_text())
        loader.add_value("due_date", due.get_text())

        item = loader.load_item()
        return item

    def extract_features(self, feature_html: bs4.Tag | None):
        features = {}
        for cls, field in self.f_classes.items():
            extracted = feature_html.find("span", {"class": cls})
            if extracted is not None:
                features[field] = extracted.get_text()
        return features