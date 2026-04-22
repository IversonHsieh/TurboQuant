# 📐 2.6 QJL (Quantized Johnson-Lindenstrauss) 解析

## 核心理論：Johnson-Lindenstrauss Lemma
**Johnson-Lindenstrauss (JL) Lemma** 是高維幾何中的一個強大理論。它指出：給定一組 $N$ 個點，我們可以將它們投影到一個維度僅為 $O(\log N / \epsilon^2)$ 的低維空間中，同時保證點與點之間的歐幾里得距離誤差不超過 $\epsilon$。

在 TurboQuant 的語境下，這意味著我們不需要保留原始的高維 Embedding 向量，透過一個精心設計的隨機投影矩陣（Random Projection Matrix），我們可以在大幅降低維度（進而減少 KV Cache 體積）的同時，幾乎不損失向量間的相似度資訊。

## 從 JL Lemma 到 QJL
傳統的隨機投影通常需要高精度的浮點數運算，這在硬體實現上並不經濟。**QJL (Quantized JL)** 則是進一步的研究方向，旨在結合「量化」與「投影」：
1. **量化投影矩陣**：使用極低位元（如 2-int 或 4-int）來儲存投影矩陣的元素。
2. **高效運算**：利用量化後的矩陣與輸入向量進行乘法，利用位元運算（Bitwise operations）與加法來加速投影過程。
3. **誤差控制**：透過優化量化後的投影矩陣結構，確保投影後的向量間距（Distance preservation）與原始高維空間中的分佈高度一致。

## 技術意義
QJL 為 TurboQuant 提供了另一層維度縮減的理論支撐。如果說 PolarQuant 是在「維度內」進行精細的量化，那麼 QJL 則是在「維度間」進行結構性的壓縮。兩者的結合，使得 TurboQuant 能夠在極端壓縮的狀態下，依然維持 Transformer 模型對長文本處理的精準度與效能。

---

> [詳細 QJL 實例、流程圖與 TurboQuant 連結，請見 QJL 專章](03-qjl-explanation.md)
