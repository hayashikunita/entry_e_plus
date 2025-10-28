#!/usr/bin/env python3
"""
e+ チケット購入自動化メインスクリプト
"""

import asyncio
import argparse
from pathlib import Path

from src.config import Settings
from src.browser import BrowserHelper
from src.flows.lottery import LotteryEntryFlow
from src.flows.purchase import QuickPurchaseFlow

async def run_login_only(config: Settings):
    """ログインのみ実行"""
    print("\n🔐 ログインモード")
    
    async with BrowserHelper(config) as helper:
        page = await helper.create_page()
        
        # e+ トップページにアクセス
        await page.goto("https://eplus.jp/", timeout=30000)
        await helper.safe_wait(3000)
        
        print("✓ e+ トップページにアクセスしました")
        print("🖱️  手動でログインしてください（120秒待機）")
        
        await helper.save_screenshot(page, "manual_login_01_top.png")
        await helper.safe_wait(120000)
        
        await helper.save_screenshot(page, "manual_login_02_after.png")
        print("✅ ログイン完了")


async def run_lottery_entry(config: Settings, event_url: str):
    """抽選応募フロー実行"""
    print("\n🎫 抽選応募モード")
    
    async with BrowserHelper(config) as helper:
        page = await helper.create_page()
        
        # まずログイン
        print("\n📝 ログイン処理...")
        await page.goto("https://eplus.jp/", timeout=30000)
        await helper.safe_wait(3000)
        
        print("🖱️  手動でログインしてください（60秒待機）")
        await helper.safe_wait(60000)
        
        # 抽選フロー実行
        flow = LotteryEntryFlow(page, helper, config, event_url)
        await flow.execute()
        
        print("\n⏱️  ブラウザは30秒後に閉じます")
        await asyncio.sleep(30)


async def run_quick_purchase(config: Settings, event_url: str):
    """即購入フロー実行"""
    print("\n⚡ 即購入モード（先着順）")
    
    async with BrowserHelper(config) as helper:
        page = await helper.create_page()
        
        # まずログイン
        print("\n📝 ログイン処理...")
        await page.goto("https://eplus.jp/", timeout=30000)
        await helper.safe_wait(3000)
        
        print("🖱️  手動でログインしてください（60秒待機）")
        await helper.safe_wait(60000)
        
        # 即購入フロー実行
        flow = QuickPurchaseFlow(page, helper, config, event_url)
        await flow.execute()
        
        print("\n⏱️  ブラウザは30秒後に閉じます")
        await asyncio.sleep(30)


def main():
    """メイン関数"""
    parser = argparse.ArgumentParser(
        description="e+ チケット購入自動化ツール",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
使用例:
  # ログインのみ
  python main.py login-only
  
  # 抽選応募
  python main.py lottery --url "https://eplus.jp/event/xxxxx"
  
  # 即購入（先着順）
  python main.py purchase --url "https://eplus.jp/event/xxxxx"
  
注意事項:
  - CAPTCHA等は手動で対応してください
  - 最終的な購入確定は必ず手動で確認してください
  - .envファイルにログイン情報を設定してください
        """
    )
    
    parser.add_argument(
        "mode",
        choices=["login-only", "lottery", "purchase"],
        help="実行モード"
    )
    
    parser.add_argument(
        "--url",
        type=str,
        help="イベントURL（lotteryまたはpurchaseモードで必須）"
    )
    
    parser.add_argument(
        "--headless",
        action="store_true",
        help="ヘッドレスモードで実行"
    )
    
    parser.add_argument(
        "--no-ai",
        action="store_true",
        help="AI支援機能を無効化"
    )
    
    args = parser.parse_args()
    
    # 設定読み込み
    config = Settings()
    
    # コマンドライン引数で上書き
    if args.headless:
        config.headless = True
    
    if args.no_ai:
        config.use_ai_selector = False
    
    # スクリーンショットディレクトリ作成
    Path(config.screenshot_dir).mkdir(parents=True, exist_ok=True)
    
    # モード別実行
    if args.mode == "login-only":
        asyncio.run(run_login_only(config))
    
    elif args.mode == "lottery":
        if not args.url:
            parser.error("lottery モードでは --url が必要です")
        asyncio.run(run_lottery_entry(config, args.url))
    
    elif args.mode == "purchase":
        if not args.url:
            parser.error("purchase モードでは --url が必要です")
        asyncio.run(run_quick_purchase(config, args.url))
    
    print("\n✅ すべての処理が完了しました")


if __name__ == "__main__":
    main()
