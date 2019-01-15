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
