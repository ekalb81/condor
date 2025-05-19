# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy


class TutorialItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


class ProductItem(scrapy.Item):
    """Item for product data from the Bumble and Bumble website.

    This item can store both raw data from the website and parsed data.
    For raw data collection, use: url, raw_html, meta_title, meta_description, category
    For parsed data, use: url, name, options, ingredients, other
    """
    # Fields for raw data collection
    url = scrapy.Field()
    raw_html = scrapy.Field()
    meta_title = scrapy.Field()
    meta_description = scrapy.Field()
    category = scrapy.Field()

    # Fields for parsed data
    name = scrapy.Field()
    options = scrapy.Field()
    ingredients = scrapy.Field()
    other = scrapy.Field()
