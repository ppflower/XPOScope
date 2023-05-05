# import os
# import re
#
# import socket
# import config
# from multiprocessing import Process, Pool
#
# pids = []
#
#
# def run_test1():
#     path = config.PAGE_TEXT_PATH + "opt.txt"
#     with open(path, "a") as f:
#         f.write("18 18\n")
#
#
# def run_test2():
#     temp=get_last_opt_page_count()
#     print(temp)
#
# def get_last_opt_page_count():
#     opt_path = config.PAGE_TEXT_PATH + "opt.txt"
#     with open(opt_path) as f:
#         opt_page_list = f.readlines()
#     last_opt_page = opt_page_list[-1]
#     last_opt_page = re.sub('\n', "", last_opt_page)
#     res = last_opt_page.split(" ")
#     return res[1]
#
# if __name__ == "__main__":
#     # pool = Pool(2)
#     # pool.apply_async(run_test2)
#     # pool.apply_async(run_test1)
#     # pool.close()
#     # pool.join()
#     hostname=socket.gethostname()
#     host=socket.gethostbyname(hostname)
#     print(host)
import asyncio
import os
import re
import time
import config


def a(temp):
    temp["name"] = "yyt"


def read_page_text(opt_page_count):
    page_file_path = config.PAGE_TEXT_PATH + opt_page_count + ".txt"
    res = []
    with open(page_file_path, 'r', encoding='utf-8') as f:
        dump_strs = f.readlines()
        f.close()
    for dump_str in dump_strs:
        new_str = re.sub('\n', "", dump_str)
        res.append(new_str)
    return res


def write_last_opt(opt_count):
    opt_file_path = config.PAGE_TEXT_PATH + "opt.txt"
    with open(opt_file_path, 'w', encoding='utf-8') as f:
        f.write(opt_count)
        f.flush()
    f.close()


def get_last_opt():
    opt_path = config.PAGE_TEXT_PATH + "opt.txt"
    if not os.path.exists(opt_path):
        return -1
    with open(opt_path) as f:
        last_opt = f.read()
        f.close()
    if last_opt == '':
        return -1
    print(type(last_opt))
    return last_opt


