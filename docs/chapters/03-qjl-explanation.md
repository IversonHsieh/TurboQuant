# Quantized Johnson-Lindenstrauss (QJL) 詳解

[🏠 返回目錄](../index.md) | [返回 TurboQuant 論文翻譯 (原文/中譯)](03-turboquant-translation.md#L89)

---

> [回到 QJL 理論基礎章節](02-6-qjl-analysis.md)

---

## 目錄

- [什麼是 QJL？](#什麼是-qjl)
- [理論基礎：從 JL Lemma 到 QJL](#理論基礎從-jl-lemma-到-qjl)
- [QJL 的形式化定義](#qjl-的形式化定義)
- [QJL 的性能保證](#qjl-的性能保證)
- [性能保證的證明](#性能保證的證明)
- [MSE 最佳量化器的內積偏差問題](#mse-最佳量化器的內積偏差問題)
- [QJL 在 TurboQuant 中的角色：兩階段方案](#qjl-在-turboquant-中的角色兩階段方案)
- [TurboQuant_prod 的完整演算法](#turboquantprod-的完整演算法)
- [TurboQuant_prod 的理論保證](#turboquantprod-的理論保證)
- [內積失真界限的推導](#內積失真界限的推導)
- [數值實例詳解](#數值實例詳解)
- [視覺化流程圖](#視覺化流程圖)
- [關鍵洞察與直覺總結](#關鍵洞察與直覺總結)
- [延伸閱讀](#延伸閱讀)

---

<a id="什麼是-qjl"></a>

## 什麼是 Quantized Johnson-Lindenstrauss (QJL)?

**Quantized Johnson-Lindenstrauss (QJL)** 是一種結合「隨機投影」與「極低位元量化」的高維資料壓縮技術，由 Zandieh 等人於 [62] 中提出。其核心目標是：

1. 將高維向量透過隨機矩陣投影後，**僅保留每個座標的符號（sign）**——即 1-bit 量化；
2. 在反量化（dequantization）時，利用投影矩陣的轉置與一個縮放因子重建向量；
3. **保證重建後的內積估計是無偏的（unbiased）**，且失真可控。

QJL 與傳統 JL Lemma 的隨機投影有根本性的差異：

| 特性 | 傳統 JL 隨機投影 | QJL |
|------|------------------|-----|
| 投影後儲存精度 | 浮點數（32-bit 或 16-bit） | 1-bit（僅 sign） |
| 內積估計無偏性 | ✓（自然無偏） | ✓（透過縮放因子保證） |
| 儲存成本 | $O(d \times k \times \text{float})$ | $O(d)$ bits |
| 計算核心 | 矩陣乘法 | sign 運算 + 矩陣乘法 |
| 適用場景 | 降維、近似距離保持 | 極低位元內積量化、殘差編碼 |

QJL 的關鍵創新在於：**它證明了即使將投影結果極端量化到只剩 1 bit，只要設計得當，仍然可以保持內積估計的無偏性與低失真**。這使得 QJL 成為 TurboQuant 第二階段——殘差量化——的理想選擇。

---

<a id="理論基礎從-jl-lemma-到-qjl"></a>

## 理論基礎：從 JL Lemma 到 QJL

### Johnson-Lindenstrauss Lemma 回顧

**Johnson-Lindenstrauss (JL) Lemma** 是高維幾何中的經典結果：給定 $N$ 個點，存在一個隨機投影 $A \in \mathbb{R}^{k \times d}$，將 $d$ 維向量 $x \in \mathbb{R}^d$ 投影到 $k = O(\log N / \epsilon^2)$ 維，使得對所有點對 $(x, y)$ 有：

$$
(1-\epsilon)\|x-y\|^2 \leq \|A x - A y\|^2 \leq (1+\epsilon)\|x-y\|^2
$$

JL Lemma 的核心洞見是：**隨機投影可以近乎完美地保持高維點對之間的距離**，且目標維度僅需對數依賴於點的數量。

### 從距離保持到內積保持

在 TurboQuant 的應用場景（KV cache 量化、最近鄰搜尋）中，我們關心的不僅是距離，更是**內積** $\langle y, x \rangle$。利用極化恆等式（polarization identity），距離保持可以推導出內積保持：

$$
\langle y, x \rangle = \frac{1}{2}\left(\|x\|^2 + \|y\|^2 - \|x - y\|^2\right)
$$

因此，JL Lemma 的距離保證隱含了內積的近似保持。

### QJL 的核心思想：量化投影

傳統 JL 投影的問題在於：投影後的座標仍然是浮點數，儲存成本高。QJL 的核心思想是：

> **如果我們對投影後的每個座標只保留其符號（sign），並在反量化時使用正確的縮放因子，內積估計仍然是無偏的。**

這個看似極端的量化策略之所以可行，是因為：

1. **sign 函數的期望值與原始值成正比**：對於高斯隨機投影的每一行 $\mathbf{s}_i$，$\mathbb{E}[\text{sign}(\mathbf{s}_i^\top x) \cdot \mathbf{s}_i^\top y]$ 與 $\langle y, x \rangle$ 存在確定的比例關係；
2. **縮放因子 $\sqrt{\pi/2d}$ 恰好補償了 sign 量化引入的系統性衰減**，使得整體估計無偏；
3. **多個獨立投影的平均**降低了變異數，且變異數以 $O(1/d)$ 的速率衰減。

---

<a id="qjl-的形式化定義"></a>

## QJL 的形式化定義

以下定義直接來自 TurboQuant 論文的 Definition 1（[論文原文](03-turboquant-translation.md#L512)）：

**定義 1（QJL）**：對於任何正整數 $d$，QJL 映射 $Q_{\text{qjl}}:\mathbb{R}^d \to \{-1,+1\}^d$ 定義為：

$$
Q_{\text{qjl}}(\mathbf{x}) := \text{sign}(\mathbf{S}\cdot\mathbf{x}) \quad \text{對於任何 } \mathbf{x}\in\mathbb{R}^d,
$$

其中：
- $\mathbf{S}\in\mathbb{R}^{d\times d}$ 是一個隨機矩陣，其元素從常態分佈 $\mathcal{N}(0,1)$ 中獨立同分佈（i.i.d.）採樣；
- $\text{sign}$ 函數逐元素（entry-wise）應用於其向量輸入，即 $\text{sign}(z) = +1$ 若 $z \geq 0$，否則 $\text{sign}(z) = -1$。

逆映射（反量化映射）$Q_{\text{qjl}}^{-1}:\{-1,+1\}^d \to \mathbb{R}^d$ 定義為：

$$
Q_{\text{qjl}}^{-1}(\mathbf{z}) := \sqrt{\frac{\pi}{2d}}\cdot\mathbf{S}^\top\cdot\mathbf{z} \quad \text{對於任何 } \mathbf{z}\in\{-1,+1\}^d.
$$

### 定義的逐步拆解

讓我們逐步理解這個定義的每個部分：

**步驟 1：隨機投影** $\mathbf{S} \cdot \mathbf{x}$

將輸入向量 $\mathbf{x} \in \mathbb{R}^d$ 乘以隨機矩陣 $\mathbf{S} \in \mathbb{R}^{d \times d}$，得到一個 $d$ 維投影向量。每一個投影座標 $\mathbf{s}_i^\top \mathbf{x}$（其中 $\mathbf{s}_i$ 是 $\mathbf{S}$ 的第 $i$ 行）是 $\mathbf{x}$ 與一個隨機方向的內積。

> 注意：QJL 的投影**不改變維度**（$d \to d$），這與傳統 JL 投影（$d \to k$, $k \ll d$）不同。QJL 的壓縮來自於量化而非降維。

**步驟 2：1-bit 量化** $\text{sign}(\mathbf{S} \cdot \mathbf{x})$

對投影後的每個座標取符號，得到一個 $d$ 維的 $\{-1, +1\}^d$ 向量。每個座標僅佔 1 bit，因此總儲存成本為 $d$ bits。

**步驟 3：反量化** $\sqrt{\frac{\pi}{2d}} \cdot \mathbf{S}^\top \cdot \mathbf{z}$

反量化分為兩步：
1. 將 sign 向量 $\mathbf{z}$ 乘以 $\mathbf{S}^\top$，相當於用隨機矩陣的列向量的加權組合來重建原始向量；
2. 乘以縮放因子 $\sqrt{\frac{\pi}{2d}}$，這個因子補償了 sign 量化引入的系統性幅度衰減。

### 為什麼縮放因子是 $\sqrt{\frac{\pi}{2d}}$？

這個縮放因子的推導基於以下觀察：對於一個均值為零的常態分佈隨機變量 $g \sim \mathcal{N}(0, \sigma^2)$，其絕對值的期望值為：

$$
\mathbb{E}[|g|] = \sigma \sqrt{\frac{2}{\pi}}
$$

在 QJL 中，$\mathbf{s}_i^\top \mathbf{x}$ 是一個均值為零、變異數為 $\|\mathbf{x}\|_2^2$ 的高斯隨機變量。sign 量化將其映射為 $\pm 1$，相當於丟失了幅度資訊。為了在期望意義上補償這個損失，我們需要乘以 $\mathbb{E}[|\mathbf{s}_i^\top \mathbf{x}|] / 1 = \|\mathbf{x}\|_2 \sqrt{2/\pi}$ 的倒數相關因子。經過對 $d$ 個獨立投影的平均，最終的縮放因子為 $\sqrt{\pi / (2d)}$。

---

<a id="qjl-的性能保證"></a>

## QJL 的性能保證

以下引理來自 TurboQuant 論文的 Lemma 4（[論文原文](03-turboquant-translation.md#L542)），是 QJL 最核心的理論結果：

**引理 4（性能保證：QJL）**：設 $Q_{\text{qjl}}$ 和 $Q_{\text{qjl}}^{-1}$ 根據定義 1 定義。對於任何向量 $\mathbf{x}\in\mathbb{S}^{d-1}$（單位超球面上的向量）和任何 $\mathbf{y}\in\mathbb{R}^d$，我們有以下結果：

- **無偏性（Unbiasedness）**：
$$
\mathbb{E}[\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{x}))\rangle] = \langle\mathbf{y},\mathbf{x}\rangle
$$

- **變異數界限（Variance Bound）**：
$$
\text{Var}(\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{x}))\rangle) \leq \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2
$$

### 這兩個保證意味著什麼？

**無偏性**意味著：如果我們多次獨立地執行 QJL（每次使用不同的隨機矩陣 $\mathbf{S}$），內積估計的平均值會精確收斂到真實內積 $\langle\mathbf{y},\mathbf{x}\rangle$。這對於最近鄰搜尋等應用至關重要——沒有系統性的偏差意味著不會持續地高估或低估某些向量的相似度。

**變異數界限**意味著：內積估計的誤差（以均方誤差衡量）至多為 $\frac{\pi}{2d} \cdot \|\mathbf{y}\|_2^2$。注意這個界限：
- 與維度 $d$ 成反比——**維度越高，QJL 的估計越精確**；
- 與查詢向量的範數 $\|\mathbf{y}\|_2^2$ 成正比——這是合理的，因為更大的查詢向量會放大誤差；
- **與輸入向量 $\mathbf{x}$ 無關**（除了透過單位範數假設）——這是一個最壞情況界限。

---

<a id="性能保證的證明"></a>

## 性能保證的證明

以下完整重現論文中引理 4 的證明（[論文原文](03-turboquant-translation.md#L564)），並加入詳細的直覺解釋。

### 無偏性的證明

無偏性直接來自 [62] 的引理 3.2。其核心思想是：對於高斯隨機向量 $\mathbf{s}_i$，$\text{sign}(\mathbf{s}_i^\top \mathbf{x})$ 與 $\mathbf{s}_i^\top \mathbf{y}$ 的乘積的期望值與 $\langle \mathbf{y}, \mathbf{x} \rangle$ 成正比，而縮放因子恰好補償了這個比例。

### 變異數界限的證明

設 $\mathbf{s}_1, \mathbf{s}_2, \ldots, \mathbf{s}_d$ 為隨機矩陣 $\mathbf{S}$ 的行向量。根據 QJL 的定義，內積估計可以展開為：

$$
\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{x}))\rangle = \frac{1}{d}\sum_{i\in[d]}\sqrt{\pi/2}\cdot\mathbf{s}_i^\top\mathbf{y}\cdot\text{sign}(\mathbf{s}_i^\top\mathbf{x}).
$$

由於 $\mathbf{s}_i$ 是 i.i.d. 的，上式實際上是 $d$ 個 i.i.d. 隨機樣本的平均值，其中每個樣本定義為：

$$
z_i := \sqrt{\pi/2}\cdot\mathbf{s}_i^\top\mathbf{y}\cdot\text{sign}(\mathbf{s}_i^\top\mathbf{x}), \quad i \in [d].
$$

**第一步：計算單個 $z_i$ 的變異數上界**

利用 [62] 中的事實 3.4：

$$
\text{Var}(z_i) = \sqrt{\pi/2}\cdot\text{Var}(\mathbf{s}_i^\top\mathbf{y}\cdot\text{sign}(\mathbf{s}_i^\top\mathbf{x})) \leq \sqrt{\pi/2}\cdot\mathbb{E}[(\mathbf{s}_i^\top\mathbf{y})^2] = \sqrt{\pi/2}\cdot\|\mathbf{y}\|_2^2, \tag{3}
$$

最後一個等式成立是因為 $\mathbf{s}_i^\top\mathbf{y}$ 是均值為零、變異數為 $\|\mathbf{y}\|_2^2$ 的高斯隨機變量。

> **直覺解釋**：$\text{sign}(\mathbf{s}_i^\top \mathbf{x})$ 只是一個 $\pm 1$ 的係數，它不會放大 $\mathbf{s}_i^\top \mathbf{y}$ 的變異數。最壞情況下，sign 與 $\mathbf{s}_i^\top \mathbf{y}$ 完全相關，此時變異數最大；但實際上 sign 的隨機性會部分抵消這種相關性。

**第二步：計算平均值的變異數**

$d$ 個 i.i.d. 隨機樣本 $z_1, z_2, \ldots, z_d$ 的平均值的變異數為：

$$
\text{Var}(\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{x}))\rangle) = \frac{1}{d^2}\sum_{i\in[d]}\text{Var}(z_i) \leq \frac{1}{d^2} \cdot d \cdot \sqrt{\pi/2} \cdot \|\mathbf{y}\|_2^2 = \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2.
$$

> **關鍵洞見**：變異數以 $O(1/d)$ 衰減，這是「多個獨立估計的平均」帶來的經典效應。這也解釋了為什麼 QJL 在高維度下特別有效——當 $d$ 很大時，$d$ 個獨立 sign 投影的平均幾乎確定地收斂到真實內積。 $\blacksquare$

---

<a id="mse-最佳量化器的內積偏差問題"></a>

## MSE 最佳量化器的內積偏差問題

在理解 QJL 為何是 TurboQuant 的關鍵組件之前，我們必須先理解一個核心問題：**MSE 最佳量化器在內積估計中是有偏的**。

### 偏差的來源

考慮 $\text{TurboQuant}_{\text{mse}}$ 在位元寬度 $b=1$ 的情況。對於足夠大的維度 $d$，解最佳化問題 (4) 得到的最佳碼本為 $\{\pm\sqrt{2/(\pi d)}\}$。因此：

- 量化映射：$Q_{\text{mse}}(\mathbf{x}) = \text{sign}(\mathbf{\Pi}\cdot\mathbf{x})$
- 反量化映射：$Q_{\text{mse}}^{-1}(\mathbf{z}) = \sqrt{\frac{2}{\pi d}}\cdot\mathbf{\Pi}^\top\cdot\mathbf{z}$

對於任意查詢向量 $\mathbf{y}$，內積估計的期望值為：

$$
\mathbb{E}[\langle\mathbf{y},Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))\rangle] = \sqrt{\frac{2}{\pi}}\cdot\langle\mathbf{y},\mathbf{x}\rangle \approx 0.798 \cdot \langle\mathbf{y},\mathbf{x}\rangle
$$

這意味著 **MSE 最佳量化器系統性地低估內積**，乘法偏差約為 $\sqrt{2/\pi} \approx 0.798$。

### 偏差為何重要？

在最近鄰搜尋等應用中，內積的系統性偏差會導致：

1. **排序錯誤**：如果不同向量的偏差程度不同（取決於其方向），則排序可能出錯；
2. **累積誤差**：在多層 Transformer 中，每一層的偏差會逐層累積；
3. **不可補償性**：乘法偏差 $\sqrt{2/\pi}$ 不同於加法偏差，無法透過簡單的偏移來校正，因為它改變了向量間的相對大小關係。

### 偏差隨位元寬度遞減

實驗結果（論文圖 1、圖 2）證實，隨著位元寬度 $b$ 的增加，MSE 量化器的內積偏差逐漸減小並趨近於零。但在低位元（$b \leq 3$）場景下，偏差仍然顯著，這正是需要 QJL 的原因。

---

<a id="qjl-在-turboquant-中的角色兩階段方案"></a>

## QJL 在 TurboQuant 中的角色：兩階段方案

TurboQuant 針對內積優化的量化器 $\text{TurboQuant}_{\text{prod}}$ 採用**兩階段方案**，巧妙地結合了 MSE 最佳量化與 QJL：

### 設計思想

> **核心洞見**：MSE 最佳量化器最小化了重建誤差（殘差的 L2 範數），但引入了內積偏差；QJL 是無偏的 1-bit 內積量化器，但其失真與輸入向量的範數成正比。如果我們先用 MSE 量化器把殘差變小，再用 QJL 量化這個小殘差，就能同時獲得「低失真」和「無偏性」。

### 兩階段流程

**第一階段：MSE 量化（$b-1$ bits）**

對輸入向量 $\mathbf{x} \in \mathbb{S}^{d-1}$ 應用位元寬度為 $b-1$ 的 $\text{TurboQuant}_{\text{mse}}$：

$$
\tilde{\mathbf{x}}_{\text{mse}} = Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))
$$

這一步的目標是**最小化殘差的 L2 範數**，使得後續 QJL 的輸入盡可能小。

**第二階段：QJL 量化殘差（1 bit）**

計算殘差向量：

$$
\mathbf{r} = \mathbf{x} - \tilde{\mathbf{x}}_{\text{mse}}
$$

對殘差應用 QJL：

$$
\text{qjl} = Q_{\text{qjl}}(\mathbf{r}) = \text{sign}(\mathbf{S} \cdot \mathbf{r})
$$

同時記錄殘差的 L2 範數 $\gamma = \|\mathbf{r}\|_2$（以浮點精度儲存）。

**反量化**

重建向量為兩部分的和：

$$
\tilde{\mathbf{x}} = \tilde{\mathbf{x}}_{\text{mse}} + \tilde{\mathbf{x}}_{\text{qjl}} = \tilde{\mathbf{x}}_{\text{mse}} + \sqrt{\frac{\pi}{2d}} \cdot \gamma \cdot \mathbf{S}^\top \cdot \text{qjl}
$$

### 為什麼這樣設計能保證無偏？

關鍵在於 QJL 的無偏性是**條件無偏**的：給定殘差 $\mathbf{r}$（即給定 $\tilde{\mathbf{x}}_{\text{mse}}$），QJL 對殘差的內積估計是無偏的：

$$
\mathbb{E}[\langle\mathbf{y}, \tilde{\mathbf{x}}_{\text{qjl}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}] = \langle\mathbf{y}, \mathbf{r}\rangle
$$

因此，整體內積估計的條件期望為：

$$
\mathbb{E}[\langle\mathbf{y}, \tilde{\mathbf{x}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}] = \langle\mathbf{y}, \tilde{\mathbf{x}}_{\text{mse}}\rangle + \langle\mathbf{y}, \mathbf{r}\rangle = \langle\mathbf{y}, \tilde{\mathbf{x}}_{\text{mse}} + \mathbf{r}\rangle = \langle\mathbf{y}, \mathbf{x}\rangle
$$

由全期望定律（law of total expectation），無條件期望也等於 $\langle\mathbf{y}, \mathbf{x}\rangle$，證明了整體估計的無偏性。

### 為什麼殘差的 L2 範數 $\gamma$ 需要單獨儲存？

QJL 的反量化公式中包含 $\gamma = \|\mathbf{r}\|_2$，這是因為：

1. QJL 的 sign 量化丟失了幅度資訊，需要外部提供縮放因子；
2. $\gamma$ 以浮點精度儲存，其額外儲存成本為 $O(1)$（每個向量僅一個純量），相對於 $d$ 維向量的量化成本可忽略不計；
3. 在反量化時，$\gamma$ 用於正確縮放 QJL 重建的部分，確保幅度匹配。

---

<a id="turboquantprod-的完整演算法"></a>

## TurboQuant_prod 的完整演算法

以下為論文演算法 2 的完整偽代碼（[論文原文](03-turboquant-translation.md#L880)）：

**演算法 2** $\text{TurboQuant}_{\text{prod}}$：針對內積優化

**全域設置（輸入：維度 $d$ 和位元寬度 $b$）：**

1. 根據演算法 1 實例化一個位元寬度為 $b-1$ 的 $\text{TurboQuant}_{\text{mse}}$
2. 生成隨機投影矩陣 $\mathbf{S}\in\mathbb{R}^{d\times d}$，其元素 $\mathbf{S}_{i,j} \sim \mathcal{N}(0,1)$ 獨立同分佈

**量化過程** $\text{Quant}_{\text{prod}}(\mathbf{x})$：

3. $\text{idx} \leftarrow \text{Quant}_{\text{mse}}(\mathbf{x})$             // 第一階段：MSE 量化
4. $\mathbf{r} \leftarrow \mathbf{x} - \text{DeQuant}_{\text{mse}}(\text{idx})$           // 計算殘差向量
5. $\text{qjl} \leftarrow \text{sign}(\mathbf{S}\cdot\mathbf{r})$                 // 第二階段：QJL 1-bit 量化殘差
6. **輸出：** $(\text{idx}, \text{qjl}, \|\mathbf{r}\|_2)$

**反量化過程** $\text{DeQuant}_{\text{prod}}(\text{idx}, \text{qjl}, \gamma)$：

7. $\tilde{\mathbf{x}}_{\text{mse}} \leftarrow \text{DeQuant}_{\text{mse}}(\text{idx})$          // 重建 MSE 量化部分
8. $\tilde{\mathbf{x}}_{\text{qjl}} \leftarrow \sqrt{\pi/(2d)}\cdot\gamma\cdot\mathbf{S}^\top\cdot\text{qjl}$   // 重建 QJL 量化部分
9. **輸出：** $\tilde{\mathbf{x}}_{\text{mse}} + \tilde{\mathbf{x}}_{\text{qjl}}$

### 位元預算分析

對於目標位元寬度 $b$：

| 組件 | 位元寬度 | 每向量儲存量 |
|------|---------|-------------|
| MSE 量化索引 $\text{idx}$ | $b-1$ bits/座標 | $(b-1) \times d$ bits |
| QJL sign 向量 $\text{qjl}$ | 1 bit/座標 | $d$ bits |
| 殘差範數 $\gamma$ | 浮點精度 | 32 bits（可忽略） |
| **總計** | **$b$ bits/座標** | **$b \times d$ bits** |

這正好達到了目標位元預算 $b \cdot d$ bits。

---

<a id="turboquantprod-的理論保證"></a>

## TurboQuant_prod 的理論保證

以下為論文定理 2 的完整陳述（[論文原文](03-turboquant-translation.md#L938)）：

**定理 2（性能保證：$\text{TurboQuant}_{\text{prod}}$）**：對於任何位元寬度 $b\geq 1$ 和任何向量 $\mathbf{x}\in\mathbb{S}^{d-1}$，過程 $\text{Quant}_{\text{prod}}(\mathbf{x})$ 輸出索引向量 $\text{idx}\in[2^{b-1}]^d$、符號向量 $\text{qjl}\in\{-1,1\}^d$ 和正數 $\gamma\geq 0$。當這些傳遞給 $\text{DeQuant}_{\text{prod}}(\text{idx}, \text{qjl}, \gamma)$ 時，產生的重建向量 $\tilde{\mathbf{x}}\in\mathbb{R}^d$ 對於任何 $\mathbf{y}\in\mathbb{R}^d$ 滿足：

- **無偏內積估計**：
$$
\mathbb{E}_{\tilde{\mathbf{x}}}[\langle\mathbf{y},\tilde{\mathbf{x}}\rangle] = \langle\mathbf{y},\mathbf{x}\rangle
$$

- **內積失真界限**（對於任何 $b\geq 0$）：
$$
D_{\text{prod}} := \mathbb{E}_{\tilde{\mathbf{x}}}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}\rangle|^2] \leq \frac{3\pi}{2}\cdot\frac{\|\mathbf{y}\|_2^2}{d}\cdot\frac{1}{4^b}
$$

- **小位元寬度的精細界限**（$b=1,2,3,4$）：
$$
D_{\text{prod}} \approx \frac{1.57}{d},\; \frac{0.56}{d},\; \frac{0.18}{d},\; \frac{0.047}{d}
$$

### 與下界的比較

根據定理 3（[論文原文](03-turboquant-translation.md#L1070)），任何量化演算法的內積失真下界為：

$$
D_{\text{prod}} \geq \frac{\|\mathbf{y}\|_2^2}{d}\cdot\frac{1}{4^b}
$$

TurboQuant_prod 的上界與此下界僅相差常數因子 $\frac{3\pi}{2} \approx 4.71$。但對於小位元寬度，這個差距更小：

| 位元寬度 $b$ | TurboQuant_prod 失真 | 下界 | 比值 |
|:---:|:---:|:---:|:---:|
| 1 | $1.57/d$ | $1/d$ | $\approx 1.57$ |
| 2 | $0.56/d$ | $0.25/d$ | $\approx 2.24$ |
| 3 | $0.18/d$ | $0.125/d$ | $\approx 1.44$ |
| 4 | $0.047/d$ | $0.0625/d$ | $\approx 0.75$（實際優於漸近上界） |

---

<a id="內積失真界限的推導"></a>

## 內積失真界限的推導

以下完整重現定理 2 中內積失真界限的推導過程（[論文原文](03-turboquant-translation.md#L964)），這是理解 TurboQuant_prod 為何有效的關鍵。

### 第一步：證明無偏性

計算內積估計在給定 $\tilde{\mathbf{x}}_{\text{mse}}$ 下的條件期望：

$$
\begin{aligned}
\mathbb{E}[\langle\mathbf{y},\tilde{\mathbf{x}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}] &= \mathbb{E}_{\tilde{\mathbf{x}}_{\text{qjl}}}[\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{mse}}+\tilde{\mathbf{x}}_{\text{qjl}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}] \\
&= \langle\mathbf{y},\tilde{\mathbf{x}}_{\text{mse}}\rangle + \mathbb{E}_{\tilde{\mathbf{x}}_{\text{qjl}}}[\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{qjl}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}] \\
&= \langle\mathbf{y},\tilde{\mathbf{x}}_{\text{mse}}\rangle + \langle\mathbf{y},\mathbf{r}\rangle \quad \text{（由引理 4 的無偏性）} \\
&= \langle\mathbf{y},\mathbf{x}\rangle \quad \text{（因為 } \mathbf{r} = \mathbf{x} - \tilde{\mathbf{x}}_{\text{mse}}\text{）}
\end{aligned}
$$

由全期望定律：$\mathbb{E}_{\tilde{\mathbf{x}}}[\langle\mathbf{y},\tilde{\mathbf{x}}\rangle] = \mathbb{E}_{\tilde{\mathbf{x}}_{\text{mse}}}[\mathbb{E}[\langle\mathbf{y},\tilde{\mathbf{x}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}]] = \langle\mathbf{y},\mathbf{x}\rangle$。 $\blacksquare$

### 第二步：推導失真界限

計算條件失真：

$$
\begin{aligned}
\mathbb{E}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}\rangle|^2 | \tilde{\mathbf{x}}_{\text{mse}}] &= \mathbb{E}_{\tilde{\mathbf{x}}_{\text{qjl}}}[|\langle\mathbf{y},\mathbf{r}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{qjl}}\rangle|^2 | \tilde{\mathbf{x}}_{\text{mse}}] \\
&= \text{Var}(\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{qjl}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}) \quad \text{（因為 } \mathbb{E}[\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{qjl}}\rangle] = \langle\mathbf{y},\mathbf{r}\rangle\text{）} \\
&\leq \frac{\pi}{2d}\cdot\|\mathbf{r}\|_2^2\cdot\|\mathbf{y}\|_2^2 \quad \text{（由引理 4 的變異數界限，加上 } \gamma = \|\mathbf{r}\|\text{ 的縮放）}
\end{aligned}
$$

由全期望定律：

$$
\begin{aligned}
D_{\text{prod}} &= \mathbb{E}_{\tilde{\mathbf{x}}_{\text{mse}}}[\mathbb{E}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}\rangle|^2 | \tilde{\mathbf{x}}_{\text{mse}}]] \\
&\leq \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2\cdot\mathbb{E}[\|\mathbf{x}-\tilde{\mathbf{x}}_{\text{mse}}\|_2^2] \\
&= \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2\cdot D_{\text{mse}}(b-1)
\end{aligned}
$$

