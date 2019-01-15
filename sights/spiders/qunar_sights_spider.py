import scrapy
import os
import requests
import base64
import json
from PIL import Image
from scrapy.shell import inspect_response
from scrapy.loader import ItemLoader
from sights.items import SightsItem
from sights.utils import baidu_ocr
from sights.custom_settings import qunar_sights_spider_settings

# 景点列表爬虫-去哪儿
class HotSightSpider(scrapy.Spider):
  name = 'qunar-hot-sights'
  page_num = 1
  proxy = None
  keyword = '普宁'
  start_urls = [ f'http://piao.qunar.com/ticket/list.htm?keyword={keyword}' ]
  custom_settings = qunar_sights_spider_settings.settings

  def parse(self, response):
    '''
    用于分析和提取去哪儿网的页面内容
    @url http://piao.qunar.com/ticket/list.htm?keyword=深圳
    @returns items
    @scrapes name sid districts point address sale_count
    '''
    print('状态', response.status)
    # 获取景点列表
    page_list = response.xpath('//div[@class="result_list"]/div[contains(@class, "sight_item")]')
    # 下一页的按钮
    next_btn = response.xpath('//div[@class="pager"]/a[@class="next"]')
    for page_item in page_list:
      item = SightsItem()
      item['name'] = self.parse_item(page_item, 'data-sight-name')
      item['sid'] = self.parse_item(page_item, 'data-id')
      item['districts'] = self.parse_item(page_item, 'data-districts')
      item['point'] = self.parse_item(page_item, 'data-point').split(',')
      item['address'] = self.parse_item(page_item, 'data-address')
      item['sale_count'] = self.parse_item(page_item, 'data-sale-count')
      yield item
    
    # 如果有下一页按钮，自动爬取下一页
    if next_btn:
      self.page_num += 1
      next_url = f'{self.start_urls[0]}&page={self.page_num}'
      print(f'正在爬取第 {self.page_num} 页的数据')
      yield scrapy.Request(next_url, callback=self.parse, dont_filter=True)
    else:
      # 在没有下一页按钮的情况下，判断是不是反爬虫页面
      robot_page = response.xpath('//div[@class="mp-robot-formcon"]')
      if robot_page:
        print('爬虫被中断: 可能IP被封')
        print(robot_page)
      else:
        print('爬到底啦！没有下一页按钮啦！')
  
  # 封装内容的提取
  def parse_item(self, page_item, data_info):
    return page_item.css('div.sight_item::attr(%s)' % data_info).extract_first()

  # 分析反爬虫验证码并破解（OCR识别库有问题！）
  # def parse_robot_img(self, response):
  #   print(response.status)
  #   if response.status == 200:
  #     file_path = 'sights/images/{0}.{1}'.format(self.keyword, 'jpg')
  #     # 将验证码图片下载下来
  #     with open(file_path, 'wb') as f:
  #       f.write(response.body)
  #     ocr_res = baidu_ocr.transImage2Text(file_path)
  #     print('ocr_res', ocr_res)
      
