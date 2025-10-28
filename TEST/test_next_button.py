"""「次へ」ボタン検出テスト"""
import asyncio
from src.browser import BrowserHelper
from src.config import settings


async def main():
    """メイン処理"""
    print("=" * 80)
    print("🔍 「次へ」ボタン検出テスト")
    print("=" * 80)
    print()
    
    async with BrowserHelper(settings) as helper:
        try:
            page = await helper.create_page()
            
            # イベントページに移動
            event_url = f"https://eplus.jp/sf/detail/{settings.event_id}"
            print(f"📍 イベントページに移動: {event_url}")
            await page.goto(event_url, wait_until="domcontentloaded")
            await helper.safe_wait(3000)
            await helper.save_screenshot(page, "next_button_test_01_initial.png")
            
            print()
            print("=" * 80)
            print("🔍 全ボタンとリンクをスキャン中...")
            print("=" * 80)
            
            # すべてのボタンを取得
            buttons = await page.query_selector_all("button")
            print(f"\n📍 ボタン要素: {len(buttons)}個")
            for i, btn in enumerate(buttons[:20]):  # 最初の20個
                try:
                    text = await btn.inner_text()
                    is_visible = await btn.is_visible()
                    classes = await btn.get_attribute("class") or ""
                    btn_type = await btn.get_attribute("type") or ""
                    print(f"  {i+1}. '{text.strip()}' (visible={is_visible}, class='{classes}', type='{btn_type}')")
                except:
                    pass
            
            # すべてのリンクを取得
            links = await page.query_selector_all("a")
            print(f"\n📍 リンク要素: {len(links)}個")
            for i, link in enumerate(links[:20]):  # 最初の20個
                try:
                    text = await link.inner_text()
                    is_visible = await link.is_visible()
                    href = await link.get_attribute("href") or ""
                    classes = await link.get_attribute("class") or ""
                    if text.strip():
                        print(f"  {i+1}. '{text.strip()}' (visible={is_visible}, class='{classes}')")
                except:
                    pass
            
            print()
            print("=" * 80)
            print("🔍 「次へ」「申込」「購入」などのキーワードで検索")
            print("=" * 80)
            
            # キーワードで検索
            keywords = ["次へ", "申込", "購入", "申し込み", "エントリー", "受付", "予約"]
            for keyword in keywords:
                elements = await page.query_selector_all(f"button:has-text('{keyword}'), a:has-text('{keyword}')")
                if elements:
                    print(f"\n✅ '{keyword}' を含む要素: {len(elements)}個")
                    for i, elem in enumerate(elements[:5]):
                        try:
                            text = await elem.inner_text()
                            is_visible = await elem.is_visible()
                            tag = await elem.evaluate("el => el.tagName")
                            print(f"   {i+1}. <{tag}> '{text.strip()}' (visible={is_visible})")
                        except:
                            pass
            
            print()
            print("=" * 80)
            print("📋 ページの主要なテキスト内容")
            print("=" * 80)
            body_text = await page.evaluate("() => document.body.innerText")
            print(body_text[:1000])
            
            print()
            print("=" * 80)
            print("⏳ 60秒間ブラウザを開いたまま（手動確認用）")
            print("=" * 80)
            await helper.safe_wait(60000)
            
        except Exception as e:
            print(f"❌ エラー: {e}")
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
