# -*- coding: utf-8 -*-

import json
import re

import config
import os
import shutil

from trafficMonitor import traffic_utils


def remove_screenshot_img(mini_app_plat, mini_app_name):
    target_dir = config.SCREENSHOT_PATH
    if mini_app_plat == 0:
        target_dir += "alipay/"
    if mini_app_plat == 1:
        target_dir += "wechat/"
    if mini_app_plat == 2:
        target_dir += "baidu/"
    target_dir += mini_app_name
    mkdir(target_dir)
    for file in os.listdir(config.SCREENSHOT_PATH):
        source_file = os.path.join(config.SCREENSHOT_PATH, file)
        target_file = os.path.join(target_dir, file)
        if os.path.isfile(source_file) and source_file.find(".png") > 0:
            shutil.move(source_file, target_file)


def mkdir(target_dir):
    if not os.path.exists(target_dir):
        os.makedirs(target_dir)


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
    report_path = report_path + config.Mini_App_Type + "\/" + mini_app_name + ".txt"
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


if __name__ == "__main__":
    str = '{"status":1,"result":{"list":[{"confId":"9898","sycModuleId":"0","style":"3","showStyle":"1","dataId":"30","status":2,"startTime":"2020/09/14 15:22:16","endTime":"","order":"4","name":"","subname":"","count":0,"showMoreType":"0","rightShowMoreType":"0","showMoreUrl":"","wxShowMoreUrl":"","rightShowMoreUrl":"","wxRightShowMoreUrl":"","data":[{"title":"珍本拍卖","imgUrl":"https://img0.kfzimg.com/operation/4b/e7/4be7d7aabe1d8188411e178c60fb4651.png","params":{"url":"http://m.kongfz.cn/dijia/","linkType":"pmZhenben"},"linkUrl":"https://m.kongfz.cn/zhenben/","subTitle":"古籍善本","wxLinkUrl":"/pages/pmlist/pmlist?auctionArea=1","miniLinkUrl":{"wxLinkUrl":"/pmpages/list/list?listType=zhenben","bdLinkUrl":"","ttLinkUrl":"","aliLinkUrl":""}},{"title":"大众拍卖","imgUrl":"https://img0.kfzimg.com/operation/2a/f0/2af0cd06e0886d1af2ec3419d468415f.png","params":{"url":"http://m.kongfz.cn/dazhong/","linkType":"pmDazhong"},"linkUrl":"https://m.kongfz.cn/dazhong/","subTitle":"大家都在拍","wxLinkUrl":"/pages/pmlist/pmlist?auctionArea=2","miniLinkUrl":{"wxLinkUrl":"/pmpages/list/list?listType=dazhong","bdLinkUrl":"","ttLinkUrl":"","aliLinkUrl":""}}],"params":null},{"confId":"24213","sycModuleId":"0","style":"9","showStyle":"1","dataId":"101","status":2,"startTime":"2022/07/05 17:00:00","endTime":"","order":"6","name":"","subname":"","count":0,"showMoreType":"0","rightShowMoreType":"1","showMoreUrl":"","wxShowMoreUrl":"","rightShowMoreUrl":"","wxRightShowMoreUrl":"","data":[],"params":{"rLinkType":"activity","rurl":"http://pmgs.kongfz.com/"}},{"confId":"9886","sycModuleId":"3","style":"5","showStyle":"1","dataId":"24","status":2,"startTime":"2018/12/19 20:00:34","endTime":"","order":"9","name":"好书推荐","subname":"","count":0,"showMoreType":"0","rightShowMoreType":"1","showMoreUrl":"","wxShowMoreUrl":"","rightShowMoreUrl":"https://m.kongfz.com/recommend/3/","wxRightShowMoreUrl":"/pages/recommend/recommend?moduleid=3&title=好书推荐","data":[{"subTitle":"","subModuleId":"3","data":[{"mid":"58218399","isbn":"9787533970055","itemName":"世说俗谈","author":"刘勃","press":"浙江文艺出版社","pubDate":"2023-01","binding":"其他","contentIntroduction":"《世说俗谈》是文史作家刘勃解读《世说新语》的历史随笔。刘勃以讲段子的形式来趣味解读《世说新语》中各种","price":"18.48","imgUrl":"https://booklibimg.kfzimg.com/data/book_lib_img_v2/user/2/8a9b/8a9b9dc2db462789218dda426edea585_0_2_140_140.jpg"},{"mid":"28789592","isbn":"9787100216425","itemName":"启蒙运动的生意：《百科全书》出版史（1775&mdash;1800）","author":"【美】罗伯特·达恩顿","press":"商务印书馆","pubDate":"2023-1","binding":"精装","contentIntroduction":"本书为著名欧洲文化史家罗伯特•达恩顿的代表作之一。它以纳沙泰尔公司的数万份档案材料为基础，详细研究论","price":"64.00","imgUrl":"https://booklibimg.kfzimg.com/data/book_lib_img_v2/user/2/8188/81880232995f011046dbfa2fe1af9093_0_2_140_140.jpg"},{"mid":"26641191","isbn":"9787553817354","itemName":"王阳明的智慧","author":"孙钦香  著；吴震","press":"岳麓书社","pubDate":"2023-01","binding":"精装","contentIntroduction":"王阳明是中国历史上极为重要的思想家，他的“心即理”“知行合一”“致良知”“万物一体”等主张，不仅影响","price":"31.00","imgUrl":"https://booklibimg.kfzimg.com/data/book_lib_img_v2/user/2/9d73/9d7315919ace37a7365fe6a4f032c29d_0_2_140_140.jpg"},{"mid":"28880872","isbn":"9787542676139","itemName":"哈德良回忆录","author":"[法]玛格丽特·尤瑟纳尔","press":"上海三联书店","pubDate":"2023-01","binding":"其他","contentIntroduction":"（法）玛格丽特•尤瑟纳尔（MargueriteYourcenar,1903-1987），法语小说家、","price":"35.00","imgUrl":"https://booklibimg.kfzimg.com/data/book_lib_img_v2/user/2/0735/07355c95048ebf7f999d42930015a527_0_2_140_140.jpg"},{"mid":"64173233","isbn":"9787201190297","itemName":"九十岁的一年：《查令十字街84号》编剧的90岁日记","author":"杨凌峰  译者；[英]詹姆斯·罗斯-埃文斯","press":"天津人民出版社","pubDate":"2023-01","binding":"精装","contentIntroduction":"当盛年不再，变老意味着什么？“今天，我迎来了自己九十岁的生日，但还有太多的东西有待发现。”2017","price":"23.78","imgUrl":"https://booklibimg.kfzimg.com/data/book_lib_img_v2/user/2/c8a0/c8a0ca5e53fdafe3b95f0f5898efc422_0_2_140_140.jpg"},{"mid":"38079513","isbn":"9787301334713","itemName":"史学原理","author":"【英】柯林武德","press":"北京大学出版社","pubDate":"2023-1","binding":"","contentIntroduction":"柯林武德被誉为20世纪最著名的历史哲学家之一，其遗作《历史的观念》为其赢得了无限声誉。而《史学原理》","price":"38.61","imgUrl":"https://booklibimg.kfzimg.com/data/book_lib_img_v2/user/2/2a59/2a59327c444f19d9b37a1bd6571c0108_0_2_140_140.jpg"},{"mid":"65990786","isbn":"9787541164446","itemName":"春分秋分","author":"陈潇 后浪  译 者；[法]西里尔·佩德罗萨  编绘","press":"四川文艺出版社","pubDate":"2016-12","binding":"其他","contentIntroduction":"春分秋分这两天，白天和夜晚一样长，世界在光明和黑暗之间找到了完美的平衡，但这种平衡转瞬即逝，如同我们","price":"68.31","imgUrl":"https://booklibimg.kfzimg.com/data/book_lib_img_v2/user/2/1547/15477bb9470f865c25bc392be9a632fc_0_2_140_140.jpg"},{"mid":"38464009","isbn":"9787559854544","itemName":"小说的细节：从简&middot;奥斯丁到石黑一雄","author":"黄昱宁  著；铸刻文化  出品","press":"广西师范大学出版社","pubDate":"2023-01","binding":"其他","contentIntroduction":"本书是一部文学评论集，聚焦二十余位世界级知名作家，其中既有简·奥斯丁、大仲马、福楼拜、狄更斯这样的经","price":"24.50","imgUrl":"https://booklibimg.kfzimg.com/data/book_lib_img_v2/user/2/c7f1/c7f190e9b7d91fb3bf81859e64606a8f_0_2_140_140.jpg"},{"mid":"30128598","isbn":"9787020173532","itemName":"如英","author":"常小琥","press":"人民文学出版社","pubDate":"2023-1","binding":"","contentIntroduction":"80后实力派作家常小琥继《琴腔》《收山》后又一部长篇力作，以醇厚而洒脱的京味笔调，重绘原生城市地图，","price":"28.39","imgUrl":"https://booklibimg.kfzimg.com/data/book_lib_img_v2/user/2/452e/452eb4b8c6e5b9918080ab53435735e6_0_2_140_140.jpg"},{"mid":"26833559","isbn":"9787108074478","itemName":"俄罗斯文学的黄金世纪：从普希金到契诃夫","author":"张建华","press":"生活·读书·新知三联书店","pubDate":"2023-2","binding":"","contentIntroduction":"落后西欧文学至少100年的“晚生子”，如何实现逆袭？为什么俄罗斯文学有动人心魄的力量？是什么","price":"48.00","imgUrl":"https://booklibimg.kfzimg.com/data/book_lib_img_v2/user/2/e200/e20093048944e2d753e091b3a88c2b82_0_2_140_140.jpg"},{"mid":"42192957","isbn":"9787576021905","itemName":"人类学家如何写作：民族志阅读指南（薄荷实验）","author":"胡安·瓦德尔  著；刘月  译；[英]帕洛玛·盖伊·布拉斯科","press":"华东师范大学出版社","pubDate":"2022-11","binding":"平装","contentIntroduction":"为什么两位研究兴趣不同的人类学家要写这样一本阅读指南？因为通常没有人教读者如何阅读民族志，而是指望","price":"34.30","imgUrl":"https://booklibimg.kfzimg.com/data/book_lib_img_v2/user/2/c4cc/c4cc8d9a5f861e0d7c99cdf96d207218_0_2_140_140.jpg"},{"mid":"51023360","isbn":"9787542679000","itemName":"进步知识分子的死与生：两次大战间的维也纳新哲学与石里克的遇害","author":"[英]大卫·埃德蒙兹  著；理想国  出品","press":"上海三联书店","pubDate":"2023-01","binding":"其他","contentIntroduction":"“如果一座城市能产生弗洛伊德、维特根斯坦、马勒、勋伯格、波普尔、哈耶克、克里姆特、卢斯——和希特勒—","price":"30.00","imgUrl":"https://booklibimg.kfzimg.com/data/book_lib_img_v2/user/2/ad78/ad7808fda821063525294db2880d17bc_0_2_140_140.jpg"}],"pager":{"total":3002,"currentPage":1,"totalPage":251}}],"params":{"linkType":"bookrecommend","rLinkType":"bookrecommend"},"appDisplay":"isbn","bqList":[]}],"pager":{"total":21,"currentPage":2,"pageSize":3,"totalPage":7}},"errCode":"","errInfo":"","errType":"","message":""}'
    str1 = str.encode('utf-8')
    str2 = str1.decode('utf-8')
    str = '''
    
    为什么俄罗斯文学有动人心魄的力量？
    
    '''
    try:
        data_json = json.loads(str2.strip())
        print(data_json)
    except json.JSONDecodeError:
        print("JSON DECODE ERROR 2")
        print(str2)