最後，代入定理 1 中位元寬度為 $b-1$ 的 MSE 界限 $D_{\text{mse}}(b-1) \leq \frac{3\pi}{2} \cdot \frac{1}{4^{b-1}}$：

$$
D_{\text{prod}} \leq \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2 \cdot \frac{3\pi}{2}\cdot\frac{1}{4^{b-1}} = \frac{3\pi^2}{4d}\cdot\frac{\|\mathbf{y}\|_2^2}{4^{b-1}} = \frac{3\pi}{2}\cdot\frac{\|\mathbf{y}\|_2^2}{d}\cdot\frac{1}{4^b}
$$

> **關鍵洞見**：內積失真 $D_{\text{prod}}$ 與 MSE 失真 $D_{\text{mse}}$ 之間的聯繫是 $\frac{\pi}{2d} \cdot \|\mathbf{y}\|_2^2$。這意味著：
> 1. MSE 量化越好（殘差越小），內積失真也越小；
> 2. 維度 $d$ 越高，QJL 的變異數衰減越快，內積估計越精確；
> 3. 內積失真隨位元寬度 $b$ 指數衰減（$1/4^b$），這是 TurboQuant 相對於現有方法的指數級改進。 $\blacksquare$

---

<a id="數值實例詳解"></a>

## 數值實例詳解

