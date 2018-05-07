import time
from pixivpy3 import *
import json
from time import sleep
import os
import member as mem
import pickle
from datetime import datetime
import sqlite as db

api = None

# ----------------------------------------------------------------------------------------------------------
# apiを利用して、絵師情報取得
# param List<tuple<followData>>
# param json(接続情報)
# param dbPath
# return tuble 失敗時(False, 失敗時のpixivID), 成功時(true, 0)
# ----------------------------------------------------------------------------------------------------------
def pixiv_artist_get(tpl_follower_list, client_info, db_path):

    imgDir = "K:/PIXIV/pixiv_images/"
    artDir = "K:/PIXIV/pixiv_artistData/"

    # ログイン処理
    api = PixivAPI()
    api.login(client_info["user_id"], client_info['password'])

    for tpl in tpl_follower_list:
        ID = tpl[0]
        start = time.time()
        # アーティスト検索から情報取得
        # try:
        artist_pixiv_id = ID

        # ここのper_pageの値を変えることで一人の絵師さんから持ってくる最大数を定義できます.
        # APIがデータ取得数により切断する。リトライ必須
        try:
            json_result = api.users_works(artist_pixiv_id, per_page=1000)
            if json_result.status == 'failure':
                continue
        except Exception as ex:
            print(type(ex))
            return False, ID

        score_list = [(idx, dic["stats"]["score"]) for idx, dic in enumerate(json_result.response)]
        dic_count = len(score_list)  # max(score_list, key=lambda item:item[1])[0]
        try:
            avg_score = round(sum(list(map(lambda x: x[1], score_list))) / dic_count)
        except:
            avg_score = 0

        artist = mem.artistData()
        artist.pixivID = ID
        # 絵師の全データより計算
        artist.avg_views_count = round(sum([dic["stats"]["views_count"] for dic in json_result.response]) / dic_count)
        artist.avg_favorited_count = \
            round(sum([dic["stats"]["favorited_count"]["public"] +
                       dic["stats"]["favorited_count"]["private"] for dic in json_result.response]) / dic_count)
        artist.score = avg_score
        # 最後のデータでアーティスト情報取得
        dic_pixiv = json_result.response[-1]
        dic_user = dic_pixiv["user"]
        artist.name = dic_user["name"]
        artist.acount = dic_user["account"]
        artist.img_count = dic_count
        artist.accessTime = datetime.now().strftime("%Y/%m/%d %H:%M:%S")

        # pickle保存
        savePath = artDir + "artist_{0}.pkl".format(ID)
        with open(savePath, 'wb') as sw:
            pickle.dump(artist, sw)
        # DB保存
        tpl = (artist.pixivID, artist.name, artist.acount, artist.avg_views_count,
               artist.avg_favorited_count, artist.score, artist.img_count, artist.accessTime)
        db.artist_set(db_path, tpl)


        # score_list.sort(key=lambda tup: tup[1], reverse=True)
        # score_list.sort(reverse=True)
        for tpl_score in score_list:
            idx = tpl_score[0]
            img_data = json_result.response[idx]
            # データ取得
            img = mem.imageData()
            img.imageID = img_data["id"]
            img.title = img_data["title"]
            img.tags = img_data["tags"]
            img.score = img_data["stats"]["score"]
            img.view_count = img_data["stats"]["views_count"]
            img.favorited_count = (img_data["stats"]["favorited_count"]["public"] + img_data["stats"]["favorited_count"]["private"])
            img.url = img_data["image_urls"]["large"]
            img.created_time = img_data["created_time"]
            # pickle保存
            hozon_dir = imgDir + "{0}/".format(ID)
            savePath = imgDir + "{0}_{1}.pkl".format(ID, img.imageID)
            with open(savePath, 'wb') as sw:
                pickle.dump(img, sw)
            # DB保存
            tpl = (img.imageID, ID, img.title, json.dumps(img.tags, ensure_ascii=False),
                   img.score, img.view_count, img.favorited_count, img.url, 0, img.created_time, None)
            db.image_set(db_path, tpl)

            # 画像ダウンロード
            # if not os.path.exists(imgDir):
            #     os.mkdir(imgDir)vchmkf
            # api.download(img_data["image_urls"]["large"], imgDir)
            # sleep(1)

        print(ID, time.time() - start)
        sleep(1)
    # 取得成功
    return True, 0


# ----------------------------------------------------------------------------------------------------------
# apiを利用して、画像取得
# apiからの切断あり
# param tuple( List<tuple(pixivID, imageID, url) >
# ----------------------------------------------------------------------------------------------------------
def pixiv_image_get(list_tpl_img, client_info, img_path, db_path):
    # ログイン処理
    api = PixivAPI()
    api.login(client_info["user_id"], client_info['password'])
    aapi = AppPixivAPI()
    # 保存
    savePath = img_path + str(list_tpl_img[0][0]) + "/"
    if not os.path.exists(savePath):  # 保存用フォルダがない場合は生成
        os.mkdir(savePath)

    for tpl_img in list_tpl_img:
        try:
            (pixivID, imageID, url) = tpl_img
            print(imageID)
            aapi.download(url, savePath)
            db.img_down_success(imageID, db_path)
            sleep(1)
        except Exception as ex:
            print(type(ex))
            return False

    return True


# ----------------------------------------------------------------------------------------------------------
# Main
# ----------------------------------------------------------------------------------------------------------
def main(tpl_follower_list, client_info, db_path):
    start = time.time()

    # ログイン処理
    # api = PixivAPI()
    # api.login(client_info["user_id"], client_info['password'])

    # フォローデータより、artist情報取得, imageデータ取得
    flg = False
    while flg == False:
        result_tpl = pixiv_artist_get(tpl_follower_list, client_info, db_path)
        flg = result_tpl[0]
        if flg == False:
            id = result_tpl[1]
            idx = [y[0] for y in tpl_follower_list].index(id)
            tpl_follower_list = tpl_follower_list[idx:]
            sleep(10)

    # 画像ダウンロード


    # 処理時間
    print("pixiv-apiより取得終了", time.time() - start)

# ----------------------------------------------------------------------------------------------------------
# スタート
# ----------------------------------------------------------------------------------------------------------
# if __name__ == "__main__":
#    main()
