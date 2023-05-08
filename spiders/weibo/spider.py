import json
from time import sleep
import urllib.parse

from selenium import webdriver
from selenium.common import exceptions
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import pandas as pd
from configs.cookie_template import wb_cookies_list
from utils.db_manager import DBManager


class Weibo:
    def __init__(self, job_id, search_param, search_size, cookie):
        """
        初始化Weibo类

        :param job_id: 工作ID
        :param search_param: 搜索关键词
        :param search_size: 搜索结果数量
        :param cookie: 存储cookie的文件路径
        """
        self.result = pd.DataFrame()
        self.job_id = job_id
        self.search_param = search_param
        self.url = None
        self.search_size = search_size
        self.cookie = cookie
        self.current_size = 0
        self.upload_size = 0
        self.user_names = []
        self.contents = []
        self.forwards = []
        self.comments = []
        self.likes = []

        # 浏览器选项
        self.chrome_options = webdriver.ChromeOptions()
        self.chrome_options.add_argument('no-sandbox')
        self.chrome_options.add_argument('--headless')
        self.chrome_options.add_argument(
            "user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 "
            "Safari/537.36'")
        self.browser = webdriver.Chrome(options=self.chrome_options)

        with open("./configs/db_manager_config.txt", "r") as f:
            db = json.loads(f.read())

        self.db_manager = DBManager(db=db)

    def get_url(self):
        """
        请求网页并等待加载

        :return: 无返回值
        """
        encoded_string = urllib.parse.quote(self.search_param)
        self.url = f"https://s.weibo.com/weibo?q={encoded_string}&t=31&band_rank=2&Refer=top"
        self.browser.get(self.url)
        WebDriverWait(self.browser, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, "//*[@action-type"
                                                                                             "='feed_list_item']")))

    def is_element_exist(self, driver, xpath):
        """
        判断元素是否存在

        :param driver: webdriver对象
        :param xpath: 元素的xpath
        :return: True或False
        """
        try:
            driver.find_element(By.XPATH, xpath)
            return True
        except exceptions.NoSuchElementException:
            return False

    def get_cookie(self):
        """
        获取用户登录后的cookie并存储到文件中

        :return: 无返回值
        """
        self.browser.get(self.url)

        # 在这个时间里手动登录，并等待页面加载cookie信息
        print("请手动登录并等待20秒...")
        sleep(20)

        with open('DouYin_cookies.txt', 'w') as f:
            # 将cookies保存为json格式并写入文件
            f.write(json.dumps(self.browser.get_cookies()))
        self.browser.close()

    def set_cookie(self):
        """
        设置cookie

        :return: 无返回值
        """
        self.browser.delete_all_cookies()
        cookie_dict = {}
        for cookie in self.cookie.split('; '):
            key, value = cookie.split('=', 1)
            cookie_dict[key] = value

        for cookie in wb_cookies_list:
            if cookie['name'] in cookie_dict.keys():
                cookie['value'] = cookie_dict[cookie['name']]
            self.browser.add_cookie(cookie)

        # 刷新页面，即可使用cookie登录
        self.browser.refresh()

    def upload_result(self):
        """
        将结果保存到数据库中

        :return: 无返回值
        """

        sql = '''
                INSERT INTO comments(
                    job_id, platform, user_name, comment, like_count, retransmission_count
                )
                VALUES (%s, %s, %s, %s, %s, %s)
            '''
        comments_list = []
        for i in range(self.upload_size, len(self.user_names)):
            comments_list.append(
                [self.job_id, 'weibo', self.user_names[i], self.contents[i], self.likes[i], self.forwards[i]])
        self.db_manager.insert(sql=sql, data_list=comments_list)
        self.upload_size += len(comments_list)

    def get_result(self):
        """
        将结果保存到csv文件中

        :return: 无返回值
        """
        self.result['用户名'] = self.user_names
        self.result['评论'] = self.contents
        self.result['转发数'] = self.forwards
        self.result['评论数'] = self.comments
        self.result['点赞数'] = self.likes
        self.result.to_csv(f"微博评论_{self.search_param}.csv", encoding='utf-8_sig')

    def work(self):
        """
        工作流程，包括设置url，设置cookie，运行程序，保存结果

        :return: 无返回值
        """
        self.get_url()
        self.set_cookie()
        self.run()
        self.db_manager.finish(job_id=self.job_id)
        self.browser.close()

    def run(self):
        """
        程序运行流程，包括获取搜索结果，解析结果，翻页等

        :return: 无返回值
        """
        WebDriverWait(self.browser, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, "//*[@action-type"
                                                                                             "='feed_list_item']")))
        items = self.browser.find_elements(By.XPATH, "//*[@action-type='feed_list_item']/div[@class='card']")
        for item in items:
            if self.current_size == self.search_size:
                self.upload_result()
                return
            self.current_size += 1
            feed = item.find_element(By.XPATH, "div[@class='card-feed']/div[@class='content']")
            self.user_names.append(feed.find_element(By.XPATH, "div[@class='info']/div[2]").text)

            if self.is_element_exist(feed, "p[@node-type='feed_list_content']/a[@action-type='fl_unfold']/i"):
                feed.find_element(By.XPATH, "p[@node-type='feed_list_content']/a[@action-type='fl_unfold']/i").click()
                self.contents.append(feed.find_element(By.XPATH, "p[@node-type='feed_list_content_full']").text)
            else:
                self.contents.append(feed.find_element(By.XPATH, "p[@node-type='feed_list_content']").text)

            acts = item.find_elements(By.XPATH, "div[@class='card-act']/ul/li")

            if acts[1].text == "转发":
                self.forwards.append(0)
            else:
                self.forwards.append(int(acts[1].text[3:]))

            if acts[2].text == "评论":
                self.comments.append(0)
            else:
                self.comments.append(int(acts[2].text[3:]))

            if acts[3].find_element(By.XPATH, "a/em").text == "":
                self.likes.append(0)
            else:
                self.likes.append(int(acts[3].find_element(By.XPATH, "a/em").text))

        self.upload_result()

        if self.is_element_exist(self.browser, "//div[@class='m-page']//*[text()='下一页']"):
            self.browser.find_element(By.XPATH, "//div[@class='m-page']//*[text()='下一页']").click()
            self.run()

        self.browser.quit()


def craw_weibo(job_id: str, search_param: str, search_size: int, cookie: str):
    """
    爬取微博评论

    :param job_id: 工作ID
    :param search_param: 搜索关键词
    :param search_size: 搜索结果数量
    :param cookie: 存储cookie的文件路径
    :return: 无返回值
    """
    w = Weibo(job_id, search_param, search_size, cookie)
    # w.get_cookie()
    w.work()


if __name__ == '__main__':
    cookie_str = "SUB=_2A25JVWp8DeRhGeBK71EV8C7Iwz2IHXVqI9y0rDV8PUNbmtAGLWv6kW9NR6sWy4Vyg5EHsbLAAKhN0WReT-iN_srr; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WFU.HO6vhCZ5ZqSupQUQZul5JpX5KzhUgL.FoqXSheXeh5X1h22dJLoIp7LxKML1KBLBKnLxKqL1hnLBoMcShB0Sh57Shnp; ALF=1714572716; SSOLoginState=1683036716; _s_tentry=-; Apache=3001444062240.0127.1683037192464; SINAGLOBAL=3001444062240.0127.1683037192464; ULV=1683037192470:1:1:1:3001444062240.0127.1683037192464:; PC_TOKEN=62fabcb1ff; WBStorage=4d96c54e|undefined"
    craw_weibo(0, "丫丫将回国", 30, cookie_str)
