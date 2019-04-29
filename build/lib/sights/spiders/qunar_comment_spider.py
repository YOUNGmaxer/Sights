from scrapy_redis.spiders import RedisCrawlSpider
from scrapy.linkextractors import LinkExtractor
from scrapy.spiders import Rule
from scrapy import Request
from sights.custom_settings import qunar_comment_spider_settings
from sights.items import SightsIdItem, CommentItem
from sights.utils import url
from sights.spiders.qunar_detail_spider import SightDetailSpider
import math
import re
import json

class SightCommentSpider(RedisCrawlSpider):
  name = 'qunar_comment'
  proxy = None
  redis_key = f'{name}:start_urls'
  custom_settings = qunar_comment_spider_settings.settings
  base_url = 'http://piao.qunar.com/ticket/detailLight/sightCommentList.json?sightId={sightId}&index={index}&page={index}&pageSize=1000&tagType=0'
  
  rules = (
    Rule(
      LinkExtractor(allow_domains='t.tt'),
      callback='parse_start_url'
    ),
  )

  # 处理景点详情页
  def parse_start_url(self, response):
    print('response 状态', response.status)
    # print('response body', str(response.body, encoding='utf-8'))

    item = SightsIdItem()
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
    # 获取 sightsId （用于调用评论的api），字段将命名为 rid
    sightIdStr = response.xpath('//link[@rel="canonical"]/@href').extract_first()
    item['rid'] = re.search(r'detail_([^\.]*)', sightIdStr).group(1)
    yield item

    # 获取评论页码数
    comment_num = int(item['comment']['全部'])
    if comment_num > 10:
      # 向上取整得到评论的页码数
      page_num = math.ceil(comment_num / 1000)
      for i in range(1, page_num + 1):
        url = self.base_url.format(sightId=item['rid'], index=i)
        request = Request(url, callback=self.parse_comment)
        # 传递 rid
        request.meta['rid'] = item['rid']
        yield request

  def parse_comment(self, response):
    item = CommentItem()
    data = str(response.body, encoding='utf-8')
    # 将数据从字符串转化为字典
    commentDict = json.loads(data)['data']
    if 'commentList' in commentDict:
      commentList = commentDict['commentList']
      for i, comment in enumerate(commentList):
        item['rid'] = response.meta['rid']
        item['author'] = comment['author']
        item['content'] = comment['content']
        item['date'] = comment['date']
        item['score'] = comment['score']
        item['commentId'] = comment['commentId']
        item['userNickName'] = comment['userNickName']
        yield item
    
  def getSidFromUrl(self, url):
    return SightDetailSpider.getSidFromUrl(self, url)

  def parseCommentTags(self, tags):
    return SightDetailSpider.parseCommentTags(self, tags)

  def packCommentTags(self, tags):
    return SightDetailSpider.packCommentTags(self, tags)
