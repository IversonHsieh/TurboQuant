# 📄 TurboQuant Paper Translation (English - Traditional Chinese)

## Abstract / 摘要

**Original:**
Vector quantization, a problem rooted in Shannon’s source coding theory, aims to quantize high-dimensional Euclidean vectors while minimizing distortion in their geometric structure. We propose TurboQuant to address both mean-squared error (MSE) and inner product distortion, overcoming limitations of existing methods that fail to achieve optimal distortion rates. Our data-oblivious algorithms, suitable for online applications, achieve near-optimal distortion rates (within a small constant factor) across all bit-widths and dimensions. TurboQuant achieves this by randomly rotating input vectors, inducing a concentrated Beta distribution on coordinates, and leveraging the near-independence property of distinct coordinates in high dimensions to simply apply optimal scalar quantizers per each coordinate. Recognizing that MSE-optimal quantizers introduce bias in inner product estimation, we propose a two-stage approach: applying an MSE quantizer followed by a 1-bit Quantized JL (QJL) transform on the residual, resulting in an unbiased inner product quantizer. We also provide a formal proof of the information-theoretic lower bounds on best achievable distortion rate by any vector quantizer, demonstrating that TurboQuant closely matches these bounds, differing only by a small constant ($\approx 2.7$) factor. Experimental results validate our theoretical findings, showing that for KV cache quantization, we achieve absolute quality neutrality with 3.5 bits per channel and marginal quality degradation with 2.5 bits per channel. Furthermore, in nearest neighbor search tasks, our method outperforms existing product quantization techniques in recall while reducing indexing time to virtually zero.

**中文翻譯：**
向量量化 (Vector quantization) 是源於 Shannon 源編碼理論的一個問題，其目標是在量化高維歐幾里得向量的同時，最小化其幾何結構的失真。我們提出了 TurboQuant，旨在同時解決均方誤差 (MSE) 與內積失真 (inner product distortion) 的問題，克服了現有方法無法達到最佳失真率的局限性。我們提出的數據無關 (data-oblivious) 演算法適用於在線應用，在所有位元寬度與維度下均能達到近乎最佳的失真率（僅差一個小的常數因子）。TurboQuant 透過隨機旋轉輸入向量，使座標呈現集中的 Beta 分佈，並利用高維空間中不同座標之間近乎獨立的特性，簡單地對每個座標應用最佳標量量化器來實現這一目標。我們意識到 MSE 最優量化器會在內積估計中引入偏差，因此提出了一種兩階段方法：首先應用 MSE 量化器，接著對殘差進行 1-bit 的量化 Johnson-Lindenstrauss (QJL) 轉換，從而得到一個無偏的內積量化器。我們還針對任何向量量化器所能達到的最佳失真率提供了資訊理論下界的正式證明，證明 Turbo Quant 與這些下界非常接近，差異僅在於一個小的常數 ($\approx 2.7$) 因子。實驗結果驗證了我們的理論發現，結果顯示在 KV cache 量化方面，我們在每通道 3.5 bits 時實現了絕對的品質中立，而在 2.5 bits 時僅有輕微的品質下降。此外，在最近鄰搜尋任務中，我們的方法在召回率上優於現有的乘積量化 (product quantization) 技術，同時將索引時間降低至幾乎為零。

---

## Introduction / 引言

**Original:**
Vector quantization (VQ) in Euclidean space is crucial for efficiently handling high-dimensional vectors across a spectrum of computational domains, from training and deploying large-scale AI and deep learning models to powering vector databases for search/retrieval systems. The core objective is to compress high dimensional vectors by quantizing them–converting floating-point coordinate values to low-bitwidth integers–while minimizing distortion, quantified by metrics such as mean-squared error (MSE) or inner product errors. By preserving these properties, inner product queries can be answered rapidly, with minimal latency, and using reduced computational and communication resources.

**中文翻譯：**
歐幾里得空間中的向量量化 (VQ) 對於在各種計算領域中高效處理高維向量至關重要，範圍涵蓋了從訓練與部署大規模 AI 及深度學習模型，到為搜尋/檢索系統提供向量資料庫動力。其核心目標是透過量化（將浮點座標值轉換為低位元寬度的整數）來壓縮高維向量，同時最小化失真，而失真透過均方誤差 (MSE) 或內積誤差等指標來量化。透過保留這些特性，內積查詢可以在極低的延遲下快速完成，並減少計算與通訊資源的使用。

---

**Original:**
This problem’s roots trace back to Shannon’s seminal work on Source Coding theory [48, 49], which established that the least distortion achievable by block source codes, now known as vector quantizers, is defined by the Shannon distortion-rate function, determined by the statistical properties of the source and the chosen distortion measure, such as MSE. Today, VQ plays a critical role in fundamental computational domains, including AI, deep and search systems.

**中文翻譯：**
這個問題的根的源可以追溯到 Shannon 在源編碼理論上的開創性工作 [48, 49]，該工作確立了由塊源編碼（現稱為向量量化器）所能達到的最小失真是由 Shannon 失真率函數定義的，而該函數取決於數據源的統計特性以及所選取的失真度量（例如 MSE）。如今，VQ 在基礎計算領域中扮演著關鍵角色，包括 AI、深度學習與搜尋系統。

---

**Original:**
A key application of VQ is in the deployment of AI models, including large language models (LLMs) [5, 18, 7, 52]. As LLM capabilities depend heavily on their model size and context length [34], serving them requires substantial memory demands and increased inference latency. This latency is primarily attributed to communication bottlenecks between HMB and SRAM on accelerators, or across distributed clusters. By compressing or quantizing model weights and activations, we can effectively mitigate these bottlenecks, resulting in significant reductions in inference costs. Inner product operations between activations and weights is at the core of deep learning models. Thus, model quantization schemes strive to compress weights and/or activation vectors while accurately preserving these inner products.

**中文翻譯：**
VQ 的一個關鍵應用是在 AI 模型的部署中，包括大型語言模型 (LLMs) [5, 18, 7, 52]。由於 LLM 的能力高度依賴於其模型大小與上下文長度 [34]，服務這些模型需要龐大的記憶體需求並增加了推論延遲。這種延遲主要歸因於加速器上 HBM 與 SRAM 之間，或是跨分散式集群之間的通訊瓶頸。透過壓縮或量化模型權重與激活值 (activations)，我們可以有效地緩解這些瓶騰，從而顯著降低推論成本。激活值與權重之間的內積運算（inner product operations）是深度學習模型的核心。因此，模型量化方案致力於在壓縮權重和/or 激活向量的同時，準確地保留這些內積特性。

