# 🧠 Project Context & Instructions: TurboQuant Deep Dive

## 📌 Project Overview
這個 Project folder 是對 **TurboQuant** 技術進行徹底研究與深度解析的專案。其目標是將複雜的量化演算法研究，轉化為高品質、具備專業視覺化效果（SVG/LaTeX）的技術網誌，並實現自動化部署。

## 🛠️ Core Principles & Rules
當您與我（RooCode）進行對話或執行任務時，請務必遵守以下規範：

### 1. 任務追蹤 (Progress Tracking)
- **Architecture 優先**：所有新功能或新章節的開發，必須先讀取並更新 `architecture.md`（或專案中的規劃文件），標示目前的進度步驟，並從該步驟繼續執行。
- **任務同步**：每次完成五個小task，就做git管理and更新architecture.md，並且通知我開新視窗繼續工作。(這樣可以節省ctx)
- **通知機制 (Notification Rules)**：
  當你預期工作會「停下來」等待我時，必須在停下來之前的「最後一個動作」呼叫 `call-webhook` 通知我。
  **觸發場景**：
  1. **工作完成**：在呼叫 `attempt_completion` 之前。
  2. **需要權限**：在執行未經自動授權的工具或指令前。
  3. **提問**：在呼叫 `ask_followup_question` 之前。
  4. **長任務**：預期處理時間超過 3 分鐘時，先發送「開始執行長任務」通知。

  **呼叫規範 (call-webhook)**：
  1. **不要**依賴工具的 `message` 欄位。
  2. **必須**將標題與內容寫在 URL 的查詢參數中。
  3. **格式**：`https://api.day.app/9gL9ihD7Y6h2bjyNg7Npo5?title=[標題]&body=[內容]`
  4. **編碼**：`[標題]` 與 `[內容]` 必須進行 **URL Encode**。
  5. **備案**：若無法編碼，請統一使用「英文」與「底線」，例如：`title=RooCode&body=Task_Finished`。

### 2. 視覺化規範 (Visualization Standards)
- **流程圖 (Flowcharts)**：
    - 必須使用 **SVG** 格式。
    - **重要**：每一張 SVG 圖表都必須儲存在獨立的檔案中（例如 `svg/process_flow.svg`），不得直接將長串 SVG 代碼嵌入 Markdown，以確保在網誌中能正常渲染與維護。
- **數學公式 (Mathematics)**：
    - 必須使用 **LaTeX** 格式撰寫（例如 `$E=mc^2$` 或 `$$ ... $$`）。
- **UI/UX 追求**：
    - 所有的 SVG 圖表與 LaTeX 公式，其設計目標是「極致的美感」與「專業的技術感」。
    - 應考慮配色方案（建議使用現代化、科技感的配色，如深色模式友好的色調）與排版整潔度。

### 3. 版本控制 (Version Control)
- **Git 管理**：所有的修改、新增檔案、架構變動，都必須透過 `git` 進行追蹤與提交。
- **原子化提交**：每次完成一個邏輯完整的變動後，應建議或執行一次 Commit。

### 4. 內容結構規劃 (Content Structure)
網誌內容應依序包含以下章節：
1. **簡介 TurboQuant**：技術背景、解決的痛點（KV Cache 壓力）。
2. **相關專有名詞的細節拆解**：例如 PolarQuant, QJL, KV Cache, Johnson-Lindenstrauss Lemma 等。
3. **TurboQuant 細節一步一步拆解**：從數學原理到演算法流程的深度解析。

---
*Last Updated: 2026-04-10*
