from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from sights.items import SightsDetailItem
from sights.items import SightsItem
from sights.custom_settings import qunar_detail_spider_settings
from sights.utils import url
from scrapy_redis.spiders import RedisCrawlSpider
from urllib import parse
import re

# 注意如果使用 scrapy-redis，这里最好应该继承 RedisCrawlSpider
class SightDetailSpider(RedisCrawlSpider):
  name = 'qunar_detail'
  proxy = None
  # 使用 redis_key 避免多个爬虫都从同一起点去开始爬取
  redis_key = f'{name}:start_urls'
  custom_settings = qunar_detail_spider_settings.settings

  rules = (
    # 此处 LinkExtractor 无意义
    Rule(
      LinkExtractor(allow_domains='t.tt'),
      callback='parse_start_url',
    ),
    Rule(
      LinkExtractor(restrict_xpaths='//div[@class="sight_item_about"]//a[@class="name"]',),
      callback='parse_item',
    ),
  )
  
  # 此处重写可能带来了 scrapy-redis 无法使用去重功能
  # def _build_request(self, rule, link):
  #   r = Request(url=link.url, callback=self._response_downloaded, dont_filter=True)
  #   r.meta.update(rule=rule, link_text=link.text)
  #   return r

  # 重写 Spider 对象中 make_requests_from_url，因为这个方法将被废弃
  # def make_requests_from_url(self, url):
  #   return Request(url)

  def parse_item(self, response):
    print('parse_item', '状态', response.status)
    item = SightsDetailItem()
    item['sid'] = self.getSidFromUrl(response.url)
    item['level'] = response.xpath('//span[@class="mp-description-level"]/text()').extract_first()
    item['star_score'] = response.xpath('//span[@id="mp-description-commentscore"]/span/text()').extract_first()
    item['basic_price'] = response.xpath('//span[@class="mp-description-qunar-price"]/em/text()').extract_first()
    commentList = response.xpath('//li[contains(@class, "mp-commentstab-item")]/text()').extract()
    tags = self.packCommentTags(self.parseCommentTags(commentList))
    item['comment'] = tags[0]
    item['tags'] = tags[1]
    content = response.xpath('//meta[@name="location"]/@content').extract_first()
    item['city'] = re.search(r'city=([^;]*)', content).group(1)
    yield item

  # 用于处理景点列表页
  def parse_start_url(self, response):
    # 获取景点列表
    page_list = response.xpath('//div[@class="result_list"]/div[contains(@class, "sight_item")]')
    # next_url = response.xpath('//div[@class="pager"]/a[@class="next"]/@href').extract_first()
    page_num = url.getQueryParam(response.url, 'page')
    print(f'正在爬取第 {page_num} 页数据')
    for page_item in page_list:
      item = SightsItem()
      item['name'] = self.extractItem(page_item, 'data-sight-name')
      item['sid'] = self.extractItem(page_item, 'data-id')
      item['districts'] = self.extractItem(page_item, 'data-districts')
      item['point'] = self.extractItem(page_item, 'data-point').split(',')
      item['address'] = self.extractItem(page_item, 'data-address')
      item['sale_count'] = self.extractItem(page_item, 'data-sale-count')
      content = response.xpath('//meta[@name="location"]/@content').extract_first()
      item['city'] = re.search(r'city=([^;]*)', content).group(1)
      # item['city'] = url.getQueryParam(response.url, 'keyword')
      yield item

  # [重写] 处理 start_urls 返回 response
  # def parse_start_url(self, response):
  #   return None

  def extractItem(self, page_item, data_info):
    return page_item.css(f'div.sight_item::attr({data_info})').extract_first()

  def getSidFromUrl(self, url):
    path = parse.urlparse(url).path
    sid = re.search(r'detail_(\d+)', path).group(1)
    return sid

  # 返回评论分布
  def parseCommentTags(self, tags):
    def transList(tag):
      reg = re.search(r'([^(]+)\((\d+)', tag)
      return { reg.group(1): reg.group(2) }
    newList = list(map(transList, tags))
    return newList

  def packCommentTags(self, tags):
    commonList = ['全部', '好评', '中评', '差评']
    commonTags = {}
    specialTags = {}
    for tag in tags:
      key = list(tag.keys())[0]
      if key in commonList:
        commonTags[key] = tag[key]
      else:
        specialTags[key] = tag[key]
    return [commonTags, specialTags]
