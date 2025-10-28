#!/usr/bin/env python3
"""e+ログイン動作確認テスト"""

import asyncio
from pathlib import Path
from src.config import Settings
from src.browser import BrowserHelper
from src.flows.base import BaseFlow

class LoginTestFlow(BaseFlow):
    """ログインテスト用フロー"""
    
    async def execute(self):
        """ログインフローを実行"""
        print("\n📋 e+ ログインテスト開始")
        print("=" * 60)
        
        # e+ ログインページにアクセス
        login_url = "https://eplus.jp/sf/top"
        print(f"\n🌐 {login_url} にアクセス中...")
        
        await self.page.goto(login_url, wait_until="domcontentloaded", timeout=30000)
        await self.helper.safe_wait(2000)
        
        # スクリーンショット保存
        await self.helper.save_screenshot(self.page, "01_eplus_top.png")
        print("✓ トップページのスクリーンショット保存完了")
        
        # ログインボタンを探す（複数パターン試行）
        login_selectors = [
            'a:has-text("ログイン")',
            'button:has-text("ログイン")',
            '[href*="login"]',
            '.login-btn',
            '#login-button'
        ]
        
        login_button = None
        for selector in login_selectors:
            try:
                login_button = await self.page.wait_for_selector(
                    selector, 
                    timeout=5000,
                    state="visible"
                )
                if login_button:
                    print(f"✓ ログインボタン検出: {selector}")
                    break
            except:
                continue
        
        if not login_button:
            print("\n⚠️  自動ログインボタン検出失敗")
            print("🖱️  手動でログインボタンをクリックしてください")
            print("   ブラウザウィンドウが開いています...")
            await self.helper.safe_wait(60000)  # 60秒待機
        else:
            # ログインボタンクリック
            await login_button.click()
            print("✓ ログインボタンクリック")
            await self.helper.safe_wait(3000)
            
            await self.helper.save_screenshot(self.page, "02_login_page.png")
            print("✓ ログインページのスクリーンショット保存完了")
            
            # ログインフォーム検出
            email_selectors = [
                'input[type="email"]',
                'input[name="email"]',
                'input[placeholder*="メール"]',
                'input[id*="email"]'
            ]
            
            password_selectors = [
                'input[type="password"]',
                'input[name="password"]',
                'input[id*="password"]'
            ]
            
            email_input = None
            for selector in email_selectors:
                try:
                    email_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if email_input:
                        print(f"✓ メールアドレス入力欄検出: {selector}")
                        break
                except:
                    continue
            
            password_input = None
            for selector in password_selectors:
                try:
                    password_input = await self.page.wait_for_selector(selector, timeout=3000)
                    if password_input:
                        print(f"✓ パスワード入力欄検出: {selector}")
                        break
                except:
                    continue
            
            if email_input and password_input and self.config.eplus_email and self.config.eplus_password:
                print("\n📝 ログイン情報を入力中...")
                await email_input.fill(self.config.eplus_email)
                print("✓ メールアドレス入力完了")
                
                await password_input.fill(self.config.eplus_password)
                print("✓ パスワード入力完了")
                
                await self.helper.save_screenshot(self.page, "03_credentials_filled.png")
                
                # ログイン実行ボタン検索
                submit_selectors = [
                    'button[type="submit"]',
                    'input[type="submit"]',
                    'button:has-text("ログイン")',
                    'button:has-text("送信")',
                    '.submit-btn'
                ]
                
                submit_button = None
                for selector in submit_selectors:
                    try:
                        submit_button = await self.page.wait_for_selector(selector, timeout=3000)
                        if submit_button:
                            print(f"✓ ログイン実行ボタン検出: {selector}")
                            break
                    except:
                        continue
                
                if submit_button:
                    print("\n⚠️  ログイン実行ボタンが見つかりました")
                    print("   CAPTCHA等がある場合は手動で対応してください")
                    print("   30秒後に自動でボタンをクリックします...")
                    await self.helper.safe_wait(30000)
                    
                    await submit_button.click()
                    print("✓ ログイン実行")
                    
                    await self.helper.safe_wait(5000)
                    await self.helper.save_screenshot(self.page, "04_after_login.png")
                    print("✓ ログイン後のスクリーンショット保存完了")
                else:
                    print("\n⚠️  ログイン実行ボタンが見つかりません")
                    print("🖱️  手動でログインを完了してください（60秒待機）")
                    await self.helper.safe_wait(60000)
            else:
                print("\n⚠️  ログインフォームの自動入力失敗")
                print("🖱️  手動でログイン情報を入力してください（60秒待機）")
                print(f"   .envファイルにEPLUS_EMAIL, EPLUS_PASSWORDを設定してください")
                await self.helper.safe_wait(60000)
        
        # 最終状態確認
        current_url = self.page.url
        print(f"\n📍 現在のURL: {current_url}")
        
        page_title = await self.page.title()
        print(f"📄 ページタイトル: {page_title}")
        
        await self.helper.save_screenshot(self.page, "05_final_state.png")
        print("✓ 最終状態のスクリーンショット保存完了")
        
        print("\n" + "=" * 60)
        print("✅ ログインテスト完了")
        print(f"📁 スクリーンショット保存先: {self.config.screenshot_dir}")

async def main():
    """メイン実行関数"""
    config = Settings()
    
    # スクリーンショットディレクトリ作成
    Path(config.screenshot_dir).mkdir(parents=True, exist_ok=True)
    
    async with BrowserHelper(config) as helper:
        page = await helper.create_page()
        flow = LoginTestFlow(page, helper, config)
        await flow.execute()
        
        # 最後に10秒待機してブラウザを確認可能に
        print("\n⏱️  10秒後にブラウザを閉じます...")
        await asyncio.sleep(10)

if __name__ == "__main__":
    asyncio.run(main())
