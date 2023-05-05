import os
import json
import re
from xmlrpc.client import boolean
import requests

from mitmproxy import ctx
from nltk import word_tokenize, pos_tag
from nltk.stem import WordNetLemmatizer
from nltk.corpus import wordnet as wn
from nltk.parse.corenlp import CoreNLPDependencyParser

is_debugging = False

dependency_parser = CoreNLPDependencyParser(url='http://localhost:9000')
dependency_recorder = {}  # 记录已经解析过的词句，加快速度

"""Nlp related functions"""


def to_dict(input_str):
    try:
        obj = json.loads(input_str)
        return obj
    except:
        return None


def extract_words(long_word):
    return re.findall(r'[a-z]{2,}|[A-Z][a-z]+', long_word)


def extract_words_lower(long_word):
    wl = extract_words(long_word)
    return [i.lower() for i in wl]


# 提取field中的单词，并做词形还原处理，返回单词列表
def to_word_sequence_lower(field_or_class):
    word_seq = ' '.join(extract_words_lower(field_or_class))
    tokens = word_tokenize(word_seq)
    tagged_sent = pos_tag(tokens)

    wnl = WordNetLemmatizer()
    lemmas_sent = []
    for tag in tagged_sent:
        wordnet_pos = get_wordnet_pos(tag[1]) or wn.NOUN
        lemmas_sent.append(wnl.lemmatize(tag[0], pos=wordnet_pos))  # 词形还原
    return lemmas_sent


def get_wordnet_pos(tag):
    if tag.startswith('J'):
        return wn.ADJ
    elif tag.startswith('V'):
        return wn.VERB
    elif tag.startswith('N'):
        return wn.NOUN
    elif tag.startswith('R'):
        return wn.ADV
    else:
        return None


def parse_dependency(key):
    input_string = ' '.join(extract_words_lower(key))
    if not input_string:
        return []
    if input_string not in dependency_recorder:
        parses, = dependency_parser.raw_parse(input_string)
        dependency_recorder[input_string] = list(parses.triples())
    return dependency_recorder[input_string]


"""File system util"""


def write_content_to_file(dir_path, file_name, content):
    if not os.path.exists(dir_path):
        os.makedirs(dir_path)

    file_path = os.path.join(dir_path, file_name)
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(str(content))


def append_content_to_file(file_path, content):
    with open(file_path, 'a', encoding='utf-8') as f:
        f.write(content)
        f.write("\n")


def listdir_path(root_dir):
    file_names = os.listdir(root_dir)
    res = []
    for file_name in file_names:
        res.append(os.path.join(root_dir, file_name))
    return res


"""Data analysis utils"""


def find_difference_of_privacy(src_data, dst_data):
    # To find a difference about privacy related item
    # Do not care about other differences
    if isinstance(src_data, dict) and isinstance(dst_data, dict):
        for key in dst_data:
            judge_res = judge_key(key)
            if key not in src_data:
                if judge_res[1]:  # current key is a privacy related item
                    # if not is_debugging:
                    #     ctx.log.error("隐私项为" + key)  # ############################# 查看中间结果
                    # print("隐私项为" + key)  # ############################# 查看中间结果
                    return True, key
            elif dst_data[key] != src_data[key]:
                if judge_res[1]:  # current key is a privacy related item
                    # if not is_debugging:
                    #     ctx.log.error("隐私项为" + key)  # ############################# 查看中间结果
                    # print("隐私项为" + key, dst_data[key], src_data[key])  # ############################# 查看中间结果
                    return True, key
                else:
                    is_different, difference = find_difference_of_privacy(src_data[key], dst_data[key])
                    if is_different:
                        return True, difference
    elif isinstance(src_data, list) and isinstance(dst_data, list):
        # Assume data in src_list and dst_list is the same type
        for index, dst_item in enumerate(dst_data):
            if index < len(src_data):
                is_different, difference = find_difference_of_privacy(src_data[index], dst_item)
                if is_different:
                    return True, difference
            else:
                # dst_data includes more private data than src_data
                detected_privacy_list = detect_privacy(dst_item)
                if bool(detected_privacy_list):
                    privacy_diff_info = "list item, include " + str(detected_privacy_list)
                    return bool(detected_privacy_list), privacy_diff_info
                break  # Assume that all items in a list have the same structure
    return False, None


