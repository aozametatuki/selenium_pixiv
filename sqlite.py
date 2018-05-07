# -*- coding: utf-8 -*-
from contextlib import closing
import sqlite3
from datetime import datetime


#  ======================================================================
#   絵師毎のダウンロードするimgURLを取得
#  <param>String dbPath
#  <return>tuple( List<tuple(pixivID, imageID, url)> , int 残り絵師数 )
#  ======================================================================
def imgurl_read(db_path):
    sql = '''
        select pixivID,imageID,url from t_image where flg = 0 and pixivID in(
        select distinct pixivID from t_image where flg = 0 order by 1 limit 1);
    '''
    list_tpl_image = []
    zan_count = 0
    try:
        with closing(sqlite3.connect(db_path)) as conn:  # auto-closes
            with conn:  # auto-commits
                with closing(conn.cursor()) as cursor:  # auto-closes
                    for row in conn.execute(sql):
                        list_tpl_image.append(row)
                with closing(conn.cursor()) as cursor2:  # auto-closes
                    for row in conn.execute("select count(*) from("
                                            "select distinct pixivID from t_image where flg = 0 order by pixivID)"):
                        zan_count = row[0]
    except Exception as ex:
        print(type(ex))
    finally:
        return list_tpl_image, zan_count


#  ======================================================================
#   ダウンロード成功
#  <param>String dbPath
#  <return>tuple( List<tuple(pixivID, imageID, url)> , int 残り絵師数 )
#  ======================================================================
def img_down_success(image_id, db_path):
    sql = '''
        update t_image set
            flg = 1,
            download_time = ?
        where
            imageID = ?
    '''
    try:
        with closing(sqlite3.connect(db_path)) as conn:  # auto-closes
            with conn:  # auto-commits
                with closing(conn.cursor()) as cursor:  # auto-closes
                    cursor.execute(sql, (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), image_id))
        return True
    except Exception as ex:
        print(type(ex))
        return False

#  ======================================================================
#   follower情報を.pklより取込
#  <param>String dbPath
#  <param>List<tuple>(member.followerData)
#  <return>Bool True：DB作成成功 False:失敗
#  ======================================================================
def follower_write(db_path, follower_tpl_list):
    sql = '''
        insert into t_follower(
            pixivID,
            name,
            comment
        )values(?,?,?)
    '''
    try:
        with closing(sqlite3.connect(db_path)) as conn:  # auto-closes
            with conn:  # auto-commits
                with closing(conn.cursor()) as cursor:  # auto-closes
                    cursor.execute("delete from t_follower")
                    cursor.executemany(sql, follower_tpl_list)

        return True
    except Exception as ex:
        print(type(ex))
        return False


#  ======================================================================
#   follower情報を.pklより取込
#  <param>String dbPath
#  <return>List<tuple>(member.followerDataをタプル化)
#  ======================================================================
def follower_read(db_path):
    tuple_follower_list = []
    sql = "select * from t_follower a where not exists (select * from t_artist b where a.pixivID=b.pixivID)"
    try:
        with closing(sqlite3.connect(db_path)) as conn:  # auto-closes
            with conn:  # auto-commits
                with closing(conn.cursor()) as cursor:  # auto-closes
                    for row in conn.execute(sql):
                        tuple_follower_list.append(row)
    except Exception as ex:
        print(type(ex))
    finally:
        return tuple_follower_list


#  ======================================================================
#   artist情報を.pklより取込
#  <param>String dbPath
#  <param>tuple(member.artistData)
#  <return>Bool True：DB作成成功 False:失敗
#  ======================================================================
def artist_set(db_path, artist_tpl):
    sql = '''
        replace into t_artist(
            pixivID,
            name,
            acount,
            avg_views_count,
            avg_favorited_count,
            avg_score,
            img_count,
            accessTime
        )values(?, ?, ?, ?, ?, ?, ?, ?)
    '''
    try:
        with closing(sqlite3.connect(db_path)) as conn:  # auto-closes
            with conn:  # auto-commits
                with closing(conn.cursor()) as cursor:  # auto-closes
                    # cursor.executemany(sql, artist_tpl_list)
                    cursor.execute(sql, artist_tpl)
        return True
    except Exception as ex:
        print(type(ex))
        return False


#  ======================================================================
#   artist情報を.pklより取込
#  <param>String dbPath
#  <param>tuple(member.artistData)
#  <return>Bool True：DB作成成功 False:失敗
#  ======================================================================
def image_set(db_path, img_tpl):
    sql = '''
        replace into t_image(
            imageID,
            pixivID,
            title,
            tags,
            score,
            view_count,
            favorited_count,
            url,
            flg,
            created_time,
            download_time
        )values(?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    '''
    try:
        with closing(sqlite3.connect(db_path)) as conn:  # auto-closes
            with conn:  # auto-commits
                with closing(conn.cursor()) as cursor:  # auto-closes
                    # cursor.executemany(sql, artist_tpl_list)
                    cursor.execute(sql, img_tpl)
        return True
    except Exception as ex:
        print(type(ex))
        return False
