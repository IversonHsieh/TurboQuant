# 📐 章節 2：數學基礎 (Mathematical Foundations)

本章節將深入探討理解 TurboQuant 演算法所需的關鍵數學背景，從基礎的座標系轉換到複雜的維度縮減理論。

## 2.1 笛卡兒座標系 (Cartesian Coordinate System)

### 核心概念
笛卡兒座標系是我們在處理高維向量空間（如 LLM 的 Embedding Space）時最常用的基準。在二維平面上，任何一點都可以透過其與 $x$ 軸與 $y$ 軸的垂直距離來定義，表示為 $(x, y)$。

### 向量的數學基礎
在機器學習的語境下，我們更常將其視為向量（Vector）的表示法。一個二進向量 $\mathbf{v}$ 可以表示為：
$$\mathbf{v} = \begin{bmatrix} x \\ y \end{bmatrix}$$

其基本運算包括：
- **向量加法 (Vector Addition)**：
  $$\begin{bmatrix} x_1 \\ y_1 \end{bmatrix} + \begin{bmatrix} x_2 \\ y_2 \end{bmatrix} = \begin{bmatrix} x_1 + x_2 \\ y_1 + y_2 \end{bmatrix}$$
- **純量乘法 (Scalar Multiplication)**：
  $$c \cdot \begin{bmatrix} x \\ y \end{bmatrix} = \begin{bmatrix} cx \\ cy \end{bmatrix}$$

### 技術關聯
在大型語言模型（LLMs）中，Token 的 Embedding 被表示為高維空間中的點。笛卡兒座標系提供了我們計算餘弦相似度（Cosine Similarity）與歐幾里得距離（Euclidean Distance）的標準框架。

---

## 2.2 極座標系 (Polar Coordinate System)

### 核心概念
極座標系提供了一種不同的視角，透過徑向距離 $r$（從原點到點的距離）與角度 $\theta$（從正 $x$ 軸逆時針旋轉的角度）來定位平面上的點。

### 座標轉換 (Coordinate Transformation)
從笛卡兒座標 $(x, y)$ 轉換到極座標 $(r, \theta)$ 的公式如下：
$$r = \sqrt{x^2 + y^2}$$
$$\theta = \operatorname{atan2}(y, x)$$

反之，從極座標轉換回笛卡兒座標則為：
$$x = r \cos(\theta)$$
$$y = r \sin(\theta)$$

### 技術優勢：為什麼 TurboQuant 需要它？
在處理量化（Quantization）過程中的旋轉與縮放變換時，極座標系具有顯著的優勢：
1. **直觀性**：旋轉變換在極座標下僅僅是 $\theta$ 的加法，而在笛卡兒座標下則涉及複雜的矩陣運算。
2. **計算效率**：在 PolarQuant 演算法中，透過分離幅度（Magnitude, $r$）與相位（Phase, $\theta$），我們可以針對不同特性的維度進行更精細、更低位元（Low-bit）的量化策略，從而降低記憶體壓力。

## 2.3 Transformer 結構解析 (Transformer Architecture Analysis)

### 核心機制：Self-Attention
Transformer 的核心在於 **Self-Attention** 機制，它允許模型在處理序列中的每個 Token 時，能夠「關注」序列中其他所有 Token 的相關資訊。其數學本質是透過計算 Query ($Q$) 與 Key ($K$) 之間的相似度，來決定 Value ($V$) 的權重分配。

### 矩陣運算與 Scaled Dot-Product Attention
對於輸入的 Embedding 矩陣 $\mathbf{X}$，我們透過三個可學習的權重矩陣 $\mathbf{W}^Q, \mathbf{進W}^K, \mathbf{W}^V$ 得到 $Q, K, V$：
$$\mathbf{Q} = \mathbf{X}\mathbf{W}^Q, \quad \mathbf{K} = \mathbf{X}\mathbf{W}^K, \quad \mathbf{V} = \mathbf{X}\mathbf{W}^V$$

Attention Score 的計算公式如下：
$$\text{Attention}(\mathbf{Q}, \mathbf{K}, \mathbf{V}) = \text{softmax}\left( \frac{\mathbf{Q}\mathbf{K}^T}{\sqrt{d_k}} \right) \mathbf{V}$$

其中：
- $\mathbf{Q}\mathbf{K}^T$：計算 Query 與 Key 之間的點積（Dot-product），代表 Token 間的相關性強度。
- $\sqrt{d_k}$：縮放因子（Scaling factor），其中 $d_k$ 是 Key 向量的維度。其目的是防止點積結果過大，導致 Softmax 進入梯度極小的區域（Gradient Vanishing）。
- $\text{softmax}(\cdot)$：將分數轉換為機率分佈，確保所有權重之和為 1。

### 運算流程視覺化
當我們計算 $\mathbf{Q}\mathbf{K}^T$ 時，矩陣中的每個元素 $a_{ij}$ 代表了第 $i$ 個 Token 對第 $j$ 個 Token 的注意力權重。這種矩陣運算在 GPU 上可以透過高度並行化的矩陣乘法（GEMM）來實現，是 Transformer 高效運算的關鍵。

---
