# Brute-Force Nearest Neighbor Search (暴力法最近鄰搜尋)

[🏠 返回目錄](../index.md) | [返回主翻譯頁面](03-turboquant-translation.md)

## 定義

**Brute-Force Nearest Neighbor Search**（暴力法最近鄰搜尋），也稱為「窮舉搜尋」或「線性搜尋」，是在一個資料集（通常是一組向量）中，尋找與目標查詢向量（Query Vector）距離最近的一個或多個向量的方法。

其核心思想是：**計算目標向量與資料集中「每一個」樣本向量之間的距離，並找出其中距離最小的那個。**

## 數學描述

給定一個資料集 $X = \{x_1, x_2, \dots, x_N\} \subset \mathbb{R}^d$，以及一個查詢向量 $q \in \mathbb{R}^d$。
暴力法搜尋的目標是找到索引 $i^*$，使得：

$$i^* = \arg\min_{i=1 \dots N} \text{dist}(q, x_i)$$

其中 $\text{dist}(\cdot, \cdot)$ 是距離度量，最常用的是歐幾里得距離（$L_2$ Norm）：

$$\text{dist}(q, x_i) = \|q - x_i\|_2 = \sqrt{\sum_{j=1}^d (q_j - x_{i,j})^2}$$

## 實例說明

假設我們在一個二維平面上有 4 個點（資料集）和一個查詢點 $q$：
- $x_1 = (1, 2)$
- $x_2 = (4, 5)$
- $x_3 = (2, 1)$
- $x_4 = (5, 3)$
- $q = (2, 2)$

**搜尋步驟**：
1. 計算 $\text{dist}(q, x_1) = \sqrt{(2-1)^2 + (2-2)^2} = \sqrt{1+0} = 1$
2. 計算 $\text{dist}(q, x_2) = \sqrt{(2-4)^2 + (2-5)^2} = \sqrt{4+9} = \sqrt{13} \approx 3.61$
3. 計算 $\text{dist}(q, x_3) = \sqrt{(2-2)^2 + (2-1)^2} = \sqrt{0+1} = 1$
4. 計算 $\text{dist}(q, x_4) = \sqrt{(2-5)^2 + (2-3)^2} = \sqrt{9+1} = \sqrt{10} \approx 3.16$

比較結果：最小值為 $1$（對應點 $x_1$ 與 $x_3$）。

## 圖解說明

![](/docs/svg/nearest_neighbor_search.svg)

*(註：上圖展示了目標點 $q$ 與資料點之間的距離計算，以及如何比較得出最近的鄰居。)*

## 效能與限制

- **優點**：確保找到絕對精確的最近鄰結果（Exact Search），實現簡單。
- **缺點**：計算複雜度為 $O(N \cdot d)$。當資料集 $N$ 非常大時，搜尋速度會變得非常慢，不適用於即時需求高的場景（例如大型向量資料庫搜尋）。

---
[返回主翻譯頁面](03-turboquant-translation.md)
