# 韮崎工業高校太鼓部ポータル全面再制作 レビュー報告

提示された4つの観点および受け入れ基準に基づき、全制作ファイル（HTML 5ページ、CSS、JS、画像アセット・manifest、検証スクリプト、監査ドキュメント）を厳格に精査しました。

---

## 総合判定
確認済み事実の準拠（部員数・顧問名・次回公演日の不創作）、外部スクリプト排除、ローカル素材（Assets2）のWebP最適化、レスポンシブ表示、prefers-reduced-motion 対応など基本骨格は極めて高い品質で実装されています。
しかし、**キーボード操作時のアクセシビリティ（メニュー非展開時のフォーカス漏れ、動画再生後のARIA不正）**、および**動画サムネイル代替テキストでの写真の誤結び付け**に具体的な問題が確認されました。

以下、重要度順（Bug > Missed Criterion > Edge Case > Style）に問題点・理由・修正方法を報告します。

---

## 1. 指摘事項（重要度順）

### 【Bug 1】モバイルメニュー非展開時のキーボードフォーカス漏れ
- **該当箇所**: [`assets/style.css`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/assets/style.css#L971-L988)
- **問題点**:
  `@media (max-width: 768px)` において、メニュー非展開時（`.main-nav` に `.is-open` が付いていない初期状態・閉鎖状態）のスタイルが `transform: translateY(-100%); opacity: 0; pointer-events: none;` のみとなっており、`visibility: hidden`、`display: none`、`inert` が指定されていません。
- **影響**:
  `pointer-events: none` や `opacity: 0` はマウスクリックを無効化するだけで、キーボードの Tab 移動順序（フォーカスオーダー）からは除外されません。
  そのため、スマホ幅でメニューが閉じている状態でも、Tab キーを押すと画面外・不可視のナビゲーションリンク5件（トップ、部について、演奏動画、実績・記録、公式リンク）に順次フォーカスが移動してしまいます。スクリーンリーダーも閉鎖状態のリンクを読み上げてしまい、WCAG 2.1 達成基準 2.4.3（フォーカス順序）および 2.4.7（フォーカスの可視化）に違反します。
  ※CHANGELOG.md に「キーボードフォーカス漏れを反映」と記載されていますが、実際には展開時の `firstFocusable.focus()` を追加したのみで、閉鎖時のフォーカス漏れが未解決のまま残っています。
- **修正提案**:
  `assets/style.css` の `.main-nav` に `visibility: hidden;` を追加し、`.main-nav.is-open` で `visibility: visible;` に切り替えてください（`transition` に `visibility` を含めることでアニメーションを損なわずにフォーカスを除外できます）。
  ```css
  /* assets/style.css */
  .main-nav {
    ...
    visibility: hidden;
    transition: transform var(--duration-normal) var(--ease-out), opacity var(--duration-normal) ease, visibility var(--duration-normal);
  }
  .main-nav.is-open {
    transform: translateY(0);
    opacity: 1;
    pointer-events: auto;
    visibility: visible;
  }
  ```

---

### 【Bug 2】YouTube遅延プレイヤー展開後の不正なARIA属性とフォーカス競合
- **該当箇所**: [`assets/script.js`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/assets/script.js#L83-L97)
- **問題点**:
  各ページの遅延プレイヤー `.yt-lazy-player` は HTML 上で `role="button"`、`tabindex="0"`、`aria-label="動画を再生する: ..."` を持っています。ユーザーがクリックまたは Enter/Space キーで再生を実行（`activatePlayer`）した際、中身が `<iframe>` に置き換わりますが、親要素から上記属性が削除されていません。
- **影響**:
  WAI-ARIA 1.2 仕様上、`role="button"` を持つ要素の内部に対話的要素（動画プレイヤーコントロールを持つ `iframe`）をネストすることは禁止されています。また再生後も親が「動画を再生するボタン」としてスクリーンリーダーに通知され、Tab 移動でも「外枠ボタン → 内部 iframe」と二重にフォーカスが当たって混乱を招きます。
- **修正提案**:
  `assets/script.js` の `activatePlayer` 処理内で、`iframe` を追加する際に親のボタン属性を解除してください。
  ```javascript
  // assets/script.js
  player.removeAttribute('role');
  player.removeAttribute('tabindex');
  player.removeAttribute('aria-label');
  ```

---

### 【Missed Criterion】動画サムネイル画像 alt テキストにおける出典の誤結び付け
- **該当箇所**:
  - [`index.html#L102`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/index.html#L102): `assets/media/stage_geibunsai-1000.webp` に `alt="定期演奏会 鍛麗2026の演奏風景サムネイル"`
  - [`videos.html#L74`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/videos.html#L74): 同上
  - [`videos.html#L128`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/videos.html#L128): `assets/media/stage_kanto-1000.webp`（関東大会写真）に `alt="士魂迅雷の演奏風景サムネイル"`
  - [`videos.html#L168`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/videos.html#L168): `assets/media/odaiko_back-1000.webp`（関東大会写真）に `alt="鍛麗2025の演奏風景サムネイル"`
  - [`videos.html#L208`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/videos.html#L208): `assets/media/festival_night-1000.webp`（小田川ホタルまつり写真）に `alt="鍛麗2024の演奏風景サムネイル"`
- **問題点**:
  採用された WebP 画像は、[`assets/media/manifest.json`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/assets/media/manifest.json) に記録されている通り、芸術文化祭、関東大会、小田川ホタルまつり等の写真です。しかし HTML の `alt` 属性では、動画タイトルに合わせて「定期演奏会 鍛麗2026」「鍛麗2025」「鍛麗2024」「士魂迅雷」のサムネイルであると断定的に記載されています。
- **影響**:
  `DESIGN.md` 40行目の**「サムネイルは提供画像を使い出典の誤結び付けを避ける。動画タイトルと対応が確実でなければ装飾画像扱いにする」**、および `REQUIREMENTS.md` 20行目の「過去イベントの告知素材を今後の開催案内にしない。作品名『鍛麗2026』と実際の開催日を混同しない」という規定に反します。地域の夜間野外演奏写真を「鍛麗2024」と記述することは、確認済み事実に反する誤認・虚偽の結び付けとなります。
- **修正提案**:
  遅延プレイヤーの外枠がすでに `aria-label="動画を再生する: 鍛麗 -TANREI 2026-..."` を提供しているため、画像自体は `DESIGN.md` の指示通り装飾画像として `alt=""` にするか、または写真自体の実際の情景を正しく表す記述（例: `alt="和太鼓演奏風景"`）に修正してください。

---

### 【Edge Case 1】スキップリンクと見出し構造：`<h1>` が `<main>` の外に配置されている
- **該当箇所**:
  - [`index.html#L43-L79`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/index.html#L43-L79)
  - [`about.html#L43-L53`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/about.html#L43-L53)
  - [`videos.html#L43-L53`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/videos.html#L43-L53)
  - [`news.html#L43-L53`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/news.html#L43-L53)
  - [`links.html#L43-L53`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/links.html#L43-L53)
- **問題点**:
  全5ページで最上部に `<a href="#main-content" class="skip-link">本文へスキップ</a>` が設置されていますが、ページ唯一の `<h1>` および導入文を含むヒーロー（`section.hero`）やページバナー（`section.page-banner`）が、すべて `<main id="main-content">` の手前（外側）に記述されています。また `<main>` に `tabindex="-1"` が付与されていません。
- **影響**:
  キーボード操作で「本文へスキップ」を実行すると、ヘッダーだけでなく、そのページの最重要見出しである `<h1>` と導入文まで丸ごとスキップしてしまいます。またランドマークナビゲーション（Screen Readerの `<main>` ジャンプ機能）を使用した際にも、`<main>` の中に `<h1>` が存在しない構造的欠陥となります。
- **修正提案**:
  各ページの `section.hero` および `section.page-banner` を `<main id="main-content" tabindex="-1">` の内側に配置してください。

---

### 【Edge Case 2】`links.html` のYouTube公式チャンネルURLにおける非ASCII文字（日本語）直書き
- **該当箇所**: [`links.html#L97`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/links.html#L97)
- **問題点**:
  `<a href="https://www.youtube.com/@山梨県立韮崎工業高校" ...>` と日本語ハンドルが直接指定されています。
- **影響**:
  一般的なモダンブラウザでは補正されますが、RFC 3986 準拠の厳格なリンクチェッカー、プロキシ、古いユーザーエージェント等でリンク切れや不正URIと判定されるリスクがあります。またハンドル名は変更される可能性がありますが、チャンネルIDは恒久的です。
- **修正提案**:
  `REQUIREMENTS.md` 62行目およびリビルド前（`archive/`）で使用されていた恒常的なチャンネルID URLに差し替えてください。
  ```html
  <a href="https://www.youtube.com/channel/UCjIHn3E2Eji269ppA6b3VWQ" ...>
  ```

---

### 【Style】`about.html` のフッターナビゲーションにおける active クラス誤設定
- **該当箇所**: [`about.html#L216`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/about.html#L216)
- **問題点**:
  `about.html` のフッターナビで、`about.html` ではなく `<li><a href="videos.html" class="active">演奏動画</a></li>` に `class="active"` が付与されています（`videos.html` からのコピペミス）。
- **影響**:
  スタイル崩れには至っていませんが、整合性を欠きます。
- **修正提案**:
  `class="active"` を削除するか、`about.html` のリンクに正しく付け替えてください。

---

### 【Audit Check】検証スクリプト `tools/verify_site.py` の検証項目不足
- **該当箇所**: [`tools/verify_site.py#L170-L220`](file:///Users/nishimuranaoki/Downloads/AIプロダクト/nirasaki-taiko-portal/tools/verify_site.py#L170-L220)
- **問題点**:
  `verify_site.py` ではメニュー開閉やEscキー、リサイズテストを行っていますが、「メニューが閉じている時にTabキーを押してもメニュー内のリンクにフォーカスが当たらないこと」のテストが含まれていませんでした。
- **影響**:
  この自動検証の漏れにより、不完全な修正で「キーボードフォーカス漏れ解消」と誤認され、UX-AUDIT.md に合格と記録されてしまいました。
- **修正提案**:
  閉鎖状態の `.main-nav a` がフォーカス不能（`visibility: hidden` 等）であることをアサートするチェックを追記することを推奨します。

---

## 2. 4つの観点に対する個別チェック結果

| 観点 | 判定 | 主な確認内容 |
|---|---|---|
| **1. REQUIREMENTS.md の確認済み事実** | **概ね適合（一部修正要）** | 未公表の現顧問名・部員数・次回公演日の創作はありません。ただし前述の通り、動画サムネイルの `alt` テキストで過去の他イベント写真を「鍛麗2024/2025」と断定表記している点は要修正です。 |
| **2. 外部リンク先の整合性** | **適合（1点推奨あり）** | 学校公式サイト、文化ホール恒常URL（`/event/`）、YouTube動画ID（4本）、Instagram元投稿URLはすべて整合しています。`links.html` のYouTubeハンドル直書きはチャンネルID URLへの変更を推奨します。 |
| **3. セマンティクス・アクセシビリティ** | **要修正（2件のBugあり）** | フォーカスリング・prefers-reduced-motion・No-JS対応は良好ですが、**「モバイルメニュー閉鎖時のTabキーフォーカス漏れ」**と**「YouTube再生後のARIA属性不整合」**、**「H1がmain外にあるスキップリンク構造」**は速やかな修正が必要です。 |
| **4. 禁止事項の遵守** | **完全遵守** | npm依存なし、外部CDN/スクリプト/フォントなし（完全ローカル完結）、学校公式サイト画像の直接ダウンロード転載なし（すべてAssets2素材より加工）を確認しました。 |

## 3. タスク外変更ファイルの有無
指示書にない余計なファイルの変更・作成はありません。変更・作成されたファイルは指定の静的HTML 5ページ、共通CSS/JS、素材展開ツール、検証ツール、監査レポートのみです。