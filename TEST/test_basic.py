#!/usr/bin/env python3
"""基本動作確認テスト - ブラウザ起動とページアクセス"""

import asyncio
from playwright.async_api import async_playwright

async def test_basic_browser():
    """ブラウザ起動とページアクセスの基本テスト"""
    print("🚀 Playwrightブラウザ起動テスト開始...")
    
    async with async_playwright() as p:
        print("✓ Playwright初期化完了")
        
        # ブラウザ起動（ヘッドレスモード）
        browser = await p.chromium.launch(headless=True)
        print("✓ Chromiumブラウザ起動完了")
        
        # コンテキスト作成
        context = await browser.new_context(
            viewport={"width": 1280, "height": 800},
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/120.0.0.0"
        )
        print("✓ ブラウザコンテキスト作成完了")
        
        # ページ作成
        page = await context.new_page()
        print("✓ 新しいページ作成完了")
        
        # テストページにアクセス（example.com）
        try:
            await page.goto("https://example.com", wait_until="domcontentloaded", timeout=30000)
            print("✓ example.comへのアクセス成功")
            
            # タイトル取得
            title = await page.title()
            print(f"  ページタイトル: {title}")
            
            # HTML取得（最初の100文字）
            html = await page.content()
            print(f"  HTML長: {len(html)} 文字")
            print(f"  HTML抜粋: {html[:100]}...")
            
        except Exception as e:
            print(f"❌ ページアクセスエラー: {e}")
        
        # クリーンアップ
        await context.close()
        await browser.close()
        print("✓ ブラウザクローズ完了")
    
    print("\n✅ 基本動作確認テスト完了！")

if __name__ == "__main__":
    asyncio.run(test_basic_browser())