### 簡化範例：$d=4$，$b=2$

假設有兩個 4 維單位向量 $\mathbf{x} = [0.5, 0.5, 0.5, 0.5]$（已歸一化為 $\|\mathbf{x}\|=1$），查詢向量 $\mathbf{y} = [1, 0, 0, 0]$。

**真實內積**：$\langle\mathbf{y}, \mathbf{x}\rangle = 0.5$

#### 第一階段：MSE 量化（$b-1=1$ bit）

1. **隨機旋轉**：乘以隨機正交矩陣 $\mathbf{\Pi}$，得到 $\mathbf{y}' = \mathbf{\Pi} \cdot \mathbf{x}$。假設旋轉後 $\mathbf{y}' \approx [0.48, -0.52, 0.47, 0.53]$。

2. **1-bit Lloyd-Max 量化**：對 $d=4$，1-bit 最佳碼本為 $\{\pm\sqrt{2/(\pi \cdot 4)}\} = \{\pm 0.399\}$。
   - $\hat{y}'_1 = +0.399$（因為 $0.48 > 0$）
   - $\hat{y}'_2 = -0.399$（因為 $-0.52 < 0$）
   - $\hat{y}'_3 = +0.399$（因為 $0.47 > 0$）
   - $\hat{y}'_4 = +0.399$（因為 $0.53 > 0$）

