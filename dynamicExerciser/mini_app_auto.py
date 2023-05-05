import time

import config
from dynamicExerciser import adb_commands, mini_app_utils
from dynamicExerciser.page_utils.Page import Page
from dynamicExerciser.page_utils.PageGraph import PageGraph
from dynamicExerciser.picLabel import evaluate
from OcrDump import ocr_recognition


class MiniAppAuto:
    app_package = None
    mini_app_plat = None
    mini_app_name = None
    mobile_model = None
    # u2 device
    d = None
    page_index = None
    root_page = None
    page_graph = None
    opt_count = None
    yolo_test = None

    def __init__(self, app_package, mini_app_plat, mini_app_name, mobile_model):
        self.app_package = app_package
        self.mini_app_plat = mini_app_plat
        self.mini_app_name = mini_app_name
        self.mobile_model = mobile_model
        self.d = mini_app_utils.connect_device()
        config.DEVICE_WIDTH = self.d.device_info['display']['width']
        config.DEVICE_HEIGHT = self.d.device_info['display']['height']
        self.page_index = 0
        self.opt_count = 0
        self.page_graph = PageGraph()
        self.yolo_test = evaluate.YoloTest()

    def start_mini_app(self) -> Page:
        root_page = None
        self.clear_background_apps()
        config.operate_sleep()
        if self.mini_app_plat == 0:
            root_page = self.start_alipay_mini_app()
        if self.mini_app_plat == 1:
            root_page = self.start_wx_mini_app()
        if self.mini_app_plat == 2:
            root_page = self.start_baidu_mini_app()
        if self.root_page is None:
            self.root_page = root_page
            self.page_graph.set_root_page(self.root_page)
        return self.root_page

    def start_alipay_mini_app(self):
        device_width = config.DEVICE_WIDTH
        device_height = config.DEVICE_HEIGHT
        self.d.app_start(self.app_package, wait=True)
        time.sleep(3)
        # 点击搜索框
        search_input_x, search_input_y = 0.31, 0.075
        adb_commands.adb_click_sleep(device_width * search_input_x, device_height * search_input_y)
        # 切换adb keyboard
        adb_commands.switch_to_adb_keyboard()
        # 再次点击搜索框 光标focus
        search_x_focus, search_y_focus = 0.22, 0.075
        adb_commands.adb_click_sleep(device_width * search_x_focus, device_height * search_y_focus)
        # 输入mini app name
        adb_commands.adb_text_zh(self.mini_app_name)
        # 点击进行搜索
        search_x, search_y = 0.92, 0.07
        adb_commands.adb_click_sleep(device_width * search_x, device_height * search_y)
        # 切换至小程序页面
        config.short_sleep()
        switch_to_mini_app_x, switch_to_mini_app_y = 0.27, 0.12
        adb_commands.adb_click_sleep(device_width * switch_to_mini_app_x, device_height * switch_to_mini_app_y)
        config.short_sleep()
        start_mini_app_x, start_mini_app_y = 0.5, 0.25
        root_page = self.create_root_page([int(start_mini_app_x * device_width), int(start_mini_app_y * device_height)])
        return root_page

    # 后续可能会对点击元素的比例进行json文件化
    def start_wx_mini_app(self):
        device_width = config.DEVICE_WIDTH
        device_height = config.DEVICE_HEIGHT
        # 启动app
        self.d.app_start(self.app_package, wait=True)
        time.sleep(3)
        # 点击发现按钮
        find_ele_x, find_ele_y = 0.62, 0.96
        adb_commands.adb_click_sleep(find_ele_x * device_width, find_ele_y * device_height)
        # 点击进入小程序界面
        enter_mini_app_x, enter_mini_app_y = 0.5, 0.75
        adb_commands.adb_click_sleep(enter_mini_app_x * device_width, enter_mini_app_y * device_height)
        # 点击搜索框进入搜索
        search_input_x, search_input_y = 0.82, 0.065
        adb_commands.adb_click_sleep(search_input_x * device_width, search_input_y * device_height)
        # 切换adb keyboard
        adb_commands.switch_to_adb_keyboard()
        # search input focus
        search_input_x_focus, search_input_y_focus = 0.3, 0.07
        adb_commands.adb_click_sleep(search_input_x_focus * device_width, search_input_y_focus * device_height)
        # 输入小程序名称(包含中文)
        adb_commands.adb_text_zh(self.mini_app_name)
        # 点击搜索小程序
        adb_commands.oneplus_wx_enter()
        config.short_sleep()
        start_mini_app_x, start_mini_app_y = 0.5, 0.23
        root_page = self.create_root_page([int(start_mini_app_x * device_width), int(start_mini_app_y * device_height)])
        return root_page

    def start_baidu_mini_app(self):
        device_width = config.DEVICE_WIDTH
        device_height = config.DEVICE_HEIGHT
        self.d.app_start(self.app_package, wait=True)
        # 百度app需要等待一定的时间
        config.long_sleep()
        # 进入我的页面
        my_page_x, my_page_y = 0.89, 0.97
        # print(my_page_x * device_width, my_page_y * device_height)
        adb_commands.adb_click_sleep(int(my_page_x * device_width), int(my_page_y * device_height))
        # 点击进入小程序
        enter_mini_app_x, enter_mini_app_y = 0.86, 0.78
        adb_commands.adb_click_sleep(enter_mini_app_x * device_width, enter_mini_app_y * device_height)
        # 点击搜索，进行文字输入
        search_input_x, search_input_y = 0.13, 0.11
        adb_commands.adb_click_sleep(search_input_x * device_width, search_input_y * device_height)
        adb_commands.switch_to_adb_keyboard()
        # 切换键盘后，光标focus
        adb_commands.adb_click_sleep(search_input_x * device_width, search_input_y * device_height)
        adb_commands.adb_text_zh(self.mini_app_name)
        adb_commands.adb_key_event(adb_commands.KEYCODE_ENTER)
        config.short_sleep()
        # 点击对应小程序
        start_mini_app_x, start_mini_app_y = 0.25, 0.2
        root_page = self.create_root_page([int(start_mini_app_x * device_width), int(start_mini_app_y * device_height)])
        return root_page

    def current_page_is_root(self, current_page):
        if self.root_page is None:
            return False
        if current_page is not None:
            return mini_app_utils.is_similar_page(current_page, self.root_page)

        current_dump_str, current_md5, ocr_locations = ocr_recognition.cache_image_dump_str()
        root_dump_str, root_md5 = self.root_page.page_dump_str, self.root_page.page_md5
        return mini_app_utils.is_similar_page_by_details(current_md5, current_dump_str, root_md5, root_dump_str)

    def create_root_page(self, new_click_location):
        adb_commands.adb_screenshot(self.page_index)
        page_dump_str, page_md5, ocr_click_locations = ocr_recognition.screenshot_dump_str(0, False)
        root_page = Page(self.page_index, page_md5, page_dump_str)
        root_page.append_new_click_location(new_click_location)
        self.page_index += 1
        return root_page

    def create_normal_page(self, click_index, from_page: Page):
        if from_page.page_md5 == self.root_page.page_md5:
            config.short_sleep()
        config.short_sleep()
        temp_index = "temp"
        adb_commands.adb_screenshot(temp_index)
        page_dump_str, page_md5, ocr_click_locations = ocr_recognition.screenshot_dump_str(temp_index, True)

        # 如果存在权限授予环节，权限确认
        if self.contain_permission_tip(page_dump_str):
            # print("权限确认")
            adb_commands.adb_screenshot(temp_index)
            page_dump_str, page_md5, ocr_click_locations = ocr_recognition.screenshot_dump_str(temp_index, True)

        new_page = Page(temp_index, page_md5, page_dump_str)
        is_new_page, new_or_similar_page = self.page_graph.append_new_page_node(from_page, click_index, new_page)
        if is_new_page:
            new_page.set_index(self.page_index)
            adb_commands.rename_screenshot(temp_index, self.page_index)
            yolo_click_locations = self.extract_click_locations(new_page.index)
            if self.is_yolo_predict_success(page_dump_str, len(yolo_click_locations)):
                new_page.append_new_click_locations(yolo_click_locations)
            else:
                new_page.append_new_click_locations(ocr_click_locations)
            self.page_index += 1
        else:
            adb_commands.del_screenshot(temp_index)
        return is_new_page, new_or_similar_page

    def create_alone_page(self):
        config.short_sleep()
        temp_index = "temp"
        adb_commands.adb_screenshot(temp_index)
        page_dump_str, page_md5, ocr_click_locations = ocr_recognition.screenshot_dump_str(temp_index, True)
        # 权限确认
        if self.contain_permission_tip(page_dump_str):
            adb_commands.adb_screenshot(temp_index)
            page_dump_str, page_md5, ocr_click_locations = ocr_recognition.screenshot_dump_str(temp_index, True)
        alone_page = Page(temp_index, page_md5, page_dump_str)
        is_alone_page, alone_or_similar_page = self.page_graph.append_alone_page_node(alone_page)
        if is_alone_page:
            alone_page.set_index(self.page_index)
            adb_commands.rename_screenshot(temp_index, self.page_index)
            yolo_click_locations = self.extract_click_locations(alone_page.index)
            if self.is_yolo_predict_success(page_dump_str, len(yolo_click_locations)):
                alone_page.append_new_click_locations(yolo_click_locations)
            else:
                alone_page.append_new_click_locations(ocr_click_locations)
            self.page_index += 1
        else:
            adb_commands.del_screenshot(temp_index)
        return is_alone_page, alone_or_similar_page

    def extract_click_locations(self, index):
        screenshot_image_path = config.SCREENSHOT_PATH + str(index) + ".png"
        element_locations = mini_app_utils.extract_image_info(self.yolo_test, screenshot_image_path)
        click_locations = []
        x_scale, y_scale = mini_app_utils.compute_xy_scale(index)
        for element_location in element_locations:
            compute_x, compute_y = (element_location[0] + element_location[2]) / 2, (
                    element_location[1] + element_location[3]) / 2
            real_x, real_y = x_scale * compute_x, y_scale * compute_y
            if not mini_app_utils.is_noise_click_location(real_x, real_y):
                click_locations.append([int(real_x), int(real_y)])
        return click_locations

    @staticmethod
    def is_yolo_predict_success(dump_strs, element_num):
        word_num = 0
        for dump_str in dump_strs:
            word_num += len(dump_str)
        if word_num / config.Word_Per_Element > 1.5 * element_num:
            return False
        else:
            return True

    # 针对不同机型进行定制操作
    # oneplus 1
    # ... ...
    def clear_background_apps(self):
        if self.mobile_model == 1:
            self.oneplus_clear_background_apps()

    def oneplus_clear_background_apps(self):
        adb_commands.adb_key_event(adb_commands.KEYCODE_SWITCH_APP)
        if self.d(textContains="清除").exists:
            self.d(textContains="清除").click()
        else:
            self.d.click(config.DEVICE_WIDTH / 2, config.DEVICE_HEIGHT / 2)

    def contain_permission_tip(self, dump_strs):
        if self.mini_app_plat == 0:
            return self.alipay_contain_permission_tip(dump_strs)
        if self.mini_app_plat == 1:
            return self.wx_contain_permission_tip(dump_strs)
        if self.mini_app_plat == 2:
            return self.baidu_contain_permission_tip(dump_strs)
        return False

    def back(self, expect_back_page: Page, current_page: Page) -> [bool, Page]:
        adb_commands.adb_key_event(adb_commands.KEYCODE_BACK)
        mini_app_utils.write_last_opt(self.opt_count)
        is_alone_page, actual_back_page = self.create_alone_page()
        mini_app_utils.write_page_text(self.opt_count, actual_back_page.page_dump_str)
        mini_app_utils.append_opt_image_map(self.opt_count, actual_back_page.index)
        self.opt_count += 1

        if mini_app_utils.is_similar_page(current_page, actual_back_page):
            adb_commands.adb_key_event(adb_commands.KEYCODE_BACK)
            mini_app_utils.write_last_opt(self.opt_count)
            is_alone_page, actual_back_page = self.create_alone_page()
            mini_app_utils.write_page_text(self.opt_count, actual_back_page.page_dump_str)
            mini_app_utils.append_opt_image_map(self.opt_count, actual_back_page.index)
            self.opt_count += 1

        if not mini_app_utils.is_similar_page(current_page, actual_back_page):
            if mini_app_utils.is_similar_page(expect_back_page, actual_back_page):
                return True, expect_back_page
            else:
                return False, actual_back_page
        else:
            return False, actual_back_page

    def enter_target_page(self, to_page: Page):
        enter_success = True
        from_page_node = self.page_graph.root_page_node
        to_page_node = self.page_graph.find_target_page_node(to_page)
        if from_page_node is None or to_page_node is None:
            return not enter_success, None
        if from_page_node.page.page_md5 == to_page_node.page.page_md5:
            return enter_success, None

        click_operations_list = self.page_graph.get_click_operations_list(from_page_node, to_page_node)
        if len(click_operations_list) == 0:
            return not enter_success, None

        # root page 点击按键只有一个，所以这边只需要选择其中任意一条路径的第一个点击操作进行点击即可
        root_click_x, root_click_y = self.root_page.click_locations[0][0], self.root_page.click_locations[0][1]
        adb_commands.adb_click(root_click_x, root_click_y)
        mini_app_utils.write_last_opt(self.opt_count)
        config.short_sleep()
        # 判断root page进入后的页面（start page）是否发生变化
        is_new_page, new_or_similar_page = self.create_normal_page(0, self.root_page)
        mini_app_utils.write_page_text(self.opt_count, new_or_similar_page.page_dump_str)
        mini_app_utils.append_opt_image_map(self.opt_count, new_or_similar_page.index)
        self.opt_count += 1
        if is_new_page:
            # 此处为减少时间开销，我们只单纯考虑root page进入后第一个页面的情况
            return not enter_success, new_or_similar_page
        else:
            for click_operations in click_operations_list:
                if len(click_operations) > 1 and click_operations[1].page_md5 == new_or_similar_page.page_md5:
                    for index in range(1, len(click_operations)):
                        adb_commands.adb_click(click_operations[index].click_x, click_operations[index].click_y)
                        mini_app_utils.write_last_opt(self.opt_count)
                        time.sleep(1)
                        if index == len(click_operations) - 1:
                            click_index = click_operations[index].click_index
                            parent_page = self.page_graph.get_page_by_md5(click_operations[index].page_md5)
                            if parent_page is None:
                                is_alone_page, curr_page = self.create_alone_page()
                            else:
                                is_new_page, curr_page = self.create_normal_page(click_index, parent_page)
                            mini_app_utils.write_page_text(self.opt_count, curr_page.page_dump_str)
                            mini_app_utils.append_opt_image_map(self.opt_count, curr_page.index)
                            self.opt_count += 1
                            if mini_app_utils.is_similar_page(to_page, curr_page):
                                return enter_success, None
                            else:
                                return not enter_success, curr_page
                        else:
                            dump_str, md5, click_locations = ocr_recognition.cache_image_dump_str()
                            mini_app_utils.write_page_text(self.opt_count, dump_str)
                            mini_app_utils.append_opt_image_map(self.opt_count, "temp")
                            self.opt_count += 1
        return not enter_success, None

    @staticmethod
    def alipay_contain_permission_tip(dump_strs):
        device_width, device_height = config.DEVICE_WIDTH, config.DEVICE_HEIGHT
        if mini_app_utils.contain_permission_tip(dump_strs):
            enter_x, enter_y = 0.75, 0.9
            adb_commands.adb_click_sleep(enter_x * device_width, enter_y * device_height)
            return True
        else:
            return False

    @staticmethod
    def wx_contain_permission_tip(dump_strs):
        device_width, device_height = config.DEVICE_WIDTH, config.DEVICE_HEIGHT
        if mini_app_utils.contain_permission_tip(dump_strs):
            enter_x, enter_y = 0.7, 0.9
            adb_commands.adb_click_sleep(enter_x * device_width, enter_y * device_height)
            return True
        else:
            return False

    @staticmethod
    def baidu_contain_permission_tip(dump_strs):
        device_width, device_height = config.DEVICE_WIDTH, config.DEVICE_HEIGHT
        if mini_app_utils.contain_permission_tip(dump_strs):
            enter_x, enter_y = 0.75, 0.93
            adb_commands.adb_click_sleep(enter_x * device_width, enter_y * device_height)
            return True
        else:
            return False

    def close_mini_app(self):
        device_width = config.DEVICE_WIDTH
        device_height = config.DEVICE_HEIGHT
        if self.mini_app_plat == 0:
            self.close_alipay_mini_app(device_width, device_height)
        if self.mini_app_plat == 1:
            self.close_wx_mini_app(device_width, device_height)
        if self.mini_app_plat == 2:
            self.close_baidu_mini_app(device_width, device_height)

    @staticmethod
    def close_alipay_mini_app(device_width, device_height):
        close_mini_app_x = 0.92
        close_mini_app_y = 0.07
        adb_commands.adb_click_sleep(device_width * close_mini_app_x, device_height * close_mini_app_y)

    @staticmethod
    def close_wx_mini_app(device_width, device_height):
        close_mini_app_x = 0.92
        close_mini_app_y = 0.07
        adb_commands.adb_click_sleep(device_width * close_mini_app_x, device_height * close_mini_app_y)

    @staticmethod
    def close_baidu_mini_app(device_width, device_height):
        close_mini_app_x = 0.927
        close_mini_app_y = 0.065
        adb_commands.adb_click_sleep(device_width * close_mini_app_x, device_height * close_mini_app_y)

    @staticmethod
    def is_similar_page(page1: Page, page2: Page):
        return mini_app_utils.is_similar_page(page1, page2)