#  ======================================================================
#   artist情報に、Flg = 1を書き込み
#  <param>String dbPath
#  <param>List<Int> pixivID
#  <return>Bool True：DB作成成功 False:失敗
#  ======================================================================
def artist_set_flg(db_path, id_list):
    sql = '''
        update t_artist set flg = 1
        where 
        pixivID in ({0})
    '''
    try:
        with closing(sqlite3.connect(db_path)) as conn:  # auto-closes
            with conn:  # auto-commits
                with closing(conn.cursor()) as cursor:  # auto-closes
                    cursor.execute(sql.format(','.join(id_list)))

        return True
    except Exception as ex:
        print(type(ex))
        return False


#  ======================================================================
#  artist情報取得時に、acountIDとscode情報の取得を失敗している < 600000
#  その分を再取得する
#  <param> String dbPath
#  <return> List<Int>pixivIV
#
#  ======================================================================
def artist_check_read(db_path):
    idList = []
    sql = "select distinct pixivID from t_artist where flg=1 and ((acount is null or acount = '') or (avg_score is null or avg_score = 0))"
    try:
        with closing(sqlite3.connect(db_path)) as conn:  # auto-closes
            with conn:  # auto-commits
                with closing(conn.cursor()) as cursor:  # auto-closes
                    for row in conn.execute(sql):
                       idList.append(row[0])
        return idList
    except Exception as ex:
        print(type(ex))
        return idList


#  ======================================================================
#  artist情報取得時に、acountIDとscode情報の取得を失敗している < 600000
#  その分を再取得する
#  <param>String dbPath
#  <param>String Flg = Read:読み込み Write:書き込み
#  <param>List<tuple()>
#
#  ======================================================================
def artist_check_write(db_path, list_tpl):
    idList = []
    sql = "update t_artist set acount=?,avg_score=? where pixivID=?"
    try:
        with closing(sqlite3.connect(db_path)) as conn:  # auto-closes
            with conn:  # auto-commits
                with closing(conn.cursor()) as cursor:  # auto-closes
                    cursor.executemany(sql, list_tpl)
    except Exception as ex:
        print(type(ex))
        return idList
#  ======================================================================
#   DB初期化
#  <param>String dbPath
#  <return>Bool True：DB作成成功 False:失敗
#  ======================================================================
def dbMake(db_path):
    # 絵師情報
    sql1 = '''
        create table t_artist(
            pixivID number primary key,
            name text,
            acount text,
            avg_views_count number,
            avg_favorited_count number,
            avg_score number,
            img_count number,
            accessTime text
        )
    '''
    # イラスト情報
    sql2 = '''
        create table t_image(
            imageID number primary key,
            pixivID number,
            title text,
            tags text,
            score number,
            view_count number,
            favorited_count number,
            url text,
            flg number default 0,
            created_time text,
            download_time text
        )
    '''
    # フォロワー情報
    sql3 = '''
        create table t_follower(
            pixivID number,
            name text,
            comment text
        )
    '''

    try:
        with closing(sqlite3.connect(db_path)) as conn:  # auto-closes
            with conn:  # auto-commits
                with closing(conn.cursor()) as cursor:  # auto-closes
                    cursor.execute(sql1)
                    cursor.execute(sql2)
                    cursor.execute(sql3)
        return True
    except Exception as ex:
        print(type(ex))
        return False


#  ======================================================================
#   SQLiteテンプレート
#  <param>
#  <return>
#  ======================================================================
def sqlite_test():
    dbname = 'd:/tmp/database.db'

    #conn = sqlite3.connect(dbname)
    with closing(sqlite3.connect(dbname)) as conn: # auto-closes
        with conn: # auto-commits
            with closing(conn.cursor()) as cursor: # auto-closes
                # executeメソッドでSQL文を実行する
                create_table = '''create table users (id int, name varchar(64),
                                    age int, gender varchar(32))'''
                cursor.execute(create_table)

                # SQL文に値をセットする場合は，Pythonのformatメソッドなどは使わずに，
                # セットしたい場所に?を記述し，executeメソッドの第2引数に?に当てはめる値を
                # タプルで渡す．
                sql = 'insert into users (id, name, age, gender) values (?,?,?,?)'
                user = (1, 'Taro', 20, 'male')
                cursor.execute(sql, user)

                # 一度に複数のSQL文を実行したいときは，タプルのリストを作成した上で
                # executemanyメソッドを実行する
                insert_sql = 'insert into users (id, name, age, gender) values (?,?,?,?)'
                users = [
                    (2, 'Shota', 54, 'male'),
                    (3, 'Nana', 40, 'female'),
                    (4, 'Tooru', 78, 'male'),
                    (5, 'Saki', 31, 'female')
                ]
                cursor.executemany(insert_sql, users)
                conn.commit()

                select_sql = 'select * from users'
                for row in conn.execute(select_sql):
                    print(row)