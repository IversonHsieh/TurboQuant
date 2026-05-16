# 📐 2.1 座標系統：笛卡兒與極座標 (Cartesian & Polar Coordinate Systems)

[🏠 返回目錄](../index.md)

## 旋轉變換的直觀對比

在量化（Quantization）過程中，座標系的選擇對旋轉與縮放變換的處理方式有著本質差異。下圖展示了笛卡兒座標與極座標在處理旋轉變換時的關鍵差異：

![Rotation Comparison](../svg/polar_rotation_comparison.svg)

> 💡 **核心洞察**：在笛卡兒座標中，旋轉需要矩陣乘法；在極座標中，旋轉僅需角度加法。這正是 PolarQuant 演算法的基礎動機。

---

## 笛卡兒座標系 (Cartesian Coordinate System)

### 核心概念
笛卡兒座標系是我們在處理高維向量空間（如 LLM 的 Embedding Space）時最常用的基準。在二維平面上，任何一點都可以透過其與 $x$ 軸與 $y$ 軸的垂直距離來定義，表示為 $(x, y)$。

### 向量的數學基礎
在機器學習的語境下，我們更常將其視為向量（Vector）的表示法。一個二維向量 $\mathbf{v}$ 可以表示為：
$$\mathbf{v} = \begin{bmatrix} x \\ y \end{bmatrix}$$

其基本運算包括：
- **向量加法 (Vector Addition)**：
  $$\begin{bmatrix} x_1 \\ y_1 \end{bmatrix} + \begin{bmatrix} x_2 \\ y_2 \end{bmatrix} = \begin{bmatrix} x_1 + x_2 \\ y_1 + y_2 \end{bmatrix}$$
- **純量乘法 (Scalar Multiplication)**：
  $$c \cdot \begin{bmatrix} x \\ y \end{bmatrix} = \begin{bmatrix} cx \\ cy \end{bmatrix}$$

### 旋轉變換
在笛卡兒座標中，旋轉變換涉及矩陣乘法，需要計算 $\sin$ 與 $\cos$ 並與原座標進行線性組合：
$$\begin{bmatrix} x' \\ y' \end{bmatrix} = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix}$$
這在維度較高時，計算量隨維度增加而顯著上升。

### 技術關聯
在大型語言模型（LLMs）中，Token 的 Embedding 被表示為高維空間中的點。笛卡兒座標系提供了我們計算餘弦相似度（Cosine Similarity）與歐幾里得距離（Euclidean Distance）的標準框架。

---

## 極座標系 (Polar Coordinate System)

### 核心概念
極座標系提供了一種不同的視角，透過徑向距離 $r$（從原點到點的距離）與角度 $\theta$（從正 $x$ 軸逆時針旋轉的角度）來定位平面上的點。

### 旋轉變換
在極座標中，旋轉變換僅僅是角度 $\theta$ 的簡單加法：
$$\theta_{new} = \theta + \Delta\theta$$
這種變換在數學邏輯上極其直觀，且不涉及複雜的乘法運算。

---

## 座標轉換 (Coordinate Transformation)

從笛卡兒座標 $(x, y)$ 轉換到極座標 $(r, \theta)$ 的公式如下：
$$r = \sqrt{x^2 + y^2}$$
$$\theta = \operatorname{atan2}(y, x)$$

反之，從極座標轉換回笛卡兒座標則為：
$$x = r \cos(\theta)$$
$$y = r \sin(\theta)$$

---

## 技術優勢：為什麼 TurboQuant 需要極座標？

在 **PolarQuant** 演算法中，透過將向量分解為幅度（Magnitude, $r$）與相位（Phase, $\theta$），我們可以實現更精細的量化策略：

### 1. 解耦量化 (Decoupled Quantization)
幅度 $r$ 與相位 $\theta$ 具有不同的統計特性，可以獨立處理，互不干擾。

### 2. 低位元策略 (Low-bit Strategy)
針對相位 $\theta$（通常對旋轉敏感度較高）與幅度 $r$（對能量敏感度較高）採用不同位元的量化精度，從而優化記憶體使用量並降低量化誤差。

### 3. 計算效率 (Computational Efficiency)
極座標下的旋轉操作從 $O(d^2)$ 的矩陣乘法降為 $O(d)$ 的角度加法，大幅減少計算開銷。