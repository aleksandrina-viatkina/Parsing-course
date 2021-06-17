import os
import dotenv
from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings
from instaparser.spiders.instagram_parser import InstagramParserSpider


if __name__ == "__main__":
    dotenv.load_dotenv(".env")
    crawler_settings = Settings()
    crawler_settings.setmodule("instaparser.settings")
    crawler_process = CrawlerProcess(settings=crawler_settings)
    crawler_process.crawl(
        InstagramParserSpider,
        login=os.getenv("USRNM1"),
        password=os.getenv("USRPSSWD1"),
        tags=["travel", ]
    )
    crawler_process.start()