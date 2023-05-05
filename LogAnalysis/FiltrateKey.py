import re
import requests
import codecs

# coding=UTF-8
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
    'longitude': ['longitude', 'lng'],
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
    'drinking', 'zodiac', 'constellation', 'race', 'religion','vip',
    'bodytype', 'hairlength', 'profession', 'citizen', 'habit', 'updateuser',
    'wish', 'user', 'student', 'task', 'employment']

shop_related_categories = [
    'shop', 'site', 'brand', 'sell', 'company', 'business', 'goods', 'bank', 'branch', 'banner',
    'bus', 'store', 'channel', 'principal', 'dept', 'project', 'wares', 'product', 'proper',
    'category'
]

no_inf_names = [
    'null', 'none', 'true', 'false', 'cn', 'com', '2000-01-01',
    'png', 'jpg', 'app', '[]', '['']', '全国', '---', '保密', '123456', "['4']"
]

flod_keys = ['font', 'vip', 'name', 'id', 'country', 'home', 'countries', 'shop', 'continent', 'code', 'display',
             'area', 'country', 'time', 'pictureheight', 'place', 'timestamp', 'group', 'state', 'occupation',
             'level', 'province', 'imageheight', 'job', 'location', 'vehicle', 'religion', 'favorite', 'experience',
             'titleheight', 'iconheight', 'app', 'brand', 'store', 'd&c', 'organization', 'age', 'year', 'old',
             'city', 'share_account_gray', 'tax', 'company', 'verify', 'image', 'service', 'balance', 'tpwd',
             'address_v2', 'externaladdress', 'addressV2', 'key_secret', 'region', 'bank', 'jianpin', 'map_address',
             'appkey', 'com.baidu.fb', 'com.baidu.vip', 'wishes', 'profession', 'price_family', 'default',
             'finger_print', 'ship_address', 'local', 'height', 'cities', 'employment', 'area', 'place',
             'freephone', 'distance', 'date', 'speed', 'district', 'zip', 'token', 'chinese', 'lineheight', 'park',
             'payment', 'music-web-config#wechat-mini-no-share-market', 'branch', 'link', 'productimgheight', 'geo',
             'effective', 'wish', 'kanban_birth','area',
             'constellation', 'index', 'office', 'loc_gcj02', 'imgheight', 'firstworkaddress', 'product', 'flag',
             'link',
             'clients', 'altitude', 'min_height', 'max_height', 'town', 'street', 'interest', 'share_user', 'bound',
             'verificationsystem', 'orderno', 't_', 'account', 'order_no', 'cardno', 'operationpwd', 'card_no',
             'trans_user', 'salary_n', 'tpl_user', 'food', 'health', 'clientfrom', 'family', 'customheight', 'benefit',
             'license', 'hotel_address', 'wap', 'reg_ip', 't_', 'official', 'body_type', 'comppassword',
             'expressaddress','cooperation_college']

confusion_keys = ['longitude', 'latitude', 'phone', 'address', 'weixin',
                  'account', 'mobile', 'geo', 'street', 'area', 'height', 'qq',
                  'pin', 'gender', 'sex', 'lat', 'lng', 'lon', 'user', 'home']

is_chiese_keys = ['address', 'school', 'area', 'street', 'distinct', 'gender', 'sex']
no_chiese_keys = ['mail', 'email', 'phone', 'mobile', 'longitude', 'latitude', 'password', 'birthday', 'income',
                  'expenses', 'ip']
my_infos = ['13952687168', '18138412378', '19167743750', '18080178034', '19121728675', '18586624118',
            '江湾', '松花江路', '202.120.234.126', '101.94.132.185', '202.120.234.248', '101.94.129.52',
            '101.94.128.152', '杨浦区', '国帆路', '交叉2号楼', '101.94.129.250', '101.94.134.114','202.120.235.226',
            '202.120.234.94','127.0.0.1','202.120.234.107','2001:da8:8001:7a82:5cce:cea3:a101:fb6b'
            ]

def is_my_info(key, val):
    for my_info in my_infos:
        if my_info in val:
            return True
    return False


def is_file_path(string):
    if re.match(r'^/(?:[^\\/:*?"<>|\r\n]+\\)*[^\\/:*?"<>|\r\n]*$', string):
        return True
    else:
        return False


def contains_chinese_characters(string):
    pattern = re.compile(r'[\u4e00-\u9fa5]')
    return bool(pattern.search(string))


def human_or_not(prkey):
    for human in human_related_categories:
        if prkey.lower() in human or human in prkey.lower():
            return True
    return False


def fold_or_not(key):
    if contains_chinese_characters(key):
        return True
    for flod_key in flod_keys:
        if flod_key in key or flod_key in find_central(key):
            return True
    return False


def delete_noinf_key(privacy_key, privacy_val):
    # print("当前key=={},val=={}".format(privacy_key, privacy_val))
    central_key = find_central(privacy_key)

    if privacy_val in privacy_key or privacy_key in privacy_val or privacy_val == '':
        return True

    if privacy_val in central_key or central_key in privacy_val:
        return True

    for is_chiese_key in is_chiese_keys:
        if is_chiese_key in central_key and not contains_chinese_characters(privacy_val):
            return True

    for no_chiese_key in no_chiese_keys:
        if no_chiese_key in central_key and contains_chinese_characters(privacy_val):
            return True

    for no_inf_name in no_inf_names:
        if no_inf_name in privacy_val.lower():
            return True

    if len(privacy_val) == 1:
        return True

    try:
        if 0 <= float(privacy_val) <= 10:
            return True
    except ValueError:
        nothing = False

    if 'height' in privacy_key.lower():
        if not (privacy_val.isdigit() and 150 < int(privacy_val) < 200):
            return True
    if 'weight' in privacy_key.lower():
        if 'kg' not in privacy_val:
            return True
    if 'weixin' in privacy_key.lower():
        if '*' in privacy_val:
            return True
    if 'ip' in privacy_key.lower():
        if '.' not in privacy_val:
            return True
    return False


def find_central(key):
    for title in privacy_set:
        for elem in privacy_set[title]:
            if key == elem:
                return title
    return key

