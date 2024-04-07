# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class FinScraperItem(scrapy.Item):
    title = scrapy.Field()
    author = scrapy.Field()
    collection_date = scrapy.Field()
    article_text = scrapy.Field()
    publication = scrapy.Field()
