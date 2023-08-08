import random
import re
import shutil

import uiautomator2 as u2
import os
import config
from dynamicExerciser import mini_app_auto as mini_app_auto
from dynamicExerciser.page_utils.Page import Page
import dynamicExerciser.picLabel.evaluate as evaluate
from PIL import Image


def connect_device():
    d = u2.connect(get_device_serial())
    return d


def get_device_serial():
    cmd_res = os.popen("adb devices").readlines()
    device_serial = cmd_res[1].split('\t')[0]
    return device_serial


def list_similarity_check(list1: list, list2: list):
    same_count = 0
    for val in list1:
        if val in list2:
            same_count += 1
    max_len = len(list1) if len(list1) >= len(list2) else len(list2)
    if len(list1) <= 5 and len(list2) <= 5:
        if same_count > 0:
            return True
        else:
            return False

    if len(list1) > 10 and len(list2) > 10:
        if max_len * config.SIMILAR_THRESHOLD <= same_count:
            return True
        else:
            return False
    else:
        if max_len * 0.5 <= same_count:
            return True
        else:
            return False


def is_similar_page(page1: Page, page2: Page):
    return is_similar_page_by_details(page1.page_md5, page1.page_dump_str, page2.page_md5, page2.page_dump_str)


def is_similar_page_by_details(page1_md5, page1_dump_str, page2_md5, page2_dump_str):
    if page1_md5 is None or page2_md5 is None or page1_dump_str is None or page2_dump_str is None:
        return False
    if page1_md5 == page2_md5 or list_similarity_check(page1_dump_str, page2_dump_str):
        return True
    return False


def extract_image_info(yolo_test: evaluate.YoloTest, image_path) -> list:
    all_element_list = yolo_test.predictOneImg(image_path)
    location_lists = []
    for element_list in all_element_list:
        location = []
        if len(element_list) > 4:
            for index in range(4):
                location.append(element_list[index])
        if location not in location_lists:
            location_lists.append(location)
    return location_lists


def compute_xy_scale(index):
    screenshot_path = config.SCREENSHOT_PATH + str(index) + ".png"
    evaluate_path = config.EVALUATE_PATH + str(index) + ".png"
    screenshot_img = Image.open(screenshot_path)
    evaluate_img = Image.open(evaluate_path)
    screenshot_width, screenshot_height = screenshot_img.width, screenshot_img.height
    evaluate_width, evaluate_height = evaluate_img.width, evaluate_img.height
    return screenshot_width / evaluate_width, screenshot_height / evaluate_height


def is_noise_click_location(x, y):
    bound_left, bound_right, bound_top, bound_bottom = 0, config.DEVICE_WIDTH, 0, 0.09 * config.DEVICE_HEIGHT
    if bound_left <= x <= bound_right and bound_top <= y < bound_bottom:
        return True
    return False


def random_click_location(now_click_locations):
    device_width, device_height = config.DEVICE_WIDTH, config.DEVICE_HEIGHT
    while True:
        x = random.randint(0, device_width)
        y = random.randint(0, device_height)
        if not is_noise_click_location(x, y) and [x, y] not in now_click_locations:
            return [x, y]


agree_list = {"允许", "同意"}
deny_list = {"拒绝", "取消"}
tip_list = {"授权", "申请", "权限", "获取"}


def contain_permission_tip(dump_strs):
    if not any_element_in_list(agree_list, dump_strs):
        return False
    if not any_element_in_list(deny_list, dump_strs):
        return False
    if not any_tip_in_list(tip_list, dump_strs):
        return False
    return True


def any_element_in_list(element_list, dump_strs):
    for element in element_list:
        if element in dump_strs:
            return True
    return False


def any_tip_in_list(element_list, dump_strs):
    for element in element_list:
        if contain_part_dump_str(dump_strs, element):
            return True
    return False


def contain_part_dump_str(dump_strs, target_str):
    for dump_str in dump_strs:
        if target_str in dump_str:
            return True
    return False


def create_opt_file():
    page_text_path = config.PAGE_TEXT_PATH + "opt.txt"
    if os.path.exists(page_text_path):
        os.remove(page_text_path)
    fp = open(config.PAGE_TEXT_PATH + "opt.txt", 'w')
    fp.close()


def create_opt_image_map_file():
    opt_image_map_path = config.PAGE_TEXT_PATH + "opt_image_map.txt"
    if os.path.exists(opt_image_map_path):
        os.remove(opt_image_map_path)
    fp = open(config.PAGE_TEXT_PATH + "opt_image_map.txt", "w")
    fp.close()


def write_last_opt(opt_count):
    opt_file_path = config.PAGE_TEXT_PATH + "opt.txt"
    with open(opt_file_path, 'w', encoding='utf-8') as f:
        f.write(str(opt_count))
        f.flush()
    f.close()


def append_opt_image_map(opt_count, image_index):
    opt_image_map_path = config.PAGE_TEXT_PATH + "opt_image_map.txt"
    with open(opt_image_map_path, 'a', encoding='utf-8') as f:
        f.write(str(opt_count) + " " + str(image_index) + "\n")
        f.flush()
    f.close()


def write_page_text(opt_page_count, dump_strs: list):
    page_file_path = config.PAGE_TEXT_PATH + str(opt_page_count) + ".txt"
    with open(page_file_path, 'w', encoding='utf-8') as f:
        for dump_str in dump_strs:
            f.write(dump_str + "\n")
        f.flush()
    f.close()


def read_page_text(opt_page_count):
    page_file_path = config.PAGE_TEXT_PATH + str(opt_page_count) + ".txt"
    res = []
    with open(page_file_path, 'r', encoding='utf-8') as f:
        dump_strs = f.readlines()
    f.close()

    for dump_str in dump_strs:
        new_str = re.sub('\n', "", dump_str)
        res.append(new_str)
    return res


def del_evaluate_img():
    for file in os.listdir(config.SCREENSHOT_PATH):
        source_file = os.path.join(config.SCREENSHOT_PATH, file)
        if os.path.isfile(source_file) and source_file.find(".png") > 0:
            os.remove(source_file)


def del_screenshot_img():
    for file in os.listdir(config.EVALUATE_PATH):
        source_file = os.path.join(config.EVALUATE_PATH, file)
        if os.path.isfile(source_file) and source_file.find(".png") > 0:
            os.remove(source_file)


def remove_screenshot_img(mini_app_plat, mini_app_type, mini_app_name):
    target_dir = config.SCREENSHOT_PATH
    if mini_app_plat == 0:
        target_dir += "alipay/"
    if mini_app_plat == 1:
        target_dir += "wechat/"
    if mini_app_plat == 2:
        target_dir += "baidu/"
    target_dir += mini_app_type + "/"
    target_dir += mini_app_name
    mkdir(target_dir)
    for file in os.listdir(config.SCREENSHOT_PATH):
        source_file = os.path.join(config.SCREENSHOT_PATH, file)
        target_file = os.path.join(target_dir, file)
        if os.path.isfile(source_file) and source_file.find(".png") > 0:
            shutil.move(source_file, target_file)


def del_page_text():
    for file in os.listdir(config.PAGE_TEXT_PATH):
        source_file = os.path.join(config.PAGE_TEXT_PATH, file)
        if os.path.isfile(source_file) and source_file.find(".txt") > 0:
            os.remove(source_file)


def mkdir(target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)


if __name__ == "__main__":
    remove_screenshot_img(1, config.MINI_APP_TYPE, "test")
