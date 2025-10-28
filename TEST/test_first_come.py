"""先着チケット購入フローのテストスクリプト"""
import asyncio
import os
import sys

# プロジェクトルートをパスに追加（このファイルは TEST/ 配下から直接実行されるため）
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.browser import BrowserHelper
from src.config import settings
from src.flows.first_come import FirstComeFlow


async def main():
    """メイン処理"""
    print("=" * 80)
    print("🎫 e+ 先着チケット購入フロー テスト")
    print("=" * 80)
    print()
    print("設定情報:")
    print(f"  📧 メールアドレス: {settings.eplus_email}")
    print(f"  🎪 イベントID: {settings.event_id}")
    print(f"  🎟️  購入枚数: {settings.ticket_count}枚")
    print(f"  📅 公演選択: インデックス {settings.performance_index}")
    print(f"  🎭 席種選択: インデックス {settings.seat_type_index}")
    print(f"  💳 支払方法: {settings.payment_method}")
    print(f"  📦 受取方法: {settings.delivery_method}")
    print()
    print("=" * 80)
    print()
    
    # イベントIDが設定されているか確認
    if not settings.event_id:
        print("❌ エラー: EVENT_IDが.envファイルに設定されていません")
        print("   例: EVENT_ID=0424600001-P0030270")
        return
    
    async with BrowserHelper(settings) as helper:
        try:
            # ブラウザページを作成
            page = await helper.create_page()
            
            # 先着チケット購入フローを実行
            flow = FirstComeFlow(page, helper, settings)
            success = await flow.execute()
            
            if success:
                print()
                print("=" * 80)
                print("✅ フロー実行完了")
                print("=" * 80)
                print()
                print("⚠️  注意: 最終確認と送信は手動で行ってください")
                print("   （誤発注防止のため、自動送信は実装していません）")
            else:
                print()
                print("=" * 80)
                print("❌ フロー実行失敗")
                print("=" * 80)
                print()
                print("スクリーンショットを確認してください:")
                print(f"  {settings.screenshot_dir}/")
            
        except Exception as e:
            print()
            print("=" * 80)
            print(f"❌ 予期しないエラー: {e}")
            print("=" * 80)
            import traceback
            traceback.print_exc()


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        # Ctrl+Cで中断しても、async with のコンテキストマネージャにより
        # ブラウザはクリーンに閉じられ、動画も保存されます。
        print("\n🛑 中断されました（Ctrl+C）。後処理を実行して終了します。")