3. **反量化並旋轉回原始基底**：$\tilde{\mathbf{x}}_{\text{mse}} = \mathbf{\Pi}^\top \cdot \hat{\mathbf{y}}'$

4. **MSE 量化後的內積估計**：$\langle\mathbf{y}, \tilde{\mathbf{x}}_{\text{mse}}\rangle \approx \sqrt{2/\pi} \cdot 0.5 \approx 0.399$（有偏！低估了約 20%）

#### 第二階段：QJL 量化殘差（1 bit）

5. **計算殘差**：$\mathbf{r} = \mathbf{x} - \tilde{\mathbf{x}}_{\text{mse}}$，$\|\mathbf{r}\|_2 \approx 0.32$（由定理 1，$b=1$ 時 $D_{\text{mse}} \approx 0.36$，$\sqrt{D_{\text{mse}}} \approx 0.6$，殘差範數約為此量級）

6. **QJL 量化**：$\text{qjl} = \text{sign}(\mathbf{S} \cdot \mathbf{r}) \in \{-1, +1\}^4$

7. **QJL 反量化**：$\tilde{\mathbf{x}}_{\text{qjl}} = \sqrt{\pi/(2 \cdot 4)} \cdot 0.32 \cdot \mathbf{S}^\top \cdot \text{qjl}$

