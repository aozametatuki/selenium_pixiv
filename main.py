import time
import datetime
import sys,os

from datetime import datetime
import pickle
import json
import random
import pixiv_selenium as web
import sqlite as db
import pixiv_api
waitSecond = 3
client_info_path = 'K:/PIXIV/client.json'
follower_path = "K:/PIXIV/follower.pkl"
db_path = 'K:/PIXIV/pixiv.db'
img_path = "K:/PIXIV/pixiv_images/"

# ----------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------
def main():

    start = time.time()
    # pixiv ログイン情報

    with open(client_info_path, 'r') as sr:
        client_info = json.load(sr)

    # selenium
    # follower情報取込
    # 更新時間から２０時間経過なら再取得


    follower_flg = True
    if os.path.exists(follower_path):
        ctime = os.path.getctime(follower_path)
        if (start - ctime) / 60 / 60 < 20:
            follower_flg = False

    if follower_flg:
        follower_list = web.main(client_info)
        #
        with open(follower_path, 'wb') as sw:
            pickle.dump(follower_list, sw)
    else:
        with open(follower_path, 'rb') as sr:
            follower_list = pickle.load(sr)

    # DB準備
    if not os.path.exists(db_path):
        flg = db.dbMake(db_path)

    idlist = set(list(map(lambda x: x.pixivID, follower_list)))
    # DB書込
    tpl_follower = list(map(lambda x: (x.pixivID, x.pixivName, x.comment), follower_list))
    db.follower_write(db_path, tpl_follower)


    # api
    # 絵師情報取得
    # db読取 t_followerが、t_artistに存在しないリスト取得
    tpl_follower = db.follower_read(db_path)
    # 絵師情報（その中にimage情報あり）取得
    pixiv_api.main(tpl_follower, client_info, db_path)
    # 絵師毎の画像URL取得
    zan = 99
    print("ダウンロード開始")
    while zan != 0:
        (tpl_images, zan) = db.imgurl_read(db_path)
        if len(tpl_images) > 0:
            print("絵師：", tpl_images[0][0], ", 枚数：", len(tpl_images))
            pixiv_api.pixiv_image_get(tpl_images, client_info, img_path, db_path)
            time.sleep(5)


    # 処理時間
    print(time.time() - start)




# ----------------------------------------------------------------------------------------------------------
# スタート
# ----------------------------------------------------------------------------------------------------------
if __name__ == "__main__":
    main()
