# -*- coding：utf-8 -*-
import re
import requests
import time
import random
from multiprocessing import Pool
import json
import sys

def LoadUserAgent(uafile):
    uas = []
    with open(uafile, 'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1])
    random.shuffle(uas)
    return uas

uas = LoadUserAgent("txt_file/user_agents.txt")


def LoadProxies(uafile):
    ips = []
    with open(uafile, 'r') as proxies:
        for ip in proxies.readlines():
            if ip:
                ips.append(ip.strip())
    random.shuffle(ips)
    return ips

ips = LoadProxies("txt_file/proxies.txt")

def LoadCookies(cookiefile):
    cks=[]
    with open(cookiefile,'r') as cookies:
        for ck in cookies.readlines():
            if ck:
                cks.append(ck.strip())
    random.shuffle(cks)
    return cks

cks=LoadCookies("txt_file/cookies.txt")

def getHtmlInfo(url):
    ua = random.choice(uas)
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'www.bilibili.com',
        'Origin': 'https://www.bilibili.com',
        'User-Agent': ua
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        response.encoding = 'utf-8'
        html = response.text
        #记录视频av号
        aid = url.rpartition('av')[2]

        # 正则表达式找出弹幕文件的cid
        #chat_id = re.findall('"cid":(.*?),"page":\d,"from":"vupload"', html)[0]
        chat_id = re.findall('"cid":(.*?),"dimension"', html)[0]
        print(chat_id)

        # danmuku_url='https://api.bilibili.com/x/v2/dm/history/index?type=1&oid=???&month=2018-05'
        timestamp_list=[]
        danmuku_time_set = set([])
        # 按日期爬取弹幕文件(请求不同的主机！需要换headers!)
        headers['Host'] = 'api.bilibili.com'
        headers['Origin'] = 'https://www.bilibili.com'

        for i in range(5,6):
            danmuku_url = 'https://api.bilibili.com/x/v2/dm/history/index?type=1&oid='+chat_id+'&month=2018-0'+str(i)
            cookie = random.choice(cks)
            #headers['Cookie'] = 'finger=edc6ecda; fts=1527413056; sid=56tlqcpx; buvid3=7CCE93FC-D9E2-4918-BAF7-930C77773B8131489infoc; rpdid=kxxkiwopoodosimpokoxw; LIVE_BUVID=00b13f615cf55a8d8dd7927634dff6b1; LIVE_BUVID__ckMd5=11240c9a82848669; UM_distinctid=163f1e1df4da5-0ba1afde044c6d-47e1f32-100200-163f1e1df4e631; _dfcaptcha=b2a8dd6972680d45f4b312aaba0b86f4; DedeUserID=48652918; DedeUserID__ckMd5=f6f84312d671c9da; SESSDATA=1e3b62b0%2C1531384395%2C8eeb076e; bili_jct=71f3eebeeb370da5f43f959070d835a8'
            headers['Cookie'] = cookie
            time_danmuku_response = requests.get(danmuku_url, headers=headers, timeout=20)
            #print(time_danmuku_response.json())
            #时间列表
            timestamp_list=time_danmuku_response.json()["data"]

            #print(timestamp_list)
            #历史记录中弹幕会有重复的，所以需要去重,set可以用来记录不重复元素

            for timestamps in timestamp_list:
                danmuku_url = 'https://api.bilibili.com/x/v2/dm/history?type=1&oid={0}&date={1}'.format(chat_id,timestamps)
                danmuku_text = requests.get(danmuku_url, headers=headers, timeout=20).text
                time.sleep(20)
                # 匹配弹幕时间（浮点数）
                danmuku_time=[]
                danmuku_time=re.findall('<d p="(.*?),', danmuku_text)
                #print(danmuku_time)
                for t in danmuku_time:
                    # 记录弹幕时间(浮点数)
                    danmuku_time_set.add(float(t))

        print(danmuku_time_set)

        int_danmuku_time_list = [round(x) for x in danmuku_time_set]
        #print(int_danmuku_time_list)
        # 每个分段的弹幕数量统计的list,时间间隔为1s(四舍五入)
        time_seg_count_list = [0]*max(int_danmuku_time_list)
        for i in range(0, max(int_danmuku_time_list)):
            time_seg_count_list[i] = int_danmuku_time_list.count(i)
        print(time_seg_count_list)

        str_danmuku_time_list=[]
        for i in range(0, max(int_danmuku_time_list)):
            minute=i // 60
            str_minute =str(minute)
            second=i % 60
            str_second =str(second)
            if minute < 10:
                str_minute = '0' + str(minute)
            if second < 10:
                str_second = '0' + str(second)
            time_str=str_minute+':'+str_second
            str_danmuku_time_list.append(time_str)

        subdict={}
        subdict['name'] = aid
        subdict['time'] = str_danmuku_time_list
        subdict['value'] = time_seg_count_list

        print(subdict)

        with open('danmuku_flow/danmuku_flow.json', 'a+', encoding='utf-8') as f:
            f.write(json.dumps(subdict)+',')
        time.sleep(20)
    except:
        print("Unexpected Error:"+sys.exc_info())
        time.sleep(20)



def danmuku_spider():
    #存放各分区前十视频av号的list
    av_list = []
    filename = 'txt_file/first10av.txt'
    with open(filename) as file:
        for line in file:
            av_list.append(line.split('\n')[0])
    print(av_list)
    #av_list = [21469961,21611096,21879543,21939408,21943764,22174951,22283476,22444246,22601482,22670081]
    #av_list = [21622065, 21515033, 21698119, 22248267, 22462265, 22517607, 22727792, 21933328, 22003590, 22450388, 21726368, 21863943, 22053983, 22057252, 22167112, 22247272, 22124946, 22395230, 22693324]
    pool = Pool()
    urls = ['https://www.bilibili.com/video/av{}'.format(i) for i in av_list]
    pool.map(getHtmlInfo, urls)
    # 将统计信息写入json文件
    pool.close()
    pool.join()


if __name__ == '__main__':
    danmuku_spider()
