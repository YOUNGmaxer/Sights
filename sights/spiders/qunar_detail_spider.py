from scrapy.spiders import CrawlSpider, Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.http import Request
from sights.items import SightsDetailItem
from sights.items import SightsItem
from sights.custom_settings import qunar_detail_spider_settings
from sights.utils import url
from urllib import parse
import re

class SightDetailSpider(CrawlSpider):
  name = 'qunar-detail'
  keyword = '普宁'
  proxy = None
  start_urls = [ f'http://piao.qunar.com/ticket/list.htm?keyword={keyword}' ]
  custom_settings = qunar_detail_spider_settings.settings

  rules = (
    Rule(
      LinkExtractor(restrict_xpaths='//div[@class="pager"]/a[@class="next"]'),
      callback='parse_start_url',
      follow=True
    ),
    Rule(
      LinkExtractor(restrict_xpaths='//div[@class="sight_item_about"]//a[@class="name"]',),
      callback='parse_item'
    )
  )

  def _build_request(self, rule, link):
    r = Request(url=link.url, callback=self._response_downloaded, dont_filter=True)
    r.meta.update(rule=rule, link_text=link.text)
    return r

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
    yield item

  # [重写] 处理 start_urls 返回 response
  def parse_start_url(self, response):
    # 获取景点列表
    page_list = response.xpath('//div[@class="result_list"]/div[contains(@class, "sight_item")]')
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
      yield item

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
