# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from elasticsearch import Elasticsearch

import pymongo


class MongoDBPipeline(object):
    def __init__(self, connection_string, database):
        self.connection_string = connection_string
        self.database = database
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            connection_string=crawler.settings.get('MONGODB_CONNECTION_STRING'),
            database=crawler.settings.get('MONGODB_DATABASE')
        )
    
    def open_spider(self, spider):
        self.client = pymongo.MongoClient(self.connection_string)
        self.db = self.client[self.database]
    
    def process_item(self, item, spider):
        name = item.__class__.__name__
        self.db[name].insert(dict(item))
        return item
    
    def close_spider(self, spider):
        self.client.close()


class ElasticsearchPipeline:
    
    def __init__(self, hosts, index):
        self.conn = Elasticsearch(hosts)
        self.index = index
        if not self.conn.indices.exists(index):
            self.conn.indices.create(index=index)
    
    @classmethod
    def from_crawler(cls, crawler):
        return cls(
            hosts=crawler.settings.get('ELASTICSEARCH_HOSTS'),
            index=crawler.settings.get('ELASTICSEARCH_INDEX')
        )
    
    def process_item(self, item, spider):
        self.conn.index(index=self.index, body=dict(item))
        return item


from scrapy import Request
from scrapy.exceptions import DropItem
from scrapy.pipelines.images import ImagesPipeline


class ImagePipeline(ImagesPipeline):
    def file_path(self, request, response=None, info=None):
        movie = request.meta['movie']
        type = request.meta['type']
        name = request.meta['name']
        file_name = f'{movie}/{type}/{name}.jpg'
        return file_name
    
    def item_completed(self, results, item, info):
        image_paths = [x['path'] for ok, x in results if ok]
        if not image_paths:
            raise DropItem('Image Downloaded Failed')
        return item
    
    def get_media_requests(self, item, info):
        print('!!!!!!!!!!item', item)
        for director in item['directors']:
            director_name = director['name']
            director_image = director['image']
            yield Request(director_image, meta={
                'name': director_name,
                'type': 'director',
                'movie': item['name']
            })
        
        for actor in item['actors']:
            print('actor', actor)
            actor_name = actor['name']
            actor_image = actor['image']
            yield Request(actor_image, meta={
                'name': actor_name,
                'type': 'actor',
                'movie': item['name']
            })
