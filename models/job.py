# coding=utf-8
# @Time : 2023/4/30 6:13 PM
# @Author : 王思哲
# @File : job.py
# @Software: PyCharm
from tortoise.models import Model
from tortoise import fields


class Job(Model):
    job_id = fields.CharField(max_length=255, unique=True, pk=True)
    search_param = fields.CharField(max_length=255)
    search_platform = fields.CharField(max_length=255)
    search_size = fields.IntField(default=0)
    create_time = fields.DatetimeField(auto_now_add=True)
    status = fields.IntField(default=0)

    class Meta:
        table = "jobs"
