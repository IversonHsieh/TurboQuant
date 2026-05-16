# 🧠 Project Context & Instructions: TurboQuant Deep Dive

## 📌 Project Overview
這個 Project folder 是對 **TurboQuant** 技術進行徹底研究與深度解析的專案。其目標是將複雜的量化演算法研究，轉化為高品質、具備專業視覺化效果（SVG/LaTeX）的技術網誌，並實現自動化部署。

## 🛠️ Core Principles & Rules
當您與我（RooCode）進行對話或執行任務時，請務必遵守以下規範：

### 1. 任務追蹤 (Progress Tracking)
- **Architecture 優先**：所有新功能或新章節的開發，必須先讀取並更新 `architecture.md`（或專案中的規劃文件），標示目前的進度步驟，並從該步驟繼續執行。

### 2. 視覺化規範 (Visualization Standards)
- **流程圖 (Flowcharts)**：
    - 必須使用 **SVG** 格式。
    - **重要**：每一張 SVG 圖表都必須儲存在獨立的檔案中（例如 `svg/process_flow.svg`），不得直接將長串 SVG 代碼嵌入 Markdown，以確保在網誌中能正常渲染與維護。
    - **注意**：SVG 檔案內**禁止**使用 LaTeX 語法（如 `$ ... $`），應使用標準 Unicode 字元（ 如 `θ`、`Δ`）以確保在所有預覽器（如 VSCode）中能正常顯示。
    - **驗證**：完成後必須使用**網頁瀏覽器**開啟 SVG 檔案，確認圖形與文字能正確且無錯誤地顯示。
- **數學公式 (Mathematics)**：
    - 必須使用 **LaTeX** 格式撰寫（例如 `$E=mc^2$` 或 `$$ ... $$`）。
- **UI/UX 追求**：
    - 所有的 SVG 圖表與 LaTeX 公式，其設計目標是「極致的美感」與「專業的技術感」。
    - 應考慮配色方案（建議使用現代化、科技感的配色，如深色模式友好的色調）與排版整潔度。
- **網頁相關讀取與瀏覽**：
    - 請使用 `mcp--puppeteer--puppeteer_navigate` 進行網頁導航與內容讀取。

### 3. 檔案修改規範 (File Modification Rules)
- **apply_diff 失敗處理**：
    - 若使用 `apply_diff` 修改檔案失敗時，應改用 `write_to_file` 重新寫入完整的檔案內容。

### 4. 版本控制 (Version Control)
- **Git 管理**：所有的修改、新增檔案、架構變動，都必須透過 `git` 進行追蹤與提交。
- **原子化提交**：每次完成一個邏輯完整的變動後，應建議或執行一次 Commit。

### 5. 內容結構規劃 (Content Structure)
網誌內容應依序包含以下章節：
1. **簡介 TurboQuant**：技術背景、解決的痛點（KV Cache 壓力）。
2. **相關專有名詞的細節拆解**：例如 PolarQuant, QJL, KV Cache, Johnson-Lindenstrauss Lemma 等。
3. **TurboQuant 細節一步一步拆解**：從數學原理到演算法流程的深度解析。
### 6. 網頁部署與同步 (Web Deployment & Sync)
- **部署架構**：使用 VitePress + GitHub Pages，網址為 `https://iversonhsieh.github.io/TurboQuant/`
- **自動部署**：推送至 `main` 分支時，GitHub Actions 會自動 build 並部署（`.github/workflows/deploy.yml`）
- **同步指令**：當你修改或新增 `.md` 檔案後，告訴我「**deploy**」或「**推送網頁**」，我就會執行以下流程：
  1. `npm run build` — 確認 build 成功
  2. `git add -A && git commit -m "描述變更" && git push` — 提交並推送
  3. 等待 GitHub Actions 部署完成後，用瀏覽器確認網站正常
- **新增章節注意事項**：如果新增了 `.md` 檔案，需要同時在 `docs/.vitepress/config.mjs` 的 `sidebar` 中加入對應連結，否則新頁面不會出現在側邊欄導航中
- **SVG 圖片路徑**：在 `docs/chapters/` 下的 `.md` 中引用 `docs/svg/` 的圖片時，使用相對路徑 `../svg/xxx.svg`（不要用絕對路徑 `/svg/xxx.svg`）
- **LaTeX 公式**：已啟用 `markdown-it-mathjax3`，直接使用 `$...$`（行內）和 `$$...$$`（區塊）即可

### 7. VitePress 排版調整經驗 (Layout Tuning)
- **問題**：VitePress 預設在 PC 大螢幕上內容區域偏窄（約 688px），兩側空白過多
- **根本原因**：VitePress 使用多層 CSS 限制寬度：
  - `--vp-layout-max-width` CSS 變數（預設 `1440px`）控制整體佈局最大寬度
  - `.VPDoc` 有固定 `width` 值（如 `1160px`）
  - `.content-container` 有 `max-width: 688px`
  - `.aside`（右側大綱）佔 256px
- **解決方案**（在 `docs/.vitepress/theme/custom.css` 中）：
  1. 在 `:root` 中覆寫 `--vp-layout-max-width: 1700px !important;`（比預設 1440px 寬，但不會像 100% 太寬）
  2. 在 `@media (min-width: 1280px)` 中覆寫：
     - `.VPDoc .content-container { max-width: 100% !important; }`
     - `.VPDoc .content { max-width: 100%; padding: 0; }`
     - `.VPDoc { width: auto !important; flex-grow: 1 !important; }`
     - `.VPDoc .aside { width: 180px; min-width: 180px; }`
  3. 所有寬度覆寫都放在 `@media (min-width: 1280px)` 內，確保 iPhone/iPad 不受影響
- **驗證方式**：使用 Puppeteer MCP 設定不同 viewport 尺寸（375x812 iPhone、768x1024 iPad、1920x1080 PC）截圖確認
- **瀏覽器快取問題**：部署後若 PC Chrome 顯示異常（白底、排版亂），按 **Ctrl+Shift+R** 強制重新整理即可
- **效果**（1920px PC 螢幕）：
  | 項目 | 原始值 | 調整後 |
  |------|--------|--------|
  | 佈局最大寬度 | 1440px | 1700px |
  | 內容區寬度 | 688px | ~1208px |
  | 右側大綱寬度 | 256px | 180px |

---

*Last Updated: 2026-05-16*
