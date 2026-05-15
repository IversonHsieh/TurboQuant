# TurboQuant 論文完整翻譯

[🏠 返回目錄](../index.md)

**論文標題：** TurboQuant: Online Vector Quantization with Near-optimal Distortion Rate

**作者：** Amir Zandieh (Google Research), Majid Daliri (New York University), Majid Hadian (Google DeepMind), Vahab Mirrokni (Google Research)

**arXiv:** 2504.19874v1 [cs.LG] 28 Apr 2025

**許可證：** CC BY 4.0

---

## Abstract（摘要）

**原文：**

[Vector quantization](03-vector-quantization-explanation.md), a problem rooted in [Shannon's source coding theory](03-shannon-source-coding-theory.md), aims to quantize high-dimensional Euclidean vectors while minimizing distortion in their geometric structure. We propose TurboQuant to address both [mean-squared error (MSE)](03-mse-explanation.md) and [inner product distortion](03-inner-product-distortion.md), overcoming limitations of existing methods that fail to achieve optimal distortion rates. Our data-oblivious algorithms, suitable for online applications, achieve near-optimal distortion rates (within a small constant factor) across all bit-widths and dimensions. TurboQuant achieves this by randomly rotating input vectors, inducing a concentrated [Beta distribution](03-beta-distribution.md) on coordinates, and leveraging the near-independence property of distinct coordinates in high dimensions to simply apply optimal scalar quantizers per each coordinate. Recognizing that MSE-optimal quantizers introduce bias in inner product estimation, we propose a two-stage approach: applying an MSE quantizer followed by a 1-bit Quantized JL (QJL) transform on the residual, resulting in an unbiased inner product quantizer. We also provide a formal proof of the information-theoretic lower bounds on best achievable distortion rate by any vector quantizer, demonstrating that TurboQuant closely matches these bounds, differing only by a small constant ($\approx 2.7$) factor. Experimental results validate our theoretical findings, showing that for KV cache quantization, we achieve absolute quality neutrality with 3.5 bits per channel and marginal quality degradation with 2.5 bits per channel. Furthermore, in nearest neighbor search tasks, our method outperforms existing product quantization techniques in recall while reducing indexing time to virtually zero.

**中文翻譯：**

[向量量化（Vector Quantization）](03-vector-quantization-explanation.md) 是一個源於 [香農（Shannon）信源編碼理論](03-shannon-source-coding-theory.md) 的問題，其目標是對高維歐幾里得向量進行量化，同時最小化其幾何結構中的失真。我們提出了 TurboQuant 來同時解決 [均方誤差（MSE）](03-mse-explanation.md) 和 [內積失真](03-inner-product-distortion.md) 問題，克服了現有方法無法達到最佳失真率的限制。我們的數據無知（data-oblivious）演算法適合線上應用，在所有位元寬度和維度上都能達到接近最佳的失真率（在一個小常數因子內）。TurboQuant 透過隨機旋轉輸入向量來實現這一目標，誘導座標上產生集中的 [Beta 分佈](03-beta-distribution.md)，並利用高維度中不同座標的近似獨立性，對每個座標簡單地應用最佳純量量化器。認識到 MSE 最佳量化器會在內積估計中引入偏差，我們提出了一個兩階段方法：首先應用 MSE 量化器，然後對殘差應用 1 位元量化 JL（QJL）變換，從而產生一個無偏的內積量化器。我們還提供了任何向量量化器可達到的最佳失真率的資訊理論下界的正式證明，表明 TurboQuant 與這些下界非常接近，僅相差一個小常數（$\approx 2.7$）因子。實驗結果驗證了我們的理論發現，表明對於 KV 快取量化，我們在每通道 3.5 位元時達到絕對的品質中性，在每通道 2.5 位元時僅有邊際的品質下降。此外，在最近鄰搜尋任務中，我們的方法在召回率方面優於現有的乘積量化技術，同時將索引時間減少到幾乎為零。

---

## 1 Introduction（引言）

**原文：**

Vector quantization (VQ) in Euclidean space is crucial for efficiently handling high-dimensional vectors across a spectrum of computational domains, from training and deploying large-scale AI and deep learning models to powering vector databases for search/retrieval systems. The core objective is to compress high dimensional vectors by quantizing them–converting floating-point coordinate values to low-bitwidth integers–while minimizing distortion, quantified by metrics such as mean-squared error (MSE) or [inner product errors](03-inner-product-errors.md). By preserving these properties, inner product queries can be answered rapidly, with minimal latency, and using reduced computational and communication resources.

**中文翻譯：**

歐幾里得空間中的向量量化（VQ）對於在一系列計算領域中有效處理高維向量至關重要，從訓練和部署大規模 AI 和深度學習模型，到為搜尋/檢索系統提供向量資料庫支援。核心目標是透過量化來壓縮高維向量——將浮點座標值轉換為低位元寬度整數——同時最小化失真，失真可由均方誤差（MSE）或 [內積誤差](03-inner-product-errors.md) 等指標來量化。透過保留這些屬性，內積查詢可以快速回答，具有最小的延遲，並使用減少的計算和通訊資源。

---

**原文：**

This problem's roots trace back to [Shannon's seminal work on Source Coding theory [48, 49]](03-shannon-source-coding-detailed.md), which established that the least distortion achievable by block source codes, now known as vector quantizers, is defined by the [Shannon distortion-rate function](03-shannon-distortion-rate-function.md), determined by the statistical properties of the source and the chosen distortion measure, such as MSE. Today, VQ plays a critical role in fundamental computational domains, including AI, deep learning, and search systems.

**中文翻譯：**

這個問題的根源可以追溯到[香農關於信源編碼理論的開創性工作 [48, 49]](03-shannon-source-coding-detailed.md)，該工作確立了塊信源編碼（現在稱為向量量化器）可達到的最小失真由香農失真 - 率函數定義，該函數由信源的統計特性和所選擇的失真度量（如 MSE）決定。如今，VQ 在基礎計算領域發揮著關鍵作用，包括 AI、深度學習和搜尋系統。

---

**原文：**

A key application of VQ is in the deployment of AI models, including large language models (LLMs) [5, 18, 7, 52]. As LLM capabilities depend heavily on their model size and context length [34], serving them requires substantial memory demands and increased inference latency. This latency is primarily attributed to communication bottlenecks between HBM and SRAM on accelerators, or across distributed clusters. By compressing or quantizing model weights and activations, we can effectively mitigate these bottlenecks, resulting in significant reductions in inference costs. Inner product operations between activations and weights is at the core of deep learning models. Thus, model quantization schemes strive to compress weights and/or activation vectors while accurately preserving these inner products.

**中文翻譯：**

VQ 的一個關鍵應用是在 AI 模型（包括大型語言模型（LLM））的部署中 [5, 18, 7, 52]。由於 LLM 的能力嚴重依賴於其模型大小和上下文長度 [34]，為它們提供服務需要大量的記憶體需求和增加的推論延遲。這種延遲主要歸因於加速器上 HBM 和 SRAM 之間的通訊瓶頸，或跨分散式集群的通訊瓶頸。透過壓縮或量化模型權重和激活，我們可以有效緩解這些瓶頸，從而顯著降低推論成本。激活和權重之間的內積運算處於深度學習模型的核心。因此，模型量化方案致力於壓縮權重和/或激活向量，同時準確地保留這些內積。

---

**原文：**

Decoder based transformer models [54] present another compelling use case. These models must store key/value (KV) embeddings from previously generated tokens in the KV cache, the size of which scales with both model size (number of layers and attention heads) and context length. This scaling is a significant bottleneck in terms of memory usage and computational speed, especially for long context models. Therefore, reducing the KV cache size without compromising accuracy is essential. In this context, the preservation of the Euclidean structure of these embedding vectors–their inner products and distances–is crucial for maintaining model performance. VQ emerges as the most suitable framework for addressing this challenge, offering a robust approach to compressing high-dimensional embeddings while preserving their essential geometric properties.

**中文翻譯：**

基於解碼器的 transformer 模型 [54] 提出了另一個引人注目的用例。這些模型必須將先前生成的 token 的鍵/值（KV）嵌入存儲在 KV 快取中，其大小隨模型大小（層數和注意力頭數）和上下文長度而擴展。這種擴展在記憶體使用和計算速度方面是一個重大瓶頸，特別是對於長上下文模型。因此，在不影響準確性的情況下減少 KV 快取大小至關重要。在這種情況下，保留這些嵌入向量的歐幾里得結構——它們的內積和距離——對於維持模型性能至關重要。VQ 成為解決這一挑戰最合適的框架，提供了一種壓縮高維嵌入同時保留其基本幾何特性的強健方法。

---

**原文：**

Additionally, [nearest neighbor](03-nearest-neighbor-explanation.md) (NN) search in high-dimensional spaces with inner product or cosine similarity [1, 27] is a cornerstone of vector databases [4, 2, 3]. These databases are fundamental for retrieval-augmented generation [23, 19] and information retrieval [35, 46]. VQ, a.k.a. [product quantization (PQ)](03-product-quantization-explanation.md), plays a critical role in these applications. It enables efficient compression of database vectors, optimizes memory usage, and facilitates low-latency, accurate estimations of inner products with query vectors, thereby enabling fast and precise [nearest neighbor searches](03-nearest-neighbor-explanation.md).

**中文翻譯：**

此外，在高維空間中使用內積或餘弦相似度的 [最近鄰](03-nearest-neighbor-explanation.md)（NN）搜尋 [1, 27] 是向量資料庫的基石 [4, 2, 3]。這些資料庫對於檢索增強生成 [23, 19] 和資訊檢索 [35, 46] 至關重要。VQ，又稱[乘積量化（PQ）](03-product-quantization-explanation.md)，在這些應用中發揮著關鍵作用。它能夠有效壓縮資料庫向量，優化記憶體使用，並促進與查詢向量的內積的低延遲、準確估計，從而實現快速和精確的 [最近鄰搜尋](03-nearest-neighbor-explanation.md)。

---

**原文：**

Existing VQ algorithms present a trade-off: either they lack accelerator (vectorization) compatibility and exhibit slow computation, making them unsuitable for real-time AI applications like KV cache quantization, or they suffer from [suboptimal distortion bounds](03-suboptimal-distortion-bounds.md) relative to bit-width. Our objective is to introduce an algorithm that addresses these limitations. Specifically, we design TurboQuant: a lightweight, capable of online application (crucial for scenarios like KV cache quantization), and highly accelerator-friendly—a critical attribute for modern AI workloads.

**中文翻譯：**

現有的 VQ 演算法存在權衡：要麼它們缺乏加速器（向量化）相容性並表現出計算緩慢，使其不適合像 KV 快取量化這樣的即時 AI 應用，要麼它們相對於位元寬度遭受 [次佳的失真界限（suboptimal distortion bounds）](03-suboptimal-distortion-bounds.md)。我們的目標是引入一種演算法來解決這些限制。具體來說，我們設計了 TurboQuant：一種輕量級的、能夠線上應用（對於像 KV 快取量化這樣的場景至關重要）、並且高度加速器友好的演算法——這是現代 AI 工作負載的關鍵屬性。

---

**原文：**

The core of TurboQuant is a two-stage process. First, we develop a vector quantizer with optimal distortion rate in terms of mean-squared error (MSE). Subsequently, we apply a 1-bit quantizer to the residual, resulting in an unbiased and low-distortion inner product quantizer. We demonstrate that quantizers optimized for MSE do not produce unbiased estimators for inner products, and our two-stage solution effectively bridges this gap. Our MSE-optimal quantizer starts by randomly rotating $d$-dimensional input vectors. Observing the key fact that each coordinate in the rotated vectors follows a [Beta distribution](03-beta-distribution.md), we design optimal [Lloyd-Max quantizer](03-lloyd-max-quantizer.md) [42, 43] for each coordinate by solving a continuous [k-means problem](03-k-means-problem.md). This method gives optimal MSE distortion bound and minimizes the L2 norm of the residual. To obtain an unbiased and low-distortion quantizer for inner products, we compose our quantizer with the recently developed [Quantized Johnson-Lindenstrauss (QJL)](03-qjl-explanation.md) transform [62], which quantizes each coordinate of the residual vector to a single bit. Our algorithm offers provably optimal distortion bounds for both MSE and inner products, achieving an exponential improvement over existing methods in terms of bit-width dependence.

> [詳細解說與範例，請見 QJL 專章](03-qjl-explanation.md)

**中文翻譯：**

TurboQuant 的核心是一個兩階段過程。首先，我們開發了一個在均方誤差（MSE）方面具有最佳失真率的向量量化器。隨後，我們對殘差應用 1 位元量化器，從而產生一個無偏且低失真的內積量化器。我們證明，針對 MSE 優化的量化器不會產生內積的無偏估計器，而我們的兩階段解決方案有效地彌合了這一差距。我們的 MSE 最佳量化器首先隨機旋轉 $d$ 維輸入向量。觀察到旋轉向量中每個座標遵循 [Beta 分佈](03-beta-distribution.md) 這一關鍵事實，我們透過解決連續 [k-means 問題](03-k-means-problem.md) 為每個座標設計最佳 [Lloyd-Max 量化器](03-lloyd-max-quantizer.md) [42, 43]。這種方法給出最佳 MSE 失真界限並最小化殘差的 [L2 範數](03-l2-norm-explanation.md)。為了獲得內積的無偏且低失真量化器，我們將我們的量化器與最近開發的[量化 Johnson-Lindenstrauss（QJL）](03-qjl-explanation.md)變換 [62] 組合，該變換將殘差向量的每個座標量化為單個位元。我們的演算法為 MSE 和內積提供了可證明的最佳失真界限，在位元寬度依賴性方面實現了相對於現有方法的指數級改進。

> [詳細解說與範例，請見 QJL 專章](03-qjl-explanation.md)

---

### 1.1 Problem Definition（問題定義）

**原文：**

Formally, our goal is to design a quantization map, denoted as $Q:\mathbb{R}^d \to \{0,1\}^B$, that transforms $d$-dimensional vectors to a binary string of $B$ bits. If we set $B=b\cdot d$ for some $b\geq 0$, this quantizer will have a bit-width of $b$, representing the average number of bits used to encode each real-valued coordinate of $\mathbb{R}^d$. Crucially, we require an inverse map, $Q^{-1}:\{0,1\}^B \to \mathbb{R}^d$ that performs dequantization, approximately reconstructing original vectors from their quantized representations. Of course, this transformation is inherently lossy, as $Q$ is not a bijection. So, our primary objective is to minimize distortion, with a specific focus on mean-squared error (MSE) and inner product distortion.

**中文翻譯：**

形式上，我們的目標是設計一個量化映射，記為 $Q:\mathbb{R}^d \to \{0,1\}^B$，將 $d$ 維向量轉換為 $B$ 位元的二進位字串。如果我們設定 $B=b\cdot d$（其中 $b\geq 0$），該量化器將具有位元寬度 $b$，表示用於編碼 $\mathbb{R}^d$ 的每個實值座標的平均位元數。至關重要的是，我們需要一個逆映射 $Q^{-1}:\{0,1\}^B \to \mathbb{R}^d$ 來執行反量化，從其量化表示中近似重建原始向量。當然，這個變換本質上是有損的，因為 $Q$ 不是雙射。因此，我們的主要目標是最小化失真，特別關注均方誤差（MSE）和內積失真。

---

**原文：**

We make no assumptions about the input vector dataset, considering the worst-case scenario. We let the quantizer $Q(\cdot)$ to be randomized, leading to stochastic outputs. Considering randomized quantizers, it is more appropriate to define the expected distortion over the randomness of the quantizer's output. Thus, we aim to design quantizers that for any desired bit-width $b$ minimize the following expected distortion measures for any (worst-case) vectors $\mathbf{x},\mathbf{y}\in\mathbb{R}^d$:

$$
\text{(MSE)}\quad D_{\text{mse}}:=\mathbb{E}_Q[\|\mathbf{x}-Q^{-1}(Q(\mathbf{x}))\|_2^2] \tag{1}
$$

