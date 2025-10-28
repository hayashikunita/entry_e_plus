# e+ チケット購入自動化ツール（先着・抽選対応）

> ⚠️ 注意: このツールは教育・検証用途のサンプルです。各サイトの利用規約と法令を厳守し、最終確認・送信（申込確定）は必ず手動で行ってください。CAPTCHAや本人認証は自動化しません。

## 概要

Python + Playwright を用いて e+（イープラス）のチケット申込を自動化するツールです。先着（受付中→次へ）フローを中心に、抽選応募やログイン補助、スクショ・録画、個人情報マスクまでカバーします。

主な機能
- ログイン自動化（iframe対応の広範なセレクタ）
- 先着フロー（イベント詳細→最新の「受付中」→「次へ」→公演/席種/枚数選択→ログイン→支払/受取→確認画面へ）
- 抽選応募/即購入の簡易CLI（main.py）
- キーワード/インデックス指定による選択（公演日時・席種・枚数）
- コンビニ優先の支払/受取（ファミマ/セブンのラベルを自動判定）
- スクリーンショット自動保存（各ステップ）
- 画面録画（.webm）と個人情報マスク（CSS blur + MutationObserver）

## 動画の説明（録画とデモ）

- 録画の有効化: `.env` に `VIDEO_ENABLED=true` を設定（保存先は `VIDEO_DIR`、既定は `videos/`）。
- 保存場所: `videos/` 配下にページごとのサブフォルダが作成され、`.webm` が出力されます（Playwright の仕様）。
- 中断時の保存: Ctrl+C で中断しても、ページ→コンテキスト→ブラウザを閉じる段階で録画が保存されます。
- 説明用デモ動画（固定ファイル）
    - 先着フローの説明用デモ: `videos/demo/first_come_overview.webm`
    - 自動録画とは別のサンプル動画の配置場所です。必要に応じてファイル名は変更し、README の記載も合わせて更新してください。

詳細な保存先や確認方法は「スクリーンショット/動画の保存場所」を参照してください。

## セットアップ

前提
- Windows 10/11（PowerShell）
- Python 3.10+（推奨 3.12 以降）

インストール
```powershell
# 仮想環境（推奨）
python -m venv .venv
.\.venv\Scripts\Activate.ps1

# 依存パッケージ
pip install -r requirements.txt

# Playwright ブラウザ（Chromium）
playwright install chromium
```

## 環境変数（.env）

最小構成（例）
```env
EPLUS_EMAIL=your_email@example.com
EPLUS_PASSWORD=your_password
EVENT_ID=0157880001-P0030158
HEADLESS=false
DEBUG=true
```

詳細オプション（必要に応じて）
```env
# 選択キーワード（優先）
PERFORMANCE_KEYWORD=2025/11/15     # 公演日時の一部（NFKC正規化・大文字小文字無視）
SEAT_TYPE_KEYWORD=スタンドＢ席     # 席種の一部
TICKET_COUNT=1                     # 枚数（例: 1）

# フォールバックのインデックス（0始まり）
PERFORMANCE_INDEX=0
SEAT_TYPE_INDEX=0

# 支払/受取（ラジオ判定に使用）
PAYMENT_METHOD=クレジットカード   # 例: クレジットカード / コンビニ
DELIVERY_METHOD=スマチケ           # 例: スマチケ / ファミリーマート / セブン-イレブン

# 録画・マスク
VIDEO_ENABLED=true                 # 動画録画の有効/無効
VIDEO_DIR=videos                   # 保存先（既定: videos）
MASK_PERSONAL_INFO=true            # メール/パスワード/カード関連のぼかし＋メール文字列伏字

# フロー完了後の待機分数（0なら即終了）
KEEP_OPEN_MINUTES=0
```

備考
- EVENT_ID はイベント詳細 URL の `https://eplus.jp/sf/detail/<EVENT_ID>` に入る文字列です（例: `0157880001-P0030158`）。
- キーワードは全角/半角や大小文字を吸収して部分一致します。
- 枚数は「n枚」または option value の末尾「/n」で判定します。

## 使い方（おすすめ：先着フローのテスト実行）

