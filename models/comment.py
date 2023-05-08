# coding=utf-8
# @Time : 2023/5/8 2:03 PM
# @Author : 王思哲
# @File : comment.py
# @Software: PyCharm
from tortoise.models import Model
from tortoise import fields


class Comment(Model):
    id = fields.IntField(pk=True)
    job = fields.ForeignKeyField('models.Job', related_name='comments')
    platform = fields.CharField(max_length=255)
    topic = fields.CharField(max_length=255, null=True)
    user_photo = fields.CharField(max_length=255, null=True)
    user_name = fields.CharField(max_length=255, null=True)
    comment = fields.CharField(max_length=1000)
    create_time = fields.CharField(max_length=255, null=True)
    like_count = fields.IntField(null=True)
    retransmission_count = fields.IntField(null=True)

    class Meta:
        table = "comments"