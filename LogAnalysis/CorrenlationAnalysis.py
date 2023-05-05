# coding=UTF-8
import ExaMatch
import ParMatch
import ReaMatch
import PageInfo
import FiltrateKey
import re
import os


def confusion_or_not(key):
    for confusion_key in FiltrateKey.confusion_keys:
        if confusion_key in key:
            return True
    return False


def filtrate_before_val(privacy_key, central_key, privacy_map):
    confusion_flag = False
    for val in privacy_map[privacy_key]:
        if bool(re.match(r"^1[3-9]\d{9}$", val)):
            confusion_flag = True
    # 对特定元素先进行商店相关检查，再进行人物相关检查
    if confusion_or_not(central_key.lower()) or confusion_flag:
        person_flag = False
        for temp_key in privacy_map.keys():
            for shop_name in FiltrateKey.shop_related_categories:
                if shop_name in temp_key and temp_key != central_key:
                    return True

        for temp_key in privacy_map.keys():
            if temp_key.lower() in FiltrateKey.human_related_categories and temp_key != central_key:
                print(temp_key)
                person_flag = True
                break
        if not person_flag:
            return True
    # 删除不敏感词汇
    if FiltrateKey.fold_or_not(privacy_key.lower()) and not confusion_flag:
        return True
    return False


def filtrate_after_val(privacy_key, privacy_val, central_key):
    # 过滤无效流量
    if FiltrateKey.delete_noinf_key(privacy_key, privacy_val):
        return True
    # 过滤无效手机号
    if 'phone' in central_key or 'mobile' in central_key:
        return not bool(re.match(r"^1[3-9]\d{9}$", privacy_val))
    return False


def generate_xpo_report(page_infos, path, name):
    # 对privacy的情况进行标记
    # 其中词能够exactly_matched 1
    # 其中词能够partially_matched 2
    # 不完全匹配就是3
    with open("{}\\{}".format(path, name), 'w', encoding='utf-8') as f:
        is_xpo = []
        not_xpo = []
        for image_index in page_infos.keys():
            page_info = page_infos[image_index]
            # 标记各种privacy类型对应的状态（完全匹配，部分匹配，不完全匹配）
            privacy_map = page_info.privacy_map
            marked_keys = []
            xpo_risk_keys = []
            no_xpo_risk_keys = []
            ui_text = page_info.ui_text
            tran_ui_text = []
            my_info_flag = False
            for privacy_key in privacy_map.keys():
                privacy_vals = privacy_map[privacy_key]
                central_key = FiltrateKey.find_central(privacy_key.lower())
                # 开始检查

                if filtrate_before_val(privacy_key, central_key, privacy_map):
                    if privacy_key == 'phone':
                        print('yes')
                    marked_keys.append(privacy_key)
                    not_xpo.append(privacy_key)
                    no_xpo_risk_keys.append(privacy_key)
                    continue

                for privacy_val in privacy_vals:
                    if filtrate_after_val(privacy_key, privacy_val, central_key):
                        marked_keys.append(privacy_key)
                        not_xpo.append(privacy_key)
                        no_xpo_risk_keys.append(privacy_key)
                        break

                    if not my_info_flag:
                        my_info_flag = FiltrateKey.is_my_info(privacy_key, privacy_val)

                    if FiltrateKey.is_my_info(privacy_key, privacy_val):
                        marked_keys.append(privacy_key)
                        not_xpo.append(privacy_key)
                        no_xpo_risk_keys.append(privacy_key)
                        break

                    # 完全匹配
                    if ExaMatch.exactly_matched(privacy_val, ui_text):
                        marked_keys.append(privacy_key)
                        not_xpo.append(privacy_key)
                        no_xpo_risk_keys.append(privacy_key)
                        break

                    # 部分匹配
                    is_partial_matched, ui_data = ParMatch.partially_matched(privacy_val, ui_text)
                    ui_informative = True
                    if is_partial_matched:
                        for each_data in ui_data:
                            privacy_not_matched, ui_not_matched = ParMatch.not_partial_matched(privacy_val, each_data)
                            # 优化
                            if len(ui_not_matched) != 0 and len(privacy_not_matched) != 0:
                                ui_informative = False
                            else:
                                marked_keys.append(privacy_key)
                                not_xpo.append(privacy_key)
                                no_xpo_risk_keys.append(privacy_key)
                                break
                            for each_index in ui_not_matched:
                                if ExaMatch.has_information(each_data[each_index]):
                                    ui_informative = True
                                    break
                            if not ui_informative:
                                marked_keys.append(privacy_key)
                                xpo_risk_keys.append(privacy_key)
                                is_xpo.append(privacy_key)
                                break
                    if privacy_key in marked_keys:
                        break
            # 关联分析
            unmarked_key = list(set(marked_keys) ^ privacy_map.keys())
            for i in range(0, len(unmarked_key)):
                unmarked_key[i] = FiltrateKey.find_central(unmarked_key[i].lower())

            if my_info_flag:
                for key in unmarked_key:
                    no_xpo_risk_keys.append(key)
                    not_xpo.append(privacy_key)

            elif len(unmarked_key) != 0:
                if len(tran_ui_text) == 0:
                    for un_tran_text in ui_text:
                        tran_ui_text.append(ReaMatch.connect(un_tran_text))

                for key in unmarked_key:
                    if ReaMatch.related_match(tran_ui_text, key):
                        no_xpo_risk_keys.append(key)
                        not_xpo.append(privacy_key)
                    else:
                        xpo_risk_keys.append(key)
                        is_xpo.append(privacy_key)

            opt_count = page_info.opt_count
            image_index = page_info.image_index
            f.write("Page " + str(opt_count) + " " + str(image_index))
            f.write("\n")
            f.write(str(ui_text))
            f.write("\n")
            f.write(str(privacy_map))
            f.write("\n")

            f.write("NO XPO RISK KEY: ")
            f.write(str(no_xpo_risk_keys))
            f.write("\n")
            f.write("XPO RISK KEY: ")
            f.write(str(xpo_risk_keys))
            f.write("\n")
    f.close()
    print("生成完毕---{}".format(name))


def get_all_dirs(data_path):
    dirs = os.listdir(data_path)
    childirs = []
    for dirname in dirs:
        childir = data_path + '\\' + str(dirname)
        childirs.append(childir)
    return childirs


def run(origin, output):
    log_names = []
    for dir_name in get_all_dirs(origin):
        log_names += get_all_dirs(dir_name)
    for log_name in log_names:
        print("start check xpo -->{}".format(log_name))
        page = PageInfo.read_report(log_name)
        generate_xpo_report(page, output, re.split(r'\\', log_name)[-1])


if __name__ == '__main__':
    run('baidu', 'final_analysis\\baidu')
