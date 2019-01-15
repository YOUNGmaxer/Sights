from urllib import request
import requests
from requests import exceptions
import json

class AddrProxy():
  def __init__(self):
    self.host = 'http://106.13.70.140'
    self.port = '5000'
    self.domain = ':'.join([self.host, self.port])
    self.error_info = '[Proxy Middleware]{}:'.format(__name__)

  def getRandomProxyIP(self):
    '''
    获得一个随机的代理IP
    :return: IP
    '''
    api = 'random'
    res = self.requestApi(api)
    return res.text
    
  def isIpExist(self, ip):
    api = 'exist/{}'.format(ip)
    res = self.requestApi(api)
    res = json.loads(res.text)
    return res['ret']

  def requestApi(self, api):
    '''
    用于请求 api 的模版
    :param api: 请求的api的path部分
    :return: 返回api的响应内容
    '''
    url = '/'.join([self.domain, api])
    try:
      res = requests.get(url, timeout=5)
      # 若返回的是不成功的状态码，会抛出异常 HTTPError
      res.raise_for_status()
      return res
    except exceptions.Timeout as e:
      print(self.error_info, 'Timeout', e)
      return None
    except exceptions.HTTPError as e:
      print(self.error_info, 'HTTPError', e)
      return None


# def proxy_request(URL, proxyIP):
#   proxyIP = getProxyIP()
#   if proxyIP:
#     proxy = { 'http': proxyIP }
#     proxy_support = request.ProxyHandler(proxy)
#     opener = request.build_opener(proxy_support)
#     opener.addheaders = {
#       ("User-Agent", "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/71.0.3578.98 Safari/537.36")
#     }
#     request.install_opener(opener)
#     response = request.urlopen(URL)
#     html = response.read().decode('utf-8')
#     print(html)
#     return html
#   else:
#     print('获取不到代理IP!')
#     return -1

# def getProxyIP():
#   url = 'localhost:5000/random'
#   res = requests.get(url)
#   return res
