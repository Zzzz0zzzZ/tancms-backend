import sys

import pandas as pd
import urllib.parse
import json
import re
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from db_manager import DBManager

dy_cookies_list = [{'domain': '.douyin.com',  'httpOnly': True, 'name': 'ssid_ucp_v1', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '1.0.0-KDE2OTE2NzhkMTc3Yzg3MjhjZWY0MGZlYjBkOWZjNDdmZDg4MjRhNWIKGQjGwLnY3AIQgJi9ogYY7zEgDDgGQPQHSAQaAmxxIiAxOTM5YWM1MmE2M2E3M2FiNWQ5MGIxNGJhODkzNGZkNw'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'sid_ucp_v1', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '1.0.0-KDE2OTE2NzhkMTc3Yzg3MjhjZWY0MGZlYjBkOWZjNDdmZDg4MjRhNWIKGQjGwLnY3AIQgJi9ogYY7zEgDDgGQPQHSAQaAmxxIiAxOTM5YWM1MmE2M2E3M2FiNWQ5MGIxNGJhODkzNGZkNw'}, {'domain': '.www.douyin.com', 'httpOnly': False, 'name': 'passport_fe_beating_status', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'true'}, {'domain': 'www.douyin.com', 'httpOnly': False, 'name': 'bd_ticket_guard_server_data', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': ''}, {'domain': '.douyin.com',  'httpOnly': False, 'name': 'msToken', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '4Ji30MoqPDxA-qmIlwKGuYIGYF6xQrsxEhq6iUwcy7Y8_9pge_bpuuU6aSo8dNj7m11v0uSkIJWP0qghoxg-82q5tbZ3z8GO_vUIlkYxAbBqsFKMAwV82hAFpaLQQRM='}, {'domain': '.douyin.com',  'httpOnly': False, 'name': 'publish_badge_show_info', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '%220%2C0%2C0%2C1682918397060%22'}, {'domain': 'www.douyin.com',  'httpOnly': False, 'name': 'ttcid', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1b9c5a419dd54503b8433e682ef731db21'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'sessionid_ss', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '1939ac52a63a73ab5d90b14ba8934fd7'}, {'domain': 'www.douyin.com', 'httpOnly': False, 'name': 'csrf_session_id', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'b40479af5f89907f60f805ab014baf7a'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'sessionid', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '1939ac52a63a73ab5d90b14ba8934fd7'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'n_mh', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'NeJDTq7aILISmcjZOtB-tFYUC-33KFBme2KheRY-I1U'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'sid_tt', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '1939ac52a63a73ab5d90b14ba8934fd7'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'passport_auth_status_ss', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '9fb58b409c116cc109c233b8a05a8b26%2C'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'odin_tt', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'e2724a308c3a55f895af4d53130dd1bf02a07241592e259c57ad8553497fd7f9b1ecad776f6bb93de77a464aa4ebc903'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'sid_guard', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '1939ac52a63a73ab5d90b14ba8934fd7%7C1682918400%7C5183999%7CFri%2C+30-Jun-2023+05%3A19%3A59+GMT'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'sid_ucp_sso_v1', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '1.0.0-KDRmOTkyMmNkMWJkYjRjOGRhNDhiNWJmMTJkNzNmYTcxMWViZDQ2OWEKHQjGwLnY3AIQ_Je9ogYY7zEgDDC87bvUBTgGQPQHGgJobCIgMGEzNThkOTczZjNkZWYyYTNjZGRjZGU4NDY4YTNmZWU'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'toutiao_sso_user', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '0a358d973f3def2a3cddcde8468a3fee'}, {'domain': 'www.douyin.com',  'httpOnly': False, 'name': 'msToken', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'sgJ5OLsmy-nRILMWgHkEV89RuNW1wESDW5PxpsLLGwKyVRSGIC49iQ11_pPQcYbYq7bWJWTrhKGlsYY8rRDJYS81m6TbwcZymKOBjIwTm9an1Ys2MNXGABnlvZRwSp8='}, {'domain': '.douyin.com',  'httpOnly': False, 'name': 'passport_csrf_token', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '497f1bed62fe6425e458f1473cc7eaad'}, {'domain': '.douyin.com',  'httpOnly': False, 'name': 'FOLLOW_LIVE_POINT_INFO', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '%22MS4wLjABAAAAqzHY6zqdtpBMocgoM4tK7wF-4yx8HQ0Ap_aAENuRdas%2F1682956800000%2F0%2F1682918397238%2F0%22'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'toutiao_sso_user_ss', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '0a358d973f3def2a3cddcde8468a3fee'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'sso_uid_tt_ss', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '880f8429789374c6d407a5ee6d9231b9'}, {'domain': 'www.douyin.com',  'httpOnly': False, 'name': '__ac_signature', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '_02B4Z6wo00f014oRSUgAAIDDChOzCaOQ4yuKIW3AAIbTdc'}, {'domain': '.douyin.com',  'httpOnly': False, 'name': 'home_can_add_dy_2_desktop', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '%220%22'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'uid_tt_ss', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': 'fea58e8a7f360efaaae0d8186f7f5d34'}, {'domain': 'www.douyin.com',  'httpOnly': False, 'name': 's_v_web_id', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'verify_lh4e5okw_yOJ94h4B_KByA_4crS_94Bk_LLsbeELdoJmT'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'uid_tt', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': 'fea58e8a7f360efaaae0d8186f7f5d34'}, {'domain': 'www.douyin.com',  'httpOnly': False, 'name': 'tt_scid', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '7NkJ2R.UrcKrtbH8BlHSO5mdvcuiMbdORbUTKvqu8JTXOhoUxDivbKS9MdqzEYRR623c'}, {'domain': 'www.douyin.com', 'httpOnly': False, 'name': 'bd_ticket_guard_client_data', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': 'eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtY2xpZW50LWNlcnQiOiItLS0tLUJFR0lOIENFUlRJRklDQVRFLS0tLS1cbk1JSUNFekNDQWJxZ0F3SUJBZ0lVQyt0bE9pUnpMUldKOVB1bkYxcnRYY0dPYm5Fd0NnWUlLb1pJemowRUF3SXdcbk1URUxNQWtHQTFVRUJoTUNRMDR4SWpBZ0JnTlZCQU1NR1hScFkydGxkRjluZFdGeVpGOWpZVjlsWTJSellWOHlcbk5UWXdIaGNOTWpNd05UQXhNRFV4T1RVM1doY05Nek13TlRBeE1UTXhPVFUzV2pBbk1Rc3dDUVlEVlFRR0V3SkRcblRqRVlNQllHQTFVRUF3d1BZbVJmZEdsamEyVjBYMmQxWVhKa01Ga3dFd1lIS29aSXpqMENBUVlJS29aSXpqMERcbkFRY0RRZ0FFOWJkOFZBNm54MklHeE9oTkpWY2xBMG43aFJRTVF4WTVnQndWS2hQU0FMR2hXY3VQcDBkWXoybldcbkRKWGxuUzJpaHhZZVhwNm1qZVBLdU40WFJtL3RTcU9CdVRDQnRqQU9CZ05WSFE4QkFmOEVCQU1DQmFBd01RWURcblZSMGxCQ293S0FZSUt3WUJCUVVIQXdFR0NDc0dBUVVGQndNQ0JnZ3JCZ0VGQlFjREF3WUlLd1lCQlFVSEF3UXdcbktRWURWUjBPQkNJRUlHbk9KbktpeFVpU1ozR2Q3aTlIZWlXNFBMU3JReVZJT3F4eUpxU2YwTkRiTUNzR0ExVWRcbkl3UWtNQ0tBSURLbForcU9aRWdTamN4T1RVQjdjeFNiUjIxVGVxVFJnTmQ1bEpkN0lrZURNQmtHQTFVZEVRUVNcbk1CQ0NEbmQzZHk1a2IzVjVhVzR1WTI5dE1Bb0dDQ3FHU000OUJBTUNBMGNBTUVRQ0lDQmhxSHFDTDZFZkZWcTRcbnMvZi92Ynd2UCs3OWZ3RTNCS0NtbVZYUnJ2QWVBaUEzaFBZQkFPSkpFekg2RkVmenQ4THM2dThLNzl1TmVnL2dcbk9GZjF5YXEyemc9PVxuLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLVxuIn0='}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'sso_uid_tt', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '880f8429789374c6d407a5ee6d9231b9'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'ttwid', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '1%7C-byPDDhZTIWnzLnMYLQfHVfrdrXThqgf_B4vgKMYLDM%7C1682918387%7Cceabbec29f16dc8150604867d15ef8c6b60ff4d83763d9e8424e59d1e53cf9a3'}, {'domain': '.douyin.com',  'httpOnly': False, 'name': 'passport_assist_user', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': 'CjxEYVOm9agp4yY35ZxwI4Ek_FI475r_gDZUn8su75RIaKXt2GM0kdt9k3RUyX-CjwIRZd27_1yVyf1MQdQaSAo8QldK0ABzPYvpjc6zhYRTqfCkX2GcihBvXW9VkgulyfOPJiGu7Tb1Xo-fAOokHN4PArDLRBj33VnOZK0fEPr4rw0Yia_WVCIBA3_doeI%3D'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'passport_auth_status', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '9fb58b409c116cc109c233b8a05a8b26%2C'}, {'domain': 'www.douyin.com',  'httpOnly': False, 'name': '__ac_nonce', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '0644f4bf30082886e47f1'}, {'domain': '.douyin.com',  'httpOnly': False, 'name': 'SEARCH_RESULT_LIST_TYPE', 'path': '/', 'sameSite': 'Lax', 'secure': True, 'value': '%22single%22'}, {'domain': '.douyin.com',  'httpOnly': False, 'name': 'passport_csrf_token_default', 'path': '/', 'sameSite': 'Lax', 'secure': False, 'value': '497f1bed62fe6425e458f1473cc7eaad'}, {'domain': '.douyin.com',  'httpOnly': True, 'name': 'ssid_ucp_sso_v1', 'path': '/', 'sameSite': 'None', 'secure': True, 'value': '1.0.0-KDRmOTkyMmNkMWJkYjRjOGRhNDhiNWJmMTJkNzNmYTcxMWViZDQ2OWEKHQjGwLnY3AIQ_Je9ogYY7zEgDDC87bvUBTgGQPQHGgJobCIgMGEzNThkOTczZjNkZWYyYTNjZGRjZGU4NDY4YTNmZWU'}]


