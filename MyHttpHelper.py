from urllib import request
import socket
import json
import gzip

class MyHttpHelper(object):
    def __init__(self):
        socket.setdefaulttimeout(3)#设置超时
        
    #HTTP GET
    def get(url,headers='',gzip=False):
        args=[url]
        if len(headers)>0:
            args.append(headers)
        try:
            req=request.Request(*args)
            res=request.urlopen(req)
            bRes=res.read()
            res.close() #关闭
            
            tRes=''
            if gzip:
                tRes=gzip.decompress(bRes).decode("utf-8")
            else:
                tRes=bRes.decode('utf-8')
            json_data=json.loads(tRes)
            return json_data
        except Exception as e:
            print('请求超时->msg:%s,url:%s'%(e,url))
            return {}


