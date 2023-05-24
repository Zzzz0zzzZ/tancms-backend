import pandas as pd
import urllib.parse
import json
import re
from time import sleep
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium import webdriver
from configs.cookie_template import dy_cookies_list

from utils.db_manager import DBManager


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
        # self.browser.refresh()
        self.get_url()

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
    d = DouYin(job_id, search_param, search_size, cookie)
    d.work()


if __name__ == '__main__':
    # cookie_str = "__ac_referer=https://www.douyin.com/search/%E4%B8%AB%E4%B8%AB%E5%B0%86%E5%9B%9E%E5%9B%BD?; ttwid=1%7CM0qYeOlC3cozDr3rzjJ_o9nhPvG3MsPRrc0s6R5mxzQ%7C1682833139%7C2d561f5559b537533987a6da3467a4c1bd1617099e48abed788822ea77185f31; passport_csrf_token=9ae30729b5e9bba1356568233e16e395; passport_csrf_token_default=9ae30729b5e9bba1356568233e16e395; s_v_web_id=verify_lh2zehvb_d7TXa8eo_g5Rb_4LCa_9mfT_Vu5iW3arLzjr; ttcid=97bb54662cee4f88a387b55ec8f0fa5935; n_mh=NeJDTq7aILISmcjZOtB-tFYUC-33KFBme2KheRY-I1U; sso_uid_tt=9b86261a51033cb78964fb540cb271cf; sso_uid_tt_ss=9b86261a51033cb78964fb540cb271cf; toutiao_sso_user=3598a1632aa9c41df6e78f3c5912732b; toutiao_sso_user_ss=3598a1632aa9c41df6e78f3c5912732b; passport_assist_user=Cjxi7Dti2m-7nqhSQElG_LV8guJn9OrJFW6Vqbw9-DSn8Iy5qZrrHuH9NJ1JXfPSh9DJDQwNIo322XC4dL4aSAo8vBC4E7rOTFOqP9Hvdvfdki6MfWr6gf_DVpqNjWQmdFdkZVDS2XJwxrc5xUBtS7uFKZSj5XJcUg5a3DCjENztrw0Yia_WVCIBA-w8L6k%3D; sid_ucp_sso_v1=1.0.0-KDQ2YzVlN2Y2MTQ0YzM1Yjk5MDA2ODVjY2ZiZDVjYTNhMzgxNTllMTkKHQjGwLnY3AIQlv63ogYY7zEgDDC87bvUBTgGQPQHGgJsZiIgMzU5OGExNjMyYWE5YzQxZGY2ZTc4ZjNjNTkxMjczMmI; ssid_ucp_sso_v1=1.0.0-KDQ2YzVlN2Y2MTQ0YzM1Yjk5MDA2ODVjY2ZiZDVjYTNhMzgxNTllMTkKHQjGwLnY3AIQlv63ogYY7zEgDDC87bvUBTgGQPQHGgJsZiIgMzU5OGExNjMyYWE5YzQxZGY2ZTc4ZjNjNTkxMjczMmI; odin_tt=408a232acfee40b6933197328ec241d5821a21413bfe87b93b3259575bd565b0a68cc13ca51351b2dca68362da1214d8; passport_auth_status=ea78869a3443b14995ed22d837b79ec6%2C; passport_auth_status_ss=ea78869a3443b14995ed22d837b79ec6%2C; uid_tt=eea6a317724b90def8e9966a9b4f3a6c; uid_tt_ss=eea6a317724b90def8e9966a9b4f3a6c; sid_tt=dd53e9d46963f5a395f398004a6d0c4b; sessionid=dd53e9d46963f5a395f398004a6d0c4b; sessionid_ss=dd53e9d46963f5a395f398004a6d0c4b; publish_badge_show_info=%220%2C0%2C0%2C1682833182703%22; LOGIN_STATUS=1; store-region=cn-bj; store-region-src=uid; sid_guard=dd53e9d46963f5a395f398004a6d0c4b%7C1682833184%7C5183993%7CThu%2C+29-Jun-2023+05%3A39%3A37+GMT; sid_ucp_v1=1.0.0-KGEwY2M5MzQ3YWNlYWI3NzRjZTJjMjgzMWVlZmI4ODA4YjIxMDZmOWEKGQjGwLnY3AIQoP63ogYY7zEgDDgGQPQHSAQaAmxmIiBkZDUzZTlkNDY5NjNmNWEzOTVmMzk4MDA0YTZkMGM0Yg; ssid_ucp_v1=1.0.0-KGEwY2M5MzQ3YWNlYWI3NzRjZTJjMjgzMWVlZmI4ODA4YjIxMDZmOWEKGQjGwLnY3AIQoP63ogYY7zEgDDgGQPQHSAQaAmxmIiBkZDUzZTlkNDY5NjNmNWEzOTVmMzk4MDA0YTZkMGM0Yg; d_ticket=3fa64e6818b494d22aa8276b90fc813259f9f; SEARCH_RESULT_LIST_TYPE=%22single%22; pwa2=%221%7C0%22; download_guide=%223%2F20230430%22; _tea_utm_cache_1243=undefined; MONITOR_WEB_ID=bd96c06c-009c-4f97-9bb6-8b5de8b21a93; strategyABtestKey=%221682917991.017%22; VIDEO_FILTER_MEMO_SELECT=%7B%22expireTime%22%3A1683522791062%2C%22type%22%3A1%7D; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAqzHY6zqdtpBMocgoM4tK7wF-4yx8HQ0Ap_aAENuRdas%2F1682956800000%2F0%2F0%2F1682926471553%22; amp_6e403e=_txHIOe6zsGDrfyIJvxj_P...1gvb2k56k.1gvb2k56m.0.6.6; __ac_nonce=06457367500bfd679fb25; __ac_signature=_02B4Z6wo00f01YxalVwAAIDBDFhvH.3Bx6mMepHAAAdCIpF8FsSsUC5ZMgnkOmgy3JtWykfZ6InDyFZrnYa1kWVEBNTjtY8HM76AGW0eeA26Kf0nRWDBattAOtfHyKJsHlV2k4A3wnxMQDT550; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAqzHY6zqdtpBMocgoM4tK7wF-4yx8HQ0Ap_aAENuRdas%2F1683475200000%2F0%2F1683437177761%2F0%22; msToken=oBGOMPHja9sTkcloYh2jFUAORWJMhNWqC3RaLgf0HWDwfTkmBhkfIfu4a7WrNgtfg_hQ-WqbcCaOPMlfG1OApA1A9VQlUfOtvZQvBzIxxNyaqbLlLQxT; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtY2xpZW50LWNlcnQiOiItLS0tLUJFR0lOIENFUlRJRklDQVRFLS0tLS1cbk1JSUNGVENDQWJxZ0F3SUJBZ0lVQnpPTmNDOE00U0ttUlFybEYxcWYyemFIb0lRd0NnWUlLb1pJemowRUF3SXdcbk1URUxNQWtHQTFVRUJoTUNRMDR4SWpBZ0JnTlZCQU1NR1hScFkydGxkRjluZFdGeVpGOWpZVjlsWTJSellWOHlcbk5UWXdIaGNOTWpNd05ETXdNRFV6T1RNMFdoY05Nek13TkRNd01UTXpPVE0wV2pBbk1Rc3dDUVlEVlFRR0V3SkRcblRqRVlNQllHQTFVRUF3d1BZbVJmZEdsamEyVjBYMmQxWVhKa01Ga3dFd1lIS29aSXpqMENBUVlJS29aSXpqMERcbkFRY0RRZ0FFa3hEL3pidjYzQVFIUElNT2lRWDVLS09teTVpTXJ3Q3d2bll0U0doY092Y3lOSkhPeFZVeWp2RjRcbnIwRUJVQ0ptaFFqLzN6bkVLcm9EVndCRGltZmtycU9CdVRDQnRqQU9CZ05WSFE4QkFmOEVCQU1DQmFBd01RWURcblZSMGxCQ293S0FZSUt3WUJCUVVIQXdFR0NDc0dBUVVGQndNQ0JnZ3JCZ0VGQlFjREF3WUlLd1lCQlFVSEF3UXdcbktRWURWUjBPQkNJRUlEeU5YK2dmaGNNZFNzdm9YWWRlL3ZndGREQXJMUEFMRG5SaHdWUTFMd1QvTUNzR0ExVWRcbkl3UWtNQ0tBSURLbForcU9aRWdTamN4T1RVQjdjeFNiUjIxVGVxVFJnTmQ1bEpkN0lrZURNQmtHQTFVZEVRUVNcbk1CQ0NEbmQzZHk1a2IzVjVhVzR1WTI5dE1Bb0dDQ3FHU000OUJBTUNBMGtBTUVZQ0lRREtTclduTEwrNlhIemdcbm1sbG9HbHAwOGVHdTI2Z2ZsQzFPc29YSGF5ZC8yd0loQVBZS0dKS3JnN1J2ZU9JczBpMk9CUTd5MkxjNG0vUG1cbnBBVCtrTE5RNkQzbVxuLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLVxuIn0=; home_can_add_dy_2_desktop=%221%22; csrf_session_id=5b25b5c2b6ad4348e78a072263e40817; tt_scid=Bt.oNmXPwyA3NysGLLGfGKcFopicA4LaNnX0MYSYl4A2K2Ft1pYpjakJ2NE1bXKu7b47; msToken=QCLSiQ9WqN6k3lL3BerD-qgvfIeALmYlJHQBiW4AqIgRAAln2w8MaPiL1PUuaW6JaCziFBERneh38-AiKsF_wOu_XAPSUf-DVLv9Rwf4HQktLw5IOonf; passport_fe_beating_status=false"
    cookie_str = "n_mh=NeJDTq7aILISmcjZOtB-tFYUC-33KFBme2KheRY-I1U; LOGIN_STATUS=1; store-region=cn-bj; store-region-src=uid; d_ticket=3fa64e6818b494d22aa8276b90fc813259f9f; MONITOR_WEB_ID=bd96c06c-009c-4f97-9bb6-8b5de8b21a93; amp_6e403e=_txHIOe6zsGDrfyIJvxj_P...1gvqf3j2t.1gvqf3j30.0.7.7; SEARCH_RESULT_LIST_TYPE=%22single%22; ttwid=1%7CPNCHivYtWFLA-DVeobEccJiWT9OH2LUfYAnOO_Yo8kk%7C1683511374%7C39161416352b7964e7c92c22297ec2870ea762d13c5d630c387603c87d6e9934; ttcid=c064dcfe28b14d70986f39941ae88c2681; s_v_web_id=verify_lhe7826g_znwqBuP2_ehTA_4IcL_8Mol_2UPCLq6x2eqV; passport_csrf_token=01548ee4a3ba3ef67f525507484f9632; passport_csrf_token_default=01548ee4a3ba3ef67f525507484f9632; sso_uid_tt=019317a5f85e1d859c86948378ec8d51; sso_uid_tt_ss=019317a5f85e1d859c86948378ec8d51; toutiao_sso_user=469b07b55a389bff3f454db9130511ec; toutiao_sso_user_ss=469b07b55a389bff3f454db9130511ec; passport_auth_status=01182275ddeb82714a9c2e707d65bd27%2C; passport_auth_status_ss=01182275ddeb82714a9c2e707d65bd27%2C; uid_tt=34c29fe795ea98693047afea62cba803; uid_tt_ss=34c29fe795ea98693047afea62cba803; sid_tt=3be70cd8780edb8478afda4523092e78; sessionid=3be70cd8780edb8478afda4523092e78; sessionid_ss=3be70cd8780edb8478afda4523092e78; odin_tt=acbff963cf7d0ac77ae6dee5cd8fdd2a98b08e9f980cd6e61fdf104ebac130dc01ad15053b3620e20ea67f4d03703d72; passport_assist_user=Cjy3IWD5w0L5PcCWQCDVIkoOQUwMzoNqxz8VHaXnIPxbV9v-fKa8BCwgCP6fj5tQbfrmSGRBIHGAC90_O5caSAo8MozayUX_U1rVpbX108KYCRuiAcATHewAMkyWtS6kKFja_e0plkSHTnrCUAxTmIMR2lns_lgC1G9H9RhGEKbFsA0Yia_WVCIBA4NwuLE%3D; sid_ucp_sso_v1=1.0.0-KDYzMDRjMGMyNmNhOTQyMjE4YzcwZGRmODhkZGQ2MjlmYThkNThjYmEKHQjGwLnY3AIQj7HhogYY7zEgDDC87bvUBTgGQPQHGgJobCIgNDY5YjA3YjU1YTM4OWJmZjNmNDU0ZGI5MTMwNTExZWM; ssid_ucp_sso_v1=1.0.0-KDYzMDRjMGMyNmNhOTQyMjE4YzcwZGRmODhkZGQ2MjlmYThkNThjYmEKHQjGwLnY3AIQj7HhogYY7zEgDDC87bvUBTgGQPQHGgJobCIgNDY5YjA3YjU1YTM4OWJmZjNmNDU0ZGI5MTMwNTExZWM; publish_badge_show_info=%220%2C0%2C0%2C1683511440742%22; sid_guard=3be70cd8780edb8478afda4523092e78%7C1683511442%7C5183998%7CFri%2C+07-Jul-2023+02%3A04%3A00+GMT; sid_ucp_v1=1.0.0-KDc2NzQyMjRhNWYyMWI2YmRiYjkzYmY1OGJhNjViNWM5OTlmZWRmNDMKGQjGwLnY3AIQkrHhogYY7zEgDDgGQPQHSAQaAmxmIiAzYmU3MGNkODc4MGVkYjg0NzhhZmRhNDUyMzA5MmU3OA; ssid_ucp_v1=1.0.0-KDc2NzQyMjRhNWYyMWI2YmRiYjkzYmY1OGJhNjViNWM5OTlmZWRmNDMKGQjGwLnY3AIQkrHhogYY7zEgDDgGQPQHSAQaAmxmIiAzYmU3MGNkODc4MGVkYjg0NzhhZmRhNDUyMzA5MmU3OA; strategyABtestKey=%221683511577.563%22; FOLLOW_LIVE_POINT_INFO=%22MS4wLjABAAAAqzHY6zqdtpBMocgoM4tK7wF-4yx8HQ0Ap_aAENuRdas%2F1683561600000%2F0%2F1683511577758%2F0%22; download_guide=%223%2F20230508%22; pwa2=%222%7C0%22; __ac_nonce=0645888c400784952d01c; __ac_signature=_02B4Z6wo00f01LVIw2gAAIDANUo5KGVv0xC1aMfAAEkPVRgmDpjV8rsd4xTLBlGBipKUvHusWHuctH6BYe6NX5J-Ywef4ihGkLHzgXylgFsN4JwvmyYXa5oixSx4G6lxsUsjfmHTUUBn6vbc4f; bd_ticket_guard_client_data=eyJiZC10aWNrZXQtZ3VhcmQtdmVyc2lvbiI6MiwiYmQtdGlja2V0LWd1YXJkLWl0ZXJhdGlvbi12ZXJzaW9uIjoxLCJiZC10aWNrZXQtZ3VhcmQtY2xpZW50LWNlcnQiOiItLS0tLUJFR0lOIENFUlRJRklDQVRFLS0tLS1cbk1JSUNGVENDQWJxZ0F3SUJBZ0lVQnpPTmNDOE00U0ttUlFybEYxcWYyemFIb0lRd0NnWUlLb1pJemowRUF3SXdcbk1URUxNQWtHQTFVRUJoTUNRMDR4SWpBZ0JnTlZCQU1NR1hScFkydGxkRjluZFdGeVpGOWpZVjlsWTJSellWOHlcbk5UWXdIaGNOTWpNd05ETXdNRFV6T1RNMFdoY05Nek13TkRNd01UTXpPVE0wV2pBbk1Rc3dDUVlEVlFRR0V3SkRcblRqRVlNQllHQTFVRUF3d1BZbVJmZEdsamEyVjBYMmQxWVhKa01Ga3dFd1lIS29aSXpqMENBUVlJS29aSXpqMERcbkFRY0RRZ0FFa3hEL3pidjYzQVFIUElNT2lRWDVLS09teTVpTXJ3Q3d2bll0U0doY092Y3lOSkhPeFZVeWp2RjRcbnIwRUJVQ0ptaFFqLzN6bkVLcm9EVndCRGltZmtycU9CdVRDQnRqQU9CZ05WSFE4QkFmOEVCQU1DQmFBd01RWURcblZSMGxCQ293S0FZSUt3WUJCUVVIQXdFR0NDc0dBUVVGQndNQ0JnZ3JCZ0VGQlFjREF3WUlLd1lCQlFVSEF3UXdcbktRWURWUjBPQkNJRUlEeU5YK2dmaGNNZFNzdm9YWWRlL3ZndGREQXJMUEFMRG5SaHdWUTFMd1QvTUNzR0ExVWRcbkl3UWtNQ0tBSURLbForcU9aRWdTamN4T1RVQjdjeFNiUjIxVGVxVFJnTmQ1bEpkN0lrZURNQmtHQTFVZEVRUVNcbk1CQ0NEbmQzZHk1a2IzVjVhVzR1WTI5dE1Bb0dDQ3FHU000OUJBTUNBMGtBTUVZQ0lRREtTclduTEwrNlhIemdcbm1sbG9HbHAwOGVHdTI2Z2ZsQzFPc29YSGF5ZC8yd0loQVBZS0dKS3JnN1J2ZU9JczBpMk9CUTd5MkxjNG0vUG1cbnBBVCtrTE5RNkQzbVxuLS0tLS1FTkQgQ0VSVElGSUNBVEUtLS0tLVxuIn0=; csrf_session_id=bf72bedf3ac60396261b6cabdfd45273; FOLLOW_NUMBER_YELLOW_POINT_INFO=%22MS4wLjABAAAAqzHY6zqdtpBMocgoM4tK7wF-4yx8HQ0Ap_aAENuRdas%2F1683561600000%2F0%2F0%2F1683525012607%22; douyin.com; VIDEO_FILTER_MEMO_SELECT=%7B%22expireTime%22%3A1684128652164%2C%22type%22%3A1%7D; passport_fe_beating_status=true; home_can_add_dy_2_desktop=%221%22; tt_scid=nlgajwzNRySLCCR08W-VFpp0t9EJb7doodAs9rCdKgZECdlchETpaL-yDqSerGt7971b; msToken=0jnKLnCsPk5dGrehIsOt7HvwfqTjF1NmRWPn1urFuf9L2_gzcpRwmBtzY0gp4immKcodVK-6lr0aeiyRZA4tBx-SdKwTF2Tq0ukS4WhyiJ6VWZsDALQOATi7As2fbz8=; msToken=a4w7hQiQ56ktLLr6eNnnd7AktxlCBMlimcBMNNy8BGucWLLSPyRGhtPpKEwFvBAdPvmxFHVkevFHqp7yK9JFhNfcP-oGe0FouwU2z6B67-dPcf_TgfDDZHAQwzbQdmg="
    craw_douyin("0", '丫丫将回国', 5, cookie_str)


