import hashlib
import string

from paddleocr import PaddleOCR
import dynamicExerciser.mini_app_utils as miniAppUtils
import config
import dynamicExerciser.adb_commands as adb_commands
ocr = PaddleOCR()


def screenshot_dump_str(image_index, need_text_locations) -> [list, string, list]:
    image_path = config.SCREENSHOT_PATH + str(image_index) + ".png"
    return dump_str(image_path, need_text_locations)


def cache_image_dump_str() -> [list, string, list]:
    # 可能需要进行临时截图
    adb_commands.adb_cache_screenshot()
    image_path = config.SCREENSHOT_CACHE_PATH + "temp.png"
    return dump_str(image_path, False)


def dump_str(image_path, need_text_locations) -> [list, string, list]:
    dump_str = ocr.ocr(image_path)
    res_dump_str = []
    ocr_click_locations = []
    for idx in range(len(dump_str)):
        lines = dump_str[idx]
        for line in lines:
            text, confidence = line[1][0], line[1][1]
            start_point, end_point = line[0][0], line[0][2]
            start_point_x, start_point_y = start_point[0], start_point[1]
            end_point_x, end_point_y = end_point[0], end_point[1]
            mid_x, mid_y = int((start_point_x + end_point_x) / 2), int((start_point_y + end_point_y) / 2)
            if not miniAppUtils.is_noise_click_location(mid_x, mid_y):
                if confidence >= config.OCR_CONFIDENCE:
                    res_dump_str.append(remove_symbols(text))
                if need_text_locations:
                    ocr_click_locations.append([mid_x, mid_y])
    res_dump_str = remove_keyboard(res_dump_str)
    merge_str = ''.join(res_dump_str)
    md5 = hashlib.md5()
    md5.update(merge_str.encode(encoding='UTF-8'))
    return res_dump_str, md5.hexdigest(), ocr_click_locations


def remove_symbols(target_str):
    res_str = ''
    for char in target_str:
        if '\u4e00' <= char <= '\u9fa5' or char in string.digits or char in string.ascii_letters:
            res_str += char
    return res_str


def remove_keyboard(current_dump_str: list) -> list:
    res = []
    license_plate = '省京津沪渝冀豫云辽黑湘皖鲁新苏浙赣鄂桂甘晋蒙陕吉闽赣粤青藏川宁琼使领警学港澳贵'
    for dump_str in current_dump_str:
        if not (len(dump_str) == 1 and dump_str in string.ascii_letters + string.punctuation + license_plate):
            res.append(dump_str)
    return res