$$
\text{(inner-prod error)}\quad D_{\text{prod}}:=\mathbb{E}_Q[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},Q^{-1}(Q(\mathbf{x}))\rangle|^2] \tag{2}
$$

**中文翻譯：**

我們不對輸入向量資料集做任何假設，考慮最壞情況。我們讓量化器 $Q(\cdot)$ 是隨機化的，導致隨機輸出。考慮到隨機量化器，更恰當的是根據量化器輸出的隨機性來定義期望失真。因此，我們的目標是設計量化器，對於任何期望的位元寬度 $b$，最小化任何（最壞情況）向量 $\mathbf{x},\mathbf{y}\in\mathbb{R}^d$ 的以下期望失真度量：

$$
\text{(MSE)}\quad D_{\text{mse}}:=\mathbb{E}_Q[\|\mathbf{x}-Q^{-1}(Q(\mathbf{x}))\|_2^2] \tag{1}
$$

$$
\text{(內積誤差)}\quad D_{\text{prod}}:=\mathbb{E}_Q[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},Q^{-1}(Q(\mathbf{x}))\rangle|^2] \tag{2}
$$

---

**原文：**

The expectations above are takes with respect to the randomness of the quantizer $Q(\cdot)$. Furthermore, for inner-product quantizers, we require unbiasedness of the inner product estimator, a desirable property for numerous applications. More precisely, we require:

$$
\text{(unbiased inner-prod)}\quad \mathbb{E}_Q[\langle\mathbf{y},Q^{-1}(Q(\mathbf{x}))\rangle]=\langle\mathbf{y},\mathbf{x}\rangle.
$$

**中文翻譯：**

上述期望是相對於量化器 $Q(\cdot)$ 的隨機性而言的。此外，對於內積量化器，我們要求內積估計器的無偏性，這是許多應用中所需的屬性。更精確地說，我們要求：

$$
\text{(無偏內積)}\quad \mathbb{E}_Q[\langle\mathbf{y},Q^{-1}(Q(\mathbf{x}))\rangle]=\langle\mathbf{y},\mathbf{x}\rangle.
$$

---

**原文：**

We aim to design computationally efficient quantizers $Q_{\text{mse}}$ and $Q_{\text{prod}}$, that achieve optimal bounds for the distortion measures defined above, for any given bit-width $b$. Additionally, we aim for $Q_{\text{prod}}$ to provide unbiased inner product estimates. In particular, assume that we are given $n$ real-valued vectors $x_1,x_2,\ldots x_n\in\mathbb{R}^d$. We design the following primitives:

• **Quant**: efficiently quantizes the dataset and computes $Q(\mathbf{x}_1),Q(\mathbf{x}_2),\ldots Q(\mathbf{x}_n)$.

• **DeQuant**: given a quantized dataset, can efficiently reconstruct original vectors by computing $Q^{-1}(Q(\mathbf{x}_i))$ for any $i\in[n]$.

**中文翻譯：**

我們的目標是設計計算高效的量化器 $Q_{\text{mse}}$ 和 $Q_{\text{prod}}$，對於任何給定的位元寬度 $b$，實現上述失真度量的最佳界限。此外，我們的目標是讓 $Q_{\text{prod}}$ 提供無偏的內積估計。特別是，假設我們給定 $n$ 個實值向量 $x_1,x_2,\ldots x_n\in\mathbb{R}^d$。我們設計以下基本操作：

• **Quant**：有效地量化資料集並計算 $Q(\mathbf{x}_1),Q(\mathbf{x}_2),\ldots Q(\mathbf{x}_n)$。

• **DeQuant**：給定一個量化資料集，可以透過計算任何 $i\in[n]$ 的 $Q^{-1}(Q(\mathbf{x}_i))$ 來有效重建原始向量。

---

### 1.2 Related Work（相關工作）

**原文：**

**Beginnings of VQ.** The vector quantization theory started by Shannon's seminal work [48, 49] on achievable distortion-rate functions. In 1963, Zador [61] made significant advances by employing high-resolution methods to derive the limiting operational distortion-rate function for fixed-rate quantization at high rates that closely matches Shannon's distortion-rate function. However, Zador did not specifically consider implementable algorithms. Gersho's influential paper [25], further advanced the vector quantization by popularizing high-resolution theory, simplifying Zador's results, introducing lattice vector quantization, and proposing a key conjecture that shaped the field. Despite these theoretical advancements, the practical applicability of vector quantization remained unclear in early years. The most straightforward encoding method, [brute-force nearest neighbor search](03-brute-force-nn-explanation.md), was computationally expensive, hindering the adoption of VQ in practice.

**中文翻譯：**

**VQ 的開端。** 向量量化理論始於香農關於可達失真 - 率函數的開創性工作 [48, 49]。1963 年，Zador [61] 透過使用高分辨率方法推導出高碼率下定量化的極限操作失真 - 率函數，該函數與香農的失真 - 率函數非常接近，取得了重大進展。然而，Zador 沒有特別考慮可實現的演算法。Gersho 的有影響力的論文 [25]（[詳細解說請見此處](03-gersho-paper.md)），進一步推進了向量量化，透過普及高分辨率理論、簡化 Zador 的結果、引入晶格向量量化，並提出了一個塑造該領域的關鍵猜想。儘管有這些理論進步，向量量化的實際適用性在早期仍不清楚。最直接的編碼方法——[暴力最近鄰搜尋](03-brute-force-nn-explanation.md)——計算成本高昂，阻礙了 VQ 在實踐中的採用。

---

**原文：**

**Online vs Offline Quantization.** Online (data-oblivious) quantization methods apply instantly without needing data-specific tuning or calibrations [16, 8, 41, 47, 28]. In contrast, offline (data-dependent) methods require heavy preprocessing and learning to adapt the quantization map to the data, making them unsuitable for dynamic data scenarios [37]. For instance, methods such as those presented in [20, 39, 57, 13] use [second-order (Hessian) information](03-hessian-information.md) to tune the quantization map which requires heavy preprocessing and even in some cases post processing as well.

**中文翻譯：**

**線上與離線量化。** 線上（數據無知）量化方法可以立即應用，無需針對特定數據進行調整或校準 [16, 8, 41, 47, 28]。相比之下，離線（數據依賴）方法需要大量的預處理和學習來使量化映射適應數據，使其不適合動態數據場景 [37]。例如，[20, 39, 57, 13] 中提出的方法使用[二階（Hessian）資訊](03-hessian-information.md)來調整量化映射，這需要大量的預處理，在某些情況下甚至需要後處理。

---

**原文：**

**Online KV Cache Compression.** Several approaches have been proposed to compress the KV cache. These include architectural modifications [50, 6, 15] which restructure the transformer to minimize the number of stored key-value pairs. Additionally, pruning or evicting redundant or less critical tokens has emerged as another approach [11, 66, 40, 58, 64, 38, 29].

A simple yet effective approach to reducing KV cache size is quantizing the KV cache. Several quantization techniques have been developed specifically for this purpose [60, 59, 17, 33, 65, 41, 30, 36, 28]. Recently, a new quantization called QJL [62] introduced an efficient, data-oblivious 1-bit quantization approach based on sketching techniques, which provides unbiased estimates for inner product queries. This method does not require tuning or adaptation to the input data and we make use of this technology in our quantizer optimized for inner product distortion.

**中文翻譯：**

**線上 KV 快取壓縮。** 已經提出了幾種方法來壓縮 KV 快取。這些包括架構修改 [50, 6, 15]，重構 transformer 以最小化存儲的鍵值對數量。此外，修剪或淘汰冗餘或不太重要的 token 已成為另一種方法 [11, 66, 40, 58, 64, 38, 29]。

一種簡單但有效的減少 KV 快取大小的方法是量化 KV 快取。已經專門為此目的開發了幾種量化技術 [60, 59, 17, 33, 65, 41, 30, 36, 28]。最近，一種稱為 QJL [62] 的新量化方法引入了一種基於草圖技術的高效、數據無知的 1 位元量化方法，該方法為內積查詢提供無偏估計。這種方法不需要針對輸入數據進行調整或適應，我們在針對內積失真優化的量化器中使用了這項技術。

---

**原文：**

**Product Quantization (PQ).** In Near Neighbor (NN) search problem with Euclidean datasets, the index size poses a significant memory bottleneck, often mitigated by quantization techniques, commonly referred to as Product Quantization (PQ) in the NN literature. Many of these algorithms rely on constructing a quantization codebook using variations of k-means during the indexing phase [31, 9, 24, 56, 27]. Therefore, these methods are ill-suited for online settings due to their requirement for extensive preprocessing.

Recently, a grid-based PQ method was introduced in [22], eliminating the need for preprocessing. This approach operates by projecting a uniform grid onto the unit sphere and conducting a search to identify the nearest projection to the data points. While the paper's theoretical guarantees are suboptimal, likely due to loose analysis—as practical performance surpasses theoretical bounds—the grid projection and binary search algorithm is also computationally slow and particularly inefficient on accelerators like GPU because of their algorithm's inherent lack of vectorization, which prevents parallel processing.

**中文翻譯：**

**乘積量化（PQ）。** 在具有歐幾里得數據集的最近鄰（NN）搜尋問題中，索引大小構成了顯著的記憶體瓶頸，通常透過量化技術來緩解，在 NN 文獻中通常稱為乘積量化（PQ）。這些演算法中的許多依賴於在索引階段使用 k-means 的變體來構建量化碼本 [31, 9, 24, 56, 27]。因此，由於需要大量預處理，這些方法不適合線上設置。

最近，[22] 中引入了一種基於網格的 PQ 方法，消除了對預處理的需求。這種方法透過將均勻網格投影到單位球面上並進行搜尋以識別最接近數據點的投影來運作。雖然該論文的理論保證是次佳的（可能是由於分析鬆散——因為實際性能超過理論界限），但網格投影和二元搜尋演算法在計算上也很慢，並且在像 GPU 這樣的加速器上特別低效，因為其演算法本質上缺乏向量化，這阻止了並行處理。

---

### 1.3 Overview of Techniques and Contributions（技術與貢獻概述）

**原文：**

**MSE Optimized TurboQuant.** Our first VQ algorithm is designed to minimize MSE distortion defined in ??. To achieve this, we apply a random rotation to the input vectors, thereby inducing a [Beta distribution](03-beta-distribution.md) on each coordinate, irrespective of the input vectors themselves. In high dimensions $d$, the distribution of each coordinate converges to a Gaussian distribution $\mathcal{N}(1,1/d)$ due to concentration of measure and the central limit theorem. Furthermore, any two distinct coordinates become nearly uncorrelated and, more importantly, almost independent (a deeper result that goes beyond just correlation). This near-independence is a crucial aspect that simplifies our quantization design. It allows us to quantize each coordinate using optimal scalar quantization, disregarding interactions or correlations between different coordinates, while still achieving near-optimal distortion.

We find optimal scalar quantizers for random variables with [Beta distributions](03-beta-distribution.md) by solving a continuous 1-dimensional k-means problem using the Max-Lloyd algorithm. We precompute and store these optimal codebooks for a range of practically useful bit-widths, to enable efficient subsequent invocations of our TurboQuant algorithm.

**中文翻譯：**

**MSE 優化的 TurboQuant。** 我們的第一個 VQ 演算法旨在最小化 ?? 中定義的 MSE 失真。為了實現這一目標，我們對輸入向量應用隨機旋轉，從而在每個座標上誘導 [Beta 分佈](03-beta-distribution.md)，無論輸入向量本身如何。在高維度 $d$ 中，由於測度集中和中心極限定理，每個座標的分佈收斂於高斯分佈 $\mathcal{N}(1,1/d)$。此外，任何兩個不同的座標變得幾乎不相關，更重要的是，幾乎獨立（這是一個比僅僅相關性更深入的結果）。這種近似獨立性是簡化我們量化設計的關鍵方面。它允許我們使用最佳純量量化來量化每個座標，忽略不同座標之間的相互作用或相關性，同時仍能實現接近最佳的失真。

我們透過使用 Max-Lloyd 演算法解決連續一維 k-means 問題，找到具有 [Beta 分佈](03-beta-distribution.md) 的隨機變量的最佳純量量化器。我們預先計算並存儲這些最佳碼本，適用於一系列實際上有用的位元寬度，以便後續高效地調用我們的 TurboQuant 演算法。

---

**原文：**

In ?? we prove that the $b$-bit MSE optimized TurboQuant $Q_{\text{mse}}:\mathbb{R}^d \to \{0,1\}^{b\cdot d}$ achieves the following distortion for any worst-case vector $\mathbf{x}\in\mathbb{R}^d$ with $\|\mathbf{x}\|=1$:

• $D_{\text{mse}}(Q_{\text{mse}}):=\mathbb{E}[\|\mathbf{x}-Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))\|_2^2] \leq \frac{3\pi}{2}\cdot\frac{1}{4^b}$ for any $b\geq 0$.

• For small bit-widths the above distortion upper bound can be further refined. Specifically, for $b=1,2,3,4$ we have $D_{\text{mse}}(Q_{\text{mse}}) \approx 0.36, 0.117, 0.03, 0.009$, respectively.

Note that the unit norm assumption, $\|x\|_2=1$, is standard and not restrictive. For datasets that do not satisfy this assumption we can compute and store the $L2$ norms in floating-point precision and rescale the dequantized points using these stored norms.

**中文翻譯：**

在 ?? 中，我們證明了 $b$ 位元 MSE 優化的 TurboQuant $Q_{\text{mse}}:\mathbb{R}^d \to \{0,1\}^{b\cdot d}$ 對於任何最壞情況向量 $\mathbf{x}\in\mathbb{R}^d$（其中 $\|\mathbf{x}\|=1$）實現以下失真：

• $D_{\text{mse}}(Q_{\text{mse}}):=\mathbb{E}[\|\mathbf{x}-Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))\|_2^2] \leq \frac{3\pi}{2}\cdot\frac{1}{4^b}$ 對於任何 $b\geq 0$。

• 對於小位元寬度，上述失真上界可以進一步細化。具體來說，對於 $b=1,2,3,4$，我們分別有 $D_{\text{mse}}(Q_{\text{mse}}) \approx 0.36, 0.117, 0.03, 0.009$。

請注意，單位範數假設 $\|x\|_2=1$ 是標準的且不具限制性。對於不滿足此假設的數據集，我們可以計算並存儲 $L2$ 範數（浮點精度），並使用這些存儲的範數重新縮放反量化點。

---

**原文：**

**Inner Product TurboQuant.** We show that the MSE optimized quantizers are biased for inner product estimation and thus a different VQ scheme is needed to get an unbiased inner product quantizer. Our solution is a two stage algorithm that first applies the abovementioned $Q_{\text{mse}}$ with a bit-width one less than our target budget and then apply a QJL [62] on the residual error. This is proved to be unbiased and also has nearly optimal inner product error rate.

In ?? we prove that the $b$-bit inner product optimized TurboQuant $Q_{\text{prod}}:\mathbb{R}^d \to \{0,1\}^{b\cdot d}$ achieves the following distortion for any worst-case vectors $\mathbf{x},\mathbf{y}\in\mathbb{R}^d$ with $\|\mathbf{x}\|=1$:

• $\mathbb{E}[\langle\mathbf{y},Q_{\text{prod}}^{-1}(Q_{\text{prod}}(\mathbf{x}))\rangle]=\langle\mathbf{y},\mathbf{x}\rangle$

• $D_{\text{prod}}(Q_{\text{prod}}):=\mathbb{E}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},Q_{\text{prod}}^{-1}(Q_{\text{prod}}(\mathbf{x}))\rangle|^2] \leq \frac{3\pi}{2}\cdot\frac{\|\mathbf{y}\|^2}{d}\cdot\frac{1}{4^b}$ for any $b\geq 0$.

• For small bit-widths the above distortion upper bound can be further refined. Specifically, for $b=1,2,3,4$ we have $D_{\text{prod}}(Q_{\text{prod}}) \approx \frac{1.57}{d}, \frac{0.56}{d}, \frac{0.18}{d}, \frac{0.047}{d}$, respectively.

**中文翻譯：**