def detect_privacy(response_content: dict):
    # 遍历一个json对象的field以及其子对象的field，从中识别出
    # ctx.log.warn("Response Content")
    # ctx.log.info(response_content)
    detect_res = detect_privacy_keys(response_content)
    # ctx.log.info(detect_res)
    # res = []  # 不重复的隐私项
    # for privacy_key, privacy_value in detect_res:
    #     ctx.log.info(privacy_key + ": " + privacy_value)
    # if privacy_key not in res:
    #     tmp = [privacy_value]
    #     res.append((privacy_key, tmp))
    # if privacy_key in res:

    return detect_res


def compare_query(original_query: dict, replayed_query: dict):
    for key in original_query:
        if original_query[key] != replayed_query[key]:
            query_diff = key + ": " + str(original_query[key]) + " -> " + str(replayed_query[key])
            if not is_debugging:
                ctx.log.warn("Query diff: " + query_diff)
            return query_diff
    if not is_debugging:
        ctx.log.error("Bug, query all the same!!!!!!")
    return None


def compare_form(original_form: dict, replayed_form: dict):
    for key in original_form:
        if original_form[key] != replayed_form[key]:
            form_diff = key + ": " + str(original_form[key]) + " -> " + str(replayed_form[key])
            if not is_debugging:
                ctx.log.warn("Form diff: " + form_diff)
            return form_diff
    if not is_debugging:
        ctx.log.error("Bug, form all the same!!!!!!")
    return None


def compare_json(original_json: dict, replayed_json: dict):
    for key in original_json:
        if original_json[key] != replayed_json[key]:
            if isinstance(original_json[key], dict):
                return compare_json(original_json[key], replayed_json[key])
            else:
                json_diff = key + ": " + str(original_json[key]) + " -> " + str(replayed_json[key])
                return json_diff
    return "Bug, implementation error!"


def recheck_false_positive(res_dir_path):
    """
    Current false positive result mainly come from two aspects:
    1. We failed to generate meaningful values for params.
      For example, when we try to mutate the param language, the original value
      zh_CN is mutated to zg_CN, which has no practical meaning.
      Sometimes the server-side api may set the default language to en_US. As a
       result, some results are the same.
    2. In some traffic, the results may have a relation with specific time
      because the status of server-side data may change with time. If there are
      too much params to mutate, the process may take a while and this will have
      an effect.
    """
    res = {}
    app_id_dir_path_list = listdir_path(res_dir_path)
    for app_id_dir_path in app_id_dir_path_list:
        if os.path.isfile(app_id_dir_path):
            continue
        app_id = os.path.basename(app_id_dir_path)
        res[app_id] = {}
        request_url_path_list = listdir_path(app_id_dir_path)
        for request_url_path in request_url_path_list:
            request_url = os.path.basename(request_url_path).replace("]", "/")
            if os.path.isfile(request_url_path):
                continue
            diff_file_paths = listdir_path(request_url_path)
            remaining_res = filter_fp_files(diff_file_paths)
            if remaining_res:
                res[app_id][request_url] = remaining_res
    # for app_id in res:
    #     print("[", app_id, "]")
    #     for request_url in res[app_id]:
    #         print("  ", request_url)
    #         print("    ", res[app_id][request_url])
    #     print()
    return res


def filter_fp_files(file_path_list):
    if len(file_path_list) == 2:
        return
    file_path_list.sort()
    files_in_group = {}
    filtered_files = {}
    for file_path in file_path_list:
        file_name = os.path.basename(file_path)
        if file_name.startswith("original_"):
            continue
        param_key = file_name.split(": ")[0]
        if param_key not in files_in_group:
            files_in_group[param_key] = []
            filtered_files[param_key] = []
        files_in_group[param_key].append(file_path)
    """start filter"""
    for param_key, file_paths in files_in_group.items():
        for i, file_path0 in enumerate(file_paths):
            for j, file_path1 in enumerate(file_paths[i + 1:]):
                traffic0 = json.load(open(file_path0))
                traffic1 = json.load(open(file_path1))
                is_different, difference = find_difference_of_privacy(traffic0, traffic1)
                if not is_different:
                    if os.path.basename(file_path0) not in filtered_files[param_key]:
                        filtered_files[param_key].append(os.path.basename(file_path0))
                    if os.path.basename(file_path1) not in filtered_files[param_key]:
                        filtered_files[param_key].append(os.path.basename(file_path1))
    remaining_files = {}
    for param_key, file_paths in files_in_group.items():
        for file_path in file_paths:
            if os.path.basename(file_path) not in filtered_files[param_key]:
                if param_key not in remaining_files:
                    remaining_files[param_key] = []
                remaining_files[param_key].append(os.path.basename(file_path))
    return remaining_files


