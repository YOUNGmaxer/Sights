import pymongo
from sights.dbs.mongoBase import MongoBaseClient

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

class SightsPipeline(MongoBasePipeline):
  def open_spider(self, spider):
    self.collection = spider.keyword
    self.mongoClient.connectMongo()
    # 设置景点数据的索引
    self.mongoClient.setIndex(self.collection, [('sid', 1)], unique=True)

  def process_item(self, item, spider):
    itemDict = dict(item)
    ret = self.mongoClient.insertItem(self.collection, itemDict)
    # 如果文档已存在，就进行文档更新
    if ret == -1:
      col = self.mongoClient.getCollection(self.collection)
      # 使用这种更新方式，如果key存在就覆盖，不存在就增加
      col.update_one({'sid': itemDict['sid']}, {'$set': itemDict})
      print('更新文档')
    return item

  def close_spider(self, spider):
    self.mongoClient.closeDB()


