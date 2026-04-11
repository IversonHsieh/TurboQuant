# 📖 專有名詞拆解 (Glossary)

在深入理解 TurboQuant 的技術細節之前，我們需要先掌握幾個關鍵的技術術語。這些術語構成了現代大型語言模型（LLM）高效推理的核心基礎。

---

## 🧠 核心術語

### 1. KV Cache (Key-Value Cache)
**鍵值快取**。在 Transformer 架構的推理過程中，為了避免重複計算先前 Token 的 Attention 權重，我們會將先前計算過的 **Key** 與 **Value** 向量儲存起來。
- **痛點**：隨著上下文長度（Context Length）增加，KV Cache 的記憶體占用會呈線性增長，成為長文本處理的主要瓶頸。
- **TurboQuant 的角色**：透過極致的壓縮技術，大幅降低 KV Cache 的記憶體占用。

### 2. PolarQuant (極座標量化)
這是一種創新的量化技術，將高維向量從傳統的**笛卡兒座標系 (Cartesian Coordinates)** 轉換到**極座標系 (Polar Coordinates)**。
- **核心概念**：透過記錄向量的**半徑 (Radius)** 與**角度 (Angle)**，利用角度分布的集中性來減少量化過程中的資訊損失與計算負擔。

### 3. QJL (Quantized Johnson-Lindenstrauss)
基於 **Johnson-Lindenstrauss Lemma** 的一種極致壓縮技術。
- **核心概念**：利用隨機投影（Random Projection）的特性，將高維向量投影到低維空間，同時盡可能地保留向量之間的相對距離（相似度）。
- **技術特點**：在 TurboQuant 中，它被實現為一種 **1-bit** 的技術，僅需 1 個 bit 即可捕捉向量的方向資訊。

### 4. Johnson-Lindenstrauss Lemma
一個數學定理，指出高維空間中的點集可以被投影到一個維度較低的空間中，且點與點之間的距離關係幾乎不會改變。這為高效的向量壓縮與搜尋提供了數學上的保證。

---

*Last Updated: 2026-04-10*
