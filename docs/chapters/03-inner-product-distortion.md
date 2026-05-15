# 什麼是 Inner Product Distortion（內積失真）？

[🏠 返回目錄](../index.md)

## 定義與背景

在高維向量量化（Vector Quantization, VQ）中，除了常見的均方誤差（MSE, Mean Squared Error）外，「內積失真（Inner Product Distortion）」也是一個極為重要的衡量指標。它描述的是：

> 當原始向量 $\mathbf{x}$ 被量化為 $\hat{\mathbf{x}}$ 後，與另一個查詢向量 $\mathbf{q}$ 的內積 $\langle \mathbf{q}, \mathbf{x} \rangle$ 與 $\langle \mathbf{q}, \hat{\mathbf{x}} \rangle$ 之間的誤差。

這在搜尋、檢索、深度學習推論等場景中非常關鍵，因為許多應用直接依賴於內積計算的精確性。

## 形式化定義

內積失真的數學定義如下：

$$
\text{Inner Product Distortion} = \left| \langle \mathbf{q}, \mathbf{x} \rangle - \langle \mathbf{q}, \hat{\mathbf{x}} \rangle \right|
$$

其中：
- $\mathbf{x}$：原始高維向量
- $\hat{\mathbf{x}}$：量化後的向量
- $\mathbf{q}$：查詢向量

## 舉例說明

假設有一個原始向量 $\mathbf{x} = [1.2, -0.7, 3.5]$，查詢向量 $\mathbf{q} = [2, 0, -1]$。

- 原始內積：$\langle \mathbf{q}, \mathbf{x} \rangle = 2 \times 1.2 + 0 \times (-0.7) + (-1) \times 3.5 = 2.4 - 3.5 = -1.1$
- 假設量化後 $\hat{\mathbf{x}} = [1, -1, 4]$
- 量化後內積：$\langle \mathbf{q}, \hat{\mathbf{x}} \rangle = 2 \times 1 + 0 \times (-1) + (-1) \times 4 = 2 - 4 = -2$
- 內積失真：$|-1.1 - (-2)| = 0.9$

## 圖示說明

![inner_product_distortion](../svg/inner_product_distortion.svg)

圖中展示了原始向量、查詢向量與量化後向量在空間中的關係，以及內積失真的幾何意義。

## 與 MSE 的差異

- **MSE** 著重於每個座標的誤差平均。
- **內積失真** 著重於整體內積計算的誤差。
- 在某些應用（如最近鄰搜尋、語意檢索）中，內積失真比 MSE 更直接影響查詢結果。

## TurboQuant 如何處理內積失真？

如 [`03-turboquant-translation.md:17`](03-turboquant-translation.md:17) 所述，TurboQuant 不僅最小化 MSE，也針對內積失真提出創新解法：
- 首先進行 MSE 最佳化量化
- 再對殘差進行 1-bit QJL 變換，得到無偏的內積估計

詳細數學推導與理論下界證明，請參考原文與翻譯：[`03-turboquant-translation.md:17`](03-turboquant-translation.md:17)

---

[返回 TurboQuant 論文翻譯](03-turboquant-translation.md:17)

[深入了解內積失真（Inner Product Distortion）](03-inner-product-distortion.md)

---

> 本頁內容引用自 [`03-turboquant-translation.md:17`](03-turboquant-translation.md:17)、[`03-turboquant-translation.md:21`](03-turboquant-translation.md:21)。
> 
> [回到 TurboQuant 論文翻譯摘要](03-turboquant-translation.md:17)
> 
> [回到 TurboQuant 論文翻譯摘要（中文）](03-turboquant-translation.md:21)
> 
> [回到 TurboQuant 內積失真說明](03-inner-product-distortion.md)
