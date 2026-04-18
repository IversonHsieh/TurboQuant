# 均方誤差 (Mean-Squared Error, MSE) 深度解析

## 1. 什麼是 MSE？

**均方誤差 (Mean-Squared Error, MSE)** 是衡量預測值與真實值之間差異的一種常見統計指標。在機器學習、訊號處理以及量化演算法（如 TurboQuant）中，MSE 被廣泛用作「失真」（Distortion）或「誤差」（Error）的度量標準。

其核心思想是：計算每個樣本點的誤差平方，然後取這些平方誤差的平均值。

### 數學定義

對於一組包含 $n$ 個樣本的數據，假設真實值為 $y_i$，預測值（或量化後的重建值）為 $\hat{y}_i$，則 MSE 的計算公式如下：

$$
\text{MSE} = \frac{1}{n} \sum_{i=1}^{n} (y_i - \hat{y}_i)^2
$$

在向量量化（Vector Quantization）的語境下，我們通常關注的是向量 $\mathbf{x}$ 與其量化重建向量 $\mathbf{\tilde{x}}$ 之間的 $L_2$ 範數平方，這可以看作是各個維度上 MSE 的總和：

$$
D_{\text{mse}} = \mathbb{E}[\|\mathbf{x} - \mathbf{\tilde{x}}\|_2^2] = \mathbb{E} \left[ \sum_{j=1}^{d} (x_j - \tilde{x}_j)^2 \right]
$$

## 2. 為什麼要使用「平方」？

為什麼不直接使用誤差的平均值（MAE, Mean Absolute Error），而要使用平方？

1.  **放大較大的誤差**：平方操作會放大較大的誤差值，使得模型對於「離群點」（Outliers）或極端錯誤更加敏感。這在需要極高精度的場景（如 TurboQuant 追求的低失真率）中非常重要。
2.  **數學上的便利性**：MSE 的函數形式是處處可微的（Differentiable），這使得我們可以使用梯度下降（Gradient Descent）等優化演算法來最小化誤差。
3.  **懲罰特性**：它對較小的誤差給予較輕的懲罰，但對較大的誤差給予不成比例的重罰，這有助於穩定模型的收斂。

## 3. 實例說明

假設我們正在對一個 2 維向量進行量化。

*   **原始向量 (True Vector):** $\mathbf{x} = [1.0, 2.0]$
*   **量化後的重建向量 (Quantized Vector):** $\mathbf{\tilde{x}} = [1.2, 1.8]$

### 計算步驟：

1.  **計算每個維度的誤差 (Error):**
    *   維度 1: $1.0 - 1.2 = -0.2$
    *   維度 2: $2.0 - 1.8 = 0.2$

2.  **計算誤差的平方 (Squared Error):**
    *   維度 1: $(-0.2)^2 = 0.04$
    *   維度 2: $(0.2)^2 = 0.04$

3.  **計算平均值 (Mean):**
    *   $\text{MSE} = \frac{0.04 + 0.04}{2} = 0.04$

在這個例子中，MSE 為 $0.04$。如果我們使用 MAE (Mean Absolute Error)，結果會是 $\frac{|-0.2| + |0.2|}{2} = 0.2$。

## 4. 相關連結

*   **原文參考：** [TurboQuant 論文原文 (Abstract)](docs/chapters/03-turboquant-translation.md:17)
*   **中文翻譯參考：** [TurboQuant 論文翻譯 (Abstract)](docs/chapters/03-turboquant-translation.md:19)
