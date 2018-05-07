import member as mem
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException
from selenium.common.exceptions import StaleElementReferenceException
from selenium.common.exceptions import WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.select import Select

waitSecond = 3

# ----------------------------------------------------------------------------------------------------------
# webDriver 初期化
# ----------------------------------------------------------------------------------------------------------
def driver_init(driver):
    options = Options()
    # options.binary_location = "C:\\Program Files (x86)\\Google\\Chrome\\Application\\chrome.exe"
    options.add_argument('--headless')
    options.add_argument('--disable-gpu')
    options.add_argument('--window-size=1024,768')
    """
    # driver = webdriver.Chrome(
        chrome_options=options, executable_path="D:\\Program\\chromedriver_win32\\chromedriver.exe")
    """
    driver = webdriver.Chrome(chrome_options=options)
    return driver


# ----------------------------------------------------------------------------------------------------------
# ページ読み込み待ち
# ----------------------------------------------------------------------------------------------------------
def page_loaded(web_driver):
   try:
        WebDriverWait(web_driver, waitSecond).until(
            lambda x: x.execute_script('return document.readyState;') == 'complete'
        )
        return True
   except:
        return False

# ----------------------------------------------------------------------------------------------------------
# 要素読み込み待ち
# ----------------------------------------------------------------------------------------------------------
def wait_element(web_driver, locator):
    element = WebDriverWait(web_driver, waitSecond).until(
        # lambda x: x.find_element_by_id(elementID)
        # EC.presence_of_element_located(locator)
        EC.visibility_of_element_located(locator)
    )
    return element

# ----------------------------------------------------------------------------------------------------------
# ログオン
# param driver
# return Bool( True: 成功, False: 失敗)
# ----------------------------------------------------------------------------------------------------------
def logon(driver, info):
    try:
        driver.get("https://accounts.pixiv.net/login")
        if not page_loaded(driver):
            raise Exception

        # ID
        locator = (By.XPATH, '//*[@id="LoginComponent"]/form/div[1]/div[1]/input')
        ele = wait_element(driver, locator)
        if ele == None:
            return False
        ele.send_keys(info["user_id"])

        # ID
        locator = (By.XPATH, '//*[@id="LoginComponent"]/form/div[1]/div[2]/input')
        ele = wait_element(driver, locator)
        if ele == None:
            return False
        ele.send_keys(info["password"])
        # 登録ボタン
        locator = (By.XPATH, '//*[@id="LoginComponent"]/form/button')
        ele = wait_element(driver, locator)
        ele.click()

        # 画面更新待ち
        driver.implicitly_wait(1)  # seconds
        return True
    except Exception as ex:
        print(type(ex))
        return False


    # 管理者画面 (画面操作のみ)
    # driver.find_element_by_css_selector("a.open_user_menu").click()
    # driver.find_element_by_xpath("//a[text()='管理者設定']").click()
    # driver.find_element_by_link_text("管理者システム設定").click()
    # driver.find_element_by_link_text("利用者設定").click()

# ----------------------------------------------------------------------------------------------------------
#
# param driver
# return List<followerData>
# ----------------------------------------------------------------------------------------------------------
def main_to_follower(driver):
    follow_list = []

    # フォロワー数を取得
    following_users_num = int(driver.find_element_by_xpath(
        "/html/body/div[3]/div[1]/div[1]/div[1]/ul[2]/li[1]/a/span[2]").text)

    # フォローユーザー一覧ページのページ数を取得
    if (following_users_num % 48 != 0):
        pages = (following_users_num // 48) + 1
    else:
        pages = following_users_num // 48

    # フォロワー詳細画面へリンククリック

    driver.find_element_by_xpath('/html/body/div[3]/div[1]/div[1]/div[1]/ul[2]/li[1]/a').click()
    for page in range(1, (pages + 1)):
        # 画面更新待ち
        driver.implicitly_wait(2)  # seconds
        # 画面のフォローメンバーを取得
        elements = driver.find_elements_by_xpath(
            "/html/body/div[3]/div[1]/div/div[2]/section/form/section/div[1]/ul/li/div[@class='userdata']")

        for l in elements:
            try:
                m = mem.followerData()
                m.comment = l.text
                tag_a = l.find_element_by_xpath("a")
                m.pixivID = tag_a.get_attribute("data-user_id")
                if m.pixivID == "11":
                    continue
                m.pixivName = tag_a.get_attribute("data-user_name")
                print(m.pixivName)

                follow_list.append(m)
            except Exception as ex:
                print(type(ex))
                continue
        # nextPage
        if pages > page:
            if page < 2:
                ele = driver.find_element_by_xpath(
                    "/html/body/div[3]/div[1]/div/div[2]/section/form/section/div[2]/ol/li/a[@class='button']")
                ele.click()
            else:
                ele = driver.find_elements_by_xpath(
                    "/html/body/div[3]/div[1]/div/div[2]/section/form/section/div[2]/ol/li/a[@class='button']")
                ele[1].click()
    return follow_list



# ----------------------------------------------------------------------------------------------------------
#  pixivにログオンしてフォローデータを返す
# return List<MemberData>
# ----------------------------------------------------------------------------------------------------------
def main(info):
    driver = None
    driver = driver_init(driver)

    # 認証
    if not logon(driver, info):
        raise Exception()

    # メイン画面からフォロワー画面へ
    member_list = main_to_follower(driver)
    return member_list