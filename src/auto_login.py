#!/usr/bin/env python3
"""完全自動ログイン機能付きフローヘルパー"""

from playwright.async_api import Page
from .browser import BrowserHelper
from .config import Settings


async def auto_login(page: Page, helper: BrowserHelper, config: Settings) -> bool:
    """
    完全自動ログイン関数
    
    Args:
        page: Playwrightページオブジェクト
        helper: ブラウザヘルパー
        config: 設定オブジェクト
    
    Returns:
        bool: ログイン成功時True
    """
    print("\n🔐 自動ログイン開始...")
    
    # 認証情報確認
    if not config.eplus_email or not config.eplus_password:
        print("❌ エラー: .envファイルにEPLUS_EMAILとEPLUS_PASSWORDが設定されていません")
        return False
    
    print(f"✓ ログイン情報読み込み: {config.eplus_email}")
    
    # e+ トップページにアクセス
    try:
        await page.goto("https://eplus.jp/", wait_until="domcontentloaded", timeout=30000)
        await helper.safe_wait(2000)
        print("✓ e+トップページアクセス完了")
    except Exception as e:
        print(f"❌ ページアクセスエラー: {e}")
        return False
    
    # トップページのログインボタンをクリック
    print("🔍 ログインボタン検索中...")
    top_login_selectors = [
        'a:has-text("ログイン")',
        'button:has-text("ログイン")',
        'a[href*="login"]',
        '.header-login'
    ]
    
    login_clicked = False
    for selector in top_login_selectors:
        try:
            top_login_btn = await page.wait_for_selector(selector, timeout=3000, state="visible")
            if top_login_btn:
                await top_login_btn.click()
                print(f"✓ ログインボタンクリック: {selector}")
                await helper.safe_wait(2000)
                login_clicked = True
                break
        except:
            continue
    
    if not login_clicked:
        print("⚠️  ログインボタンが見つかりません（すでにログイン済みの可能性）")
    
    # メールアドレス入力欄を検出
    email_selectors = [
        'input[name="login_id"]',  # e+の実際のセレクタ
        'input[type="email"]',
        'input[name="loginid"]',
        'input[id="loginid"]',
        'input[placeholder*="メール"]',
        'input[placeholder*="ID"]'
    ]
    
    email_input = None
    for selector in email_selectors:
        try:
            email_input = await page.wait_for_selector(selector, timeout=5000, state="visible")
            if email_input:
                print(f"✓ メール入力欄検出: {selector}")
                break
        except:
            continue
    
    if not email_input:
        print("⚠️  メール入力欄が見つかりません（すでにログイン済みの可能性）")
        # ログイン済みかチェック
        current_url = page.url
        if "login" not in current_url.lower():
            print("✅ すでにログイン済みです")
            return True
        return False
    
    # パスワード入力欄を検出
    password_selectors = [
        'input[name="login_pw"]',  # e+の実際のセレクタ
        'input[type="password"]',
        'input[name="password"]',
        'input[id="password"]'
    ]
    
    password_input = None
    for selector in password_selectors:
        try:
            password_input = await page.wait_for_selector(selector, timeout=5000, state="visible")
            if password_input:
                print(f"✓ パスワード入力欄検出: {selector}")
                break
        except:
            continue
    
    if not password_input:
        print("❌ パスワード入力欄が見つかりません")
        return False
    
    # ログイン情報を入力
    print("📝 ログイン情報入力中...")
    try:
        await email_input.fill(config.eplus_email)
        print(f"✓ メールアドレス入力完了")
        
        await helper.safe_wait(500)
        await password_input.fill(config.eplus_password)
        print(f"✓ パスワード入力完了")
        
        await helper.save_screenshot(page, "auto_login_filled.png")
    except Exception as e:
        print(f"❌ 入力エラー: {e}")
        return False
    
    # ログインボタンを検出してクリック
    submit_selectors = [
        'button.button--primary.button--block:has-text("ログイン")',  # e+の実際のセレクタ
        'button:has-text("ログイン")',
        'button[type="submit"]',
        'input[type="submit"]',
        'button:has-text("ログインする")'
    ]
    
    submit_button = None
    for selector in submit_selectors:
        try:
            submit_button = await page.wait_for_selector(selector, timeout=3000, state="visible")
            if submit_button:
                print(f"✓ ログインボタン検出: {selector}")
                break
        except:
            continue
    
    if not submit_button:
        print("❌ ログインボタンが見つかりません")
        return False
    
    # ログインボタンをクリック（複数の方法を試行）
    print("🖱️  ログイン実行中...")
    
    # 方法1: 通常のクリック
    click_success = False
    try:
        await submit_button.click(timeout=5000)
        print("✓ 通常クリック完了")
        click_success = True
    except Exception as e1:
        print(f"⚠️  通常クリック失敗: {e1}")
        
        # 方法2: JavaScriptクリック
        try:
            await submit_button.evaluate("el => el.click()")
            print("✓ JavaScriptクリック完了")
            click_success = True
        except Exception as e2:
            print(f"⚠️  JavaScriptクリック失敗: {e2}")
            
            # 方法3: フォースクリック
            try:
                await submit_button.click(force=True, timeout=5000)
                print("✓ フォースクリック完了")
                click_success = True
            except Exception as e3:
                print(f"⚠️  フォースクリック失敗: {e3}")
                
                # 方法4: セレクタから再取得してクリック
                try:
                    for selector in submit_selectors:
                        try:
                            btn = await page.query_selector(selector)
                            if btn:
                                await btn.evaluate("el => el.click()")
                                print(f"✓ セレクタ再取得クリック完了: {selector}")
                                click_success = True
                                break
                        except:
                            continue
                except Exception as e4:
                    print(f"❌ すべてのクリック方法が失敗: {e4}")
    
    if not click_success:
        print("❌ ログインボタンのクリックに失敗しました")
        print("📸 現在の状態をスクリーンショット保存します")
        await helper.save_screenshot(page, "auto_login_click_failed.png")
        print("\n⚠️  手動でログインボタンをクリックしてください（30秒待機）")
        await helper.safe_wait(30000)
        # 手動クリック後も続行
        click_success = True
    
    # ログイン成功判定
    current_url = page.url
    print(f"📍 現在のURL: {current_url}")
    
    if "login" not in current_url.lower() or "mypage" in current_url.lower():
        print("✅ ログイン成功！")
        await helper.save_screenshot(page, "auto_login_success.png")
        print("⏳ 60分間待機します...")
        await helper.safe_wait(3600000)  # 60分 = 3600秒 = 3600000ミリ秒
        return True
    else:
        print("⚠️  ログイン状態を確認中...")
        final_url = page.url
        success = "login" not in final_url.lower()
        
        if success:
            print("✅ ログイン成功！")
            await helper.save_screenshot(page, "auto_login_success.png")
            print("⏳ 60分間待機します...")
            await helper.safe_wait(3600000)  # 60分 = 3600秒 = 3600000ミリ秒
        else:
            print("❌ ログイン失敗")
            await helper.save_screenshot(page, "auto_login_failed.png")
        
        return success
