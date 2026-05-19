# Beta Distribution (Beta 分佈) 詳細解析

[🏠 返回目錄](../index.md) | [返回 TurboQuant 論文翻譯](03-turboquant-translation.md)

> **相關文件：** 本文是針對 [`03-turboquant-translation.md`](03-turboquant-translation.md) 中提到的 Beta distribution 概念的補充說明。

---

## 1. 一目瞭然：Beta 分佈的各種形態

Beta 分佈由兩個形狀參數 $\alpha$ 和 $\beta$ 控制，可以呈現多種截然不同的形態。下圖直觀展示了不同參數組合下的機率密度函數：

![Beta Distribution 各種參數形狀](../svg/beta_distribution.svg)

**圖表解讀：**
- **左上圖**：U 型 $(0.5, 0.5)$、均勻 $(1, 1)$、右偏 $(2, 5)$、左偏 $(5, 2)$ 分佈
- **右上圖**：對稱鐘型 $(2, 2)$、對稱尖峰 $(5, 5)$、J 型 $(0.5, 1)$、反 J 型 $(1, 0.5)$ 分佈
- **左下圖**：TurboQuant 中使用的 Beta 分佈在不同維度下的變化（維度越高越集中）
- **右下圖**：均值和變異數隨參數變化的趨勢

### 1.1 參數組合與形狀對照表

| 參數 $(\alpha, \beta)$ | 形狀描述 | 特徵 | 應用場景 |
|:----------------------:|:--------:|:----:|:--------:|
| $(0.5, 0.5)$ | **U 型分佈** | 兩端高、中間低 | 雙峰分佈 |
| $(1, 1)$ | **均勻分佈** | 完全平坦 | 完全隨機 |
| $(2, 5)$ | **右偏分佈** | 偏向 0 | 大部分值接近 0 |
| $(5, 2)$ | **左偏分佈** | 偏向 1 | 大部分值接近 1 |
| $(2, 2)$ | **對稱鐘型** | 類似常態 | 溫和集中 |
| $(5, 5)$ | **對稱尖峰** | 高度集中 | 高度集中在 0.5 |
| $(0.5, 1)$ | **J 型分佈** | 單調遞減 | 極端值在 0 |
| $(1, 0.5)$ | **反 J 型分佈** | 單調遞增 | 極端值在 1 |

---

## 2. Beta Distribution 的數學定義

**Beta Distribution（Beta 分佈）** 是一種連續機率分佈，定義在區間 $[0, 1]$ 上（TurboQuant 中使用的是定義在 $[-1, 1]$ 上的變體，見第 3 節），由形狀參數 $\alpha > 0$ 和 $\beta > 0$ 控制。

### 2.1 機率密度函數（PDF）

$$
f(x; \alpha, \beta) = \frac{1}{B(\alpha, \beta)} x^{\alpha-1} (1-x)^{\beta-1}, \quad x \in [0, 1]
$$

其中歸一化常數 $B(\alpha, \beta)$ 為 Beta 函數：

$$
B(\alpha, \beta) = \int_0^1 t^{\alpha-1} (1-t)^{\beta-1} dt = \frac{\Gamma(\alpha)\Gamma(\beta)}{\Gamma(\alpha+\beta)}
$$

這裡 $\Gamma(\cdot)$ 是 Gamma 函數（階乘的推廣，$\Gamma(n) = (n-1)!$ 當 $n$ 為正整數時）。

### 2.2 基本統計特性

| 特性 | 公式 |
|:----:|:----:|
| **均值（Mean）** | $\displaystyle \mu = \frac{\alpha}{\alpha + \beta}$ |
| **變異數（Variance）** | $\displaystyle \sigma^2 = \frac{\alpha\beta}{(\alpha+\beta)^2(\alpha+\beta+1)}$ |
| **眾數（Mode）** | $\displaystyle \frac{\alpha-1}{\alpha+\beta-2}$ （當 $\alpha, \beta > 1$） |
| **偏度（Skewness）** | $\displaystyle \frac{2(\beta-\alpha)\sqrt{\alpha+\beta+1}}{(\alpha+\beta+2)\sqrt{\alpha\beta}}$ |

### 2.3 為什麼 Beta 分佈這麼靈活？

