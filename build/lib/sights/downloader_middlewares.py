import random
import logging
from sights.utils.ip_proxy import AddrProxy
from scrapy.downloadermiddlewares.retry import RetryMiddleware
from scrapy.downloadermiddlewares.redirect import RedirectMiddleware
from scrapy.crawler import Crawler
from scrapy import Request
import re
import json

logger = logging.getLogger(__name__)

# 用于随机选取 UserAgent 用于发送请求
class RandomUserAgentMiddleware():
  def __init__(self):
    self.user_agents = [
      'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36',
      "Mozilla/4.0 (compatible; MSIE 6.0; Windows NT 5.1; SV1; AcooBrowser; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
      "Mozilla/4.0 (compatible; MSIE 7.0; Windows NT 6.0; Acoo Browser; SLCC1; .NET CLR 2.0.50727; Media Center PC 5.0; .NET CLR 3.0.04506)",
      "Mozilla/4.0 (compatible; MSIE 7.0; AOL 9.5; AOLBuild 4337.35; Windows NT 5.1; .NET CLR 1.1.4322; .NET CLR 2.0.50727)",
      "Mozilla/5.0 (Windows; U; MSIE 9.0; Windows NT 9.0; en-US)",
      "Mozilla/4.0 (compatible; MSIE 7.0b; Windows NT 5.2; .NET CLR 1.1.4322; .NET CLR 2.0.50727; InfoPath.2; .NET CLR 3.0.04506.30)",
      "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN) AppleWebKit/523.15 (KHTML, like Gecko, Safari/419.3) Arora/0.3 (Change: 287 c9dfb30)",
      "Mozilla/5.0 (X11; U; Linux; en-US) AppleWebKit/527+ (KHTML, like Gecko, Safari/419.3) Arora/0.6",
      "Mozilla/5.0 (Windows; U; Windows NT 5.1; en-US; rv:1.8.1.2pre) Gecko/20070215 K-Ninja/2.1.1",
      "Mozilla/5.0 (Windows; U; Windows NT 5.1; zh-CN; rv:1.9) Gecko/20080705 Firefox/3.0 Kapiko/3.0",
      "Mozilla/5.0 (X11; Linux i686; U;) Gecko/20070322 Kazehakase/0.4.5",
      "Mozilla/5.0 (X11; U; Linux i686; en-US; rv:1.9.0.8) Gecko Fedora/1.9.0.8-1.fc10 Kazehakase/0.5.6",
      "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_3) AppleWebKit/535.20 (KHTML, like Gecko) Chrome/19.0.1036.7 Safari/535.20",
      "Opera/9.80 (Macintosh; Intel Mac OS X 10.6.8; U; fr) Presto/2.9.168 Version/11.52"
    ]
  
  def process_request(self, request, spider):
    request.headers['User-Agent'] = random.choice(self.user_agents)

# 用于处理代理的中间件
class ProxyMiddleware():
  def process_request(self, request, spider):
    print('进入 ProxyMiddleware', spider.proxy)
    # 确保代理 ip 能被暂时沿用
    if spider.proxy:
      request.meta['proxy'] = spider.proxy
    # 赋值代理的判断条件为 retry_times, 即第一次请求失败之后才启用代理
    if request.meta.get('retry_times'):
      updateProxy(request, spider)
  
  # def process_response(self, request, response, spider):
  #   if response.status == 403:
  #     print('403 告警')
  #     _set_retry(request)
  #     return request
  #   return response


class LocalRetryMiddleware(RetryMiddleware):
  def process_response(self, request, response, spider):
    if request.meta.get('dont_retry', False):
      print('不用重试')
      return response
    
    print('进入 LocalRetryMiddleware')
    # 检查是否出现去哪儿的“请求数据错误”页面
    # 重试的时候会经过 ProxyMiddleware 进行代理 ip 更新
    page_error = response.xpath('//div[@class="error"]')
    if page_error:
      logger.debug('[爬虫异常]:发现 去哪儿 数据错误页面，需要更换代理ip重新发送请求')
      logger.debug('当前请求ip %s', request.meta.get('proxy'))
      return self._retry(request, response.status, spider) or response

    # 如果出现 403 页面，需要进行更换代理重试
    elif response.status == 403:
      logger.debug('出现 403 异常页面，需要更换代理ip重新发送请求')
      logger.debug('当前请求ip %s', request.meta.get('proxy'))
      return self._retry(request, response.status, spider) or response

    # 如果出现 407 页面，需要进行更换代理重试
    elif response.status == 407:
      logger.debug('出现 407 异常页面，需要更换代理ip重新发送请求')
      logger.debug('当前请求ip %s', request.meta.get('proxy'))
      return self._retry(request, response.status, spider) or response

    return response

class LocalRedirectMiddleware(RedirectMiddleware):
  def _redirect(self, redirected, request, spider, reason):
    # 这里 redirected 实际就是一个 request 对象
    # 如果重定向的 location 不是指定的 url，那么就进行正常重定向
    if not self._is_qunar_defense_url(redirected.url):
      return super()._redirect(redirected, request, spider, reason)
    print(f'发现反爬虫防御重定向 {request.url}')
    updateProxy(request, spider)
    # 如果返回 request 对象，那么重新调度下载，并添加一个随机值
    request.url = f'{request.url}&redirectkey={random.random()}'
    return request

  def _is_qunar_defense_url(self, url):
    return '//piao.qunar.com/captcha/pc.htm?captchaRequestURI' in url

class DealCommentApiMiddleware():
  def process_response(self, request, response, spider):
    print('进入 DealCommentApiMiddleware')
    # 如果是针对评论api的请求才进行处理
    if response.status == 200 and re.match('http://piao.qunar.com/ticket/detailLight/sightCommentList.json', request.url):
      data = json.loads(str(response.body, encoding='utf-8'))
      data = data['data']
      if 'commentList' in data:
        logger.debug('评论数据有 commentList 字段')
        return response
      else:
        logger.debug('评论数据没有 commentList 字段')
        request.url = f'{request.url}&redirectkey={random.random()}'
        return request
    return response

# 设置为一次重试
def _set_retry(request):
  retries = request.meta.get('retry_times', 0) + 1
  print(f'重试次数 {retries}')
  request.meta['retry_times'] = retries

# 获取并更新代理
def updateProxy(request, spider):
  addrProxy = AddrProxy()
  ip = addrProxy.getRandomProxyIP()
  print(f'获取代理ip为 {ip}')
  if ip:
    ip = f'http://{ip}'
    request.meta['proxy'] = ip
    spider.proxy = ip
    print(f'更换代理ip为 {ip}')
