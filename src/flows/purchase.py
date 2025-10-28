"""即購入フロー"""

from playwright.async_api import Page
from .base import BaseFlow
from ..browser import BrowserHelper
from ..config import Settings


class QuickPurchaseFlow(BaseFlow):
    """即購入フロー（先着順チケット）"""
    
    def __init__(self, page: Page, helper: BrowserHelper, config: Settings, event_url: str):
        super().__init__(page, helper, config)
        self.event_url = event_url
    
    async def execute(self):
        """即購入フローを実行"""
        print("\n⚡ 即購入フロー開始")
        print("=" * 60)
        
        # イベントページにアクセス
        print(f"\n🌐 {self.event_url} にアクセス中...")
        await self.page.goto(self.event_url, wait_until="domcontentloaded", timeout=30000)
        await self.helper.safe_wait(1000)
        await self.helper.save_screenshot(self.page, "purchase_01_event_page.png")
        
        # 購入ボタンを探す（高速クリック重視）
        purchase_selectors = [
            'button:has-text("購入")',
            'a:has-text("購入")',
            'button:has-text("申し込む")',
            'button:has-text("今すぐ購入")',
            '[class*="purchase"]',
            '[class*="buy"]'
        ]
        
        purchase_button = None
        for selector in purchase_selectors:
            try:
                purchase_button = await self.page.wait_for_selector(
                    selector,
                    timeout=3000,
                    state="visible"
                )
                if purchase_button:
                    print(f"✓ 購入ボタン検出: {selector}")
                    # 即座にクリック
                    await purchase_button.click()
                    print("✓ 購入ボタンクリック")
                    break
            except:
                continue
        
        if not purchase_button:
            print("\n⚠️  購入ボタンが自動検出できませんでした")
            print("🖱️  手動で購入ボタンをクリックしてください（30秒待機）")
            await self.helper.safe_wait(30000)
        else:
            await self.helper.safe_wait(2000)
            await self.helper.save_screenshot(self.page, "purchase_02_after_click.png")
        
        # 座席選択
        seat_selectors = [
            'button:has-text("座席を選ぶ")',
            '[class*="seat-select"]',
            'button:has-text("選択")'
        ]
        
        seat_button = None
        for selector in seat_selectors:
            try:
                seat_button = await self.page.wait_for_selector(selector, timeout=5000)
                if seat_button:
                    print(f"✓ 座席選択ボタン検出: {selector}")
                    await seat_button.click()
                    print("✓ 座席選択ボタンクリック")
                    break
            except:
                continue
        
        if seat_button:
            await self.helper.safe_wait(2000)
            await self.helper.save_screenshot(self.page, "purchase_03_seat_selection.png")
        
        # 枚数選択
        quantity_selectors = [
            'select[name*="quantity"]',
            'select[name*="ticket"]',
            'input[name*="quantity"]'
        ]
        
        quantity_input = None
        for selector in quantity_selectors:
            try:
                quantity_input = await self.page.wait_for_selector(selector, timeout=5000)
                if quantity_input:
                    print(f"✓ 枚数選択要素検出: {selector}")
                    tag_name = await quantity_input.evaluate("el => el.tagName")
                    if tag_name.lower() == "select":
                        await quantity_input.select_option(value="1")
                    else:
                        await quantity_input.fill("1")
                    print("✓ 枚数選択完了（1枚）")
                    break
            except:
                continue
        
        if quantity_input:
            await self.helper.save_screenshot(self.page, "purchase_04_quantity_selected.png")
        
        # カートに追加 / 次へボタン
        next_selectors = [
            'button:has-text("カートに入れる")',
            'button:has-text("次へ")',
            'button:has-text("確認")',
            'button[type="submit"]'
        ]
        
        next_button = None
        for selector in next_selectors:
            try:
                next_button = await self.page.wait_for_selector(selector, timeout=5000)
                if next_button:
                    print(f"✓ 次へボタン検出: {selector}")
                    await next_button.click()
                    print("✓ 次へボタンクリック")
                    break
            except:
                continue
        
        if next_button:
            await self.helper.safe_wait(3000)
            await self.helper.save_screenshot(self.page, "purchase_05_after_next.png")
        
        # 支払い方法選択ページ
        print("\n💳 支払い方法選択ページに到達した可能性があります")
        print("   ここから先は手動で進めてください（60秒待機）")
        await self.helper.safe_wait(60000)
        
        # 最終確認
        current_url = self.page.url
        print(f"\n📍 現在のURL: {current_url}")
        
        page_title = await self.page.title()
        print(f"📄 ページタイトル: {page_title}")
        
        await self.helper.save_screenshot(self.page, "purchase_06_final_state.png")
        
        print("\n" + "=" * 60)
        print("✅ 即購入フロー完了")
        print("⚠️  最終的な購入確定は手動で行ってください")
