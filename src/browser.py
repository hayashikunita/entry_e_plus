"""ブラウザ制御ヘルパー"""

import asyncio
from pathlib import Path
import json
from typing import Optional
from playwright.async_api import Browser, BrowserContext, Page, async_playwright, Playwright

from .config import Settings


class BrowserHelper:
    """Playwrightブラウザ制御ヘルパークラス"""
    
    def __init__(self, config: Settings):
        self.config = config
        self.playwright: Optional[Playwright] = None
        self.browser: Optional[Browser] = None
        self.context: Optional[BrowserContext] = None
    
    async def __aenter__(self):
        """非同期コンテキストマネージャー - 開始"""
        await self.start()
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """非同期コンテキストマネージャー - 終了"""
        await self.stop()
    
    async def start(self):
        """ブラウザを起動"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.config.headless,
            args=[
                '--disable-blink-features=AutomationControlled',
                '--no-sandbox'
            ]
        )
        new_context_kwargs = dict(
            viewport={"width": 1280, "height": 800},
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            )
        )
        # ビデオ録画の有効化
        if self.config.video_enabled:
            new_context_kwargs.update({
                "record_video_dir": str(self.config.video_dir),
                "record_video_size": {"width": 1280, "height": 800},
            })
        self.context = await self.browser.new_context(**new_context_kwargs)
    
    async def stop(self):
        """ブラウザを停止"""
        if self.context:
            # 動画保存のため、ページを先に閉じる
            try:
                for p in list(self.context.pages):
                    try:
                        await p.close()
                    except Exception:
                        pass
            except Exception:
                pass
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def create_page(self) -> Page:
        """新しいページを作成"""
        if not self.context:
            raise RuntimeError("Browser context not initialized")
        page = await self.context.new_page()
        # 個人情報のマスキングを適用
        if self.config.mask_personal_info:
            try:
                await self._apply_privacy_masks(page)
            except Exception:
                pass
        return page

    async def _apply_privacy_masks(self, page: Page):
        """入力欄などの個人情報を画面上でマスク（録画用）"""
        # 1) CSSで代表的な入力欄をぼかす
        css = """
        input[type="password"],
        input[name="login_id"],
        input[name="login_pw"],
        #login_id,
        #login_pw,
        input[autocomplete="username"],
        input[autocomplete="current-password"],
        #securityCode,
        input[name*="security" i],
        .GB1112MainFormCreditCardNo,
        [id^="creditCardId_"],
        #sm-menu-card,
        .sm-menu
        { filter: blur(8px) !important; -webkit-filter: blur(8px) !important; }
        """

        async def apply_to_frame(fr):
            try:
                await fr.add_style_tag(content=css)
            except Exception:
                pass

        # ページ本体と既存iframeに適用
        await apply_to_frame(page)
        for fr in page.frames:
            await apply_to_frame(fr)

        # 新規にアタッチされるiframeにも適用
        def _on_frame_attached(frame):
            try:
                asyncio.create_task(apply_to_frame(frame))
            except Exception:
                pass
        page.on("frameattached", _on_frame_attached)

        # 2) 画面上に表示されるメールアドレス文字列を伏字化（テキストノードのみ）
        email = getattr(self.config, "eplus_email", "") or ""
        if email:
            js = """
            (function(maskTarget) {
              try {
                const mask = (text) => text.split(maskTarget).join('*'.repeat(8));
                // 既存のテキストノードを書き換え
                const walker = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
                let node; while ((node = walker.nextNode())) {
                  if (node.nodeValue && node.nodeValue.includes(maskTarget)) {
                    node.nodeValue = mask(node.nodeValue);
                  }
                }
                // 変化を監視して都度マスク
                const obs = new MutationObserver((mutations) => {
                  for (const m of mutations) {
                    const nodes = [];
                    if (m.addedNodes) nodes.push(...m.addedNodes);
                    for (const n of nodes) {
                      try {
                        if (n.nodeType === Node.TEXT_NODE) {
                          if (n.nodeValue && n.nodeValue.includes(maskTarget)) {
                            n.nodeValue = mask(n.nodeValue);
                          }
                        } else if (n.nodeType === Node.ELEMENT_NODE) {
                          const w = document.createTreeWalker(n, NodeFilter.SHOW_TEXT);
                          let tn; while ((tn = w.nextNode())) {
                            if (tn.nodeValue && tn.nodeValue.includes(maskTarget)) {
                              tn.nodeValue = mask(tn.nodeValue);
                            }
                          }
                        }
                      } catch(e) {}
                    }
                  }
                });
                obs.observe(document.body, {childList: true, subtree: true, characterData: true});
              } catch(e) {}
            })({json_email});
            """.replace("{json_email}", json.dumps(email))
            try:
                await page.add_init_script(js)
                await page.evaluate(js)
            except Exception:
                pass
    
    async def safe_wait(self, ms: int):
        """安全な待機（ミリ秒）"""
        await asyncio.sleep(ms / 1000)
    
    async def save_screenshot(self, page: Page, filename: str):
        """スクリーンショットを保存"""
        screenshot_dir = Path(self.config.screenshot_dir)
        screenshot_dir.mkdir(parents=True, exist_ok=True)
        
        filepath = screenshot_dir / filename
        await page.screenshot(path=str(filepath), full_page=True)
        
        if self.config.debug:
            print(f"📸 スクリーンショット保存: {filepath}")