**內積 TurboQuant。** 我們表明，MSE 優化的量化器對於內積估計是有偏的，因此需要不同的 VQ 方案來獲得無偏的內積量化器。我們的解決方案是一個兩階段演算法，首先應用上述 $Q_{\text{mse}}$（位元寬度比我們的目標預算少 1），然後對殘差誤差應用 QJL [62]。這被證明是無偏的，並且也具有接近最佳的內積誤差率。

在 ?? 中，我們證明了 $b$ 位元內積優化的 TurboQuant $Q_{\text{prod}}:\mathbb{R}^d \to \{0,1\}^{b\cdot d}$ 對於任何最壞情況向量 $\mathbf{x},\mathbf{y}\in\mathbb{R}^d$（其中 $\|\mathbf{x}\|=1$）實現以下失真：

• $\mathbb{E}[\langle\mathbf{y},Q_{\text{prod}}^{-1}(Q_{\text{prod}}(\mathbf{x}))\rangle]=\langle\mathbf{y},\mathbf{x}\rangle$

• $D_{\text{prod}}(Q_{\text{prod}}):=\mathbb{E}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},Q_{\text{prod}}^{-1}(Q_{\text{prod}}(\mathbf{x}))\rangle|^2] \leq \frac{3\pi}{2}\cdot\frac{\|\mathbf{y}\|^2}{d}\cdot\frac{1}{4^b}$ 對於任何 $b\geq 0$。

• 對於小位元寬度，上述失真上界可以進一步細化。具體來說，對於 $b=1,2,3,4$，我們分別有 $D_{\text{prod}}(Q_{\text{prod}}) \approx \frac{1.57}{d}, \frac{0.56}{d}, \frac{0.18}{d}, \frac{0.047}{d}$。

---

**原文：**

**Lower Bound.** In ??, we leverage Shannon's lower bound and Yao's minimax principle to prove that for any randomized quantization algorithm $Q:\mathbb{R}^d \to \{0,1\}^{b\cdot d}$ with bit-width $b$, there exist hard input instances $\mathbf{x},\mathbf{y}\in\mathbb{R}^d$ with $\|\mathbf{x}\|=1$ such that the following lower bounds hold:

• $D_{\text{mse}}(Q):=\mathbb{E}[\|\mathbf{x}-Q^{-1}(Q(\mathbf{x}))\|_2^2] \geq \frac{1}{4^b}$

• $D_{\text{prod}}(Q)=\mathbb{E}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},Q^{-1}(Q(\mathbf{x}))\rangle|^2] \geq \frac{\|\mathbf{y}\|^2}{d}\cdot\frac{1}{4^b}$

As demonstrated by our lower bounds, TurboQuant's MSE distortion is provably within a factor of at most $\frac{3\pi}{2} \approx 2.7$ of the information-theoretical lower bound. Notably, for smaller bit-widths, this factor significantly decreases. For instance, at a bit-width of $b=1$ TurboQuant achieves a distortion that is only a factor of approximately $1.45$ away from the optimal which is also confirmed by our experimental results, indicating its efficiency in low-bit-width scenarios.

**中文翻譯：**

**下界。** 在 ?? 中，我們利用香農下界和 Yao 的 minimax 原理來證明，對於任何具有位元寬度 $b$ 的隨機量化演算法 $Q:\mathbb{R}^d \to \{0,1\}^{b\cdot d}$，存在困難的輸入實例 $\mathbf{x},\mathbf{y}\in\mathbb{R}^d$（其中 $\|\mathbf{x}\|=1$），使得以下下界成立：

• $D_{\text{mse}}(Q):=\mathbb{E}[\|\mathbf{x}-Q^{-1}(Q(\mathbf{x}))\|_2^2] \geq \frac{1}{4^b}$

• $D_{\text{prod}}(Q)=\mathbb{E}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},Q^{-1}(Q(\mathbf{x}))\rangle|^2] \geq \frac{\|\mathbf{y}\|^2}{d}\cdot\frac{1}{4^b}$

正如我們的下界所示，TurboQuant 的 MSE 失真被證明在資訊理論下界的 $\frac{3\pi}{2} \approx 2.7$ 因子內。值得注意的是，對於較小的位元寬度，這個因子顯著減少。例如，在位元寬度 $b=1$ 時，TurboQuant 實現的失真僅比最佳值大約 $1.45$ 倍，這也得到了我們的實驗結果的證實，表明其在低位元寬度場景中的效率。

---

**原文：**

**Experimental Results.** In ??, we empirically validate our theoretical distortion bounds, demonstrating that TurboQuant's observed distortions closely align with our predictions across various real-world datasets, approaching the established lower bounds.

Furthermore, in ?? and ??, we showcase TurboQuant's efficacy in online KV cache quantization. Specifically, we achieve perfect long-context retrieval in needle-in-a-haystack tasks and maintain high performance on other long-context downstream tasks, all while compressing the KV cache by a factor exceeding $5\times$.

Finally in ?? we apply TurboQuant to various high-dimensional near neighbor search tasks. TurboQuant consistently outperforms data-dependent product quantization (PQ), while reducing the indexing time to essentially zero.

**中文翻譯：**

**實驗結果。** 在 ?? 中，我們經驗性地驗證了我們的理論失真界限，表明 TurboQuant 的觀察失真在各種真實世界數據集上與我們的預測密切一致，接近已建立的下界。

此外，在 ?? 和 ?? 中，我們展示了 TurboQuant 在線上 KV 快取量化中的有效性。具體來說，我們在「大海撈針」任務中實現了完美的長上下文檢索，並在其他長上下文下游任務中保持高性能，同時將 KV 快取壓縮超過 $5\times$ 倍。

最後，在 ?? 中，我們將 TurboQuant 應用於各種高維最近鄰搜尋任務。TurboQuant 始終優於數據依賴的乘積量化（PQ），同時將索引時間減少到幾乎為零。

---

## 2 Preliminaries（預備知識）

**原文：**

We use boldface lowercase letters, such as $\mathbf{x}$ and $\mathbf{y}$, to denote vectors, and boldface uppercase letters, like $\mathbf{M}$, to denote matrices. To denote a slice of a vector $\mathbf{x}$ between the coordinate indices $i$ and $j$ inclusive of the endpoints, we use the notation $\mathbf{x}_{i:j}$. For a matrix $\mathbf{M}$, we write $\mathbf{M}_{i,:}$ to denote its $i$-th row vector, which we will simply refer to as $\mathbf{M}_i$.

We use the notation $\mathbb{S}^{d-1}$ to denote the hypersphere in $\mathbb{R}^d$ of radius $1$. For a random variable $x$ we denote its differential entropy as $h(x)$. For random variables $x$ and $y$, the mutual information between them is denoted as $I(x;y)=h(x)-h(x|y)$.

**中文翻譯：**

我們使用粗體小寫字母（如 $\mathbf{x}$ 和 $\mathbf{y}$）表示向量，使用粗體大寫字母（如 $\mathbf{M}$）表示矩陣。為了表示向量 $\mathbf{x}$ 在座標索引 $i$ 和 $j$ 之間（包括端點）的切片，我們使用符號 $\mathbf{x}_{i:j}$。對於矩陣 $\mathbf{M}$，我們寫 $\mathbf{M}_{i,:}$ 表示其第 $i$ 個行向量，我們將其簡單地稱為 $\mathbf{M}_i$。

我們使用符號 $\mathbb{S}^{d-1}$ 表示 $\mathbb{R}^d$ 中半徑為 $1$ 的超球面。對於隨機變量 $x$，我們將其微分熵表示為 $h(x)$。對於隨機變量 $x$ 和 $y$，它們之間的互資訊表示為 $I(x;y)=h(x)-h(x|y)$。

---

**原文：**

Given that TurboQuant employs random rotation to mitigate worst-case input scenarios, understanding the statistical properties of random points on a hypersphere is essential. The following lemma outlines one such property that we will need for analysis and design purposes:

**Lemma 1** (coordinate distribution of random point on hypersphere). For any positive integer $d$ if $\mathbf{x}\in\mathbb{S}^{d-1}$ is a random variable uniformly distributed over the unit hypersphere, then for any $j\in[d]$ the coordinate $\mathbf{x}_j$ follows the following (scaled/shifted) [Beta distribution](03-beta-distribution.md):

$$
\mathbf{x}_j \sim f_X(x) := \frac{\Gamma(d/2)}{\sqrt{\pi}\cdot\Gamma((d-1)/2)}(1-x^2)^{(d-3)/2}.
$$

In high dimensions this [beta distribution](03-beta-distribution.md) converges to the normal distribution $f_X(\cdot) \to \mathcal{N}(0,1/d)$.

**中文翻譯：**

鑑於 TurboQuant 採用隨機旋轉來緩解最壞情況的輸入場景，了解超球面上隨機點的統計屬性至關重要。以下引理概述了一個我們將用於分析和設計目的的此類屬性：

**引理 1**（超球面上隨機點的座標分佈）。對於任何正整數 $d$，如果 $\mathbf{x}\in\mathbb{S}^{d-1}$ 是在單位超球面上均勻分佈的隨機變量，那麼對於任何 $j\in[d]$，座標 $\mathbf{x}_j$ 遵循以下（縮放/平移的）[Beta 分佈](03-beta-distribution.md)：

$$
\mathbf{x}_j \sim f_X(x) := \frac{\Gamma(d/2)}{\sqrt{\pi}\cdot\Gamma((d-1)/2)}(1-x^2)^{(d-3)/2}.
$$

在高維度中，這個 [Beta 分佈](03-beta-distribution.md) 收斂於常態分佈 $f_X(\cdot) \to \mathcal{N}(0,1/d)$。

---

**原文：**

**Proof.** $f_X(x)$ equals the ratio of the area of a sphere with radius $\sqrt{1-x^2}$ in dimension $d-1$ to the volume of a unit sphere in dimension $d$ scaled down by $1/\sqrt{1-x^2}$ (by Pythagorean theorem). Therefore,

$$
f_X(x) = \frac{\frac{2\pi^{(d-1)/2}}{\Gamma((d-1)/2)}\cdot(1-x^2)^{(d-2)/2}}{\frac{2\pi^{d/2}}{\Gamma(d/2)}\cdot 1/\sqrt{1-x^2}} = \frac{\Gamma(d/2)}{\sqrt{\pi}\cdot\Gamma((d-1)/2)}(1-x^2)^{(d-3)/2}.
$$

∎

**中文翻譯：**

**證明。** $f_X(x)$ 等於 $d-1$ 維中半徑為 $\sqrt{1-x^2}$ 的球體面積與 $d$ 維中單位球體體積的比率，並按比例縮小 $1/\sqrt{1-x^2}$（根據畢達哥拉斯定理）。因此，

$$
f_X(x) = \frac{\frac{2\pi^{(d-1)/2}}{\Gamma((d-1)/2)}\cdot(1-x^2)^{(d-2)/2}}{\frac{2\pi^{d/2}}{\Gamma(d/2)}\cdot 1/\sqrt{1-x^2}} = \frac{\Gamma(d/2)}{\sqrt{\pi}\cdot\Gamma((d-1)/2)}(1-x^2)^{(d-3)/2}.
$$

∎

---

### 2.1 Shannon Lower Bound on Distortion（失真的香農下界）

**原文：**

The Shannon Lower Bound (SLB) is a powerful tool, derived from Shannon's lossy source coding theorem [49], that provides a universal lower bound on the optimal achievable distortion rate for any lossy compression scheme. Specifically, we use a version of SLB tailored for the mean-squared error (MSE) distortion measure applied to general $d$-dimensional sources.

**Lemma 2** (SLB). Let $\mathbf{x}\in\mathbb{R}^d$ be a random vector with an arbitrary probability distribution $p_X$ and finite differential entropy $h(\mathbf{x})$. Define the MSE distortion-rate function $D(B)$ for total bit complexity $B\geq 0$ as:

$$
D(p_X,B) := \inf\{\mathbb{E}[\|\mathbf{x}-\mathbf{y}\|_2^2] : I(\mathbf{x};\mathbf{y}) \leq B\},
$$

where the infimum is taken over all joint distributions of $\mathbf{x}$ and a reconstruction random vector $\mathbf{y}\in\mathbb{R}^d$ such that the mutual information $I(\mathbf{x};\mathbf{y})$ is at most $B$ and $\mathbb{E}[\|\mathbf{x}-\mathbf{y}\|_2^2]$ is the expected MSE distortion, calculated with respect to the joint distribution of $\mathbf{x}$ and $\mathbf{y}$. Then, for any bit complexity $B\geq 0$, the following Shannon Lower Bound holds:

$$
D(p_X,B) \geq \frac{d}{2\pi e}\cdot 2^{(2/d)(h(\mathbf{x})-B)}.
$$

This is a classic result proved using backward Gaussian test channel (for a proof see [14]). Our lower bound result uses a corollary of SLB that corresponds to the uniformly distributed random points on the unit hypersphere. We present this in the following lemma:

**中文翻譯：**

香農下界（SLB）是一個強大的工具，源自香農的有損信源編碼定理 [49]，為任何有損壓縮方案提供了最佳可達失真率的通用下界。具體來說，我們使用一個針對應用於一般 $d$ 維信源的均方誤差（MSE）失真度量定制的 SLB 版本。

**引理 2**（SLB）。設 $\mathbf{x}\in\mathbb{R}^d$ 是一個具有任意機率分佈 $p_X$ 和有限微分熵 $h(\mathbf{x})$ 的隨機向量。定義總位元複雜度 $B\geq 0$ 的 MSE 失真 - 率函數 $D(B)$ 為：

$$
D(p_X,B) := \inf\{\mathbb{E}[\|\mathbf{x}-\mathbf{y}\|_2^2] : I(\mathbf{x};\mathbf{y}) \leq B\},
$$

其中下確界是在 $\mathbf{x}$ 和重建隨機向量 $\mathbf{y}\in\mathbb{R}^d$ 的所有聯合分佈上取得的，使得互資訊 $I(\mathbf{x};\mathbf{y})$ 至多為 $B$，且 $\mathbb{E}[\|\mathbf{x}-\mathbf{y}\|_2^2]$ 是相對於 $\mathbf{x}$ 和 $\mathbf{y}$ 的聯合分佈計算的期望 MSE 失真。那麼，對於任何位元複雜度 $B\geq 0$，以下香農下界成立：

$$
D(p_X,B) \geq \frac{d}{2\pi e}\cdot 2^{(2/d)(h(\mathbf{x})-B)}.
$$

這是一個使用反向高斯測試信道證明的經典結果（證明見 [14]）。我們的下界結果使用了 SLB 的推論，該推論對應於單位超球面上均勻分佈的隨機點。我們在以下引理中呈現這一點：

---

**原文：**

**Lemma 3** (SLB for random point on hypersphere). Let $\mathbf{x}\in\mathbb{S}^{d-1}$ be a random variable uniformly distributed over the unit hypersphere and define the MSE distortion-rate function $D(B)$ for total bit complexity $B$ as per ??. Then, for any bit complexity $B\geq 0$, the following distortion lower bound holds:

$$
D(B) \geq 2^{-2B/d}.
$$

**Proof.** If we let $A_d$ denote the area of the hypersphere $\mathbb{S}^{d-1}$, the entropy of uniform distribution over hypersphere is $h(\mathbf{x})=\log_2 A_d$. Plugging this into the SLB from ?? we get $D(B) \geq \frac{d}{2\pi e}\cdot A_d^{2/d}\cdot 2^{-2B/d}$. Using Stirling's approximation formula for Gamma function we have $A_d = \frac{2\pi^{d/2}}{\Gamma(d/2)} \geq (\frac{2\pi e}{d})^{d/2}\cdot\sqrt{\frac{d}{\pi}}\cdot(1-O(1/d))$. By substituting this into the inequality obtained from ?? we get the desired lower bound. ∎

**中文翻譯：**

**引理 3**（超球面上隨機點的 SLB）。設 $\mathbf{x}\in\mathbb{S}^{d-1}$ 是在單位超球面上均勻分佈的隨機變量，並根據 ?? 定義總位元複雜度 $B$ 的 MSE 失真 - 率函數 $D(B)$。那麼，對於任何位元複雜度 $B\geq 0$，以下失真下界成立：

