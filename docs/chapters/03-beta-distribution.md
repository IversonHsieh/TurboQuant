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

**Beta Distribution（Beta 分佈）** 是一種連續機率分佈，定義在區間 $[0, 1]$ 上（TurboQuant 中定義在 $[-1, 1]$），由形狀參數 $\alpha > 0$ 和 $\beta > 0$ 控制。

### 2.1 機率密度函數（PDF）

$$
f(x; \alpha, \beta) = \frac{1}{B(\alpha, \beta)} x^{\alpha-1} (1-x)^{\beta-1}, \quad x \in [0, 1]
$$

其中歸一化常數 $B(\alpha, \beta)$ 為 Beta 函數：

$$
B(\alpha, \beta) = \int_0^1 t^{\alpha-1} (1-t)^{\beta-1} dt = \frac{\Gamma(\alpha)\Gamma(\beta)}{\Gamma(\alpha+\beta)}
$$

這裡 $\Gamma(\cdot)$ 是 Gamma 函數。

### 2.2 基本統計特性

| 特性 | 公式 |
|:----:|:----:|
| **均值（Mean）** | $\displaystyle \mu = \frac{\alpha}{\alpha + \beta}$ |
| **變異數（Variance）** | $\displaystyle \sigma^2 = \frac{\alpha\beta}{(\alpha+\beta)^2(\alpha+\beta+1)}$ |
| **眾數（Mode）** | $\displaystyle \frac{\alpha-1}{\alpha+\beta-2}$ （當 $\alpha, \beta > 1$） |
| **偏度（Skewness）** | $\displaystyle \frac{2(\beta-\alpha)\sqrt{\alpha+\beta+1}}{(\alpha+\beta+2)\sqrt{\alpha\beta}}$ |

---

## 3. Beta Distribution 在 TurboQuant 中的應用

### 3.1 核心思想：隨機旋轉後的座標分佈

TurboQuant 的核心是對輸入向量進行**隨機旋轉**。關鍵觀察是：

> **引理 1**（超球面上隨機點的座標分佈）。對於任何正整數 $d$，如果 $\mathbf{x}\in\mathbb{S}^{d-1}$ 是在單位超球面上均勻分佈的隨機變量，那麼對於任何 $j\in[d]$，座標 $\mathbf{x}_j$ 遵循以下 Beta 分佈：

$$
\mathbf{x}_j \sim f_X(x) := \frac{\Gamma(d/2)}{\sqrt{\pi}\cdot\Gamma((d-1)/2)}(1-x^2)^{(d-3)/2}, \quad x \in [-1, 1]
$$

### 3.2 為什麼是 Beta Distribution？——直觀解釋

1. **幾何解釋**：考慮一個 $d$ 維單位超球面上的隨機點，觀察其某個座標，實際上是在計算該點在該座標軸上的投影。

2. **面積比例**：機率密度 $f_X(x)$ 等於：
   - 分子：$(d-1)$ 維中半徑為 $\sqrt{1-x^2}$ 的球體表面積
   - 分母：$d$ 維中單位超球體的表面積

3. **高維收斂**：當維度 $d$ 增加時，Beta 分佈收斂到常態分佈：

$$
f_X(\cdot) \to \mathcal{N}(0, 1/d) \quad \text{當 } d \to \infty
$$

### 3.3 TurboQuant 中的具體應用流程

在 TurboQuant 的 MSE 優化量化器中：

1. **隨機旋轉**：輸入向量 $\mathbf{x}$ 被乘以隨機旋轉矩陣 $\mathbf{\Pi}$
2. **座標分佈**：旋轉後的每個座標 $\mathbf{y}_j = (\mathbf{\Pi}\mathbf{x})_j$ 服從上述 Beta 分佈
3. **最佳量化**：利用這個已知的分佈，可以為每個座標設計最佳的 Lloyd-Max 量化器

這使得 TurboQuant 能夠：
- ✅ 避免對輸入數據做任何假設（data-oblivious）
- ✅ 在所有位元寬度上達到接近最佳的失真率
- ✅ 高效地進行線上量化

---

## 4. 維度實例：從低維到高維

### 4.1 低維度 ($d=3$)：均勻分佈

$$
f_X(x) = \frac{\Gamma(3/2)}{\sqrt{\pi}\cdot\Gamma(1)}(1-x^2)^{0} = \frac{1}{2}, \quad x \in [-1, 1]
$$

這是一個**均勻分佈**——在 3 維超球面上，每個座標值出現的機率相等。

### 4.2 中等維度 ($d=5$)：拋物線型分佈

$$
f_X(x) = \frac{\Gamma(5/2)}{\sqrt{\pi}\cdot\Gamma(2)}(1-x^2)^{1} = \frac{3}{4}(1-x^2), \quad x \in [-1, 1]
$$

這是一個**拋物線型分佈**，在 $x=0$ 處有最大值——座標值開始傾向接近 0。

### 4.3 高維度 ($d=100$)：近似常態分佈

$$
f_X(x) \approx \mathcal{N}(0, 1/100) = \mathcal{N}(0, 0.01)
$$

在高維度下，隨機旋轉後的座標值**幾乎總是接近 0**——這就是**測度集中（concentration of measure）**現象。

---

## 5. Beta Distribution 與常態分佈的關係

### 5.1 測度集中與中心極限定理

在高維度下，Beta 分佈收斂到常態分佈的現象是**測度集中**和**中心極限定理**的結果。

### 5.2 直觀理解：高維超球面的「赤道集中」

想像一個高維超球面：
- 🌐 大部分**表面積**集中在「赤道」附近
- 🎯 隨機選擇一個點時，其座標值**很可能接近 0**
- 📈 維度越高，集中效應越強

這就是 TurboQuant 在高維度下表現優異的根本原因。

---

## 6. 總結

| 特性 | 說明 |
|:----:|:----:|
| **定義域** | $[0, 1]$ 或 $[-1, 1]$（TurboQuant 使用後者） |
| **參數** | $\alpha, \beta > 0$ 控制形狀 |
| **靈活性** | 可呈現 U 型、均勻、偏態、鐘型等多種形狀 |
| **TurboQuant 角色** | 描述隨機旋轉後座標的分佈 |
| **高維特性** | 收斂到 $\mathcal{N}(0, 1/d)$ |
| **應用價值** | 使最佳純量量化器設計成為可能 |

---

## 參考資源

- **維基百科：** [Beta distribution](https://en.wikipedia.org/wiki/Beta_distribution)
- **原始論文：** [TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate](https://arxiv.org/abs/2504.19874)
- **相關文件：**
  - [向量量化解釋](03-vector-quantization-explanation.md)
  - [MSE 解釋](03-mse-explanation.md)
  - [內積失真解釋](03-inner-product-distortion.md)

---

*最後更新：2026-05-18*
*作者：TurboQuant Deep Dive Project*