---

**Original:**
Decoder based transformer models [54] present another compelling use case. These models must store key/value (KV) embeddings from previously generated tokens in the KV cache, the size of which scales with both model size (number of layers and attention heads) and context length. This scaling is a significant bottleneck in terms of memory usage and computational speed, especially for long context models. Therefore, reducing the KV cache size without compromising accuracy is essential. In this context, the preservation of the Euclidean structure of these embedding vectors–their inner products and distances–is crucial for maintaining model performance. VQ emerges as the most suitable framework for addressing this challenge, offering a robust approach to compressing high-dimensional embeddings while preserving their essential geometric properties.

**中文翻譯：**
基於 Decoder 的 Transformer 模型 [54] 提供了另一個極具吸引力的使用案例。這些模型必須將先前生成的 token 的 Key/模 KV (KV) 嵌入 (embeddings) 儲存在 KV cache 中，其大小隨模型規模（層數與注意力頭數）及上下文長度同步擴展。這種擴展在記憶體使用量與計算速度方面構成了一個重大瓶頸，對於長上下文模型尤其如此。因此，在不損害準確性的前提下縮減 KV cache 的大小至關重要。在這種背景下，保留這些嵌入向量的歐幾里得結構（即其內積與距離）對於維持模型性能至關重要。VQ 成為解決此挑戰最合適的框架，它提供了一種強大的方法，能在壓縮高維嵌入的同時，保留其核心的幾何特性。

---

**Original:**
Additionally, nearest neighbor (NN) search in high-dimensional spaces with inner product or cosine similarity [1, 27] is a cornerstone of vector databases [4, 2, 3]. These databases are fundamental for retrieval-augmented generation [23, 19] and information retrieval [35, 46]. VQ, a.k.a. product quantization (PQ), plays a critical role in these applications. It enables efficient compression of database vectors, optimizes memory usage, and facilitates low-latency, accurate estimations of inner products with query vectors, thereby enabling fast and precise nearest neighbor searches.

**中文翻譯：**
此外，在高維空間中使用內積或餘弦相似度進行的最近鄰 (NN) 搜尋 [1, 27] 是向量資料庫 [4, 2, 3] 的基石。這些資料庫對於檢索增強生成 (RAG) [23, 19] 與資訊檢索 [35, 46] 至關重要。VQ（亦稱為乘積量化, PQ）在這些應用中扮演著關鍵角色。它能夠實現資料庫向量的高效壓縮、優化記憶體使用，並促進與查詢向量之間低延遲、準確的內積估計，從而實現快速且精確的最近鄰搜尋。

---

**Original:**
Existing VQ algorithms present a trade-off: either they lack accelerator (vectorization) compatibility and exhibit slow computation, making them unsuitable for real-time AI applications like KV cache quantization, or they suffer from suboptimal distortion bounds relative to bit-width. Our objective is to introduce an algorithm that addresses these limitations. Specifically, we design TurboQuant: a lightweight, capable of online application (crucial for scenarios like KV cache quantization), and highly accelerator-friendly—a critical attribute for modern AI workloads.

**中文翻譯：**
現有的 VQ 演算法存在權衡問題：要麼缺乏加速器（向量化）相容性且計算速度緩慢，使其不適用於如 KV cache 量化等即時 AI 應用；要麼相對於位元寬度而言，其失真界限（distortion bounds）並非最優。我們的目標是引入一種能解決這些局限性的演算法。具體而言，我們設計了 TurboQuant：一種輕量化、具備在線應用能力（對於 KV cache 量化等場景至關重要），且對加速器非常友好的演算法——這是現代 AI 工作負載的一個關鍵屬性。

---

**Original:**
The core of TurboQuant is a two-stage process. First, we develop a vector quantizer with optimal distortion rate in terms of mean-squared error (MSE). Subsequently, we apply a 1-bit quantizer to the residual, resulting in an unbiased and low-distortion inner product quantizer. We demonstrate that quantizers optimized for MSE do not produce unbiased estimators for inner products, and our two-stage solution effectively bridges this gap. Our MSE-optimal quantizer starts by randomly rotating $d$-dimensional input vectors. Observing the key fact that each coordinate in the rotated vectors follows a Beta distribution, we design optimal Lloyd-Max quantizer [42, 43] for each coordinate by solving a continuous k-means problem. This method gives optimal MSE distortion bound and minimizes the $L_2$ norm of the residual. To obtain an unbiased and low-distortion quantizer for inner products, we compose our quantizer with the recently developed Quantized Johnson-Lindenstrauss (QJL) transform [62], which quantizes each coordinate of the residual vector to a single bit. Our algorithm offers provably optimal distortion bounds for both MSE and inner products, achieving an exponential improvement over existing methods in terms of bit-width dependence.

**中文翻譯：**
TurboQuant 的核心是一個兩階段的過程。首先，我們開發了一個在均方誤差 (MSE) 方面具有最佳失真率的向量量化器。隨後，我們對殘差應用 1-bit 量化器，從而得到一個無偏且低失真的內積量化器。我們證明了針對 MSE 優化的量化器無法為內積提供無偏估計器，而我們的兩階段解決方案有效地彌補了這一差距。我們的 MSE 最優量化器首先對 $d$ 維輸入向量進行隨機旋轉。透過觀察到旋轉後的向量中每個座標都遵循 Beta 分佈這一關鍵事實，我們藉由解決一個連續的 k-means 問題，為每個座標設計了最佳的 Lloyd-Max 量化器 [42, 43]。此方法提供了最佳的 MSE 失真界限，並最小化了殘差的 $L_2$ 範數。為了獲得用於內積的無偏且低失真的量化器，我們將我們的量化器與最近開發的量化 Johnson-Lindenstrauss (QJL) 轉換 [62] 相結合，該轉換將殘差向量的每個座標量化為單個位元。我們的演算法在 MSE 與內積方面均提供了可證明的最佳失真界限，在位元寬度依賴性方面較現有方法實現了指數級的改進。

---

**Original:**
Formally, our goal is to design a quantization map, denoted as $Q: \mathbb{R}^d \to \{0, 1\}^B$, that transforms $d$-dimensional vectors to a binary string of $B$ bits. If we set $B = b \cdot d$ for some $b \ge 0$, this quantizer will have a bit-width of $b$, representing the average number of bits used to encode each real-valued coordinate of $\mathbb{R}^d$. Crucially, we require an inverse map, $Q^{-1}: \{0, 1\}^B \to \mathbb{R}^d$ that performs dequantization, approximately reconstructing original vectors from their quantized representations. Of course, this transformation is inherently lossy, as $Q$ is not a bijection. So, our primary objective is to minimize distortion, with a specific focus on mean-squared error (MSE) and inner product distortion.

