from scrapy import Spider
from scrapy import Request
import logging
from urllib.parse import urlencode
from sights.items import SightsPageItem
from sights.dbs.mongoBase import MongoBaseClient
from sights.custom_settings import inital_redis_key_spider_settings

logger = logging.getLogger(__name__)

# 用于初始化开始列表的爬虫，便于分布式爬取
class InitalRedisKeySpider(Spider):
  name = 'init_redis_key'
  base_url = 'http://piao.qunar.com/ticket/list.htm?keyword={keyword}'
  city_url = 'http://localhost:5001/city'
  start_urls = [ city_url ]
  req_url = None
  redis_key = 'qunar_detail_test:start_urls'
  custom_settings = inital_redis_key_spider_settings.settings
  max_page = 150
  proxy = None

  def parse(self, response):
    # 将数据解码为中文字符
    cityData = response.body.decode('unicode_escape')
    # 将数据转化为字典
    cityDict = eval(cityData)
    cityRows = cityDict['rows']
    for i, area in enumerate(cityRows):
      logger.info('序号 %s 值 %s', i, area)
      if area['type'] == '直辖市':
        self.req_url = self.base_url.format(keyword=area['area'])
        # print('req_url', self.req_url)
        yield Request(url=self.req_url, callback=self.parse_page)
      else:
        for i, city in enumerate(area['cities']):
          logger.debug('城市 %s %s', i, city)
          self.req_url = self.base_url.format(keyword=city)
          # print('req_url', self.req_url)
          yield Request(url=self.req_url, callback=self.parse_page)

  def parse_page(self, response):
    logger.info(f'列表首页 - 状态{response.status}')
    next_url = response.css('.pager .next::attr(href)').extract_first()
    last_page = response.css('.pager a:nth-last-child(2)::text').extract_first()
    if last_page:
      last_page = int(last_page)
    page_num = 0
    if next_url:
      page_num = (last_page, self.max_page)[last_page > 150]
      for i in range(1, int(page_num) + 1):
        item = SightsPageItem()
        url = f'{response.url}&page={i}'.encode(encoding='utf-8')
        item['url'] = url
        item['page'] = i
        yield item
    else:
      page_num = 1
      logger.warn('该关键词只有一页数据')
    