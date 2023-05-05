# coding=UTF-8
import uuid
import requests
import hashlib
import time
from importlib import reload
import sys
import DataBase
from trans007 import GoogleTranslate
import ast
YOUDAO_URL = ''
APP_KEY = ''
APP_SECRET = ''
reload(sys)


def encrypt(signStr):
    hash_algorithm = hashlib.sha256()
    hash_algorithm.update(signStr.encode('utf-8'))
    return hash_algorithm.hexdigest()


def truncate(q):
    if q is None:
        return None
    size = len(q)
    return q if size <= 20 else q[0:10] + str(size) + q[size - 10:size]


def do_request(data):
    headers = {'Content-Type': 'application/x-www-form-urlencoded'}
    return requests.post(YOUDAO_URL, data=data, headers=headers)


def connect(words):
    q = words
    data = {}
    data['from'] = '源语言'
    data['to'] = '目标语言'
    data['signType'] = 'v3'
    curtime = str(int(time.time()))
    data['curtime'] = curtime
    salt = str(uuid.uuid1())
    signStr = APP_KEY + truncate(q) + salt + curtime + APP_SECRET
    sign = encrypt(signStr)
    data['appKey'] = APP_KEY
    data['q'] = q
    data['salt'] = salt
    data['sign'] = sign
    data['vocabId'] = "您的用户词表ID"

    response = do_request(data).json()
    if 'web' in response.keys():
        return response['web'][0]['value']
    else:
        return str(response['translation'][0]).split(' ')


def get_related(start, end):
    if start.lower() == end.lower():
        return True
    # 本地库
    # local_flag = DataBase.search_local(start, end)
    # if local_flag is not None:
    #     if local_flag == 1:
    #         return True
    #     else:
    #         return False
    # 知识图谱
    return False
    # try:
    #     url = 'https://api.conceptnet.io/relatedness?' \
    #           'node1=/c/en/{0}&node2=/c/en/{1}'.format(start, end)
    #     obj = requests.get(url).json()
    # except:
    #     time.sleep(5)
    #     url = 'https://api.conceptnet.io/relatedness?' \
    #           'node1=/c/en/{0}&node2=/c/en/{1}'.format(start, end)
    #     obj = requests.get(url).json()
    # if obj['value'] >= 0.2:
    #     DataBase.load_local(start, end, 1)
    #     return True
    # else:
    #     DataBase.load_local(start, end, 0)
    #     return False


def related_match(ui_texts, word):
    for ui_text in ui_texts:
        for pic_word in ui_text:
            if get_related(pic_word.replace('_', ' ').replace('"', "'"), word.replace('_', ' ').replace('"', "'")):
                return True
    return False

if __name__ == '__main__':
    string = '本文在对小程序框架和技术现状进行文献研究和系统分析的基础上，从自动化和通用性两个角度出发，开发了第一款通用的小程序自动化测试框架。首先通过调研小程序框架和市场，详细阐述了小程序的现有技术和市场规模，并对现有自动化工具的相关工作做了详细介绍。在对小程序技术做了比较全面的综述之后，本文开始正式阐述自动化测试框架的研究思路和实现过程，以“点击位置识别”的方式将小程序自动化测试抽象为以页面为节点的图遍历过程，并将这一测试框架通用化，使其能运行在不同的小程序承载平台。最后，本文对自动化测试框架进行了实验评估和分析，通过小程序覆盖率这一指标评估了框架的性能，并用XPO攻击检测的方式对框架的实用性进行了深度测评。这款通用的小程序自动化测试框架的研发，将为后续研究者对小程序的隐私检测、安全性分析和敏感行为分析等提供通用性的方案。'
    print(connect(string))