Beta 分佈的靈活性來自於 $x^{\alpha-1}(1-x)^{\beta-1}$ 這個核心結構：
- $x^{\alpha-1}$ 控制**靠近 1** 的行為：$\alpha$ 越大，越往 1 集中
- $(1-x)^{\beta-1}$ 控制**靠近 0** 的行為：$\beta$ 越大，越往 0 集中
- 當 $\alpha = \beta$ 時，分佈關於 $x = 0.5$ 對稱

這種「兩端可控」的特性使得 Beta 分佈能模擬從均勻到極端集中的各種形態。

---

## 3. TurboQuant 中的 Beta 分佈：從標準 Beta 到超球面座標

### 3.1 標準 Beta 分佈 vs. TurboQuant 的 Beta 分佈

TurboQuant 論文中使用的 Beta 分佈**不是**標準的 $[0, 1]$ 區間 Beta 分佈，而是一個**對稱的、縮放到 $[-1, 1]$ 區間**的變體。這兩者的關係如下：

**標準 Beta 分佈**（定義在 $[0, 1]$）：

$$f(x; \alpha, \beta) = \frac{1}{B(\alpha, \beta)} x^{\alpha-1} (1-x)^{\beta-1}$$

**TurboQuant 的 Beta 分佈**（定義在 $[-1, 1]$）：

$$f_X(x) = \frac{\Gamma(d/2)}{\sqrt{\pi}\cdot\Gamma((d-1)/2)}(1-x^2)^{(d-3)/2}, \quad x \in [-1, 1]$$

### 3.2 兩者之間的轉換

TurboQuant 的公式可以從標準 Beta 分佈推導出來，步驟如下：

**步驟 1：對稱性。** 超球面上的座標分佈是關於 0 對稱的（正負值出現機率相同），所以 $\alpha = \beta$。

**步驟 2：變數替換。** 令 $u = \frac{x+1}{2}$，將 $x \in [-1, 1]$ 映射到 $u \in [0, 1]$。反過來，$x = 2u - 1$，$1 - x^2 = 1 - (2u-1)^2 = 4u(1-u)$。

**步驟 3：代入。** TurboQuant 的公式對應於標準 Beta 分佈中 $\alpha = \beta = \frac{d-1}{2}$ 的情況：

$$f_X(x) = \frac{1}{2} \cdot \text{Beta}\!\left(\frac{d-1}{2}, \frac{d-1}{2}\right)\!\left(\frac{x+1}{2}\right)$$

其中 $\frac{1}{2}$ 來自於變數替換的 Jacobian（$dx = 2\,du$），而 $\alpha = \beta = \frac{d-1}{2}$ 確保了對稱性。

**關鍵觀察：** 維度 $d$ 直接決定了 Beta 分佈的形狀參數 $\alpha = \beta = \frac{d-1}{2}$。維度越高，參數越大，分佈越集中。

### 3.3 核心思想：隨機旋轉後的座標分佈

TurboQuant 的核心是對輸入向量進行**隨機旋轉**。關鍵觀察是：

> **引理 1**（超球面上隨機點的座標分佈）。對於任何正整數 $d$，如果 $\mathbf{x}\in\mathbb{S}^{d-1}$ 是在單位超球面上均勻分佈的隨機變量，那麼對於任何 $j\in[d]$，座標 $\mathbf{x}_j$ 遵循以下（縮放/平移的）Beta 分佈：

$$
\mathbf{x}_j \sim f_X(x) := \frac{\Gamma(d/2)}{\sqrt{\pi}\cdot\Gamma((d-1)/2)}(1-x^2)^{(d-3)/2}, \quad x \in [-1, 1]
$$

### 3.4 為什麼超球面上的座標遵循 Beta 分佈？——逐步推導

這是理解 TurboQuant 的關鍵數學。以下用幾何直覺逐步推導：

**問題設定：** 在 $d$ 維單位超球面 $\mathbb{S}^{d-1}$ 上隨機取一個點 $\mathbf{x} = (x_1, x_2, \ldots, x_d)$，問某個座標 $x_j$ 的機率分佈是什麼？

**步驟 1：約束條件。** 因為 $\mathbf{x} \in \mathbb{S}^{d-1}$，所以 $\|\mathbf{x}\|_2 = 1$，即：

$$x_1^2 + x_2^2 + \cdots + x_d^2 = 1$$

**步驟 2：固定一個座標。** 如果我們固定 $x_j = x$，那麼其餘 $d-1$ 個座標必須滿足：

