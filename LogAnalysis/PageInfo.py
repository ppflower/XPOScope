# coding=UTF-8
class PageInfo:
    opt_count = None
    image_index = None
    ui_text = None
    privacy_map = None

    def __init__(self, opt_count, image_index, privacy_map, ui_text):
        self.opt_count = opt_count
        self.image_index = image_index
        self.privacy_map = privacy_map
        self.ui_text = ui_text


def read_report(report_path):
    page_infos = {}
    try:
        f = open(report_path, 'r', encoding='utf-8')
        line = f.readline().replace('\n', '')
    except UnicodeDecodeError:
        f = open(report_path, 'r', encoding='ANSI')
        line = f.readline().replace('\n', '')
    while line:
        if line.startswith("Page"):
            opt_image = line.split(' ')
            opt_count = opt_image[1]
            image_index = opt_image[2]
            if image_index in page_infos.keys():
                line = f.readline().replace('\n', '')
                if line != '':
                    privacy_list = line.split(',')
                    page_info = page_infos[image_index]
                    exist_privacy_map = page_info.privacy_map
                    for privacy_tuple in privacy_list:
                        temp = privacy_tuple.split(' ')
                        if len(temp) == 2:
                            privacy_key = temp[0]
                            privacy_val = temp[1]
                        else:
                            continue
                        if privacy_key not in exist_privacy_map.keys():
                            exist_privacy_map[privacy_key] = [privacy_val]
                        else:
                            if privacy_val not in exist_privacy_map[privacy_key]:
                                exist_privacy_map[privacy_key].append(privacy_val)
                line = f.readline().replace('\n', '')
            else:
                line = f.readline().replace('\n', '')
                privacy_map = {}
                if line != '':
                    privacy_list = line.split(',')
                    for privacy_tuple in privacy_list:
                        temp = privacy_tuple.split(' ')
                        if len(temp) != 2:
                            continue
                        privacy_key = temp[0]
                        privacy_val = temp[1]
                        if privacy_key not in privacy_map.keys():
                            privacy_map[privacy_key] = [privacy_val]
                        else:
                            if privacy_val not in privacy_map[privacy_key]:
                                privacy_map[privacy_key].append(privacy_val)
                line = f.readline().replace('\n', '')
                tmp_ui_text = line.split(',')
                ui_text = []
                for tmp in tmp_ui_text:
                    tmp = tmp.strip()
                    if len(tmp) > 0:
                        ui_text.append(tmp)
                page_info = PageInfo(opt_count, image_index, privacy_map, ui_text)
                page_infos[image_index] = page_info
        line = f.readline().replace('\n', '')
    return page_infos
