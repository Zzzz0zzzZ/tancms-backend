# coding=utf-8
# @Time : 2023/4/30 6:46 PM
# @Author : 王思哲
# @File : test.py
# @Software: PyCharm
from fastapi import APIRouter
from models.comment import Comment
from models.job import Job

router = APIRouter()

# 根据job_id查询数据列表
@router.get("/grouped/{job_id}", description="根据job_id查询数据列表")
async def get_job_comments_group_by_platform(job_id: str):
    comments = await Comment.filter(job_id=job_id)
    jobs = await Job.filter(job_id=job_id)

    if comments is None:
        return {"error": "Job not found"}

    platform_comments_map = {}

    for comment in comments:
        if comment.platform not in platform_comments_map:
            platform_comments_map[comment.platform] = []

        platform_comments_map[comment.platform].append(comment.__dict__)

    platform_comments_map["job_detail"] = [job.__dict__ for job in jobs]

    return platform_comments_map


