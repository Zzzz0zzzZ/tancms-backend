# coding=utf-8
# @Time : 2023/5/27 1:03 AM
# @Author : 王思哲
# @File : analyze.py
# @Software: PyCharm
import json

from fastapi import APIRouter
from fastapi import Query
from starlette.responses import StreamingResponse

from analysis.senti.visualization import drawpic as getpic_senti
from utils.db_manager import DBManager

with open("./configs/db_manager_config.txt", "r") as f:
    db = json.loads(f.read())
dbm = DBManager(db=db)

router = APIRouter()


# 获取分析图片
@router.get("/pic")
async def get_pics(type: str = Query(...), job_id: str = Query(...), platform: str = Query(...)):

    if platform not in ["xhs", "bilibili", "weibo", "douyin", "all"]:
        return "platform_error"

    if type == "sentiment":

        data = dbm.get_senti_score(job_id=job_id, platform=platform)

        senti_filename = getpic_senti(data)

        photo = open(senti_filename, mode="rb")
        return StreamingResponse(
            photo,
            media_type="image/png"
        )


    elif type == "statistic":
        # stat_filename = getpic_stat()

        return "功能完善中"

    return "type_error"


