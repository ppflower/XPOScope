import re

import xlrd
import config


def get_target_mini_app_names(type_name):
    excel = xlrd.open_workbook("WeChat_XPOCheckerMini_TestCases.xls")
    sheet = excel.sheet_by_index(0)
    cols_num = sheet.ncols
    target_col_vals = None
    for i in range(cols_num):
        col_vals = sheet.col_values(i)
        if col_vals[0] == type_name:
            target_col_vals = col_vals
            break
    return target_col_vals


if __name__ == "__main__":
    # mini_app_names = get_target_mini_app_names("约会")
    # for i in range(len(mini_app_names)):
    #     mini_app_name = (mini_app_names[i]).replace("\n", "")
    #     print(mini_app_name)
    str="nameByeBye"
    str2=str[:-len("Bye")]
    print(str2)
