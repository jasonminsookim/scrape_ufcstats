from scrapy import Spider, Request
from datetime import datetime
from ..items import ScrapyEventItem
import pandas as pd
import re

MONTHS_ARR = [
    "January",
    "February",
    "March",
    "April",
    "May",
    "June",
    "July",
    "August",
    "September",
    "October",
    "November",
    "December",
]


class EventsSpider(Spider):
    name = "events"

    def start_requests(self):
        urls = ["http://www.ufcstats.com/statistics/events/completed?page=all"]
        for url in urls:
            yield Request(url=url, callback=self.parse_event)

    def parse_event(self, response):
        scrape_datetime = datetime.utcnow()
        events_df = pd.read_html(response.request.url, skiprows=2)[0]
        # Finds all event_urls that have already taken place.
        event_urls = response.css(".b-link_style_black::attr(href)").getall()

        if len(event_urls) == events_df.shape[0]:
            print("The nubmer of rows match.")

        rx = re.compile( fr"\s+(?=(?:{'|'.join(MONTHS_ARR)})\b)", re.I )
        for i in range(len(event_urls)):
            event_url = event_urls[i]
            event_location = events_df.iloc[i, 1]
            event_name_date = events_df.iloc[i, 0]
            event_name = rx.split(event_name_date)[0]
            event_date_str = rx.split(event_name_date)[-1].strip()
            event_date = datetime.strptime(event_date_str, "%B %d, %Y")

            event_item = ScrapyEventItem()
            event_item["event_name"] = event_name
            event_item["event_date"]  = event_date
            event_item["event_location"] = event_location
            event_item["event_url"] = event_url
            event_item["datetime_scraped"] = scrape_datetime
            yield event_item
