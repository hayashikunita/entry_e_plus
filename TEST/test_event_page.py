"""イベントページ移動の単純テスト"""
import asyncio
from src.browser import BrowserHelper
from src.config import settings


async def main():
    """メイン処理"""
    print("=" * 80)
    print("🔍 イベントページ移動テスト")
    print("=" * 80)
    print()
    print(f"イベントID: {settings.event_id}")
    print()
    
    async with BrowserHelper(settings) as helper:
        try:
            page = await helper.create_page()
            
            # 直接イベントページに移動してみる
            event_url = f"https://eplus.jp/sf/detail/{settings.event_id}"
            print(f"📍 移動先URL: {event_url}")
            print()
            
            print("⏳ ページ読み込み中...")
            response = await page.goto(event_url, wait_until="domcontentloaded", timeout=30000)
            
            print(f"✅ レスポンスステータス: {response.status}")
            print(f"📍 最終URL: {page.url}")
            
            await helper.safe_wait(3000)
            await helper.save_screenshot(page, "direct_event_page.png")
            
            # ページタイトル
            title = await page.title()
            print(f"📄 ページタイトル: {title}")
            print()
            
            # ページ内容の一部を表示
            body_html = await page.content()
            print(f"📝 HTML長さ: {len(body_html)} 文字")
            
            # エラーメッセージがあるか確認
            error_messages = await page.query_selector_all(".error, .alert, .message--error")
            if error_messages:
                print(f"⚠️  エラーメッセージが見つかりました: {len(error_messages)}個")
                for i, elem in enumerate(error_messages[:3]):
                    text = await elem.inner_text()
                    print(f"   {i+1}. {text}")
            
            # 本文テキストの一部
            body_text = await page.evaluate("() => document.body.innerText")
            print()
            print("📋 ページ内容（最初の500文字）:")
            print("-" * 80)
            print(body_text[:500])
            print("-" * 80)
            print()
            
            # ログインが必要かチェック
            login_form = await page.query_selector("form[action*='login']")
            if login_form:
                print("⚠️  ログインフォームが検出されました - ログインが必要です")
            
            # 「次へ」ボタンを探す
            print("🔍 「次へ」ボタンを探しています...")
            next_button = await page.query_selector("button:has-text('次へ'), a:has-text('次へ')")
            if next_button:
                is_visible = await next_button.is_visible()
                print(f"✅ 「次へ」ボタンが見つかりました (visible={is_visible})")
            else:
                print("⚠️  「次へ」ボタンが見つかりません")
            
            print()
            print("=" * 80)
            print("⏳ 60秒間ブラウザを開いたままにします（手動確認用）")
            print("=" * 80)
            await helper.safe_wait(60000)
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()
            
            try:
                await helper.save_screenshot(page, "error_page.png")
            except:
                pass


if __name__ == "__main__":
    asyncio.run(main())
