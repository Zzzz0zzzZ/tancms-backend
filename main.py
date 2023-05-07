import asyncio
import queue
import random
import json
import uvicorn
from fastapi import FastAPI
from tortoise.contrib.fastapi import register_tortoise
from utils.globalq import tasks_queue
from routers.job import router as job_router
from routers.test import router as test_router
from utils.logger import log
from spiders.xhs.spider import craw_xhs
from spiders.weibo.spider import craw_weibo
from spiders.douyin.spider import craw_douyin
NUM_WORKERS = 3     # 爬虫工作协程

with open("./configs/config.txt", "r") as f:
    config = json.loads(f.read())

app = FastAPI()

app.include_router(job_router, prefix="/jobs")
app.include_router(test_router, prefix="/test")

# 注册数据库连接
register_tortoise(
    app,
    db_url=config["db_url"],
    modules={"models": ["models.job"]},
    # generate_schemas=True
)


# 处理消息队列爬虫
async def spider_task():
    task_name = asyncio.current_task().get_name()
    log(f"{task_name} is waiting for task...")
    while True:
        try:
            job = tasks_queue.get_nowait()
            log(f"JOBS:    queue_size {tasks_queue.qsize()}| job {job}| WORKER {task_name}  finished!")
            # TODO: 根据search_platform调用爬虫
            if job['search_platform'] == 'xhs':
                craw_xhs(
                    job_id=job['job_id'],
                    search_param=job['search_param'],
                    search_size=job['search_size'],
                    cookie=job['cookie']
                )
            elif job['search_platform'] == 'weibo':
                craw_weibo(
                    job_id=job['job_id'],
                    search_param=job['search_param'],
                    search_size=job['search_size'],
                    cookie=job['cookie']
                )
            elif job['search_platform'] == 'douyin':
                craw_douyin(
                    job_id=job['job_id'],
                    search_param=job['search_param'],
                    search_size=job['search_size'],
                    cookie=job['cookie']
                )
            await asyncio.sleep(random.randint(0, 5))
        except queue.Empty:
            await asyncio.sleep(1)
            continue


# 初始化
@app.on_event("startup")
async def startup_event():
    # 开启多个爬虫协程
    for i in range(NUM_WORKERS):
        asyncio.create_task(spider_task(), name=f"spider_task_{i}")


if __name__ == "__main__":
    uvicorn.run(app, port=1111)
