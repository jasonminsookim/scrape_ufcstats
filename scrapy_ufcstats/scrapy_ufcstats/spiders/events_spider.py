from scrapy import Spider, Request
from datetime import datetime
from ..items import ScrapyEventItem


class EventsSpider(Spider):
    name = "events"

    def start_requests(self):
        urls = ["http://www.ufcstats.com/statistics/events/completed?page=all"]
        for url in urls:
            yield Request(url=url, callback=self.parse)

    def parse(self, response):
        # Finds all event_urls that have already taken place.
        for event_url in response.css(".b-link_style_black::attr(href)").getall():
            yield Request(event_url, callback=self.parse_event)

    def parse_event(self, response):

        items = ScrapyEventItem()

        items["event_url"] = response.url
        items["date_scraped"] = datetime.now().date()
        yield items
