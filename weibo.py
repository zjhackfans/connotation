from urllib import request,parse,error
from mysql_helper import MySQLCommand
from MyHttpHelper import MyHttpHelper
from datetime import datetime,timedelta, timezone
import http.cookiejar
import re
import json
import os
import time
import gzip
import random
import socket

class weibo(object):
    def __init__(self):
         #微博
        self.url_video='http://m.weibo.cn/container/getIndex?retcode=6102&containerid=1076031794308181'
        self.url_niuzai='http://m.weibo.cn/container/getIndex?retcode=6102&containerid=1076035460816214'
        self.url_yj='http://m.weibo.cn/container/getIndex?retcode=6102&containerid=1076032006913442'
        self.url_mine='http://m.weibo.cn/container/getIndex?retcode=6102&containerid=1076032939193095'
        self.url_yj_uinfo='http://m.weibo.cn/container/getIndex?retcode=6102&type=uid&value=2006913442&containerid=1005052006913442'
        #用户信息

        socket.setdefaulttimeout(3)
        self.url_follows='http://m.weibo.cn/container/getSecond?containerid=%s_-_FOLLOWERS&retcode=6102'
        self.url_user_more_info='http://m.weibo.cn/container/getIndex?containerid=%s_-_INFO&retcode=6102'
    ######output######
    #0.00%
    #0.07%
    #0.13%
    #0.20%
    #....
    #99.94%
    #100.00%
    def Schedule(self,a,b,c):
        '''''
        a:已经下载的数据块
        b:数据块的大小
        c:远程文件的大小
       '''
        per = 100.0 * a * b / c
        if per > 100 :
            per = 100
        print('%.2f%%' % per)

    def download_file(self,download_url,save_path):
        print('开始下载...')
        request.urlretrieve(download_url,save_path,self.Schedule)
        print('下载完成！3s后开始继续下载...')

    #下载保存视频文件
    def save_mp4_file(self,page,folderName,mp4_list):
        
        #编译正则，获取视频名称
        re_mp4_name=re.compile(r'\w+\.mp4')

        for mp4Url in mp4_list:
            mp4Url=mp4Url.replace('\\','')

            #视频名称
            mp4_name=re_mp4_name.search(mp4Url).group()

            #目录不存在则创建
            save_folder=r'D:\python3\dowload'+'\\'+folderName
            if not os.path.exists(save_folder):
                os.mkdir(save_folder)
            
            #保存的本地文件路径
            save_path = os.path.join(save_folder,mp4_name)

            #如果存在，继续下一个循环
            if os.path.exists(save_path):
                print('文件已存在->',save_path)
                continue

            print('开始下载...')
            request.urlretrieve(mp4Url,save_path,Schedule)
            print('下载完成！3s后开始继续下载...')
            time.sleep(3)

        #保存下载信息
        with open(save_folder+'\\'+'mp4.info','a') as f:
            f.write('视频->第%s页共%s条下载完成！\n'% (page,len(mp4_list)))

    #保存文本文件
    def save_text_file(self,folderName,text):
        #目录不存在则创建
        save_folder=r'D:\python3\dowload'+'\\'+folderName
        if not os.path.exists(save_folder):
            os.mkdir(save_folder)
            
        #保存的本地文件路径
        save_path = os.path.join(save_folder,folderName+'.txt')

        with open(save_path,'a',encoding='utf-8') as f:
            f.write(text)

        

    #下载保存文件
    def save_pic_file(self,folderName,pic_list):

        header = {
            "User-Agent":"Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25"
        }

        #编译正则，获取图片名称
        re_pic_name=re.compile(r'(\w+.jpg)')
        
        for pic_url in pic_list:
            pic_url=pic_url.replace('\\','')
           
            #文件名
            pic_name='default.jpg'
            try:
                pic_name=re_pic_name.search(pic_url).group(1)
            except Exception as e:
                print('获取图片名称出错！')
                continue

            #目录不存在则创建
            save_folder=r'D:\python3\dowload'+'\\'+folderName
            if not os.path.exists(save_folder):
                os.mkdir(save_folder)

            #保存的本地文件路径
            save_path = os.path.join(save_folder,pic_name)

            #如果存在，继续下一个循环
            if os.path.exists(save_path):
                print('文件已存在->',save_path)
                continue

            #写入文件
            print('打开网络文件->',pic_url)
            req=request.Request(pic_url,headers=header)
            with request.urlopen(req) as f:
                io_local=None
                print('保存为本地文件->',save_path)
                try :
                    io_local=open(save_path,'wb')
                    io_local.write(f.read())
                    io_local.close()
                except Exception as e:
                    #///
                    print('保存失败!')
                finally :
                    if io_local:
                        io_local.close()


    def get_weibo_data(self,url):
        
        header = {
            
            "User-Agent":"Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25"
        }
        
        
        #req.add_header("User-Agent","Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25")

        print('opening...')

        #编译
        re_pic=re.compile(r'http:[\w\./\\]+\.jpg')
        #文本
        re_text=re.compile(r'"text":"(.*?)","')

        re_mp4=re.compile(r'(http:[\w\./\\]*?\.mp4.*?)"}')
        
        page=8 #第5页已完成
        index=0
        while True:
            page+=1
            search_url=url+'%s'% ('&page=%s'% page)

            req=request.Request(search_url,headers=header)
        
            with request.urlopen(req) as f:
                data=f.read().decode(encoding="utf-8", errors="ignore")
                ############视频Start##################
                mp4_list=re_mp4.findall(data)
                mp4_count=len(mp4_list)
                if mp4_count==0:
                    print('爬取视频完成！')
                    break
                print('第%s页共有%s个视频，准备保存到本地...'% (page,mp4_count))

                #保存视频文件
                save_mp4_file(page,'上品性感美女会所',mp4_list)

                
                
                ############视频End##################


                ############文字Start##################
    ##            text_list=re_text.findall(data)
    ##            text_count=len(text_list)
    ##            if text_count==0:
    ##                print('爬取文字结束!')
    ##                break
    ##            
    ##            print('第%s页共有%s条微博，准备保存到本地...'% (page,text_count))
    ##
    ##            text_total_list=[]
    ##            for txt in text_list:
    ##                index+=1
    ##                if '\\u' in txt:
    ##                    txt=txt.encode('utf-8').decode('unicode_escape')+'\n\n'
    ##
    ##                text_total_list.append('%s -> %s' %(index,txt))  
    ##                #print(index,'->',txt)
    ##
    ##            #保存文本
    ##            save_text_file('tulips13',''.join(text_total_list))

                ############文字End##################

                
                #############图片Start############
    ##            pic_list=re_pic.findall(data)
    ##            
    ##            pic_count=len(pic_list)
    ##            if pic_count==0:
    ##                print('爬取图片结束！')
    ##                break
    ##
    ##            print('第%s页共有%s张图片，准备保存到本地...'% (page,pic_count))
    ##
    ##            #保存文件
    ##            save_pic_file('tulips13',set(pic_list))
                ###############图片Een###############


                

                
            #线程延迟3s
            print('已完成，等待进入下一循环...')
            time.sleep(10)



    ##        json_data=json.loads(data)
    ##                
    ##        #json_data:dict
    ##        #json_data['cards']:list
    ##        #json_data['cards'][0]:dict
    ##        #scheme:微博详细
    ##        #card_type
    ##        #show_type
    ##        #mblog:微博主体 dict
    ##        #itemid
    ##
    ##        #mblog->dict
    ##        #text:微博的文字说明
    ##        #pics:图片列表 list  thumbnail，bmiddle，large
    ##        #retweeted_status:来自转发微博
    ##        #comments_count:评论数量
    ##        #isLongText
    ##        #visible:dict
    ##        #picStatus
    ##        #source
    ##        #attitudes_count:点赞数
    ##        #textLength
    ##        #id
    ##        #favorited
    ##        #thumbnail_pic
    ##        #bmiddle_pic
    ##        #created_at
    ##        #bid
    ##        #user
    ##
    ##
    ##        #pics->
    ##        #geo
    ##        #large:geo,url,size
    ##        #url
    ##        
    ##        mblog=json_data['cards'][6]['mblog']
    ##        
    ##        for key in mblog:
    ##            if key=='pics':
    ##                uName=mblog['user']['screen_name']
    ##                #return None
    ##                for item in mblog['pics']:
    ##                    pic_url=item['large']['url']
    ##                    pic_name=re.search(r'(\w+.jpg)',pic_url).group(1)
    ##
    ##                    #目录不存在则创建
    ##                    save_folder=r'D:\python3\dowload'+'\\'+uName
    ##                    if not os.path.exists(save_folder):
    ##                        os.mkdir(save_folder)
    ##
    ##                    #保存的本地文件路径
    ##                    save_path = os.path.join(save_folder,pic_name)
    ##                    
    ##                    print('打开网络文件->',pic_url)
    ##                    req=request.Request(pic_url,headers=header)
    ##                    with request.urlopen(req) as f:
    ##                        io_local=None
    ##                        print('保存为本地文件->',save_path)
    ##                        try :
    ##                            io_local=open(save_path,'wb')
    ##                            io_local.write(f.read())
    ##                            io_local.close()
    ##                        except Exception as e:
    ##                            #///
    ##                            print('Err!')
    ##                        finally :
    ##                            if io_local:
    ##                                io_local.close()
                        
   
    #get_weibo_data(url_video)

    #发布
    def blog_add(self,text=''):
        if text=='':
                text='测试内容->'
                length_msg=32
                while length_msg>0:
                    length_msg-=1
                    text+=chr(random.randint(0x4E00, 0x9FBF))
        url='http://m.weibo.cn/mblogDeal/addAMblog?retcode=6102'
        cookie='_T_WM=191b6a6a816cd555c3fad6d414411831; SCF=AiVYQPlnKcnAe9PhpNdNNR0e2XYyXVmjPTOfBdCUX8El-0p8tFEVWE8nnx2rh-L2ZkqERG9Rkq8paS3bxdaLPN8.; SUB=_2A251lYH9DeRxGeRH6FsQ-S3MwjmIHXVXeS-1rDV6PUJbkdBeLXTikW2g-hdZKvfRAy4JF4Msa4OTDPM1og..; SUHB=02M_QwIlXI7rV9; SSOLoginState=1485959597; H5_INDEX=3; H5_INDEX_TITLE=Never_%E5%81%A5; WEIBOCN_WM=5091_0026; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D1076031771925961%26fid%3D1076031771925961%26uicode%3D10000011'
        header={
            'Host':'m.weibo.cn'
            ,'Connection':'keep-Alive'
            ,'Accept':'application/json, text/javascript, */*; q=0.01'
            ,'origin':'http://m.weibo.cn'
            ,'X-Requested-With':'X-Requested-With: XMLHttpRequest'
            ,'User-Agent':'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.85 Mobile Safari/537.36 XiaoMi/MiuiBrowser/8.2.15'
            ,'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8'
            ,'Referer':'http://m.weibo.cn/mblog'
            ,'Accept-Encoding':'gzip,deflate'
            ,'Cookie':cookie
            }
        post_data={
            'content':text
            ,'annotations':''
            ,'st':'d08345'
            }
        post_data=parse.urlencode(post_data).encode('utf-8')

        req=request.Request(url,data=post_data,headers=header)
        res= request.urlopen(req)
        bRes=res.read()
        res.close()
        tRest=gzip.decompress(bRes).decode("utf-8")
        print(tRest)

    #点赞
    def blog_like(self,blog_ids):
       
        url='http://m.weibo.cn/attitudesDeal/add'
        cookie='_T_WM=191b6a6a816cd555c3fad6d414411831; SCF=AiVYQPlnKcnAe9PhpNdNNR0e2XYyXVmjPTOfBdCUX8El-0p8tFEVWE8nnx2rh-L2ZkqERG9Rkq8paS3bxdaLPN8.; SUB=_2A251lYH9DeRxGeRH6FsQ-S3MwjmIHXVXeS-1rDV6PUJbkdBeLXTikW2g-hdZKvfRAy4JF4Msa4OTDPM1og..; SUHB=02M_QwIlXI7rV9; SSOLoginState=1485959597; H5_INDEX=3; H5_INDEX_TITLE=Never_%E5%81%A5; WEIBOCN_WM=5091_0026; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D1076031771925961%26fid%3D1076031771925961%26uicode%3D10000011'
        header={
            'Host':'m.weibo.cn'
            ,'Connection':'keep-Alive'
            ,'Accept':'application/json, text/plain, */*'
            ,'origin':'http://m.weibo.cn'
            ,'X-Requested-With':'X-Requested-With: XMLHttpRequest'
            ,'User-Agent':'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.85 Mobile Safari/537.36 XiaoMi/MiuiBrowser/8.2.15'
            ,'Content-Type':'application/x-www-form-urlencoded'
            ,'Referer':'http://m.weibo.cn/?wm=5091_0026'
            ,'Accept-Encoding':'gzip,deflate'
            ,'Cookie':cookie
            }
        if not type(blog_ids) == list:
            blog_ids=[blog_ids]

        err_num=0 #记录失败次数，达到2次进行下一循环
        while len(blog_ids)>0:
            blog_id=blog_ids.pop()
            
            print('%s->ready 30s to update...'%blog_id)
            time.sleep(10)#update weibo too fast!
            print('%s->start to update.'%blog_id)
            post_data={
                'id':blog_id
                ,'attitude':'heart'
                ,'st':'d08345'
                }
            post_data=parse.urlencode(post_data).encode('utf-8')
            req=request.Request(url,data=post_data,headers=header)
            res= request.urlopen(req)
            bRes=res.read()
            res.close()
            tRest=gzip.decompress(bRes).decode("utf-8")
            
            json_res=json.loads(tRest)
            if not json_res['ok']=='1':
                err_num+=1
                if err_num<=2:
                    #点赞不成功，将id重新添加回列表
                    blog_ids.append(blog_id)
                else:
                    err_num=0
                    
                print('%s->点赞失败'%blog_id)
                
            print(tRest)


    #评论
    def blog_comment(self,blog_id,content):
       
        url='http://m.weibo.cn/commentDeal/addCmt'
        cookie='_T_WM=191b6a6a816cd555c3fad6d414411831; SCF=AiVYQPlnKcnAe9PhpNdNNR0e2XYyXVmjPTOfBdCUX8El-0p8tFEVWE8nnx2rh-L2ZkqERG9Rkq8paS3bxdaLPN8.; SUB=_2A251lYH9DeRxGeRH6FsQ-S3MwjmIHXVXeS-1rDV6PUJbkdBeLXTikW2g-hdZKvfRAy4JF4Msa4OTDPM1og..; SUHB=02M_QwIlXI7rV9; SSOLoginState=1485959597; H5_INDEX=3; H5_INDEX_TITLE=Never_%E5%81%A5; WEIBOCN_WM=5091_0026; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D1076031771925961%26fid%3D1076031771925961%26uicode%3D10000011'
        header={
            'Host':'m.weibo.cn'
            ,'Connection':'keep-Alive'
            ,'Accept':'application/json, text/plain, */*'
            ,'origin':'http://m.weibo.cn'
            ,'X-Requested-With':'X-Requested-With: XMLHttpRequest'
            ,'User-Agent':'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.85 Mobile Safari/537.36 XiaoMi/MiuiBrowser/8.2.15'
            ,'Content-Type':'application/x-www-form-urlencoded'
            ,'Referer':'http://m.weibo.cn/comment'
            ,'Accept-Encoding':'gzip,deflate'
            ,'Cookie':cookie
            }
        post_data={
            'content':content
            ,'id':blog_id
            ,'st':'d08345'
            }
        post_data=parse.urlencode(post_data).encode('utf-8')

        req=request.Request(url,data=post_data,headers=header)
        res= request.urlopen(req)
        bRes=res.read()
        res.close()
        tRest=gzip.decompress(bRes).decode("utf-8")
        print(tRest)

    def get_blog_ids(self,url,page):
        
        header = {
            
            "User-Agent":"Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25"
        }
        
        
        #req.add_header("User-Agent","Mozilla/6.0 (iPhone; CPU iPhone OS 8_0 like Mac OS X) AppleWebKit/536.26 (KHTML, like Gecko) Version/8.0 Mobile/10A5376e Safari/8536.25")

        print('opening...')

        #编译
        re_id=re.compile(r'"mblog".*?"id"[^\d]*(\d+)')
        page-=1
        index=0
        while True:
            time.sleep(1)
            page+=1
            search_url=url+'%s'% ('&page=%s'% page)

            req=request.Request(search_url,headers=header)
        
            with request.urlopen(req) as f:
                data=f.read().decode(encoding="utf-8", errors="ignore")
                
                id_list=re_id.findall(data)
                ids_count=len(id_list)
                if ids_count==0:
                    print('爬取用户id完成！')
                    blog_chat('2006913442','yj,我把你全部微博都赞了一遍，惊不惊喜，意不意外 ｡◕‿◕｡')
                    break
                print('第%s页共有%s个id，准备点赞...'% (page,ids_count))
                return id_list
                #blog_like(id_list)
                #print(id_list)

    #获取消息
    def get_chat_msg(self):
        url='http://m.weibo.cn/msg/messages?uid=5175429989&page=1&retcode=6102'
        cookie='_T_WM=191b6a6a816cd555c3fad6d414411831; SCF=AiVYQPlnKcnAe9PhpNdNNR0e2XYyXVmjPTOfBdCUX8El-0p8tFEVWE8nnx2rh-L2ZkqERG9Rkq8paS3bxdaLPN8.; SUB=_2A251lYH9DeRxGeRH6FsQ-S3MwjmIHXVXeS-1rDV6PUJbkdBeLXTikW2g-hdZKvfRAy4JF4Msa4OTDPM1og..; SUHB=02M_QwIlXI7rV9; WEIBOCN_WM=5091_0026; H5_INDEX=1; H5_INDEX_TITLE=Never_%E5%81%A5; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D102803'
        header={
            'Host':'m.weibo.cn'
            ,'Connection':'keep-Alive'
            ,'Accept':'application/json, text/plain, */*'
            ,'origin':'http://m.weibo.cn'
            ,'X-Requested-With':'X-Requested-With: XMLHttpRequest'
            ,'User-Agent':'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.85 Mobile Safari/537.36 XiaoMi/MiuiBrowser/8.2.15'
            ,'Content-Type':'application/x-www-form-urlencoded'
            ,'Referer':'http://m.weibo.cn/msg/chat'
            ,'Accept-Encoding':'gzip,deflate'
            ,'Cookie':cookie
            }


        req=request.Request(url,headers=header)
        res= request.urlopen(req)
        bRes=res.read()
        res.close()
        tRest=gzip.decompress(bRes).decode("utf-8")
        print(tRest)

    
    #聊天
    def blog_chat(self,uid=5175429989,msg='哈喽~！',cmd=0):
       
        #http://m.weibo.cn/msg/chat
        url='http://m.weibo.cn/msgDeal/sendMsg'
        #cookie='_T_WM=191b6a6a816cd555c3fad6d414411831; SCF=AiVYQPlnKcnAe9PhpNdNNR0e2XYyXVmjPTOfBdCUX8El-0p8tFEVWE8nnx2rh-L2ZkqERG9Rkq8paS3bxdaLPN8.; SUB=_2A251lYH9DeRxGeRH6FsQ-S3MwjmIHXVXeS-1rDV6PUJbkdBeLXTikW2g-hdZKvfRAy4JF4Msa4OTDPM1og..; SUHB=02M_QwIlXI7rV9; SSOLoginState=1485959597; H5_INDEX=3; H5_INDEX_TITLE=Never_%E5%81%A5; WEIBOCN_WM=5091_0026; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D1076031771925961%26fid%3D1076031771925961%26uicode%3D10000011'
        cookie='_T_WM=191b6a6a816cd555c3fad6d414411831; SCF=AiVYQPlnKcnAe9PhpNdNNR0e2XYyXVmjPTOfBdCUX8El-0p8tFEVWE8nnx2rh-L2ZkqERG9Rkq8paS3bxdaLPN8.; SUB=_2A251lYH9DeRxGeRH6FsQ-S3MwjmIHXVXeS-1rDV6PUJbkdBeLXTikW2g-hdZKvfRAy4JF4Msa4OTDPM1og..; SUHB=02M_QwIlXI7rV9; WEIBOCN_WM=5091_0026; H5_INDEX=1; H5_INDEX_TITLE=Never_%E5%81%A5; M_WEIBOCN_PARAMS=luicode%3D10000011%26lfid%3D102803'
        header={
            'Host':'m.weibo.cn'
            ,'Connection':'keep-Alive'
            ,'Accept':'application/json, text/plain, */*'
            ,'origin':'http://m.weibo.cn'
            ,'X-Requested-With':'X-Requested-With: XMLHttpRequest'
            ,'User-Agent':'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.85 Mobile Safari/537.36 XiaoMi/MiuiBrowser/8.2.15'
            ,'Content-Type':'application/x-www-form-urlencoded'
            ,'Referer':'http://m.weibo.cn/msg/chat'
            ,'Accept-Encoding':'gzip,deflate'
            ,'Cookie':cookie
            }
        
        while True:
            if cmd==1:
                msg=input('To %s->'%uid)
                if msg=='$quit':
                    break
            post_data={
                'filedId':'null'
                ,'uid':uid
                #,'content':msg+'\r\n-----------------本条消息From[自动推送]'
                ,'content':msg
                ,'st':'e055b2'
                }
            print(post_data)
            post_data=parse.urlencode(post_data).encode('utf-8')

            req=request.Request(url,data=post_data,headers=header)
            res= request.urlopen(req)
            bRes=res.read()
            res.close()
            tRest=gzip.decompress(bRes).decode("utf-8")
            print(tRest)

            if cmd==0:
                break


    
    #获取用户ID
    def get_user_ids(self,topic_id=4072216884945355,page=1):
        url='http://m.weibo.cn/api/comments/show?id=%s&page=%s&retcode=6102'%(topic_id,page)
        headers = { 
            'User-Agent':'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.85 Mobile Safari/537.36 XiaoMi/MiuiBrowser/8.2.15'
        }
        req=request.Request(url,headers=headers)
        res= request.urlopen(req)
        bRes=res.read()
        res.close()
        #tRest=gzip.decompress(bRes).decode("utf-8")
        tRest=bRes.decode("utf-8")
        json_res=json.loads(tRest)
        if len(json_res)>0 and json_res['ok']==1: 
            return json_res['data']
        else:
            return []

    #获取用户
    def get_user(self,user_id):
        url='http://m.weibo.cn/container/getIndex?retcode=6102&type=uid&type=uid&value=%s'%user_id
        
        headers={
            'Host':'m.weibo.cn'
            ,'Connection':'keep-Alive'
            ,'Accept':'application/json, text/plain, */*'
            ,'X-Requested-With':'X-Requested-With: XMLHttpRequest'
            ,'User-Agent':'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.85 Mobile Safari/537.36 XiaoMi/MiuiBrowser/8.2.15'
            ,'Referer':'http://m.weibo.cn/p/'
            ,'Accept-Encoding':'gzip,deflate'
            }
        req=request.Request(url,headers=headers)
        res= request.urlopen(req)
        bRes=res.read()
        res.close()
        tRest=gzip.decompress(bRes).decode("utf-8")
        json_res=json.loads(tRest)
        return json_res
        #print(json_res['userInfo'])
        #save_user_info(json_res)

    #获取用户详细信息
    def get_user_detail(self,user_id):
        headers = {
            'Host':'m.weibo.cn'
            ,'Connection':'keep-Alive'
            ,'Accept':'application/json, text/plain, */*'
            ,'X-Requested-With':'X-Requested-With: XMLHttpRequest'
            ,'User-Agent':'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.85 Mobile Safari/537.36 XiaoMi/MiuiBrowser/8.2.15'
            ,'Referer':'http://m.weibo.cn/p/'
            ,'Accept-Encoding':'gzip,deflate'
            #'User-Agent':'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.85 Mobile Safari/537.36 XiaoMi/MiuiBrowser/8.2.15'
            ,'Cookie':'_T_WM=191b6a6a816cd555c3fad6d414411831; SCF=AiVYQPlnKcnAe9PhpNdNNR0e2XYyXVmjPTOfBdCUX8El-0p8tFEVWE8nnx2rh-L2ZkqERG9Rkq8paS3bxdaLPN8.; SUB=_2A251lYH9DeRxGeRH6FsQ-S3MwjmIHXVXeS-1rDV6PUJbkdBeLXTikW2g-hdZKvfRAy4JF4Msa4OTDPM1og..; SUHB=02M_QwIlXI7rV9; SSOLoginState=1485959597; WEIBOCN_WM=5091_0026; H5_INDEX=3; H5_INDEX_TITLE=Never_%E5%81%A5; APP_TIPS_HIDE=1; M_WEIBOCN_PARAMS=ext%3Dgrowth%253A1%257Cbuid%253A1803234654%257Cterminal%253A%257Creason%253A3.0%257Cact%253Askip%257Cuid%253A2939193095%257Cfollow%253A5097174964%257Cskiptype%253Aprofile%257Cagain%253A%26luicode%3D10000011%26lfid%3D2302831815418641%26fid%3D2302831815418641_-_INFO%26uicode%3D10000011'
        }
        url=self.url_user_more_info % user_id
        req=request.Request(url,headers=headers)
        res= request.urlopen(req)
        bRes=res.read()
        res.close()
        #tRest=gzip.decompress(bRes).decode("utf-8")
        tRest=bRes.decode("utf-8")
        #re_match=re.search('"\u6807\u7b7e"[\S\s]+?:\s+"(.*?)"[\s\S]+"所在地"[\S\s]+?:\s+"(.*?)"[\s\S]+?"等级"[\S\s]+"LV\s+(\d+?)"[\s\S]+"注册时间"[\S\s]+?:\s+"(.*?)"',tRest)
        re_match=re.search('"\u6807\u7b7e',tRest)        
        print(re_match)
    #保存用户信息
    def save_user_info(self,info_list):
        cmd=MySQLCommand(db='weibo')
        cmd.connectMysql()

    
        fileds_user='''id ,screen_name,profile_image_url,statuses_count,verified,verified_type,verified_type_ext
                    ,verified_reason,description,gender,followers_count ,follow_count ,cover_image_phone'''
        
        for info in info_list:
            
            user_info=info['user']
            verified_type_ext='0'
           
            description=''

            try:
                description=user_info['description']
            except Exception as e:
                print('description->出错！')
                
            values_user=(
                        user_info['id']
                        ,user_info['screen_name']
                        ,user_info['profile_image_url']
                        ,user_info['statuses_count']
                        ,user_info['verified']
                        ,user_info['verified_type']
                        ,verified_type_ext
                        ,user_info['verified_reason']
                        ,description
                        ,user_info['gender']
                        ,user_info['followers_count']
                        ,user_info['follow_count']
                        ,user_info['cover_image_phone']
                 
                        )
            if len(values_user)==0:
                print('用户数据为空！')
                continue
            sql_add_user="REPLACE INTO t_user (%s) VALUES %s " %(fileds_user,values_user)

            try:
                res_insert=cmd.insertMysql(sql_add_user)
                if res_insert==1:
                    print('%s->保存成功!'%user_info['screen_name'])
                elif res_insert==2:
                    print('%s->已经存在!'%user_info['screen_name'])
                else :
                    print('%s->保存失败！'%sql_add_user)
            except Exception as e:
                print('插入数据发生错误!->msg:%s'%(e))
                
        print('正在关闭连接...')
        cmd.closeMysql()

    #暂时获取关注用户
    def get_top1_userid(self):
        
        cmd=MySQLCommand(db='weibo')
        cmd.connectMysql()
        sql="select id from (select id from t_user t1 left join t_spider_info t2 on t2.module='follow' and t2.moduleid =t1.id  where t2.ikey is null order by t1.follow_count desc limit 0,1)a"
        #sql='select user_id,followers,followings from t_user order by followers desc limit 0,1'
        try:
            return cmd.queryMysql(sql,1)[0]
        except Exception as e:
            print('发生错误，msg:%s'% e.args[0])
        finally:
            cmd.closeMysql()

    #主程序
    def main(self):

        while True:
            user_id=self.get_top1_userid()
            
            page=0
            orig_url='http://m.weibo.cn/container/getSecond?containerid=100505%s_-_FOLLOWERS&retcode=6102'%user_id
            while True:
                time.sleep(3)
                page+=1

                search_url=orig_url+'&page=%s'%page
                try:
                    
                    follow_list=self.get_folows(search_url)
                   
                    if len(follow_list)==0:
                        print('爬取完成！等待3s进入下个循环元')
                        self.__update_spider_info('follow',user_id,page,10,1)
                        break
                    self.save_user_info(follow_list)
                except Exception as e:
                    continue
                self.__update_spider_info('follow',user_id,page,10,0)
                print('当前第%s页爬取完成！'%page)

    def __update_spider_info(self,module,moduleid,page,size,finished=0):
        cmd=MySQLCommand(db='weibo')
        cmd.connectMysql()
        sql="REPLACE INTO t_spider_info(ikey,module,moduleid,page,size,finished) VALUES('%s','%s',%s,%s,%s,%s)" %('%s_%s'%(module,moduleid),module,moduleid,page,size,finished)
        
        try:
            cmd.insertMysql(sql)
        except Exception as e:
            print('sql发生错误，msg:%s'% e.args[0])
        finally:
            cmd.closeMysql()
        
    #获取关注用户
    def get_folows(self,url,page=1,size=50):
        headers = {
            'Host':'m.weibo.cn'
            ,'Connection':'keep-Alive'
            ,'Accept':'application/json, text/plain, */*'
            ,'X-Requested-With':'X-Requested-With: XMLHttpRequest'
            ,'User-Agent':'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.85 Mobile Safari/537.36 XiaoMi/MiuiBrowser/8.2.15'
            ,'Referer':'http://m.weibo.cn/p/'
            #,'Accept-Encoding':'gzip,deflate'
            #'User-Agent':'Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.85 Mobile Safari/537.36 XiaoMi/MiuiBrowser/8.2.15'
            ,'Cookie':'_T_WM=191b6a6a816cd555c3fad6d414411831; SCF=AiVYQPlnKcnAe9PhpNdNNR0e2XYyXVmjPTOfBdCUX8El-0p8tFEVWE8nnx2rh-L2ZkqERG9Rkq8paS3bxdaLPN8.; SUB=_2A251lYH9DeRxGeRH6FsQ-S3MwjmIHXVXeS-1rDV6PUJbkdBeLXTikW2g-hdZKvfRAy4JF4Msa4OTDPM1og..; SUHB=02M_QwIlXI7rV9; SSOLoginState=1485959597; WEIBOCN_WM=5091_0026; H5_INDEX=3; H5_INDEX_TITLE=Never_%E5%81%A5; APP_TIPS_HIDE=1; M_WEIBOCN_PARAMS=ext%3Dgrowth%253A1%257Cbuid%253A1803234654%257Cterminal%253A%257Creason%253A3.0%257Cact%253Askip%257Cuid%253A2939193095%257Cfollow%253A5097174964%257Cskiptype%253Aprofile%257Cagain%253A%26luicode%3D10000011%26lfid%3D2302831815418641%26fid%3D2302831815418641_-_INFO%26uicode%3D10000011'
        }

     
        bRes=[]
        req=request.Request(url,headers=headers)
        res= request.urlopen(req)
        try:
 
            bRes=res.read()
            res.close()
        except Exception as e:
            print('超时啦~')
            res.close()
            return []
        #tRest=gzip.decompress(bRes).decode("utf-8")
        tRest=bRes.decode("utf-8")
      
        json_res=json.loads(tRest)
        if len(json_res)>0 and json_res['ok']==1: 
            return json_res['cards']
        else:
            return []
    
    def query_user_by_sql(self):
        rows=[]
        sql='select screen_name,profile_id,weibo_id from t_user '
        cmd=MySQLCommand(db='weibo')
        cmd.connectMysql()
        
        try:
            rows=cmd.queryMysql(sql)
        except Exception as e:
            print('Err')
        cmd.closeMysql()

        for row in rows:
            print('name:%s,profile_id:%s,weibo_id:%s'%(row[0],row[1],row[2]))

            
        
wb=weibo()
wb.get_chat_msg()
#while True:
    #wb.blog_chat(msg='思考啥人生')
    #time.sleep(3)
    

