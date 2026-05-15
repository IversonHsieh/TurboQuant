# 📐 2.1 笛卡兒座標系 (Cartesian Coordinate System)

[🏠 返回目錄](../index.md)

## 核心概念
笛卡兒座標系是我們在處理高維向量空間（如 LLM 的 Embedding Space）時最常用的基準。在二維平面上，任何一點都可以透過其與 $x$ 軸與 $y$ 軸的垂直距離來定義，表示為 $(x, y)$。

## 向量的數學基礎
在機器學習的語境下，我們更常將其視為向量（Vector）的表示法。一個二進向量 $\mathbf{v}$ 可以表示為：
$$\mathbf{v} = \begin{bmatrix} x \\ y \end{bmatrix}$$

其基本運算包括：
- **向量加法 (Vector Addition)**：
  $$\begin{bmatrix} x_1 \\ y_1 \end{bmatrix} + \begin{bmatrix} x_2 \\ y_2 \end{bmatrix} = \begin{bmatrix} x_1 + x_2 \\ y_1 + y_2 \end{bmatrix}$$
- **純量乘法 (Scalar Multiplication)**：
  $$c \cdot \begin{bmatrix} x \\ y \end{bmatrix} = \begin{bmatrix} cx \\ cy \end{bmatrix}$$

## 技術關聯
在大型語言模型（LLMs）中，Token 的 Embedding 被表示為高維空間中的點。笛卡兒座標系提供了我們計算餘弦相似度（Cosine Similarity）與歐幾里得距離（Euclidean Distance）的標準框架。
