#!/usr/bin/env python3
"""
自動ログイン実行例
このスクリプトを実行すると自動でe+にログインします
"""

import asyncio
from pathlib import Path

from src.config import Settings
from src.browser import BrowserHelper
from src.auto_login import auto_login


async def main():
    """メイン実行関数"""
    print("\n" + "=" * 60)
    print("🔐 e+ 自動ログイン")
    print("=" * 60)
    
    # 設定読み込み
    config = Settings()
    
    # スクリーンショットディレクトリ作成
    Path(config.screenshot_dir).mkdir(parents=True, exist_ok=True)
    
    # ブラウザ起動
    async with BrowserHelper(config) as helper:
        page = await helper.create_page()
        
        # 自動ログイン実行
        success = await auto_login(page, helper, config)
        
        if success:
            print("\n" + "=" * 60)
            print("✅ ログイン完了！")
            print("=" * 60)
        else:
            print("\n" + "=" * 60)
            print("❌ ログイン失敗")
            print("=" * 60)
            print("\n以下を確認してください:")
            print("1. .envファイルにEPLUS_EMAIL, EPLUS_PASSWORDが設定されている")
            print("2. メールアドレス・パスワードが正しい")
            print("3. CAPTCHAが表示されていないか")
            print(f"4. スクリーンショット確認: {config.screenshot_dir}\n")
            
            await asyncio.sleep(10)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⚠️  ユーザーによる中断")
