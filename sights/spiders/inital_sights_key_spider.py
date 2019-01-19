from pymongo import MongoClient
from redis import Redis

class InitalSightsKey():
  MONGO_HOST = '106.13.70.140'
  MONGO_PORT = 27017
  MONGO_DB = 'sights'
  REDIS_HOST = '106.13.70.140'
  REDIS_PORT = 6379
  REDIS_PASSWORD = '688232'
  base_url = 'http://piao.qunar.com/ticket/detail_{}.html'
  redis_key = 'qunar_comment_test:start_urls'

  def __init__(self):
    self.mongo = MongoClient(host=self.MONGO_HOST, port=self.MONGO_PORT)
    self.db = self.mongo[self.MONGO_DB]

    self.redis = Redis(host=self.REDIS_HOST, port=self.REDIS_PORT, password=self.REDIS_PASSWORD)
    

  def getCollectionNames(self):
    names = self.db.list_collection_names()
    def lambdaFilter(x):
      if x != '城市名单' and x != '热门景点':
        return x
    ret = filter(lambdaFilter, names)
    return list(ret)

  def getDocuments(self, name):
    data = self.db[name].find()
    return list(data)

  def getUrl(self, data):
    sid = data['sid']
    num = len(data)
    url = self.base_url.format(sid)
    # 元素有缺少的景点需要添加符号
    if num < 13:
      url = url + '?flag=1'
      return url
    else:
      comment = data['comment']
      if len(comment) == 0:
        comment['全部'] = '0'
      if comment['全部'] == '0':
        print('comment is 0')
        return None
      else:
        return url
  
  def saveUrl(self, url):
    self.redis.lpush(self.redis_key, url)
    print('插入 url', url)

if __name__ == '__main__':
  ins = InitalSightsKey()
  names = ins.getCollectionNames()
  for i, name in enumerate(names):
    if i + 1 >= 117:
      print('城市', i + 1, name)
      sights = ins.getDocuments(name)
      for sight in sights:
        url = ins.getUrl(sight)
        if url:
          ins.saveUrl(url)
