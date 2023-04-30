# coding=utf-8
# @Time : 2023/4/30 6:13 PM
# @Author : 王思哲
# @File : job.py
# @Software: PyCharm
from fastapi import APIRouter
from uuid import uuid4
from pydantic import BaseModel
from typing import Dict
from utils.globalq import tasks_queue
from models.job import Job
from utils.logger import debug


class JobCreateRequest(BaseModel):
    search_param: str  # 查询内容
    search_platform: str  # 查询平台，用｜隔开; 查询平台有 "weibo" "xhs" "bilibili" "douyin"; 如参例如: "weibo|xhs|bilibili"
    search_size: Dict[str, int]  # 每个平台的查询数量
    cookie: Dict[str, str]  # cookie传入以键值对的形式，键必须与查询平台对应


router = APIRouter()


# 创建任务
@router.post("/", description="创建爬虫任务")
async def create_job(job_request: JobCreateRequest):
    job_id = str(uuid4())
    job = Job(job_id=job_id, search_param=job_request.search_param, search_platform=job_request.search_platform)

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
    return {"id": job.id, "job_id": job.job_id, "search_param": job.search_param,
            "search_platform": job.search_platform,
            "create_time": job.create_time, "status": job.status}


# 获取任务列表
@router.get("/", description="获取爬虫任务列表")
async def get_jobs():
    jobs = await Job.all()
    return [{
        "id": job.id,
        "job_id": job.job_id,
        "search_param": job.search_param,
        "search_platform": job.search_platform,
        "create_time": job.create_time,
        "status": job.status
    } for job in jobs]
