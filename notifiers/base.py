from abc import ABC, abstractmethod

class BaseNotifier(ABC):
    def __init__(self, config):
        """
        初始化 Notifier
        :param config: 該 Notifier 的設定 dict (例如包含 webhook_url)
        """
        self.config = config

    @abstractmethod
    def send(self, messages: list[str]):
        """
        發送通知的標準介面
        :param messages: 一個字串列表，每個字串是一則要發送的訊息
        """
        pass