import scrapy
from scrapy import Field

class SightsItem(scrapy.Item):
  # 景点名称
  name = Field()
  # 景点id
  sid = Field()
  # 景点经纬度
  point = Field()
  # 景点地区
  districts = Field()
  # 景点地址
  address = Field()
  # 景点销量
  sale_count = Field()
  # 城市
  city = Field()

class SightsDetailItem(scrapy.Item):
  # 景点id
  sid = Field()
  # 景区评级
  level = Field()
  # 景点评分
  star_score = Field()
  # 景点起步价
  basic_price = Field()
  # 城市
  city = Field()
  '''
  景点评论分布
  :key all: 全部评论数
  :key good: 好评数
  :key mid: 中评数
  :key bad: 差评数
  '''
  comment = Field()
  '''
  景点热评标签
  :key 某特点: 评论数
  '''
  tags = Field()

class SightsPageItem(scrapy.Item):
  url = Field()
  page = Field()

# 用于添加 rid 或补充信息
class SightsIdItem(SightsDetailItem):
  rid = Field()

# 用于存储评论信息
class CommentItem(scrapy.Item):
  # rid
  rid = Field()
  # 评论用户
  author = Field()
  # 评论内容
  content = Field()
  # 评论时间
  date = Field()
  # 评论分数
  score = Field()
  # 评论id
  commentId = Field()
  # 用户昵称
  userNickName = Field()
