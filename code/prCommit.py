# -*- coding: utf-8 -*-
#####��ȡproject��label������Ŀ
#####��ַ��https://api.github.com/repos/rails/rails/labels
import xlrd
import itertools
import json
import os
import scrapy
from scrapy import Request

class pullRequestSpider(scrapy.spiders.Spider):

    name = "commitComments1" #��������
    allowed_domains = ["github.com"] #�ƶ���ȡ����
    num = 1 # ҳ����Ĭ�ϴӵ�һҳ��ʼ
    handle_httpstatus_list = [404, 403, 401,500] #�����������б��е�״̬�룬����Ҳ������ֹ
    output_file = open('commitComments2', "w") #����ļ�
    crawlResult = []
    allRes = []
    crawlList = []
    index=0
    error=0  
  
    def __init__(self): #��ʼ��
        scrapy.spiders.Spider.__init__(self)
        self.token_list = []
        self.filepath = r'/media/mamile/DATA1/G���ļ���/beihang_study/scapy_spider/���߳���ȡpr��commit/crawlComments1/commitComments'
        with open(self.filepath,"r") as e:
            for line in e:
                data = json.loads(line)
		self.crawlList.append([data['comments_url'],data["pullRequestID"],data["owner"]])

        self.token_list = [
	'f0f1147d70df77018989579552b83e616a9286c0',
	'74d04340a4852d69b7984a4823e2ae864037aa4b',
	'b0deefda65f81ca88228870966dc6ccbeae074bd',]
        self.token_iter = itertools.cycle(self.token_list) #����ѭ�������������������һ��token�󣬻����¿�ʼ����    

    def __del__(self): #�������ʱ���ر��ļ�
        self.output_file.close()

    def start_requests(self):
        start_urls = [] #��ʼ��ȡ�����б�
        url = self.crawlList[self.index][0]+"?per_page=99&page="+str(self.num) ##��һ����ȡurl
        #���һ����ȡ����
        start_urls.append(scrapy.FormRequest(url, headers={
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0',
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'Authorization': 'token ' + self.token_iter.next(),#����ֶ�Ϊ���token�ֶ�
            },dont_filter=True, callback=self.parse)) 

        return start_urls

    def yield_request(self): #����һ������������
        url = self.crawlList[self.index][0]+"?per_page=99&page="+str(self.num) #��һ����ȡurl
        #��������
        return Request(url,headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:36.0) Gecko/20100101 Firefox/36.0',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en',
                'Authorization': 'token ' + self.token_iter.next(),
                },dont_filter=True,callback=self.parse)

    #��������
    def parse(self, response,max=5):
        if self.index == self.crawlList.__len__():
            return

        if response.status in self.handle_httpstatus_list:#�������handle_httpstatus_list�г��ֵ�״̬��
            print '**************************'
            self.error+=1
            if self.error==max:
                self.index+=1
                self.num=1
                self.error=0
            if self.index == self.crawlList.__len__():
                return
            else:
                yield self.yield_request() #�����µ�����
            return

        json_data = json.loads(response.body_as_unicode()) #��ȡjson
        length = len(response.body_as_unicode()) #��ȡjson����
        #print (json_data==None)
        if length > 5:
            self.error=0
            self.num = self.num + 1
            for issue in json_data:
                if issue == None:
                    continue
                data = {}
                data['body']=issue.get("body",None)
		if 'user' in issue and issue['user'] != None:
                    data["user"]=issue["user"].get("login",None)
		else:
		    data['user']=None
		data['owner'] = self.crawlList[self.index][-1]
		data['pullRequestID'] = self.crawlList[self.index][1]
		data['created_at'] = issue.get('created_at',None)
            	self.output_file.write(json.dumps(data)+'\n') #���ÿһ�У���ʽҲΪjson
            self.output_file.flush()
            yield self.yield_request() #�����µ�����

        else: #��ζ����ȡ�����һҳ
            self.error=0
            self.index+=1          
            self.num=1
            if self.index == self.crawlList.__len__():
                self.__del__()
                return
            else:
                yield self.yield_request() #�����µ�����