# 🚀 章節 3：TurboQuant 深度解析 (TurboQuant Deep Dive)

[🏠 返回目錄](../index.md)

本章節將深入探討 TurboQuant 演算法的具體實作流程，從輸入的原始 Embedding 到最終壓縮後的 KV Cache 儲存，詳細解析其核心技術步驟。

## 3.1 TurboQuant 演算法全景 (Algorithm Overview)

### 🔄 演算法端到端流程 (End-to-End Pipeline)

TurboQuant 的核心流程可以概括為一個從高維、高精度向量到低維、低位元壓縮向量的轉換過程。

*(註：TurboQuant Algorithm Flow 流程圖待實作)*

### 🛠️ 核心處理步驟說明

1.  **輸入 (Input)**：接收來自 Transformer 模型前一層的原始高維 Embedding 向量 $\mathbf{X}$。
2.  **極座標轉換 (Polar Transformation)**：
    - 將笛卡組座標下的向量 $\mathbf{x} = [x_1, x_2, \dots, x_d]$ 轉換為極座標表示法。
    - 計算每個維度的幅度 $r$ 與相位 $\theta$。
3.  **分層量化 (Hierarchical Quantization - PolarQuant)**：
    - **幅度量化**：對 $r$ 進行較高位元的量化（例如 4-bit 或 8-bit），以保留關鍵的能量資訊。
    - **相位量化**：對 $\theta$ 進行極低位元的量化（例如 2-bit 或 3-bit），利用角度的連續性來極大化壓縮率。
4.  **維度縮減 (Dimensionality Reduction - QJL Projection)**：
    - 使用量化後的隨機投影矩陣 $\mathbf{P}$，將轉換後的向量投影到更低維度的空間。
    - 透過 QJL 技術，確保投影後的向量間距與原始空間高度一致。
5.  **輸出 (Output - Compressed KV Cache)**：
    - 產生壓縮後的 $\mathbf{K}$ 與 $\mathbf{V}$ 向量，並將其儲存於 KV Cache 中，供後續 Token 生成時使用。

---