$$x_1^2 + \cdots + x_{j-1}^2 + x_{j+1}^2 + \cdots + x_d^2 = 1 - x^2$$

這意味著其餘座標落在半徑為 $\sqrt{1-x^2}$ 的 $(d-2)$ 維超球面 $\mathbb{S}^{d-2}(\sqrt{1-x^2})$ 上。

**步驟 3：截面積計算。** 座標 $x_j = x$ 的機率密度正比於「在 $x_j = x$ 處，超球面的截面積」。這個截面是一個 $(d-2)$ 維超球面，其「面積」為：

$$\text{Area}(\mathbb{S}^{d-2}(\sqrt{1-x^2})) = \frac{2\pi^{(d-1)/2}}{\Gamma((d-1)/2)} \cdot (\sqrt{1-x^2})^{d-2} = \frac{2\pi^{(d-1)/2}}{\Gamma((d-1)/2)} \cdot (1-x^2)^{(d-2)/2}$$

**步驟 4：歸一化。** 整個超球面 $\mathbb{S}^{d-1}$ 的面積為：

$$\text{Area}(\mathbb{S}^{d-1}) = \frac{2\pi^{d/2}}{\Gamma(d/2)}$$

但還需要考慮一個幾何因子 $1/\sqrt{1-x^2}$（因為截面是傾斜的，需要投影校正），所以：

$$f_X(x) = \frac{\text{Area}(\mathbb{S}^{d-2}(\sqrt{1-x^2}))}{\text{Area}(\mathbb{S}^{d-1})} \cdot \frac{1}{\sqrt{1-x^2}}$$

$$= \frac{\frac{2\pi^{(d-1)/2}}{\Gamma((d-1)/2)} \cdot (1-x^2)^{(d-2)/2}}{\frac{2\pi^{d/2}}{\Gamma(d/2)}} \cdot \frac{1}{\sqrt{1-x^2}}$$

$$= \frac{\Gamma(d/2)}{\sqrt{\pi}\cdot\Gamma((d-1)/2)} \cdot (1-x^2)^{(d-2)/2} \cdot (1-x^2)^{-1/2}$$

$$= \frac{\Gamma(d/2)}{\sqrt{\pi}\cdot\Gamma((d-1)/2)} \cdot (1-x^2)^{(d-3)/2}$$

這就是論文中的公式！$\blacksquare$

### 3.5 直覺解釋：為什麼高維度時座標集中在 0 附近？

公式中的關鍵項是 $(1-x^2)^{(d-3)/2}$。當 $d$ 很大時，指數 $(d-3)/2$ 很大，這意味著：

- 當 $x$ 接近 0 時：$(1-x^2)^{(d-3)/2} \approx 1$，機率密度高
- 當 $x$ 接近 $\pm 1$ 時：$(1-x^2)^{(d-3)/2} \approx 0$，機率密度極低

**幾何直覺**：高維超球面的表面積集中在「赤道」附近。想像一個 $d$ 維球，絕大多數的表面積都在 $x_j \approx 0$ 的區域，只有極少部分在「極點」（$x_j \approx \pm 1$）附近。這就是**測度集中（concentration of measure）**現象。

### 3.6 TurboQuant 中的具體應用流程

在 TurboQuant 的 MSE 優化量化器中：

1. **隨機旋轉**：輸入向量 $\mathbf{x}$ 被乘以隨機旋轉矩陣 $\mathbf{\Pi}$
2. **座標分佈已知**：旋轉後的每個座標 $\mathbf{y}_j = (\mathbf{\Pi}\mathbf{x})_j$ 服從上述 Beta 分佈
3. **最佳量化**：利用這個已知的分佈，可以為每個座標設計最佳的 Lloyd-Max 量化器（即求解一維 k-means 問題）

這使得 TurboQuant 能夠：
- ✅ 避免對輸入數據做任何假設（data-oblivious）
- ✅ 在所有位元寬度上達到接近最佳的失真率
- ✅ 高效地進行線上量化

---

## 4. 維度實例：從低維到高維

### 4.1 低維度 ($d=3$)：均勻分佈

$$
f_X(x) = \frac{\Gamma(3/2)}{\sqrt{\pi}\cdot\Gamma(1)}(1-x^2)^{0} = \frac{\sqrt{\pi}/2}{\sqrt{\pi}\cdot 1} \cdot 1 = \frac{1}{2}, \quad x \in [-1, 1]
$$

