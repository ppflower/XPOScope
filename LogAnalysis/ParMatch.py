# coding=UTF-8
def edit_distance(str1, str2):
    import edit_distance
    sm = edit_distance.SequenceMatcher(str1, str2)
    return sm.distance()


def is_informative(var):
    if isinstance(var, int) or isinstance(var, str) or isinstance(var, float):
        return True
    return False


def partially_matched(privacy_val, ui_strs):
    if len(str(privacy_val)) == 0:
        return False, []

    if is_informative(privacy_val):
        distances = {}
        for each_ui_str in ui_strs:
            dist = edit_distance(str(privacy_val), each_ui_str)
            #print(dist)
            data_masking_rate = dist / len(str(privacy_val))
            #print(data_masking_rate)
            if data_masking_rate < 1:
                if dist in distances.keys():
                    distances[dist].append(each_ui_str)
                else:
                    distances[dist] = [each_ui_str]
        if len(distances) > 0:
            min_dist = min(distances.keys())
            #print(privacy_val,min_dist,distances[min_dist])
            return True, distances[min_dist]
    return False, []

def not_partial_matched(str1, str2):
    #print("str1:{},str2:{}".format(str1,str2))
    if not isinstance(str1, str):
        str1 = str(str1)
    if not isinstance(str2, str):
        str2 = str(str2)
    import edit_distance
    len1 = len(str1)
    len2 = len(str2)
    str1_matched = []
    str2_matched = []
    str1_not_matched = []
    str2_not_matched = []
    sm = edit_distance.SequenceMatcher(str1, str2)
    #print("sm:{}".format(sm))
    for each in sm.get_matching_blocks():
        #print("each:{}".format(each))
        if each[-1] == 1:
            # matched
            str1_matched.append(each[0])
            str2_matched.append(each[1])
    for i in range(max(len1, len2)):
        if i not in str1_matched and i < len1:
            str1_not_matched.append(i)
        if i not in str2_matched and i < len2:
            str2_not_matched.append(i)
    #print("re:{},{}".format(str1_not_matched,str2_not_matched))
    return str1_not_matched, str2_not_matched