class DouYin:
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
        self.search_size = search_size
        self.cookie = cookie
        self.url = None
        self.current_size = 0
        self.upload_size = 0
        self.user_names = []
        self.contents = []
        self.likes = []

        # 设置chrome浏览器，开启无界面化模式，添加user-agent等设置
        option = webdriver.ChromeOptions()
        option.add_argument('no-sandbox')
        option.add_argument('--headless')
        option.add_argument(
            "user-agent='Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/62.0.3202.94 "
            "Safari/537.36'")
        self.browser = webdriver.Chrome(options=option)

        with open("./configs/db_manager_config.txt", "r") as f:
            db = json.loads(f.read())

        self.db_manager = DBManager(db=db)

    def get_url(self):
        """
        请求网页并等待加载

        :return: 无返回值
        """
        encoded_string = urllib.parse.quote(self.search_param)
        self.url = f"https://www.douyin.com/search/{encoded_string}?"
        self.browser.get(self.url)
        WebDriverWait(self.browser, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, "//*[@class='OFZHdvpl']")))

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
        读取之前保存的cookie信息并添加到浏览器中

        :return: 无返回值
        """
        self.browser.delete_all_cookies()
        cookie_dict = {}

        if " douyin.com;" in self.cookie:
            self.cookie = self.cookie.replace(" douyin.com;", "")
        for cookie in self.cookie.split('; '):
            key, value = cookie.split('=', 1)
            cookie_dict[key] = value

        for cookie in dy_cookies_list:
            if cookie['name'] in cookie_dict.keys():
                cookie['value'] = cookie_dict[cookie['name']]
            self.browser.add_cookie(cookie)

        # 刷新页面，即可使用cookie登录
        self.browser.refresh()

    def get_result(self):
        """
        将抓取到的评论、点赞数和用户名存储到DataFrame中，然后保存到csv文件中

        :return: 无返回值
        """
        self.result['用户名'] = self.user_names
        self.result['评论'] = self.contents
        self.result['点赞数'] = self.likes
        self.result.to_csv(f"抖音评论_{self.search_param}.csv", encoding='utf-8_sig')

    def upload_result(self):
        """
        将抓取到的评论、点赞数和用户名上传到数据库中

        :return: 无返回值
        """
        sql = '''
                        INSERT INTO comments(
                            job_id, platform, user_name, comment, like_count
                        )
                        VALUES (%s, %s, %s, %s, %s)
                    '''
        comments_list = []
        for i in range(self.upload_size, len(self.user_names)):
            comments_list.append(
                [self.job_id, 'douyin', self.user_names[i], self.contents[i], str(self.likes[i])])
        self.db_manager.insert(sql=sql, data_list=comments_list)
        self.upload_size += len(comments_list)

    def work(self):
        """
        完成所有操作的主函数

        :return: 无返回值
        """
        self.get_url()
        self.set_cookie()
        self.run()
        # self.get_result()
        self.upload_result()
        self.db_manager.finish(job_id=self.job_id)
        self.browser.close()

    def expand(self, size):
        """
        根据size递归扩展评论列表
        :param size: int, 当前评论数
        :return: 无返回值
        """
        comments = len(self.browser.find_elements(By.XPATH, "//*[@data-e2e='comment-list']/div")) - 1
        if comments > size:
            return
        WebDriverWait(self.browser, 10, 0.5).until(
            EC.presence_of_element_located((By.XPATH, "//div[@class='aWSRclC8']")))
        self.browser.find_element(By.XPATH, "//div[@class='aWSRclC8']").click()
        self.expand(size)

    def run(self):
        """
        抓取包含评论的视频以及视频中的评论

        :return: 无返回值
        """
        WebDriverWait(self.browser, 10, 0.5).until(EC.presence_of_element_located((By.XPATH, "//*[@class='OFZHdvpl']")))

        videos = self.browser.find_elements(By.XPATH, "//*[@class='OFZHdvpl']")

        for video in videos:
            comments_btn = video.find_element(By.XPATH, "div[2]")
            comments_btn.click()
            WebDriverWait(self.browser, 10, 0.5).until(
                EC.presence_of_element_located((By.XPATH, "//*[@data-e2e='comment-list']")))
            comments = self.browser.find_element(By.XPATH, "//*[@data-e2e='comment-list']")
            comments_text = comments.find_element(By.XPATH, f"//span[@class='k_GzrwDi']").text
            comments_num = int(re.search('\d+', comments_text).group())
            if self.current_size == self.search_size:
                break
            if self.current_size + comments_num >= self.search_size:
                comments_num = self.search_size - self.current_size
                self.current_size = self.search_size
            else:
                self.current_size += comments_num

            # 扩展评论列表并抓取包含用户和点赞数的评论信息
            self.expand(comments_num)
            for i in range(comments_num):
                comment = comments.find_element(By.XPATH, f"div[{i + 1}]//p[@class='a9uirtCT']").text
                username = comments.find_element(By.XPATH, f"div[{i + 1}]//div[@class='nEg6zlpW']").text
                like = comments.find_element(By.XPATH, f"div[{i + 1}]//p[@class='eJuDTubq']").text
                if '万' in like:
                    like = int(float(like[:-1]) * 10000)
                self.likes.append(like)
                self.user_names.append(username)
                self.contents.append(comment)


def craw_douyin(job_id: str, search_param: str, search_size: int, cookie: str):
    """
    爬取抖音评论

    :param job_id: 工作ID
    :param search_param: 搜索关键词
    :param search_size: 搜索结果数量
    :param cookie: 存储cookie的文件路径
    :return: 无返回值
    """
    try:
        d = DouYin(job_id, search_param, search_size, cookie)
        d.work()
    except Exception as e:
        d.browser.close()


if __name__ == '__main__':
    job_id = sys.argv[1]
    search_param = sys.argv[2]
    search_size = int(sys.argv[3])
    cookie = sys.argv[4]

    # 调用函数
    craw_douyin(job_id, search_param, search_size, cookie)


