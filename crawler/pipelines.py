from itemadapter import ItemAdapter
import pymongo
from scrapy.crawler import Crawler
import scrapy

class CleanNoneFieldPipeline:
    def process_item(self, item: scrapy.Item, spider: scrapy.Spider):
        return {
            key: value for key, value in item.items()
            if value is not None
        }

class MongoPipeline:
    def __init__(
        self, 
        enabled: bool,
        username: str,
        password: str,
        host: str, 
        port: int, 
        db_name: str
    ) -> None:
        self.username = username
        self.password = password
        self.host = host
        self.port = port
        self.db_name = db_name
        self.enabled = enabled
    
    @classmethod
    def from_crawler(cls, crawler: Crawler):
        return cls(
            enabled=crawler.settings.get("MONGO_ENABLED", False),
            username=crawler.settings.get("MONGO_USERNAME", None),
            password=crawler.settings.get("MONGO_PASSWORD", None),
            host=crawler.settings.get("MONGO_HOST", "phatdatsite.ddns.net"),
            port=crawler.settings.get("MONGO_PORT", 3000),
            db_name=crawler.settings.get("MONGO_DB", "research")
        )
        
    def process_item(self, item: scrapy.Item, spider: scrapy.Spider):
        if (
            not hasattr(spider, "collection_name") or
            not self.enabled
        ):
            return item

        collection = self.db[spider.collection_name]
        data = ItemAdapter(item).asdict()

        collection.insert_one(data)
        return item
    
    def open_spider(self, spider: scrapy.Spider):
        self.client = pymongo.MongoClient(
            host=self.host,
            port=self.port,
            username=self.username,
            password=self.password
        )
        self.db = self.client[self.db_name]

    def close_spider(self, spider: scrapy.Spider):
        self.client.close()