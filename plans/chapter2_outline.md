# 📝 章節 2：數學基礎大綱 (Mathematical Foundations Outline)

本文件概述了 TurboQuant Deep Dive 網誌中章節 2 將涵蓋的結構與關鍵數學概念。

## 🎯 目標 (Objective)
提供理解 TurboQuant 演算法所需的必要數學背景（包括 Coordinate Systems、Transformer Mechanisms 以及 Dimensionality Reduction）。

## 📂 章節結構 (Chapter Structure)

### 2.1 Cartesian Coordinate System (笛卡兒座標系)
- **核心概念 (Core Concept)**：二維平面上的 $(x, y)$ 座標定義。
- **數學基礎 (Mathematical Foundation)**：Vector 的表示法與基本運算（Addition, Scalar Multiplication）。
- **技術關聯 (Technical Relevance)**：作為 LLMs 中高維 Vector Space 的標準基準。

### 2.2 Polar Coordinate System (極座標系)
- **核心概念 (Core Concept)**：徑向距離 $r$ 與角度 $\theta$ 的定義。
- **座標轉換 (Coordinate Transformation)**：使用 $\sin$ 與 $\cos$ 進行 $(x, y) \to (r, \theta)$ 的轉換公式。
- **技術優勢 (Technical Advantage)**：解釋為何在 Quantization 的旋轉與縮放變換 (Rotation and Scaling Transformations) 時，Polar Coordinates 比 Cartesian Coordinates 更具直觀性與計算效率。

### 2.3 Transformer Architecture Analysis (Transformer 結構解析)
- **核心機制 (Core Mechanism)**：Self-Attention 的數學模型。
- **矩陣運算 (Matrix Operations)**：$Q$ (Query), $K$ (Key), 與 $V$ (Value) 矩陣的生成與 Dot-product 計算。
- **視覺化規劃 (Visualization Plan)**：規劃一個展示 Attention Score 計算流程的 SVG Flowchart。

### 2.4 KV Cache Mechanism (KV Cache 解析)
- **問題背景 (Problem Background)**：Autoregressive Decoding 中的冗餘計算問題。
- **解決方案 (Solution)**：如何透過 Caching $K$ 與 $V$ Vectors 來加速 Inference。
- **效能影響 (Performance Impact)**：對 Memory Usage 與 Computation Time 的權衡分析 (Trade-off Analysis)。

### 2.5 PolarQuant Core Principle (PolarQuant 核心原理)
- **創新思路 (Innovative Approach)**：將 Quantization 過程從 Cartesian Space 轉移到 Polar Space。
- **量化策略 (Quantization Strategy)**：利用 $r$ (Magnitude) 與 $\theta$ (Phase/Angle) 的特性來降低 Bit-width 需求。

### 2.6 QJL (Quantized Johnson-Lindenstrauss) Algorithm
- **數學理論 (Mathematical Theory)**：Johnson-Lindenstrauss Lemma 的基本原理（Dimensionality Reduction 與 Distance Preservation）。
- **量化整合 (Quantization Integration)**：量化後的 Projection 技術如何在高維空間中維持結構特徵。

---
*最後更新日期: 2026-04-12*
