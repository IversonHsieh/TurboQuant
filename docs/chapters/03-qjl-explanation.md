# Quantized Johnson-Lindenstrauss (QJL) 詳解

[返回 TurboQuant 論文翻譯 (原文/中譯)](03-turboquant-translation.md#L89)

---

> [回到 QJL 理論基礎章節](02-6-qjl-analysis.md)

---

> [回到 QJL 相關章節理論背景](02-6-qjl-analysis.md)

---

## 什麼是 Quantized Johnson-Lindenstrauss (QJL)?

Quantized Johnson-Lindenstrauss (QJL) 是一種結合「隨機投影」與「極低位元量化」的高維資料壓縮技術。其核心目標是：

- 將高維向量投影到低維空間，
- 並以極低的位元（如 1-bit, 2-bit）儲存每個投影後的座標，
- 同時最大程度保留原始向量間的距離或內積結構。

QJL 是 Johnson-Lindenstrauss (JL) Lemma 的量化版本。JL Lemma 保證：經過隨機投影後，任意兩點的距離幾乎不變。QJL 則進一步將投影結果量化，極大壓縮資料體積，並以理論方法控制失真。

---

## QJL 的理論基礎

- **JL Lemma**：給定 $N$ 個點，存在一個隨機投影 $A$，將 $d$ 維向量 $x \in \mathbb{R}^d$ 投影到 $k = O(\log N / \epsilon^2)$ 維，使得所有點對 $(x, y)$ 有：
  $$
  (1-\epsilon)\|x-y\|^2 \leq \|A x - A y\|^2 \leq (1+\epsilon)\|x-y\|^2
  $$
- **QJL**：在投影後，對每個座標進行 $b$ 位元量化（$b=1$ 為最極端），例如：
  $$
  q(z) = \operatorname{sign}(z) \in \{-1, +1\}
  $$
  或更高位元的均勻/非均勻量化。

---

## QJL 在 TurboQuant 的角色

TurboQuant 兩階段量化流程：
1. **MSE 最佳量化**：先將高維向量隨機旋轉，並對每個座標做最佳 Lloyd-Max 量化，最小化均方誤差（MSE）。
2. **QJL 變換**：對殘差向量（原始向量減去量化後的重建向量）再做一次 1-bit QJL 量化，確保內積估計無偏且低失真。

這樣設計可同時達到最佳 MSE 失真與最佳內積失真。

---

## 實例說明

假設有兩個 4 維向量 $x = [1, 2, 3, 4]$，$y = [2, 1, 4, 3]$。

1. **隨機旋轉**：先將 $x, y$ 乘上一個隨機正交矩陣 $R$，得到 $x', y'$。
2. **Lloyd-Max 量化**：對 $x', y'$ 每個座標做最佳量化，得到 $\hat{x}, \hat{y}$。
3. **計算殘差**：$r_x = x' - \hat{x}$，$r_y = y' - \hat{y}$。
4. **QJL 1-bit 量化**：對 $r_x, r_y$ 每個座標取 sign，得到 $q_x, q_y$。
5. **重建與內積估計**：
   - 估計 $x, y$ 內積時，合併 $\hat{x}, q_x$ 與 $\hat{y}, q_y$，可得到無偏且低失真的估計。

---

## 視覺化流程圖

![QJL 流程圖](../svg/qjl_flowchart.svg)

> 若尚未有 `qjl_flowchart.svg`，請於 docs/svg/ 製作一張：
> - 展示「原始向量 → 隨機旋轉 → Lloyd-Max 量化 → 殘差 → QJL 1-bit 量化 → 壓縮結果」的流程。

---

## 延伸閱讀

- [2.6 QJL (Quantized Johnson-Lindenstrauss) 解析](02-6-qjl-analysis.md)
- [TurboQuant 論文翻譯 (QJL 相關段落)](03-turboquant-translation.md#L89)

---

[回到 03-turboquant-translation.md QJL 相關段落](03-turboquant-translation.md#L89)