$$
D(B) \geq 2^{-2B/d}.
$$

**證明。** 如果我們讓 $A_d$ 表示超球面 $\mathbb{S}^{d-1}$ 的面積，則超球面上均勻分佈的熵為 $h(\mathbf{x})=\log_2 A_d$。將其代入 ?? 中的 SLB，我們得到 $D(B) \geq \frac{d}{2\pi e}\cdot A_d^{2/d}\cdot 2^{-2B/d}$。使用 Gamma 函數的 Stirling 近似公式，我們有 $A_d = \frac{2\pi^{d/2}}{\Gamma(d/2)} \geq (\frac{2\pi e}{d})^{d/2}\cdot\sqrt{\frac{d}{\pi}}\cdot(1-O(1/d))$。透過將此代入從 ?? 獲得的不等式，我們得到所需的下界。∎

---

### 2.2 QJL: 1-bit inner product quantization（QJL：1 位元內積量化）

**原文：**

As previously stated, we design two VQ algorithms: one optimized for minimizing MSE and the other for minimizing inner product error. We show that MSE-optimal quantizers do not necessarily provide unbiased inner product estimates, particularly exhibiting significant bias at lower bit-widths. Our solution for inner product quantization is a two-stage algorithm. First, we apply the MSE-optimal quantizer using one less bit than the desired bit-width budget, thus minimizing the L2 norm of the residuals. Next we apply an unbiased and optimal single-bit quantizer to the residual. For the single-bit inner product quantizer, we utilize the recently proposed Quantized Johnson-Lindenstrauss (QJL) algorithm [62], which is an optimal inner product quantizer with a bit-width of one. Here, we present the QJL algorithm and its essential theoretical guarantees.

**中文翻譯：**

如前所述，我們設計了兩種 VQ 演算法：一種針對最小化 MSE 進行優化，另一種針對最小化內積誤差進行優化。我們表明，MSE 最佳量化器不一定提供無偏的內積估計，特別是在較低位元寬度下表現出顯著偏差。我們對於內積量化的解決方案是一個兩階段演算法。首先，我們應用 MSE 最佳量化器，使用比期望位元寬度預算少 1 位的位元，從而最小化殘差的 L2 範數。接下來，我們對殘差應用無偏且最佳的單位元量化器。對於單位元內積量化器，我們利用最近提出的量化 Johnson-Lindenstrauss（QJL）演算法 [62]，這是一個位元寬度為 1 的最佳內積量化器。在這裡，我們介紹 QJL 演算法及其基本的理論保證。

---

**原文：**

**Definition 1** (QJL). For any positive integer $d$ the QJL map $Q_{\text{qjl}}:\mathbb{R}^d \to \{-1,+1\}^d$ is defined as:

$$
Q_{\text{qjl}}(\mathbf{x}) := \text{sign}(\mathbf{S}\cdot\mathbf{x}) \text{ for any } \mathbf{x}\in\mathbb{R}^d,
$$

where $\mathbf{S}\in\mathbb{R}^{d\times d}$ is a random matrix with i.i.d. entries sampled from the normal distribution $\mathcal{N}(0,1)$ and the $\text{sign}$ function is applied entry-wise to its vector input. The inverse/dequantization map $Q_{\text{qjl}}^{-1}:\{-1,+1\}^d \to \mathbb{R}^d$ is defined as:

$$
Q_{\text{qjl}}^{-1}(\mathbf{z}) := \sqrt{\pi/2d}\cdot\mathbf{S}^\top\cdot\mathbf{z} \text{ for any } \mathbf{z}\in\{-1,+1\}^d.
$$

**中文翻譯：**

**定義 1**（QJL）。對於任何正整數 $d$，QJL 映射 $Q_{\text{qjl}}:\mathbb{R}^d \to \{-1,+1\}^d$ 定義為：

$$
Q_{\text{qjl}}(\mathbf{x}) := \text{sign}(\mathbf{S}\cdot\mathbf{x}) \text{ 對於任何 } \mathbf{x}\in\mathbb{R}^d,
$$

其中 $\mathbf{S}\in\mathbb{R}^{d\times d}$ 是一個隨機矩陣，其元素是從常��分佈 $\mathcal{N}(0,1)$ 中獨立同分佈採樣的，並且 $\text{sign}$ 函數逐元素應用於其向量輸入。逆/反量化映射 $Q_{\text{qjl}}^{-1}:\{-1,+1\}^d \to \mathbb{R}^d$ 定義為：

$$
Q_{\text{qjl}}^{-1}(\mathbf{z}) := \sqrt{\pi/2d}\cdot\mathbf{S}^\top\cdot\mathbf{z} \text{ 對於任何 } \mathbf{z}\in\{-1,+1\}^d.
$$

---

**原文：**

In the next lemma we restate the results from [62] that show the QJL is unbiased and also has small inner product distortion:

**Lemma 4** (performance guarantee: QJL). Let $Q_{\text{qjl}}$ and $Q_{\text{qjl}}^{-1}$ be defined as per ??. For any vector $\mathbf{x}\in\mathbb{S}^{d-1}$ and any $\mathbf{y}\in\mathbb{R}^d$ we have the following:

• **Unbiased:** $\mathbb{E}[\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{x}))\rangle]=\langle\mathbf{y},\mathbf{x}\rangle$.

• **Variance Bound:** $\text{Var}(\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{x}))\rangle) \leq \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2$

**中文翻譯：**

在下一個引理中，我們重述 [62] 中的結果，表明 QJL 是無偏的並且也具有小的內積失真：

**引理 4**（性能保證：QJL）。設 $Q_{\text{qjl}}$ 和 $Q_{\text{qjl}}^{-1}$ 根據 ?? 定義。對於任何向量 $\mathbf{x}\in\mathbb{S}^{d-1}$ 和任何 $\mathbf{y}\in\mathbb{R}^d$，我們有以下結果：

• **無偏性：** $\mathbb{E}[\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{x}))\rangle]=\langle\mathbf{y},\mathbf{x}\rangle$。

• **變異數界限：** $\text{Var}(\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{x}))\rangle) \leq \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2$

---

**原文：**

**Proof.** The unbiasedness immediately follows from Lemma 3.2 of [62]. To show the variance bound let $\mathbf{s}_1,\mathbf{s}_2,\ldots \mathbf{s}_m$ denote the rows of the random matrix $\mathbf{S}$ in ??. We have:

$$
\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{x}))\rangle = \frac{1}{d}\sum_{i\in[d]}\sqrt{\pi/2}\cdot\mathbf{s}_i^\top\mathbf{y}\cdot\text{sign}(\mathbf{s}_i^\top\mathbf{x}).
$$

Since $\mathbf{s}_i$'s are i.i.d. the above is indeed the average of $d$ i.i.d. random samples defined as $z_i := \sqrt{\pi/2}\cdot\mathbf{s}_i^\top\mathbf{y}\cdot\text{sign}(\mathbf{s}_i^\top\mathbf{x})$ for $i\in[d]$. Let us now upper bound the variance of a single $z_i$ using Fact 3.4 from [62]:

$$
\text{Var}(z_i) = \sqrt{\pi/2}\cdot\text{Var}(\mathbf{s}_i^\top\mathbf{y}\cdot\text{sign}(\mathbf{s}_i^\top\mathbf{x})) \leq \sqrt{\pi/2}\cdot\mathbb{E}[(\mathbf{s}_i^\top\mathbf{y})^2] = \sqrt{\pi/2}\cdot\|\mathbf{y}\|_2^2, \tag{3}
$$

where the last equality above follows because $\mathbf{s}_i^\top\mathbf{y}$ is a Gaussian random variable with mean zero and variance $\|\mathbf{y}\|_2^2$. Now the variance of the average of $d$ i.i.d. random samples $z_1,z_2,\ldots z_d$ is:

$$
\text{Var}(\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{x}))\rangle) = \frac{1}{d^2}\sum_{i\in[d]}\text{Var}(z_i) \leq \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2.
$$

∎

**中文翻譯：**

**證明。** 無偏性直接來自 [62] 的引理 3.2。為了證明變異數界限，設 $\mathbf{s}_1,\mathbf{s}_2,\ldots \mathbf{s}_m$ 表示 ?? 中隨機矩陣 $\mathbf{S}$ 的行。我們有：

$$
\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{x}))\rangle = \frac{1}{d}\sum_{i\in[d]}\sqrt{\pi/2}\cdot\mathbf{s}_i^\top\mathbf{y}\cdot\text{sign}(\mathbf{s}_i^\top\mathbf{x}).
$$

由於 $\mathbf{s}_i$ 是獨立同分佈的，上述確實是 $d$ 個獨立同分佈隨機樣本的平均值，定義為 $z_i := \sqrt{\pi/2}\cdot\mathbf{s}_i^\top\mathbf{y}\cdot\text{sign}(\mathbf{s}_i^\top\mathbf{x})$（對於 $i\in[d]$）。現在我們使用 [62] 中的事實 3.4 來上限單個 $z_i$ 的變異數：

$$
\text{Var}(z_i) = \sqrt{\pi/2}\cdot\text{Var}(\mathbf{s}_i^\top\mathbf{y}\cdot\text{sign}(\mathbf{s}_i^\top\mathbf{x})) \leq \sqrt{\pi/2}\cdot\mathbb{E}[(\mathbf{s}_i^\top\mathbf{y})^2] = \sqrt{\pi/2}\cdot\|\mathbf{y}\|_2^2, \tag{3}
$$

其中上述最後一個等式成立是因為 $\mathbf{s}_i^\top\mathbf{y}$ 是一個均值為零、變異數為 $\|\mathbf{y}\|_2^2$ 的高斯隨機變量。現在 $d$ 個獨立同分佈隨機樣本 $z_1,z_2,\ldots z_d$ 的平均值的變異數為：

$$
\text{Var}(\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{x}))\rangle) = \frac{1}{d^2}\sum_{i\in[d]}\text{Var}(z_i) \leq \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2.
$$

∎

---

## 3 TurboQuant: High Performance Quantization（TurboQuant：高性能量化）

**原文：**

We developed two VQ algorithms, each tailored to a specific objective. The first algorithm is designed to minimize the MSE between the original and reconstructed vectors after quantization. The second algorithm is optimized for unbiased inner product estimation, addressing the bias inherent in MSE-optimal quantizers. These algorithms are detailed in the following subsections.

Furthermore, in ??, we establish information-theoretic lower bounds on the best achievable distortion rates for any vector quantizer. This analysis demonstrates that TurboQuant achieve near-optimality, differing from the lower bound by only a small constant factor across all bit-widths.

**中文翻譯：**

我們開發了兩種 VQ 演算法，每種都針對特定目標量身定制。第一種演算法旨在最小化量化後原始向量與重建向量之間的 MSE。第二種演算法針對無偏內積估計進行優化，解決了 MSE 最佳量化器中固有的偏差問題。這些演算法在以下小節中詳細說明。

此外，在 ?? 中，我們建立了任何向量量化器可達到的最佳失真率的資訊理論下界。該分析表明，TurboQuant 實現了接近最佳性，在所有位元寬度上與下界僅相差一個小常數因子。

---

### 3.1 MSE Optimal TurboQuant（MSE 最佳 TurboQuant）

**原文：**

Let $\mathbf{x}\in\mathbb{S}^{d-1}$ be a (worst-case) vector on the unit sphere in dimension $d$. We aim to quantize $\mathbf{x}$ to $b$ bits per coordinate while minimizing the reconstruction MSE defined in ??. We start by randomizing this vector by multiplying it with a random rotation matrix $\mathbf{\Pi}\in\mathbb{R}^{d\times d}$. We can generate $\mathbf{\Pi}$ by applying QR decomposition on a random matrix with i.i.d Normal entries.

The resulting rotated vector, $\mathbf{\Pi}\cdot\mathbf{x}$, is uniformly distributed on the unit sphere $\mathbb{S}^{d-1}$. As shown in ??, each coordinate of $\mathbf{\Pi}\cdot\mathbf{x}$ follows a [Beta distribution](03-beta-distribution.md), which converges to a normal distribution in high dimensions. Furthermore, in high dimensions, distinct coordinates of $\mathbf{\Pi}\cdot\mathbf{x}$ become nearly independent [55], allowing us to apply optimal scalar quantizers to each coordinate independently. Therefore, by ??, our task reduces to designing a scalar quantizer for random variables with the distribution $f_X(x) = \frac{\Gamma(d/2)}{\sqrt{\pi}\cdot\Gamma((d-1)/2)}(1-x^2)^{(d-3)/2}$ for $x\in[-1,1]$.

**中文翻譯：**

設 $\mathbf{x}\in\mathbb{S}^{d-1}$ 是 $d$ 維單位球面上的（最壞情況）向量。我們的目標是將 $\mathbf{x}$ 量化為每個座標 $b$ 位元，同時最小化 ?? 中定義的重建 MSE。我們首先透過將該向量與隨機旋轉矩陣 $\mathbf{\Pi}\in\mathbb{R}^{d\times d}$ 相乘來隨機化該向量。我們可以透過對具有獨立同分佈常態項的隨機矩陣應用 QR 分解來生成 $\mathbf{\Pi}$。

產生的旋轉向量 $\mathbf{\Pi}\cdot\mathbf{x}$ 在單位球面 $\mathbb{S}^{d-1}$ 上均勻分佈。如 ?? 所示，$\mathbf{\Pi}\cdot\mathbf{x}$ 的每個座標遵循 [Beta 分佈](03-beta-distribution.md)，該分佈在高維度中收斂於常態分佈。此外，在高維度中，$\mathbf{\Pi}\cdot\mathbf{x}$ 的不同座標變得幾乎獨立 [55]，使我們能夠獨立地對每個座標應用最佳純量量化器。因此，根據 ??，我們的任務簡化為為具有分佈 $f_X(x) = \frac{\Gamma(d/2)}{\sqrt{\pi}\cdot\Gamma((d-1)/2)}(1-x^2)^{(d-3)/2}$（其中 $x\in[-1,1]$）的隨機變量設計純量量化器。

---

**原文：**

The optimal scalar quantization problem, given a known probability distribution, can be framed as a continuous k-means problem in dimension one. Specifically, we aim to partition the interval $[-1,1]$ into $2^b$ clusters/buckets. The optimal solution adheres to a Voronoi tessellation [42], meaning interval boundaries are the midpoints between consecutive centroids, when arranged in sorted order. Therefore, with $c_i$'s denoting the centroids in ascending order, we can formulate the scalar quantization as the following k-means optimization problem:

$$
\mathcal{C}(f_X,b) := \min_{-1\leq c_1\leq c_2\leq\ldots\leq c_{2^b}\leq 1} \sum_{i=1}^{2^b} \int_{\frac{c_{i-1}+c_i}{2}}^{\frac{c_i+c_{i+1}}{2}} |x-c_i|^2\cdot f_X(x)dx. \tag{4}
$$

Note that $\mathcal{C}(f_X,b)$ in ?? denotes the optimal MSE cost function for bit-width $b$, a quantity we will bound to prove the upper bound on the end-to-end MSE of TurboQuant. The problem in ?? can be solved using iterative numerical methods to achieve any desired precision. We solve ?? for a range of practically relevant bit-widths $b$ once, and store the results for future uses by the quantizer.

**中文翻譯：**

給定已知機率分佈的最佳純量量化問題可以框定為一維連續 k-means 問題。具體來說，我們的目標是將區間 $[-1,1]$ 劃分為 $2^b$ 個簇/桶。最佳解遵循 Voronoi 鑲嵌 [42]，這意味著當按排序順序排列時，區間邊界是連續質心之間的中點。因此，用 $c_i$ 表示按升序排列的質心，我們可以將純量量化公式化為以下 k-means 優化問題：

$$
\mathcal{C}(f_X,b) := \min_{-1\leq c_1\leq c_2\leq\ldots\leq c_{2^b}\leq 1} \sum_{i=1}^{2^b} \int_{\frac{c_{i-1}+c_i}{2}}^{\frac{c_i+c_{i+1}}{2}} |x-c_i|^2\cdot f_X(x)dx. \tag{4}
$$

