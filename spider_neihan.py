from urllib import request,parse
from mysql_helper import MySQLCommand
from datetime import datetime
import os
import re
import time
import json
import socket
import gzip
import random
class ConnotationSpider(object):
    
    
    
    def __init__(self):
        self.user_id=3188361577
        self.spider_page=1
        self.spider_size=50
        
        socket.setdefaulttimeout(3)#设置超时
        print('初始化完成...')

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

    #下载保存视频文件
    def __save_mp4_file(self,mp4_list):

        host='http://ic.snssdk.com/neihan/video/playback/?video_id='

        for mp4_name in mp4_list:
            mp4Url=host+mp4_name

            #保存的本地文件路径
            save_path = os.path.join(self.spider_path,mp4_name)+'.mp4'

            #如果存在，继续下一个循环
            if os.path.exists(save_path):
                print('文件已存在->',save_path)
                continue
            
            print('开始下载...')
            request.urlretrieve(mp4Url,save_path,self.Schedule)
            print('下载完成！3s后开始继续下载...')
            time.sleep(3)

       
            

    #下载保存图片文件
    def __save_pic_file(self,pic_list):

        host='http://pb3.pstatp.com/large'
        
        #编译正则，获取图片名称
        #re_pic_name=re.compile('large/(\w+)')
        
        for dic_pic in pic_list:
            pic_name=dic_pic[0] #文件名
            ext_name='.jpg' #拓展名
            is_gif=dic_pic[1]
            if is_gif=='1':
                ext_name='.gif'
            pic_url=host+'/'+pic_name

            #保存的本地文件路径
            save_path = os.path.join(self.spider_path,pic_name)+ext_name

            
            #如果存在，继续下一个循环
            if os.path.exists(save_path):
                print('文件已存在->',save_path)
                continue
           
            
            #写入文件
            print('打开网络文件->',pic_url)
            req=request.Request(pic_url)
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

        

    #获取用户作品
    def get_user_topics(self,spider_type,spider_name):     

        url_source='http://lf.snssdk.com/2/essay/zone/user/posts/?mpic=1&webp=1&essence=1&user_id=%s&count=30'%self.user_id
        url=url_source
        
        #re_large_pic=re.compile(r'"large/(\w+)')
        re_large_pic=re.compile(r'"large/(\w+)[\s\S]+?is_gif[^\d\w]+(\d|\w+)')
        re_orig_vedio=re.compile(r'origin/(\w+)')
        re_text=re.compile(r'"text"[\s\S]+?"(.*?)"[\s\S]+?"id"[\s\S]+?"(.*?)"')
        
        #通用时间戳
        re_timestamp=re.compile(r'create_time[^\d]*(\d+)')
        timestamp=0

        while True:
            if int(timestamp)>0:
                url=url_source+'&max_time=%s'%timestamp
                print(url)
          
            req=request.Request(url)
            with request.urlopen(req) as f:
                str_data=f.read().decode('utf-8')

                #通用时间戳
                list_timestamp=re_timestamp.findall(str_data)
                #最后读取时间
                len_timestamp_list=len(list_timestamp)
                if len_timestamp_list>0:
                    timestamp=list_timestamp[len_timestamp_list-1]
                
                
                if spider_type==0:
                    #########图片Start#############
                    file_list=re_large_pic.findall(str_data)
                    if len(file_list)==0:
                        if len_timestamp_list>0:
                            #当前页无图片，有作品，继续获取下一页数据
                            continue
                        else:
                            print('爬取完成!')
                            self.__save_download_info('爬取完成!')
                            break
                    #print(list_pic)
                    #保存作品
                    self.__save_pic_file(file_list)
                    ##########图片End#########
                elif spider_type==1:
                    #########视频Start#############
                    file_list=re_orig_vedio.findall(str_data)
                    
                    if len(file_list)==0:
                        if len_timestamp_list>0:
                            #当前页无视频，有作品，继续获取下一页数据
                            continue
                        else:
                            print('爬取完成!')
                            self.__save_download_info('爬取完成!')
                            break
                    #print(list_pic)
                    #保存作品
                    self.__save_mp4_file(file_list)
                    ##########视频End#########

                elif spider_type==2:
                    file_list=re_text.findall(str_data)
                    print(file_list)
                    return
                    if len(file_list)==0:
                        if len_timestamp_list>0:
                            #当前页无视频，有作品，继续获取下一页数据
                            continue
                        else:
                            print('爬取完成!')
                            self.__save_download_info('爬取完成!')
                            break
                    #print(list_pic)
                    #保存作品
                   # self.__save_mp4_file(file_list)

            msg='%s->当前时间戳%s,共有%s条记录下载完成！'%(spider_type,timestamp,len(file_list))
            self.__save_download_info(msg)
            time.sleep(3)
        
    #保存下载信息
    def __save_download_info(self,msg):
        
        with open(self.spider_path+'\\'+'spider.info','a') as f:
            f.write(msg+'\n')

    #获取用户详细信息
    def get_user_detail(self,user_id):
        search_url='http://lf.snssdk.com/neihan/user/profile/v2/?user_id=%s'%user_id
        
        try:
            req=request.Request(search_url)
        
            res=request.urlopen(req)
            str_data=res.read().decode('utf-8')
            res.close() #关闭
            json_data=json.loads(str_data)
            return json_data['data']
        except Exception as e:
            print('请求超时->%s'%search_url)
            return []

    #保存用户数据->mysql
    def __save_user_data(self,list_users):
        cmd=MySQLCommand('connotation')
        cmd.connectMysql()

        fileds='point,ugc_count,create_time,user_verified,city,user_id,comment_count,followers,description,screen_name,name,repin_count,gender,followings,avatar_url'
        for user in list_users:
            user_id=int(user['user_id'])
            
            #用户详细信息，list
            #print('开始获取用户详细...')
            user_data=self.get_user_detail(user_id)
            
            if len(user_data)==0:
                print('获取用户详细信息失败，重新获取...')
                user_data=self.get_user_detail(user_id)
                if len(user_data)==0:
                    print('再次获取失败,进行下一循环...')
                    continue

            #print('用户信息获取成功!')
            values=(
                user_data['point']
                ,user_data['ugc_count']
                ,user_data['create_time']
                ,user_data['user_verified']
                ,user_data['city']
                ,user_data['user_id']
                ,user_data['comment_count']
                ,user_data['followers']
                ,user_data['description']
                ,user_data['screen_name']
                ,user_data['name']
                ,user_data['repin_count']
                ,user_data['gender']
                ,user_data['followings']
                ,user_data['avatar_url']
                )
            
            #values=(user['user_id'],user['name'],user['screen_name'],user['avatar_url'],user['last_update'],user['create_time'],user['status'])
            sql="REPLACE INTO t_user (%s) VALUES %s " %(fileds,values)
            try:
                #print(values)
                res_insert=cmd.insertMysql(sql)
                if res_insert==1:
                    print('用户->%s保存成功!'%user_id)
                elif res_insert==2:
                    print('用户->%s已经存在！%s'%(user_id,res_insert))
                else :
                    print('保存失败！')
            except Exception as e:
                print('插入数据发生错误!')
                continue

        print('正在关闭连接...')
        cmd.closeMysql()
        

    #抓取用户数据
    def __get_user_main(self,module):
        while True:
            print('正在启动线程...')
            time.sleep(1)
            print('线程开始...')
            
            temp_data=self.get_top1_userid()
            if not temp_data or len(temp_data)==0 :
                print('当前未能获取用户id,重新获取用户id...')
                continue

            user_id=temp_data[0]
            followings=temp_data[2]#我的关注
            if followings==0 :
                print('当前用户 %s 关注为0,重新获取用户id...'%user_id)
                #更新用户状态为抓取完成
                self.__update_spider_info(module,user_id,self.spider_page,self.spider_size,1)
                continue
            
            
            print('user_id->%s,followers->%s,followigns->%s'%(user_id,temp_data[1],followings))

            #开始抓取用户数据
            self.__get_and_save_users(module,user_id,followings)

            
    
    #根据用户id获取粉丝
    def __get_and_save_users(self,module,moduleid,followings):
        page=self.spider_page-1
        
        orig_url='http://lf.snssdk.com/neihan/user_relation/get_following/v1/?homepage_user_id=%s&count=%s'% (moduleid,self.spider_size)

        if module=='fans':
            orig_url='http://lf.snssdk.com/neihan/user_relation/get_followed/v1/?homepage_user_id=%s&count=%s'% (moduleid,self.spider_size)
        timer_break=0#超过3次获取不到数据就退出
        while True:
            page+=1
            search_url=orig_url + '&offset=%s'% (self.spider_size*(page-1))

            time.sleep(1)
     
            try:
                req=request.Request(search_url)
                with request.urlopen(req) as res:
                    str_data=res.read().decode('utf-8')
                    json_data=json.loads(str_data)
                    
                    
                    json_user_data=json_data['data']['users']
                    #空数组退出循环
                    if len(json_user_data)==0:
                        #当前获取数据条数大于等于关注人数
                        if page*self.spider_size>=followings:
                            print('爬取完成!')
                            break
                        else:
                            timer_break+=1
                            print('没有获取到数据，正尝试第%s次爬取...'% timer_break)
                            if timer_break==3:
                                self.__update_spider_info(module,moduleid,page,self.spider_size,1)
                                print('爬取完成!')
                                break;
                    else:
                        timer_break=0
                        #保存数据
                        print('开始保存第%s页数据...'%page)
                        self.__save_user_data(json_user_data)
                        self.__update_spider_info(module,moduleid,page,self.spider_size)
                        print('保存完成，等待1s进行下一个循环...')
            except Exception as e:
                print('发生错误,位置：get_users() msg:%s'% e.args)
                continue

            #更新用户状态为已抓取
            self.__update_spider_info(module,moduleid,page,self.spider_size)
            

    def __update_spider_info(self,module,moduleid,page,size,finished=0):
        cmd=MySQLCommand()
        cmd.connectMysql()
        sql="REPLACE INTO t_spider_info(ikey,module,moduleid,page,size,finished) VALUES('%s','%s',%s,%s,%s,%s)" %('%s_%s'%(module,moduleid),module,moduleid,page,size,finished)
        #print(sql)
        try:
            cmd.insertMysql(sql)
        except Exception as e:
            print('发生错误，msg:%s'% e.args[0])
        finally:
            cmd.closeMysql()

    #暂时获取关注用户
    def get_top1_userid(self):
        
        cmd=MySQLCommand()
        cmd.connectMysql()
        sql="select * from (select user_id,followers,followings from t_user t1 left join t_spider_info t2 on t2.module='follow' and t2.moduleid =t1.user_id  where t2.ikey is null order by t1.followers desc limit 0,1)a"
        #sql='select user_id,followers,followings from t_user order by followers desc limit 0,1'
        try:
            return cmd.queryMysql(sql,1)
        except Exception as e:
            print('发生错误，msg:%s'% e.args[0])
        finally:
            cmd.closeMysql()

    #发布作品
    def topic_add(self,tag='joke',category_id=1,text=''):
        url='http://lf.snssdk.com/2/essay/zone/ugc/post/v2/'
        #cookie='uuid=867830029868587; login_flag=bec9b86cdd51ad1cd5ed7475110436dc; sessionid=e35627e56ac9280a81b9fd4ba6f6e57a; sid_tt=e35627e56ac9280a81b9fd4ba6f6e57a; sid_guard="e35627e56ac9280a81b9fd4ba6f6e57a|1486399703|2591823|Wed\054 08-Mar-2017 16:45:26 GMT"; qh[360]=1; alert_coverage=97; install_id=7743928436; ttreq=1$7479476a0c15a5069bfc02f898470131b3e1d52b'
        #uuid=867830029868587; qh[360]=1; alert_coverage=97; login_flag=46d31be3e41ea38b08653a08c0f537ad; sessionid=cffb78a88d85a27cbb68f571618c8fc0; sid_tt=cffb78a88d85a27cbb68f571618c8fc0; sid_guard="cffb78a88d85a27cbb68f571618c8fc0|1486909351|2591984|Tue\054 14-Mar-2017 14:22:15 GMT"; install_id=7743928436; ttreq=1$7479476a0c15a5069bfc02f898470131b3e1d52b
        cookie='uuid=867830029868587; qh[360]=1; alert_coverage=93; login_flag=cf710382c2a471bdf8d03c30c4794b99; sessionid=4c9e67f4933e289a9de6ee33800bafc2; sid_tt=4c9e67f4933e289a9de6ee33800bafc2; sid_guard="4c9e67f4933e289a9de6ee33800bafc2|1486990460|2591985|Wed\054 15-Mar-2017 12:54:05 GMT"; install_id=7743928436; ttreq=1$7479476a0c15a5069bfc02f898470131b3e1d52b'
        header={
            'User-Agent':'okhttp/2.7.5'
            ,'Accept-Encoding':'gzip'
            ,'Content-Type':'application/x-www-form-urlencoded'
            ,'Host':'is.snssdk.com'
            ,'Connection':'keep-Alive'
            
            ,'Cookie':cookie
            }
        post_data={
            'tag':tag
            ,'category_id':category_id
            ,'use_video_tool':'0'
            ,'text':text
            ,'activity_id':'0'
            }
        post_data=parse.urlencode(post_data).encode('utf-8')

        req=request.Request(url,data=post_data,headers=header)
        res= request.urlopen(req)
        bRes=res.read()
        res.close()
        tRest=gzip.decompress(bRes).decode("utf-8")
        jsonRes=json.loads(tRest)
      
        return jsonRes
    #评论
    def topic_comment(self,topic_id='55150886286',text=''):
        
        if text=='':
            length_msg=32
            while length_msg>0:
                length_msg-=1
                text+=chr(random.randint(0x4E00, 0x9FBF))
            
        url='http://is.snssdk.com/2/data/v2/post_message/'
        cookie='uuid=867830029868587; qh[360]=1; alert_coverage=31; install_id=7743928436; ttreq=1$7479476a0c15a5069bfc02f898470131b3e1d52b; login_flag=38151db09f58c31509b494b24415a30b; sessionid=1c5cff65cd046179696114ee0cb70952; sid_tt=1c5cff65cd046179696114ee0cb70952; sid_guard="1c5cff65cd046179696114ee0cb70952|1486374511|2589402|Wed\054 08-Mar-2017 09:05:13 GMT"'
        header={
            'User-Agent':'okhttp/2.7.5'
            ,'Accept-Encoding':'gzip'
            ,'Content-Type':'application/x-www-form-urlencoded'
            ,'Host':'is.snssdk.com'
            ,'Connection':'keep-Alive'
            
            ,'Cookie':cookie
            }
        post_data={
            'group_id':topic_id
            ,'item_id':topic_id
            ,'forum_id':'0'
            ,'text':text
            ,'is_comment':'1'
            ,'action':'comment'
            }
     

        req=request.Request(url,data=post_data,headers=header)
        res= request.urlopen(req)
        bRes=res.read()
        res.close()
        tRest=gzip.decompress(bRes).decode("utf-8")
        print(tRest)
            
    #修改昵称
    def user_update_name(self,name):
        url='http://lf.snssdk.com/2/user/update/v2/'
        cookie='uuid=867830029868587; qh[360]=1; alert_coverage=31; install_id=7743928436; ttreq=1$7479476a0c15a5069bfc02f898470131b3e1d52b; login_flag=38151db09f58c31509b494b24415a30b; sessionid=1c5cff65cd046179696114ee0cb70952; sid_tt=1c5cff65cd046179696114ee0cb70952; sid_guard="1c5cff65cd046179696114ee0cb70952|1486374511|2589402|Wed\054 08-Mar-2017 09:05:13 GMT"'
        header={
            'User-Agent':'okhttp/2.7.5'
            ,'Accept-Encoding':'gzip'
            ,'Content-Type':'application/x-www-form-urlencoded'
            ,'Host':'is.snssdk.com'
            ,'Connection':'keep-Alive'
            
            ,'Cookie':cookie
            }
        post_data={
            'name':name
            }

        post_data=parse.urlencode(post_data).encode('utf-8')

        req=request.Request(url,data=post_data,headers=header)
        with request.urlopen(req) as res:
            bRes=res.read()
            tRest=gzip.decompress(bRes).decode("utf-8")
            print(tRest)


    #顶评论
    def comment_zan(self,comment_id,num,sleep=0):
        url='http://lf.snssdk.com/2/data/comment_action/'
        #cookie登陆
        cookie='uuid=867830029868587; qh[360]=1; alert_coverage=31; install_id=7743928436; ttreq=1$7479476a0c15a5069bfc02f898470131b3e1d52b; login_flag=38151db09f58c31509b494b24415a30b; sessionid=1c5cff65cd046179696114ee0cb70952; sid_tt=1c5cff65cd046179696114ee0cb70952; sid_guard="1c5cff65cd046179696114ee0cb70952|1486374511|2589402|Wed\054 08-Mar-2017 09:05:13 GMT"'
        header={
            'User-Agent':'okhttp/2.7.5'
            ,'Accept-Encoding':'gzip'
            ,'Content-Type':'application/x-www-form-urlencoded'
            ,'Host':'is.snssdk.com'
            ,'Connection':'keep-Alive'
            #,'Cookie':cookie
            }
        
        
        while num>0:
            if sleep>0:
                time.sleep(sleep)
            num-=1
            device_id=random.randint(33969000000,33969999999)
            
            post_data={
                'comment_id':comment_id
                ,'action':'digg'
                ,'device_id':device_id
                }
            post_data=parse.urlencode(post_data).encode('utf-8')

            try:
                req=request.Request(url,data=post_data,headers=header)
                res= request.urlopen(req)
                bRes=res.read()
                res.close()
                tRest=gzip.decompress(bRes).decode("utf-8")
                #print(tRest)
            except Exception as e:
                continue
        

    #Http POST
    def spider_post(self,url,data):
        cookie='uuid=867830029868587; qh[360]=1; alert_coverage=31; install_id=7743928436; ttreq=1$7479476a0c15a5069bfc02f898470131b3e1d52b; login_flag=38151db09f58c31509b494b24415a30b; sessionid=1c5cff65cd046179696114ee0cb70952; sid_tt=1c5cff65cd046179696114ee0cb70952; sid_guard="1c5cff65cd046179696114ee0cb70952|1486374511|2589402|Wed\054 08-Mar-2017 09:05:13 GMT"'
        header={
            'User-Agent':'okhttp/2.7.5'
            ,'Accept-Encoding':'gzip'
            ,'Content-Type':'application/x-www-form-urlencoded'
            ,'Host':'is.snssdk.com'
            ,'Connection':'keep-Alive'
            ,'Cookie':cookie
            }
        post_data=parse.urlencode(post_data).encode('utf-8')

        req=request.Request(url,data=post_data,headers=header)
        res= request.urlopen(req)
        bRes=res.read()
        res.close()
        tRest=gzip.decompress(bRes).decode("utf-8")
        return json.loads(tRest)
        
    #搜索
    def search(self,keyword,search_type=2,page=1,size=10):

        action='search'
        if search_type==1:
            search_type='category'
        elif search_type==2:
            search_type='user'
        elif search_type==3:
            search_type='content'
            action='search_all'

        offset=size*(page-1)
        keyword=parse.quote(keyword) #编码
        url='http://lf.snssdk.com/api/2/essay/%s/%s/?keyword=%s&offset=%s'%(search_type,action,keyword,offset)
        #print('ready to search->%s'% url)
        
        req=request.Request(url)
        with request.urlopen(req) as res:
            str_data=res.read().decode('utf-8')
            json_data=json.loads(str_data)
            return json_data
    
        
    #配置
    def set_config(self,config):
        re_config=re.match('(\w+)=([0-9a-zA-Z]+)',config)
        if re_config:
            key=re_config.group(1).lower()
            value=re_config.group(2).lower()
            if key=='page':
                self.page=value
            elif key=='size':
                self.size=value
            elif key=='userid':
                self.user_id=value
    #搜索用户
    def search_user(self,keyword):
        data={}
        if keyword.isdigit():
            data=[self.get_user_detail(keyword)]
        else:
            json_res=self.search(keyword,2)
            if len(json_res)>0:
                data=json_res['data']
        for user in data:
            info=(user['name'],user['user_id'],user['gender'],user['ugc_count'],user['followers'],user['followings'])
            print('name:%s,user_id:%s,gender:%s,ugc_count:%s,followers:%s,followings:%s'%info)
            print('=====================================================================================\n')
    #搜索段子
    def search_content(self,keyword):
        json_res=self.search(keyword,3)
        if len(json_res)>0:
            data=json_res['data']['text']
            for text in data:
                user=text['user']
                info=(text['id'],user['user_id'],user['name'],text['digg_count'],text['comment_count'])
                print('id:%s,user_id:%s,name:%s,digg_count:%s,comment_count:%s'%info)
                print('text:%s'%text['text'])
                print('=====================================================================================\n')

    #段子推荐
    def topic_get(slef,topic_type=-102,count=30,device_id=33960902094):
        url='http://lf.snssdk.com/neihan/stream/mix/v1/?content_type=%s&count=%s&device_id=%s'%(topic_type,count,device_id)
        
        req=request.Request(url)
        with request.urlopen(req) as res:
            str_data=res.read().decode('utf-8')
           
            json_data=json.loads(str_data)
            if len(json_data)>0:
                return json_data['data']['data']
            else:
                return []
    #保存段子
    def topic_save_text(self,group_list):
        cmd=MySQLCommand(db='connotation')
        cmd.connectMysql()

        fileds='id ,text ,media_type,category_name ,create_time ,status_desc ,digg_count ,favorite_count,status  ,share_count ,comment_count ,group_id ,category_id ,user_id'
        
        for group in group_list:
            group=group['group']
            values=(
                group['id']
                ,group['text']
                ,group['media_type']
                ,group['category_name']
                ,group['create_time']
                ,group['status_desc']
                ,group['digg_count']
                ,group['favorite_count']
                ,group['status']
                ,group['share_count']
                ,group['comment_count']
                ,group['group_id']
                ,group['category_id']
                ,group['user']['user_id']
             
                )
            
            
            sql="REPLACE INTO t_joke (%s) VALUES %s " %(fileds,values)
           
            try:
               
                res_insert=cmd.insertMysql(sql)
                if res_insert==1:
                    print('段子->%s保存成功!'%group['id'])
                elif res_insert==2:
                    print('段子->%s已经存在！'%(group['id']))
                else :
                    print('保存失败!')
            except Exception as e:
                print('插入数据发生错误!%s'%e)
                continue
            
        print('正在关闭连接...')
        cmd.closeMysql()
    #根据用户id查找作品
    def search_topic(self,user_id,size=15,timestamp=0):
        url_source='http://lf.snssdk.com/2/essay/zone/user/posts/?mpic=1&webp=1&essence=1&user_id=%s&count=%s'%(user_id,size)
        url=url_source
   
        re_text=re.compile(r'"text"[\s\S]+?"(.*?)"[\s\S]+?"id"[\s\S]+?(\d+?),')
        
        #通用时间戳
        re_timestamp=re.compile(r'create_time[^\d]*(\d+)')
        timestamp=0

        if int(timestamp)>0:
            url=url_source+'&max_time=%s'%timestamp
            print(url)
      
        req=request.Request(url)
        with request.urlopen(req) as f:
            str_data=f.read().decode('utf-8')
            if '\\u' in str_data:
                str_data=str_data.encode('utf-8').decode('unicode_escape')

            
            #通用时间戳
            list_timestamp=re_timestamp.findall(str_data)
            #最后读取时间
            len_timestamp_list=len(list_timestamp)
            if len_timestamp_list>0:
                timestamp=list_timestamp[len_timestamp_list-1]
          
            file_list=re_text.findall(str_data)
           
                
            return {'data':file_list,'timestamp':timestamp}
            
    #根据作品id获取评论
    def get_comment(self,group_id,page=1,size=20):
        url='http://is.snssdk.com/neihan/comments/?group_id=%s&count=%s&offset=%s'%(group_id,size,(page-1)*size)

        re_text=re.compile(r'"id"[\s\S]+?(\d+?),[\s,"]+?group_id[\s\S]+?"text"[\s\S]+?"(.*?)"')
        req=request.Request(url)
        with request.urlopen(req) as f:
            str_data=f.read().decode('utf-8')

            file_list=re_text.findall(str_data)

            return file_list
                           
    #抓取段子From捧腹网
    def get_text_from_pengfu(self,page):
        url='http://m.pengfu.com/xiaohua_%s.html'%page
        req=request.Request(url)
        with request.urlopen(req) as res:
            str_data=res.read().decode('utf-8')
           
            text_list=re.findall(r'class="con-img">([\s\S]+?)</div',str_data)
            
            return text_list

   #Sex
    def get_and_down_sex_pic(self):
        page=0
        re_pic=re.compile('/art/html/(\d+)[\s\S]+?/span>(.*)</a>')
        agent='Mozilla/5.0 (Linux; U; Android 5.1.1; zh-cn; Mi-4c Build/LMY47V) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/46.0.2490.85 Mobile Safari/537.36 XiaoMi/MiuiBrowser/8.2.15'
        while True:
            page+=1
            url='http://www.1xnxn.net/art/Qpic/index-%s.html'%page
            headers={'User-Agent':agent}
            req=request.Request(url,headers=headers)
            
            with request.urlopen(req) as res:
                str_data=res.read().decode('utf-8')
                picUrlList=re_pic.findall(str_data)
               
                if len(picUrlList)>0:
                    for picItem in picUrlList:
                        picUrl='http://www.1xnxn.net/art/html/%s.html'%picItem[0]
                        title=picItem[1]
                        
                        _path='D:\\Python3\\Download\\Sex\\%s'% title
                        if not os.path.exists(_path):
                            os.mkdir(_path)
                           
                        req1=request.Request(picUrl,headers=headers)
                        with request.urlopen(req1) as res1:
                            str_data1=res1.read().decode('utf-8')
                            picUrls=re.findall('<img[\s\S]+?(http.*?\.jpg)',str_data1)
                            for url in picUrls:
                                print(url)
                                save_path=_path+'\\'+re.search('(\w+).jpg',txt).group(1)+'.jpg'
                                #如果存在，继续下一个循环
                                if os.path.exists(save_path):
                                    print('文件已存在->',save_path)
                                    continue
                               
                                
                                #写入文件
                                print('打开网络文件->',url)
                                req2=request.Request(url)
                                with request.urlopen(req2,headers=headers) as f:
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
                            
                        
            time.sleep(10)
    #上传图片
    def upload_img(self):
        #buld post body data
        boundary = '----------%s' % hex(int(time.time() * 1000))
        data = []
        data.append('--%s' % boundary)
        
        data.append('Content-Disposition: form-data; name="%s"\r\n' % 'openudid')
        data.append('2b4c9f6cd91ac0c')
        data.append('--%s' % boundary)
        
        data.append('Content-Disposition: form-data; name="%s"\r\n' % 'category_id')
        data.append('7')
        data.append('--%s' % boundary)
        
        data.append('Content-Disposition: form-data; name="%s"\r\n' % 'aid')
        data.append('7')
        data.append('--%s' % boundary)
        
        fr=open(r'D:\PHOTO\hardaway0.jpg','rb')
        data.append('Content-Disposition: form-data; name="%s"; filename="hardaway0.jpg"' % 'file')
        data.append(fr.read())
        fr.close()
        data.append('--%s--\r\n' % boundary)
    
        http_url='http://is.snssdk.com/neihan/file/upload/v1/image/?iid=7743928436&device_id=33960902094&ac=wifi&channel=xiaomi&aid=7&app_name=joke_essay&version_code=601&version_name=6.0.1&device_platform=android&ssmix=a&device_type=Mi-4c&device_brand=Xiaomi&os_api=22&os_version=5.1.1&uuid=867830029868587&openudid=2b4c9f6cd91ac0c&manifest_version_code=601&resolution=1080*1920&dpi=480&update_version_code=6011'
        http_body=b''
        for x in data:
            if(type(x) == str):
                http_body += x.encode('utf-8')+'\r\n'.encode('utf-8')
            else:
                http_body += x+'\r\n'.encode('utf-8')
        try:
            #buld http request
            req=request.Request(http_url, data=http_body)

            cookie='uuid=867830029868587; qh[360]=1; alert_coverage=31; install_id=7743928436; ttreq=1$7479476a0c15a5069bfc02f898470131b3e1d52b; login_flag=38151db09f58c31509b494b24415a30b; sessionid=1c5cff65cd046179696114ee0cb70952; sid_tt=1c5cff65cd046179696114ee0cb70952; sid_guard="1c5cff65cd046179696114ee0cb70952|1486374511|2589402|Wed\054 08-Mar-2017 09:05:13 GMT"'

        
            #header
            req.add_header('Content-Type', 'multipart/form-data; boundary=%s' % boundary)
            req.add_header('User-Agent','okhttp/2.7.5')
            req.add_header('Referer','http://is.snssdk.com')
            req.add_header('Accept-Encoding','gzip')
            req.add_header('Host','is.snssdk.com')
            req.add_header('cookie',cookie)
            #post data to server
            resp = request.urlopen(req, timeout=5)
            #get response
            qrcont=resp.read()
            resp.close()
            tRest=gzip.decompress(qrcont).decode("utf-8")
            print (tRest)
            
            
        except Exception as e:
            
            print('一场啦')
    #主函数
    def main(self):
        while True:
            
            #0:抓图片 1：抓视频 2：抓粉丝 3：抓关注
            #search_user
            #search_content

         
             
            cmd=input('输入命令:')

            
            #如果抓取的信息需要保存到本地，先创建一个文件夹
            if cmd=='0' or cmd=='1':
                user_id=input('输入用户ID：')
                while not( user_id == 'quit') and not user_id.isdigit():
                    user_id=input('输入错误，请重新输入用户ID：')

                if user_id.lower()=='quit':
                    print('退出成功！')
                    break
                
                user_id=int(user_id)
                if user_id>0:
                    self.user_id=user_id
                list_user_data=self.get_user_detail(self.user_id)
                
                if len(list_user_data)==0:
                    print('用户不存在！')
                    break
                
                spider_name=list_user_data['name']

                self.spider_path='D:\\python3\\dowload\\%s'% spider_name
                if not os.path.exists(self.spider_path):
                    os.mkdir(self.spider_path)
     
            if cmd=='0':
                self.get_user_topics(0,spider_name)
            elif cmd=='1':
                self.get_user_topics(1,spider_name)
            elif cmd=='2':
                print('')
            elif cmd=='3':
                print('爬取用户线程启动...')
                self.__get_user_main('follow')
                #topic_add
            elif cmd=='4':
                print('爬取段子线程启动...')
                device_id='33960902094'
                timer=0
                while True:
                    time.sleep(3)
                    
                    topic_data=self.topic_get(device_id=device_id)
                    if len(topic_data)==0:
                        timer+=1
                        if timer>=3:
                            break
                        device_id='339609%s'%random.randint(10000,99999)
                        print('===============%s==============='%device_id)
                        
                    self.topic_save_text(topic_data)
                    
            elif cmd=='5':
                print('发布作品线程启动...')
                device_id='33960902094'
                timer=0
                add_time_span=2*60
                page=30
                while True:
                    page-=1
                    
                    try:
                        topic_data=text_list=self.get_text_from_pengfu(page)
                        if len(topic_data)==0:
                            timer+=1
                            if timer>=3:
                                break
                            continue
                        else:
                            timer=0
                        for text in topic_data:
                            text=text.replace('&nbsp;','')
                            jsonRes=self.topic_add(text=text)
                            bRes=jsonRes['message']=='success' and jsonRes['code']==0
                            if bRes:
                                
                                add_time_span=random.randint(3*60,5*60)
                                #self.topic_comment(content_id,'我自己就是审评！')
                                print('发布成功！~')
                                print('%ss后重新发布~'%add_time_span)
                            else :
                                print('发布失败！%s'%jsonRes)
                            time.sleep(add_time_span)#延时
                    except Exception as e:
                        print('发布作品异常！%s'%e)
                        continue
                    
                    
            elif cmd=='6':#顶评论
                comment_id=input('输入评论id：')
                num=input('输入次数：')
                self.comment_zan(comment_id,int(num),0)
                #topic_add
            elif cmd=='7':#根据用户id获取作品
                user_id=input('输入用户id：')
                dic_data=self.search_topic(user_id)
                for lst in dic_data['data']:
                    print(lst[1],'->',lst[0],'\n')
            elif cmd=='8' or cmd=='9':#根据作品id获取评论
                page=1
                if cmd=='9':
                    page=input('输入页数：')
                topic_id=input('输入作品id：')
                list_data=self.get_comment(topic_id,int(page))
                for lst in list_data:
                    print(lst[0],'->',lst[1],'\n')
                    
            elif 'search' in cmd: #搜索
                
                search_type=cmd.replace('search','')
                if len(search_type)==0 or not search_type.isdigit():
                    break
                
                keyword=input('输入关键字:')
                json_data=self.search(keyword)
                if search_type=='2': #搜用户
                    self.search_user(keyword)
                elif search_type=='3':#搜段子
                    self.search_content(keyword)
            elif cmd=='-1':
                ext_cmd=input('是否启用默认配置（Y/N）：')
                if ext_cmd.lower()=='n':
                    config=''
                    while not config=='ok':
                        config=input('输入配置（key=value）:')
                        self.set_config(config)
            

spider=ConnotationSpider()
spider.main()