8. **最終內積估計**：$\langle\mathbf{y}, \tilde{\mathbf{x}}\rangle = \langle\mathbf{y}, \tilde{\mathbf{x}}_{\text{mse}}\rangle + \langle\mathbf{y}, \tilde{\mathbf{x}}_{\text{qjl}}\rangle$

   - 雖然單次估計可能偏離 0.5，但**期望值精確等於 0.5**（無偏性保證）；
   - 變異數約為 $\frac{\pi}{2 \cdot 4} \cdot \|\mathbf{y}\|_2^2 \cdot D_{\text{mse}}(1) \approx \frac{1.57}{4} \cdot 1 \cdot 0.36 \approx 0.14$。

> **注意**：此範例中的數值為示意性質，實際值取決於隨機矩陣 $\mathbf{\Pi}$ 和 $\mathbf{S}$ 的具體實例。無偏性是期望意義上的保證，單次實例可能偏離。

### 高維度下的行為

當 $d$ 很大時（如 $d=1536$，對應 OpenAI 嵌入維度）：

- QJL 的變異數界限為 $\frac{\pi}{2 \cdot 1536} \cdot \|\mathbf{y}\|_2^2 \approx 0.001 \cdot \|\mathbf{y}\|_2^2$，非常小；
- 這意味著在實際應用的高維場景中，QJL 的內積估計幾乎確定地接近真實值。

