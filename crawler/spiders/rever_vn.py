from scrapy.http import Response
from scrapy.loader import ItemLoader
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from crawler.items import ReverVnItem
from bs4 import BeautifulSoup
import bs4
import re
from typing import Literal
from utils import map

class ReverVnSpider(CrawlSpider):
    name = "rever_vn"
    collection_name = "rever_vn"
    allowed_domains = ["rever.vn"]
    start_urls = ["https://rever.vn/s/ho-chi-minh/mua/can-ho--dat-nen--land-business--biet-thu--can-ho-dich-vu--pent-house--nha-pho--office-tel--shop-house--studio-flat--van-phong--studio-flat--building-business?page=1"]

    rules = [
        Rule(LinkExtractor(allow=r"\?page=\d+$")),
        Rule(
            LinkExtractor(allow=r"https://rever.vn/(mua|thue)/.+", deny=r"\?page=\d+$"), 
            callback="parse_item"
        )
    ]

    droom_map = {
        "Phòng ngủ": "bedroom",
        "Phòng tắm": "wc",
        "Diện tích": "area",
        "Hướng nhà": "facing_dir"
    }

    dmore_map = {
        "Loại hình": "category",
        "Tình hình nội thất": "furniture_status",
        "Loại chủ quyền": "legal_status",
        "Tình trạng sử dụng": "use_status",
        "Dự án": "project",
        "Tháp": "building_name",
        "Trạng thái": "status"
    }
    advantage_map = {
        "Đặc điểm nổi bật": "advantage_features",
        "Mô tả vị trí": "advantage_location",
        "Cộng đồng dân cư": "advantage_resident",
        "Về giáo dục": "advantage_education",
        "Tìm kiếm theo từ khoá": "advantage_search_keyword"
    }

    def __init__(self, type: Literal["mua"] | Literal["thue"] = "mua", **kw):
        if type == "mua":
            self.start_urls  = ["https://rever.vn/s/ho-chi-minh/mua/can-ho--dat-nen--land-business--biet-thu--can-ho-dich-vu--pent-house--nha-pho--office-tel--shop-house--studio-flat--van-phong--studio-flat--building-business?page=1"]
        elif type == "thue":
            self.start_urls = ["https://rever.vn/s/ho-chi-minh/thue/can-ho--land-business--biet-thu--can-ho-dich-vu--pent-house--nha-pho--office-tel--shop-house--studio-flat--van-phong--studio-flat--studio-flat--building-business?page=1"]
        super().__init__(**kw)

    def parse_item(self, response: Response):
        loader = ItemLoader(
            item=ReverVnItem(),
            response=response
        )
        soup = BeautifulSoup(response.text, "lxml")

        id = soup.find("div", {"class": "listing-id"})
        address = soup.find("div", {"class": "address"})
        price = soup.find("div", {"class": "listing-detail-price-cost"}).strong
        droom_html = soup.find("ul", {"class": "detailroom"})
        droom = self.extract_detailroom(droom_html)
        dmore_html = soup.find("ul", {"class": "detail-more"})
        dmore = self.extract_detailmore(dmore_html)
        amenities = self.extract_li(soup.find("div", {"id": "details-amenities"}))
        try:
            furnitures_html = soup.find(string="Thiết bị, dịch vụ").find_next("div")
            furnitures = self.extract_li(furnitures_html.ul)
        except:
            furnitures = None
        
        try:
            tools_html = soup.find(string="Nội thất").find_next("div")
            tools = self.extract_li(tools_html.ul)
        except:
            tools = None
        
        try:
            adv_html = soup.find(string="Ưu điểm ngôi nhà").find_next("div")
            advantages = self.extract_advantages(adv_html)
        except:
            advantages = {}
        map_img = soup.find("section", {"class": "map-detail"}).img
        regex_match: re.Match = re.search(r".+\?center=([0-9\.]+),([0-9\.]+)", map_img["src"])
        lat, lon = regex_match.group(1), regex_match.group(2)
        
        loader.add_value("_id", id.get_text())
        loader.add_value("title", soup.h1.string)
        loader.add_value("url", response.url)
        loader.add_value("address", address.get_text())
        loader.add_value("price", price.string)
        for key, value in droom.items():
            loader.add_value(key, value)
        loader.add_value("description", soup.find("p", {"class": "summary"}))
        for key, value in dmore.items():
            loader.add_value(key, value)
        if amenities is not None:
            for a in amenities:
                loader.add_value("amenities", a)
        if furnitures is not None:
            for f in furnitures:
                loader.add_value("furnitures", f)
        if tools is not None:
            for t in tools:
                loader.add_value("tools", t)
        for key, value in advantages.items():
            loader.add_value(key, value)
        loader.add_value("longitude", lon)
        loader.add_value("latitude", lat)

        item = loader.load_item()
        return item

    def extract_detailroom(self, droom_html: bs4.Tag | None):
        droom = {}
        for title, field in self.droom_map.items():
            element = droom_html.find("li", {"title": title})
            if element is not None:
                droom[field] = element.get_text()
        return droom
    
    def extract_detailmore(self, dmore_html: bs4.Tag | None):
        dmore = {}
        rows = dmore_html.find_all("li")
        for row in rows:
            name, value = row.find_all("p")
            name, value = name.get_text().strip(), value.get_text()
            if name in self.dmore_map:
                mapped_name = self.dmore_map[name]
                dmore[mapped_name] = value
        return dmore
    
    def extract_li(self, ul_tag: bs4.Tag | None):
        if ul_tag is None:
            return None
        li_tags = ul_tag.ul.find_all("li")
        return map(li_tags, lambda li: li.string)
    
    def extract_advantages(self, adv_html: bs4.Tag | None):
        adv = {}
        rows = adv_html.find_all("div", {"class": "list-advantage"},recursive=False)
        for row in rows:
            name, value = row.find_all("div", recursive=False)
            name, value = name.get_text().strip(), value.get_text()
            if name in self.advantage_map:
                mapped_name = self.advantage_map[name]
                adv[mapped_name] = value
        return adv