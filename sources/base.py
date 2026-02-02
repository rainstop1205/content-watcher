# 抽象類別，規定所有爬蟲都要遵守的規則
class BaseSource:
    def __init__(self, config):
        self.config = config

    def fetch_new_posts(self):
        """
        所有 source 都必須實作這個功能。
        回傳值必須統一格式，例如：
        [
            {'id': '唯一碼', 'title': '標題', 'link': '連結', 'source': '來源名'}
        ]
        """
        raise NotImplementedError("子類別必須實作這個方法！")