**中文翻譯：**
正式地說，我們的目標是設計一個量化映射，記作 $Q: \mathbb{R}^d \to \{0, 1\}^B$，將 $d$ 維向量轉換為長度為 $B$ 位元的二進位字串。如果我們設定 $B = b \cdot d$（其中 $b \ge 0$），則該量化器的位元寬度為 $b$，代表編碼 $\mathbb{R}^d$ 中每個實值座標所使用的平均位元數。至關重要的是，我們需要一個逆映射 $Q^{- 1}: \{0, 1\}^B \to \mathbb{R}^d$ 來執行反量化，從量化表示中近似重建原始向量。當然，由於 $Q$ 並非雙射，這種轉換本質上是有損的。因此，我們的主要目標是最小化失真，特別關注均方誤差 (MSE) 與內積失真。

---

**Original:**
We make no assumptions about the input vector dataset, considering the worst-case scenario. We let the quantizer $Q(\cdot)$ to be randomized, leading to stochastic outputs. Considering randomized quantizers, it is more appropriate to define the expected distortion over the randomness of the quantizer’s output. Thus, we aim to design quantizers that for any desired bit-width $b$ minimize the following expected distortion measures for any (worst-case) vectors $\mathbf{x}, \mathbf{y} \in \mathbb{R}^d$:
[Formulae omitted]
The expectations above are taken with respect to the randomness of the quantizer $Q(\cdot)$. Furthermore, for inner-product quantizers, we require unbiasedness of the inner product estimator, a desirable property for numerous applications. More precisely, we require:
[Formulae omitted]
We aim to design computationally efficient quantizers $Q_{\text{mse}}$ and $Q_{\text{prod}}$, that achieve optimal bounds for the distortion measures defined above, for any given bit-width $b$. Additionally, we aim for $Q_{\text{prod}}$ to provide unbiased inner product estimates. In particular, assume that we are given $n$ real-valued vectors $\mathbf{x}_1, \mathbf{x}_2, \dots, \mathbf{x}_n \in \mathbb{R}^d$. We design the following primitives:
Quant: efficiently quantizes the dataset and computes $Q(\mathbf{x}_1), Q(\mathbf{x}_2), \dots, Q(\mathbf{x}_n)$.
DeQuant: given a quantized dataset, can efficiently reconstruct original vectors by computing $Q^{-1}(Q(\mathbf{x}_i))$ for any $i \in [n]$.

**中文翻譯：**
我們不對輸入向量數據集做任何假設，而是考慮最壞情況。我們讓量化器 $Q(\cdot)$ 具有隨機性，從而導致隨機輸出。考慮到隨機量化器，在量化器輸出的隨機性之上定義期望失真更為合適。因此，我們的目標是設計出對於任何所需的位元寬度 $b$，都能最小化以下針對任何（最壞情況）向量 $\mathbf{x}, \mathbf{y} \in \mathbb{R}^d$ 的期望失真度量的量化器：
[公式省略]
上述期望是針對量化器 $Q(\sdot)$ 的隨機性而計算的。此外，對於內積量化器，我們要求內積估計器具有無偏性，這是許多應用中理想的特性。更精確地說，我們要求：
[公式省略]
我們的目標是設計出計算效率高的量化器 $Q_{\text{mse}}$ 與 $Q_{\text{prod}}$，使其在任何給定的位元寬度 $b$ 下，都能達到上述失真度量的最佳界限。此外，我們希望 $Q_{\text{prod}}$ 能提供無偏的內積估計。特別地，假設我們給定 $n$ 個實值向量 $\mathbf{x}_1, \mathbf{x}_2, \dots, \mathbf{x}_n \in \mathbb{R}^d$。我們設計了以下原語 (primitives)：
Quant：高效地量化數據集並計算 $Q(\mathbf{x}_1), Q(\mathbf{x}_2), \dots, Q(\mathbf{x}_n)$。
DeQuant：給定量化後的數據集，可以透過計算 $Q^{-1}(Q(\mathbf{x}_i))$ 來高效地重建原始向量，其中任何 $i \in [n]$。

---

**Original:**
The vector quantization theory started by Shannon’s seminal work [48, 49] on achievable distortion-rate functions. In 1963, Zador [61] made significant advances by employing high-resolution methods to derive the limiting operational distortion-rate function for fixed-rate quantization at high rates that closely matches Shannon’s distortion-rate function. However, Zador did not specifically consider implementable algorithms. Gersho’s influential paper [25], further advanced the vector quantization by popularizing high-resolution theory, simplifying Zador’s results, introducing lattice vector quantization, and proposing a key conjecture that shaped the field. Despite these theoretical advancements, the practical applicability of vector quantization remained unclear in early years. The most straightforward encoding method, brute-force nearest neighbor search, was computationally expensive, hindering the adoption of VQ in practice.

**中文翻譯：**
向量量化理論始於 Shannon 在可實現失真率函數方面的開創性工作 [48, 49]。1963 年，Zador [61] 透過採用高解析度方法，推導出了高率下固定率量化的極限操作失真率函數，該函數與 Shannon 的失真率函數非常接近，取得了重大進展。然而，Zador 並未特別考慮可實現的演算法。Gersho 的影響力論文 [25] 透過普及高解析度理論、簡化 Zador 的結果、引入格點向量量化 (lattice vector quantization) 並提出了一個塑造該領域的關鍵猜想，進一步推進了向量量化。儘管有了這些理論上的進步，向量量化在早期的實際適用性仍不明朗。最直接的編碼方法——暴力最近鄰搜尋——計算成本極高，阻礙了 VQ 在實務中的採用。

---

**Original:**
Online (data-oblivious) quantization methods apply instantly without needing data-specific tuning or calibrations [16, 8, 41, 47, 28]. In contrast, offline (data-dependent) methods require heavy preprocessing and learning to adapt the quantization map to the data, making them unsuitable for dynamic data scenarios [37]. For instance, methods such as those presented in [20, 39, 57, 13] use second-order (Hessian) information to tune the quantization map which requires heavy preprocessing and even in some cases post processing as well.

