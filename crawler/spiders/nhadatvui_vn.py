from scrapy.http import Response
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from crawler.items import NhadatvuiVnItem
from bs4 import BeautifulSoup
import bs4
from typing import Literal
from utils import map

class NhadatvuiVnSpider(CrawlSpider):
    name = "nhadatvui_vn"
    collection_name = "nhadatvui_vn"
    allowed_domains = ["nhadatvui.vn"]

    rules = [
        Rule(LinkExtractor(allow=r"page=\d+$")),
        Rule(
            LinkExtractor(allow=r".*\d+$", deny=r"page=\d+$"), 
            callback="parse_item"
        )
    ]

    info_map = {
        "Diện tích": "area",
        "Phòng ngủ": "bedroom",
        "Phòng tắm": "wc",
        "Chiều rộng": "width",
        "Chiều dài": "height",
        "Hướng": "facing_dir",
        "Giấy tờ pháp lý": "legal_status",
        "Hiện trạng nhà": "real_estate_status",
        "Vị trí": "location",
        "Trạng thái sử dụng": "use_status",
        "Số tầng": "floor",
        "Đường rộng": "road_width"
    }

    def __init__(self, type: Literal["mua"] | Literal["thue"] = "mua", **kw):
        if type == "mua":
            self.start_urls =["https://nhadatvui.vn/mua-ban-nha-dat?page=1"] 
        elif type == "thue":
            self.start_urls = ["https://nhadatvui.vn/cho-thue-nha-dat?page=1"]
        super().__init__(**kw)

    def parse_item(self, response: Response):
        loader = ItemLoader(
            item=NhadatvuiVnItem(),
            response=response
        )
        soup = BeautifulSoup(response.text, "lxml")

        status_html = soup.find("div", {"class": "product-status"})
        publish, due, news_rank, id = map(
            status_html.find_all("div"),
            lambda tag: tag.find_all("span")[-1]
        )
        address = soup.find("div", {"class": ["display-flex", "flex-center", "line-22", "text-medium-s"]}).span
        price = soup.find("span", {"class": "price"})
        description = soup.find("div", {"id": "tab-custom"}).div
        info_table_html = soup.find("div", {"id": "tab-info"})
        infos = self.extract_info(info_table_html.find("ul"))
        utils = self.extract_list(info_table_html, "Tiện ích lân cận")
        furnitures = self.extract_list(info_table_html, "Nội thất, tiện nghi")
        neighbor = self.extract_list(info_table_html, "Hàng xóm")
        security = self.extract_list(info_table_html, "An ninh")
        entrance = self.extract_list(info_table_html, "Đường vào bđs")
        search_phrases = soup.find("h5").find_next_sibling("div").find_all("a")
        
        loader.add_value("_id", id.string)
        loader.add_value("url", response.url)
        loader.add_value("title", soup.h1.string)
        loader. add_value("address", address.string)
        loader.add_value("publish_date", publish.string)
        loader.add_value("due_date", due.string)
        loader.add_value("news_rank", news_rank.string)
        loader.add_value("price", price.string) 
        loader.add_value("description", description.get_text())
        for key, value in infos.items():
            loader.add_value(key, value)
        for util in utils:
            loader.add_value("nearby_utilities", util)
        for fur in furnitures:
            loader.add_value("furnitures", fur)
        for nei in neighbor:
            loader.add_value("neighbor", nei)
        for sec in security:
            loader.add_value("security", sec)
        for ent in entrance:
            loader.add_value("entrance", ent)
        for phrase in search_phrases:
            loader.add_value("search_phrases", phrase.string)

        item = loader.load_item()
        return item

    def extract_info(self, info_table_html: bs4.Tag | None):
        infos = {}
        rows = info_table_html.find_all("li", recursive=False)
        for row in rows:
            name, value = row.find_all("span", recursive=False)
            name, value = name.get_text().strip(), value.get_text()
            if name in self.info_map:
                mapped_name = self.info_map[name]
                infos[mapped_name] = value
        return infos

    def extract_list(self, info_table_html: bs4.Tag | None, list_name: str):
        if info_table_html is None:
            return []
        try:
            list_html = info_table_html.find_next_sibling("h2", string=f"\n                                        {list_name}\n                                    ").find_next_sibling("ul")
            list = [li.span.string for li in list_html.find_all("li", recursive=False)]
        except:
            list = []
        return list