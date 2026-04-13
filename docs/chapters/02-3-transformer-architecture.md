# 📐 2.3 Transformer 結構解析 (Transformer Architecture Analysis)

## 核心機制：Self-Attention
Transformer 的核心在於 **Self-Attention** 機制，它允許模型在處理序列中的每個 Token 時，能夠「關注」序列中其他所有 Token 的相關資訊。其數學本質是透過計算 Query ($Q$) 與 Key ($K$) 之間的相似度，來決定 Value ($V$) 的權重分配。

## 矩陣運算與 Scaled Dot-Product Attention
對於輸入的 Embedding 矩陣 $\mathbf{X}$，我們透過三個可學習的權重矩陣 $\mathbf{W}^Q, \mathbf{W}^K, \mathbf{W}^V$ 得到 $Q, K, V$：
$$\mathbf{Q} = \mathbf{X}\mathbf{W}^Q, \quad \mathbf{K} = \mathbf{X}\mathbf{W}^K, \quad \mathbf{V} = \mathbf{X}\mathbf{W}^V$$

Attention Score 的計算公式如下：
$$\text{Attention}(\mathbf{Q}, \mathbf/K, \mathbf{V}) = \text{softmax}\left( \frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}} \right) \mathbf{V}$$

其中：
- $\mathbf{Q}\mathbf{K}^T$：計算 Query 與 Key 之間的點積（Dot-product），代表 Token 間的相關性強度。
- $\sqrt{d_k}$：縮放因子（Scaling factor），其中 $d_k$ 是 Key 向量的維度。其目的是防止點積結果過大，導致 Softmax 進入梯度極小的區域（Gradient Vanishing）。
- $\text{softmax}(\cdot)$：將分數轉換為機率分佈，確保所有權重之和為 1。

## 運算流程視覺化
當我們計算 $\mathbf{Q}\mathbf{K}^T$ 時，矩陣中的每個元素 $a_{ij}$ 代表了第 $i$ 個 Token 對第 $j$ 個 Token 的注意力權重。這種矩陣運算在 GPU 上可以透過高度並行化的矩陣乘法（GEMM）來實現，是 Transformer 高效運算的關鍵。