**中文翻譯：**
在線（數據無關）量化方法無需針對特定數據進行調整或校準即可立即應用 [16, 8, 41, 47, 28]。相比之下，離線（數據依應）方法需要繁重的預處理與學習，以使量化映射適應數據，這使得它們不適用於動態數據場景 [37]。例如，如 [20, 39, 57, 13] 中提出的方法使用二階（Hessian）資訊來調整量化映射，這需要繁重的預處理，在某些情況下甚至還需要後處理。

---

**Original:**
Several approaches have been proposed to compress the KV cache. These include architectural modifications [50, 6, 15] which restructure the transformer to minimize the number of stored key-value pairs. Additionally, pruning or evicting redundant or less critical tokens has emerged as another approach [11, 66, 40, 58, 64, 38, 29].

**中文翻譯：**
目前已有多種方法被提出用於壓縮 KV cache。其中包括架構修改 [50, 6, 15]，透過重構 Transformer 以最小化儲存的 Key-Value 對數量。此外，剪枝 (pruning) 或剔除冗餘或較不關鍵的 token 也成為另一種方法 [11, 66, 40, 58, 64, 38, 29]。

---

**Original:**
A simple yet effective approach to reducing KV cache size is quantizing the KV cache. Several quantization techniques have been 
developed specifically for this purpose [60, 59, 17, 33, 65, 41, 30, 36, 28]. Recently, a new quantization called QJL [62] introduced an efficient, data-oblivious 1-bit quantization approach based on sketching techniques, which provides unbiased estimates for inner product queries. This method does not require tuning or adaptation to the input data and we make use of this technology in our quantizer optimized for inner product distortion.

**中文翻譯：**
一種簡單且有效縮減 KV cache 大小的方法是對 KV cache 進行量化。專為此目的開發了多種量化技術 [60, 59, 17, 33, 65, 41, 30, 36, 28]。最近，一種名為 QJL [62] 的新量化技術引入了一種基於 sketching 技術的高效、數據無關的 1-bit 量化方法，它能為內積查詢提供無偏估計。該方法不需要針對輸入數據進行調整或適應，我們在針對內積失真優化的量化器中也利用了這項技術。

---

**Original:**
In Near Neighbor (NN) search problem with Euclidean datasets, the index size poses a significant memory bottleneck, often mitigated by quantization techniques, commonly referred to as Product Quantization (PQ) in the NN literature. Many of these algorithms rely on constructing a quantization codebook using variations of k-means during the indexing phase [31, 9, 24, 56, 27]. Therefore, these methods are ill-suited for online settings due to their requirement for extensive preprocessing.

**中文翻譯：**
在具有歐幾里得數據集的最近鄰 (NN) 搜尋問題中，索引大小構成了顯著的記憶體瓶頸，通常透過量化技術來緩解，在 NN 文獻中通常稱為乘積量化 (PQ)。這些演算法中的許多都依賴於在索引階段使用 k-means 的變體來構建量化碼本 (codebook) [31, 9, 24, 56, 27]。因此，由於需要大量的預處理，這些方法並不適合在線場景。

---

**Original:**
Recently, a grid-based PQ method was introduced in [22], eliminating the need for preprocessing. This approach operates by projecting a uniform grid onto the unit sphere and conducting a search to identify the nearest projection to the data points. While the paper’s theoretical guarantees are suboptimal, likely due to loose analysis—as practical performance surpasses theoretical bounds—the grid projection and binary search algorithm is also computationally slow and particularly inefficient on accelerators like GPU because of their algorithm’s inherent lack of vectorization, which prevents parallel processing.

**中文翻譯：**
最近，[22] 引入了一種基於網格的 PQ 方法，消除了預處理的需求。該方法透過將均勻網格投影到單位球面上，並進行搜尋以識別與數據點最近的投影來運作。雖然該論文的理論保證並非最優（可能是由於分析不夠嚴密——因為實際性能超過了理論界限），但網格投影與二分搜尋演算法在計算上也很緩慢，且由於演算法本身缺乏向量化，導致無法進行並行處理，因此在 GPU 等加速器上特別低效。

---

**Original:**
Our first VQ algorithm is designed to minimize MSE distortion deinfed in ??. To achieve this, we apply a random rotation to the input vectors, thereby inducing a Beta distribution on each coordinate, irrespective of the input vectors themselves. In high dimensions $d$, the distribution of each coordinate converges to a Gaussian distribution $\mathcal{N}(0, 1/d)$ due to concentration of measure and the central limit theorem. Furthermore, any two distinct coordinates become nearly uncorrelated and, more important, almost independent (a deeper result that goes beyond just correlation). This near-independence is a crucial aspect that simplifies our quantization design. It allows us to quantize each coordinate using optimal scalar quantization, disregarding interactions or correlations between different coordinates, while still achieving near-optimal distortion.

**中文翻譯：**
我們的第一個 Vq 演算法旨在最小化 ?? 中定義的 MSE 失真。為了實現這一點，我們對輸入向量進行隨機旋轉，從而使每個座標都呈現 Beta 分佈，而與輸入向量本身無關。在高維度 $d$ 下，由於測度集中 (concentration of measure) 與中心極限定理，每個座標的分布會收斂到高斯分佈 $\mathcal{N}(0, 1/d)$。此外，任何兩個不同的座標都會變得近乎不相關，更重要的是，幾乎是相互獨立的（這是一個超越了僅僅是相關性的更深層結果）。這種近乎獨立的特性是簡化我們量化設計的一個關鍵方面。它允許我們使用最佳標量量化來量化每個座標，而無需考慮不同座標之間的交互作用或相關性，同時仍能達到近乎最佳的失真。

---

**Original:**
We find optimal scalar quantizers for random variables with Beta distributions by solving a continuous 1-dimensional k-means problem using the Max-Lloyd algorithm. We precompute and store these optimal codebooks for a range of practically useful bit-widths, to enable efficient subsequent invocations of our TurboQuant algorithm.

**中文翻譯：**
我們透過使用 Max-Lloyd 演算法解決一個連續的一維 k-means 問題，找到了具有 Beta 分佈的隨機變量的最佳標量量化器。我們預先計算並儲存了這些針對一系列實用位元寬度的最佳碼本，以便後續高效地調用我們的 TurboQuant 演算法。

---

**Original:**
In ?? we prove that the $b$-bit MSE optimized TurboQuant $Q_{\text{mse}}:\mathbb{R}^d \to \{0, 1\}^{b \cdot d}$ achieves the following distortion for any worst-case vector $\mathbf{x} \in \mathbb{R}^d$ with $\|\mathbf{x}\| = 1$:
[Formulae omitted]
For small bit-widths, specifically $b=1, 2, 3, 4$ we have $D_{\text{mse}}(Q_{\text{mse}}) \approx 0.36, 0.117, 0.03, 0.009$, respectively.

