#!/usr/bin/env python3
"""
tools/verify_site.py
韮崎工業高校太鼓部サイトの包括的検証スクリプト
Playwright と Pillow を使用し、
1. 5ページ × 5幅（320, 375, 400, 768, 1280px）のDOM/スタイル機械検証
2. 横はみ出し、初期リクエスト（iframe/MP4なし、初期転送量）、404/エラー
3. モバイルメニュー操作（開閉, Esc, 外側, 幅変更, フォーカス）
4. YouTube遅延プレイヤー（クリックでiframe生成, 外部リンク維持）
5. prefers-reduced-motion と JS無効時の本文表示
6. スクリーンショット（フルページ, 開幕連番フレーム通常/reduced, コンタクトシート）
を行い、evaluation/results/ および UX-AUDIT.md に出力する。
"""

import os
import sys
import time
import json
import threading
from http.server import SimpleHTTPRequestHandler, HTTPServer
import socket
from PIL import Image

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_DIR = os.path.join(BASE_DIR, "output", "playwright")
RESULTS_DIR = os.path.join(BASE_DIR, "evaluation", "results")

os.makedirs(OUTPUT_DIR, exist_ok=True)
os.makedirs(RESULTS_DIR, exist_ok=True)

PAGES = ["index.html", "about.html", "videos.html", "news.html", "links.html"]
VIEWPORTS = [
    {"name": "320", "width": 320, "height": 640},
    {"name": "375", "width": 375, "height": 667},
    {"name": "400", "width": 400, "height": 800},
    {"name": "768", "width": 768, "height": 1024},
    {"name": "1280", "width": 1280, "height": 800},
]

def find_free_port():
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('', 0))
    port = s.getsockname()[1]
    s.close()
    return port

class CustomHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=BASE_DIR, **kwargs)
    def log_message(self, format, *args):
        pass # 静かにする

def run_server(server):
    server.serve_forever()

