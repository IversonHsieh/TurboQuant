# 最近鄰搜尋 (Nearest Neighbor Search) 詳細解說

[🏠 返回目錄](../index.md)

**相關連結：**
- [返回 TurboQuant 論文翻譯](03-turboquant-translation.md)
- [向量量化解釋](03-vector-quantization-explanation.md)
- [內積誤差解釋](03-inner-product-errors.md)

---

## 1. 什麼是最近鄰搜尋 (Nearest Neighbor Search)？

**最近鄰搜尋 (Nearest Neighbor Search, NN Search)** 是一種在高維空間中尋找與查詢點最相似的數據點的技術。這個「最相似」通常是通過計算**距離**或**相似度**來衡量的。

### 1.1 問題定義

給定：
- 一個數據集 $\mathcal{D} = \{\mathbf{x}_1, \mathbf{x}_2, \ldots, \mathbf{x}_n\}$，其中每個 $\mathbf{x}_i \in \mathbb{R}^d$ 是 $d$ 維空間中的一個點
- 一個查詢點 $\mathbf{q} \in \mathbb{R}^d$

**最近鄰搜尋的目標**是找到：

$$
\mathbf{x}^* = \arg\min_{\mathbf{x}_i \in \mathcal{D}} \text{dist}(\mathbf{q}, \mathbf{x}_i)
$$

其中 $\text{dist}(\cdot, \cdot)$ 是一個距離函數。

### 1.2 常見的距離/相似度度量

| 度量名稱 | 公式 | 應用場景 |
|---------|------|---------|
| **歐幾里得距離 (Euclidean Distance)** | $\|\mathbf{q} - \mathbf{x}\|_2 = \sqrt{\sum_{i=1}^d (q_i - x_i)^2}$ | 幾何空間中的直線距離 |
| **內積 (Inner Product)** | $\langle \mathbf{q}, \mathbf{x} \rangle = \sum_{i=1}^d q_i x_i$ | 相似度衡量，值越大越相似 |
| **餘弦相似度 (Cosine Similarity)** | $\cos(\theta) = \frac{\langle \mathbf{q}, \mathbf{x} \rangle}{\|\mathbf{q}\|_2 \cdot \|\mathbf{x}\|_2}$ | 方向相似度，忽略大小 |
| **曼哈頓距離 (Manhattan Distance)** | $\|\mathbf{q} - \mathbf{x}\|_1 = \sum_{i=1}^d |q_i - x_i|$ | 網格狀路徑距離 |

---

## 2. 為什麼最近鄰搜尋很重要？

### 2.1 實際應用場景

1. **向量資料庫檢索**
   - 在 RAG (Retrieval-Augmented Generation) 系統中，需要快速找到與用戶查詢最相關的文檔
   - 例如：搜尋引擎、推薦系統

2. **圖像檢索**
   - 找到與查詢圖像最相似的圖像
   - 應用：以圖搜圖、人臉識別

3. **語意搜尋**
   - 使用嵌入 (embeddings) 將文本轉換為向量，然後搜尋語意上最相似的文本
   - 應用：問答系統、文檔檢索

4. **異常檢測**
   - 如果一個點的最近鄰距離很遠，可能是異常點
   - 應用：欺詐檢測、系統監控

### 2.2 在 TurboQuant 中的應用

在 [TurboQuant 論文](03-turboquant-translation.md) 中，最近鄰搜尋有兩個關鍵應用：

1. **KV Cache 量化**：在 transformer 模型中，需要快速找到與當前查詢最相關的 key/value 對
2. **向量資料庫**：TurboQuant 可以用於壓縮向量資料庫中的數據，同時保持高召回率

論文中提到：
> "在我們的方法中，在最近鄰搜尋任務中，我們在召回率方面優於現有的乘積量化技術，同時將索引時間減少到幾乎為零。"

---

## 3. 最近鄰搜尋的挑戰

### 3.1 計算複雜度問題

**暴力搜尋 (Brute-Force Search)** 是最直接的方法：

```python
def brute_force_nn(query, dataset):
    """暴力最近鄰搜尋"""
    min_dist = float('inf')
    nearest_point = None
    
    for point in dataset:
        dist = euclidean_distance(query, point)
        if dist < min_dist:
            min_dist = dist
            nearest_point = point
    
    return nearest_point
```

**問題**：對於有 $n$ 個點的數據集，每次查詢需要 $O(n \cdot d)$ 的時間複雜度。當 $n$ 很大時（例如百萬級別），這變得非常慢。

### 3.2 維度災難 (Curse of Dimensionality)

隨著維度 $d$ 的增加：
- 數據變得稀疏
- 距離分佈趨於均勻，使得「最近」和「最遠」的區別變得不明顯
- 許多傳統的空間索引結構（如 kd-tree）在高維空间中失效

這就是為什麼需要像 **TurboQuant** 這樣的量化技術來加速高維最近鄰搜尋。

---

## 4. 最近鄰搜尋的視覺化示例

![最近鄰搜尋示意圖](../svg/nearest_neighbor_search.svg)

*圖：最近鄰搜尋示意圖。黃色點為查詢點 q，彩色點為數據集中的數據點。虛線表示查詢點到各數據點的距離，其中到點 B 的距離最短（黃色高亮虛線），因此 B 是最近鄰。*