**中文翻譯：**
在 ?? 中，我們證明了 $b$-bit MSE 優化的 TurboQuant $Q_{\text{mse}}:\mathbb{R}^d \to \{0, 1\}^{b \cdot d}$ 對於任何滿足 $\|\mathbf{x}\| = 1$ 的最壞情況向量 $\mathbf{x} \in \mathbb{R}^d$ 均能達到以下失真：
[公式省略]
對於較小的位元寬度，特別是 $b=1, 2, 3, 4$，我們分別得到 $D_{\text{mse}}(Q_{\text{mse}}) \approx 0.36, 0.117, 0.03, 0.009$。

---

**Original:**
Note that the unit norm assumption, $\|\mathbf{x}\|_2 = 1$, is standard and not restrictive. For datasets that do not satisfy this assumption we can compute and compute and store the $L_2$ norms in floating-point precision and rescale the dequantized points using these stored norms.

**中文翻譯：**
請注意，單位範數假設 $\|\mathbf{x}\|_2 = 1$ 是標準做法且並無限制性。對於不滿足此假設的數據集，我們可以以浮點精度計算並儲存 $L_2$ 範數，並使用這些儲存的範數來重新縮放反量化後的點。

---

**Original:**
We show that the MSE optimized quantizers are biased for inner product estimation and thus a different VQ scheme is needed to get an unbiased inner product quantizer. Our solution is a two stage algorithm that first applies the abovementioned $Q_{\text{mse}}$ with a bit-width one less than our target budget and then apply a QJL [62] on the residual error. This is proved to be unbiased and also has nearly optimal inner product error rate.

**中文翻譯：**
我們展示了 MSE 優化的量化器在內積估片方面存在偏差，因此需要一種不同的 VQ 方案來獲得無偏的內積量化器。我們的解決方案是一種兩階段演算法，首先應用上述位元寬度比目標預算少 1 的 $Q_{\text{mse}}$，然後對殘差誤差應用 QJL [62]。這已被證明是無偏的，並且具有近乎最佳的內積誤差率。

---

**Original:**
In ?? we prove that the $b$-bit inner product optimized TurboQuant $Q_{\text{prod}}:\mathbb{R}^d \to \{0, 1\}^{b \cdot d}$ achieves the following distortion for any worst-case vectors $\mathbf{x}, \mathbf{y} \in \mathbb 
[Formulae omitted]
For small bit-widths, specifically $b=1, 2, 3, 4$, $D_{\text{prod}}(Q_{\text{prod}}) \approx 1.57d, 0.56d, 0.18d, 0.047d$, respectively.

**中文翻譯：**
在 ?? 中，我們證明了 $b$-bit 內積優化的 TurboQuant $Q_{\text{prod}}:\mathbb{R}^d \to \{0, 1\}^{b \cdot d}$ 對於任何最壞情況向量 $\mathbf{x}, \mathbf{y} \in \mathbb{R}^d$ 均能達到以下失真：
[公式省略]
對於較小的位元寬度，特別是 $b=1, 2, 3, 4$，我們分別得到 $D_{\text{prod}}(Q_{\text{prod}}) \approx 1.57d, 0.56d, 0.18d, 0.047d$。

---

**Original:**
In ??, we leverage Shannon’s lower bound and Yao’s minimax principle to prove that for any randomized quantization algorithm $Q:\mathbb{R}^d \to \{0, 1\}^{b \cdot d}$ with bit-width $b$ and any reconstruction map $Q^{-1}:\{0, 1\}^{b \cdot d} \to \mathbb{R}^d$, there exist a hard input instance $\mathbf{x} \in \mathbb{S}^{d-1}$ such that:
[Formulae omitted]
Furthermore, there exists a $\mathbf{y} \in \mathbb{S}^{d-1}$ such that:
[Formulae omitted]
By Yao’s minimax principle the expected MSE of the optimal randomized compression algorithm for worst-case inputs ($D_{\text{mse}}$) is equal to the expected MSE of the optimal deterministic compression algorithm when applied to inputs drawn from a maximally difficult randomized distribution. By definition, the MSE of the latter scenario is lower-bounded by the best achievable MSE for inputs uniformly distributed on the unit hypersphere.

**中文翻譯：**
在 ?? 中，我們利用 Shannon 的下界與 Yao 的極小化極大原理 (minimax principle) 來證明，對於任何位元寬度為 $b$ 的隨機量化演算法 $Q:\mathbb{R}^d \to \{0, 1\}^{b \cdot d}$，都存在難題輸入實例 $\mathbf{x} \in \mathbb{S}^{d-1}$ 使得：
[公式省略]
此外，存在一個 $\mathbf{y} \in \mathbb{S}^{d-1}$ 使得：
[公式省略]
根據 Yao 的極小化極大原理，針對最壞情況輸入的最佳隨機壓縮演算法的期望 MSE ($D_{\text{mse}}$)，等於將最佳確定性壓縮演算法應用於從極難隨機分佈中抽取的輸入時的期望 MSE。根據定義，後者的 MSE 下界由單位超球面上均勻分佈輸入的最佳可實現 MSE 所界定。

---

**Original:**
The best achievable MSE for a compression algorithm with bit-width $b$, operating on uniformly distributed inputs from the sphere $\mathbb{S}^{d-1}$, is lower bounded in ??. Therefore, by invoking ?? we conclude that $D_{\text{mse}} \ge \frac{1}{4^b}$.

**中文翻譯：**
對於在單位球 $\mathbb{S}^{d-1}$ 上均勻分佈的輸入上運行的位元寬度為 $b$ 的壓縮演算法，其最佳可實現 MSE 在 ?? 中給出了下界。因此，透過引用 ??，我們得出結論 $D_{\text{mse}} \ge \frac{1}{4^b}$。

---

**Original:**
Furthermore, from $D_{\text{mse}} \ge \frac{1}{4^b}$ and using the definition of $D_{\text{mse}}$ we conclude that:
[Formulae omitted]
By pigeonhole principle there exist an index $j \in [d]$ such that $\mathbb{E}[\dots] \ge \frac{1}{d} \cdot \frac{1}{4^b}$, which completes the proof. $\blacksquare$

**中文翻譯：**
此外，從 $D_{\text{mse}} \ge \frac{1}{4^b}$ 並使用 $D_{\text{mse}}$ 的定義，我們得出結論：
[公式省略]
根據鴿巢原理 (pigeonhole principle)，存在一個索引 $j \in [d]$ 使得 $\mathbb{E}[\dots] \ge \frac{1}{d} \cdot \frac{1}{4^b}$，從而完成了證明。$\blacksquare$