請注意，?? 中的 $\mathcal{C}(f_X,b)$ 表示位元寬度 $b$ 的最佳 MSE 成本函數，我們將限制這個量來證明 TurboQuant 端到端 MSE 的上界。?? 中的問題可以使用迭代數值方法求解，以達到任何期望的精度。我們一次性求解一系列實際相關的位元寬度 $b$ 的 ??，並存儲結果以備量化器將來使用。

---

**原文：**

For example, in moderately high dimensions $d$, where the distribution $f_X(x)$ closely approximates a normal distribution, the optimal quantization centroids for bit-widths $b=1,2$ are $\{\pm\sqrt{2/\pi d}\}$ and $\{\pm\frac{0.453}{\sqrt{d}}, \pm\frac{1.51}{\sqrt{d}}\}$, respectively.

Therefore the quantizer $Q_{\text{mse}}:\mathbb{R}^d \to \{0,1\}^{b\cdot d}$ first computes $\mathbf{\Pi}\cdot\mathbf{x}$ and then computes and stores the indices of the nearest centroids to each coordinate of this vector. The dequantization map $Q_{\text{mse}}^{-1}:\{0,1\}^{b\cdot d} \to \mathbb{R}^d$ reconstructs the vector by retrieving the centroids corresponding to the stored indices and then rotating the result back to the original basis through multiplication with $\mathbf{\Pi}^\top$. A pseudocode for these procedures is given in ??.

**中文翻譯：**

例如，在中等高維度 $d$ 中，分佈 $f_X(x)$ 密切近似於常態分佈，位元寬度 $b=1,2$ 的最佳量化質心分別是 $\{\pm\sqrt{2/\pi d}\}$ 和 $\{\pm\frac{0.453}{\sqrt{d}}, \pm\frac{1.51}{\sqrt{d}}\}$。

因此，量化器 $Q_{\text{mse}}:\mathbb{R}^d \to \{0,1\}^{b\cdot d}$ 首先計算 $\mathbf{\Pi}\cdot\mathbf{x}$，然後計算並存儲該向量每個座標的最近質心的索引。反量化映射 $Q_{\text{mse}}^{-1}:\{0,1\}^{b\cdot d} \to \mathbb{R}^d$ 透過檢索對應於存儲索引的質心，然後透過與 $\mathbf{\Pi}^\top$ 相乘將結果旋轉回原始基底來重建向量。這些過程的偽代碼見 ??。

---

**原文：**

**Algorithm 1** $\text{TurboQuant}_{\text{mse}}$: optimized for MSE

1: **input:** dimension $d$ and bit-width $b$ // Global Parameters for Setting up $\text{TurboQuant}_{\text{mse}}$

2: Generate a random rotation matrix $\mathbf{\Pi}\in\mathbb{R}^{d\times d}$

3: Construct codebook by finding centroids $c_1,c_2,\ldots c_{2^b}\in[-1,1]$ that minimize MSE cost in ??

4: **Procedure** $\text{Quant}_{\text{mse}}(\mathbf{x})$

5: $\mathbf{y} \leftarrow \mathbf{\Pi}\cdot\mathbf{x}$

6: $\text{idx}_j \leftarrow \arg\min_{k\in[2^b]} |\mathbf{y}_j-c_k|$ for every $j\in[d]$ { $\text{idx}_j$'s are $b$-bit integers}

7: **output:** $\text{idx}$

8: **Procedure** $\text{DeQuant}_{\text{mse}}(\text{idx})$

9: $\tilde{\mathbf{y}}_j \leftarrow c_{\text{idx}_j}$ for every $j\in[d]$

10: $\tilde{\mathbf{x}} \leftarrow \mathbf{\Pi}^\top\cdot\tilde{\mathbf{y}}$

11: **output:** $\tilde{\mathbf{x}}$

**中文翻譯：**

**演算法 1** $\text{TurboQuant}_{\text{mse}}$：針對 MSE 優化

1: **輸入：** 維度 $d$ 和位元寬度 $b$ // 設置 $\text{TurboQuant}_{\text{mse}}$ 的全域參數

2: 生成隨機旋轉矩陣 $\mathbf{\Pi}\in\mathbb{R}^{d\times d}$

3: 透過找到最小化 ?? 中 MSE 成本的質心 $c_1,c_2,\ldots c_{2^b}\in[-1,1]$ 來構建碼本

4: **過程** $\text{Quant}_{\text{mse}}(\mathbf{x})$

5: $\mathbf{y} \leftarrow \mathbf{\Pi}\cdot\mathbf{x}$

6: $\text{idx}_j \leftarrow \arg\min_{k\in[2^b]} |\mathbf{y}_j-c_k|$ 對於每個 $j\in[d]$ { $\text{idx}_j$ 是 $b$ 位元整數}

7: **輸出：** $\text{idx}$

8: **過程** $\text{DeQuant}_{\text{mse}}(\text{idx})$

9: $\tilde{\mathbf{y}}_j \leftarrow c_{\text{idx}_j}$ 對於每個 $j\in[d]$

10: $\tilde{\mathbf{x}} \leftarrow \mathbf{\Pi}^\top\cdot\tilde{\mathbf{y}}$

11: **輸出：** $\tilde{\mathbf{x}}$

---

**原文：**

We are now ready to prove our main theorem for $\text{TurboQuant}_{\text{mse}}$.

**Theorem 1** (performance guarantee: $\text{TurboQuant}_{\text{mse}}$). For any bit-width $b\geq 1$ and any vector $\mathbf{x}\in\mathbb{S}^{d-1}$, the procedure $\text{Quant}_{\text{mse}}(\mathbf{x})$ in ?? outputs an index vector $\text{idx}\in[2^b]^d$. When this index vector is passed to the primitive $\text{DeQuant}_{\text{mse}}(\text{idx})$, it produces a reconstructed vector $\tilde{\mathbf{x}}\in\mathbb{R}^d$ that satisfies the following distortion bounds:

• MSE defined as $D_{\text{mse}}:=\mathbb{E}_{\tilde{\mathbf{x}}}[\|\mathbf{x}-\tilde{\mathbf{x}}\|_2^2]$ is bounded by $D_{\text{mse}} \leq \frac{3\pi}{2}\cdot\frac{1}{4^b}$ for any $b\geq 0$.

• For small bit-widths, specifically $b=1,2,3,4$ the MSE exhibits finer-grained distortion values: $D_{\text{mse}} \approx 0.36, 0.117, 0.03, 0.009$, respectively.

**中文翻譯：**

我們現在準備證明我們關於 $\text{TurboQuant}_{\text{mse}}$ 的主要定理。

**定理 1**（性能保證：$\text{TurboQuant}_{\text{mse}}$）。對於任何位元寬度 $b\geq 1$ 和任何向量 $\mathbf{x}\in\mathbb{S}^{d-1}$，?? 中的過程 $\text{Quant}_{\text{mse}}(\mathbf{x})$ 輸出一個索引向量 $\text{idx}\in[2^b]^d$。當這個索引向量傳遞給基本操作 $\text{DeQuant}_{\text{mse}}(\text{idx})$ 時，它產生一個重建向量 $\tilde{\mathbf{x}}\in\mathbb{R}^d$，滿足以下失真界限：

• MSE 定義為 $D_{\text{mse}}:=\mathbb{E}_{\tilde{\mathbf{x}}}[\|\mathbf{x}-\tilde{\mathbf{x}}\|_2^2]$，對於任何 $b\geq 0$，有 $D_{\text{mse}} \leq \frac{3\pi}{2}\cdot\frac{1}{4^b}$。

• 對於小位元寬度，特別是 $b=1,2,3,4$，MSE 呈現更精細的失真值：$D_{\text{mse}} \approx 0.36, 0.117, 0.03, 0.009$。

---

**原文：**

**Proof.** We start the proof by showing that $D_{\text{mse}} = d\cdot\mathcal{C}(f_X,b)$, where $\mathcal{C}(f_X,b)$ is the optimal MSE cost for scalar quantizer defined in ??. Let $\tilde{\mathbf{y}}$ be defined as per line 9 of ??. Since $\mathbf{\Pi}$ is a rotation matrix we can write: $\|\mathbf{x}-\tilde{\mathbf{x}}\|_2 = \|\mathbf{\Pi}\cdot\mathbf{x}-\tilde{\mathbf{y}}\|_2$. Using the notation $\mathbf{y}=\mathbf{\Pi}\cdot\mathbf{x}$ as per line 5 of ?? and plugging this into the definition of $D_{\text{mse}}$ we can write:

$$
\begin{aligned}
D_{\text{mse}} &= \mathbb{E}[\|\mathbf{y}-\tilde{\mathbf{y}}\|_2^2] \\
&= \sum_{j\in[d]}\mathbb{E}[|\mathbf{y}_j-\tilde{\mathbf{y}}_j|^2] \\
&= \sum_{j\in[d]}\mathbb{E}[|\mathbf{y}_j-c_{\text{idx}_j}|^2] \\
&= d\cdot\mathbb{E}[|\mathbf{y}_1-c_{\text{idx}_1}|^2] \\
&= d\cdot\min_{-1\leq c_1\leq c_2\leq\ldots\leq c_{2^b}\leq 1} \sum_{i=1}^{2^b} \int_{\frac{c_{i-1}+c_i}{2}}^{\frac{c_i+c_{i+1}}{2}} |x-c_i|^2\cdot f_X(x)dx \\
&= d\cdot\mathcal{C}(f_X,b).
\end{aligned}
$$

The third equality above follows from the definition of $\tilde{\mathbf{y}}$ in line 9 of ?? and the fourth line above follows because all $\mathbf{y}_j$'s have identical distribution of $\mathbf{y}_j \sim f_X(\cdot)$ as shown in ??. The last two lines above follows because $c_{\text{idx}_j}$ is chosen to be the nearest centroid to each coordinate $\mathbf{y}_j$ in line 6.

**中文翻譯：**

**證明。** 我們首先證明 $D_{\text{mse}} = d\cdot\mathcal{C}(f_X,b)$，其中 $\mathcal{C}(f_X,b)$ 是 ?? 中定義的純量量化器的最佳 MSE 成本。設 $\tilde{\mathbf{y}}$ 根據 ?? 的第 9 行定義。由於 $\mathbf{\Pi}$ 是旋轉矩陣，我們可以寫：$\|\mathbf{x}-\tilde{\mathbf{x}}\|_2 = \|\mathbf{\Pi}\cdot\mathbf{x}-\tilde{\mathbf{y}}\|_2$。使用 ?? 第 5 行中的符號 $\mathbf{y}=\mathbf{\Pi}\cdot\mathbf{x}$ 並將其代入 $D_{\text{mse}}$ 的定義，我們可以寫：

$$
\begin{aligned}
D_{\text{mse}} &= \mathbb{E}[\|\mathbf{y}-\tilde{\mathbf{y}}\|_2^2] \\
&= \sum_{j\in[d]}\mathbb{E}[|\mathbf{y}_j-\tilde{\mathbf{y}}_j|^2] \\
&= \sum_{j\in[d]}\mathbb{E}[|\mathbf{y}_j-c_{\text{idx}_j}|^2] \\
&= d\cdot\mathbb{E}[|\mathbf{y}_1-c_{\text{idx}_1}|^2] \\
&= d\cdot\min_{-1\leq c_1\leq c_2\leq\ldots\leq c_{2^b}\leq 1} \sum_{i=1}^{2^b} \int_{\frac{c_{i-1}+c_i}{2}}^{\frac{c_i+c_{i+1}}{2}} |x-c_i|^2\cdot f_X(x)dx \\
&= d\cdot\mathcal{C}(f_X,b).
\end{aligned}
$$

上述第三個等式來自 ?? 第 9 行中 $\tilde{\mathbf{y}}$ 的定義，上述第四行成立是因為所有 $\mathbf{y}_j$ 具有相同的分佈 $\mathbf{y}_j \sim f_X(\cdot)$，如 ?? 所示。上述最後兩行成立是因為 $c_{\text{idx}_j}$ 在第 6 行中被選擇為每個座標 $\mathbf{y}_j$ 的最近質心。

---

**原文：**

Now we must bound the optimal k-means cost $\mathcal{C}(f_X,b)$. For moderate values of $d$, $f_X \to \mathcal{N}(0,1/d)$. By numerically solving the optimization problem in ?? for values $b=1,2,3,4$ we get that $\mathcal{C}(f_X,b) \approx \frac{0.36}{d}, \frac{0.117}{d}, \frac{0.03}{d}, \frac{0.009}{d}$, respectively. For larger bit-widths $b>4$, we can apply the Panter-Dite [44] high-resolution formula for the distortion of a fixed-rate scalar quantizer, yielding the following bound:

$$
\mathcal{C}(f_X,b) \leq \frac{1}{12}\cdot(\int f_X(x)^{1/3}dx)^3\cdot\frac{1}{4^b} = \frac{3\pi}{2d}\cdot\frac{1}{4^b}.
$$

This completes the proof. ∎

**中文翻譯：**

現在我們必須限制最佳 k-means 成本 $\mathcal{C}(f_X,b)$。對於適中的 $d$ 值，$f_X \to \mathcal{N}(0,1/d)$。透過數值求解 ?? 中的優化問題（對於值 $b=1,2,3,4$），我們分別得到 $\mathcal{C}(f_X,b) \approx \frac{0.36}{d}, \frac{0.117}{d}, \frac{0.03}{d}, \frac{0.009}{d}$。對於較大的位元寬度 $b>4$，我們可以應用 Panter-Dite [44] 高解析度公式來計算固定碼率純量量化器的失真，得出以下界限：

$$
\mathcal{C}(f_X,b) \leq \frac{1}{12}\cdot(\int f_X(x)^{1/3}dx)^3\cdot\frac{1}{4^b} = \frac{3\pi}{2d}\cdot\frac{1}{4^b}.
$$

這完成了證明。∎

---

**原文：**

**Entropy Encoding Codebook Pointers.** TurboQuant's efficiency can be further increased by applying entropy encoding to the indices that point to the closest codebook elements. Specifically, the probability of each codeword index appearing in the quantized vectors can be computed as $p_\ell := \int_{\frac{c_{\ell-1}+c_\ell}{2}}^{\frac{c_\ell+c_{\ell+1}}{2}} f_X(x)dx$. Optimally coding the indices, reduces the average bit-width to nearly the entropy of the distribution $\{p_i\}_{i\in[2^b]}$. This lossless compression does not affect the distortion and provides a bit-width reduction at no cost. The most significant reduction occurs for $b=4$, where the entropy of $\{p_i\}_{i\in[2^b]}$ is approximately $3.8$. Detailed calculations for optimal prefix codes reveal that the average bit-width can be reduced by $5\%$. However, given the limited gain, we have chosen not to incorporate this technique into TurboQuant to maintain simplicity and speed.

**中文翻譯：**

**熵編碼碼本指針。** TurboQuant 的效率可以透過對指向最近碼本元素的索引應用熵編碼來進一步提高。具體來說，每個碼字索引在量化向量中出現的機率可以計算為 $p_\ell := \int_{\frac{c_{\ell-1}+c_\ell}{2}}^{\frac{c_\ell+c_{\ell+1}}{2}} f_X(x)dx$。最佳地編碼索引，將平均位元寬度減少到接近分佈 $\{p_i\}_{i\in[2^b]}$ 的熵。這種無損壓縮不影響失真，並提供無成本的位元寬度減少。最顯著的減少發生在 $b=4$ 時，其中 $\{p_i\}_{i\in[2^b]}$ 的熵約為 $3.8$。最佳前綴碼的詳細計算表明，平均位元寬度可以減少 $5\%$。然而，鑑於增益有限，我們選擇不將此技術納入 TurboQuant，以保持簡單性和速度。

---

### 3.2 Inner-product Optimal TurboQuant（內積最佳 TurboQuant）

**原文：**

For important applications like nearest neighbor search, having an unbiased inner product estimator is essential. However, $\text{TurboQuant}_{\text{mse}}$ presented in ?? does not provide unbiased inner product estimates with query vectors. To illustrate this, consider the case with a bit-width of $b=1$. In this scenario, the optimal codebooks that solve the optimization problem in ??, for sufficiently large $d$, are $\{\pm\sqrt{\frac{2}{\pi d}}\}$. This implies that the quantization map for $\text{TurboQuant}_{\text{mse}}$ is $Q_{\text{mse}}(\mathbf{x})=\text{sign}(\mathbf{\Pi}\cdot\mathbf{x})$ for any $\mathbf{x}\in\mathbb{R}^d$, and the dequantization map is $Q_{\text{mse}}^{-1}(\mathbf{z})=\sqrt{\frac{2}{\pi d}}\cdot\mathbf{\Pi}^\top\cdot\mathbf{z}$ for any $\mathbf{z}\in\{-1,+1\}^d$. Therefore, for large enough $d$, according to ??, we have $\mathbb{E}[\langle\mathbf{y},Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))\rangle] = \sqrt{\frac{2}{\pi}}\cdot\langle\mathbf{y},\mathbf{x}\rangle$, which has a multiplicative bias of $\sqrt{2/\pi}$. This bias diminishes with increasing bit-widths $b$, as we empirically demonstrate in ??.

