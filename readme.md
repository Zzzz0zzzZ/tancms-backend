# 多平台舆情监控与分析系统

* spiders下放各自的爬虫，最好可以支持下列调用形式：

```python
def craw_weibo(job_id: str, search_param: str, search_size: int, cookie: str) -> None:
def craw_douyin(job_id: str, search_param: str, search_size: int, cookie: str) -> None:
def craw_xhs(job_id: str, search_param: str, search_size: int, cookie: str) -> None:
def craw_bilibili(job_id: str, search_param: str, search_size: int, cookie: str) -> None:
```

* 爬到的数据，插入数据库，使用DBManager：

> 详细用法参照`spiders.xhs.spider.py`和`utils.db_manager.py`，由于爬虫容易被封，建议使用`try except`环绕，且每爬一定的数据就入库。

```python
# 引入
from utils.db_manager import DBManager
import json

# 实例化
with open("./configs/db_manager_config.txt", "r") as f:
	db = json.loads(f.read())
db_manager = DBManager(db)

# 插入: 自定义sql模板, %s的个数 与 需要插入的字段个数 对应; 
# 	   data_list格式：[[], [], []] 里面为每一条需要插入的数据，这么做可以批量插入，加快速度。
sql = '''
        INSERT INTO comments(
            job_id, platform, topic, user_photo, user_name, comment, create_time, like_count
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    '''
db_manager.insert(sql=sql, data_list=comments_list)

# 所有插入工作完成，更新任务状态
db_manager.finish(job_id=job_id)
```