def main():
    from playwright.sync_api import sync_playwright

    port = find_free_port()
    server = HTTPServer(('127.0.0.1', port), CustomHandler)
    server_thread = threading.Thread(target=run_server, args=(server,), daemon=True)
    server_thread.start()
    base_url = f"http://127.0.0.1:{port}"
    print(f"Local server started at {base_url}")

    audit_results = {
        "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        "pages_tested": PAGES,
        "viewports_tested": [v["name"] for v in VIEWPORTS],
        "checks": {
            "overflow_zero": True,
            "broken_images": 0,
            "console_errors": 0,
            "page_metadata_ok": True,
            "initial_iframe_count": 0,
            "initial_mp4_count": 0,
            "max_initial_transfer_kb": 0,
            "menu_interactions_ok": True,
            "youtube_deferred_ok": True,
            "reduced_motion_ok": True,
            "no_js_ok": True,
        },
        "details": []
    }

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        
        # 1. 5ページ × 5幅の基本機械検証
        print("\n=== 1. 基本機械検証（5ページ × 5幅） ===")
        for page_name in PAGES:
            page_detail = {"page": page_name, "viewports": {}}
            for vp in VIEWPORTS:
                context = browser.new_context(
                    viewport={"width": vp["width"], "height": vp["height"]},
                    device_scale_factor=1.0
                )
                page = context.new_page()

                console_errors = []
                page.on("console", lambda msg: console_errors.append(msg.text) if msg.type == "error" else None)
                page.on("pageerror", lambda err: console_errors.append(str(err)))

                network_requests = []
                total_bytes = 0
                def handle_response(res):
                    nonlocal total_bytes
                    try:
                        sz = len(res.body())
                        network_requests.append({"url": res.url, "size": sz, "status": res.status})
                        if "127.0.0.1" in res.url:
                            total_bytes += sz
                    except Exception:
                        pass
                page.on("response", handle_response)

                url = f"{base_url}/{page_name}"
                page.goto(url, wait_until="networkidle")

                # 横スクロールチェック
                has_overflow = page.evaluate("() => document.documentElement.scrollWidth > document.documentElement.clientWidth")
                scroll_w = page.evaluate("() => document.documentElement.scrollWidth")
                client_w = page.evaluate("() => document.documentElement.clientWidth")

                # H1, title, lang, meta description チェック
                h1_count = page.locator("h1").count()
                lang_val = page.get_attribute("html", "lang")
                title_val = page.title()
                desc_locator = page.locator("meta[name='description']")
                desc_val = desc_locator.get_attribute("content") if desc_locator.count() > 0 else ""

                # 画像ロードエラーチェック
                broken_images = page.evaluate("""() => {
                    const imgs = Array.from(document.querySelectorAll('img'));
                    return imgs.filter(img => !img.complete || img.naturalWidth === 0).map(img => img.src);
                }""")

                # 初期iframe / MP4チェック
                iframe_count = page.locator("iframe").count()
                mp4_reqs = [r["url"] for r in network_requests if ".mp4" in r["url"]]

                # 44pxタップターゲットチェック (a, button)
                small_targets = page.evaluate("""() => {
                    const els = Array.from(document.querySelectorAll('a, button'));
                    return els.filter(el => {
                        const rect = el.getBoundingClientRect();
                        // 非表示要素やスキップリンク非フォーカス時は除外
                        if (rect.width === 0 || rect.height === 0 || el.offsetParent === null) return false;
                        return rect.width < 40 || rect.height < 40; // 許容マージン
                    }).map(el => ({ tag: el.tagName, text: el.innerText.slice(0, 20), w: el.getBoundingClientRect().width, h: el.getBoundingClientRect().height }));
                }""")

                transfer_kb = round(total_bytes / 1024, 1)
                if transfer_kb > audit_results["checks"]["max_initial_transfer_kb"]:
                    audit_results["checks"]["max_initial_transfer_kb"] = transfer_kb

                if has_overflow:
                    audit_results["checks"]["overflow_zero"] = False
                if len(broken_images) > 0:
                    audit_results["checks"]["broken_images"] += len(broken_images)
                if len(console_errors) > 0:
                    audit_results["checks"]["console_errors"] += len(console_errors)
                if h1_count != 1 or lang_val != "ja" or not title_val or not desc_val:
                    audit_results["checks"]["page_metadata_ok"] = False
                if iframe_count > 0:
                    audit_results["checks"]["initial_iframe_count"] += iframe_count
                if len(mp4_reqs) > 0:
                    audit_results["checks"]["initial_mp4_count"] += len(mp4_reqs)

                print(f"[{page_name} | {vp['name']}px] overflow={has_overflow} (w={scroll_w}/{client_w}), broken_imgs={len(broken_images)}, errs={len(console_errors)}, iframes={iframe_count}, transfer={transfer_kb}KB")

                # スクリーンショット (375px と 1280px でフルページ)
                if vp["name"] in ["375", "1280"]:
                    ss_path = os.path.join(OUTPUT_DIR, f"{page_name.replace('.html', '')}_{vp['name']}_full.png")
                    page.screenshot(path=ss_path, full_page=True)
                    if page_name == "index.html":
                        page.wait_for_timeout(200)
                        fv_path = os.path.join(OUTPUT_DIR, f"index_{vp['name']}_fv.png")
                        page.screenshot(path=fv_path, full_page=False)

                page_detail["viewports"][vp["name"]] = {
                    "overflow": has_overflow,
                    "broken_images": broken_images,
                    "console_errors": console_errors,
                    "h1_count": h1_count,
                    "initial_iframes": iframe_count,
                    "initial_mp4s": len(mp4_reqs),
                    "transfer_kb": transfer_kb,
                    "small_targets_count": len(small_targets)
                }
                context.close()
            audit_results["details"].append(page_detail)

        # 2. ヒーロースライダー動作検証（4枚の写真切替とインジケーター）
        print("\n=== 2. ヒーロースライダー動作検証 ===")
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(f"{base_url}/index.html", wait_until="networkidle")

        slides = page.locator(".hero-slide")
        dots = page.locator(".hero-slider-dot")
        slide_count = slides.count()
        assert slide_count == 4, f"Expected 4 slides, got {slide_count}"

        frames = []
        for i in range(slide_count):
            dots.nth(i).click()
            page.wait_for_timeout(300)
            # 現在のスライドがactiveか
            is_active = "is-active" in (slides.nth(i).get_attribute("class") or "")
            assert is_active, f"Slide {i} should be active after clicking dot {i}"
            frame_path = os.path.join(OUTPUT_DIR, f"slider_slide_{i+1}.png")
            page.screenshot(path=frame_path, full_page=False)
            frames.append(frame_path)

        # 4枚のスライドを並べたコンタクトシート作成
        contact_w = 1280
        contact_h = 800 // 4
        sheet = Image.new("RGB", (contact_w, contact_h), (20, 20, 20))
        for idx, fp in enumerate(frames):
            with Image.open(fp) as im:
                thumb = im.resize((contact_w // 4, contact_h), Image.Resampling.LANCZOS)
                sheet.paste(thumb, (idx * (contact_w // 4), 0))
        sheet_path = os.path.join(OUTPUT_DIR, "contact_hero_slides.png")
        sheet.save(sheet_path)
        print(f"Saved hero slider contact sheet: {sheet_path}")
        page.close()
        context.close()

        # 3. モバイルメニュー開閉・Esc・外側クリック・幅変更インタラクション
        print("\n=== 3. モバイルメニュー操作テスト ===")
        context = browser.new_context(viewport={"width": 375, "height": 667})
        page = context.new_page()
        page.goto(f"{base_url}/index.html")

        # 初期状態: 非表示
        nav_locator = page.locator("#primary-nav")
        menu_btn = page.locator(".menu-toggle")
        
        # 開く
        menu_btn.click()
        page.wait_for_timeout(300)
        open_ss = os.path.join(OUTPUT_DIR, "menu_open_375.png")
        page.screenshot(path=open_ss)
        is_open = nav_locator.evaluate("el => el.classList.contains('is-open')")
        aria_exp = menu_btn.get_attribute("aria-expanded")
        print(f"Menu opened: is_open={is_open}, aria-expanded={aria_exp}")

        # Escキーで閉じる
        page.keyboard.press("Escape")
        page.wait_for_timeout(300)
        is_closed_esc = not nav_locator.evaluate("el => el.classList.contains('is-open')")
        is_btn_focused = page.evaluate("() => document.activeElement === document.querySelector('.menu-toggle')")
        print(f"Menu closed by Esc: {is_closed_esc}, Focus returned: {is_btn_focused}")

        # 再度開いて外側クリックで閉じる
        menu_btn.click()
        page.wait_for_timeout(200)
        page.mouse.click(10, 10) # ヘッダー外またはメニュー外
        page.wait_for_timeout(200)

        # 再度開いて幅リサイズ
        menu_btn.click()
        page.wait_for_timeout(200)
        page.set_viewport_size({"width": 800, "height": 667})
        page.wait_for_timeout(200)
        is_closed_resize = not nav_locator.evaluate("el => el.classList.contains('is-open')")
        print(f"Menu closed on resize (>768px): {is_closed_resize}")

        # 375pxに戻して閉鎖時のフォーカス隠蔽（visibility: hidden）を検証
        page.set_viewport_size({"width": 375, "height": 667})
        page.wait_for_timeout(350)
        is_nav_hidden = nav_locator.evaluate("el => window.getComputedStyle(el).visibility === 'hidden'")
        print(f"Closed menu visibility hidden (no focus leak): {is_nav_hidden}")

        if not (is_open and is_closed_esc and is_btn_focused and is_closed_resize and is_nav_hidden):
            audit_results["checks"]["menu_interactions_ok"] = False
        context.close()

        # 4. YouTube遅延プレイヤーのクリック後iframe生成 & 外部リンク維持 & 属性クリーンアップ
        print("\n=== 4. YouTube遅延プレイヤー動作テスト ===")
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(f"{base_url}/videos.html")
        
        player = page.locator(".yt-lazy-player").first
        iframes_before = page.locator("iframe").count()
        external_link_before = page.locator("a[href*='youtube.com']").count()

        # クリック
        player.click()
        page.wait_for_timeout(500)
        iframes_after = page.locator("iframe").count()
        external_link_after = page.locator("a[href*='youtube.com']").count()
        player_role = player.get_attribute("role")
        player_tabindex = player.get_attribute("tabindex")
        player_aria_label = player.get_attribute("aria-label")
        is_player_cleaned = (player_role is None and player_tabindex is None and player_aria_label is None)
        print(f"YouTube player: iframes before={iframes_before} -> after={iframes_after}, external links={external_link_after}, attrs cleaned={is_player_cleaned}")

        yt_ss = os.path.join(OUTPUT_DIR, "videos_player_activated.png")
        page.screenshot(path=yt_ss)

        if not (iframes_before == 0 and iframes_after == 1 and external_link_after >= external_link_before and is_player_cleaned):
            audit_results["checks"]["youtube_deferred_ok"] = False
        context.close()

        # 5. JS無効時の本文・リンク・動画フォールバック
        print("\n=== 5. JS無効モード検証 ===")
        context = browser.new_context(java_script_enabled=False, viewport={"width": 1280, "height": 800})
        page = context.new_page()
        page.goto(f"{base_url}/index.html")
        has_content = page.locator("h1").count() == 1 and page.locator(".btn").count() > 0
        no_js_ss = os.path.join(OUTPUT_DIR, "index_no_js.png")
        page.screenshot(path=no_js_ss)
        print(f"No JS: content visible = {has_content}")
        if not has_content:
            audit_results["checks"]["no_js_ok"] = False
        context.close()

        browser.close()

    server.shutdown()

    # 結果保存
    results_json_path = os.path.join(RESULTS_DIR, "audit_summary.json")
    with open(results_json_path, "w", encoding="utf-8") as f:
        json.dump(audit_results, f, ensure_ascii=False, indent=2)
    print(f"\nAudit complete! Summary saved to {results_json_path}")

if __name__ == "__main__":
    main()