---

**Original:**
We note that a comparable lower bound for the worst-case distortion in vector quantization can be derived using “sphere packing” arguments (indeed, with larger constants as this is a harder problem) [26]. However, ?? offers a more robust and relevant lower bound for our analysis. This is because it establishes a lower bound on the expected distortion, rather than the worst-case error, and aligns seamlessly with our upper bounds presented in ?? and ??.

**中文翻譯：**
我們注意到，向量量化中最壞情況失真的可比下界可以透過「球體填充」(sphere packing) 論點推導出來（事實上，由於這是一個更難的問題，其常數會更大）[26]。然而，?? 為我們的分析提供了一個更穩健且更相關的下界。這是因為它建立的是期望失真的下界，而非最壞情況誤差，並且與我們在 ?? 和 ?? 中提出的上界完美契合。

---

**Original:**
All experiments are performed using a single NVIDIA A100 GPU. The experimental section is divided into two parts: one to empirically validate the theoretical results, and another to evaluate the performance of our methods on downstream tasks, specifically KV cache quantization and nearest neighbor vector search.

**中文翻譯：**
所有實驗均使用單張 NVIDIA A100 GPU 進行。實驗部分分為兩個部分：一部分是用於實證理論結果，另一部分是用於評估我們的方法在下游任務（特別是 KV cache 量化與最近鄰向量搜尋）中的性能。

---

**Original:**
In this section, we verify the theoretical results established in previous sections. We conduct our experiments using the DBpedia Entities dataset, which has been encoded into 1536-dimensional and 3072-dimensional spaces using OpenAI3 embeddings. To perform our experiments, we randomly sample 100,000 data points from the dataset, denoted as training set, which serves as our primary training and evaluation set. Additionally, we extract 1,000 distinct entries, denoted as query set, to be used as query points for datasets that do not explicitly provide a query set. For the GloVe dataset, we use a pre-existing query set consisting of 10,000 points.

**中文翻譯：**
在本節中，我們驗證了前幾節建立的理論結果。我們使用 DBpedia Entities 數據集進行實驗，該數據集已使用 OpenAI3 嵌入技術被編碼到 1536 維與 3072 維空間中。為了進行實驗，我們從數據集中隨機抽取了 100,000 個數據點，稱為訓練集，作為我們的主要訓練與評估集。此外，我們提取了 1,000 個不同的條目，稱為查詢集，用作對於未明確提供查詢集的數據集的查詢點。對於 GloVe 數據集，我們使用一個包含 10,000 個點的現有查詢集。

---

**Original:**
We evaluate two quantization methods: $TurboQuant_{\text{prod}}$ and $TurboQuant_{\text{mse}}$. The method $TurboQuant_{\text{mse}}$ is designed to be optimzed for estimating the mean squared error (MSE) between the quantized and original vectors. In contrast, $TurboQuant_{\text{prod}}$ is unbiased for estimating the inner product between the quantized and original vectors.

**中文翻譯：**
我們評估了兩種量化方法：$TurboQuant_{\text{prod}}$ 與 $TurboQuant_{\text{mse}}$。其中 $TurboQuant_{\text{mse}}$ 方法旨在優化量化向量與原始向量之間的均方誤差 (MSE) 估計。相比之下，$TurboQuant_{\text{prod}}$ 在估計量化向量與原始向量之間的內積時是無偏的。

---

**Original:**
Both methods are applied to the task of inner product estimation by quantizing training set and analyzing the distortion in inner product calculations across different bit widths. As shown in ??, increasing the bit width reduces variance in both methods. However, when used for inner product estimation, $TurboQuant_{\text{mse}}$ introduces bias. This bias diminishes as the bit width increases and eventually converges to zero.

**中文翻譯：**
這兩種方法都應用於內積估計任務，透過量化訓練集並分析不同位元寬度下內積計算的失真。如 ?? 所示，增加位元寬度會降低這兩種方法的方差。然而，當用於內積估計時，$TurboQuant_{\text{mse}}$ 會引入偏差。隨著位元寬度的增加，這種偏差會逐漸減小並最終趨於零。

---

 

**Original:**
The experimental results, illustrated in ??, confirm that $TurboQuant_{\text{prod}}$ remains unbiased for inner product estimation across all bit widths, while $TurboQuant_{\text{mse}}$ gradually improves with increasing bit width.

**中文翻譯：**
如 ?? 所示的實驗結果證實，$TurboQuant_{\text{prod}}$ 在所有位元寬度下對於內積估計保持無偏，而 $TurboQuant_{\text{mse}}$ 則隨著位元寬度的增加而逐漸改善。

---

**Original:**
As observed in ??, when quantizing to 2 bits, the variance remains constant regardless of the inner product of the original vector in the $TurboQuant_{\text{prod}}$ approach. However, the same plot indicates that the bias in the $TurboQuant_{\text{mse}}$ approach is dependent on the average inner product. As the average inner product increases, the bias also increases.

**中文翻譯：**
如 ?? 所觀察到的，在量化為 2 bits 時，在 $TurboQuant_{\text{prod}}$ 方法中，無論原始向量的內積如何，方差都保持不變。然而，同一張圖表顯示 $TurboQuant_{\text{mse}}$ 方法中的偏差取決於平均內積。隨著平均內積的增加，偏差也會隨之增加。

---

**Original:**
Along with the histograms, we also plot ?? the average inner product error and MSE between the original and quantized vectors across different bit ratios. These plots are drawn alongside the upper and lower bounds established in our theoretical analysis. Our observations confirm that the results align with the theoretical predictions. Specifically, for inner product estimation, the $Turbo Quant_{\text{prod}}$ approach performs better at lower bit ratios. However, as the bit count increases, $TurboQuant_{\text{mse}}$ reduces bias and ultimately achieves superior performance in inner product estimation.

**中文翻譯：**
除了直方圖外，我們還繪製了不同位元率下原始向量與量化向量之間的平均內積誤差與 MSE。這些圖表是與我們理論分析中建立的上下界一同繪製的。我們的觀察證實，結果與理論預測一致。具體而言，對於內積估計，$TurboQuant_{\text{prod}}$ 方法在較低的位元率下表現更好。然而，隨著位元數增加，$TurboQuant_{\text{mse}}$ 會減少偏差，並最終在內積估計中實現更優越的性能。

---

