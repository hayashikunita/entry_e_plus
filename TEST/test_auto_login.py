#!/usr/bin/env python3
"""e+ 完全自動ログインテスト"""

import asyncio
from pathlib import Path
from src.config import Settings
from src.browser import BrowserHelper
from src.flows.base import BaseFlow

class AutoLoginFlow(BaseFlow):
    """完全自動ログインフロー"""
    
    async def execute(self):
        """自動ログインフローを実行"""
        print("\n🔐 e+ 自動ログイン開始")
        print("=" * 60)
        
        # 設定確認
        if not self.config.eplus_email or not self.config.eplus_password:
            print("❌ エラー: .envファイルにEPLUS_EMAILとEPLUS_PASSWORDが設定されていません")
            return False
        
        print(f"✓ ログイン情報読み込み完了")
        print(f"  メール: {self.config.eplus_email}")
        print(f"  パスワード: {'*' * len(self.config.eplus_password)}")
        
        # e+ トップページにアクセスしてからログインボタンをクリック
        top_url = "https://eplus.jp/"
        print(f"\n🌐 {top_url} にアクセス中...")
        
        try:
            await self.page.goto(top_url, wait_until="domcontentloaded", timeout=30000)
            await self.helper.safe_wait(2000)
            await self.helper.save_screenshot(self.page, "auto_01_top_page.png")
            print("✓ トップページ表示完了")
            
            # ログインボタンを探してクリック
            print("\n🔍 ログインボタンを検索中...")
            top_login_selectors = [
                'a:has-text("ログイン")',
                'button:has-text("ログイン")',
                'a[href*="login"]',
                '.header-login',
                '#login-link'
            ]
            
            top_login_btn = None
            for selector in top_login_selectors:
                try:
                    top_login_btn = await self.page.wait_for_selector(
                        selector,
                        timeout=3000,
                        state="visible"
                    )
                    if top_login_btn:
                        print(f"✓ トップページのログインボタン検出: {selector}")
                        await top_login_btn.click()
                        print("✓ ログインボタンクリック")
                        await self.helper.safe_wait(3000)
                        await self.helper.save_screenshot(self.page, "auto_01_login_page.png")
                        break
                except:
                    continue
            
            if not top_login_btn:
                print("⚠️  トップページのログインボタンが見つかりません")
                print("   直接ログインフォームを探します...")
            else:
                print("✓ ログインページ表示完了")
            
        except Exception as e:
            print(f"❌ ページアクセスエラー: {e}")
            return False
        
        # メールアドレス入力欄を検出
        email_selectors = [
            'input[name="login_id"]',  # e+の実際のセレクタ
            'input[type="email"]',
            'input[name="loginid"]',
            'input[id="loginid"]',
            'input[placeholder*="メール"]',
            'input[placeholder*="ID"]',
            '#loginid'
        ]
        
        email_input = None
        found_email_selector = None
        for selector in email_selectors:
            try:
                email_input = await self.page.wait_for_selector(
                    selector, 
                    timeout=5000,
                    state="visible"
                )
                if email_input:
                    found_email_selector = selector
                    print(f"✓ メール入力欄検出: {selector}")
                    break
            except:
                continue
        
        if not email_input:
            print("❌ メール入力欄が見つかりません")
            await self.helper.save_screenshot(self.page, "auto_error_no_email.png")
            return False
        
        # パスワード入力欄を検出
        password_selectors = [
            'input[name="login_pw"]',  # e+の実際のセレクタ
            'input[type="password"]',
            'input[name="password"]',
            'input[id="password"]',
            '#password'
        ]
        
        password_input = None
        found_password_selector = None
        for selector in password_selectors:
            try:
                password_input = await self.page.wait_for_selector(
                    selector,
                    timeout=5000,
                    state="visible"
                )
                if password_input:
                    found_password_selector = selector
                    print(f"✓ パスワード入力欄検出: {selector}")
                    break
            except:
                continue
        
        if not password_input:
            print("❌ パスワード入力欄が見つかりません")
            await self.helper.save_screenshot(self.page, "auto_error_no_password.png")
            return False
        
        # ログイン情報を入力
        print("\n📝 ログイン情報を入力中...")
        try:
            # メールアドレス入力（より安全な方法）
            await self.page.evaluate(
                f'document.querySelector("{found_email_selector}")?.focus()'
            )
            await self.helper.safe_wait(300)
            await self.page.keyboard.type(self.config.eplus_email, delay=50)
            print(f"✓ メールアドレス入力: {self.config.eplus_email}")
            
            await self.helper.safe_wait(500)
            
            # パスワード入力
            await self.page.evaluate(
                f'document.querySelector("{found_password_selector}")?.focus()'
            )
            await self.helper.safe_wait(300)
            await self.page.keyboard.type(self.config.eplus_password, delay=50)
            print(f"✓ パスワード入力: {'*' * len(self.config.eplus_password)}")
            
            await self.helper.save_screenshot(self.page, "auto_02_filled.png")
        except Exception as e:
            print(f"⚠️  キーボード入力失敗、代替方法を試行: {e}")
            try:
                # フォールバック: fillメソッド
                await email_input.fill(self.config.eplus_email)
                print(f"✓ メールアドレス入力: {self.config.eplus_email}")
                
                await self.helper.safe_wait(500)
                await password_input.fill(self.config.eplus_password)
                print(f"✓ パスワード入力: {'*' * len(self.config.eplus_password)}")
                
                await self.helper.save_screenshot(self.page, "auto_02_filled.png")
            except Exception as e2:
                print(f"❌ 入力エラー: {e2}")
                return False
        
        # ログインボタンを検出
        login_button_selectors = [
            'button.button--primary.button--block:has-text("ログイン")',  # e+の実際のセレクタ
            'button:has-text("ログイン")',
            'button[type="submit"]',
            'input[type="submit"]',
            'button:has-text("ログインする")',
            'a:has-text("ログイン")',
            '.login-btn',
            '#loginBtn',
            '[class*="login"][class*="button"]'
        ]
        
        login_button = None
        for selector in login_button_selectors:
            try:
                login_button = await self.page.wait_for_selector(
                    selector,
                    timeout=3000,
                    state="visible"
                )
                if login_button:
                    print(f"✓ ログインボタン検出: {selector}")
                    break
            except:
                continue
        
        if not login_button:
            print("❌ ログインボタンが見つかりません")
            await self.helper.save_screenshot(self.page, "auto_error_no_button.png")
            return False
        
        # ログインボタンをクリック（複数の方法を試行）
        print("\n🖱️  ログインボタンをクリック...")
        
        click_success = False
        
        # 方法1: 通常のクリック
        try:
            await login_button.click(timeout=5000)
            print("✓ 通常クリック完了")
            click_success = True
        except Exception as e1:
            print(f"⚠️  通常クリック失敗: {e1}")
            
            # 方法2: JavaScriptクリック
            try:
                await login_button.evaluate("el => el.click()")
                print("✓ JavaScriptクリック完了")
                click_success = True
            except Exception as e2:
                print(f"⚠️  JavaScriptクリック失敗: {e2}")
                
                # 方法3: フォースクリック
                try:
                    await login_button.click(force=True, timeout=5000)
                    print("✓ フォースクリック完了")
                    click_success = True
                except Exception as e3:
                    print(f"⚠️  フォースクリック失敗: {e3}")
                    
                    # 方法4: ページのsubmitを実行
                    try:
                        await self.page.evaluate("""
                            () => {
                                const forms = document.querySelectorAll('form');
                                if (forms.length > 0) {
                                    forms[0].submit();
                                    return true;
                                }
                                return false;
                            }
                        """)
                        print("✓ フォームsubmit完了")
                        click_success = True
                    except Exception as e4:
                        print(f"❌ すべてのクリック方法が失敗: {e4}")
        
        if not click_success:
            print("\n⚠️  自動クリックに失敗しました")
            await self.helper.save_screenshot(self.page, "auto_click_failed.png")
            print("🖱️  手動でログインボタンをクリックしてください（30秒待機）")
            await self.helper.safe_wait(30000)
            # 手動クリック後も続行
            click_success = True
        
        # ログイン後のページ遷移を待機
        print("\n⏳ ログイン処理中...")
        await self.helper.safe_wait(5000)
        await self.helper.safe_wait(5000)
        
        # 現在のURL確認
        current_url = self.page.url
        print(f"📍 現在のURL: {current_url}")
        
        # ログイン成功判定
        if "login" not in current_url.lower() or "mypage" in current_url.lower():
            print("✅ ログイン成功！")
            await self.helper.save_screenshot(self.page, "auto_03_success.png")
            
            # ページタイトル表示
            page_title = await self.page.title()
            print(f"📄 ページタイトル: {page_title}")
            
            return True
        else:
            print("⚠️  ログイン後のページ遷移を確認中...")
            await self.helper.save_screenshot(self.page, "auto_03_after_login.png")
            
            # エラーメッセージ確認
            error_selectors = [
                '.error-message',
                '.alert-danger',
                '[class*="error"]'
            ]
            
            for selector in error_selectors:
                try:
                    error_elem = await self.page.query_selector(selector)
                    if error_elem:
                        error_text = await error_elem.inner_text()
                        print(f"⚠️  エラーメッセージ: {error_text}")
                except:
                    pass
            
            print("\n⏱️  5秒待機して最終確認...")
            await self.helper.safe_wait(5000)
            
            final_url = self.page.url
            print(f"📍 最終URL: {final_url}")
            await self.helper.save_screenshot(self.page, "auto_04_final.png")
            
            return "login" not in final_url.lower()


async def main():
    """メイン実行関数"""
    config = Settings()
    
    print("\n" + "=" * 60)
    print("e+ 自動ログインテスト")
    print("=" * 60)
    
    # スクリーンショットディレクトリ作成
    Path(config.screenshot_dir).mkdir(parents=True, exist_ok=True)
    
    async with BrowserHelper(config) as helper:
        page = await helper.create_page()
        flow = AutoLoginFlow(page, helper, config)
        success = await flow.execute()
        
        if success:
            print("\n" + "=" * 60)
            print("✅ 自動ログインテスト成功！")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ 自動ログインテスト失敗")
            print("=" * 60)
            print("\n📸 スクリーンショットを確認してください:")
            print(f"   {config.screenshot_dir}")
            print("\n⏱️  ブラウザは60秒後に閉じます")
            await asyncio.sleep(60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  ユーザーによる中断")
