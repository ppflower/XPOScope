class ClickOperation:
    page_md5 = None
    click_index = None
    click_x = None
    click_y = None

    def __init__(self, page_md5, click_index, click_x, click_y):
        self.page_md5 = page_md5
        self.click_index = click_index
        self.click_x = click_x
        self.click_y = click_y
