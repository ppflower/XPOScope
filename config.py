import os
import time

project_prefix = "D:/Laboratory/Code/XpoCheckerMini"
prefix = "D:/Laboratory/Code/XpoCheckerMini/dynamicExerciser"

MOBILE_IMAGE_PATH = "/sdcard/screenshots/"
SCREENSHOT_PATH = prefix + "/data/screenshots/"
EVALUATE_PATH = prefix + "/data/evaluate_classifier/"

MOBILE_SCREENSHOT_CACHE_PATH = "/sdcard/picCache/"
SCREENSHOT_CACHE_PATH = prefix + "/data/picCache/"

PAGE_TEXT_PATH = prefix + "/data/page_text/"
MINI_APP_LOG = project_prefix + "/MiniAppLog/"

SHORT_SLEEP_TIME = 3
LONG_SLEEP_TIME = 6
OPERATION_SLEEP_TIME = 1.5
SIMILAR_THRESHOLD = 0.7
OCR_CONFIDENCE = 0.8
DEVICE_WIDTH = 1080
DEVICE_HEIGHT = 2400
TCP_PORT = 12345
ALIPAY_TRANSFER_PORT = 9999
BUFFER_SIZE = 1024
MINI_APP_TEST_TIME = 60 * 10
WORD_PER_ELEMENT = 8
MINI_APP_TYPE = '医疗'
WORK_BOOK = "./AliPay_XPOCheckerMini_TestCases.xls"

All_Mini_App_Types = ['活动']
# All_Mini_App_Types = ['书籍', '交通', '体育', '健康', '健身', '医疗', '商业', '地图', '天气',
#                      '娱乐', '家庭', '摄影', '教育', '新闻', '旅游', '汽车', '活动', '漫画',
#                      '生活', '社交', '约会', '美容', '育儿', '艺术', '视频', '购物', '通讯', '金融', '音乐', '食品']

def long_sleep():
    time.sleep(LONG_SLEEP_TIME)


def short_sleep():
    time.sleep(SHORT_SLEEP_TIME)


def operate_sleep():
    time.sleep(OPERATION_SLEEP_TIME)


def get_ip():
    return "127.0.0.1"
    # return "192.168.0.4"


def mini_apps_start_num(mini_app_plat):
    log_path = MINI_APP_LOG
    if mini_app_plat == 0:
        log_path += "alipay/"
    if mini_app_plat == 1:
        log_path += "wechat/"
    if mini_app_plat == 2:
        log_path += "baidu/"
    log_path = log_path + MINI_APP_TYPE + "/"
    if not os.path.exists(log_path):
        os.makedirs(log_path)
    count = 0
    for file in os.listdir(log_path):
        log_file = os.path.join(log_path, file)
        if os.path.isfile(log_file) and log_file.find(".txt") > 0:
            count += 1
    return count


if __name__ == "__main__":
    print(len(All_Mini_App_Types))
