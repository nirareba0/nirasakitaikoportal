# UX-AUDIT — 韮崎工業高校太鼓部 ポータル サイト品質・アクセシビリティ監査

実施日時: 2026-09-12 16:09:57  
検証ツール: `tools/verify_site.py`（Playwright / Chromium headless + Pillow）  
検証対象: 5ページ（index.html, about.html, videos.html, news.html, links.html）  
検証画面幅: 320px, 375px, 400px, 768px, 1280px  
レビュー反映: レビュアーサブエージェント指摘7件（Bug 2件、Missed Criterion 1件、Edge Case 2件、Style 1件、Audit Check 1件）を全件反映完了

---

## 1. 総合評価サマリー

| 監査項目 | 目標・合格基準 | 実測値・結果 | 判定 |
|---|---|---|---|
| **横スクロール・はみ出し** | 全5幅で `scrollWidth <= clientWidth`（はみ出し0） | 5ページ × 5幅すべてで幅一致（320px〜1280px 横はみ出し0） | ✅ 合格 |
| **画像ロードエラー** | 404 / broken image 0件 | 0件 | ✅ 合格 |
| **コンソールエラー** | JS例外・コンソールエラー 0件 | 0件 | ✅ 合格 |
| **文書構造（H1/lang/meta）** | 各ページH1が1つ、`lang="ja"`、title/description固有、`<main>`内H1 | 全5ページ適合（スキップリンク直後にH1到達保証） | ✅ 合格 |
| **初期リクエスト軽量性** | 1.5MB以下、初期iframe=0、初期MP4=0 | 最大330.5KB（目標値の約22%）、iframe=0、MP4=0 | ✅ 合格 |
| **モバイルメニュー** | 開閉・aria-expanded連動・Escキー閉鎖・フォーカス復帰・幅拡大リセット・閉鎖時フォーカス除外 | すべて動作確認済み（閉鎖時 `visibility: hidden` によるキーボードフォーカス漏れ防止検証済み） | ✅ 合格 |
| **YouTube遅延再生** | 初期ロード時外部通信なし、クリックでiframe生成、常時外部リンク提供、再生後ARIA属性整理 | 初期0件 → クリック後1件生成、外部リンク4件常時表示、再生後親属性（role/tabindex/aria-label）解除済み | ✅ 合格 |
| **動き低減（Reduced Motion）** | `prefers-reduced-motion: reduce` で演出停止・本文即時可読 | 即座に静止最終状態を表示（コンタクトシート検証済み） | ✅ 合格 |
| **JS無効環境（No-JS）** | JS無効時にも全ページの文章・画像・静的リンクが閲覧可能 | 本文可読性・外部リンク正常確認済み | ✅ 合格 |

---

## 2. 画面幅別・ページ別転送量とレイアウト検証

| ページ | 320px | 375px | 400px | 768px | 1280px | 特記事項 |
|---|---|---|---|---|---|---|
| **index.html** | 170.3 KB (はみ出し無) | 170.3 KB (はみ出し無) | 170.3 KB (はみ出し無) | 199.4 KB (はみ出し無) | 237.8 KB (はみ出し無) | ヒーローWebPレスポンシブ切り替え正常、`<main>`内H1配置 |
| **about.html** | 154.8 KB (はみ出し無) | 154.8 KB (はみ出し無) | 154.8 KB (はみ出し無) | 299.3 KB (はみ出し無) | 299.3 KB (はみ出し無) | 歴史・天野流・モットーの章立て正常、フッターactive修正 |
| **videos.html** | 330.5 KB (はみ出し無) | 330.5 KB (はみ出し無) | 330.5 KB (はみ出し無) | 330.5 KB (はみ出し無) | 330.5 KB (はみ出し無) | 320pxグリッド調整によりはみ出し完全解消、サムネイルalt装飾化 |
| **news.html** | 75.2 KB (はみ出し無) | 75.2 KB (はみ出し無) | 75.2 KB (はみ出し無) | 120.2 KB (はみ出し無) | 120.2 KB (はみ出し無) | 公式発表実績一覧と出典リンク正常、`<main>`内H1配置 |
| **links.html** | 52.2 KB (はみ出し無) | 52.2 KB (はみ出し無) | 52.2 KB (はみ出し無) | 69.9 KB (はみ出し無) | 69.9 KB (はみ出し無) | 恒久チャンネルID URL採用、外部公式リンク集正常 |

---

## 3. レビュー指摘の反映内容詳細

1. **【Bug 1】モバイルメニュー非展開時のキーボードフォーカス漏れ対策**
   - `assets/style.css` の `.main-nav` に `visibility: hidden;`、開いたときに `visibility: visible;` を設定。トランジションディレイを精密制御し、閉鎖中はTabキーのフォーカス順序から確実に除外。
2. **【Bug 2】YouTube遅延プレイヤー展開後のARIA属性競合防止**
   - `assets/script.js` の `activatePlayer` で `<iframe>` を生成した際、親要素の `role="button"`, `tabindex="0"`, `aria-label` を削除。WAI-ARIA 1.2準拠の対話要素重複を防止。
3. **【Missed Criterion】動画サムネイル画像 alt テキストの出典誤結び付け解消**
   - `DESIGN.md` 40行目の規定に基づき、動画タイトルと対応が確定しないサムネイル画像を装飾画像扱い（`alt=""`）に変更。親要素の `aria-label` で動画名を明示。
4. **【Edge Case 1】スキップリンクとランドマーク構造の適正化**
   - 全5ページで `<section class="page-banner">` および `section.hero` を `<main id="main-content" tabindex="-1">` 内に内包。スキップリンク実行時にページ主見出し（H1）へ正しくフォーカスが移動するよう改修。
5. **【Edge Case 2】YouTube公式チャンネルURLの恒久化**
   - `links.html` のリンク先を非ASCIIハンドルから、恒久的でRFC 3986準拠のチャンネルID URL（`https://www.youtube.com/channel/UCjIHn3E2Eji269ppA6b3VWQ`）に更新。
6. **【Style】フッターナビゲーションの active クラス整合性**
   - `about.html` のフッターで誤って `videos.html` に付いていた `class="active"` を修正し、全5ページでヘッダー・フッターの現在地表示を完全同期。
7. **【Audit Check】検証スクリプトの検査拡充**
   - `tools/verify_site.py` に「メニュー閉鎖時の `visibility: hidden` 検査」と「遅延プレイヤー起動後の属性解除検査」を自動アサーションとして追加。

---

## 4. 保存アーティファクト
- 機械検証生データ: `evaluation/results/audit_summary.json`
- スクリーンショット一覧: `output/playwright/`
  - 全ページフルスクリーンショット（375px / 1280px）
  - 開幕演出時系列フレーム（0ms, 150ms, 450ms, 1000ms, 1300ms / 通常・動き低減）
  - モーション比較コンタクトシート（`contact_intro_normal.png`, `contact_intro_reduced.png`）
  - メニュー展開状態（`menu_open_375.png`）
  - YouTubeプレイヤー展開状態（`videos_player_activated.png`）
  - JS無効状態キャプチャ（`index_no_js.png`）
