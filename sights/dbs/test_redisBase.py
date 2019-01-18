import unittest
from sights.dbs.redisBase import RedisBaseClient
from urllib.parse import urlencode

class TestRedisBase(unittest.TestCase):
  def setUp(self):
    self.REDIS_HOST = '106.13.70.140'
    self.REDIS_PORT = 6379
    self.REDIS_PASSWORD = '688232'
    self.r = RedisBaseClient(self.REDIS_HOST, self.REDIS_PORT, self.REDIS_PASSWORD)

  def test_getRedis(self):
    server = self.r.getRedis()
    print(f'连接 redis {server}')

  def test_lpush(self):
    server = self.r.getRedis()
    ret = server.lpush('urltest', '汕头'.encode(encoding='utf-8'))
    print(f'插入 redis {ret}')
