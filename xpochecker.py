import json
import multiprocessing
import os
import time
import re
import socket
import threading
import eventlet
import config
from trafficMonitor import traffic_utils as traffic_utils
import xlrd


def get_last_opt():
    opt_path = config.PAGE_TEXT_PATH + "opt.txt"
    if not os.path.exists(opt_path):
        return -1
    with open(opt_path) as f:
        last_opt = f.read()
        f.close()
    if last_opt == '':
        return -1

    return last_opt


def read_page_text(page_index):
    page_file_path = config.PAGE_TEXT_PATH + str(page_index) + ".txt"
    res = []
    with open(page_file_path, 'r', encoding='utf-8') as f:
        dump_strs = f.readlines()
        f.close()
    for dump_str in dump_strs:
        new_str = re.sub('\n', "", dump_str)
        res.append(new_str)
    return res


def traffic_listening_server(url_traffic_map, url_page_index_map):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', config.TCP_PORT))
    s.listen()
    start_time = time.time()
    while True:
        sock, addr = s.accept()
        thread_server = threading.Thread(target=link, args=(sock, addr, url_traffic_map, url_page_index_map))
        thread_server.start()
        end_time = time.time()
        if end_time - start_time > config.MINI_APP_TEST_TIME + 10:
            break
    s.close()


def link(sock, addr, url_traffic_map, url_page_index_map):
    print("Accept new connection from %s:%s..." % addr)
    sock.send('Connect success!'.encode())
    while True:
        # 解决传输数据超过缓冲区大小的问题multiprocessing Manager dict是否线程安全
        recv_data = bytes()
        while True:
            temp_data = sock.recv(config.BUFFER_SIZE)
            if temp_data != b' ':
                recv_data += temp_data
            if len(temp_data) < config.BUFFER_SIZE:
                break
        try:
            recv_json = json.loads(recv_data.strip())
        except json.JSONDecodeError:
            continue
        opt_type = recv_json['opt_type']
        print("Receive Data")
        # opt_type 0 接受隐私数据流量
        # opt_type 1 关闭连接
        if opt_type == 1:
            # back_data = {'opt_type': opt_type, 'status_code': 200}
            privacy_data = recv_json['data']
            privacy_url = recv_json['url']
            if privacy_url not in url_traffic_map.keys():
                # time.sleep(0.5)
                last_opt_count = get_last_opt()
                if last_opt_count != -1:
                    url_traffic_map[privacy_url] = privacy_data
                    url_page_index_map[privacy_url] = last_opt_count
                else:
                    print("Not append")
            else:
                print("url recorded")
        elif opt_type == 2:
            break
    sock.close()


def generate_report(mini_app_name, mini_app_plat, url_traffic_map, url_page_index_map):
    url_privacy_tuples_map = {}
    for url in url_traffic_map.keys():
        if url not in url_privacy_tuples_map.keys():
            traffic = url_traffic_map[url]
            privacy_traffic = traffic_utils.detect_privacy(traffic)
            if len(privacy_traffic) != 0:
                url_privacy_tuples_map[url] = privacy_traffic
    opt_urls_map = {}
    for url in url_page_index_map.keys():
        if url not in url_privacy_tuples_map.keys():
            continue
        page_index = url_page_index_map[url]
        if page_index not in opt_urls_map.keys():
            opt_urls_map[page_index] = [url]
        else:
            opt_urls_map[page_index].append(url)

    print("开始生成报告")
    report_path = config.MINI_APP_LOG
    if mini_app_plat == 0:
        report_path += "alipay/"
    if mini_app_plat == 1:
        report_path += "wechat/"
    if mini_app_plat == 2:
        report_path += "baidu/"
    report_path = report_path + config.MINI_APP_TYPE + "/" + mini_app_name + ".txt"
    opt_image_map = generate_opt_image_map()
    with open(report_path, 'w') as f:
        for opt_count in opt_urls_map.keys():
            if opt_count in opt_image_map.keys():
                f.write("Page " + str(opt_count) + " " + str(opt_image_map[opt_count]))
            else:
                f.write("Page " + str(opt_count) + " temp")
            f.write("\n")
            urls = opt_urls_map[opt_count]
            ui_text = read_page_text(opt_count)
            privacy_tuples = []
            for url in urls:
                if url not in url_privacy_tuples_map.keys():
                    continue
                for tup in url_privacy_tuples_map[url]:
                    if tup not in privacy_tuples and tup[1] != '':
                        privacy_tuples.append(tup)
            for idx in range(len(privacy_tuples)):
                if idx == len(privacy_tuples) - 1:
                    f.write(str(privacy_tuples[idx][0]) + " " + str(privacy_tuples[idx][1]))
                else:
                    f.write(str(privacy_tuples[idx][0]) + " " + str(privacy_tuples[idx][1]) + ",")
            f.write("\n")
            for idx in range(len(ui_text)):
                if idx == len(ui_text) - 1:
                    f.write(str(ui_text[idx]))
                else:
                    f.write(str(ui_text[idx]) + ",")
            f.write("\n")
        f.flush()
        f.close()


def generate_opt_image_map():
    opt_image_map_path = config.PAGE_TEXT_PATH + "opt_image_map.txt"
    opt_image_map = {}
    with open(opt_image_map_path, 'r') as f:
        line = f.readline().replace('\n', '')
        while line:
            opt_image = line.split(' ')
            opt_count = opt_image[0]
            image_index = opt_image[1]
            opt_image_map[opt_count] = image_index
            line = f.readline().replace('\n', '')
    return opt_image_map