最も実用的な先着フローを試すには、以下を実行します。
```powershell
python .\TEST\test_first_come.py
```
フローの流れ
1) イベント詳細へ移動（`https://eplus.jp/sf/detail/EVENT_ID`）
2) 最新の「受付中」に紐づく「次へ」を検出してクリック
3) 公演日時/席種/枚数を選択（キーワード優先→枚数ルール→インデックス）
4) ログイン（iframe内も探索）
5) 受取（ファミマ/セブンをテキスト判定）・支払（コンビニ/ATM優先）を自動選択
6) 最後に「次へ」をクリックして確認画面へ（最終送信は手動）

出力
- スクショ: `screenshots/` に各ステップの PNG
- 動画: `videos/`（VIDEO_ENABLED=true のとき）。各ページのサブフォルダ配下に `.webm`

Ctrl+C で中断したとき
- with コンテキストのクリーンアップによりページ→コンテキスト→ブラウザの順で閉じます。録画はこのタイミングで保存されます。

## 使い方（CLI：抽選・即購入の簡易フロー）

簡易的な CLI も利用できます（手動ログイン前提）。
```powershell
# ログインのみ（手動）
python .\main.py login-only

# 抽選応募（手動ログイン→応募）
python .\main.py lottery --url "https://eplus.jp/event/xxxxx"

# 即購入（手動ログイン→購入）
python .\main.py purchase --url "https://eplus.jp/event/xxxxx"
```
オプション
- `--headless`: ヘッドレス実行
- `--no-ai`: AI支援を無効化

## スクリーンショット/動画の保存場所

- スクリーンショット: `screenshots/step*_*.png`
- 動画: `videos/`（VIDEO_ENABLED=true）
    - 例: `videos/…/trace.webm`（Playwright 仕様でサブフォルダが作成されます）


動画が見当たらない場合
- `.env` に `VIDEO_ENABLED=true` があるか
- 実行終了（または Ctrl+C 中断）まで待ったか（ページ/コンテキストを閉じたタイミングで保存）
- `videos/` を再帰で確認
```powershell
if (Test-Path .\videos) { Get-ChildItem -Recurse .\videos }
```

## トラブルシューティング

- 「受付中/次へ」が見つからない
    - 発売前の場合は待機ループに入ります。発売直後は数秒ポーリングしています。
    - ページ構造が異なる場合はスクショ（`screenshots/step2_*`）をご共有ください。
- 公演/席種/枚数の選択がずれる
    - キーワードの表記ゆれ（全角/半角）に注意。より具体的に（例: `アリーナS席`）。
    - インデックス（0始まり）でのフォールバックも設定可能。
- ログイン要素が見つからない
    - 端末やイベントで iframe が変わる場合があります。`step4_*` のスクショをご確認ください。
- 終了時に TargetClosedError が出る
    - 長時間保持後の終了で稀に出る Playwright の既知事象です。録画/スクショには影響しません。

## プロジェクト構成（抜粋）

```
entry_e_plus/
├── main.py                     # 簡易CLI（手動ログイン前提の抽選/即購入）
├── TEST/                       # テストスクリプト一式
│   ├── test_first_come.py      # 先着フローの実行（おすすめ）
│   ├── test_login.py           # ログイン確認
│   ├── test_auto_login.py      # 自動ログイン確認
│   ├── test_event_page.py      # イベントページ確認
│   ├── test_next_button.py     # 「次へ」検出確認
│   └── test_step_by_step.py    # ステップごとの確認
├── requirements.txt
├── .env
├── screenshots/
├── videos/
└── src/
        ├── config.py               # 設定（.env 読み込み、録画/マスク/待機など）
    ├── browser.py              # Playwright起動・録画・マスク注入
        ├── flows/
        │   ├── base.py
        │   ├── first_come.py       # 先着フロー本体
        │   ├── lottery.py          # 抽選フロー（CLI用）
        │   └── purchase.py         # 即購入フロー（CLI用）
        └── ...
```

## ライセンス / 免責

- MIT License
- 本ツールの使用によって生じたいかなる損害についても、作者は責任を負いません。利用は自己責任でお願いします。

---
最終更新: 2025-10-28
