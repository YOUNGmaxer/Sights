# -*- coding: utf-8 -*-

# Scrapy settings for sights project
#
# For simplicity, this file contains only settings considered important or
# commonly used. You can find more settings consulting the documentation:
#
#     https://doc.scrapy.org/en/latest/topics/settings.html
#     https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
#     https://doc.scrapy.org/en/latest/topics/spider-middleware.html

BOT_NAME = 'sights'

SPIDER_MODULES = ['sights.spiders']
NEWSPIDER_MODULE = 'sights.spiders'

# 查询关键词
KEYWORD = '汕头1'

# MongoDB
MONGO_HOST = '106.13.70.140'
MONGO_PORT = 27017
MONGO_DB = 'sights'

# 设置 log 级别
# LOG_LEVEL = 'INFO'

# Obey robots.txt rules
ROBOTSTXT_OBEY = True

# Enable or disable downloader middlewares
# See https://doc.scrapy.org/en/latest/topics/downloader-middleware.html
DOWNLOADER_MIDDLEWARES = {
  'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
  'sights.downloader_middlewares.RandomUserAgentMiddleware': 500,
  'scrapy.downloadermiddlewares.redirect.RedirectMiddleware': None,
  'sights.downloader_middlewares.LocalRedirectMiddleware': 600,
  'sights.downloader_middlewares.ProxyMiddleware': 800,
}

# Configure item pipelines
# See https://doc.scrapy.org/en/latest/topics/item-pipeline.html
ITEM_PIPELINES = {

}

# 下载延迟
DOWNLOAD_DELAY = 0.8

# 配置 Scrapy-Redis
# SCHEDULER = 'scrapy_redis.scheduler.Scheduler'
SCHEDULER = 'scrapy_redis_bloomfilter.scheduler.Scheduler'

# 去重类使用 scrapy_redis_bloomfilter
# DUPEFILTER_CLASS = 'scrapy_redis.dupefilter.RFPDupeFilter'
DUPEFILTER_CLASS = 'scrapy_redis_bloomfilter.dupefilter.RFPDupeFilter'

# 散列函数的个数，默认为6，可以自行修改
BLOOMFILTER_HASH_NUMBER = 6

# Bloom Filter 的bit参数，默认30，占用128MB空间，去重量级1亿
BLOOMFILTER_BIT = 30

# 配置持久化，爬取队列不自动清空
SCHEDULER_PERSIST = True

# 配置 Redis 连接信息
# 形式 REDIS_URL=redis://[:password]@host:port/db
REDIS_URL = 'redis://:688232@106.13.70.140:6379'
# 或分开（会出错，暂不知道原因）
REDIS_HOST = '106.13.70.140'
REDIS_PORT = '6379'
REDIS_PASSWORD = '688232'
