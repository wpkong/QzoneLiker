# -*- coding:utf-8 -*-

from __future__ import unicode_literals

from django.db import models

# Create your models here.

class LikerConfig(models.Model):
    qq = models.CharField(max_length=128)
    cookie = models.CharField(max_length=1024)

class AlreadyLiked(models.Model):
    mood_id = models.CharField(max_length=128)
    time = models.DateTimeField(verbose_name='点赞时间')
