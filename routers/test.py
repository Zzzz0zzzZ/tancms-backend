# coding=utf-8
# @Time : 2023/4/30 6:46 PM
# @Author : 王思哲
# @File : test.py
# @Software: PyCharm

from uuid import uuid4

from fastapi import APIRouter

from utils.globalq import tasks_queue

router = APIRouter()


# 发送到消息队列
@router.post("/")
async def set_task(keywords: dict):
    job_id = uuid4()
    keywords["job_id"] = job_id
    tasks_queue.put(keywords)
    return {
        "message": "Task received and scheduled for processing.",
        "job_id": job_id
    }