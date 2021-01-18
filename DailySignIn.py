#!/usr/bin/python3
import sys
import logging
import hashlib
import requests
from time import sleep
from os import environ
from random import uniform

# 配置logger
logger = logging.getLogger('BaiduTieBa-DailySignIn')
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler(sys.stdout)
handler.setLevel(logging.DEBUG)
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

# 从环境变量中获取SCKEY和BDUSS
SCKEY = environ.get('SCKEY', 'Specified environment variable is not set.')

BDUSS = environ.get('BDUSS', 'Specified environment variable is not set.')

cookies = {"BDUSS": BDUSS}

headers = {
    "connection":
    "keep-alive",
    "Content-Type":
    "application/x-www-form-urlencoded",
    "charset":
    "UTF-8",
    "User-Agent":
    "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.71 Safari/537.36",
}


# md5加密
def md5Encryption(str):
    # 创建md5对象
    hl = hashlib.md5()
    hl.update(str.encode(encoding='utf-8'))
    return hl.hexdigest()


# 获取TBS
def get_tbs(headers, cookies):
    tbs_url = "http://tieba.baidu.com/dc/common/tbs"
    r = requests.get(url=tbs_url,
                     headers=headers,
                     cookies=cookies,
                     allow_redirects=False)
    jsondata = r.json()
    if jsondata['is_login'] == 1:
        logger.info('获取TBS成功')
    else:
        logger.error(f'获取TBS失败 {jsondata}')
    tbs = jsondata['tbs']
    return tbs


# 获取没有签到和已签到的贴吧
def get_forums(headers, cookies):
    followed_url = "https://tieba.baidu.com/mo/q/newmoindex"
    r = requests.get(url=followed_url,
                     headers=headers,
                     cookies=cookies,
                     allow_redirects=False)
    jsondata = r.json()
    if jsondata['error'] != "success":
        logger.error('获取贴吧列表失败')
    else:
        logger.info('获取贴吧列表成功')
    not_signed_forums_list = []
    signed_forums_list = []
    forums = jsondata['data']['like_forum']
    for forum in forums:
        if forum['is_sign'] == 0:
            not_signed_forums_list.append(forum['forum_name'])
        else:
            signed_forums_list.append(forum['forum_name'])
    return not_signed_forums_list, signed_forums_list


# 贴吧签到
def signin(tbs, not_signed_forums_list, signed_forums_list, cookies,
           signround):
    sign_url = "http://c.tieba.baidu.com/c/c/forum/sign"
    logger.info(f'开始第{signround+1}轮贴吧签到')
    for forum in not_signed_forums_list:
        enCodeMd5 = md5Encryption(f'kw={forum}tbs={tbs}tiebaclient!!!')
        data = f"kw={forum}&tbs={tbs}&sign={enCodeMd5}"
        data = data.encode('utf-8')
        r = requests.post(url=sign_url, data=data, cookies=cookies)
        jsondata = r.json()
        if jsondata['error_code'] == "0":
            logger.info(f'{forum}吧签到成功')
            signed_forums_list.append(forum)
            not_signed_forums_list.remove(forum)
        elif jsondata['error_code'] == "160002":
            logger.info(f'亲，你之前已经签过{forum}吧了')
            signed_forums_list.append(forum)
            not_signed_forums_list.remove(forum)
        else:
            logger.info(f'{forum}吧签到失败')
        # 每个贴吧之间随机休眠 1 到 4 秒
        sleep_time = uniform(1, 4)
        logger.info(f'随机休眠： {sleep_time}秒')
        sleep(sleep_time)
    logger.info(f'第{signround+1}轮贴吧签到结束')
    logger.info(f"第{signround+1}轮贴吧签到结束后，已签到贴吧: {', '.join(signed_forums_list)}")
    logger.info(f"第{signround+1}轮贴吧签到结束后，未签到贴吧: {', '.join(not_signed_forums_list)}")
    return not_signed_forums_list, signed_forums_list


# Server酱推送
def serverchan_notif(sckey, signed_forums_list, not_signed_forums_list):
    logger.info("推送任务结果到Server酱")
    serverchan_url = f"https://sc.ftqq.com/{sckey}.send"
    data = {
        "text":
        "百度贴吧签到任务完成",
        "desp":
        f"已签到的贴吧： {', '.join(signed_forums_list)}\n\n签到失败的贴吧： {', '.join(not_signed_forums_list)}"
    }
    r = requests.post(url=serverchan_url, data=data)
    jsondata = r.json()
    if jsondata['errmsg'] == 'success':
        logger.info("Server酱推送成功")
    else:
        logger.info("Server酱推送失败")


if __name__ == "__main__":
    logger.info("BaiduTieBa-DailySignIn任务启动")
    tbs = get_tbs(headers, cookies)
    not_signed_forums_list, signed_forums_list = get_forums(
        headers, cookies)
    logger.info(f"待签到的贴吧： {', '.join(not_signed_forums_list)}")
    logger.info(f"已签到的贴吧： {', '.join(signed_forums_list)}")
    signround = 0
    while not_signed_forums_list and signround < 5:
        # 每一轮签到间隔30秒， 最多进行5轮尝试签到
        if signround != 0:
            logger.info("休眠30秒，准备开始下一轮重新签到签到失败的贴吧")
            sleep(30)
        logger.info(f"{'-'*30}")
        not_signed_forums_list, signed_forums_list = signin(
            tbs, not_signed_forums_list, signed_forums_list, cookies,
            signround)
        logger.info(f"{'-'*30}")
        signround += 1
        if signround == 5:
            logger.info(f"系统设置的{signround}轮签到全部结束")
            break
    logger.info("签到任务结束")
    not_signed_forums_list = set(not_signed_forums_list)
    signed_forums_list = set(signed_forums_list)
    logger.info(f"已签到的贴吧： {', '.join(signed_forums_list)}")
    logger.info(f"签到失败的贴吧： {', '.join(not_signed_forums_list)}")
    serverchan_notif(SCKEY, signed_forums_list, not_signed_forums_list)
