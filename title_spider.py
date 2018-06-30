import requests
import time
import pymysql
import random
from multiprocessing import Pool
from bs4 import BeautifulSoup
import os

conn = pymysql.connect(host = '127.0.0.1' , port = 3306 , user = 'root' , passwd = '' , db = 'bilibili',charset='utf8')
cur = conn.cursor()
result = []
video_list = []
video_list2 = []

def LoadUserAgent(uafile):
    uas = []
    with open(uafile,'rb') as uaf:
        for ua in uaf.readlines():
            if ua:
                uas.append(ua.strip()[1:-1])
    random.shuffle(uas)
    return uas

uas = LoadUserAgent("txt_file/user_agents.txt")

def LoadProxies(uafile):
    ips = []
    with open(uafile,'r') as proxies:
        for ip in proxies.readlines():
            if ip:
                ips.append(ip.strip())
    random.shuffle(ips)
    return ips

ips = LoadProxies("txt_file/proxies.txt")


def getHtmlInfo2(url):
    ua = random.choice(uas)
    headers = {
        'Accept-Encoding': 'gzip, deflate, br',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8,ja;q=0.7',
        'Connection': 'keep-alive',
        'Host': 'www.bilibili.com',
        'Origin': 'https://www.bilibili.com',
        # 'Referer': 'https://www.bilibili.com/video/' + str(i) + '?spm_id_from=333.338.recommend_report.3',
        'User-Agent': ua
    }
    try:
        response = requests.get(url, headers=headers, timeout=1)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        tag = soup.find(id='viewbox_report')

        video_list2.append(tag.h1.get_text())
        crumbs = tag.find_all(class_='crumb')

        video_list2.append(crumbs[0].get_text().split(' ')[0])
        video_list2.append(crumbs[1].get_text().split(' ')[0])
        video_list2.append(crumbs[2].get_text().split(' ')[0])

        video_list2.append(tag.time.get_text())

        aid = url.rpartition('av')[2]
        video_list2.append(aid)
        print(video_list2)

        save_db2()
        time.sleep(0.1)
        # gevent.sleep(0.1)

    except:
        print("@@@@")
        time.sleep(0.1)
        # gevent.sleep(0.1)
        # print(ip_choice)

def save_db2():
    # 将数据保存至本地
    global video_list2, cur, conn
    #sql = "insert into bili_video2(title,zone,time,aid) values(%s, %s, %s) where aid=%s;"
    #sql = "update bili_video set title=%s,zone1=%s,zone2=%s,zone3=%s,time=%s where aid=%s;"
    sql = "insert into bili_video2(title,zone1,zone2,zone3,time,aid) values(%s, %s, %s, %s, %s, %s);"
    #for row in video_list2:
    #try:
        #print(row)
    cur.execute(sql, video_list2)
    conn.commit()
    video_list2 = []



def spider2():
    pool = Pool()
    urls = ['https://www.bilibili.com/video/av{}'.format(i) for i in range(22500000,22800000)]
    pool.map(getHtmlInfo2, urls)
    pool.close()
    pool.join()


if __name__ == '__main__':
    spider2()
    conn.close()


