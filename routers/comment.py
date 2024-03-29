# coding=utf-8
# @Time : 2023/4/30 6:46 PM
# @Author : 王思哲
# @File : test.py
# @Software: PyCharm
from io import BytesIO

import pandas as pd
from fastapi import APIRouter, Response
from openpyxl import Workbook
from starlette.responses import StreamingResponse, FileResponse

from models.comment import Comment
from models.job import Job

router = APIRouter()

# 根据job_id查询数据列表
@router.get("/grouped/{job_id}", description="根据job_id查询数据列表")
async def get_job_comments_group_by_platform(job_id: str):
    comments = await Comment.filter(job_id=job_id)
    jobs = await Job.filter(job_id=job_id)

    def get_senti_text(t):
        if t > 0:
            return "积极"
        elif t == 0:
            return "中性"
        elif t == -100:
            return "空数据"
        else:
            return "消极"

    if comments is None:
        return {"error": "Job not found"}

    platform_comments_map = {}

    for job in jobs:
        platform_comments_map["job_detail"] = job.__dict__

    platform_comments_map["job_detail"]["comments"] = {}

    for comment in comments:
        if comment.platform not in platform_comments_map["job_detail"]["comments"]:
            platform_comments_map["job_detail"]["comments"][comment.platform] = []

        t_comment = comment.__dict__
        t_comment["sentiment_level"] = get_senti_text(float(t_comment["sentiment"] if t_comment["sentiment"] is not None else -100))

        platform_comments_map["job_detail"]["comments"][comment.platform].append(t_comment)

    return platform_comments_map

# 根据job_id查询评论并导出excel文件
@router.get("/export/{job_id}", description="根据job_id查询评论并导出excel文件")
async def export_comments(job_id: str, response: Response):
    comments = await Comment.filter(job_id=job_id).all()

    def get_senti_text(t):
        if t > 0:
            return "积极"
        elif t == 0:
            return "中性"
        elif t == -100:
            return "空数据"
        else:
            return "消极"

    comments = [
        {
            "id": c.id,
            "job_id": c.job_id,
            "platform": c.platform,
            "topic": c.topic,
            "user_photo": c.user_photo,
            "user_name": c.user_name,
            "comment": c.comment,
            "create_time": c.create_time,
            "like_count": c.like_count,
            "retransmission_count": c.retransmission_count,
            "sentiment_point": c.sentiment,
            "sentiment_level": get_senti_text(float(c.sentiment if c.sentiment is not None else -100))
        }
            for c in comments
    ]
    filename = f"job_{job_id}_data.xlsx"
    filepath = "./export/" + filename
    df = pd.DataFrame(comments)
    df.to_excel(filepath, index=False)
    return FileResponse(filepath, filename=f"{filename}")