**中文翻譯：**

對於像最近鄰搜尋這樣的重要應用，擁有無偏內積估計器至關重要。然而，?? 中提出的 $\text{TurboQuant}_{\text{mse}}$ 不提供與查詢向量的無偏內積估計。為了說明這一點，考慮位元寬度 $b=1$ 的情況。在這種場景下，對於足夠大的 $d$，解決 ?? 中優化問題的最佳碼本是 $\{\pm\sqrt{\frac{2}{\pi d}}\}$。這意味著 $\text{TurboQuant}_{\text{mse}}$ 的量化映射是 $Q_{\text{mse}}(\mathbf{x})=\text{sign}(\mathbf{\Pi}\cdot\mathbf{x})$（對於任何 $\mathbf{x}\in\mathbb{R}^d$），反量化映射是 $Q_{\text{mse}}^{-1}(\mathbf{z})=\sqrt{\frac{2}{\pi d}}\cdot\mathbf{\Pi}^\top\cdot\mathbf{z}$（對於任何 $\mathbf{z}\in\{-1,+1\}^d$）。因此，對於足夠大的 $d$，根據 ??，我們有 $\mathbb{E}[\langle\mathbf{y},Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))\rangle] = \sqrt{\frac{2}{\pi}}\cdot\langle\mathbf{y},\mathbf{x}\rangle$，這具有 $\sqrt{2/\pi}$ 的乘法偏差。正如我們在 ?? 中經驗性地證明的那樣，這種偏差隨著位元寬度 $b$ 的增加而減少。

---

**原文：**

To address this bias, we propose a solution that combines $\text{TurboQuant}_{\text{mse}}$ with an instance of QJL [62]. Specifically, let $Q_{\text{mse}}$ be the quantization map corresponding to $\text{TurboQuant}_{\text{mse}}$ with a bit-width of $b-1$. For any $\mathbf{x}\in\mathbb{S}^{d-1}$ the residual vector, defined as $\mathbf{r} := \mathbf{x} - Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))$, has a small L2 norm, i.e., on expectation $\mathbb{E}[\|\mathbf{r}\|] = \mathcal{C}(f_X,b-1)$ (per ??). We can then apply the QJL quantization map $Q_{\text{qjl}}$ on this residual vector, resulting in an overall bit-width of $b$ and providing the following unbiased inner product estimator:

$$
\langle\mathbf{y},Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))\rangle + \|\mathbf{r}\|_2\cdot\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{r}))\rangle.
$$

**中文翻譯：**

為了解決這個偏差，我們提出了一種將 $\text{TurboQuant}_{\text{mse}}$ 與 QJL [62] 實例相結合的解決方案。具體來說，設 $Q_{\text{mse}}$ 是對應於位元寬度為 $b-1$ 的 $\text{TurboQuant}_{\text{mse}}$ 的量化映射。對於任何 $\mathbf{x}\in\mathbb{S}^{d-1}$，殘差向量定義為 $\mathbf{r} := \mathbf{x} - Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))$，具有小的 L2 範數，即期望上 $\mathbb{E}[\|\mathbf{r}\|] = \mathcal{C}(f_X,b-1)$（根據 ??）。然後我們可以對這個殘差向量應用 QJL 量化映射 $Q_{\text{qjl}}$，從而產生總體位元寬度為 $b$，並提供以下無偏內積估計器：

$$
\langle\mathbf{y},Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))\rangle + \|\mathbf{r}\|_2\cdot\langle\mathbf{y},Q_{\text{qjl}}^{-1}(Q_{\text{qjl}}(\mathbf{r}))\rangle.
$$

---

**原文：**

More formally, the quantization map $Q_{\text{prod}}:\mathbb{S}^{d-1} \to [2^{b-1}]^d \times \{-1,1\}^d \times \mathbb{R}$ is defined as:

$$
Q_{\text{prod}}(\mathbf{x}) = [Q_{\text{mse}}(\mathbf{x}), Q_{\text{qjl}}(\mathbf{x}-Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))), \|\mathbf{x}-Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))\|_2].
$$

A pseudocode for this procedure is given in ??.

**中文翻譯：**

更正式地說，量化映射 $Q_{\text{prod}}:\mathbb{S}^{d-1} \to [2^{b-1}]^d \times \{-1,1\}^d \times \mathbb{R}$ 定義為：

$$
Q_{\text{prod}}(\mathbf{x}) = [Q_{\text{mse}}(\mathbf{x}), Q_{\text{qjl}}(\mathbf{x}-Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))), \|\mathbf{x}-Q_{\text{mse}}^{-1}(Q_{\text{mse}}(\mathbf{x}))\|_2].
$$

該過程的偽代碼見 ??。

---

**原文：**

**Algorithm 2** $\text{TurboQuant}_{\text{prod}}$: optimized for inner product

1: **input:** dimension $d$ and bit-width $b$ // Global Parameters for Setting up $\text{TurboQuant}_{\text{prod}}$

2: Instantiate a $\text{TurboQuant}_{\text{mse}}$ with bit-width $b-1$ as per ??

3: Generate a random projection matrix $\mathbf{S}\in\mathbb{R}^{d\times d}$ with i.i.d. entries $\mathbf{S}_{i,j} \sim \mathcal{N}(0,1)$

4: **Procedure** $\text{Quant}_{\text{prod}}(\mathbf{x})$

5: $\text{idx} \leftarrow \text{Quant}_{\text{mse}}(\mathbf{x})$

6: $\mathbf{r} \leftarrow \mathbf{x} - \text{DeQuant}_{\text{mse}}(\text{idx})$ { residual vector}

7: $\text{qjl} \leftarrow \text{sign}(\mathbf{S}\cdot\mathbf{r})$ { QJL on residual vector}

8: **output:** $(\text{idx}, \text{qjl}, \|r\|_2)$

9: **Procedure** $\text{DeQuant}_{\text{prod}}(\text{idx}, \text{qjl}, \gamma)$

10: $\tilde{\mathbf{x}}_{\text{mse}} \leftarrow \text{DeQuant}_{\text{mse}}(\text{idx})$

11: $\tilde{\mathbf{x}}_{\text{qjl}} \leftarrow \sqrt{\pi/2d}\cdot\gamma\cdot\mathbf{S}^\top\cdot\text{qjl}$

12: **output:** $\tilde{\mathbf{x}}_{\text{mse}} + \tilde{\mathbf{x}}_{\text{qjl}}$

**中文翻譯：**

**演算法 2** $\text{TurboQuant}_{\text{prod}}$：針對內積優化

1: **輸入：** 維度 $d$ 和位元寬度 $b$ // 設置 $\text{TurboQuant}_{\text{prod}}$ 的全域參數

2: 根據 ?? 實例化一個位元寬度為 $b-1$ 的 $\text{TurboQuant}_{\text{mse}}$

3: 生成隨機投影矩陣 $\mathbf{S}\in\mathbb{R}^{d\times d}$，其元素 $\mathbf{S}_{i,j} \sim \mathcal{N}(0,1)$ 獨立同分佈

4: **過程** $\text{Quant}_{\text{prod}}(\mathbf{x})$

5: $\text{idx} \leftarrow \text{Quant}_{\text{mse}}(\mathbf{x})$

6: $\mathbf{r} \leftarrow \mathbf{x} - \text{DeQuant}_{\text{mse}}(\text{idx})$ { 殘差向量}

7: $\text{qjl} \leftarrow \text{sign}(\mathbf{S}\cdot\mathbf{r})$ { 對殘差向量進行 QJL}

8: **輸出：** $(\text{idx}, \text{qjl}, \|r\|_2)$

9: **過程** $\text{DeQuant}_{\text{prod}}(\text{idx}, \text{qjl}, \gamma)$

10: $\tilde{\mathbf{x}}_{\text{mse}} \leftarrow \text{DeQuant}_{\text{mse}}(\text{idx})$

11: $\tilde{\mathbf{x}}_{\text{qjl}} \leftarrow \sqrt{\pi/2d}\cdot\gamma\cdot\mathbf{S}^\top\cdot\text{qjl}$

12: **輸出：** $\tilde{\mathbf{x}}_{\text{mse}} + \tilde{\mathbf{x}}_{\text{qjl}}$

---

**原文：**

We prove the main result for $\text{TurboQuant}_{\text{prod}}$ in the following theorem.

**Theorem 2** (performance guarantee: $\text{TurboQuant}_{\text{prod}}$). For any bit-width $b\geq 1$ and any vector $\mathbf{x}\in\mathbb{S}^{d-1}$, the procedure $\text{Quant}_{\text{prod}}(\mathbf{x})$ in ?? outputs an index vector $\text{idx}\in[2^{b-1}]^d$ along with a sign vector $\text{qjl}\in\{-1,1\}^d$ and a positive number $\gamma\geq 0$. When these vectors and the scalar value are passed to the primitive $\text{DeQuant}_{\text{prod}}(\text{idx}, \text{qjl}, \gamma)$, it produces a reconstructed vector $\tilde{\mathbf{x}}\in\mathbb{R}^d$ that for any vector $\mathbf{y}\in\mathbb{R}^d$ satisfies the following properties:

• Expected inner-product $\mathbb{E}_{\tilde{\mathbf{x}}}[\langle\mathbf{y},\tilde{\mathbf{x}}\rangle] = \langle\mathbf{y},\mathbf{x}\rangle$

• Inner-product distortion defined as $D_{\text{prod}}:=\mathbb{E}_{\tilde{\mathbf{x}}}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}\rangle|^2]$ is bounded by $D_{\text{prod}} \leq \frac{3\pi}{2}\cdot\frac{\|\mathbf{y}\|_2^2}{d}\cdot\frac{1}{4^b}$ for any $b\geq 0$.

• For small bit-widths, specifically $b=1,2,3,4$, $D_{\text{prod}}$ exhibits finer-grained distortion values: $D_{\text{prod}} \approx \frac{1.57}{d}, \frac{0.56}{d}, \frac{0.18}{d}, \frac{0.047}{d}$, respectively.

**中文翻譯：**

我們在下述定理中證明 $\text{TurboQuant}_{\text{prod}}$ 的主要結果。

**定理 2**（性能保證：$\text{TurboQuant}_{\text{prod}}$）。對於任何位元寬度 $b\geq 1$ 和任何向量 $\mathbf{x}\in\mathbb{S}^{d-1}$，?? 中的過程 $\text{Quant}_{\text{prod}}(\mathbf{x})$ 輸出一個索引向量 $\text{idx}\in[2^{b-1}]^d$ 以及一個符號向量 $\text{qjl}\in\{-1,1\}^d$ 和一個正數 $\gamma\geq 0$。當這些向量和純量值傳遞給基本操作 $\text{DeQuant}_{\text{prod}}(\text{idx}, \text{qjl}, \gamma)$ 時，它產生一個重建向量 $\tilde{\mathbf{x}}\in\mathbb{R}^d$，對於任何向量 $\mathbf{y}\in\mathbb{R}^d$ 滿足以下屬性：

• 期望內積 $\mathbb{E}_{\tilde{\mathbf{x}}}[\langle\mathbf{y},\tilde{\mathbf{x}}\rangle] = \langle\mathbf{y},\mathbf{x}\rangle$

• 內積失真定義為 $D_{\text{prod}}:=\mathbb{E}_{\tilde{\mathbf{x}}}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}\rangle|^2]$，對於任何 $b\geq 0$，有 $D_{\text{prod}} \leq \frac{3\pi}{2}\cdot\frac{\|\mathbf{y}\|_2^2}{d}\cdot\frac{1}{4^b}$。

• 對於小位元寬度，特別是 $b=1,2,3,4$，$D_{\text{prod}}$ 呈現更精細的失真值：$D_{\text{prod}} \approx \frac{1.57}{d}, \frac{0.56}{d}, \frac{0.18}{d}, \frac{0.047}{d}$。

---

**原文：**

**Proof.** First we compute the conditional expectation of the inner product estimate $\langle\mathbf{y},\tilde{\mathbf{x}}\rangle$ conditioned on $\tilde{\mathbf{x}}_{\text{mse}}$ as follows:

$$
\begin{aligned}
\mathbb{E}[\langle\mathbf{y},\tilde{\mathbf{x}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}] &= \mathbb{E}_{\tilde{\mathbf{x}}_{\text{qjl}}}[\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{mse}}+\tilde{\mathbf{x}}_{\text{qjl}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}] \\
&= \langle\mathbf{y},\tilde{\mathbf{x}}_{\text{mse}}\rangle + \mathbb{E}_{\tilde{\mathbf{x}}_{\text{qjl}}}[\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{qjl}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}] \\
&= \langle\mathbf{y},\tilde{\mathbf{x}}_{\text{mse}}\rangle + \langle\mathbf{y},\mathbf{r}\rangle \\
&= \langle\mathbf{y},\mathbf{x}\rangle,
\end{aligned}
$$

where the first equality follows from the definition of $\tilde{\mathbf{x}}$ in line 12 of the algorithm. The third equality above follows from ?? and last line follows from definition of the residual vector $\mathbf{r}=\mathbf{x}-\tilde{\mathbf{x}}_{\text{mse}}$ in line 6. Now we can computed the unconditional expectation using the law of total expectation: $\mathbb{E}_{\tilde{\mathbf{x}}}[\langle\mathbf{y},\tilde{\mathbf{x}}\rangle] = \mathbb{E}_{\tilde{\mathbf{x}}_{\text{mse}}}[\mathbb{E}[\langle\mathbf{y},\tilde{\mathbf{x}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}]] = \mathbb{E}[\langle\mathbf{y},\mathbf{x}\rangle] = \langle\mathbf{y},\mathbf{x}\rangle$, which proves the first claim of the theorem.

**中文翻譯：**

**證明。** 首先我們計算內積估計 $\langle\mathbf{y},\tilde{\mathbf{x}}\rangle$ 在條件 $\tilde{\mathbf{x}}_{\text{mse}}$ 下的條件期望，如下所示：

$$
\begin{aligned}
\mathbb{E}[\langle\mathbf{y},\tilde{\mathbf{x}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}] &= \mathbb{E}_{\tilde{\mathbf{x}}_{\text{qjl}}}[\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{mse}}+\tilde{\mathbf{x}}_{\text{qjl}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}] \\
&= \langle\mathbf{y},\tilde{\mathbf{x}}_{\text{mse}}\rangle + \mathbb{E}_{\tilde{\mathbf{x}}_{\text{qjl}}}[\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{qjl}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}] \\
&= \langle\mathbf{y},\tilde{\mathbf{x}}_{\text{mse}}\rangle + \langle\mathbf{y},\mathbf{r}\rangle \\
&= \langle\mathbf{y},\mathbf{x}\rangle,
\end{aligned}
$$

