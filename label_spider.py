# -*- coding：utf-8 -*-
import requests
import time
import random
from multiprocessing import Pool
from bs4 import BeautifulSoup
import codecs
#中文分词工具结巴
#import jieba

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
        video_info_list = []
        response = requests.get(url, headers=headers, timeout=1)
        html = response.text
        soup = BeautifulSoup(html, 'lxml')
        #视频的av号
        aid = url.rpartition('av')[2]
        #视频标题
        #tag = soup.find(id='viewbox_report')
        #title=tag.h1.get_text()
        #print(title)
        #结巴分词
        #seg_list=jieba.cut_for_search(title)
        #print(' '.join(seg_list))
        #video_info_list.append(tag.h1.get_text())

        #视频标签
        labels = soup.find_all(class_='tag')
        for label in labels:
            video_info_list.append(label.get_text())
        print(video_info_list)

        filename='labels/av'+aid+'.txt'
        file=codecs.open(filename,'w','utf-8')
        for str in video_info_list:
            file.write(str+' ')

        time.sleep(0.1)

    except:
        print("error")
        time.sleep(0.1)


def label_spider():
    av_list = []
    filename = 'txt_file/guichuAV.txt'
    with open(filename) as file:
        for line in file:
            av_list.append(line.split('\n')[0])
    print(av_list)

    pool = Pool()
    urls = ['https://www.bilibili.com/video/av{}'.format(i) for i in av_list]
    print(urls)
    pool.map(getHtmlInfo, urls)
    pool.close()
    pool.join()


if __name__ == '__main__':
    label_spider()