def get_core_word(word_seq: str):
    return None
    pass


def get_relatedness(seq0, seq1):
    str0 = "_".join(to_word_sequence_lower(seq0))
    str1 = "_".join(to_word_sequence_lower(seq1))
    request_url = 'https://api.conceptnet.io/relatedness?node1=/c/en/{}&node2=/c/en/{}'.format(str0, str1)
    print(request_url)
    res = requests.get(request_url).json()["value"]
    return res


relatedness_threshold = 0.3


def filter_privacy_unrelated_params(remaining_res):
    """
    :param remaining_res: results remained after filtering fp
    filter out those request that contains privacy related params
    """
    privacy_related_res = {}
    privacy_related_params = []
    for app_id in remaining_res:
        privacy_related_res[app_id] = {}
        for request_url in remaining_res[app_id]:
            contains_privacy = False
            for param_key in remaining_res[app_id][request_url]:
                p_key, judge_res = judge_key(param_key)
                if judge_res:
                    contains_privacy = True
                    break
            if contains_privacy:
                privacy_related_res[app_id][request_url] = remaining_res[app_id][request_url]
                for param_key in remaining_res[app_id][request_url]:
                    if param_key not in privacy_related_params:
                        privacy_related_params.append(param_key)
    for app_id in privacy_related_res:
        print("[", app_id, "]")
        for request_url in privacy_related_res[app_id]:
            print("  ", request_url)
            print("    ", privacy_related_res[app_id][request_url])
        print()

    import sys
    sys.exit()
    """下面是扩展一些和可能隐私相关的字段"""
    extended_res = {}
    for app_id in remaining_res:
        extended_res[app_id] = {}
        for request_url in remaining_res[app_id]:
            if request_url in privacy_related_res[app_id]:
                continue
            for param_key in remaining_res[app_id][request_url]:
                """
                判断和已经出现过的词语的关联度，如果关联度超过一个阈值
                """
                for privacy_related_param in privacy_related_params:
                    relatedness = get_relatedness(privacy_related_param, param_key)
                    if (relatedness - relatedness_threshold) > 0:
                        if request_url not in extended_res[app_id]:
                            extended_res[app_id][request_url] = {}
                        extended_res[app_id][request_url][param_key] = remaining_res[app_id][request_url][param_key]
    print(extended_res)


"""
Privacy recognizer
"""