其中第一個等式來自演算法第 12 行中 $\tilde{\mathbf{x}}$ 的定義。上述第三個等式來自 ??，最後一行來自第 6 行中殘差向量 $\mathbf{r}=\mathbf{x}-\tilde{\mathbf{x}}_{\text{mse}}$ 的定義。現在我們可以使用全期望定律計算無條件期望：$\mathbb{E}_{\tilde{\mathbf{x}}}[\langle\mathbf{y},\tilde{\mathbf{x}}\rangle] = \mathbb{E}_{\tilde{\mathbf{x}}_{\text{mse}}}[\mathbb{E}[\langle\mathbf{y},\tilde{\mathbf{x}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}]] = \mathbb{E}[\langle\mathbf{y},\mathbf{x}\rangle] = \langle\mathbf{y},\mathbf{x}\rangle$，這證明了定理的第一個主張。

---

**原文：**

We apply the same conditioning on $\tilde{\mathbf{x}}_{\text{mse}}$, when computing the distortion, and then compute the resulting conditional distortion:

$$
\begin{aligned}
\mathbb{E}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}\rangle|^2 | \tilde{\mathbf{x}}_{\text{mse}}] &= \mathbb{E}_{\tilde{\mathbf{x}}_{\text{qjl}}}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{mse}}+\tilde{\mathbf{x}}_{\text{qjl}}\rangle|^2 | \tilde{\mathbf{x}}_{\text{mse}}] \\
&= \mathbb{E}_{\tilde{\mathbf{x}}_{\text{qjl}}}[|\langle\mathbf{y},\mathbf{r}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{qjl}}\rangle|^2 | \tilde{\mathbf{x}}_{\text{mse}}] \\
&= \text{Var}(\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{qjl}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}) \\
&\leq \frac{\pi}{2d}\cdot\|\mathbf{r}\|_2^2\|\mathbf{y}\|_2^2,
\end{aligned}
$$

where the second equality above follows from the definitions of $\mathbf{r}$ and $\tilde{\mathbf{x}}_{\text{mse}}$ in lines 6 and 10 of ??. The third line above follows because $\mathbb{E}[\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{qjl}}\rangle] = \langle\mathbf{y},\mathbf{r}\rangle$, by ??. The last line follows from the variance bound of QJL estimator shown in ?? and using the fact that $\tilde{\mathbf{x}}_{\text{qjl}}$ in line 11 is re-scaled by $\gamma=\|\mathbf{r}\|$.

**中文翻譯：**

我們在計算失真時對 $\tilde{\mathbf{x}}_{\text{mse}}$ 應用相同的條件，然後計算產生的條件失真：

$$
\begin{aligned}
\mathbb{E}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}\rangle|^2 | \tilde{\mathbf{x}}_{\text{mse}}] &= \mathbb{E}_{\tilde{\mathbf{x}}_{\text{qjl}}}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{mse}}+\tilde{\mathbf{x}}_{\text{qjl}}\rangle|^2 | \tilde{\mathbf{x}}_{\text{mse}}] \\
&= \mathbb{E}_{\tilde{\mathbf{x}}_{\text{qjl}}}[|\langle\mathbf{y},\mathbf{r}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{qjl}}\rangle|^2 | \tilde{\mathbf{x}}_{\text{mse}}] \\
&= \text{Var}(\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{qjl}}\rangle | \tilde{\mathbf{x}}_{\text{mse}}) \\
&\leq \frac{\pi}{2d}\cdot\|\mathbf{r}\|_2^2\|\mathbf{y}\|_2^2,
\end{aligned}
$$

其中上述第二個等式來自 ?? 第 6 行和第 10 行中 $\mathbf{r}$ 和 $\tilde{\mathbf{x}}_{\text{mse}}$ 的定義。上述第三行成立是因為根據 ??，$\mathbb{E}[\langle\mathbf{y},\tilde{\mathbf{x}}_{\text{qjl}}\rangle] = \langle\mathbf{y},\mathbf{r}\rangle$。最後一行來自 ?? 中顯示的 QJL 估計器的變異數界限，並使用第 11 行中 $\tilde{\mathbf{x}}_{\text{qjl}}$ 被 $\gamma=\|\mathbf{r}\|$ 重新縮放的事實。

---

**原文：**

Now by law of total expectation along with the fact that $\mathbf{r}=\mathbf{x}-\tilde{\mathbf{x}}_{\text{mse}}$ we can bound the inner product distortion as follows:

$$
\begin{aligned}
D_{\text{prod}} &= \mathbb{E}_{\tilde{\mathbf{x}}_{\text{mse}}}[\mathbb{E}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}\rangle|^2 | \tilde{\mathbf{x}}_{\text{mse}}]] \\
&\leq \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2\cdot\mathbb{E}[\|\mathbf{x}-\tilde{\mathbf{x}}_{\text{mse}}\|_2^2] \\
&= \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2\cdot D_{\text{mse}}.
\end{aligned}
$$

The theorem follows by invoking the MSE bounds from ?? with bit-width $b-1$. ∎

**中文翻譯：**

現在透過全期望定律以及 $\mathbf{r}=\mathbf{x}-\tilde{\mathbf{x}}_{\text{mse}}$ 的事實，我們可以限制內積失真如下：

$$
\begin{aligned}
D_{\text{prod}} &= \mathbb{E}_{\tilde{\mathbf{x}}_{\text{mse}}}[\mathbb{E}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},\tilde{\mathbf{x}}\rangle|^2 | \tilde{\mathbf{x}}_{\text{mse}}]] \\
&\leq \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2\cdot\mathbb{E}[\|\mathbf{x}-\tilde{\mathbf{x}}_{\text{mse}}\|_2^2] \\
&= \frac{\pi}{2d}\cdot\|\mathbf{y}\|_2^2\cdot D_{\text{mse}}.
\end{aligned}
$$

透過引用 ?? 中位元寬度為 $b-1$ 的 MSE 界限，定理得證。∎

---

### 3.3 Lower Bounds（下界）

**原文：**

We show that TurboQuant achieves an optimal distortion rate, up to a small constant factor, for any bit-width by proving lower bounds on the best achievable distortion for any compression algorithm. Our lower bound proof leverages Yao's minimax principle. This principle allows us to relate the lower bound for randomized algorithms with worst-case deterministic input vectors to the lower bound for deterministic algorithms with randomized input vectors. Subsequently, we derive a lower bound on the achievable distortion rate for the latter using Shannon's lower bound (SLB) presented in ??. Formally, we prove the following theorem.

**中文翻譯：**

我們透過證明任何壓縮演算法可達到的最佳失真的下界，表明 TurboQuant 對於任何位元寬度實現了最佳失真率（最多相差一個小常數因子）。我們的下界證明利用了 Yao 的 minimax 原理。這個原理允許我們將具有最壞情況確定性輸入向量的隨機演算法的下界與具有隨機輸入向量的確定性演算法的下界聯繫起來。隨後，我們使用 ?? 中提出的香農下界（SLB）推導出後者可達到的失真率的下界。形式上，我們證明以下定理。

---

**原文：**

**Theorem 3** (lower bound on best achievable compression distortion). For any randomized quantization algorithm $Q:\mathbb{S}^{d-1} \to \{0,1\}^{b\cdot d}$ with bit-width $b$ and any reconstruction map $Q^{-1}:\{0,1\}^{b\cdot d} \to \mathbb{R}^d$, there exist a hard input instance $\mathbf{x}\in\mathbb{S}^{d-1}$ such that:

$$
D_{\text{mse}}(Q) := \mathbb{E}[\|\mathbf{x}-Q^{-1}(Q(\mathbf{x}))\|_2^2] \geq \frac{1}{4^b}.
$$

Furthermore, there exists a $\mathbf{y}\in\mathbb{S}^{d-1}$ such that:

$$
D_{\text{prod}}(Q) = \mathbb{E}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},Q^{-1}(Q(\mathbf{x}))\rangle|^2] \geq \frac{1}{d}\cdot\frac{1}{4^b}
$$

**中文翻譯：**

**定理 3**（最佳可達壓縮失真的下界）。對於任何具有位元寬度 $b$ 的隨機量化演算法 $Q:\mathbb{S}^{d-1} \to \{0,1\}^{b\cdot d}$ 和任何重建映射 $Q^{-1}:\{0,1\}^{b\cdot d} \to \mathbb{R}^d$，存在一個困難的輸入實例 $\mathbf{x}\in\mathbb{S}^{d-1}$ 使得：

$$
D_{\text{mse}}(Q) := \mathbb{E}[\|\mathbf{x}-Q^{-1}(Q(\mathbf{x}))\|_2^2] \geq \frac{1}{4^b}.
$$

此外，存在一個 $\mathbf{y}\in\mathbb{S}^{d-1}$ 使得：

$$
D_{\text{prod}}(Q) = \mathbb{E}[|\langle\mathbf{y},\mathbf{x}\rangle-\langle\mathbf{y},Q^{-1}(Q(\mathbf{x}))\rangle|^2] \geq \frac{1}{d}\cdot\frac{1}{4^b}
$$

---

**原文：**

**Proof.** By Yao's minimax principle the expected MSE of the optimal randomized compression algorithm for worst-case inputs ($D_{\text{mse}}$) is equal to the expected MSE of the optimal deterministic compression algorithm when applied to inputs drawn from a maximally difficult randomized distribution. By definition, the MSE of the latter scenario is lower-bounded by the best achievable MSE for inputs uniformly distributed on the unit hypersphere.

The best achievable MSE for a compression algorithm with bit-width $b$, operating on uniformly distributed inputs from the sphere $\mathbb{S}^{d-1}$, is lower bounded in ??. Therefore, by invoking ?? we conclude that $D_{\text{mse}} \geq \frac{1}{4^b}$.

**中文翻譯：**

**證明。** 根據 Yao 的 minimax 原理，對於最壞情況輸入的最佳隨機壓縮演算法的期望 MSE（$D_{\text{mse}}$）等於當應用於從最困難的隨機分佈中抽取的輸入時的最佳確定性壓縮演算法的期望 MSE。根據定義，後者場景的 MSE 下界是對於單位超球面上均勻分佈的輸入可達到的最佳 MSE。

對於具有位元寬度 $b$ 的壓縮演算法，在來自球面 $\mathbb{S}^{d-1}$ 的均勻分佈輸入上操作，可達到的最佳 MSE 在 ?? 中有下界。因此，透過引用 ??，我們得出結論 $D_{\text{mse}} \geq \frac{1}{4^b}$。

---

**原文：**

Furthermore, from $D_{\text{mse}} \geq \frac{1}{4^b}$ and using the definition of $D_{\text{mse}}$ we conclude that:

$$
\begin{aligned}
D_{\text{mse}} &= \sum_{j=1}^{d}\mathbb{E}[|\mathbf{x}_j-[Q^{-1}(Q(\mathbf{x}))]_j|^2] \\
&= \sum_{j=1}^{d}\mathbb{E}[|\langle\mathbf{e}_j,\mathbf{x}\rangle-\langle\mathbf{e}_j,Q^{-1}(Q(\mathbf{x}))\rangle|^2] \\
&\geq \frac{1}{4^b}.
\end{aligned}
$$

By pigeonhole principle there exist an index $j\in[d]$ such that $\mathbb{E}[|\langle\mathbf{e}_j,\mathbf{x}\rangle-\langle\mathbf{e}_j,Q^{-1}(Q(\mathbf{x}))\rangle|^2] \geq \frac{1}{d}\cdot\frac{1}{4^b}$, which completes the proof. ∎

**中文翻譯：**

此外，從 $D_{\text{mse}} \geq \frac{1}{4^b}$ 並使用 $D_{\text{mse}}$ 的定義，我們得出結論：

$$
\begin{aligned}
D_{\text{mse}} &= \sum_{j=1}^{d}\mathbb{E}[|\mathbf{x}_j-[Q^{-1}(Q(\mathbf{x}))]_j|^2] \\
&= \sum_{j=1}^{d}\mathbb{E}[|\langle\mathbf{e}_j,\mathbf{x}\rangle-\langle\mathbf{e}_j,Q^{-1}(Q(\mathbf{x}))\rangle|^2] \\
&\geq \frac{1}{4^b}.
\end{aligned}
$$

根據鴿巢原理，存在一個索引 $j\in[d]$ 使得 $\mathbb{E}[|\langle\mathbf{e}_j,\mathbf{x}\rangle-\langle\mathbf{e}_j,Q^{-1}(Q(\mathbf{x}))\rangle|^2] \geq \frac{1}{d}\cdot\frac{1}{4^b}$，這完成了證明。∎

---

**原文：**

We note that a comparable lower bound for the worst-case distortion in vector quantization can be derived using "sphere packing" arguments (indeed, with larger constants as this is a harder problem) [26]. However, ?? offers a more robust and relevant lower bound for our analysis. This is because it establishes a lower bound on the expected distortion, rather than the worst-case error, and aligns seamlessly with our upper bounds presented in ?? and ??.

**中文翻譯：**

我們注意到，可以使用「球體填充」論點推導出向量量化中最壞情況失真的可比下界（實際上，由於這是一個更難的問題，具有更大的常數）[26]。然而，?? 為我們的分析提供了一個更強健和相關的下界。這是因為它建立了期望失真的下界，而不是最壞情況誤差，並且與我們在 ?? 和 ?? 中提出的上界無縫對齊。

---

## 4 Experiments（實驗）

**原文：**

All experiments are performed using a single NVIDIA A100 GPU. The experimental section is divided into two parts: one to empirically validate the theoretical results, and another to evaluate the performance of our methods on downstream tasks, specifically KV cache quantization and nearest neighbor vector search.

**中文翻譯：**

所有實驗均使用單個 NVIDIA A100 GPU 執行。實驗部分分為兩部分：一部分是經驗性地驗證理論結果，另一部分是評估我們的方法在下游任務上的性能，特別是 KV 快取量化和最近鄰向量搜尋。

---

### 4.1 Empirical Validation（經驗驗證）

**原文：**

In this section, we verify the theoretical results established in previous sections. We conduct our experiments using the DBpedia Entities dataset, which has been encoded into a 1536-dimensional space using OpenAI3 embeddings. To perform our experiments, we randomly sample 100,000 data points from the dataset, denoted as training set, which serves as our primary dataset. Additionally, we extract 1,000 distinct entries, denoted as query set, to be used as query points.

We evaluate two quantization methods: $\text{TurboQuant}_{\text{prod}}$ and $\text{TurboQuant}_{\text{mse}}$. The method $\text{TurboQuant}_{\text{mse}}$ is designed to be optimized for estimating the mean squared error (MSE) between the quantized and original vectors. In contrast, $\text{TurboQuant}_{\text{prod}}$ is unbiased for estimating the inner product between the quantized and original vectors.

**中文翻譯：**

在本節中，我們驗證前面章節中建立的理論結果。我們使用 DBpedia Entities 數據集進行實驗，該數據集已使用 OpenAI3 嵌入編碼到 1536 維空間中。為了執行實驗，我們從數據集中隨機採樣 100,000 個數據點，記為訓練集，作為我們的主要數據集。此外，我們提取 1,000 個不同的條目，記為查詢集，用作查詢點。

我們評估兩種量化方法：$\text{TurboQuant}_{\text{prod}}$ 和 $\text{TurboQuant}_{\text{mse}}$。$\text{TurboQuant}_{\text{mse}}$ 方法旨在優化估計量化向量與原始向量之間的均方誤差（MSE）。相比之下，$\text{TurboQuant}_{\text{prod}}$ 對於估計量化向量與原始向量之間的內積是無偏的。

---

**原文：**

Both methods are applied to the task of inner product estimation by quantizing training set and analyzing the distortion in inner product calculations across different bit widths. As shown in ??, increasing the bit width reduces variance in both methods. However, when used for inner product estimation, $\text{TurboQuant}_{\text{mse}}$ introduces bias. This bias diminishes as the bit width increases and eventually converges to zero.

The experimental results, illustrated in ??, confirm that $\text{TurboQuant}_{\text{prod}}$ remains unbiased for inner product estimation across all bit widths, while $\text{TurboQuant}_{\text{mse}}$ gradually improves with increasing bit width.

