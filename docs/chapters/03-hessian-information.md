# Hessian 矩陣與二階資訊詳解

[🏠 返回目錄](../index.md)

## 概述
在最佳化問題中，我們通常關注函數如何隨參數變化。**二階資訊 (Second-order information)** 指的是函數對參數的二階導數，通常以 **Hessian 矩陣**表示。它描述了函數在某一點的「曲率」資訊，這比僅依賴一階導數（梯度）能提供更豐富的結構資訊，幫助我們更快、更準確地找到極值。

## 數學定義
假設有一個純量函數 $f(\mathbf{x})$，其中 $\mathbf{x} = [x_1, x_2, ..., x_n]^T$。

1. **一階導數 (梯度 Vector)**:
   $$\nabla f(\mathbf{x}) = \left[ \frac{\partial f}{\partial x_1}, \frac{\partial f}{\partial x_2}, ..., \frac{\partial f}{\partial x_n} \right]^T$$

2. **二階導數 (Hessian Matrix $H$)**:
   Hessian 矩陣 $H$ 是一個 $n \times n$ 的對稱矩陣，其元素為二階偏導數：
   $$H_{ij} = \frac{\partial^2 f}{\partial x_i \partial x_j}$$

## 視覺化說明
![Hessian Matrix Concept](../svg/hessian_explanation.svg)

如圖所示，當梯度為零（達到臨界點）時，Hessian 矩陣的正負定性決定了該點是極小值、極大值還是鞍點：
* $H$ 為正定 (Positive definite, 所有特徵值 > 0)：局部極小值。
* $H$ 為負定 (Negative definite, 所有特徵值 < 0)：局部極大值。
* $H$ 不定 (Indefinite)：鞍點。

## 為什麼需要二階資訊？
在機器學習或量化模型中，一階優化（如梯度下降）僅知道「方向」，而二階優化（如牛頓法）利用 Hessian 矩陣知道「曲率」，能夠更聰明地調整步長，從而在更少的迭代次數內收斂到極小值。

---
[返回原文章節：TurboQuant Translation](../chapters/03-turboquant-translation.md)
