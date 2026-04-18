# 向量量化 (Vector Quantization, VQ) 深度解析

向量量化 (Vector Quantization, VQ) 是一種將高維向量壓縮為低維度表示的技術。與傳統的純量量化 (Scalar Quantization, SQ) 不同，VQ 同時考慮了向量中各個維度之間的相關性，透過將一組維度視為一個單元（向量）來進行量化，從而能更有效地捕捉數據的幾何結構並降低失真。

## 1. 核心概念

在向量量化中，我們擁有一組預先定義好的向量，稱為 **碼本 (Codebook)**。每個向量稱為 **碼向量 (Codevector)** 或 **質心 (Centroid)**。

量化的過程如下：
1. **輸入**：一個高維歐幾里得向量 $\mathbf{x} \in \mathbb{R}^d$。
2. **搜尋**：在碼本中尋找一個與 $\mathbf{x}$ 最接近的碼向量 $\mathbf{c}_i$。通常使用最小化歐幾里得距離（即最小化 MSE）作為準則：
   $$\hat{\mathbf{c}} = \arg\min_{\mathbf{c}_i \in \mathcal{C}} \|\mathbf{x} - \mathbf{c}_i\|^2$$
3. **輸出**：輸出該碼向量的索引 $i$，或者直接輸出量化後的向量 $\hat{\mathbf{c}}$。

## 2. 視覺化說明

下圖展示了向量量化如何將輸入的數據點（藍色）映射到最近的碼向量（紅色）上。

![Vector Quantization Concept](../svg/vector_quantization_example.svg)

在圖中，你可以看到多個輸入向量（藍色點）被「歸類」到了最近的碼向量（紅色圓圈）所代表的區域。這種「聚類」的過程就是量化的核心。

## 3. 實際範例：圖像壓縮

想像一張 $256 \times 256$ 像素的灰階圖像。

* **純量量化 (SQ)**：我們對每一個像素點獨立進行量化（例如將 0-255 壓縮到 0-15）。這完全忽略了像素之間的空間相關性。
* **向量量化 (VQ)**：我們將圖像切分成 $4 \times 4$ 的小塊（每個塊包含 16 個像素，即一個 16 維向量）。我們建立一個包含數千個 $4 \times 4$ 模式的碼本。量化時，我們只需記錄每個 $4 \times 4$ 塊對應於碼本中的哪一個索引。

**優勢**：由於圖像中相鄰像素通常非常相似，VQ 可以用極少的資訊（僅需索引）來重建具有高度結構性的圖像，從而實現極高的壓縮比。

## 4. 向量量化 vs. 純量量化

| 特性 | 純量量化 (Scalar Quantization) | 向量量化 (Vector Quantization) |
| :--- | :--- | :--- |
| **處理單位** | 單一數值 (Scalar) | 向量 (Vector/Block) |
| **維度相關性** | 忽略維度間的相關性 | 捕捉維度間的相關性 |
| **壓縮效率** | 較低 | 較高 (在相同失真下) |
| **計算複雜度** | 極低 | 較高 (需要搜尋碼本) |
| **典型應用** | 音訊編碼、簡單數據壓縮 | 圖像/影片壓縮 (如 JPEG 變體)、特徵提取 |

## 5. 總結

向量量化是資訊理論中「失真率函數 (Distortion-Rate Function)」在向量空間中的具體實現。雖然其計算複雜度高於純量量化，但在處理具有強相關性的高維數據（如 Transformer 的 KV Cache 或圖像特徵）時，它能提供更接近理論極限的壓縮性能。

---

## 與 TurboQuant 論文的連結

本頁內容是對 TurboQuant 論文摘要中提到的 **Vector Quantizers** 概念的深入解說。

* [回到 TurboQuant 論文翻譯 - 摘要](./03-turboquant-translation.md#abstract 摘要)
* [回到 TurboQuant 論文翻譯 - 引言](./03-turboquant-translation.md#1-introduction 引言)
