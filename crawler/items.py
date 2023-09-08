import scrapy
from itemloaders.processors import TakeFirst, MapCompose
import datetime
from utils import unit_to_quantity, area_ratio, quantity_ratio

class BatdongsanVnItem(scrapy.Item):
    _id = scrapy.Field(
        input_processor=MapCompose(
            lambda s: s.split(": ")[-1],
            str.strip,
            int
        ),
        output_processor=TakeFirst()
    )
    url = scrapy.Field(
        output_processor=TakeFirst()
    )
    title = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    price = scrapy.Field(
        input_processor=MapCompose(
            str.strip,
            lambda s: s if s == "Thỏa thuận" 
                else unit_to_quantity(s, quantity_ratio)
        ),
        output_processor=TakeFirst()
    )
    area = scrapy.Field(
        input_processor=MapCompose(
            str.strip,
            lambda s: unit_to_quantity(s, area_ratio)
        ),
        output_processor=TakeFirst()
    )
    bedroom = scrapy.Field(
        input_processor=MapCompose(
            str.strip,
            lambda s: unit_to_quantity(s, {})
        ),
        output_processor=TakeFirst()
    )
    wc = scrapy.Field(
        input_processor=MapCompose(
            str.strip,
            lambda s: unit_to_quantity(s, {})
        ),
        output_processor=TakeFirst()
    )
    facing_dir = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    balcony_dir = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    address = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    description = scrapy.Field(
        input_processor=MapCompose(str.strip),
        output_processor=TakeFirst()
    )
    author_name = scrapy.Field(
        output_processor=TakeFirst()
    )
    author_email = scrapy.Field(
        output_processor=TakeFirst()
    )
    author_phone = scrapy.Field(
        output_processor=TakeFirst()
    )
    publish_date = scrapy.Field(
        input_processor=MapCompose(
            lambda s: s.split(": ")[-1],
            lambda s: datetime.datetime.strptime(s, "%H:%M %d/%m/%Y")
        ),
        output_processor=TakeFirst()
    )

class HomedyVnItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    url = scrapy.Field()
    