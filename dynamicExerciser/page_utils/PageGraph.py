from dynamicExerciser.page_utils.PageNode import PageNode
from dynamicExerciser.page_utils.Page import Page
import dynamicExerciser.mini_app_utils as miniAppUtils
from dynamicExerciser.page_utils.ClickOperation import ClickOperation


class PageGraph:
    root_page_node = None
    start_page_nodes = None
    all_page_nodes = None

    def __init__(self):
        self.start_page_nodes = []
        self.all_page_nodes = []

    def set_root_page(self, root_page: Page):
        if self.root_page_node is None:
            self.root_page_node = PageNode(root_page)
            self.all_page_nodes.append(self.root_page_node)

    # False:该页面已经存在或者添加失败
    # True: 新页面成功添加
    def append_new_page_node(self, from_page: Page, click_index, to_page: Page) -> [bool, Page]:
        # 维护已有page之间的关系
        if self.is_page_node_in_all(to_page) and self.is_page_node_in_all(from_page):
            from_page_node = self.find_target_page_node(from_page)
            to_page_node = self.find_target_page_node(to_page)
            if from_page.page_md5 != to_page.page_md5 and not miniAppUtils.is_similar_page(to_page, from_page):
                if isinstance(from_page_node, PageNode) and isinstance(to_page_node, PageNode):
                    to_page_node.update_click_nodes_map(from_page_node, click_index)
            return False, to_page_node.page

        # 如果页面从根节点来，则单独需要进行操作
        to_page_node = PageNode(to_page)
        if miniAppUtils.is_similar_page(from_page, self.root_page_node.page):
            to_page_node.update_click_nodes_map(self.root_page_node, click_index)
            self.root_page_node.append_children_node(to_page_node)
            self.start_page_nodes.append(to_page_node)
        else:
            from_page_node = self.find_target_page_node(from_page)
            to_page_node.update_click_nodes_map(from_page_node, click_index)
            from_page_node.append_children_node(to_page_node)

        self.all_page_nodes.append(to_page_node)
        return True, to_page_node.page

    # False: is not alone page
    def append_alone_page_node(self, alone_page: Page) -> [bool, Page]:
        alone_page_node = self.find_target_page_node(alone_page)
        # alone_page is new page
        if alone_page_node is None:
            alone_page_node = PageNode(alone_page)
            self.all_page_nodes.append(alone_page_node)
            return True, alone_page
        return False, alone_page_node.page

    def is_page_node_in_all(self, new_page: Page):
        for page_node in self.all_page_nodes:
            if miniAppUtils.is_similar_page(page_node.page, new_page):
                return True
        return False

    def is_page_node_in_start(self, new_page: Page):
        for page_node in self.start_page_nodes:
            if miniAppUtils.is_similar_page(page_node.page, new_page):
                return True
        return False

    def find_target_page_node(self, target_page) -> PageNode:
        target_page_node = None
        for page_node in self.all_page_nodes:
            if miniAppUtils.is_similar_page(page_node.page, target_page):
                target_page_node = page_node
        return target_page_node

    def get_similar_page(self, target_page):
        similar_page = None
        for page_node in self.all_page_nodes:
            if miniAppUtils.is_similar_page(page_node.page, target_page):
                similar_page = page_node.page
        return similar_page

    def get_page_by_md5(self, page_md5):
        for page_node in self.all_page_nodes:
            if page_node.page.page_md5 == page_md5:
                return page_node.page
        return None

    def get_click_operations_list(self, from_page_node: PageNode, to_page_node: PageNode):
        from_page = from_page_node.page
        init_click_operations_list = []
        for page_node in to_page_node.parent_nodes_to_click_index_map.keys():
            page = page_node.page
            md5 = page.page_md5
            click_index = to_page_node.parent_nodes_to_click_index_map[page_node]
            click_x, click_y = page.click_locations[click_index][0], page.click_locations[click_index][1]
            click_operation = ClickOperation(md5, click_index, click_x, click_y)
            click_operations = [click_operation]
            init_click_operations_list.append(click_operations)

        res_click_operations_list = []
        while len(init_click_operations_list) > 0:
            for click_operations in init_click_operations_list:
                first_click_operation = click_operations[0]
                first_page_md5 = first_click_operation.page_md5
                first_page_node = self.find_page_node_by_md5(first_page_md5)
                if first_page_md5 == from_page.page_md5 or first_page_md5 == self.root_page_node.page.page_md5:
                    res_click_operations_list.append(click_operations)
                else:
                    for page_node in first_page_node.parent_nodes_to_click_index_map.keys():
                        page = page_node.page
                        md5 = page.page_md5
                        click_index = first_page_node.parent_nodes_to_click_index_map[page_node]
                        click_x, click_y = page.click_locations[click_index][0], page.click_locations[click_index][1]
                        click_operation = ClickOperation(md5, click_index, click_x, click_y)
                        click_operations_copy = click_operations.copy()
                        if not self.check_operations_is_loop(click_operations_copy, click_operation):
                            click_operations_copy.insert(0, click_operation)
                            init_click_operations_list.append(click_operations_copy)
                init_click_operations_list.remove(click_operations)
        return res_click_operations_list

    @staticmethod
    def check_operations_is_loop(click_operations: [ClickOperation], click_operation: ClickOperation):
        for temp_click_operation in click_operations:
            if temp_click_operation.page_md5 == click_operation.page_md5:
                return True
        return False

    def is_click_operations_list_end(self, click_operations_list, from_page_md5):
        for click_operations in click_operations_list:
            first_click_operation = click_operations[0]
            if first_click_operation.page_md5 != from_page_md5 and first_click_operation.page_md5 != self.root_page_node.page.page_md5:
                return False
        return True

    def find_page_node_by_md5(self, page_md5):
        for page_node in self.all_page_nodes:
            if page_node.page.page_md5 == page_md5:
                return page_node
        return None

    def print_graph(self):
        enqueue = []
        print("图中所有节点")
        for page_node in self.all_page_nodes:
            enqueue.append(page_node)
            print(page_node.page.page_md5, page_node.page.page_dump_str)

        print("图结构")
        while len(enqueue) > 0:
            page_node = enqueue.pop(0)
            print(page_node.page.page_md5, page_node.page.page_dump_str)
            print("当前节点父节点和进入点击点")
            if len(page_node.parent_nodes_to_click_index_map) == 0:
                print("无父节点")
            else:
                for tmp_node in page_node.parent_nodes_to_click_index_map.keys():
                    print(tmp_node.page.page_md5, tmp_node.page.page_dump_str,
                          page_node.parent_nodes_to_click_index_map[tmp_node])
            print("当前节点的子节点")
            if len(page_node.children_page_nodes) == 0:
                print("无节点")
            else:
                for tmp_node in page_node.children_page_nodes:
                    print(tmp_node.page.page_md5, tmp_node.page.page_dump_str)