讓我們通過一個二維示例來直觀理解最近鄰搜尋：

### 4.1 基本示例

假設我們有一個二維數據集，包含以下點：

| 點名稱 | 座標 (x, y) | 類別 |
|-------|------------|------|
| A | (1, 2) | 紅 |
| B | (2, 3) | 紅 |
| C | (3, 1) | 藍 |
| D | (4, 2) | 藍 |
| E | (5, 4) | 綠 |

如果查詢點 $\mathbf{q} = (2.5, 2.5)$，那麼：

- 到 A 的距離：$\sqrt{(2.5-1)^2 + (2.5-2)^2} = \sqrt{2.25 + 0.25} = \sqrt{2.5} \approx 1.58$
- 到 B 的距離：$\sqrt{(2.5-2)^2 + (2.5-3)^2} = \sqrt{0.25 + 0.25} = \sqrt{0.5} \approx 0.71$
- 到 C 的距離：$\sqrt{(2.5-3)^2 + (2.5-1)^2} = \sqrt{0.25 + 2.25} = \sqrt{2.5} \approx 1.58$
- 到 D 的距離：$\sqrt{(2.5-4)^2 + (2.5-2)^2} = \sqrt{2.25 + 0.25} = \sqrt{2.5} \approx 1.58$
- 到 E 的距離：$\sqrt{(2.5-5)^2 + (2.5-4)^2} = \sqrt{6.25 + 2.25} = \sqrt{8.5} \approx 2.92$

**結果**：點 B 是最近鄰，因為它的距離最小 (0.71)。

### 4.2 k-最近鄰 (k-NN)

除了找**一個**最近鄰，我們還可以找 **k 個**最近鄰：

- **1-NN**：找 1 個最近鄰
- **k-NN**：找 k 個最近鄰（例如 k=5）

k-NN 在機器學習中是一個經典的分類/回歸演算法。

---

## 5. 加速最近鄰搜尋的技術

### 5.1 基於樹的方法

- **kd-tree**：k 維樹，適合低維空間
- **Ball tree**：球樹，對高維空間稍好

### 5.2 基於哈希的方法

- **LSH (Locality Sensitive Hashing)**：局部敏感哈希
- 相似點有更高機率被哈希到同一個桶中

### 5.3 基於量化的方法（產品量化）

- **Product Quantization (PQ)**：將向量分解為多個子向量，分別量化
- **TurboQuant**：通過隨機旋轉和最佳純量量化實現接近最佳的失真率

### 5.4 基於圖的方法

- **HNSW (Hierarchical Navigable Small World)**：層次可導航小世界
- 構建一個圖結構，在圖上進行貪婪搜尋

---

## 6. TurboQuant 在最近鄰搜尋中的優勢

根據論文實驗結果，TurboQuant 在最近鄰搜尋中具有以下優勢：

| 特性 | TurboQuant | 傳統 Product Quantization |
|-----|-----------|------------------------|
| **索引時間** | 幾乎為零（無需預處理） | 需要 k-means 聚類 |
| **召回率** | 更高 | 較低 |
| **線上應用** | 支援（data-oblivious） | 不支援（需要數據依賴的預處理） |
| **GPU 加速** | 完全支援（向量化） | 部分支援 |

---

## 7. 實作範例

### 7.1 使用 Python 和 scikit-learn 進行最近鄰搜尋

```python
from sklearn.neighbors import NearestNeighbors
import numpy as np

# 創建數據集
X = np.array([[1, 2], [2, 3], [3, 1], [4, 2], [5, 4]])

# 創建查詢點
query = np.array([[2.5, 2.5]])

# 創建最近鄰模型
nbrs = NearestNeighbors(n_neighbors=1, algorithm='ball_tree')
nbrs.fit(X)

# 搜尋最近鄰
distances, indices = nbrs.kneighbors(query)

print(f"最近鄰的索引：{indices[0][0]}")  # 輸出：1 (點 B)
print(f"距離：{distances[0][0]:.2f}")    # 輸出：0.71
```

### 7.2 使用內積的最近鄰搜尋

在許多應用中（如 transformer 的注意力機制），我們使用**內積**而不是歐幾里得距離：

```python
def inner_product_nn(query, dataset):
    """使用內積的最近鄰搜尋（最大值）"""
    inner_products = np.dot(dataset, query)
    nearest_idx = np.argmax(inner_products)
    return nearest_idx, inner_products[nearest_idx]
```

---

## 8. 總結

| 概念 | 說明 |
|-----|------|
| **最近鄰搜尋** | 在高維空間中尋找與查詢點最相似的數據點 |
| **距離度量** | 歐幾里得距離、內積、餘弦相似度等 |
| **挑戰** | 計算複雜度高、維度災難 |
| **加速方法** | 樹、哈希、量化、圖結構 |
| **TurboQuant 優勢** | 無需預處理、高召回率、支援線上應用 |

---

## 參考文獻

1. [TurboQuant 論文翻譯](03-turboquant-translation.md) - 第 1.3 節和第 4.4 節討論了最近鄰搜尋應用
2. [向量量化解釋](03-vector-quantization-explanation.md) - 了解量化如何用於壓縮和加速
3. [內積誤差解釋](03-inner-product-errors.md) - 理解內積在相似度計算中的重要性

---

*最後更新：2026-04-20*
*作者：TurboQuant Deep Dive Project*
