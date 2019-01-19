import pymongo
from sights.dbs.mongoBase import MongoBaseClient
from sights.dbs.redisBase import RedisBaseClient
from sights.items import SightsIdItem, CommentItem, SightsDetailItem, SightsItem
import logging

logger = logging.getLogger(__name__)

class MongoBasePipeline():
  def __init__(self, mongo_host, mongo_port, mongo_db):
    self.mongo_host = mongo_host
    self.mongo_port = mongo_port
    self.mongo_db = mongo_db
    self.mongoClient = MongoBaseClient(self.mongo_host, self.mongo_port, self.mongo_db)

  @classmethod
  def from_crawler(cls, crawler):
    return cls(
      mongo_host = crawler.settings.get('MONGO_HOST'),
      mongo_port = crawler.settings.get('MONGO_PORT'),
      mongo_db = crawler.settings.get('MONGO_DB')
    )

# 需要抽取链接关键字存到相应的 collection 中
class SightsPipeline(MongoBasePipeline):
  def open_spider(self, spider):
    self.mongoClient.connectMongo()

  def process_item(self, item, spider):
    # 只有 item 属于这几种对象才进行处理
    if isinstance(item, (SightsDetailItem, SightsIdItem, SightsItem)):
      itemDict = dict(item)
      # 以城市名为存储的 collection
      collection = itemDict['city']
      self.mongoClient.setIndex(collection, [('sid', 1)], unique=True)
      ret = self.mongoClient.insertItem(collection, itemDict)
      # 如果文档已存在，就进行文档更新
      if ret == -1:
        col = self.mongoClient.getCollection(collection)
        # 使用这种更新方式，如果key存在就覆盖，不存在就增加
        col.update_one({'sid': itemDict['sid']}, {'$set': itemDict})
        logger.debug('更新文档')
      return item
    return item

  def close_spider(self, spider):
    self.mongoClient.closeDB()


class PageUrlsPipeline():
  def __init__(self, redis_host, redis_port, redis_password):
    self.redis_host = redis_host
    self.redis_port = redis_port
    self.redis_password = redis_password
    self.redisClient = RedisBaseClient(self.redis_host, self.redis_port, self.redis_password)

  @classmethod
  def from_crawler(cls, crawler):
    return cls(
      redis_host = crawler.settings.get('REDIS_HOST'),
      redis_port = crawler.settings.get('REDIS_PORT'),
      redis_password = crawler.settings.get('REDIS_PASSWORD')
    )
  
  def open_spider(self, spider):
    self.server = self.redisClient.getRedis()

  # 将链接存入到开始列表中
  def process_item(self, item, spider):
    itemDict = dict(item)
    itemUrl = itemDict['url']
    logger.info(f'[PageUrlsPipeline] 插入 itemUrl {itemUrl}')
    self.server.lpush(spider.redis_key, itemUrl)
    return item

class CommentPipeline(MongoBasePipeline):
  def open_spider(self, spider):
    self.mongoClient.connectMongo()

  def process_item(self, item, spider):
    # 只处理评论类的 item
    if isinstance(item, CommentItem):
      itemDict = dict(item)
      collection = itemDict['rid']
      self.mongoClient.setIndex(collection, [('commentId', 1)], unique=True)
      itemDict.pop('rid')
      ret = self.mongoClient.insertItem(collection, itemDict)
      if ret == -1:
        logger.debug('该评论数据已存在 %s', itemDict['commentId'])
      return item
    return item

  def close_spider(self, spider):
    self.mongoClient.closeDB()

  @classmethod
  def from_crawler(cls, crawler):
    return cls(
      mongo_host = crawler.settings.get('MONGO_HOST'),
      mongo_port = crawler.settings.get('MONGO_PORT'),
      mongo_db = crawler.settings.get('COMMENT_DB')
    )