**中文翻譯：**

兩種方法都應用於內積估計任務，透過量化訓練集並分析不同位元寬度下內積計算中的失真。如 ?? 所示，增加位元寬度可以減少兩種方法的變異數。然而，當用於內積估計時，$\text{TurboQuant}_{\text{mse}}$ 引入偏差。這種偏差隨著位元寬度的增加而減少，最終收斂於零。

?? 中說明的實驗結果證實，$\text{TurboQuant}_{\text{prod}}$ 在所有位元寬度下對於內積估計保持無偏，而 $\text{TurboQuant}_{\text{mse}}$ 隨著位元寬度的增加逐漸改善。

![Figure 1: TurboQuant_prod 和 TurboQuant_mse 在內積估計中的誤差分佈](https://arxiv.org/html/2504.19874v1/x1.png)

![Figure 2: TurboQuant_prod 的內積誤差變異數保持恆定，而 TurboQuant_mse 隨平均內積增加而增加（位元寬度 b=2）](https://arxiv.org/html/2504.19874v1/x2.png)

---

**原文：**

As observed in ??, when quantizing to 2 bits, the variance remains constant regardless of the inner product of the original vector in the $\text{TurboQuant}_{\text{prod}}$ approach. However, the same plot indicates that the bias in the $\text{TurboQuant}_{\text{mse}}$ approach is dependent on the average inner product. As the average inner product increases, the bias also increases.

**中文翻譯：**

如 ?? 中觀察到的那樣，當量化為 2 位元時，在 $\text{TurboQuant}_{\text{prod}}$ 方法中，變異數保持恆定，無論原始向量的內積如何。然而，相同的圖表明，$\text{TurboQuant}_{\text{mse}}$ 方法中的偏差依賴於平均內積。隨著平均內積的增加，偏差也增加。

---

**原文：**

Along with the histograms, we also plot ?? the average inner product error and MSE between the original and quantized vectors across different bit ratios. These plots are drawn alongside the upper and lower bounds established in our theoretical analysis. Our observations confirm that the results align with the theoretical predictions. Specifically, for inner product estimation, the $\text{TurboQuant}_{\text{prod}}$ approach performs better at lower bit ratios. However, as the bit count increases, $\text{TurboQuant}_{\text{mse}}$ reduces bias and ultimately achieves superior performance in inner product estimation.

**中文翻譯：**

除了直方圖之外，我們還在 ?? 中繪製了不同位元比率下原始向量與量化向量之間的平均內積誤差和 MSE。這些圖表與我們理論分析中建立的上界和下界一起繪製。我們的觀察證實，結果與理論預測一致。具體來說，對於內積估計，$\text{TurboQuant}_{\text{prod}}$ 方法在較低位元比率下表現更好。然而，隨著位元數量的增加，$\text{TurboQuant}_{\text{mse}}$ 減少偏差並最終在內積估計中實現優越的性能。

![Figure 3: 不同位元比率下內積誤差和 MSE 與理論界限的比較](https://arxiv.org/html/2504.19874v1/x3.png)

---

### 4.2 Needle-In-A-Haystack（大海撈針）

**原文：**

The "Needle-In-A-Haystack Test" [32] is a benchmark designed to evaluate a model's ability to retrieve specific information embedded within a long document. The test involves placing a unique sentence (the "needle") at an arbitrary location within a much larger text (the "haystack") and assessing whether the model can successfully extract it.

Following the experimental setup of Fu et al. [21], we conduct evaluations using the $\text{Llama-3.1-8B-Instruct}$ model. To analyze performance across different input sequence lengths, we vary the document size from 4k to 104k tokens. The primary metric used for evaluation is the recall score, which measures how accurately the model retrieves the hidden sentence.

For comparison, we benchmark our approach against several state-of-the-art memory-efficient methods, including PolarQuant [28], SnapKV [38], PyramidKV [12], and KIVI [41]. Each method is tested under a memory compression ratio of 0.25, meaning that only 25% of the full KV cache is utilized.

The results, illustrated in ??, reveal that quantization methods with theoretical guarantees, such as PolarQuant and TurboQuant, outperform token-level compression techniques like SnapKV and PyramidKV, as well as scalar quantization approaches like KIVI, which lack formal theoretical guarantees. Notably, TurboQuant achieves identical performance to the full-precision model, even at $4\times$ compression, making it a robust solution for long-context processing.

**中文翻譯：**

「大海撈針測試」[32] 是一個基準測試，旨在評估模型檢索嵌入長文件中的特定資訊的能力。該測試涉及將一個獨特的句子（「針」）放置在一個大得多的文本（「稻草堆」）中的任意位置，並評估模型是否可以成功提取它。

遵循 Fu 等人 [21] 的實驗設置，我們使用 $\text{Llama-3.1-8B-Instruct}$ 模型進行評估。為了分析不同輸入序列長度的性能，我們將文檔大小從 4k 變化到 104k tokens。用於評估的主要指標是召回分數，它衡量模型檢索隱藏句子的準確程度。

為了比較，我們將我們的方法與幾種最先進的記憶體高效方法進行基準測試，包括 PolarQuant [28]、SnapKV [38]、PyramidKV [12] 和 KIVI [41]。每種方法都在 0.25 的記憶體壓縮比下進行測試，這意味著只使用了完整 KV 快取的 25%。

?? 中說明的結果表明，具有理論保證的量化方法（如 PolarQuant 和 TurboQuant）優於 token 級壓縮技術（如 SnapKV 和 PyramidKV），以及缺乏正式理論保證的純量量化方法（如 KIVI）。值得注意的是，TurboQuant 即使在 $4\times$ 壓縮下也能實現與全精度模型相同的性能，使其成為長上下文處理的強健解決方案。

![Figure 4: Llama-3.1-8B-Instruct 在「大海撈針」測試上的評估結果](https://arxiv.org/html/2504.19874v1/x4.png)

---

### 4.3 End-to-end Generation on LongBench（LongBench 上的端到端生成）

**原文：**

We experiment with various KV cache compression algorithms on the LongBench dataset [10], which encompasses a broad range of long-text scenarios, including single- and multi-document question-answering, summarization, few-shot learning, synthetic tasks, and code completion. To ensure a balanced evaluation across different context lengths, we employ LongBench-E, a subset designed with a more uniform length distribution. This enables a fair assessment of each model's performance across varying context sizes, making it a more reliable benchmark for evaluating compression techniques.

We compare TurboQuant against the leading baseline methods introduced in ??, using both $\text{Llama-3.1-8B-Instruct}$ and $\text{Ministral-7B-Instruct}$. Unlike existing approaches such as KIVI and PolarQuant, which leave generated tokens unquantized, our method applies quantization even during the streaming generation process.

**中文翻譯：**

我們在 LongBench 數據集 [10] 上實驗各種 KV 快取壓縮演算法，該數據集涵蓋了廣泛的長文本場景，包括單文檔和多文檔問答、摘要、少樣本學習、合成任務和代碼完成。為了確保在不同上下文長度之間的平衡評估，我們使用 LongBench-E，這是一個設計具有更均勻長度分佈的子集。這使得能夠公平評估每個模型在不同上下文大小下的性能，使其成為評估壓縮技術的更可靠基準。

我們使用 $\text{Llama-3.1-8B-Instruct}$ 和 $\text{Ministral-7B-Instruct}$ 將 TurboQuant 與 ?? 中介紹的主要基準方法進行比較。與現有方法（如 KIVI 和 PolarQuant）不同，這些方法不對生成的 token 進行量化，而我們的方法甚至在流式生成過程中應用量化。

---

**原文：**

As shown in ??, our approach outperforms other methods for both $\text{Llama-3.1-8B-Instruct}$ and $\text{Ministral-7B-Instruct}$, achieving significantly higher average scores. We evaluate our method using 2.5-bit and 3.5-bit quantization during text generation. These non-integer bit precisions result from our strategy of splitting channels into outlier and non-outlier sets, and applying two independent instances of TurboQuant to each, allocating higher bit precision to outliers. This outlier treatment strategy is consistent with prior work [63, 51]. For example, in our 2.5-bit setup, 32 outlier channels are quantized at 3 bits, while the remaining 96 channels use 2 bits, leading to an effective bit precision of $(32\times 3+96\times 2)/128 = 2.5$. For 3.5-bit quantization, a different ratio of outliers and regular channels leads to a higher effective bit precision. Despite using fewer bits than competing techniques, TurboQuant maintains performance comparable to unquantized models. Remarkably, we achieve this while compressing quantized vectors by at least a factor of $4.5\times$.

**中文翻譯：**

如 ?? 所示，我們的方法在 $\text{Llama-3.1-8B-Instruct}$ 和 $\text{Ministral-7B-Instruct}$ 上都優於其他方法，實現了顯著更高的平均分數。我們使用 2.5 位元和 3.5 位元量化在文本生成過程中評估我們的方法。這些非整數位精度源於我們將通道分為異常值和非異常值集合的策略，並對每個集合應用兩個獨立的 TurboQuant 實例，為異常值分配更高的位精度。這種異常值處理策略與先前的工作 [63, 51] 一致。例如，在我們的 2.5 位元設置中，32 個異常通道以 3 位元量化，而剩餘的 96 個通道使用 2 位元，導致有效位精度為 $(32\times 3+96\times 2)/128 = 2.5$。對於 3.5 位元量化，異常值和常規通道的不同比率導致更高的有效位精度。儘管使用的位元少於競爭技術，TurboQuant 仍保持與未量化模型相當的性能。值得注意的是，我們在將量化向量壓縮至少 $4.5\times$ 倍的情況下實現了這一點。

---

### 4.4 Near Neighbour Search Experiments（最近鄰搜尋實驗）

**原文：**

In this section, we establish the strength of our proposed method, even in the context of near-neighbor search. We conduct our experiments using the DBpedia [53] Entities dataset, which has been encoded into 1536-dimensional and 3072-dimensional spaces using OpenAI3 embeddings. Additionally, we evaluate performance on a lower-dimensional dataset, utilizing the standard GloVe [45] embeddings. To construct our experimental setup, we randomly sample 100,000 data points from the dataset, denoted as training set, which serves as our primary training and evaluation set. Furthermore, we extract 1,000 distinct entries, denoted as query set, to be used as query points for datasets that do not explicitly provide a query set. For the GloVe dataset, we use a pre-existing query set consisting of 10,000 points.

We compare our method, TurboQuant, against two baseline quantization approaches: Product Quantization (PQ) and RabitQ [22]. To ensure a fair comparison, we quantize the dataset training set using all three methods and evaluate their performance based on recall ratio at top-k, denoted as 1@k. Specifically, this metric assesses how often the true top inner product result is captured within the top-k approximated results returned by each algorithm.

**中文翻譯：**

在本節中，我們確立了我們提出的方法的優勢，即使在最近鄰搜尋的背景下。我們使用 DBpedia [53] Entities 數據集進行實驗，該數據集已使用 OpenAI3 嵌入編碼到 1536 維和 3072 維空間中。此外，我們在較低維數據集上評估性能，使用標準的 GloVe [45] 嵌入。為了構建我們的實驗設置，我們從數據集中隨機採樣 100,000 個數據點，記為訓練集，作為我們的主要訓練和評估集。此外，我們提取 1,000 個不同的條目，記為查詢集，用作沒有明確提供查詢集的數據集的查詢點。對於 GloVe 數據集，我們使用由 10,000 個點組成的現有查詢集。

我們將我們的方法 TurboQuant 與兩種基準量化方法進行比較：乘積量化（PQ）和 RabitQ [22]。為了確保公平比較，我們使用所有三種方法對數據集訓練集進行量化，並根據 top-k 的召回率（記為 1@k）評估它們的性能。具體來說，這個指標評估每個演算法返回的 top-k 近似結果中捕获真實頂級內積結果的頻率。

---

**原文：**

**Product Quantization (PQ).** Product Quantization (PQ) relies on the k-means algorithm to construct codebooks, which require separate storage. As the number of bits increases, the size of the codebook grows exponentially, leading to additional storage overhead. In our experiments, we carefully tuned the parameters to match the bit allocation of other methods. The most efficient implementation, designed for rapid querying, employs AVX2 In-Register Lookup Tables (LUTs). Specifically, it uses LUT16 with (l = 16) codewords. However, we observed substantial quality degradation at this configuration. To achieve a balance between speed and accuracy, we opted for a version of PQ that uses LUT256, which contains 256 codewords. For 2-bit quantization, it groups 4 coordinates per lookup, while for 4-bit quantization, it groups 2 coordinates per lookup. Notably, since we use the same dataset for both training and evaluation, PQ benefits from an inherent advantage in this setup.

**中文翻譯：**

**乘積量化（PQ）。** 乘積量化（PQ）依賴 k-means 演算法來構建碼本，這需要單獨的存儲。隨著位元數量的增加，碼本的大小呈指數增長，導致額外的存儲開銷。在我們的實驗中，我們仔細調整參數以匹配其他方法的位元分配。為快速查詢設計的最有效實現採用 AVX2 暫存器內查找表（LUTs）。具體來說，它使用具有（l = 16）碼字的 LUT16。然而，我們在這種配置下觀察到顯著的品質下降。為了在速度和準確性之間取得平衡，我們選擇了使用 LUT256 的 PQ 版本，其中包含 256 個碼字。對於 2 位元量化，它每次查找分組 4 個座標，而對於 4 位元量化，它每次查找分組 2 個座標。值得注意的是，由於我們對訓練和評估使用相同的數據集，PQ 在這種設置中具有固有的優勢。

---

**原文：**

**RabitQ.** Unlike PQ, RabitQ lacks a fully vectorized implementation, making it impossible to leverage GPU acceleration. As a result, it runs significantly slower on CPU. Additionally, the method incurs extra computational overheads that we do not explicitly account for in the bit ratio comparisons. While RabitQ claims a certain bit ratio, in practice, it utilizes more bits than reported due to these inefficiencies.

Despite the advantages granted to the baseline methods, TurboQuant consistently outperforms both Product Quantization and RabitQ in terms of recall ratio across all experiments. This demonstrates the robustness and efficiency of our approach, making it a compelling alternative for high-dimensional quantization-based search tasks.

**中文翻譯：**

**RabitQ。** 與 PQ 不同，RabitQ 缺乏完全向量化的實現，使其無法利用 GPU 加速。因此，它在 CPU 上運行明顯较慢。此外，該方法產生了額外的計算開銷，我們在位元比率比較中沒有明確考慮這些開銷。雖然 RabitQ 宣稱具有一定的位元比率，但在實踐中，由於這些低效率，它使用的位元比報告的要多。

儘管基準方法獲得了優勢，TurboQuant 在所有實驗中始終在召回率方面優於乘積量化和 RabitQ。這證明了我們方法的強健性和效率，使其成為基於高維量化搜尋任務的引人注目的替代方案。

![Figure 5: 不同數據集和嵌入維度上的召回率比較](https://arxiv.org/html/2504.19874v1/x5.png)

---

## References（參考文獻）

**中文翻譯：**

參考文獻部分包含論文引用的所有文獻來源，包括：

- Elastic search (2025)
- Qdrant vector search (2025)
- Pgvector search (2025)
- Pinecone vector database (2025)
- Achiam et al. (2023) - GPT-4 technical report
- Ainslie et al. (2023) - GQA: Training generalized multi-query transformer models
- Anthropic (2024) - Claude 3 family
- Ashkboos et al. (2024) - Quarot: Outlier-free 4-bit inference in rotated LLMs
- Babenko & Lempitsky (2014) - Additive quantization for extreme vector compression
- Bai et al. (2023) - LongBench: A bilingual, multitask benchmark for long context understanding
- 以及其他 50+ 篇相關研究論文

---

**表格說明：**

論文中包含以下表格：

**Table 1:** LongBench-V1 結果比較（各種 KV 快取壓縮方法在 Llama-3.1-8B-Instruct 上的表現）

**Table 2:** 不同方法在不同維度下的量化時間比較（使用 4 位元量化）

---

*翻譯完成日期：2026-04-18*

*翻譯者：TurboQuant Deep Dive Project*

