import pymongo
from pymongo import errors
from scrapy import crawler

class MongoBaseClient():
  def __init__(self, mongo_host, mongo_port, mongo_db):
    self.mongo_host = mongo_host
    self.mongo_port = mongo_port
    self.mongo_db = mongo_db
    self.client = None
    self.db = None
  
  def connectMongo(self):
    try:
      self.client = pymongo.MongoClient(self.mongo_host, self.mongo_port)
      # 指定连接哪个数据库
      self.db = self.client[self.mongo_db]
      print('成功连接数据库', self.db)
      return True
    except Exception as e:
      print('连接失败', e)
      return None

  def getCollection(self, collection):
    return self.db[collection]

  def insertItem(self, collection, document):
    if self.db:
      # 这里需要考虑，如果设置了唯一索引，那么此时插入重复的文档会报错，需要在这里捕获异常
      try:
        return self.db[collection].insert_one(dict(document))
      except errors.DuplicateKeyError as e:
        print('插入文档出现异常!', e)
        return -1
      except errors.ServerSelectionTimeoutError as e:
        print('捕获异常 ServerSelectionTimeoutError', e)
    else:
      print('可能尚未连接数据库')
      return None

  def findBy_id(self, collection, _id):
    '''
    根据 _id 查询文档
    :param collection:
    :param _id:
    :return: document or None
    '''
    filter_param = { '_id': _id }
    return self.db[collection].find_one(dict(filter_param))

  def findAll(self, collection):
    self.db[collection].find()

  def setIndex(self, collection, keys, **options):
    '''
    用来设置集合的索引
    :param collection: 指定集合
    :param keys: 指定哪些键作为索引，可以指定多个，使用元组或元组数据
    :param **options: 传递配置项，设置索引
    '''
    try:
      self.db[collection].create_index(keys, **options)
      print('设置数据库{0}索引{1}'.format(collection, [key[0] for key in keys]))
    except errors.ServerSelectionTimeoutError as e:
      print('捕获异常 ServerSelectionTimeoutError', e)

  def getAllIndex(self, collection):
    res = self.db[collection].list_indexes()
    print('索引', res.next())

  def closeDB(self):
    self.client.close()
    print('关闭数据库')
