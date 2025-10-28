"""ベースフロークラス"""

from abc import ABC, abstractmethod
from playwright.async_api import Page

from ..config import Settings
from ..browser import BrowserHelper


class BaseFlow(ABC):
    """すべてのフローの基底クラス"""
    
    def __init__(self, page: Page, helper: BrowserHelper, config: Settings):
        self.page = page
        self.helper = helper
        self.config = config
    
    @abstractmethod
    async def execute(self):
        """フローの実行（サブクラスで実装）"""
        pass