---

<a id="視覺化流程圖"></a>

## 視覺化流程圖

![QJL 流程圖](../svg/qjl_flowchart.svg)

上圖展示了 TurboQuant_prod 的完整兩階段流程：

1. **原始向量** → 經過隨機旋轉 → Lloyd-Max 量化（第一階段，MSE 最佳）
2. 計算**殘差** → QJL 1-bit 量化（第二階段，無偏內積）
3. 合併兩階段結果 → **壓縮結果**

---

<a id="關鍵洞察與直覺總結"></a>

## 關鍵洞察與直覺總結

### 1. QJL 的本質：用 sign 做內積估計

QJL 的核心操作是 $\text{sign}(\mathbf{S} \cdot \mathbf{x})$——將隨機投影的結果二值化。這看似極端，但高維統計學保證了：**足夠多的獨立 sign 投影的平均，可以無偏地估計內積**。這是「弱大數法則」在高維空間中的體現。

### 2. 為什麼 QJL 作用於殘差而非原始向量？

如果直接對原始向量 $\mathbf{x}$ 應用 QJL（$b=1$），內積失真為 $\frac{\pi}{2d} \cdot \|\mathbf{y}\|_2^2 \cdot \|\mathbf{x}\|_2^2 = \frac{\pi}{2d} \cdot \|\mathbf{y}\|_2^2$（因為 $\|\mathbf{x}\|=1$）。

