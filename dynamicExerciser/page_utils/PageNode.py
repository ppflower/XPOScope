from dynamicExerciser.page_utils.Page import Page


class PageNode:
    page = None
    parent_nodes_to_click_index_map = None
    children_page_nodes = None

    def __init__(self, page: Page):
        self.page = page
        self.parent_nodes_to_click_index_map = {}
        self.children_page_nodes = []

    def update_click_nodes_map(self, parent_page_node, click_index):
        for page_node in self.parent_nodes_to_click_index_map.keys():
            if page_node.page.page_md5 == parent_page_node.page.page_md5:
                self.parent_nodes_to_click_index_map[page_node] = click_index
                return
        self.parent_nodes_to_click_index_map[parent_page_node] = click_index

    def append_children_node(self, new_page_node):
        # 子节点已经存在，则无需添加
        for page_node in self.children_page_nodes:
            if page_node.page.page_md5 == new_page_node.page.page_md5:
                return
        # 添加子节点
        if isinstance(new_page_node, PageNode):
            self.children_page_nodes.append(new_page_node)
