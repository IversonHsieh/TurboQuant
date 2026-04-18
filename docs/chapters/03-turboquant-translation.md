# TurboQuant 論文完整翻譯

**論文標題：** TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate

**作者：** Amir Zandieh (Google Research), Majid Daliri (New York University), Majid Hadian (Google DeepMind), Vahab Mirrokni (Google Research)

**arXiv:** 2504.19874v1 [cs.LG] 28 Apr 2025

**許可證：** CC BY 4.0

---

## Abstract（摘要）

**原文：**

[Vector quantization](03-vector-quantization-explanation.md), a problem rooted in [Shannon's source coding theory](03-shannon-source-coding-theory.md), aims to quantize high-dimensional Euclidean vectors while minimizing distortion in their geometric structure. We propose TurboQuant to address both [mean-squared error (MSE)](03-mse-explanation.md) and [inner product distortion](03-inner-product-distortion.md), overcoming limitations of existing methods that fail to achieve optimal distortion rates. Our data-oblivious algorithms, suitable for online applications, achieve near-optimal distortion rates (within a small constant factor) across all bit-widths and dimensions. TurboQuant achieves this by randomly rotating input vectors, inducing a concentrated Beta distribution on coordinates, and leveraging the near-independence property of distinct coordinates in high dimensions to simply apply optimal scalar quantizers per each coordinate. Recognizing that MSE-optimal quantizers introduce bias in inner product estimation, we propose a two-stage approach: applying an MSE quantizer followed by a 1-bit Quantized JL (QJL) transform on the residual, resulting in an unbiased inner product quantizer. We also provide a formal proof of the information-theoretic lower bounds on best achievable distortion rate by any vector quantizer, demonstrating that TurboQuant closely matches these bounds, differing only by a small constant ($\approx 2.7$) factor. Experimental results validate our theoretical findings, showing that for KV cache quantization, we achieve absolute quality neutrality with 3.5 bits per channel and marginal quality degradation with 2.5 bits per channel. Furthermore, in nearest neighbor search tasks, our method outperforms existing product quantization techniques in recall while reducing indexing time to virtually zero.

**中文翻譯：**

[向量量化（Vector Quantization）](03-vector-quantization-explanation.md) 是一個源於 [香農（Shannon）信源編碼理論](03-shannon-source-coding-theory.md) 的問題，其目標是對高維歐幾里得向量進行量化，同時最小化其幾何結構中的失真。我們提出了 TurboQuant 來同時解決 [均方誤差（MSE）](03-mse-explanation.md) 和 [內積失真](03-inner-product-distortion.md) 問題，克服了現有方法無法達到最佳失真率的限制。我們的數據無知（data-oblivious）演算法適合線上應用，在所有位元寬度和維度上都能達到接近最佳的失真率（在一個小常數因子內）。TurboQuant 透過隨機旋轉輸入向量來實現這一目標，誘導座標上產生集中的 Beta 分佈，並利用高維度中不同座標的近似獨立性，對每個座標簡單地應用最佳純量量化器。認識到 MSE 最佳量化器會在內積估計中引入偏差，我們提出了一個兩階段方法：首先應用 MSE 量化器，然後對殘差應用 1 位元量化 JL（QJL）變換，從而產生一個無偏的內積量化器。我們還提供了任何向量量化器可達到的最佳失真率的資訊理論下界的正式證明，表明 TurboQuant 與這些下界非常接近，僅相差一個小常數（$\approx 2.7$）因子。實驗結果驗證了我們的理論發現，表明對於 KV 快取量化，我們在每通道 3.5 位元時達到絕對的品質中性，在每通道 2.5 位元時僅有邊際的品質下降。此外，在最近鄰搜尋任務中，我們的方法在召回率方面優於現有的乘積量化技術，同時將索引時間減少到幾乎為零。

---

## 1 Introduction（引言）

**原文：**

Vector quantization (VQ) in Euclidean space is crucial for efficiently handling high-dimensional vectors across a spectrum of computational domains, from training and deploying large-scale AI and deep learning models to powering vector databases for search/retrieval systems. The core objective is to compress high dimensional vectors by quantizing them–converting floating-point coordinate values to low-bitwidth integers–while minimizing distortion, quantified by metrics such as mean-squared error (MSE) or inner product errors. By preserving these properties, inner product queries can be answered rapidly, with minimal latency, and using reduced computational and communication resources.

**中文翻譯：**

歐幾里得空間中的向量量化（VQ）對於在一系列計算領域中有效處理高維向量至關重要，從訓練和部署大規模 AI 和深度學習模型，到為搜尋/檢索系統提供向量資料庫支援。核心目標是透過量化來壓縮高維向量——將浮點座標值轉換為低位元寬度整數——同時最小化失真，失真可由均方誤差（MSE）或內積誤差等指標來量化。透過保留這些屬性，內積查詢可以快速回答，具有最小的延遲，並使用減少的計算和通訊資源。

---

**原文：**

This problem's roots trace back to Shannon's seminal work on Source Coding theory [48, 49], which established that the least distortion achievable by block source codes, now known as vector quantizers, is defined by the Shannon distortion-rate function, determined by the statistical properties of the source and the chosen distortion measure, such as MSE. Today, VQ plays a critical role in fundamental computational domains, including AI, deep learning, and search systems.

**中文翻譯：**

這個問題的根源可以追溯到香農關於信源編碼理論的開創性著作 [48, 49]，其中確立了塊源碼可達到的最小失真（現在稱為向量量化器）由香農失真率函數定義，該函數由源的統計特性和所選擇的失真度量（如 MSE）決定。如今，VQ 在基礎計算領域（包括 AI、深度學習和搜尋系統）中發揮著至關重要的作用。

---

[深入了解向量量化（Vector Quantization）](03-vector-quantization-explanation.md)

[深入了解內積失真（Inner Product Distortion）](03-inner-product-distortion.md)

[返回 TurboQuant 論文翻譯](03-turboquant-translation.md)

---

> 本頁內容引用自 [`03-vector-quantization-explanation.md`](03-vector-quantization-explanation.md) 和 [`03-inner-product-distortion.md`](03-inner-product-distortion.md)。
> 
> [回到 TurboQuant 內積失真說明](03-inner-product-distortion.md)
> [回到 TurboQuant 向量量化說明](03-vector-quantization-explanation.md)