if __name__ == "__main__":
    # page_index_urls_map = {'0': [
    #     'https://opapi-ol.sns.sohu.com/sns-opapi/configuration/get?flyer=1671617540817&appid=330008&app_key_vs=1.0.0&sig=882d65cc8963c692b44dcf6afb7c3ed2'],
    #     '3': [
    #         'https://cs-ol.sns.sohu.com/circle/feed/ranklist/v20?circle_id=826522127825056896&count=10&tpl=1%2C2%2C3%2C4&stpl=1%2C2%2C3%2C4%2C7%2C9&flyer=1671617562915&appid=330008&app_key_vs=1.0.0&sig=a298b6175ee6f01a125fc6451e902af0',
    #         'https://cs-ol.sns.sohu.com/330008/v8/circle/show?circle_id=826522127825056896&flyer=1671617563143&appid=330008&app_key_vs=1.0.0&sig=8e71e6b7e00748cafff109c5ac7b410b'],
    #     '7': [
    #         'https://cs-ol.sns.sohu.com/circle/secondhand/market/v20?circle_id=826522127825056896&flyer=1671617586966&appid=330008&app_key_vs=1.0.0&sig=9b2464b5bacb8048a226e5401f76385a'],
    #     '11': [
    #         'https://cs-ol.sns.sohu.com/330008/v7/feeds/show?feed_id=981354323776835328&flyer=1671617614968&appid=330008&app_key_vs=1.0.0&sig=91ed84a946e44bf5bb2baa526d096b09'],
    #     '13': [
    #         'https://cs-ol.sns.sohu.com/330008/v7/feeds/show?feed_id=979246510757843200&flyer=1671617627262&appid=330008&app_key_vs=1.0.0&sig=0f134f7865f41d582ef8b2d2507f1b05'],
    #     '17': [
    #         'https://cs-ol.sns.sohu.com/330008/v8/circle/feed/list?circle_id=826522127825056896&list_type=2&count=10&score=0&tpl=1%2C2%2C3%2C4&stpl=1%2C2%2C3%2C4%2C7%2C9&board_id=836406669427815936&flyer=1671617653203&appid=330008&app_key_vs=1.0.0&sig=21c2a933f2d6ce01b019f9d6f60ed846'],
    #     '19': [
    #         'https://opapi-ol.sns.sohu.com/sns-opapi/configuration/get?flyer=1671617664606&appid=330008&app_key_vs=1.0.0&sig=fd788a7188fe6af55291ccc3eff76378',
    #         'https://cs-ol.sns.sohu.com/330008/v8/userapi/user/show'], '20': [
    #         'https://cs-ol.sns.sohu.com/circle/feed/ranklist/v20?circle_id=826522127825056896&count=10&tpl=1%2C2%2C3%2C4&stpl=1%2C2%2C3%2C4%2C7%2C9&flyer=1671617675464&appid=330008&app_key_vs=1.0.0&sig=c79064d3462c5b9f92f98d05bfab8b7b',
    #         'https://cs-ol.sns.sohu.com/330008/v8/circle/show?circle_id=826522127825056896&flyer=1671617675753&appid=330008&app_key_vs=1.0.0&sig=1e434d0883ccf7fb349466f019a6f7cf']}
    # url_privacy_tuples_map = {
    #     'https://opapi-ol.sns.sohu.com/sns-opapi/configuration/get?flyer=1671617540817&appid=330008&app_key_vs=1.0.0&sig=882d65cc8963c692b44dcf6afb7c3ed2': [
    #         ('name', '点赞'), ('name', '大笑'), ('name', '吃惊'), ('name', '安慰'), ('name', '狗头'), ('name', '大黄脸'),
    #         ('name', '福yǒuyōu第一弹'), ('name', '纯文字表情包'), ('name', '沙雕行为的日常'), ('name', '猫咪表情包'),
    #         ('name', 'Charles的233语录'), ('name', '漫画风表情'), ('name', '是憨憨啊'), ('name', 'Charles新春特辑')],
    #     'https://cs-ol.sns.sohu.com/circle/feed/ranklist/v20?circle_id=826522127825056896&count=10&tpl=1%2C2%2C3%2C4&stpl=1%2C2%2C3%2C4%2C7%2C9&flyer=1671617562915&appid=330008&app_key_vs=1.0.0&sig=a298b6175ee6f01a125fc6451e902af0': [
    #         ('sex', 1), ('souceAppName', ''), ('userName', '踏实的明珠'), ('userId', '605441265022111232'),
    #         ('circleName', '上海大学'), ('height', 600), ('sex', 3), ('souceAppName', ''), ('userName', '强悍的岳灵珊'),
    #         ('userId', '605441265022111232'), ('circleName', '上海大学'), ('height', 600)],
    #     'https://cs-ol.sns.sohu.com/330008/v8/circle/show?circle_id=826522127825056896&flyer=1671617563143&appid=330008&app_key_vs=1.0.0&sig=8e71e6b7e00748cafff109c5ac7b410b': [
    #         ('userName', '上海大学表白墙'), ('userId', '930137545491297280'), ('circleName', '上海大学'), ('userName', '踏实的明珠'),
    #         ('userId', '605441265022111232'), ('boardName', '树洞'), ('boardName', '卖室友'), ('boardName', '一周CP打卡'),
    #         ('boardName', '嘉定'), ('boardName', '社团组织招新'), ('boardName', '选课排雷'), ('height', 600),
    #         ('userName', '上海大学表白墙'), ('userId', '930137545491297280'), ('userName', '上大福利墙（迎新版'),
    #         ('userId', '937519663385098880'), ('userName', '狐友1667102837070'), ('userId', '937531112903883648'),
    #         ('userName', '上海大学表白墙'), ('userId', '930137545491297280')],
    #     'https://cs-ol.sns.sohu.com/circle/secondhand/market/v20?circle_id=826522127825056896&flyer=1671617586966&appid=330008&app_key_vs=1.0.0&sig=9b2464b5bacb8048a226e5401f76385a': [
    #         ('circleName', '上海大学'), ('tabName', '推荐'), ('tabName', '转卖'), ('tabName', '求购'), ('tabName', '悬赏派单'),
    #         ('dealTypeName', '转卖'), ('fullDealTypeName', '闲置转卖'), ('categoryName', '书籍资料'), ('categoryName', '电子数码'),
    #         ('categoryName', '洗漱日化'), ('categoryName', '鞋包服饰'), ('categoryName', '票卡转让'), ('categoryName', '代步工具'),
    #         ('categoryName', '体育器材'), ('categoryName', '仙女集市'), ('categoryName', '食品零食'), ('categoryName', '学习用品'),
    #         ('categoryName', '电器家具'), ('categoryName', '其他'), ('dealTypeName', '求购'), ('fullDealTypeName', '闲置求购'),
    #         ('categoryName', '书籍资料'), ('categoryName', '电子数码'), ('categoryName', '洗漱日化'), ('categoryName', '代步工具'),
    #         ('categoryName', '鞋包服饰'), ('categoryName', '票卡转让'), ('categoryName', '体育器材'), ('categoryName', '仙女集市'),
    #         ('categoryName', '食品零食'), ('categoryName', '学习用品'), ('categoryName', '电器家具'), ('categoryName', '其他'),
    #         ('dealTypeName', '派单'), ('fullDealTypeName', '悬赏派单'), ('categoryName', '帮拿代取'), ('categoryName', '提问求助'),
    #         ('categoryName', '求租求借'), ('categoryName', '宿舍搬迁'), ('categoryName', '游戏代练'), ('categoryName', '其他服务'),
    #         ('campusName', '宝山校区'), ('campusName', '嘉定校区'), ('campusName', '延长校区'), ('campusName', '杨浦校区')],
    #     'https://cs-ol.sns.sohu.com/330008/v7/feeds/show?feed_id=981354323776835328&flyer=1671617614968&appid=330008&app_key_vs=1.0.0&sig=91ed84a946e44bf5bb2baa526d096b09': [
    #         ('sex', 1), ('souceAppName', ''), ('userName', '狐友166717812127904'), ('userId', '962734227600901248'),
    #         ('sourceRegion', '河南'), ('circleName', '上海大学'), ('height', 600)],
    #     'https://cs-ol.sns.sohu.com/330008/v7/feeds/show?feed_id=979246510757843200&flyer=1671617627262&appid=330008&app_key_vs=1.0.0&sig=0f134f7865f41d582ef8b2d2507f1b05': [
    #         ('sex', 1), ('souceAppName', ''), ('userName', '踏实的明珠'), ('userId', '605441265022111232'),
    #         ('sourceRegion', '上海'), ('circleName', '上海大学'), ('height', 600), ('name', '点赞'), ('name', '狗头'),
    #         ('name', '大笑'), ('name', '吃惊'), ('name', '安慰')],
    #     'https://cs-ol.sns.sohu.com/330008/v8/circle/feed/list?circle_id=826522127825056896&list_type=2&count=10&score=0&tpl=1%2C2%2C3%2C4&stpl=1%2C2%2C3%2C4%2C7%2C9&board_id=836406669427815936&flyer=1671617653203&appid=330008&app_key_vs=1.0.0&sig=21c2a933f2d6ce01b019f9d6f60ed846': [
    #         ('sex', 3), ('souceAppName', ''), ('userName', '强悍的岳灵珊'), ('userId', '605441265022111232'),
    #         ('circleName', '上海大学'), ('height', 600), ('sex', 1), ('souceAppName', ''), ('userName', '焦虑的田归农'),
    #         ('userId', '605441265022111232'), ('circleName', '上海大学'), ('height', 600), ('sex', 3), ('souceAppName', ''),
    #         ('userName', '耿直的玄难'), ('userId', '605441265022111232'), ('circleName', '上海大学'), ('height', 600),
    #         ('sex', 0), ('souceAppName', ''), ('userName', '虚弱的周颠'), ('userId', '605441265022111232'),
    #         ('circleName', '上海大学'), ('height', 600), ('sex', 1), ('souceAppName', ''), ('userName', '宽厚的林远图'),
    #         ('userId', '605441265022111232'), ('circleName', '上海大学'), ('height', 600), ('sex', 3), ('souceAppName', ''),
    #         ('userName', '高尚的张君宝'), ('userId', '605441265022111232'), ('circleName', '上海大学'), ('height', 600),
    #         ('sex', 1), ('souceAppName', ''), ('userName', '可爱的鲜于通'), ('userId', '605441265022111232'),
    #         ('circleName', '上海大学'), ('height', 600), ('sex', 0), ('souceAppName', ''), ('userName', '谦虚的贺老三'),
    #         ('userId', '605441265022111232'), ('circleName', '上海大学'), ('height', 600), ('name', '点赞'), ('name', '安慰'),
    #         ('sex', 1), ('souceAppName', ''), ('userName', '乐观的明珠'), ('userId', '605441265022111232'),
    #         ('circleName', '上海大学'), ('height', 600), ('sex', 1), ('souceAppName', ''), ('userName', '稳健的殷野王'),
    #         ('userId', '605441265022111232'), ('circleName', '上海大学'), ('height', 600)],
    #     'https://opapi-ol.sns.sohu.com/sns-opapi/configuration/get?flyer=1671617664606&appid=330008&app_key_vs=1.0.0&sig=fd788a7188fe6af55291ccc3eff76378': [
    #         ('name', '点赞'), ('name', '大笑'), ('name', '吃惊'), ('name', '安慰'), ('name', '狗头'), ('name', '大黄脸'),
    #         ('name', '福yǒuyōu第一弹'), ('name', '纯文字表情包'), ('name', '沙雕行为的日常'), ('name', '猫咪表情包'),
    #         ('name', 'Charles的233语录'), ('name', '漫画风表情'), ('name', '是憨憨啊'), ('name', 'Charles新春特辑')],
    #     'https://cs-ol.sns.sohu.com/330008/v8/userapi/user/show': [('userId', '978838604262609536'),
    #                                                                ('userName', '狐友167101770389302'), ('sex', 1),
    #                                                                ('createTime', '2022-12-14 19:35:03.894'),
    #                                                                ('updateTime', '2022-12-14 19:36:17.000')],
    #     'https://cs-ol.sns.sohu.com/circle/feed/ranklist/v20?circle_id=826522127825056896&count=10&tpl=1%2C2%2C3%2C4&stpl=1%2C2%2C3%2C4%2C7%2C9&flyer=1671617675464&appid=330008&app_key_vs=1.0.0&sig=c79064d3462c5b9f92f98d05bfab8b7b': [
    #         ('sex', 1), ('souceAppName', ''), ('userName', '踏实的明珠'), ('userId', '605441265022111232'),
    #         ('circleName', '上海大学'), ('height', 600), ('sex', 3), ('souceAppName', ''), ('userName', '强悍的岳灵珊'),
    #         ('userId', '605441265022111232'), ('circleName', '上海大学'), ('height', 600)],
    #     'https://cs-ol.sns.sohu.com/330008/v8/circle/show?circle_id=826522127825056896&flyer=1671617675753&appid=330008&app_key_vs=1.0.0&sig=1e434d0883ccf7fb349466f019a6f7cf': [
    #         ('userName', '上海大学表白墙'), ('userId', '930137545491297280'), ('circleName', '上海大学'), ('userName', '踏实的明珠'),
    #         ('userId', '605441265022111232'), ('boardName', '树洞'), ('boardName', '卖室友'), ('boardName', '一周CP打卡'),
    #         ('boardName', '嘉定'), ('boardName', '社团组织招新'), ('boardName', '选课排雷'), ('height', 600),
    #         ('userName', '上海大学表白墙'), ('userId', '930137545491297280'), ('userName', '上大福利墙（迎新版'),
    #         ('userId', '937519663385098880'), ('userName', '狐友1667102837070'), ('userId', '937531112903883648'),
    #         ('userName', '上海大学表白墙'), ('userId', '930137545491297280')]}
    # report_path = config.MINI_APP_LOG + "狐友Lite.txt"
    # with open(report_path, 'w') as f:
    #     for index in page_index_urls_map.keys():
    #         print("write" + index)
    #         f.write("Page " + str(index))
    #         f.write("\n")
    #         urls = page_index_urls_map[index]
    #         ui_text = read_page_text(index)
    #         print(ui_text)
    #         privacy_tuples = []
    #         for url in urls:
    #             if url not in url_privacy_tuples_map.keys():
    #                 continue
    #             for tup in url_privacy_tuples_map[url]:
    #                 if tup not in privacy_tuples and tup[1] != '':
    #                     privacy_tuples.append(tup)
    #         for idx in range(len(privacy_tuples)):
    #             if idx == len(privacy_tuples) - 1:
    #                 f.write(str(privacy_tuples[idx][0]) + " " + str(privacy_tuples[idx][1]))
    #             else:
    #                 f.write(str(privacy_tuples[idx][0]) + " " + str(privacy_tuples[idx][1]) + ",")
    #         f.write("\n")
    #         print(len(ui_text))
    #         for idx in range(len(ui_text)):
    #             if idx == len(ui_text) - 1:
    #                 f.write(str(ui_text[idx]))
    #             else:
    #                 f.write(str(ui_text[idx]) + ",")
    #         f.write("\n")
    #     f.flush()
    #     f.close()
    # write_last_opt(2)
    # print(get_last_opt())
    str = "'狐友Lite'"
    print(str)
    str = str.strip("'")
    print(str)
