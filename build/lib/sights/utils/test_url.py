import unittest
from sights.utils import url as urltool

class TestUrl(unittest.TestCase):
  url = 'http://piao.qunar.com/ticket/list.htm?keyword=%E7%83%AD%E9%97%A8%E6%99%AF%E7%82%B9&region=&from=mpl_search_suggest&page=3657'

  def test_getQueryParam__case1(self):
    '''
    case: 查询的参数在 url 中存在
    '''
    param = 'page'
    value = urltool.getQueryParam(self.url, param)
    self.assertEqual(value, '3657')
  
  def test_getQueryParam__case1_1(self):
    param = 'keyword'
    url = 'http://piao.qunar.com/ticket/list.htm?keyword=%E5%85%AD%E7%9B%98%E6%B0%B4%E5%B8%82&page=1'
    value = urltool.getQueryParam(url, param)
    self.assertEqual(value, '六盘水市')
  
  def test_getQueryParam__case1_2(self):
    param = 'flag'
    url = 'http://piao.qunar.com/ticket/detail_775187833.html?flag=1'
    value = urltool.getQueryParam(url, param)
    self.assertEqual(value, '1')
  
  def test_getQueryParam__case1_3(self):
    param = 'flag'
    url = 'http://piao.qunar.com/ticket/detail_775187833.html'
    value = urltool.getQueryParam(url, param)
    self.assertIsNone(value)

  def test_getQueryParam__case2(self):
    '''
    case: 查询的参数在 url 中不存在
    '''
    param = 'page'
    url = 'http://piao.qunar.com/ticket/list.htm?keyword=%E7%83%AD%E9%97%A8%E6%99%AF%E7%82%B9&region=&from=mpl_search_suggest'
    value = urltool.getQueryParam(url, param)
    self.assertEqual(value, None)


if __name__ == '__main__':
  unittest.main()
