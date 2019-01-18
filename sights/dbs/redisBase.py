import redis

class RedisBaseClient():
  def __init__(self, redis_host, redis_port, redis_password):
    self.redis_host = redis_host
    self.redis_port = redis_port
    self.redis_password = redis_password

  def getRedis(self):
    r = redis.Redis(host=self.redis_host, port=self.redis_port, password=self.redis_password)
    return r
