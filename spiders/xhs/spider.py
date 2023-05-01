# coding=utf-8
# @Time : 2023/5/1 11:00 PM
# @Author : 王思哲
# @File : spider.py
# @Software: PyCharm
import json

from xhs import XhsClient
from utils.db_manager import DBManager


def craw_xhs(job_id: str, search_param: str, search_size: int, cookie: str) -> None:
    # search_size 搜索多少篇笔记 20以内

    with open("./configs/db_manager_config.txt", "r") as f:
        db = json.loads(f.read())

    jid = job_id
    error_count = 0
    retry_times = 3
    note_count = 0

    db_manager = DBManager(db=db)
    sql = '''
        INSERT INTO comments(
            job_id, platform, topic, user_photo, user_name, comment, create_time, like_count
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    '''

    xhs_client = XhsClient(cookie)

    notes = xhs_client.get_note_by_keyword(
        keyword=search_param
    )

    # get all notes id
    for note in notes['items']:
        if note_count <= search_size:
            note_count += 1

            note_id = note['id']
            note_title = "<没有标题>"
            try:
                note_title = note['note_card']['display_title']
                # get comment list
                comments = xhs_client.get_note_all_comments(note_id=note_id)

                comments_list = [
                    [jid, 'xhs', note_title, comment['user_info']['image'], comment['user_info']['nickname'],
                     comment['content'], comment['create_time'], comment['like_count']]
                    for comment in comments
                ]

                db_manager.insert(sql=sql, data_list=comments_list)

            except Exception as e:
                if error_count > retry_times:
                    break
                error_count += 1
                continue

    db_manager.finish(job_id=jid)