def run_traffic_monitor():
    os.system("python ./trafficMonitor/traffic_monitor.py")


def run_dynamic_exerciser(mini_app_plat, mobile_model, mini_app_name, queue: multiprocessing.Queue):
    os.system(
        "python ./dynamicExerciser/dynamic_exerciser.py {0} {1} {2}".format(mini_app_plat, mobile_model, mini_app_name))
    queue.put("end")


def run_traffic_listening_server(url_traffic_map, url_page_index_map):
    eventlet.monkey_patch()
    with eventlet.Timeout(config.MINI_APP_TEST_TIME + 20, False):
        traffic_listening_server(url_traffic_map, url_page_index_map)
    # 生成记录报告
    # try:
    #     generate_report(mini_app_name, url_traffic_map, url_page_index_map)
    # except Exception as e:
    #     print(e)
    print("listening server end!")


def get_target_mini_app_names(type_name):
    excel = xlrd.open_workbook(config.WORK_BOOK)
    sheet = excel.sheet_by_index(0)
    cols_num = sheet.ncols
    target_col_vals = None
    for i in range(cols_num):
        col_vals = sheet.col_values(i)
        if col_vals[0] == type_name:
            target_col_vals = col_vals
            break
    return target_col_vals


#
# if __name__ == "__main__":
#     os.system("adb reverse tcp:8080 tcp:8080")
#
#     mini_app_platform = 1
#     mobile_model = 1
#     for mini_app_type in config.All_Mini_App_Types:
#         config.Mini_App_Type = mini_app_type
#         mini_app_names = get_target_mini_app_names(config.Mini_App_Type)
#         mini_apps_start_num = config.mini_apps_start_num(mini_app_platform)
#
#         for i in range(mini_apps_start_num + 1, len(mini_app_names)):
#             mini_app_name = (mini_app_names[i]).replace("\n", "")
#             mini_app_name = mini_app_name.replace(" ", "")
#             if len(mini_app_name) == 0:
#                 continue
#
#             print("开始生成{0}Log:".format(mini_app_name))
#             queue = multiprocessing.Queue(maxsize=1)
#             processes = []
#             manager = multiprocessing.Manager()
#             url_traffic_map = manager.dict()
#             url_page_index_map = manager.dict()
#             traffic_listen_process = multiprocessing.Process(target=run_traffic_listening_server,
#                                                              args=(url_traffic_map, url_page_index_map))
#             processes.append(traffic_listen_process)
#             traffic_listen_process.start()
#             time.sleep(3)
#             mitmproxy_process = multiprocessing.Process(target=run_traffic_monitor)
#             processes.append(mitmproxy_process)
#             mitmproxy_process.start()
#             time.sleep(3)
#             dynamic_exerciser_process = multiprocessing.Process(target=run_dynamic_exerciser, args=(
#                 mini_app_platform, mobile_model, mini_app_name, queue,))
#             processes.append(dynamic_exerciser_process)
#             dynamic_exerciser_process.start()
#
#             ret = queue.get()
#             for i in range(len(processes)):
#                 process = processes[i]
#                 if process.is_alive():
#                     process.terminate()
#
#             from psutil import process_iter
#             from signal import SIGTERM  # or SIGKILL
#
#             for proc in process_iter():
#                 for conns in proc.connections(kind='inet'):
#                     if conns.laddr.port == 8080:
#                         print("KILL Mitmproxy")
#                         try:
#                             proc.send_signal(SIGTERM)  # or SIGKILL
#                         except Exception as e:
#                             continue
#             try:
#                 generate_report(mini_app_name, mini_app_platform, url_traffic_map, url_page_index_map)
#             except Exception as e:
#                 print(e)
#             print(mini_app_name + "报告生成完成")

if __name__ == "__main__":
    os.system("adb reverse tcp:9999 tcp:9999")
    mini_app_platform = 2
    mobile_model = 1
    mini_app_name = "伊尔美重庆美容院加盟"
    #
    print("开始生成{0}Log:".format(mini_app_name))
    queue = multiprocessing.Queue(maxsize=1)
    processes = []
    manager = multiprocessing.Manager()
    url_traffic_map = manager.dict()
    url_page_index_map = manager.dict()
    traffic_listen_process = multiprocessing.Process(target=run_traffic_listening_server,
                                                     args=(url_traffic_map, url_page_index_map))
    processes.append(traffic_listen_process)
    traffic_listen_process.start()
    time.sleep(3)
    mitmproxy_process = multiprocessing.Process(target=run_traffic_monitor)
    processes.append(mitmproxy_process)
    mitmproxy_process.start()
    time.sleep(3)
    dynamic_exerciser_process = multiprocessing.Process(target=run_dynamic_exerciser, args=(
        mini_app_platform, mobile_model, mini_app_name, queue,))
    processes.append(dynamic_exerciser_process)
    dynamic_exerciser_process.start()

    ret = queue.get()
    for i in range(len(processes)):
        process = processes[i]
        if process.is_alive():
            process.terminate()

    from psutil import process_iter
    from signal import SIGTERM  # or SIGKILL

    for proc in process_iter():
        for conns in proc.connections(kind='inet'):
            if conns.laddr.port == 8080:
                print("KILL Mitmproxy")
                try:
                    proc.send_signal(SIGTERM)  # or SIGKILL
                except Exception as e:
                    continue
    try:
        generate_report(mini_app_name,mini_app_platform, url_traffic_map, url_page_index_map)
    except Exception as e:
        print(e)
# 处理运行过程产生的图片和数据，主要是截图的转移以及文本文件的删除