**Original:**
The “Needle-In-A-Haystack Test” [32] is a benchmark designed to evaluate a model’s ability to retrieve specific information embedded within a long document. The test involves placing a unique sentence (the ”needle”) at an arbitrary location within a much larger text (the ”haystack”) and assessing whether the model can successfully extract it.

**中文翻譯：**
「大海撈針測試」(Need le-In-A-Haystack Test) [32] 是一種旨在評估模型從長文件中檢索特定資訊能力的基準測試。該測試涉及在一個巨大的文本（「乾草堆」）中的任意位置放置一個唯一的句子（「針」），並評估模型是否能成功提取它。

---

**Original:**
Following the experimental setup of Fu et al. [21], we conduct evaluations using the $Llama-3.1-8B-Instruct$ model. To analyze performance across different input sequence lengths, we vary the document size from 4k to 104k tokens. The primary metric used for evaluation is the recall score, which measures how accurately the model retrieves the hidden sentence.

**中文 翻譯：**
遵循 Fu 等人 [21] 的實驗設置，我們使用 $Llama-3.1-8B-Instruct$ 模型進行評估。為了分析不同輸入序列長度下的性能，我們將文檔大小從 4k 變動到 104k tokens。評估使用的主要指標是召回率 (recall score)，它衡量模型檢索隱藏句子的準確程度。

---

**Original:**
For comparison, we benchmark our approach against several state-of-the-art memory-efficient methods, including PolarQuant [28], SnapKV [38], PyramidKV [12], and KIVI [41]. Each method is tested under a memory compression ratio of 0.25, meaning that only 2 5% of the full KV cache is utilized.

**中文翻譯：**
為了進行比較，我們將我們的方法與幾種最先進的記憶體高效方法進行基準測試，包括 PolarQuant [28]、SnapKV [38]、PyramidKV [12] 和 KIVI [41]。每種方法都在 0.25 的記憶體壓縮率下進行測試，這意味著僅使用了 25% 的完整 KV cache。

---

**Original:**
The results, illustrated in ??, reveal that quantization methods with theoretical guarantees, such as PolarQuant and TurboQuant, outperform token-level compression techniques like SnapKV and PyramidKV, as well as scalar quantization approaches like KIVI, which lack formal theoretical guarantees. Notably, TurboQuant achieves identical performance to the full-precision model, even at $4\times$ compression, making it a robust solution for long-context processing.

**中文翻譯：**
如 ?? 所示的結果顯示，具有理論保證的量化方法（如 PolarQuant 和 Turbo Quant）優於像 SnapKV 和 PyramidKV 這樣的 token 級壓縮技術，也優於像 KIVI 這樣缺乏正式理論保證的標量量化方法。值得注意的是，即使在 $4\times$ 壓縮下，TurboQuant 仍能達到與全精度模型相同的性能，使其成為長上下文處理的強大解決方案。

---

**Original:**
We experiment with various KV cache compression algorithms on the LongBench dataset [10], which encompasses a broad range of long-text scenarios, including single- and multi-document question-answering, summarization, few-shot learning, synthetic tasks, and code completion. To ensure a balanced evaluation across different context lengths, we employ LongBench-E, a subset designed with a more uniform length distribution. This enables a fair assessment of each model’s performance across varying context sizes, making it a more reliable benchmark for evaluating compression techniques.

**中文翻譯：**
我們在 LongBench 數據集 [10] 上對各種 KV cache 壓縮演算法進行了實驗，該數據集涵蓋了廣泛的長文本場景，包括單一與多文檔問答、摘要、少樣本學習、合成任務與程式碼補全。為了確保在不同上下文長度下的平衡評估，我們採用了 LongBench-E，這是一個設計有更均勻長度分佈的子集。這使得我們能夠公平地評估每個模型在不同上下文大小下的性能，使其成為評估壓縮技術更可靠的基準。

---

**Original:**
We compare TurboQuant against the leading baseline methods introduced in ??, using both $Llama-3.1-8B-Instruct$ and $Ministral-7B-Instruct$. Unlike existing approaches such as KIVI and PolarQuant, which leave generated tokens unquantized, our method applies quantization even during the streaming generation process.

**中文翻譯：**
我們將 TurboQuant 與 ?? 中引入的領先基準方法進行比較，使用了 $Llama-3.1-8B-Instruct$ 與 $Ministral-7B-Instruct$。與 KIVI 和 PolarQuant 等現有方法（這些方法會讓生成的 token 保持不量化）不同，我們的方法甚至在流式生成過程中也應用了量化。

---

**Original:**
As shown in ??, our approach outperforms other methods for both $Llama-3.1-8B-Instruct$ and $Ministral-7B-Instruct$, achieving significantly higher average scores. We evaluate our method using 2.5-bit and 3.5-bit quantization during text generation. These non-integer bit precisions result from our strategy of splitting channels into outlier and non-outlier sets, and applying two independent instances of TurboQuant to each, allocating higher bit precision to outliers. This outlier treatment strategy is consistent with prior work [63, 51]. For example, in our 2.5-bit setup, 32 outlier channels are quantized at 3 bits, while the remaining 96 channels use 2 bits, leading to an effective bit precision of $(32 \times 3 + 96 \times 2) / 128 = 2.5$. For 3.5-bit quantization, a different ratio of outliers and regular channels leads to a higher effective bit precision. Despite using fewer bits than competing techniques, TurboQuant maintains performance comparable to unquantized models. Remarkably, we achieve this while compressing quantized vectors by at least a 4.5$\times$.

**中文翻譯：**
如 ?? 所示，我們的方法在 $Llama-3.1-8B-Instruct$ 與 $Ministral-7B-Instruct$ 上均優於其他方法，實現了顯著更高的平均分數。我們在文本生成期間使用 2.5-bit 與 3.5-bit 量化來評估我們的方法。這些非整數位元精度源於我們將通道拆分為離群值 (outlier) 與非離群值集合的策略，並對每一部分分別應用兩個獨立的 TurboQuant 實例，為離群值分配更高的位元精度。這種離群值處理策略與先前的工作 [63, 51] 是一致的。例如，在我們的 2.5-bit 設定中，32 個離群值通道以 3 bits 量化，而其餘 96 個通道使用 2 bits，導致有效位元精度為 $(32 \times 3 + 96 \times 2) / 128 = 2.5$。對於 3.5-bit 量化，不同的離群值與常規通道比例會導致更高的有效位元精度。儘管使用的位元比競爭技術更少，TurboQuant 仍能維持與未量化模型相當的性能。值得注意的是，我們在將量化向量壓縮至少 $4.5\times$ 的同時實現了這一點。

