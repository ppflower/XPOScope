"""
判断流量中的字段是否为混淆，对于每个对象分别判断。
判断一个JSON对象为用户隐私的标准：
1、其中至少有一个字段与人强相关
2、其对应的字段名称包含User、Profile等关键词（？这一点不确定）
如果一个JSON对象被判定为用户相关的对象了，那么其所有子对象会被判定为用户相关类。

如果一条流量中返回了用户相关的对象，那么认为该流量信息相对敏感，考虑fuzz该流量
"""

from traffic_utils import parse_dependency, to_word_sequence_lower

privacy_set = {
    'birthday': [
        'birthday', 'birthdate', 'birth', 'dayofbirth', 'datebirth',
        'dateofbirth', 'dob'
    ],
    'birthmonth': ['birthmonth'],
    'birthyear': ['birthyear'],
    'birthplace': ['birthplace'],
    'user': ['user'],
    'username': ['realname', 'firstname', 'middlename', 'lastname', 'username', 'nickname'],
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
                if isinstance(obj[key], str) or isinstance(obj[key], list):
                    res.append((key, obj[key]))
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
    test_case = {
        "students": [
            {
                "name": ["yyt", "ls"],
                "gender": "1",
                "MobilePhone": "789"
            },
            {
                "name": "zs",
                "gender": "0",
                "phone": "012"
            }
        ],
        "phone": [
            "123",
            "456"
        ]
    }

    # test_case = [{"display_name": "Lee"}, {"mail": "hn@fudan.edu.cn"}]
    detect_res = detect_privacy_keys(test_case)
    dict = {}
    for dr in detect_res:
        key = dr[0]
        if key in dict:
            if isinstance(dr[1], str):
                dict[key].append(dr[1])
            if isinstance(dr[1], list):
                dict[key].extend(dr[1])
        else:
            dict[key] = []
            if isinstance(dr[1], str):
                dict[key].append(dr[1])
            if isinstance(dr[1], list):
                dict[key].extend(dr[1])

    print(dict)

    pass
