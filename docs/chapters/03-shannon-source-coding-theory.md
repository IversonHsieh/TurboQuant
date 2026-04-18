# Shannon's Source Coding Theory (香農信源編碼理論)

香農信源編碼理論 (Shannon's source coding theory) 是資訊理論的核心組成部分，由克勞德·香農 (Claude Shannon) 於 1948 年提出。該理論定義了數據壓縮的基礎極限。

## 核心概念

### 1. 資訊熵 (Entropy)
香農定義了資訊熵 $H(X)$，衡量一個隨機變數 $X$ 的平均不確定性。對於取值於集合 $\mathcal{X}$ 的離散隨機變數，其熵為：
$$H(X) = -\sum_{x \in \mathcal{X}} p(x) \log_2 p(x)$$
單位通常為位元 (bits)。

### 2. 信源編碼定理 (Source Coding Theorem)
該定理指出，對於一個信源 $X$，我們可以將其編碼為二進位碼，使得每個符號的平均編碼長度 $L$ 滿足：
$$L \ge H(X)$$
這意味著，壓縮後的資料長度不可能小於該資訊源的熵。

## 在 TurboQuant 中的意義

在 TurboQuant 的上下文中，這種理論用來優化模型參數或 KV Cache 的存儲，透過編碼技術達到接近熵的極限，從而減少記憶體佔用。
