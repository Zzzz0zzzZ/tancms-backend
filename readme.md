# 多平台舆情监控与分析系统

* spiders下放各自的爬虫，最好可以支持下列调用形式：

```python
def craw_weibo(search_param: str, search_size: int, cookie: str) -> None:
def craw_douyin(search_param: str, search_size: int, cookie: str) -> None:
def craw_xhs(search_param: str, search_size: int, cookie: str) -> None:
def craw_bilibili(search_param: str, search_size: int, cookie: str) -> None:
```

