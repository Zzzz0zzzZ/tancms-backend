import asyncio
import json
import os
import queue
import uvicorn
from fastapi import FastAPI
from starlette.middleware.cors import CORSMiddleware
from tortoise.contrib.fastapi import register_tortoise
from routers.comment import router as comment_router
from routers.job import router as job_router
from utils.globalq import tasks_queue
from utils.logger import log

NUM_WORKERS = 3     # 爬虫工作协程

with open("./configs/config.txt", "r") as f:
    config = json.loads(f.read())

app = FastAPI()

# 处理跨域
# 配置允许域名
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
]

# 处理跨域
# 配置允许域名列表、允许方法、请求头、cookie等
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(job_router, prefix="/jobs")
app.include_router(comment_router, prefix="/comments")

# 注册数据库连接
register_tortoise(
    app,
    db_url=config["db_url"],
    modules={"models": ["models.job", "models.comment"]},
    # generate_schemas=True
)


# 处理消息队列爬虫
async def spider_task():
    task_name = asyncio.current_task().get_name()
    log(f"{task_name} is waiting for task...")
    while True:
        try:
            job = tasks_queue.get_nowait()

            # TODO: 根据search_platform调用爬虫
            if job['search_platform'] == 'xhs':
                os.system(f"nohup python3 ./scripts/xhs_.py '{job['job_id']}' '{job['search_param']}' '{job['search_size']}' '{job['cookie']}' >> ./logs/tancms_sys_log.out 2>&1 &")
            elif job['search_platform'] == 'weibo':
                os.system(f"nohup python3 ./scripts/weibo.py '{job['job_id']}' '{job['search_param']}' '{job['search_size']}' '{job['cookie']}' >> ./logs/tancms_sys_log.out 2>&1 &")
            elif job['search_platform'] == 'douyin':
                os.system(f"nohup python3 ./scripts/douyin.py '{job['job_id']}' '{job['search_param']}' '{job['search_size']}' '{job['cookie']}' >> ./logs/tancms_sys_log.out 2>&1 &")
            log(f"JOBS:    queue_size {tasks_queue.qsize()}| job {job}| WORKER {task_name}  already submitted!")

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
    # local
    uvicorn.run(app, port=1111, log_config="./configs/uvicorn_config.json", debug=True)
    # online
    # uvicorn.run(app, host='0.0.0.0', port=7957, log_config="./configs/uvicorn_config.json", debug=True)
