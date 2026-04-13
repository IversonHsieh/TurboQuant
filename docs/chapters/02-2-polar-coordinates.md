# 📐 2.2 極座標系 (Polar Coordinate System)

## 核心概念
極座標系提供了一種不同的視角，透過徑向距離 $r$（從原點到點的距離）與角度 $\theta$（從正 $x$ 軸逆時針旋轉的角度）來定位平面上的點。

## 座標轉換 (Coordinate Transformation)
從笛卡兒座標 $(x, y)$ 轉換到極座標 $(r, \theta)$ 的公式如下：
$$r = \sqrt{x^2 + y^2}$$
$$\theta = \operatorname{atan2}(y, x)$$

反之，從極座標轉換回笛卡兒座標則為：
$$x = r \cos(\theta)$$
$$y = r \sin(\theta)$$

## 技術優勢：為什麼 TurboQuant 需要它？

在處理量化（Quantization）過程中的旋轉與縮放變換時，極座標系具有顯著的優勢。下圖展示了笛卡兒座標與極座標在處理旋轉變換時的本質差異：

![Rotation Comparison](./../svg/polar_rotation_comparison.svg)

### 1. **直觀性 (Intuitiveness)**
* **笛卡兒座標 (Cartesian)**：旋轉變換涉及矩陣乘法，需要計算 $\sin$ 與 $\cos$ 並與原座標進行線性組合：
  $$\begin{bmatrix} x' \\ y' \end{bmatrix} = \begin{bmatrix} \cos\theta & -\sin\theta \\ \sin\theta & \cos\theta \end{bmatrix} \begin{bmatrix} x \\ y \end{bmatrix}$$
  這在維度較高時，計算量隨維度增加而顯著上升。
* **極座標 (Polar)**：旋轉變換僅僅是角度 $\theta$ 的簡單加法：
  $$\theta_{new} = \theta + \Delta\theta$$
  這種變換在數學邏輯上極其直觀，且不涉及複雜的乘法運算。

### 2. **計算效率 (Computational Efficiency)**
在 **PolarQuant** 演算法中，透過將向量分解為幅度（Magnitude, $r$）與相位（Phase, $\theta$），我們可以實現更精細的量化策略：
* **解耦量化 (Decoupled Quantization)**：幅度 $r$ 與相位 $\theta$ 具有不同的統計特性。
* **低位元策略 (Low-bit Strategy)**：針對相位 $\theta$（通常對旋轉敏感度較高）與幅度 $r$（對能量敏感度較高）採用不同位元的量化精度，從而優化記憶體使用量並降低量化誤差。
