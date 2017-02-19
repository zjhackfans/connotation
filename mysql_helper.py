# -*- coding: utf-8 -*-
__author__ = 'djstava@gmail.com'

import logging
import pymysql

class MySQLCommand(object):
    
    def __init__(self,host='localhost',port=3306,user='root',passwd='alt43353',db='connotation',table='t_user'):
        self.host = host
        self.port = port
        self.user = user
        self.password = passwd
        self.db = db
        self.table = table

    def connectMysql(self):
        try:
            self.conn = pymysql.connect(host=self.host,port=self.port,user=self.user,passwd=self.password,db=self.db,charset='utf8')
            self.cursor = self.conn.cursor()
        except:
            print('connect mysql error.')

   
        

    def queryMysql(self,sql,f=0):
        
        try:
            self.cursor.execute(sql)
            rows = []
            if f==0:
                rows=self.cursor.fetchall()
            else:
                rows=self.cursor.fetchone()
            return rows

        except:
            print(sql + ' execute failed.')
            return []

    ##单条插入数据行
    def insertMysql(self,sql):
        
        #sql = "INSERT INTO " + self.table + " (%s) VALUES %s" % (fileds,values)+';'

        res_execute=0
        try:
            res_execute=self.cursor.execute(sql)
            self.conn.commit()
        except:
            print("insert failed.")
            self.conn.rollback()
        return res_execute
        

    ##多条插入数据行
    def insertMysqlMLine(self,list_values):
        
        self.connectMysql()
        
        sql = "INSERT INTO " + self.table + " (%s) VALUES %s" % (fileds,values)+';'
        
        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            print("insert failed.")
            self.conn.rollback()
        finally:
            self.closeMysql()
    

    def updateMysqlSN(self,name,sex):
        sql = "UPDATE " + self.table + " SET sex='" + sex + "'" + " WHERE name='" + name + "'"
        print("update sn:" + sql)

        try:
            self.cursor.execute(sql)
            self.conn.commit()
        except:
            self.conn.rollback()
            


    def closeMysql(self):
        self.cursor.close()
        self.conn.close()



##mysql=MySQLCommand()
##
##fileds='userid,name,avatar_url'
##values=('123','zj','http:\\www.zj.com')
##mysql.insertMysql(fileds,values)


