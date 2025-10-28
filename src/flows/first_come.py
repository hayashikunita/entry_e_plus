"""先着チケット購入フロー"""
import asyncio
from playwright.async_api import Page
from ..browser import BrowserHelper
from ..config import Settings
from ..auto_login import auto_login
from .base import BaseFlow


class FirstComeFlow(BaseFlow):
    """先着チケット購入フロー
    
    1. ログイン
    2. イベント詳細ページに移動
    3. 「次へ」ボタンが出現するまで待機（発売時刻まで）
    4. 公演日時・席種・枚数を選択
    5. 再ログイン
    6. 支払方法・受取方法を選択
    """
    
    def __init__(self, page: Page, helper: BrowserHelper, config: Settings):
        super().__init__(page, helper, config)
        
    async def execute(self) -> bool:
        """フローを実行"""
        try:
            print("=" * 60)
            print("🎫 先着チケット購入フロー開始")
            print("=" * 60)
            
            # ステップ1: イベント詳細ページへ移動（ログイン不要）
            if not await self._step1_navigate_to_event():
                return False
            
            # ステップ2: 「次へ」ボタン待機＆クリック
            if not await self._step2_wait_for_next_button():
                return False
            
            # ステップ3: チケット選択（公演日時・席種・枚数）
            if not await self._step3_select_tickets():
                return False
            
            # ステップ4: ログイン（チケット選択後に必要）
            if not await self._step4_login():
                return False
            
            # ステップ5: 支払方法・受取方法選択
            if not await self._step5_select_payment_delivery():
                return False
            
            print("=" * 60)
            print("✅ 先着チケット購入フロー完了")
            print("=" * 60)
            return True
            
        except Exception as e:
            print(f"❌ エラーが発生しました: {e}")
            await self.helper.save_screenshot(self.page, "first_come_error.png")
            return False
    
    async def _step1_navigate_to_event(self) -> bool:
        """ステップ1: イベント詳細ページへ移動"""
        print("\n[ステップ1] イベント詳細ページへ移動")
        print("-" * 60)
        
        try:
            event_url = f"https://eplus.jp/sf/detail/{self.config.event_id}"
            print(f"📍 イベントページに移動: {event_url}")
            
            await self.page.goto(event_url, wait_until="domcontentloaded")
            await self.helper.safe_wait(3000)
            await self.helper.save_screenshot(self.page, "step1_event_detail_page.png")
            
            print(f"✅ ステップ1完了: イベントページ表示")
            return True
            
        except Exception as e:
            print(f"❌ ステップ1でエラー: {e}")
            await self.helper.save_screenshot(self.page, "step1_error.png")
            return False
    
    async def _step2_wait_for_next_button(self) -> bool:
        """ステップ2: 「次へ」ボタンが出現するまで待機してクリック"""
        print("\n[ステップ2] 「次へ」ボタン待機")
        print("-" * 60)
        
        try:
            print("⏳ 発売時刻まで待機中...")
            print("   （「受付中」の「次へ」ボタンが出現するまでポーリングします）")
            
            max_wait_time = 3600  # 最大1時間待機
            check_interval = 2  # 2秒ごとにチェック
            elapsed_time = 0
            
            while elapsed_time < max_wait_time:
                try:
                    # ページ全体から「受付中」のテキストを探す
                    accepting_elements = await self.page.query_selector_all("text=/受付中/")
                    
                    if accepting_elements:
                        print(f"✅ 「受付中」要素を発見: {len(accepting_elements)}個")
                        
                        # 最後（一番最近）の「受付中」要素を取得
                        target_element = accepting_elements[-1]
                        
                        # その近くにある「次へ」ボタンを探す
                        # 親要素を遡って「次へ」ボタンを探す
                        parent = await target_element.evaluate_handle("el => el.closest('.eventlist__item, .item, article, section, li, div[class*=\"event\"]')")
                        
                        if parent:
                            # 親要素内の「次へ」ボタンを探す
                            next_button_selectors = [
                                "button:has-text('次へ')",
                                "a:has-text('次へ')",
                                "button.button--primary:has-text('次へ')",
                                "button[type='submit']:has-text('次へ')",
                            ]
                            
                            for selector in next_button_selectors:
                                try:
                                    button = await parent.query_selector(selector)
                                    if button and await button.is_visible():
                                        print(f"✅ 「受付中」に対応する「次へ」ボタンを発見")
                                        print("🖱️  ボタンをクリックします...")
                                        
                                        # クリック試行
                                        await self.helper.safe_wait(500)
                                        
                                        # 複数の方法でクリック
                                        try:
                                            await button.click(timeout=3000)
                                            click_success = True
                                        except:
                                            try:
                                                await self.page.evaluate("(el) => el.click()", button)
                                                click_success = True
                                            except:
                                                try:
                                                    await button.click(force=True, timeout=3000)
                                                    click_success = True
                                                except:
                                                    click_success = False
                                        
                                        if click_success:
                                            print("✅ ステップ2完了: 「次へ」ボタンクリック成功")
                                            await self.helper.safe_wait(3000)
                                            await self.helper.save_screenshot(self.page, "step2_after_next_button.png")
                                            return True
                                except:
                                    continue
                    
                    # 進捗表示
                    if elapsed_time % 60 == 0:  # 1分ごとに表示
                        print(f"   待機中... ({elapsed_time // 60}分経過)")
                    
                except Exception as check_error:
                    # チェック中のエラーは無視して次の試行へ
                    pass
                
                await asyncio.sleep(check_interval)
                elapsed_time += check_interval
            
            print(f"⚠️  タイムアウト: {max_wait_time}秒経過しても「受付中」の「次へ」ボタンが見つかりませんでした")
            await self.helper.save_screenshot(self.page, "step2_timeout.png")
            return False
            
        except Exception as e:
            print(f"❌ ステップ2でエラー: {e}")
            await self.helper.save_screenshot(self.page, "step2_error.png")
            return False
    
    async def _step3_select_tickets(self) -> bool:
        """ステップ3: チケット選択（公演日時・席種・枚数）"""
        print("\n[ステップ3] チケット選択")
        print("-" * 60)
        
        try:
            await self.helper.save_screenshot(self.page, "step3_before_ticket_selection.png")
            
            # 公演日時の選択（テーブル行の見出しベースで検出）
            print("📅 公演日時を選択中...")
            if self.config.performance_keyword:
                print(f"   キーワード: '{self.config.performance_keyword}'")
            performance_selected = False
            # まずは見出し『公演日時』行の<select>を探す
            perf_select = await self.page.query_selector("xpath=//tr[.//th[contains(normalize-space(),'公演日時')]]//select")
            # 見つからなければフォールバックの汎用セレクタ
            if not perf_select:
                for selector in [
                    "select[name*='performance']",
                    "select[name*='schedule']",
                    "select[name*='date']",
                    "#performanceSelect",
                    ".performance-select select"
                ]:
                    try:
                        el = await self.page.query_selector(selector)
                        if el:
                            perf_select = el
                            break
                    except:
                        pass
            if perf_select:
                performance_selected = await self._select_option_by_keyword_or_index(
                    perf_select,
                    keyword=self.config.performance_keyword,
                    index=self.config.performance_index,
                    skip_placeholder_auto=True
                )
            if not performance_selected:
                print("⚠️  公演日時の選択をスキップ（選択肢なし/要素未検出）")
            
            # 席種の選択（見出し『席種』行の<select>）
            print("🎭 席種を選択中...")
            if self.config.seat_type_keyword:
                print(f"   キーワード: '{self.config.seat_type_keyword}'")
            seat_selected = False
            seat_select = await self.page.query_selector("xpath=//tr[.//th[contains(normalize-space(),'席種')]]//select")
            if not seat_select:
                for selector in [
                    "select[name*='seat']",
                    "select[name*='ticket']",
                    "#seatTypeSelect",
                    ".seat-select select"
                ]:
                    try:
                        el = await self.page.query_selector(selector)
                        if el:
                            seat_select = el
                            break
                    except:
                        pass
            if seat_select:
                seat_selected = await self._select_option_by_keyword_or_index(
                    seat_select,
                    keyword=self.config.seat_type_keyword,
                    index=self.config.seat_type_index,
                    skip_placeholder_auto=True
                )
            if not seat_selected:
                print("⚠️  席種の選択をスキップ（選択肢なし/要素未検出）")
            
            # 枚数の選択（見出し『枚数』行の<select>）
            print(f"🎟️  枚数を選択中: {self.config.ticket_count}枚")
            count_selected = False
            count_select = await self.page.query_selector("xpath=//tr[.//th[contains(normalize-space(),'枚数')]]//select")
            if not count_select:
                for selector in [
                    "select[name*='count']",
                    "select[name*='quantity']",
                    "select[name*='num']",
                    "#ticketCountSelect",
                    ".count-select select"
                ]:
                    try:
                        el = await self.page.query_selector(selector)
                        if el:
                            count_select = el
                            break
                    except:
                        pass
            if count_select:
                count_selected = await self._select_option_by_keyword_or_index(
                    count_select,
                    count=self.config.ticket_count,
                    skip_placeholder_auto=True
                )
            if not count_selected:
                print("⚠️  枚数の選択をスキップ（選択肢なし/要素未検出）")
            
            await self.helper.save_screenshot(self.page, "step3_after_ticket_selection.png")
            
            # 「ログイン」ボタンをクリック
            print("🔐 ログインボタンを探しています...")
            login_button_selectors = [
                "button:has-text('ログイン')",
                "a:has-text('ログイン')",
                "button.login-button",
                "button[type='submit']:has-text('ログイン')"
            ]
            
            login_clicked = False
            for selector in login_button_selectors:
                if await self._safe_click(selector):
                    print("✅ ログインボタンクリック成功")
                    login_clicked = True
                    await self.helper.safe_wait(2000)
                    break
            
            if not login_clicked:
                print("⚠️  ログインボタンが見つかりません")
                await self.helper.save_screenshot(self.page, "step3_login_button_not_found.png")
                return False
            
            print("✅ ステップ3完了: チケット選択完了")
            return True
            
        except Exception as e:
            print(f"❌ ステップ3でエラー: {e}")
            await self.helper.save_screenshot(self.page, "step3_error.png")
            return False
    
    async def _select_option_by_keyword_or_index(
        self,
        select_el,
        keyword: str | None = None,
        index: int | None = None,
        count: int | None = None,
        skip_placeholder_auto: bool = True,
    ) -> bool:
        """<select>の<option>を選択するユーティリティ。
        優先度: keyword（完全/部分一致）→ count（『n枚』/ value末尾 '/n'）→ index（先頭プレースホルダを自動スキップ）
        """
        try:
            options = await select_el.query_selector_all("option")
            if not options:
                return False

            import unicodedata
            def _normalize(text: str) -> str:
                # 全角→半角、NBSP除去、前後空白除去、lower
                t = unicodedata.normalize('NFKC', (text or "")).replace("\xa0", " ").replace("\u3000", " ").strip()
                return t.lower()

            # 1) keyword での選択（公演日時/席種）
            if keyword:
                kw = _normalize(keyword)
                for opt in options:
                    text = _normalize(await opt.inner_text())
                    if kw in text:
                        value = await opt.get_attribute("value")
                        if value is not None:
                            await select_el.select_option(value=value)
                            print(f"   → 選択: '{text}' (value='{value}')")
                            await self.helper.safe_wait(500)
                            return True

            # 2) 枚数の選択（ラベル 'n枚' or value 末尾 '/n'）
            if count is not None:
                for opt in options:
                    text = _normalize(await opt.inner_text())
                    value = await opt.get_attribute("value") or ""
                    if f"{count}枚" in text or value.endswith(f"/{count}"):
                        await select_el.select_option(value=value)
                        print(f"   → 枚数選択: '{text}' (value='{value}')")
                        await self.helper.safe_wait(500)
                        return True

            # 3) インデックスでのフォールバック
            if index is not None:
                target_index = index
                if skip_placeholder_auto and len(options) >= 2:
                    # 先頭がプレースホルダ（空value or 『選択して下さい』）なら+1
                    first_text = _normalize(await options[0].inner_text())
                    first_val = await options[0].get_attribute("value") or ""
                    if first_val == "" or "選択して下さい" in first_text:
                        target_index = index + 1
                if 0 <= target_index < len(options):
                    value = await options[target_index].get_attribute("value")
                    text = _normalize(await options[target_index].inner_text())
                    if value is not None:
                        await select_el.select_option(value=value)
                        print(f"   → フォールバック選択: '{text}' (index={target_index}, value='{value}')")
                        await self.helper.safe_wait(500)
                        return True

            return False

        except Exception as e:
            return False

    async def _step4_login(self) -> bool:
        """ステップ4: ログイン（チケット選択後）"""
        print("\n[ステップ4] ログイン")
        print("-" * 60)
        
        try:
            await self.helper.save_screenshot(self.page, "step4_before_login.png")

            # 対象フレーム群（ページ本体＋全iframe）で探索
            frames = [self.page, *self.page.frames]

            # メール/パスワード入力
            print("📧 メールアドレスとパスワードを入力中...")
            email_filled = False
            password_filled = False
            target_frame = None

            email_selectors = [
                "input[name='login_id']",
                "input[type='email']",
                "input[name='email']",
                "#login_id",
                "input[autocomplete='username']",
                "input[placeholder*='メール']",
                "input[placeholder*='email' i]",
                "input[name*='id']"
            ]
            password_selectors = [
                "input[name='login_pw']",
                "input[type='password']",
                "input[name='password']",
                "#login_pw",
                "input[autocomplete='current-password']",
                "input[placeholder*='パスワード']"
            ]

            for fr in frames:
                try:
                    # Email
                    for sel in email_selectors:
                        el = await fr.query_selector(sel)
                        if el:
                            await el.fill(self.config.eplus_email)
                            email_filled = True
                            target_frame = fr
                            print("✅ メールアドレス入力完了")
                            break
                    # Password（同じフレームで探す）
                    if email_filled:
                        for sel in password_selectors:
                            el = await fr.query_selector(sel)
                            if el:
                                await el.fill(self.config.eplus_password)
                                password_filled = True
                                print("✅ パスワード入力完了")
                                break
                    if email_filled and password_filled:
                        break
                except:
                    continue

            if not email_filled:
                print("❌ メールアドレス入力欄が見つかりません")
                return False
            if not password_filled:
                print("❌ パスワード入力欄が見つかりません")
                return False

            await self.helper.safe_wait(500)

            # ログインボタンクリック（見つけたフレーム内を優先）
            print("🖱️  ログインボタンをクリック中...")
            login_button_selectors = [
                "button.button--primary.button--block:has-text('ログイン')",
                "button:has-text('ログイン')",
                "button[type='submit']",
                "input[type='submit']",
                "a:has-text('ログイン')"
            ]
            click_success = False
            search_frames = [target_frame] if target_frame else frames
            for fr in search_frames:
                for sel in login_button_selectors:
                    try:
                        btn = await fr.query_selector(sel)
                        if not btn:
                            continue
                        try:
                            await btn.click(timeout=3000)
                            click_success = True
                        except:
                            try:
                                await fr.evaluate("(el) => el.click()", btn)
                                click_success = True
                            except:
                                try:
                                    await btn.click(force=True, timeout=3000)
                                    click_success = True
                                except:
                                    pass
                        if click_success:
                            break
                    except:
                        continue
                if click_success:
                    break

            if not click_success:
                print("❌ ログインボタンのクリックに失敗しました")
                return False

            await self.helper.safe_wait(3000)
            await self.helper.save_screenshot(self.page, "step4_after_login.png")
            print("✅ ステップ4完了: ログイン成功")
            return True
            
        except Exception as e:
            print(f"❌ ステップ4でエラー: {e}")
            await self.helper.save_screenshot(self.page, "step4_error.png")
            return False
    
    async def _step5_select_payment_delivery(self) -> bool:
        """ステップ5: 支払方法・受取方法選択"""
        print("\n[ステップ5] 支払方法・受取方法選択")
        print("-" * 60)
        
        try:
            await self.helper.save_screenshot(self.page, "step5_before_payment_delivery.png")
            
            import unicodedata
            def _normalize(text: str) -> str:
                t = unicodedata.normalize('NFKC', (text or "")).replace("\xa0", " ").replace("\u3000", " ").strip()
                return t.lower()

            # 受取方法（コンビニ）: ラジオ name="vuketoriHohoSentaku" を優先的に選択
            # 優先順: ファミリーマート -> セブン-イレブン（configにキーワードがあれば尊重）
            print("📦 受取方法を選択中（コンビニ優先）...")
            receive_selected = False
            preferred_receive = []
            dm_norm = _normalize(self.config.delivery_method)
            if 'ファミ' in dm_norm or 'family' in dm_norm:
                preferred_receive = ['ファミリーマート', 'セブン-イレブン']
            elif 'セブン' in dm_norm or 'seven' in dm_norm:
                preferred_receive = ['セブン-イレブン', 'ファミリーマート']
            else:
                preferred_receive = ['ファミリーマート', 'セブン-イレブン']

            try:
                receive_radios = await self.page.query_selector_all("input[type='radio'][name='vuketoriHohoSentaku']")
                if receive_radios:
                    # それぞれのラジオに対応するラベル文言を取得
                    candidates = []
                    for el in receive_radios:
                        try:
                            label_text = await self.page.evaluate("(el) => { const id=el.id; const byFor=id?document.querySelector(`label[for=\"${id}\"]`):null; if(byFor){return byFor.innerText;} const wrap=el.closest('label'); return wrap?wrap.innerText:''; }", el)
                        except:
                            label_text = ""
                        candidates.append((el, label_text or ""))

                    # 優先順でマッチ
                    for pref in preferred_receive:
                        pref_n = _normalize(pref)
                        for el, label in candidates:
                            if pref_n in _normalize(label):
                                try:
                                    await el.click()
                                except:
                                    try:
                                        await self.page.evaluate("(el)=>el.click()", el)
                                    except:
                                        await el.click(force=True)
                                receive_selected = True
                                print(f"✅ 受取方法: '{pref}' を選択（label='{label.strip()}')")
                                await self.helper.safe_wait(800)
                                break
                        if receive_selected:
                            break

                    # どれも一致しなければ最初の選択肢
                    if not receive_selected and candidates:
                        try:
                            await candidates[0][0].click()
                            receive_selected = True
                            print(f"⚠️  受取方法: 既定の先頭を選択（label='{(candidates[0][1] or '').strip()}')")
                            await self.helper.safe_wait(800)
                        except:
                            pass
                else:
                    print("⚠️  受取方法のラジオが見つかりませんでした（name='vuketoriHohoSentaku'）")
            except Exception as _:
                print("⚠️  受取方法の選択時に一時的なエラー")

            if not receive_selected:
                print("⚠️  受取方法の選択をスキップ（要素未検出）")

            # 支払方法（コンビニ/ATM）: ラジオ name="vsiharaiHohoSentaku"
            # 優先は『コンビニ／ＡＴＭ』『ファミリーマート』『セブン-イレブン』等を含むもの（value=3 が目安）
            print("💳 支払方法を選択中（コンビニ優先）...")
            pay_selected = False

            # 受取方法で選んだ店舗名（あれば揃える）
            chosen_store = None
            try:
                if receive_selected:
                    # 直近でcheckedになっている受取ラジオのラベルから推定
                    checked_receive = await self.page.query_selector("input[type='radio'][name='vuketoriHohoSentaku']:checked")
                    if checked_receive:
                        label_text = await self.page.evaluate("(el) => { const id=el.id; const byFor=id?document.querySelector(`label[for=\"${id}\"]`):null; if(byFor){return byFor.innerText;} const wrap=el.closest('label'); return wrap?wrap.innerText:''; }", checked_receive)
                        lt = _normalize(label_text or "")
                        if 'ファミ' in lt or 'family' in lt:
                            chosen_store = 'ファミリーマート'
                        elif 'セブン' in lt or 'seven' in lt:
                            chosen_store = 'セブン-イレブン'
            except:
                pass

            try:
                pay_radios = await self.page.query_selector_all("input[type='radio'][name='vsiharaiHohoSentaku']")
                if pay_radios:
                    candidates = []
                    for el in pay_radios:
                        try:
                            value = await el.get_attribute('value')
                        except:
                            value = None
                        try:
                            label_text = await self.page.evaluate("(el) => { const id=el.id; const byFor=id?document.querySelector(`label[for=\"${id}\"]`):null; if(byFor){return byFor.innerText;} const wrap=el.closest('label'); return wrap?wrap.innerText:''; }", el)
                        except:
                            label_text = ""
                        candidates.append((el, value, label_text or ""))

                    # 1) value=3（コンビニ/ATM）を最優先
                    for el, value, label in candidates:
                        if (value or "").strip() == '3':
                            try:
                                await el.click()
                            except:
                                try:
                                    await self.page.evaluate("(el)=>el.click()", el)
                                except:
                                    await el.click(force=True)
                            pay_selected = True
                            print(f"✅ 支払方法: コンビニ/ATM を選択（label='{label.strip()}')")
                            await self.helper.safe_wait(800)
                            break

                    # 2) ラベル一致（店舗名が表示されている場合、受取と合わせる）
                    if not pay_selected and chosen_store:
                        for el, _value, label in candidates:
                            if _normalize(chosen_store) in _normalize(label):
                                try:
                                    await el.click()
                                except:
                                    try:
                                        await self.page.evaluate("(el)=>el.click()", el)
                                    except:
                                        await el.click(force=True)
                                pay_selected = True
                                print(f"✅ 支払方法: '{chosen_store}' を選択（label='{label.strip()}')")
                                await self.helper.safe_wait(800)
                                break

                    # 3) クレジットカード指定がconfigにあれば最後に尊重
                    if not pay_selected and 'クレジット' in _normalize(self.config.payment_method):
                        for el, value, label in candidates:
                            if (value or "").strip() == '1' or 'クレジット' in _normalize(label):
                                try:
                                    await el.click()
                                except:
                                    try:
                                        await self.page.evaluate("(el)=>el.click()", el)
                                    except:
                                        await el.click(force=True)
                                pay_selected = True
                                print(f"✅ 支払方法: クレジットカードを選択（label='{label.strip()}')")
                                await self.helper.safe_wait(800)
                                break

                    # 4) どれも無ければ先頭
                    if not pay_selected and candidates:
                        try:
                            await candidates[0][0].click()
                            pay_selected = True
                            print(f"⚠️  支払方法: 既定の先頭を選択（label='{(candidates[0][2] or '').strip()}')")
                            await self.helper.safe_wait(800)
                        except:
                            pass
                else:
                    print("⚠️  支払方法のラジオが見つかりませんでした（name='vsiharaiHohoSentaku'）")
            except Exception as _:
                print("⚠️  支払方法の選択時に一時的なエラー")

            if not pay_selected:
                print("⚠️  支払方法の選択をスキップ（要素未検出）")

            await self.helper.save_screenshot(self.page, "step5_after_payment_delivery.png")

            # 次へボタンをクリック（確認画面へ進む）
            print("➡️  最後に『次へ』をクリックして確認画面へ進みます...")
            await self.helper.safe_wait(600)
            next_clicked = False
            next_button_selectors = [
                "button:has-text('次へ')",
                "button.button--primary:has-text('次へ')",
                "button[type='submit']:has-text('次へ')",
                "input[type='submit'][value*='次へ']",
                "a:has-text('次へ')",
            ]
            for sel in next_button_selectors:
                if await self._safe_click(sel):
                    next_clicked = True
                    break

            if next_clicked:
                print("✅ 『次へ』クリック成功。確認画面に遷移中...")
                await self.helper.safe_wait(2000)
                await self.helper.save_screenshot(self.page, "step5_after_next_click.png")
            else:
                print("⚠️  『次へ』ボタンが見つかりません。ページ構造が異なる可能性があります。")
                await self.helper.save_screenshot(self.page, "step5_next_button_not_found.png")

            print("\n⚠️  ここから先（最終確認・送信）は手動で行ってください")
            print("   （誤発注防止のため、自動送信は実装していません）")
            
            # 指定分ブラウザを開いたまま待機（0なら待機なし）
            if self.config.keep_open_minutes and self.config.keep_open_minutes > 0:
                wait_ms = int(self.config.keep_open_minutes * 60 * 1000)
                print(f"\n⏳ {self.config.keep_open_minutes}分間ブラウザを開いたままにします...")
                await self.helper.safe_wait(wait_ms)
            
            return True
            
        except Exception as e:
            print(f"❌ ステップ5でエラー: {e}")
            await self.helper.save_screenshot(self.page, "step5_error.png")
            return False
    
    async def _safe_click(self, selector: str) -> bool:
        """安全なクリック処理（複数の方法を試行）"""
        try:
            element = await self.page.query_selector(selector)
            if not element:
                return False
            
            # 方法1: 通常のクリック
            try:
                await element.click(timeout=3000)
                return True
            except:
                pass
            
            # 方法2: JavaScriptでクリック
            try:
                await self.page.evaluate("(el) => el.click()", element)
                return True
            except:
                pass
            
            # 方法3: forceオプション付きクリック
            try:
                await element.click(force=True, timeout=3000)
                return True
            except:
                pass
            
            return False
            
        except Exception as e:
            return False