這是一個**均勻分佈**——在 3 維超球面（也就是 2D 球面，即普通的球面）上，每個座標值出現的機率相等。

**直覺**：在普通的球面上隨機取點，其 $x$ 座標在 $[-1, 1]$ 上均勻分佈。這是因為 $(d-3)/2 = 0$，指數項消失了。

### 4.2 中等維度 ($d=5$)：拋物線型分佈

$$
f_X(x) = \frac{\Gamma(5/2)}{\sqrt{\pi}\cdot\Gamma(2)}(1-x^2)^{1} = \frac{3\sqrt{\pi}/4}{\sqrt{\pi}\cdot 1} \cdot (1-x^2) = \frac{3}{4}(1-x^2), \quad x \in [-1, 1]
$$

這是一個**拋物線型分佈**，在 $x=0$ 處有最大值 $3/4$——座標值開始傾向接近 0。

**驗證**：$\int_{-1}^{1} \frac{3}{4}(1-x^2)\,dx = \frac{3}{4} \cdot \frac{4}{3} = 1$ ✓

### 4.3 高維度 ($d=100$)：近似常態分佈

$$
f_X(x) \approx \mathcal{N}(0, 1/100) = \mathcal{N}(0, 0.01)
$$

在高維度下，隨機旋轉後的座標值**幾乎總是接近 0**——這就是**測度集中（concentration of measure）**現象。

**數值感受**：當 $d=100$ 時，標準差為 $\sigma = 1/\sqrt{d} = 0.1$。這意味著座標值 $x_j$ 有 99.7% 的機率落在 $[-0.3, 0.3]$ 之內，而這個區間只佔 $[-1, 1]$ 總長度的 30%。

### 4.4 極高維度 ($d=4096$)：深度學習的實際場景

在 LLM 的 KV cache 量化中，向量維度 $d$ 可能是 4096 或更高。此時：

$$
\sigma = \frac{1}{\sqrt{d}} = \frac{1}{\sqrt{4096}} = \frac{1}{64} \approx 0.0156
$$

座標值 $x_j$ 有 99.7% 的機率落在 $[-0.047, 0.047]$ 之內——幾乎所有值都極度集中在 0 附近。這使得量化非常高效：大部分位元可以用來編碼接近 0 的值，而不用浪費在極少出現的大值上。

---

## 5. Beta 分佈與常態分佈的關係

### 5.1 數學推導：為什麼高維度時收斂到常態分佈？

TurboQuant 的 Beta 分佈公式中，令 $x = y/\sqrt{d}$，當 $d \to \infty$ 時：

$$
(1-x^2)^{(d-3)/2} = \left(1-\frac{y^2}{d}\right)^{(d-3)/2} \approx e^{-y^2/2}
$$

這是因為 $\lim_{n\to\infty}(1-a/n)^n = e^{-a}$。同時，歸一化常數 $\frac{\Gamma(d/2)}{\sqrt{\pi}\cdot\Gamma((d-1)/2)}$ 在高維度時近似 $\sqrt{d/(2\pi)}$。

因此：

$$
f_X(x) \approx \sqrt{\frac{d}{2\pi}} \cdot e^{-dx^2/2} = \frac{1}{\sqrt{2\pi/d}} \exp\left(-\frac{x^2}{2/d}\right) = \mathcal{N}(0, 1/d)
$$

### 5.2 測度集中與中心極限定理

在高維度下，Beta 分佈收斂到常態分佈的現象可以從兩個角度理解：

1. **測度集中（Concentration of Measure）**：高維超球面的表面積集中在赤道附近，所以隨機點的座標值幾乎必然接近 0。

2. **中心極限定理**：因為 $x_1^2 + x_2^2 + \cdots + x_d^2 = 1$，每個 $x_j$ 可以看作是 $d$ 個「競爭」同一個總和的分量。當 $d$ 很大時，每個分量的貢獻都很小，類似於獨立同分佈的隨機變量之和除以 $d$，因此趨向常態分佈。

### 5.3 直觀理解：高維超球面的「赤道集中」

想像一個高維超球面：
- 🌐 大部分**表面積**集中在「赤道」附近
- 🎯 隨機選擇一個點時，其座標值**很可能接近 0**
- 📈 維度越高，集中效應越強

