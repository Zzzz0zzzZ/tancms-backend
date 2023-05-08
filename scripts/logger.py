# coding=utf-8
# @Time : 2023/4/30 5:39 PM
# @Author : 王思哲
# @File : logger.py
# @Software: PyCharm
from datetime import datetime


def log(msg):
    print(f"\033[32m[INFO {datetime.now()}] {msg}\033[0m\n")

def debug(msg, DEBUG=True):
    if DEBUG:
        print(f"\033[93m[DEBUG {datetime.now()}] {msg}\033[0m\n")