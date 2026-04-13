# 🏗️ TurboQuant Blog Architecture Plan

## 🎯 Objective
建立一個高效、美觀且自動化部署的技術網誌，用於展示 TurboQuant 的深度研究成果。

## 🛠️ Technical Stack
- **Static Site Generator (SSG)**: [VitePress](https://vitepress.dev/)
    - *Reason*: 極速的開發體驗、基於 Vue 3、對 Markdown 支援極佳、適合技術文件。
- **Deployment**: [GitHub Pages](https://pages.github.com/)
    - *Reason*: 與 GitHub 整合度最高、免費、支援自動化部署。
- **CI/CD**: [GitHub Actions](https://github.com/features/actions)
    - *Reason*: 實現「一-鍵上傳」的核心，當 `git push` 時自動編譯並部署。
- **Mathematical Notation**: [KaTeX](https://katex.org/)
    - *Reason*: 比 MathJax 更快，適合網誌的即時渲染需求。
- **Visualizations**:
    - **Flowcharts**: SVG (獨立檔案儲存)。
    - **Math**: LaTeX 語法。
- **Styling**: Custom CSS/SCSS (追求極致的 UI/UX)。

## 📂 Directory Structure
```text
.
├── .github/
│   └── workflows/
│       └── deploy.yml          # GitHub Actions 部署腳本
├── docs/                       # VitePress 根目錄
│   ├── .vitepress/
│   │   ├── config.mjs          # VitePress 配置 (主題、導航、KaTeX 插件)
│   │   └── theme/              # 自定義主題與 CSS
│   │       └── custom.css      # 全局樣式 (UI/UX 優化)
│   ├── assets/                 # 靜態資源 (圖片、字體)
│   ├── svg/                    # 所有的 SVG 流程圖 (獨立檔案)
│   │   └── flowchart.svg
│   ├── chapters/               # 核心內容章節
│   │   ├── 01-introduction.md  # 簡介 TurboQuant
│   │   ├── 02-glossary.md      # 相關專有名詞細節拆解
│   │   └── 03-deep-dive.md     # TurboQuant 細節一步一步拆解
│   └── index.md                # 網誌首頁 (Landing Page)
├── scripts/                    # 自動化腳本 (例如：SVG 檢查、部署輔助)
├── package.json                # 專案依賴與指令
└── architecture.md             # 本架構文件
```

## 🚀 Deployment Workflow (The "One-Click" Process)
1. **Developer**: 完成內容修改 $\to$ `git add .` $\to$ `git commit -m "Update content"` $\to$ `git push origin main`.
2. **GitHub Actions**: 
    - 偵測到 `push` 事件。
    - 啟動虛擬機，安裝 Node.js 與依賴。
    - 執行 `npm run build` (VitePress 編譯)。
    - 將 `docs/.vitepress/dist` 目錄內容推送到 `gh-pages` 分支。
3. **GitHub Pages**: 自動從 `gh-pages` 分支讀取內容並更新網站。

## 📊 Progress Tracking
- [x] 第一階段：環境初始化與基礎架構搭建 (Foundation)
- [x] 第二階段：內容遷移與結構化 (Content Migration)
    - [x] 章節 1: 簡介 Turbo
    - [x] 章節 2: 基礎數學
        - [x] 章節 2.1: 笛卡兒座標系解析
        - [x] 章節 2.2: 極座標系
        - [ ] 章節 2.3: 前饋神經網路 (Feed-Forward Neural Network)
        - [-] 章節 2.4: Transformer 結構解析 (翻譯自 [The Illustrated Transformer](https://jalammar.github.io/illustrated-transformer/))
            - [-] 內容抓取與翻譯 (使用 Puppeteer)
            - [-] 視覺化資源製作 (SVG)
            - [ ] 內容整合與文件生成
            - [ ] 最終驗證
        - [x] 章節 2.5: KV Cache 解析
        - [x] 章節 2.6: PolarQuant 解析
        - [x] 章節 2.7: QJL (Quantized Johnson-Lindenstrauss) 解析
    - [-] 章節 3: TurboQuant 細節一步一步拆解
- [x] 資源路徑校正 (Path Correction)
- [ ] 第三階段：視覺化優化與美化 (Visual Enhancement)
    - [ ] SVG 流程圖優化 (檢查 docs/svg/flowchart.svg 配色與設計)
    - [ ] LaTeX 公式美化 (檢查各章節公式排版與渲染)
    - [ ] 自定義 CSS 強化 (優化 docs/.vitepress/theme/custom.css)
- [ ] 第四階段：驗證與部署 (Verification & Deployment)
    - [ ] 建立 GitHub Actions 部署腳本 (.github/workflows/deploy.yml)
    - [ ] 端到端測試 (執行 npm run build 並檢查編譯結果)
    - [ ] 最終檢查 (檢查所有資源路徑與連結)

## 🎨 UI/UX Design Principles
- **Typography**: 使用清晰的無襯線字體 (Sans-serif)，確保長文閱讀不疲勞。
- **Color Palette**: 採用深色模式 (Dark Mode) 為主，搭配科技感的藍/青色 (Cyan) 作為強調色。
- **Mathematical Beauty**: LaTeX 公式需有適當的間距與字體大小，確保在行動端與桌面端皆清晰。
	- 使用 `$$ ... $$` 進行區塊公式排版。
- **SVG Integration**: 所有的 SVG 必須具備響應式設計，並在 Markdown 中以 `![alt](path/to/file.svg)` 的方式引用。

---
*Status: Draft*
*Last Updated: 2026-04-11*
