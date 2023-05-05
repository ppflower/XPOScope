# coding=UTF-8
def is_informative(var):
    if isinstance(var, int) or isinstance(var, str) or isinstance(var, float):
        return True
    return False

def has_information(var):
    if is_number(var) or var.isalnum():
        return True
    return False

def is_number(var):
    try:
        complex(var)
    except ValueError:
        return False
    return True


def exactly_matched(privacy_val, ui_strs):
    if is_informative(privacy_val):
        # url过滤
        if privacy_val.startswith('https') or privacy_val.startswith('http'):
            return True
        if privacy_val in ui_strs or str(privacy_val) in ui_strs:
            return True
        else:
            for ui_str in ui_strs:
                if privacy_val in ui_str:
                    return True
            return False
    return False
