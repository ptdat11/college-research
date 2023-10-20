import scrapy
from w3lib.html import remove_tags
from itemloaders.processors import TakeFirst, MapCompose, Join
import datetime
import re
from utils import unit_to_quantity, area_ratio, quantity_ratio, try_parse_int

def strip_field(*in_proc):
    return scrapy.Field(
        input_processor=MapCompose(str.strip, *in_proc),
        output_processor=TakeFirst()
    ) 
def list_field(separator = ",", *in_proc):
    return scrapy.Field(
        input_processor=MapCompose(str.strip, *in_proc),
        output_processor=Join(f"{separator} ")
    )
def to_str_field(*in_proc):
    return scrapy.Field(
        input_processor=MapCompose(str, *in_proc),
        output_processor=TakeFirst()
    )

class BatdongsanVnItem(scrapy.Item):
    _id = scrapy.Field(
        input_processor=MapCompose(
            lambda s: s.split(": ")[-1],
            str.strip,
            int
        ),
        output_processor=TakeFirst()
    )
    url = scrapy.Field(output_processor=TakeFirst())
    title = strip_field()
    price = strip_field(
        lambda s: s if s == "Thỏa thuận" 
            else unit_to_quantity(s, quantity_ratio)
    )
    area = strip_field(
        lambda s: unit_to_quantity(s, area_ratio)
    )
    bedroom = strip_field(
        lambda s: unit_to_quantity(s, {})
    )
    wc = strip_field(
        lambda s: unit_to_quantity(s, {})
    )
    facing_dir = strip_field()
    balcony_dir = strip_field()
    address = strip_field()
    description = strip_field()
    author_name = scrapy.Field(output_processor=TakeFirst())
    author_email = scrapy.Field(output_processor=TakeFirst())
    author_phone = scrapy.Field(output_processor=TakeFirst())
    publish_date = scrapy.Field(
        input_processor=MapCompose(
            lambda s: s.split(": ")[-1],
            lambda s: datetime.datetime.strptime(s, "%H:%M %d/%m/%Y")
        ),
        output_processor=TakeFirst()
    )

class HomedyVnItem(scrapy.Item):
    _id = strip_field(int)
    title = strip_field()
    url = scrapy.Field(output_processor=TakeFirst())
    publish_date = strip_field(
        lambda s: datetime.datetime.strptime(s, "%d/%m/%Y")
    )
    due_date = strip_field(
        lambda s: datetime.datetime.strptime(s, "%d/%m/%Y")
    )
    info_type = strip_field()
    geolocation = strip_field()
    price = strip_field(lambda s: s.replace("\n", " "))
    area = strip_field(lambda s: s.replace("\n", " "))
    description = strip_field()
    category = strip_field()
    bedroom = strip_field(int)
    floor = strip_field(int)
    legal_status = strip_field()
    facing_dir = strip_field()
    balcony_dir = strip_field()
    furniture = strip_field()

class Bds123VnItem(scrapy.Item):
    _id = strip_field(int)
    url = strip_field()
    title = strip_field()
    address = scrapy.Field(
        input_processor=MapCompose(
            str.strip,
            lambda s: s.split(": ")[-1]
        ),
        output_processor=TakeFirst()
    )
    price = strip_field()
    area = strip_field()
    bedroom = strip_field(
        lambda s: s.split(" ")[0],
        int
    )
    wc = strip_field(
        lambda s: s.split()[0],
        int
    )
    facing_dir = strip_field()
    desc_summary = strip_field()
    description = strip_field()
    author = strip_field()
    author_phone = strip_field()
    publish_date = strip_field(
        lambda s: s.split(", ", 1)[-1],
        lambda s: datetime.datetime.strptime(s, "%H:%M %d/%m/%Y")
    )
    due_date = strip_field(
        lambda s: s.split(", ", 1)[-1],
        lambda s: datetime.datetime.strptime(s, "%H:%M %d/%m/%Y")
    )

class ReverVnItem(scrapy.Item):
    _id = strip_field(lambda s: s.split(":")[-1])
    title = strip_field()
    url = strip_field()
    address = strip_field(lambda s: s.replace("\n", ", "))
    price = strip_field()
    bedroom = strip_field(int)
    wc = strip_field(int)
    area = strip_field(lambda s: s.replace("\n", " "))
    facing_dir = strip_field()
    description = strip_field()
    category = strip_field()
    furniture_status = strip_field()
    legal_status = strip_field()
    use_status = strip_field()
    project = strip_field()
    building_name = strip_field()
    status = strip_field()
    amenities = list_field()
    furnitures = list_field()
    tools = list_field()
    advantage_features = strip_field()
    advantage_location = strip_field()
    advantage_resident = strip_field()
    advantage_education = strip_field()
    advantage_search_keyword = list_field(",", lambda s: s.replace("\n", ", "))
    longitude = strip_field(float)
    latitude = strip_field(float)

class NhadatvuiVnItem(scrapy.Item):
    _id = strip_field(int)
    title = strip_field()
    url = strip_field()
    publish_date = strip_field(
        lambda s: datetime.datetime.strptime(s, "%d/%m/%Y")
    )
    due_date = strip_field(
        lambda s: datetime.datetime.strptime(s, "%d/%m/%Y")
    )
    news_rank = strip_field()
    address = strip_field()
    price = strip_field()
    description = strip_field()
    area = strip_field()
    bedroom = strip_field(int)
    wc = strip_field(int)
    width = strip_field(lambda s: s.replace(" ", "").replace("\n", ""))
    height = strip_field(lambda s: s.replace(" ", "").replace("\n", ""))
    facing_dir = strip_field()
    legal_status = strip_field()
    real_estate_status = strip_field()
    location = strip_field()
    use_status = strip_field()
    floor = strip_field(try_parse_int)
    road_width = strip_field(lambda s: s.replace(" ", "").replace("\n", ""))
    nearby_utilities = list_field()
    furnitures = list_field()
    neighbor = list_field()
    security = list_field()
    entrance = list_field()
    search_phrases = list_field()

class AlonhadatComVnItem(scrapy.Item):
    _id = strip_field(int)
    title = strip_field()
    url = strip_field()
    address = strip_field()
    price = strip_field()
    area = strip_field()
    description = strip_field()
    news_type = strip_field()
    category = strip_field()
    width = strip_field()
    height = strip_field()
    facing_dir = strip_field()
    entrance_length = strip_field()
    legal_status = strip_field()
    floor = strip_field(try_parse_int)
    bedroom = strip_field(try_parse_int)
    dining_room = to_str_field()
    kitchen = to_str_field()
    terrace = to_str_field()
    car_storage = to_str_field()
    verified_owner = to_str_field()

class TheNumbersComItem(scrapy.Item):
    _id = strip_field()
    url = strip_field()
    name = strip_field()
    year = strip_field(int)
    summary = strip_field(lambda s: s.replace("\n", "").replace("\r", ""))
    dom_bo = strip_field()
    int_bo = strip_field()
    opening_weekend = strip_field()
    legs = strip_field()
    budget = strip_field()
    theater_counts = strip_field()
    infl_bo = strip_field()

    domestic_releases = strip_field()
    domestic_distributors = list_field()
    mpaa = strip_field()
    running_time = strip_field()
    franchise = list_field()
    keywords = strip_field()
    source = strip_field()
    genre = strip_field()
    production_method = strip_field()
    creative_type = strip_field()
    production_financing = list_field()
    languages = list_field()

    leading_cast = list_field()
    supporting_cast = list_field()
    technical_credits = list_field()