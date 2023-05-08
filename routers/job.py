# coding=utf-8
# @Time : 2023/4/30 6:13 PM
# @Author : 王思哲
# @File : job.py
# @Software: PyCharm
from typing import Dict
from uuid import uuid4
from fastapi import APIRouter, Body
from pydantic import BaseModel
from models.job import Job
from utils.globalq import tasks_queue
from utils.logger import debug


class JobCreateRequest(BaseModel):
    search_param: str  # 查询内容
    search_platform: str  # 查询平台，用｜隔开; 查询平台有 "weibo" "xhs" "bilibili" "douyin"; 如参例如: "weibo|xhs|bilibili"
    search_size: Dict[str, int]  # 每个平台的查询数量
    cookie: Dict[str, str]  # cookie传入以键值对的形式，键必须与查询平台对应


router = APIRouter()


# 创建爬虫任务
@router.post("", description="创建爬虫任务")
async def create_job(job_request: JobCreateRequest = Body(example={
    "search_param": "搜索关键词",
    "search_platform": "xhs|bilibili|douyin|weibo",
    "search_size": {
        "douyin": 10,
        "weibo": 10,
        "xhs": 1,
        "bilibili": 1
    },
    "cookie": {
        "douyin": "用户的cookie",
        "weibo": "用户的cookie",
        "xhs": "用户的cookie",
        "bilibili": "用户的cookie"
    }
})):
    job_id = str(uuid4())
    job = Job(
        job_id=job_id,
        search_param=job_request.search_param,
        search_platform=job_request.search_platform,
        search_size=len(job_request.search_platform.split("|"))
    )

    for job_per_platform in job_request.search_platform.split("|"):
        job_details = {
            "job_id": job_id,
            "search_platform": job_per_platform,
            "search_param": job_request.search_param,
            "search_size": job_request.search_size[job_per_platform],
            "cookie": job_request.cookie[job_per_platform]
        }
        tasks_queue.put(job_details)

    debug(f"/jobs/  请求参数:   {job_request}")
    await job.save()
    return job.__dict__


# 获取任务列表
@router.get("", description="获取爬虫任务列表")
async def get_jobs():
    jobs = await Job.all()
    return [job.__dict__ for job in jobs]