privacy_set = {
    'birthday': [
        'birthday', 'birthdate', 'birth', 'dayofbirth', 'datebirth',
        'dateofbirth', 'dob'
    ],
    'birthmonth': ['birthmonth'],
    'birthyear': ['birthyear'],
    'birthplace': ['birthplace'],
    'user': ['user'],
    'username': ['realname', 'firstname', 'middlename', 'lastname', 'username'],
    'age': ['age', 'agerange', 'agemaxage', 'maxage', 'agemax', 'minage', 'agemin'],
    'school': ['academy', 'school', 'university', 'college', 'universityname'],
    'job': [
        'occupation', 'career', 'job', 'profession', 'work', 'profession',
        'expertise'
    ],
    'income': [
        'income', 'videoincome', 'annualincome', 'benefit', 'salary', 'wage',
        'earnings'
    ],
    'marriage': ['marriage', 'marry'],
    'bloodtype': ['bloodtype'],
    'wantchild': ['wantchild'],
    'smoking': ['smoking'],
    'drinking': ['drinking'],
    'vip': ['vip'],
    'name': ['name'],
    'height': ['height'],
    'weight': ['weight'],
    'password': [
        'passphrase', 'passcode', 'pwd', 'userpassword', 'forgotpassword',
        'resetpassword', 'userpwd', 'passwd', 'passport', 'password', 'pass',
        'newpassword', 'confirmpassword'
    ],
    'phone': [
        'phoneno', 'homephone', 'smartphones', 'mobile', 'telephony',
        'telephone', 'phone', 'phonecode', 'telphone', 'phonebrand',
        'phonenumber', 'bindphone', 'cellphone', 'mobileno', 'workphone',
        'cell'
    ],
    'mail': [
        'contactemail', 'useremail', 'mailbox', 'email', 'emailaddress',
        'memberemail', 'mail', 'voicemail'
    ],
    'longitude': ['longitude', 'lon', 'lng', 'long'],
    'latitude': ['latitude', 'lat'],
    'geo': [
        'gps', 'location', 'geolocation', 'lastlocation', 'geoplace', 'geoip',
        'geopoint',
    ],
    'ip': ['ipaddr', 'partnership', 'ipaddress', 'ip', 'clientip'],
    'address': ['address', 'addrdetail'],
    'distance': ['distance'],
    'license': ['license', 'licensing'],
    'key_secret': ['appkey', 'authkey', 'secretkey', 'clientsecret'],
    'deviceid': ['deviceid'],
    'androidid': ['androidid'],
    'imei': ['imei'],
    'pin': ['pin', 'pincode'],
    'number': ['orderno', 'cardno'],
    'invitecode': ['invitecode', 'invitationcode'],
    'validationcode': ['validationcode', 'verifycode'],
    'fbid': ['fbid', 'facebookid', 'facebook', 'fb', 'fbuid'],
    'twitterid': ['twitterid', 'twitter'],
    'twitterurl': ['twitterurl'],
    'weixin': ['weixin', 'wechat'],
    'qq': ['qq'],
    'whatsapp': ['whatsapp'],
    'paypal': ['paypal'],
    'icq': ['icq'],
    'amazon': ['amazon'],
    'baidu': ['baidu'],
    'instagram': ['instagram'],
    'microsoft': ['microsoft'],
    'telegram': ['telegram'],
    'tiktok': ['tiktok'],
    'youtube': ['youtube'],
    'linkedin': ['linkedin'],
    'weibo': ['weibo'],
    'googleaccount': ['googleaccount'],
    'account': ['account', 'subaccount', 'accountid'],
    'balance': ['balance'],

    'zodiac': ['zodiac'],
    'constellation': ['constellation'],
    'image': [
        'headpic', 'profilephoto', 'userpic', 'headphoto', 'profileimage',
        'profilepic', 'userphoto', 'headimgurl', 'headimage', 'userimage',
        'userimgs', 'profilepicture', 'headimg', 'imglist',
        'avatarurl', 'fbphoto', 'faceimg'
    ],
    'altitude': ['altitude'],
    'gender': ['sex', 'sexuality', 'gender', 'sexid'],
    'race': ['race', 'ethnicity'],
    'language': ['language', 'languagevalue', 'languages'],
    'color': ['haircolor', 'eyecolor'],
    'place': [
        'area', 'userarea', 'place', 'district', 'region', 'placename',
        'geoname', 'hometown'
    ],
    'continent': ['continent'],
    'country': ['nation', 'nationality', 'country'],
    'street': ['street', 'addressstreet', 'streetaddress'],
    'province': ['province'],
    'city': ['city', 'cityname', 'collectcity'],
    'collectunit': ['collectunit'],
    'checkresult': ['checkresult'],
    'town': ['town'],
    'company': [
        'companytitle', 'organization', 'organisation', 'division', 'company',
        'office'
    ],
    'religion': ['religion', 'faith', 'belief'],
    'zip': ['zip', 'zipcd', 'zipcode', 'postcode', 'postalcode'],
    'timezone': ['timezone', 'timezoneid'],
    'timestamp': [
        'expiretime', 'visittime', 'createtime', 'expirestime', 'expiredtime',
        'regtime', 'endtime', 'publishtime', 'arrivaltime', 'starttime',
        'invitetime', 'updatetime', 'logintime', 'lastlogin', 'lastonline', 'collectTime'
    ],
    'date': ['createdate', 'expirationdate'],
    'bodytype': ['bodytype'],
    'hairlength': ['hairlength'],
    'bank': ['bank', 'banking'],
    'profession': ['expertise', 'certification', 'certificate'],
    'citizen': ['citizenship', 'citizen'],
    'employment': ['employee', 'employment', 'employer'],
    'experience': ['education', 'training', 'experience'],
    'home': ['house', 'home', 'residence', 'residency'],
    'holder': ['accountholder', 'cardholder'],
    'finger_print': ['devicefingerprint', 'fingerprint'],
    'family': ['family', 'familyid'],
    'state': ['onlinestate', 'userstate', 'online', 'contactstatus'],
    'level': ['userlevel', 'level', 'viplevel', 'vipgrade'],
    'favorite': ['favorite', 'favorites'],
    'food': ['food', 'diet'],
    'vehicle': ['vehicle'],
    'membershiptype': ['membershiptype'],
    'reputation': ['reputation'],
    'appplatfrom': ['appplatfrom', 'devicetype', 'system', 'client'],
    'areacode':
        ['areacode', 'countrycode', 'provincecode', 'citycode', 'geocode'],
    'areaid': ['countryid', 'cityid', 'locationid', 'areaid', 'addressid'],
    'doorcode': ['doorcode'],
    'userid': ['loginid', 'loginuserid', 'useruuid', 'useridx', 'userid', 'uid'],  # 这里为了把我们的case包含进来做了一些调整
    'speed': ['speed'],
    'habit': ['habit'],
    'tax': ['tax', 'shippingtax'],
    'transaction': ['transaction', 'billpay', 'expense', 'payment'],
    'interest': ['interest'],
    'health': ['health'],
    'wish': ['wish'],
    'token': ['logintoken', 'facebooktoken', 'fbtoken', 'devicetoken']
}

