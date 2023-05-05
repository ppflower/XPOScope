import os
import time

import config as config

KEYCODE_HOME = 3
KEYCODE_BACK = 4
KEYCODE_SEARCH = 84
KEYCODE_ENTER = 66
KEYCODE_SWITCH_APP = 187


def adb_screenshot(page_index):
    time.sleep(1.5)
    os.system("adb shell screencap {0}{1}.png".format(config.MOBILE_IMAGE_PATH, page_index))
    os.system("adb pull {0}{2}.png {1}{2}.png".format(config.MOBILE_IMAGE_PATH, config.SCREENSHOT_PATH, page_index))


def adb_cache_screenshot():
    time.sleep(1.5)
    page_index = "temp"
    os.system("adb shell screencap {0}{1}.png".format(config.MOBILE_SCREENSHOT_CACHE_PATH, page_index))
    os.system("adb pull {0}{2}.png {1}{2}.png".format(config.MOBILE_SCREENSHOT_CACHE_PATH, config.SCREENSHOT_CACHE_PATH,
                                                      page_index))


def adb_text_input(text: str):
    os.system("adb shell input text \"{0}\"".format(text))


def adb_key_event(key_code: int):
    os.system("adb shell input keyevent {0}".format(key_code))
    config.operate_sleep()


# ADB Keyboard实现中文打印
def adb_text_zh(text: str):
    os.system("adb shell am broadcast -a ADB_INPUT_TEXT --es msg '{0}'".format(text))
    config.operate_sleep()


def oneplus_wx_enter():
    switch_to_gboard_keyboard()
    config.operate_sleep()
    adb_click(0.91 * config.DEVICE_WIDTH, 0.91 * config.DEVICE_HEIGHT)


def switch_to_adb_keyboard():
    # adb shell ime list -a 查找所有输入法
    os.system("adb shell ime set com.android.adbkeyboard/.AdbIME")


def switch_to_gboard_keyboard():
    os.system(
        "adb shell ime set com.google.android.inputmethod.latin/com.android.inputmethod.latin.LatinIME")


# # 切换为原先的键盘便于后续的搜索按键点击
# def switch_to_huawei_keyboard():
#     os.system("adb shell ime set com.baidu.input_huawei/.ImeService")
#
#


def adb_keyboard_key_event(key_code: int):
    os.system("adb shell am broadcast -a ADB_INPUT_CODE --ei code {0}".format(key_code))


def adb_click_sleep(x: float, y: float):
    os.system("adb shell input tap {0} {1}".format(x, y))
    config.operate_sleep()


def adb_click(x: float, y: float):
    os.system("adb shell input tap {0} {1}".format(x, y))


def adb_delete_file(file_path: str):
    os.system("adb shell rm {0}".format(file_path))


def adb_mk_dir(dir_path: str):
    os.system("adb shell mkdir {0}".format(dir_path))


# 删除文件夹及其内部文件
def adb_del_dir(dir_path: str):
    os.system("adb shell rm -r {0}".format(dir_path))


# 在对screenshot重命名的同时也需要对classifier中对象进行重命名
def rename_screenshot(old_screenshot_name, new_screenshot_name):
    old_screenshot_path = config.SCREENSHOT_PATH + str(old_screenshot_name) + ".png"
    new_screenshot_path = config.SCREENSHOT_PATH + str(new_screenshot_name) + ".png"
    if os.path.exists(new_screenshot_path):
        os.remove(new_screenshot_path)
    os.rename(old_screenshot_path, new_screenshot_path)


def del_screenshot(del_screenshot_name):
    del_screenshot_path = config.SCREENSHOT_PATH + str(del_screenshot_name) + ".png"
    os.remove(del_screenshot_path)
