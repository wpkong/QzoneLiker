# -*- coding:utf-8 -*-
import requests
import re
import execjs
import json
import datetime
from models import AlreadyLiked


class QzoneLiker(object):

    def __init__(self,cookie,qq):
        self.cookie = cookie
        self.qq = qq

        self.headers = {
            'cookie': self.cookie,
            'origin':'https://h5.qzone.qq.com',
            'referer':'https://h5.qzone.qq.com/mqzone/index',
            'user-agent':'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_12_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/57.0.2987.133 Safari/537.36',
            'x-requested-with':'XMLHttpRequest',
            'content-type':'application/x-www-form-urlencoded',
        }

    def _get_page(self):
        response = requests.get('https://h5.qzone.qq.com/mqzone/index', headers = self.headers)
        self._document = response.text.encode('utf-8')

    def _get_qzonetoken(self):
        pattern = re.compile(r'window.shine0callback = \(function\(\){ try{return (.*?);', re.S)
        encrypt = pattern.findall(self._document)[0]
        ctx = execjs.compile(
            '''function qzonetoken(){ location = 'https://h5.qzone.qq.com/mqzone/index'; return %s}''' % (encrypt))
        self.qzonetoken = ctx.call("qzonetoken")

    def _get_p_sk(self):
        pattern = re.compile(r'p_skey=(.*?);', re.S)
        self.p_skey = pattern.findall(self.cookie)[0]

    def _get_g_tk(self):
        ctx = execjs.compile(
            '''function getGTK(){
                    var str = '%s';
                    var hash = 5381;
                    for(var i = 0, len = str.length; i < len; ++i){
                        hash += (hash << 5) + str.charAt(i).charCodeAt();
                    }
                    return hash & 0x7fffffff;
                }''' % self.p_skey)
        self.g_tk = ctx.call("getGTK")

    def _get_speak_speak(self):
        pattern = re.compile(r'var FrontPage = (.*?);</script>', re.S)
        data = pattern.findall(self._document)[0].decode('utf-8')
        ctx = execjs.compile(
            '''function getJsonData(){
                    return JSON.stringify(%s.data);
                }
            ''' % data)

        for speak_speak in json.loads(ctx.call('getJsonData'))['data']['vFeeds']:
            comm = speak_speak.get('comm')
            data = (comm.get('orglikekey', ''), comm.get('curlikekey', ''), comm.get('appid', None),)
            yield data

    def _like(self):
        like_url = 'https://h5.qzone.qq.com/proxy/domain/w.qzone.qq.com/cgi-bin/likes/internal_dolike_app?zonetoken=%s&g_tk=%s' % (self.qzonetoken, self.g_tk)
        post_data = {
            'opuin':self.qq,
            'opr_type':'like',
            'format':'purejson',
            'unikey':'',
            'curkey':'',
            'appid':''
        }

        for speak in self._get_speak_speak():
            for like in AlreadyLiked.objects.all():
                if like.mood_id == speak[1]:
                    continue

            post_data['unikey'] = speak[0]
            post_data['curkey'] = speak[1]
            post_data['appid'] = speak[2]
            response = requests.post(like_url,headers=self.headers,data=post_data)
            like = AlreadyLiked.objects.create(mood_id=speak[1],time=datetime.datetime.now())
            like.save()
            response = json.loads(response.text)
            if response['ret'] == 0:
                print '[%s]like %s' % (like.time,like.mood_id)
            else:
                print 'error: [%s]like %s' % (like.time,like.mood_id)

    def run(self):
        self._get_page()
        self._get_p_sk()
        self._get_g_tk()
        self._get_qzonetoken()
        self._like()
