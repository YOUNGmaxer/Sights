# 调用 Baidu OCR API 将图片识别为文本
import base64
import requests
import json

'''
Args:
  filePath: 必写。图片的存储路径。
  apiType: 可选。表示调用Baidu的哪个api来进行识别（Baidu提供多个api，有强弱精度区别）
'''
def transImage2Text(filePath, apiType = 0):
  # 首先将图片转化为 base64
  with open(filePath, 'rb') as f:
    base64_data = base64.b64encode(f.read())

  # 请求所需内容
  # 此token需要30天更换一次
  ACCESS_TOKEN = '24.b190c799dc1d8a9c48d276a9cd92d084.2592000.1549069278.282335-15327006'
  OCR_URL = [
    'https://aip.baidubce.com/rest/2.0/ocr/v1/accurate?access_token={}'.format(ACCESS_TOKEN)
  ]
  BODY = {
    'image_type': 'BASE64',
    'image': base64_data,
    'group_id': 'group001',
    'user_id': '0001'
  }
  HEADER = {
    'Content-Type': 'application/x-www-form-urlencoded'
  }

  try:
    if apiType >=0 and apiType < len(OCR_URL):
      r = requests.post(OCR_URL[apiType], data=BODY, headers=HEADER)
      res = json.loads(r.text)
      if res['words_result_num'] > 0:
        return res['words_result']
      else:
        print('[识别失败]: 识别得到的结果为 0 个')
        return -1
    else:
      print('输入的参数可能有误！')
  except Exception:
    print('调用 API 请求出现异常！')


  