但如果先做 MSE 量化再對殘差做 QJL，失真變為 $\frac{\pi}{2d} \cdot \|\mathbf{y}\|_2^2 \cdot D_{\text{mse}}(b-1)$，其中 $D_{\text{mse}}(b-1)$ 遠小於 1。**殘差的範數越小，QJL 引入的失真也越小**。

### 3. 兩階段的分工

| 階段 | 目標 | 方法 | 位元預算 |
|------|------|------|---------|
| 第一階段（MSE） | 最小化重建誤差 | 隨機旋轉 + Lloyd-Max 純量量化 | $b-1$ bits/座標 |
| 第二階段（QJL） | 消除內積偏差 | 隨機投影 + sign 量化 | 1 bit/座標 |

兩階段各司其職：MSE 量化負責「壓縮主要資訊」，QJL 負責「修正偏差並捕捉殘差資訊」。

### 4. 資訊理論的最優性

TurboQuant_prod 的內積失真上界為 $\frac{3\pi}{2} \cdot \frac{\|\mathbf{y}\|_2^2}{d} \cdot \frac{1}{4^b}$，而資訊理論下界為 $\frac{\|\mathbf{y}\|_2^2}{d} \cdot \frac{1}{4^b}$。兩者僅差常數因子 $\frac{3\pi}{2} \approx 4.71$，且在小位元寬度下差距更小。這意味著 **TurboQuant_prod 在漸近意義上是最優的**。

