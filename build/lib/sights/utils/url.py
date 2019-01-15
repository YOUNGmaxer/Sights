from urllib import parse

# 获取 url 某个参数值
def getQueryParam(url, param):
  queryString = parse.urlparse(url).query
  paramDict = parse.parse_qs(queryString)
  if param in paramDict:
    return paramDict[param][0]
  else:
    print(f'{param} 不存在！')
    return None
