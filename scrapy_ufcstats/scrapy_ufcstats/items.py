# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class ScrapyEventItem(scrapy.Item):
    event_name = scrapy.Field()
    event_date = scrapy.Field()
    event_location = scrapy.Field()
    event_url = scrapy.Field()
    datetime_scraped = scrapy.Field()


class ScrapyUfcstatsItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass
