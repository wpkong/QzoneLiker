# -*- coding: utf-8 -*-

import json
import time
from qzone_liker import QzoneLiker
from models import LikerConfig

class Starter(object):

    def get_config(self):
        config = LikerConfig.objects.all()
        for i in config:
            yield (i.qq,i.cookie)

    def start(self):
        for con in self.get_config():
            qq = con[0]
            cookie = con[1]
            liker = QzoneLiker(cookie,qq)
            liker.run()
