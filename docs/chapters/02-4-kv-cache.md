# 📐 2.4 KV Cache 解析 (KV Cache Analysis)

[🏠 返回目錄](../index.md)

## 核心概念：避免重複計算
在 Transformer 的自回算（Autoregressive）生成過程中，每生成一個新的 Token，模型都需要根據之前的 Token 序列來計算注意力權重。如果每次都重新計算所有先前 Token 的 Key ($\mathbf{K}$) 與 Value ($\mathbf{V}$) 向量，計算量將會隨著序列長度 $L$ 的增加而呈平方級別（$O(L^2)$）增長。

為了優化這個過程，我們引入了 **KV Cache** 技術。其核心思想是：將已經計算過的先前 Token 的 $\mathbf{K}$ 與 $\mathbf{V}$ 向量儲存在記憶體中，在生成下一個 Token 時，只需要計算當前新 Token 的 $\mathbf{Q}, \mathbf{K}, \mathbf{V}$，然後直接與快取中的 $\mathbf{K}$ 與 $\mathbf{V}$ 進行矩陣運算。

## 運算流程優化
假設序列長度為 $L$，當我們處理第 $L+1$ 個 Token 時：
- **不使用 KV Cache**：需要計算 $\mathbf{Q}_{1:L+1}, \mathbf{K}_{1:L+1}, \mathbf{V}_{1:L+1}$，並進行完整的注意力計算。
- **使用 KV Cache**：
  1. 從記憶體讀取 $\text{Cache}_K = \{\mathbf{k}_1, \dots, \mathbf{k}_L\}$ 與 $\text{Cache}_V = \{\mathbf{v}_1, \dots, \mathbf{v}_L\}$。
  2. 僅計算當前 Token 的 $\mathbf{q}_{L+1}, \mathbf{k}_{L+1}, \mathbf{v}_{L+1}$。
  3. 將 $\mathbf{k}_{L+1}$ 與 $\mathbf{v}_{L+1}$ 更新至 Cache 中。
  4. 計算 $\text{Attention}(\mathbf{q}_{L+1}, \text{Cache}_K, \text{cache}_V)$。

## 面臨的挑戰：記憶體壓力 (Memory Bottleneck)
雖然 KV Cache 顯著降低了計算量（從 $O(L^2)$ 降至 $O(L)$ 的單步計算量），但它帶來了嚴重的**記憶體容量問題**：
1. **空間複雜度**：隨著序列長度 $L$ 的增加，KV Cache 的大小會線性增長。對於長文本（Long Context）場景，KV Cache 可能會佔用數 GB 甚至更多的顯存（VRAM）。
2. **頻寬瓶頸**：在推理（Inference）過程中，頻繁地從記憶體讀取龐大的 KV Cache 會導致記憶體頻寬（Memory Bandwidth）成為效能瓶頸，限制了 Token 的生成速度（Decoding Throughput）。

這正是 **TurboQuant** 試圖解決的核心問題：如何透過更高效的量化技術（如 PolarQuant）來壓縮 KV Cache 的體積，同時維持模型的精準度。
