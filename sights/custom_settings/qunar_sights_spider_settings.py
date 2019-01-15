settings = {
  'SETTING_NAME': 'qunar_sights_spider.qunar-hot-sights',
  'DOWNLOADER_MIDDLEWARES': {
    'scrapy.downloadermiddlewares.useragent.UserAgentMiddleware': None,
    'sights.downloader_middlewares.RandomUserAgentMiddleware': 500,

  },
  'ITEM_PIPELINES': {
    'sights.pipelines.SightsPipeline': 300
  }
}
