"""設定管理モジュール"""
from pathlib import Path
from typing import Optional
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """アプリケーション設定"""
    
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=False,
        extra="ignore"
    )
    
    # e+ ログイン情報
    eplus_email: str = ""
    eplus_password: str = ""
    
    # チケット購入設定
    event_id: str = ""  # 例: 0424600001-P0030270
    
    # キーワードベースの選択（優先）
    performance_keyword: str = ""  # 公演日時のキーワード（例: "2025/11/15", "15日", "昼公演"）
    seat_type_keyword: str = ""  # 席種のキーワード（例: "S席", "指定席", "全席指定"）
    ticket_count: int = 1  # 購入枚数
    
    # インデックスベースの選択（フォールバック用）
    performance_index: int = 0  # 公演日時の選択（0から始まるインデックス）
    seat_type_index: int = 0  # 席種の選択（0から始まるインデックス）
    
    # 支払・受取設定
    payment_method: str = "クレジットカード"  # 支払方法
    delivery_method: str = "スマチケ"  # 受取方法
    
    # 録画・マスキング設定
    video_enabled: bool = False  # ブラウザ操作の録画を有効化
    video_dir: Path = Path("videos")  # 録画ファイルの保存先
    mask_personal_info: bool = True  # 画面上の個人情報をマスク（CSS/MutationObserver）
    keep_open_minutes: int = 0  # フロー完了後の待機分数（0で待機なし＝完了後すぐブラウザ終了）

    # OpenAI API
    openai_api_key: str = ""
    
    # ブラウザ設定
    headless: bool = False
    timeout_ms: int = 30000
    screenshot_dir: Path = Path("screenshots")
    
    # AI支援機能
    use_ai_selector: bool = True
    ai_model: str = "gpt-4o-mini"
    
    # デバッグ設定
    debug: bool = True
    
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # スクリーンショットディレクトリを作成
        self.screenshot_dir.mkdir(parents=True, exist_ok=True)
        # ビデオディレクトリを作成
        if self.video_enabled:
            Path(self.video_dir).mkdir(parents=True, exist_ok=True)


# グローバル設定インスタンス
settings = Settings()
