import os
import scrapy

from dotenv import load_dotenv

load_dotenv()


class AlphaSpider(scrapy.Spider):
    name = "alpha"
    url = "https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={}&outputsize=full&apikey={}"

    def start_requests(self):
        symbols = [
            "IBM",
        ]
        for symbol in symbols:
            yield scrapy.Request(
                url=self.url.format(symbol, os.getenv("ALPHA_API_KEY")),
                callback=self.parse,
            )

    def parse(self, response):
        yield {"text": response.text}
