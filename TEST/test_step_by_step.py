"""ステップごとにテストするスクリプト"""
import asyncio
from src.browser import BrowserHelper
from src.config import settings
from src.auto_login import auto_login


async def main():
    """メイン処理"""
    print("=" * 80)
    print("🔍 ステップバイステップ デバッグテスト")
    print("=" * 80)
    print()
    print("設定情報:")
    print(f"  📧 メールアドレス: {settings.eplus_email}")
    print(f"  🎪 イベントID: {settings.event_id}")
    print()
    
    async with BrowserHelper(settings) as helper:
        try:
            # ブラウザページを作成
            page = await helper.create_page()
            
            # ステップ1: ログイン
            print("=" * 80)
            print("[ステップ1] ログインテスト")
            print("=" * 80)
            
            print("📍 e+ログインページに移動中...")
            await page.goto("https://eplus.jp/sf/login", wait_until="domcontentloaded")
            await helper.safe_wait(2000)
            await helper.save_screenshot(page, "test_01_login_page.png")
            
            print("🔐 自動ログイン実行...")
            login_success = await auto_login(page, helper, settings)
            
            if not login_success:
                print("❌ ログイン失敗")
                return
            
            print("✅ ログイン成功")
            current_url = page.url
            print(f"   現在のURL: {current_url}")
            await helper.save_screenshot(page, "test_02_after_login.png")
            
            # ステップ2: イベント詳細ページへ移動
            print()
            print("=" * 80)
            print("[ステップ2] イベント詳細ページ移動テスト")
            print("=" * 80)
            
            if not settings.event_id:
                print("❌ EVENT_IDが設定されていません")
                return
            
            event_url = f"https://eplus.jp/sf/detail/{settings.event_id}"
            print(f"📍 イベントページに移動: {event_url}")
            
            try:
                await page.goto(event_url, wait_until="domcontentloaded", timeout=30000)
                await helper.safe_wait(3000)
                await helper.save_screenshot(page, "test_03_event_page.png")
                
                final_url = page.url
                print(f"✅ ページ移動成功")
                print(f"   最終URL: {final_url}")
                
                # ページタイトルを取得
                title = await page.title()
                print(f"   ページタイトル: {title}")
                
                # ページ内容を少し確認
                body_text = await page.evaluate("() => document.body.innerText")
                print(f"   ページ内容の最初の200文字:")
                print(f"   {body_text[:200]}")
                
                # 「次へ」ボタンがあるか確認
                print()
                print("🔍 「次へ」ボタンを探しています...")
                selectors = [
                    "button:has-text('次へ')",
                    "a:has-text('次へ')",
                    "button.button--primary:has-text('次へ')",
                    "button[type='submit']:has-text('次へ')",
                ]
                
                for selector in selectors:
                    try:
                        element = await page.query_selector(selector)
                        if element:
                            is_visible = await element.is_visible()
                            print(f"   ✅ 見つかりました: {selector} (visible={is_visible})")
                    except:
                        pass
                
                print()
                print("=" * 80)
                print("⏳ ブラウザを60秒間開いたままにします（手動確認用）")
                print("=" * 80)
                await helper.safe_wait(60000)
                
            except Exception as e:
                print(f"❌ ページ移動エラー: {e}")
                await helper.save_screenshot(page, "test_03_error.png")
                
                # エラー時の詳細情報
                current_url = page.url
                print(f"   現在のURL: {current_url}")
                title = await page.title()
                print(f"   ページタイトル: {title}")
                
                print()
                print("=" * 80)
                print("⏳ エラー確認のため60秒間ブラウザを開いたままにします")
                print("=" * 80)
                await helper.safe_wait(60000)
            
        except Exception as e:
            print()
            print("=" * 80)
            print(f"❌ 予期しないエラー: {e}")
            print("=" * 80)
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
