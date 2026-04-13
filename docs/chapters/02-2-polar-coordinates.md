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
在處理量化（Quantization）過程中的旋轉與縮放變換時，極座標系具有顯著的優勢：
1. **直觀性**：旋轉變換在極座標下僅僅是 $\theta$ 的加法，而在笛卡兒座標下則涉及複雜的矩陣運算。
2. **計算效率**：在 PolarQuant 演算法中，透過分離幅度（Magnitude, $r$）與相位（Phase, $\theta$），我們可以針對不同特性的維度進行更精細、更低位元（Low-bit）的量化策略，從而降低記憶體壓力。