### 5. 與現有方法的指數級改進

現有方法（如基於網格的 PQ）的失真界限通常包含對位元寬度的多項式依賴（如 $1/b^2$），而 TurboQuant 的失真以 $1/4^b$ 指數衰減。這是**指數級的改進**，在低位元場景下尤為顯著。

---

<a id="延伸閱讀"></a>

## 延伸閱讀

- [2.6 QJL (Quantized Johnson-Lindenstrauss) 理論基礎解析](02-6-qjl-analysis.md) — QJL 的背景知識與技術意義
- [TurboQuant 論文翻譯 — QJL 定義與性能保證](03-turboquant-translation.md#L496) — 論文第 2.2 節原文與中譯
- [TurboQuant 論文翻譯 — 內積最佳 TurboQuant](03-turboquant-translation.md#L824) — 論文第 3.2 節原文與中譯
- [Beta 分佈詳解](03-beta-distribution.md) — 隨機旋轉後座標的分佈特性
- [Lloyd-Max 量化器詳解](03-lloyd-max-quantizer.md) — MSE 最佳純量量化器的設計
- [內積失真詳解](03-inner-product-distortion.md) — 內積失真的定義與分析
- [Shannon 失真率函數](03-shannon-distortion-rate-function.md) — 資訊理論下界的推導基礎

---

[回到 03-turboquant-translation.md QJL 相關段落](03-turboquant-translation.md#L496)
