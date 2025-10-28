"""抽選応募フロー"""

from playwright.async_api import Page
from .base import BaseFlow
from ..browser import BrowserHelper
from ..config import Settings


class LotteryEntryFlow(BaseFlow):
    """抽選応募フロー"""
    
    def __init__(self, page: Page, helper: BrowserHelper, config: Settings, event_url: str):
        super().__init__(page, helper, config)
        self.event_url = event_url
    
    async def execute(self):
        """抽選応募フローを実行"""
        print("\n🎫 抽選応募フロー開始")
        print("=" * 60)
        
        # イベントページにアクセス
        print(f"\n🌐 {self.event_url} にアクセス中...")
        await self.page.goto(self.event_url, wait_until="domcontentloaded", timeout=30000)
        await self.helper.safe_wait(2000)
        await self.helper.save_screenshot(self.page, "lottery_01_event_page.png")
        
        # 応募ボタンを探す
        entry_selectors = [
            'button:has-text("応募")',
            'a:has-text("応募")',
            'button:has-text("申し込む")',
            'a:has-text("申し込む")',
            '[class*="entry"]',
            '[class*="apply"]'
        ]
        
        entry_button = None
        for selector in entry_selectors:
            try:
                entry_button = await self.page.wait_for_selector(
                    selector,
                    timeout=5000,
                    state="visible"
                )
                if entry_button:
                    print(f"✓ 応募ボタン検出: {selector}")
                    break
            except:
                continue
        
        if entry_button:
            await entry_button.click()
            print("✓ 応募ボタンクリック")
            await self.helper.safe_wait(3000)
            await self.helper.save_screenshot(self.page, "lottery_02_after_click.png")
        else:
            print("\n⚠️  応募ボタンが自動検出できませんでした")
            print("🖱️  手動で応募ボタンをクリックしてください（60秒待機）")
            await self.helper.safe_wait(60000)
        
        # 枚数選択
        quantity_selectors = [
            'select[name*="quantity"]',
            'select[name*="ticket"]',
            'input[name*="quantity"]',
            '[class*="quantity"]'
        ]
        
        quantity_input = None
        for selector in quantity_selectors:
            try:
                quantity_input = await self.page.wait_for_selector(selector, timeout=5000)
                if quantity_input:
                    print(f"✓ 枚数選択要素検出: {selector}")
                    break
            except:
                continue
        
        if quantity_input:
            # デフォルトで1枚選択
            tag_name = await quantity_input.evaluate("el => el.tagName")
            if tag_name.lower() == "select":
                await quantity_input.select_option(value="1")
            else:
                await quantity_input.fill("1")
            print("✓ 枚数選択完了（1枚）")
            await self.helper.save_screenshot(self.page, "lottery_03_quantity_selected.png")
        
        # 確認・次へボタン
        confirm_selectors = [
            'button:has-text("確認")',
            'button:has-text("次へ")',
            'button:has-text("進む")',
            'button[type="submit"]',
            'input[type="submit"]'
        ]
        
        confirm_button = None
        for selector in confirm_selectors:
            try:
                confirm_button = await self.page.wait_for_selector(selector, timeout=5000)
                if confirm_button:
                    print(f"✓ 確認ボタン検出: {selector}")
                    break
            except:
                continue
        
        if confirm_button:
            print("\n⚠️  確認ボタンが見つかりました")
            print("   手動で内容を確認して進めてください（60秒待機）")
            await self.helper.safe_wait(60000)
        
        # 最終確認
        current_url = self.page.url
        print(f"\n📍 現在のURL: {current_url}")
        
        page_title = await self.page.title()
        print(f"📄 ページタイトル: {page_title}")
        
        await self.helper.save_screenshot(self.page, "lottery_04_final_state.png")
        
        print("\n" + "=" * 60)
        print("✅ 抽選応募フロー完了")
        print("⚠️  最終的な応募確定は手動で行ってください")
