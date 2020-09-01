# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

from scrapy import Item, Field


class MovieItem(Item):
    mongodb_collection_name = 'movies'
    
    name = Field()
    categories = Field()
    drama = Field()
    score = Field()
    directors = Field()
    actors = Field()