human_related_categories = [
    'birthday', 'birthmonth', 'birthyear', 'birthplace', 'username', 'age',
    'school', 'job', 'income', 'marriage', 'bloodtype', 'wantchild', 'smoking',
    'drinking', 'vip', 'zodiac', 'constellation', 'gender', 'race', 'religion',
    'bodytype', 'hairlength', 'profession', 'citizen', 'userid', 'habit',
    'wish', 'user'
]

only_highly_sensitive = False

is_debug = True
# is_debug = False

"""
def profile_obj_judge(key_list):
    # 目前仅仅用key来判断
    key_res_list = analyze_keys(key_list)
    return 1, key_res_list
    # 暂时不要求必须与人相关
    # if include_human_related_privacy_item(key_res_list):
    #     return 1, key_res_list
    # return 0, None
"""


def detect_privacy_keys(content):
    # ctx.log.info("List:")
    key_res_list = analyze_obj(content)
    return key_res_list


def analyze_obj(obj):
    res = []
    if isinstance(obj, dict):
        for key in obj:
            # ctx.log.info(key)
            judge_res = judge_key(key)
            if judge_res[1]:
                if isinstance(obj[key], str) or isinstance(obj[key], float) or isinstance(obj[key], int) or isinstance(
                        obj[key], list):
                    res.append((key, obj[key]))
                elif isinstance(obj[key], boolean):
                    pass
                else:
                    res.extend(analyze_obj(obj[key]))
        for value in obj.values():
            res.extend(analyze_obj(value))
    elif isinstance(obj, list):
        for item in obj:
            res.extend(analyze_obj(item))
    return res


def judge_key(key):
    # 语法依存分析，判断是否关键词是否为核心词
    match_res = match_privacy_in_word_sequence(key)
    dp_res = privacy_dependence_analyze(key, match_res)
    return key, dp_res  # dp_res是隐私的类别
    pass


def privacy_dependence_analyze(key, match_res):
    # 对field或者class name短语进行依存关系分析，如果隐私词为核心词返回True
    if match_res[0]:  # 完全匹配
        return match_privacy_category(match_res[1][0])

    dependencies = parse_dependency(key)
    for privacy_item in match_res[1]:
        # 通过语义结构再滤掉一些FP
        is_privacy_field = False
        for dp in dependencies:
            if privacy_item in dp[0]:
                if dp[1] == 'compound':
                    is_privacy_field = True
                elif dp[1] == 'amod' or dp[1].startswith('nmod'):
                    # nummod 带来的误报较多
                    is_privacy_field = True
                elif dp[1] == 'dep':
                    is_privacy_field = True
                else:
                    is_privacy_field = False
                    break
            elif privacy_item in dp[2]:
                if is_debug:
                    pass
                    # ctx.log.warn('    [dp]' + privacy_item + str(dp))
                    # print('    [dp]' + privacy_item + str(dp))
                if dp[1] == 'obj' and dp[0][1] == 'VBN':
                    is_privacy_field = True
                else:
                    is_privacy_field = False
                    break

        if is_privacy_field:
            return match_privacy_category(privacy_item)

    return None


def match_privacy_category(word):
    for cate in privacy_set:
        if word in privacy_set[cate]:
            return cate
    return None


def match_privacy_in_word_sequence(field):
    # 返回值签名的1表示完全匹配，0表示非完全匹配
    # 返回值第一个参数表示完全匹配，比如confirm_password完全匹配上了confirmpassword这一项
    words = to_word_sequence_lower(field)
    full_word = ''.join(words)
    match_res = match_privacy(full_word)
    if match_res:
        return 1, [full_word]
    res = []
    for word in words:
        match_res = match_privacy(word)
        if match_res:
            res.append(word)
    return 0, res


def match_privacy(word):
    for cate in privacy_set:
        if word in privacy_set[cate]:
            return True
    return False


def include_human_related_privacy_item(key_res_list):
    for key_res in key_res_list:
        if key_res[0] and key_res[2] in human_related_categories:
            return True
    return False


if __name__ == "__main__":
    print(judge_key("education"))