---

 

**Original:**
In this section, we establish the strength of our proposed method, even in the context of near-neighbor search. We conduct our experiments using the DBpedia [53] Entities dataset, which has been encoded into 1536-dimensional and 3072-dimensional spaces using OpenAI3 embeddings. Additionally, we evaluate performance on a lower-dimensional dataset, utilizing the standard GloVe [45] embeddings. To construct our experimental setup, we randomly sample 100,000 data points from the dataset, denoted as training set, which serves as our primary training and evaluation set. Furthermore, we extract 1,000 distinct entries, denoted as query set, to be used as query points for datasets that do not explicitly provide a query set. For the GloVe dataset, we use a pre-existing query set consisting of 10,000 points.

**中文翻譯：**
在本節中，我們展示了我們提出的方法即使在最近鄰搜尋的背景下也具有強大的實力。我們使用 DBpedia [53] Entities 數據集進行實驗，該數據集已使用 OpenAI3 嵌入技術被編碼到 1536 維與 3072 維空間中。此外，我們還在較低維度的數據集上進行了評估，使用了標準的 GloVe [45] 嵌入。為了構建實驗設置，我們從數據集中隨機抽取了 100,000 個數據點，稱為訓練集，作為我們的主要訓練與評估集。此外，我們提取了 1,000 個不同的條目，稱為查詢集，用作對於未明確提供查詢集的數據集的查詢點。對於 GloVe 數據集，我們使用一個包含 10,000 個點的現有查詢集。

---

**Original:**
We compare our method, TurboQuant, against two baseline quantization approaches: Product Quantization (PQ) and RabitQ [22]. To ensure a fair comparison, we quantize the dataset training set using all three methods and evaluate their performance based on recall ratio at top-k, denoted as 1@k. Specifically, this metric assesses how often the true top inner product result is captured within the top- k approximated results returned by each algorithm.

**中文翻譯：**
我們將 TurboQuant 方法與兩種基準量化方法進行比較：乘積量化 (PQ) 與 RabitQ [22]。為了確保公平比較，我們使用這三種方法對訓練集進行量化，並根據 top-k 的召回率 (recall ratio, 記作 1@k) 來評估其性能。具體而言，該指標衡量每個演算法返回的 top-k 近似結果中，包含真實最高內積結果的頻率。

---

**Original:**
Product Quantization (PQ) relies on the k-means algorithm to construct codebooks, which require separate storage. As the number of bits increases, the size of the codebook grows exponentially, leading to additional storage overhead. In our experiments, we carefully tuned the parameters to match the bit allocation of other methods. The most efficient implementation, designed for rapid querying, employs AVX2 In-Register Lookup Tables (LUTs). Specifically, it uses LUT16 with (l = 1 6) codewords. However, we observed substantial quality degradation at this configuration. To achieve a balance between speed and accuracy, we opted for a version of PQ that uses LUT256, which contains 256 codewords. For 2-bit quantization, it groups 4 coordinates per lookup, while for 4-bit quantization, it groups 2 coordinates per lookup. Notably, since we use the same dataset for both training and evaluation, PQ benefits from an inherent advantage in this setup.

**中文翻譯：**
乘積量化 (PQ) 依賴於 k-模演算法來構建碼本，這需要額外的儲存空間。隨著位元數的增加，碼本的大小會呈指數級增長，導致額外的儲存開銷。在我們的實驗中，我們仔細調整了參數，以匹配其他方法的位元分配。為了實現快速查詢而設計的最有效實現採用了 AVX2 寄存器內查找表 (LUTs)。具體而言，它使用具有 16 個字元的 LUT16。然而，我們觀察到在此配置下品質會大幅下降。為了在速度與準確性之間取得平衡，我們選擇了使用包含 256 個字元的 LUT256 版本。對於 2-bit 量化，它每次查找分組 4 個座標，而對於 4-bit 量化，它每次查找分組 2 個座標。值得注意的是，由於我們在訓練與評估中使用相同的數據集，因此 PQ 在此設置中具有內在優勢。

---

**Original:**
RabitQ. Unlike PQ, RabitQ lacks a fully vectorized implementation, making it impossible to leverage GPU acceleration. As a result, it runs significantly slower on CPU. Additionally, the method incurs extra computational overheads that we do not explicitly account for in the bit ratio comparisons. While RabitQ claims a certain bit ratio, in practice, it utilizes more bits than reported due to these inefficiencies.

**中文翻譯：**
RabitQ。與 PQ 不同，RabitQ 缺乏完全向量化的實現，因此無法利用 GPU 加速。因此，它在 CPU 上的運行速度明顯較慢。此外，該方法會產生額外的計算開銷，我們在位元率比較中並未明確考慮這些開銷。雖然 RabitQ 聲稱具有特定的位元率，但由於這些低效性，在實務中它使用的位元比報告的要多。

---

**Original:**
Despite the advantages granted to the baseline methods, TurboQuant consistently outperforms both Product Quantization and RabitQ in terms of recall ratio across all experiments. This demonstrates the robustness and efficiency of our approach, making it a compelling alternative for high-dimensional quantization-based search tasks.

**中文翻譯：**
儘管基準方法具有其優勢，但 TurboQuant 在所有實驗中的召回率均一致優於乘積量化 (PQ) 與 RabitQ。這證明了我們方法的穩健性與效率，使其成為高維度基於量化搜尋任務的一個極具吸引力的替代方案。

---

**Original:**
We are continuing to improve HTML versions of papers, and your feedback helps enhance accessibility and mobile support. To report errors in the HTML that will help us improve conversion and rendering, choose any of the methods listed below:
[Methods omitted]
Our team has already identified the following issues. We appreciate your time reviewing and reporting rendering errors we may not have found yet. Your efforts will help us improve the HTML versions for all readers, because disability should not be a barrier to accessing research. Thank you for your continued support in championing open access for all.

**中文翻譯：**
我們正在持續改進論文的 HTML 版本，您的回饋將有助於增強可訪問性與行動端支援。若要回報 HTML 中的錯誤以幫助我們改進轉換與渲染，請選擇下方列出的任何方法：
[方法省略]
我們的團隊已經發現了以下問題。我們感謝您花時間審查並回報我們可能尚未發現的渲染錯誤。您的努力將幫助我們為所有讀者改進 HTML 版本，因為殘障不應成為獲取研究成果的障礙。感謝您對倡導全民開放獲取 (open access) 的持續支持。