這就是 TurboQuant 在高維度下表現優異的根本原因：座標值集中在 0 附近，使得純量量化器可以精確地量化大部分值。

---

## 6. 從 Beta 分佈到最佳量化器：TurboQuant 的核心邏輯

### 6.1 為什麼知道分佈就能設計最佳量化器？

量化問題本質上是：給定一個機率分佈，如何選擇 $2^b$ 個量化質心（centroids），使得期望失真最小？

這就是一維的 **k-means 問題**（也稱 Lloyd-Max 量化器設計）：

$$
\mathcal{C}(f_X, b) := \min_{-1 \leq c_1 \leq c_2 \leq \ldots \leq c_{2^b} \leq 1} \sum_{i=1}^{2^b} \int_{\frac{c_{i-1}+c_i}{2}}^{\frac{c_i+c_{i+1}}{2}} |x - c_i|^2 \cdot f_X(x)\,dx
$$

**關鍵**：因為隨機旋轉使得每個座標的分佈 $f_X(x)$ 是已知的 Beta 分佈，我們可以**預先計算**最佳質心，而不需要看到任何數據！

### 6.2 不同位元寬度下的最佳質心

在中等高維度 $d$ 下，$f_X(x)$ 近似 $\mathcal{N}(0, 1/d)$，最佳量化質心為：

| 位元寬度 $b$ | 最佳質心 | 說明 |
|:---:|:---:|:---:|
| $b=1$ | $\{\pm\sqrt{2/(\pi d)}\}$ | 2 個質心，對稱分佈在 0 兩側 |
| $b=2$ | $\{\pm\frac{0.453}{\sqrt{d}}, \pm\frac{1.51}{\sqrt{d}}\}$ | 4 個質心，內外兩層 |

注意所有質心都與 $1/\sqrt{d}$ 成比例——這正是 Beta 分佈收斂到 $\mathcal{N}(0, 1/d)$ 的直接結果。

### 6.3 TurboQuant 的完整流程

```
輸入：向量 x ∈ ℝᵈ（可能 ||x||₂ ≠ 1）
  │
  ├─ ① 分離 norm：存 ||x||₂，取 x̂ = x/||x||₂ → x̂ ∈ S^{d-1}
  │
  ├─ ② 隨機旋轉：y = Π · x̂ → y 在 S^{d-1} 上均勻分佈
  │
  ├─ ③ 每個座標 yⱼ ~ Beta 分佈（已知、可預計算）
  │
  ├─ ④ 對每個座標獨立做最佳純量量化（1D k-means）
  │
  ├─ ⑤ 反旋轉：Πᵀ · 量化後的 y → 重建 x̂
  │
  └─ ⑥ 乘回 norm：重建的 x̂ × ||x||₂ → 最終重建向量
```

Beta 分佈是步驟 ③ 的數學基礎，它讓步驟  ④ 的最佳量化器設計成為可能。

---

## 7. 總結

| 特性 | 說明 |
|:----:|:----:|
| **標準定義域** | $[0, 1]$（標準 Beta 分佈） |
| **TurboQuant 定義域** | $[-1, 1]$（對稱 Beta 分佈的縮放版本） |
| **參數** | $\alpha = \beta = \frac{d-1}{2}$（由維度 $d$ 決定） |
| **靈活性** | 可呈現 U 型、均勻、偏態、鐘型等多種形狀 |
| **TurboQuant 角色** | 描述隨機旋轉後座標的分佈 |
| **高維特性** | 收斂到 $\mathcal{N}(0, 1/d)$ |
| **核心價值** | 使 data-oblivious 的最佳純量量化器設計成為可能 |
| **幾何直覺** | 高維超球面的表面積集中在赤道附近 |

---

## 參考資源

- **維基百科：** [Beta distribution](https://en.wikipedia.org/wiki/Beta_distribution)
- **原始論文：** [TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate](https://arxiv.org/abs/2504.19874)
- **相關文件：**
  - [向量量化解釋](03-vector-quantization-explanation.md)
  - [MSE 解釋](03-mse-explanation.md)
  - [內積失真](03-inner-product-distortion.md)
  - [L2 範數解釋](03-l2-norm-explanation.md)
  - [TurboQuant 論文翻譯](03-turboquant-translation.md)

---

*最後更新：2026-05-19*
*作者：TurboQuant Deep Dive Project*
