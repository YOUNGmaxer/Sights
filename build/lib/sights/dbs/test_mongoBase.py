import unittest
from sights.dbs.mongoBase import MongoBaseClient

class TestMongoBase(unittest.TestCase):
  def setUp(self):
    self.MONGO_HOST = '106.13.70.140'
    self.MONGO_PORT = 27017
    self.MONGO_DB = 'test'
    self.collection_name = 'base'
    self.mongoClient = MongoBaseClient(self.MONGO_HOST, self.MONGO_PORT, self.MONGO_DB)

  def test_connectMongo(self):
    res = self.mongoClient.connectMongo()
    self.assertTrue(res, True)
  
  def test_insertItem(self):
    doc = {
      'name': 'yzm',
      'age': 18
    }
    self.mongoClient.connectMongo()
    # 插入文档
    _id = self.mongoClient.insertItem(self.collection_name, doc)
    if _id is not None:
      # 查询文档以判断文档是否插入成功
      res = self.mongoClient.findBy_id(self.collection_name, _id.inserted_id)
      self.assertIsNotNone(res)

  def test_setIndex(self):
    self.mongoClient.connectMongo()
    keys = [('name', 1)]
    # 设置索引
    self.mongoClient.setIndex(self.collection_name, keys, unique=True)
    print('设置索引', keys)

if __name__ == '__main__':
  unittest.main()
