import sys

import eventlet

import config
from dynamicExerciser import mini_app_auto
from dynamicExerciser.page_utils.Page import Page
from dynamicExerciser import adb_commands
from dynamicExerciser import mini_app_utils


def bfs_auto_run(app_package, mini_app_plat, mini_app_name, mobile_model):
    enqueue = []
    mini_app = mini_app_auto.MiniAppAuto(app_package, mini_app_plat, mini_app_name, mobile_model)
    root_page = mini_app.start_mini_app()
    enqueue.append(root_page)
    bfs_click(enqueue, mini_app)


def bfs_click(enqueue, mini_app):
    root_page = enqueue.pop(0)
    target_page = page_bfs_click(root_page, mini_app, enqueue)
    while len(enqueue) > 0 or target_page is not None:
        while target_page is None:
            if len(enqueue) > 0:
                target_page = enqueue.pop(0)
            else:
                target_page = None
                break
            enter_success, enter_page = mini_app.enter_target_page(target_page)
            if not enter_success:
                if enter_page is not None:
                    # enqueue.append(target_page)
                    target_page = enter_page
                    break
                # else:
                #     enqueue.append(target_page)
        if target_page is not None:
            target_page = page_bfs_click(target_page, mini_app, enqueue)
        else:
            break


def page_bfs_click(target_page: Page, mini_app: mini_app_auto.MiniAppAuto, enqueue: list) -> [Page]:
    if len(target_page.click_locations) == 1:
        click_x, click_y = target_page.click_locations[0][0], target_page.click_locations[0][1]
        adb_commands.adb_click(click_x, click_y)
        mini_app_utils.write_last_opt(mini_app.opt_count)
        if target_page.click_index < len(target_page.click_locations):
            target_page.click_index += 1
        is_new_page, new_or_similar_page = mini_app.create_normal_page(0, target_page)
        mini_app_utils.write_page_text(mini_app.opt_count, new_or_similar_page.page_dump_str)
        mini_app_utils.append_opt_image_map(mini_app.opt_count, new_or_similar_page.index)
        mini_app.opt_count += 1
        target_page = new_or_similar_page
        return target_page

    for cdx in range(target_page.click_index, len(target_page.click_locations)):
        click_x, click_y = target_page.click_locations[cdx][0], target_page.click_locations[cdx][1]
        adb_commands.adb_click(click_x, click_y)
        mini_app_utils.write_last_opt(mini_app.opt_count)
        if target_page.click_index < len(target_page.click_locations):
            target_page.click_index += 1
        is_new_page, new_or_similar_page = mini_app.create_normal_page(cdx, target_page)
        mini_app_utils.write_page_text(mini_app.opt_count, new_or_similar_page.page_dump_str)
        mini_app_utils.append_opt_image_map(mini_app.opt_count, new_or_similar_page.index)
        mini_app.opt_count += 1
        if mini_app.current_page_is_root(new_or_similar_page):
            if cdx < len(target_page.click_locations) - 1:
                enqueue.append(new_or_similar_page)
            return None
        if not mini_app.is_similar_page(new_or_similar_page, target_page):
            if is_new_page and len(new_or_similar_page.page_dump_str) > 0:
                enqueue.append(new_or_similar_page)

            back_success, actual_back_page = mini_app.back(target_page, new_or_similar_page)
            # 如果没有返回到预期的页面
            if not back_success:
                if mini_app.current_page_is_root(actual_back_page):
                    if cdx < len(target_page.click_locations) - 1:
                        enqueue.append(target_page)
                    return None
                else:
                    return actual_back_page
    mini_app.close_mini_app()
    if not mini_app.current_page_is_root(None):
        mini_app.start_mini_app()
    return None


def mini_app_test(app_package, mini_app_platform, mini_app_name, mobile_model):
    bfs_auto_run(app_package, mini_app_platform, mini_app_name, mobile_model)


if __name__ == "__main__":
    args = sys.argv
    mini_app_platform = int(args[1])
    mobile_model = int(args[2])
    mini_app_name = args[3].strip("'")
    # mini_app_platform = 0
    # mobile_model = 1
    # mini_app_name = '孔夫子旧书网'
    if mini_app_platform == 0:
        app_package = 'com.eg.android.AlipayGphone'
    elif mini_app_platform == 1:
        app_package = 'com.tencent.mm'
    else:
        app_package = 'com.baidu.searchbox'
    mini_app_utils.del_evaluate_img()
    mini_app_utils.del_page_text()
    mini_app_utils.create_opt_file()
    mini_app_utils.create_opt_image_map_file()
    eventlet.monkey_patch()
    with eventlet.Timeout(config.MINI_APP_TEST_TIME, False):
        mini_app_test(app_package, mini_app_platform, mini_app_name, mobile_model)
    mini_app_utils.remove_screenshot_img(mini_app_platform, config.Mini_App_Type, mini_app_name)
    print("Dynamic Exerciser end")
