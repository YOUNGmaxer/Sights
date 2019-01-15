import unittest
from sights.utils.ip_proxy import AddrProxy

class TestAddrProxy(unittest.TestCase):
  def test_getRandomProxyIP(self):
    addrProxy = AddrProxy()
    ip = addrProxy.getRandomProxyIP()
    self.assertTrue(addrProxy.isIpExist(ip))

if __name__ == '__main__':
  unittest.main()
