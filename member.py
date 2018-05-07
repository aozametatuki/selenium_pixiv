# coding: utf-8
import json
from json import JSONEncoder

"""
ﾘｻｲﾌﾟｵﾌｨｽより取得した情報を格納
"""


class followerData:
    def __init__(self, pixiv_id=None, pixiv_name=None, comment=None):  # デフォルト値
        self.pixivID = pixiv_id
        self.pixivName = pixiv_name
        self.comment = comment


"""
作家情報
"""
class artistData:
    def __init__(self):  # デフォルト値
        self.pixivID = None  #
        self.name = None    # 漢字名
        self.acount = None  # ローマ字名
        self.avg_views_count = None       # TOP10の平均
        self.avg_favorited_count = None
        self.images = None  # list[imageData]
        self.score = None   #stats.score
        self.img_count = None #
        self.accessTime = None


"""
画像情報
"""
class imageData:
    def __init__(self):  # デフォルト値
        self.imageID = None
        self.pixivID = None
        self.title = None
        self.tags = None
        self.score = None
        self.view_count = None
        self.favorited_count = None
        self.url = None
        self.flg = None
        self.created_time = None

