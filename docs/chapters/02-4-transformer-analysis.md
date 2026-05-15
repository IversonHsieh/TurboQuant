# 🧠 Transformer 結構解析 (The Illustrated Transformer)

[🏠 返回目錄](../index.md)

# The Illustrated Transformer

在之前的文章中，我們探討了注意力機制 (Attention) —— 這是現代深度學習模型中無處不在的方法。注意力機制是一個幫助提升神經機器翻譯應用性能的概念。在本文中，我們將研究 Transformer —— 一種利用注意力機制來提升模型訓練速度的模型。Transformer 在特定任務上的表現優於 Google 的神經機器翻譯模型。然而，它最大的優勢在於其具備高度的可並行化能力。事實上，Google Cloud 也建議使用 Transformer 作為參考模型，以利用其 Cloud TPU 的優勢。因此，讓我們試著拆解這個模型，並觀察它是如何運作的。

Transformer 是在《Attention is All You Need》論文中提出的。TensorFlow 的實現版本可以作為 Tensor2Tensor 套件的一部分找到。哈佛大學的 NLP 小組也製作了一個指南，使用 PyTorch 實現來註解該論文。在本文中，我們將嘗試稍微簡化內容，並逐一介紹這些概念，希望能讓沒有深在專業知識的人也能更容易理解。

## 高層次概覽 (A High-Level Look)

讓我們首先將模型視為一個單一的黑盒子。在機器翻譯應用中，它會接收一種語言的句子，並輸出另一種語言的翻譯。

![Transformer Black Box](https://jalammar.github.io/images/t/the_transformer_3.png)![Transformer Black Box]()(../svg/the_transformer_3.svg)

打開這個「擎天柱 (Optimus Prime)」般的精妙結構，我們可以看到一個編碼組件 (encoding component)、一個解碼組件 (decoding component) 以及它們之間的連接。

![Encoder Decoder Components](https://jalammar.github.io/images/t/The_transformer_encoders_decoders.png)
![Encoder Decoder Components]()(../svg/The_transformer_encoders_decoders.svg)

編碼組件是由一堆編碼器堆疊而成（論文中堆疊了六層 —— 六這個數字並沒有什麼魔力，完全可以嘗試其他的配置）。解碼組件同樣是由相同數量的解碼器堆疊而成。

![Encoder Decoder Stack](https://jalammar.github.io/images/t/The_transformer_encoder_decoder_stack.png)
![Encoder Decoder Stack]()(../svg/The_transformer_encoders_decoders_v2.svg)

所有的編碼器在結構上都是完全相同的（但它們並不共享權重）。每一個編碼器都分解為兩個子層：

![Encoder Sub-layers](https://jalammar.github.io/images/t/Transformer_encoder.png)
![Encoder Sub-layers]()(../svg/Transformer_encoder.svg)

編碼器的輸入首先流經一個自注意力層 (self-attention layer) —— 這個層級能幫助編碼器在編碼特定單詞時，去觀察輸入句子中的其他單詞。我們稍後會在文中詳細討論自注意力機制。

自注意力層的輸出會被送入一個前饋神經網路 (feed-forward neural network)。完全相同的前饋網路會獨立地應用於每一個位置。

解碼器同時擁有這兩種層，但在它們之間還有一個注意力層，能幫助解動器專注於輸入句子中的相關部分（類似於 seq2seq 模型中注意力機制的作用）。

![Decoder Sub-layers](https://jalammar.github.io/images/t/Transformer_decoder.png)
![Decoder Sub-layers]()(docs/svg/decoder_sublayers.svg)

## 將張量引入視野 (Bringing The Tensors Into The Picture)

既然我們已經看到了模型的主要組件，現在讓我們開始觀察各種向量/張量 (vectors/tensors)，以及它們如何在這些組件之間流動，從而將訓練模型的輸入轉化為輸出。

與一般的 NLP 應用相同，我們首先使用嵌入演算法 (embedding algorithm) 將每個輸入單詞轉換為向量。

![Embeddings](https://jalammar.github.io/images/t/embeddings.png)
![Embeddings & Vectors]()(docs/svg/embeddings_vectors.svg)

嵌入過程僅發生在最底層的編碼器中。所有編碼器共同的抽象特性是：它們接收一組維度為 $512$ 的向量列表 —— 在最底層編碼器中，這就是單詞嵌入 (word embeddings)；但在其他編碼器中，這則是下方編碼器的輸出。這個列表的大小是一個可以設定的超參數 —— 基本上它就是我們訓練數據集中最長句子的長度。

在對輸入序列中的單詞進行嵌入後，每個單詞都會流經編碼器的這兩個層級。

![Encoder with Tensors](https://jalammar.github.io/images/t/encoder_with_tensors.png)
![Self-Attention Process](docs/svg/self_attention_process.svg)

在這裡，我們開始看到 Transformer 的一個關鍵特性：每個位置的單詞在編碼器中都有其專屬的流動路徑。在自注意力層中，這些路徑之間存在依賴關係。然而，前饋層則沒有這些依賴關係，因此在流經前饋層時，各種路並行運算。

接下來，我們將切換到一個較短的句子範例，並觀察編碼器每個子層中發生了什麼。

## 現在我們開始編碼了！ (Now We’re Encoding!)

正如我們之前提到的，編碼器接收一個向量列表作為輸入。它透過將這些向量送入「自注意力」層，接著送入前饋神經網路，然後將輸出向上傳遞到下一個編碼器來處理這個列表。

![Encoder with Tensors 2](https://jalammar.github.io/images/t/encoder_with_tensors_2.png)
![Self-Attention Process](docs/svg/self_attention_process.svg)

## 自注意力機制的高層次解析 (Self-Attention at a High Level)

不要被我隨口說出「自注意力」這個詞而誤導，以為這是一個人人都應該熟悉的概念。我個人在讀到《Attention is All You Need》論文之前，也從未接觸過這個概念。讓我們來拆解它的運作原理。

假設以下句子是我們想要翻譯的輸入句子：

「The animal didn't cross the street because it was too tired」
（這隻動物因為太累了，所以沒有穿過街道）

這個句子中的「it」指的是什麼？是指「街道」還是「動物」？對人類來說這是一個簡單的問題，但對演算法來說卻不簡單。

當模型正在處理「it」這個單詞時，自注意力機制允許它將「it」與「animal」聯繫起來。

當模型處理每個單詞（輸入序列中的每個位置）時，自注意力機制允許它觀察輸入序列中的其他位置，尋找能幫助為該單詞提供更好編碼的線索。

如果你熟悉 RNN，可以想想維持隱藏狀態 (hidden state) 如何讓 RNN 在處理當前單詞時，能結合之前處理過的單詞/向量的表示。自注意力機制正是 Transformer 用來將其他相關單詞的「理解」融入到我們目前正在處理的單詞中的方法。

![Self-Attention Visualization](https://jalammar.github.io/images/t/transformer_self-attention_visualization.png)
![Self-Attention Process](docs/svg/self_attention_process.svg)

請務前查看 Tensor2Tensor 筆記本，你可以在其中載入 Transformer 模型，並使用這個互動式視覺化工具進行檢查。

## 自注意力機制的細節解析 (Self-Attention in Detail)

我們首先看看如何使用向量來計算自注意力，然後接著研究它是如何使用矩陣來實際實現的。

計算自自注意力的第一步是從每個編碼器的輸入向量（在此例中為每個單端詞的嵌入）中創建三個向量。因此，對於每個單詞，我們創建一個查詢向量 (Query vector, $Q$)、一個鍵向量 (Key vector, $K$) 和一個值向量 (Value vector, $V$)。這些向量是透過將嵌入向量乘以我們在訓練過程中訓練的三個矩陣來創建的。

請注意，這些新向量的維度比嵌入向量小。它們的維度是 $64$，而嵌入向量以及編碼器的輸入/輸出向量維度則是 $512$。它們並不「必須」更小，這是一種為了讓多頭注意力 (multi-headed attention) 的計算量（主要）保持恆定的架構選擇。

![Self-Attention Vectors](https://jalammar.github.io/images/t/transformer_self_attention_vectors.png)
![Self-Attention Process](docs/svg/self_attention_process.svg)

什麼是「查詢 (query)」、「鍵 (key)」和「值 (value)」向量？

它們是對於計算和思考注意力非常有用的抽象概念。一旦你繼續閱讀下文關於注意力如何計算的部分，你就會掌握這些向量所扮演的角色的絕大部分知識。

計算自自注意力的第二步是計算一個分數 (score)。假設我們正在計算這個範例中第一個單詞「Thinking」的自注意力。我們需要針對這個單詞，對輸入句子中的每個單詞進行評分。這個分數決定了在編碼特定位置的單詞時，應該對輸入句子中的其他部分投入多少關注。

分數的計算方法是取查詢向量與我們正在評分的對應單詞的鍵向量的點積 (dot product)。因此，如果我們正在處理位置 #1 單誠的自注意力，第一個分數將是 $q_1$ 與 $k_1$ 的點積。第二個分數將是 $q_1$ 與 $k_2$ 的點積。

![Self-Attention Score](https://jalammar.github.io/images/t/transformer_self_attention_score.png)
![Self-Attention Process](docs/svg/self_attention_process.svg)

第三步和第四步是將分數除以 $8$（這是論文中所使用的鍵向量維度的平方根 $\sqrt{64}$，這能帶來更穩定的梯度。這裡可能會有其他可能的值，但這是預設值），然後將結果通過一個 softmax 操作。Softmax 會將分數正規化，使其全部為正值且總和為 $1$。

![Self Attention Softmax](https://jalammar.github.io/images/t/self-attention_softmax.png)
![Self-Attention Process](docs/svg/self_attention_process.svg)

這個 softmax 分數決定了每個單詞在該位置會如何被表達。顯然，該位置的單詞將擁有最高的 softmax 分數，但有時關注與當前單詞相關的其他單詞也是很有用的。

第五步是將每個值向量乘以 softmax 分數（為了後續的加總做準備）。這裡的直覺是保留我們想要關注的單詞的值，並淹沒不相關的單詞（例如透過將它們乘以像 $0.001$ 這樣微小的數字）。

第六步是將加權後的值向量進行加總。這產生了該位置自注意力層的輸出（針對第一個單詞）。

![Self-Attention Output](https://jalammar.github.io/images/t/self-attention-output.png)
![Self-Attention Process](docs/svg/self_attention_process.svg)

自注意力計算到此結束。產生的向量是我們可以送往前饋神經網路的向量。然而，在實際實現中，這種計算是以矩陣形式進行的，以便進行更快速的處理。既然我們已經看到了單詞層級的計算直進，現在讓我們來看看矩陣形式的計算。

## 自注意力的矩陣計算 (Matrix Calculation of Self-Attention)

第一步是計算查詢 ($Q$)、鍵 ($K$) 和值 ($V$) 矩陣。我們透過將嵌入向量打包成一個矩陣 $X$，並將其乘以我們訓練好的權重矩陣 ($W^Q, W^K, W^V$) 來完成。

![Self-Attention Matrix Calculation 1](https://jalammar.github.io/images/t/self-attention-matrix-calculation.png)
![Multi-Head Attention](docs/svg/multi_head_attention.svg)

最後，既然我們處理的是矩陣，我們可以用一個公式將第二步到第六步壓縮起來，以計算自注意力層的 輸出。

![Self-Attention Matrix Calculation 2](https://jalammar.github.io/images/t/self-attention-matrix-calculation-2.png)
![Multi-Head Attention](docs/svg/multi_head_attention.svg)

## 多頭注意力：強大的機制 (The Beast With Many Heads)

論文透過加入一種稱為「多頭 (multi-headed)」注意力的機制，進一步優化了自注意力層。這從兩個方面提升了注意力層的性能：

1. 它擴展了模型關注不同位置的能力。是的，在上面的範例中，$z_1$ 包含了其他所有編碼的一點點資訊，但它可能會被單詞本身所主導。如果我們正在翻譯像「The animal didn’t cross the street because it was too tired」這樣的句子，知道「it」指的是哪個單詞會非常有幫助。

2. 它為注意力層提供了多個「表示子空間 (representation subspaces)」。正如我們接下來將看到的，透過多頭注意力，我們不僅有一個，而是有多組查詢/鍵/誠值權重矩陣（Transformer 使用了八個注意力頭，因此每個編碼器/解碼器都有八組）。每一組都是隨機初始化的。接著，在訓練之後，每一組都會被用來將輸入嵌入（或來自下方編碼器/解碼器的向量）投影到不同的表示子空間中。

![Multi-Head Attention QKV](https://jalammar.github.io/images/t/transformer_attention_heads_qkv.png)
![Multi-Head Attention](docs/svg/multi_head_attention.svg)

如果我們使用不同的權重矩陣，重複上述自注意力計算八次，我們最終會得到八個不同的 $Z$ 矩陣。

![Multi-Head Attention Z](https://jalammar.github.io/images/t/transformer_attention_heads_z.png)
![Multi-Head Attention](docs/svg/multi_head_attention.svg)

這給我們帶來了一個挑戰。前饋層並不預期接收八個矩陣 —— 它預期的是一個單一矩陣（每個單詞對應一個向量）。因此，我們需要一種方法將這八個矩陣壓縮成一個單一矩陣。

我們該怎麼做呢？我們將這些矩陣進行拼接 (concat)，然後再乘以一個額外的權重矩陣 $W^O$。

![Multi-Head Attention WO](https://jalammar.github.io/images/t/transformer_attention_heads_weight_matrix_o.png)
![Multi-Head Attention](docs/svg/multi_head_attention.svg)

這基本上就是多頭自注意力機制的所有內容了。我意識到這涉及相當多量的矩陣。讓我嘗試將它們全部放在一個視覺化圖表中，以便我們能一目了然地觀察。

![Multi-Head Attention Recap](https://jalammar.github.io/images/t/transformer_multi-headed_self-attention-recap.png)
![Multi-Head Attention](docs/svg/multi_head_attention.svg)

既然我們已經觸及了注意力頭，讓我們重新檢視之前的範例，看看在編碼我們範例句子中的「it」時，不同的注意力頭分別關注在哪裡：

![Self-Attention Visualization 2](https://jalamarr.github.io/images/t/transformer_self-attention_visualization_2.png)
![Self-Attention Visualization 2](https://jalamarr.github.io/images/t/transformer_self-attention_visualization_2.png)

然而，如果我們把所有的注意力頭都加入到圖中，事情可能會變得難以解釋：

![Self-Attention Visualization 3](https://jalammar.githubio/images/t/transformer_self-attention_visualization_3.png)

## 使用位置編碼表示序列順序 (Representing The Order of The Sequence Using Positional Encoding)

到目前為止我們所描述的模型中，缺少的一個要素是能夠考慮輸入序列中單詞的順序。

為了應對這個問題，Transformer 為每個輸入嵌入添加了一個向量。這些向量遵循模型學習到的特定模式，這有助於它確定每個單詞的位置，或者序列中不同單 詞之間的距離。這裡的直覺是，將這些值添加到嵌入中，可以在將它們投影到 $Q/K/V$ 向量以及進行點積注意力期間，在嵌入向量之間提供有意義的距離。

![Positional Encoding Vectors](https://jalammar.github.io/images/t/transformer_positional_encoding_vectors.png)
![Positional Encoding](docs/svg/positional_encoding.svg)

如果我們假設嵌入的維度為 $4$，實際的位置編碼看起來會像這樣：

![Positional Encoding Example](https://jalammar.github.io/images/t/transformer_positional_encoding_example.png)
![Positional Encoding](docs/svg/positional_encoding.svg)

這種模式看起來會是什麼樣子呢？

在下圖中，每一行對應於一個向量的位置編碼。因此，第一行將是我們要添加到輸入序列中第一個單詞嵌入的向量。每一行包含 $512$ 個值 —— 每個值都在 $1$ 到 $-1$ 之間。我們對它們進行了顏色編碼，以便模式清晰可見。

![Positional Encoding Large Example](https://jalammar.github.io/images/t/transformer_position_encoding_large_example.png)
![Positional Encoding](docs/svg/positional_encoding.svg)

位置編碼的公式在論文中有所描述（第 3.5 節）。你可以看到用於生成位置編碼的程式碼位於 `get_timing_signal_1d()` 中。這並不是位置編碼的唯一可能方法。然而，它具有能夠擴展到未見過的序列長度的優點（例如，如果我們的訓練模型被要求翻譯一個比我們訓練集中任何句子都長的句子）。

2020 年 7 月更新：上方顯示的位置編碼來自 Transformer 的 Tensor2Tensor 實現。論文中顯示的方法略有不同，它不是直接拼接，而是交織這兩個信號。下圖展示了其樣貌。以下是生成它的程式碼：

![Positional Encoding Update](https://jalammar.github.io/images/t/attention-is-all-you-need-positional-encoding.png)
![Positional Encoding](docs/svg/positional_encoding.svg)

## 殘差連接 (The Residuals)

在繼續討論之前，我們需要提到編碼器架構中的一個細節：每個編碼器中的每個子層（自注意力、FFNN）都有一個環繞它的殘差連接 (residual connection)，並且隨後是一個層歸一化 (layer-normalization) 步驟。

![Residual Layer Norm 1](https://jalammar.github_io/images/t/transformer_resideual_layer_norm.png)
![Residual & LayerNorm](docs/svg/residual_layer_norm.svg)

如果我們要視覺化與自注意力相關的向量和層歸一化操作，看起來會是這樣：

![Residual Layer Norm 2](https://jalammar.github.io/images/t/transformer_resideual_layer_norm_2.png)
![Residual & LayerNorm](docs/svg/residual_layer_norm.svg)

這對於解碼器的子層也是一樣的。如果我們考慮一個由兩個堆疊的編碼器和解碼器組成的 Transformer，它看起來會像這樣：

![Residual Layer 3](https://jalammar.github.io/images/t/transformer_resideual_layer_norm_3.png)
![Residual & LayerNorm](docs/svg/residual_layer_norm.svg)

## 解碼器端 (The Decoder Side)

既然我們已經涵蓋了編碼器端的大部分概念，我們基本上也知道了解碼器組件是如何協同工作的。讓我們來看看它們是如何一起運作的。

編碼器首先處理輸入序列。頂層編碼器的輸出隨後被轉換為一組注意力向量 $K$ 和 $V$。這些向量將被每個解碼器在其「編碼器-解碼器注意力」層中使用，這有助於解碼器專注於輸入序列中的適當位置：

![Decoder Decoding 1](https://jalammar.github.io/images/t/transformer_decoding_1.gif)
![Decoder Decoding Process](docs/svg/decoder_decoding_process.svg)

這個過程會不斷重複，直到遇到一個特殊符號，表示 Transformer 解碼器已完成其輸出。每一步的輸出都會被送入下一個時間步的底層解碼器，解碼器會像編碼器那樣向上傳遞它們的解碼結果。而且，就像我們對編碼器輸入所做的那樣，我們對這些解碼器輸入進行嵌入並添加位置編組，以指示每個單詞的位置。

![Decoder Decoding 2](httpshttps://jalammar.github.io/images/t/transformer_decoding_2.gif)
![Decoder Decoding Process](docs/svg/decoder_decoding_process.svg)

解碼器中的自注意力層運作方式與編碼器中的略有不同：

在解碼器中，自注意力層僅被允許關注輸出序列中的早期位置。這是透過在自注意力計算的 softmax 步驟之前，對未來位置進行遮蔽 (masking，將其設置為 $-\infty$) 來實現的。

「編碼 碼器-解碼器注意力」層的工作方式與多頭自注意力非常相似，不同之處在於它從其下方的層創建查詢矩陣 ($Q$)，並從編碼器堆疊的輸出中獲取鍵矩陣 ($K$) 和值矩陣 ($V$)。

## 最終的線性層與 Softmax 層 (The Final Linear and Softmax Layer)

解碼器堆疊輸出一個浮點數向量。我們如何將它轉換成一個單詞？這就是最終線性層的工作，隨後是 Softmax 層。

線性層是一個簡單的全連接神經網路，它將解碼器堆疊產生的向量投影到一個大得多的向量中，稱為 logits 向量。

假設我們的模型知道 $10,000$ 個唯一的英文單詞（我們模型的「輸出詞彙量」），這是從我們的訓練數據集中學習到的。這會使 logits 向量寬度為 $10,000$ 個單元 —— 每個單組對應於一個唯一單詞的分數。這就是我們如何透過線性層後面的輸出來解釋模型結果的方式。

接著，softmax 層將這些分數轉換為機率（全部為正值且總和為 $1.0$）。選擇機率最高的單元，並產生與該單詞相關的單詞作為該時間步的輸出。

![Decoder Output Softmax](https://jalammar.github.io/images/t/transformer_decoder_output_softmax.png)
![Loss Comparison](docs/svg/loss_comparison.svg)

## 訓練回顧 (Recap Of Training)

既然我們已經涵蓋了經過訓練的 Transformer 的整個前向傳播過程，瀏覽一下訓練模型的直覺將會很有幫助。

在訓練期間，一個未經訓練的模型也會經歷完全相同的正向傳播過程。但由於我們是在標記好的訓練數據集上進行訓練，因此我們可以將其輸出與實際的正確輸出進行比較。

為了視覺化這一點，讓我們假設我們的輸出詞彙量僅包含六個單詞（「a」、「am」、「i」、「thanks」、「student」和「」）（「」代表「句子結束」）。

![Vocabulary](https://jalammar.github.io/images/t/vocabulary.png)
![One-Hot Encoding](docs/svg/one_hot_encoding.svg)

一旦我們定義了輸出詞彙量，我們就可以使用相同寬度的向量來表示我們詞彙表中的每個單詞。這也被稱為單熱編碼 (one-hot encoding)。例如，我們可以使用以下向量來表示單詞「am」：

![One-hot Vocabulary Example](https://jalammar.github.io/images/t/one-hot-vocabulary-example.png)
![One-Hot Encoding](docs/svg/one_hot_encoding.svg)

在回顧之後，讓我們討論模型的損失函數 (loss function) —— 這是我們在訓練階段進行優化，以期獲得一個訓練良好且可能非常準確的模型的核心指標。

## 損失函數 (The Loss Function)

假設我們正在訓練我們的模型。假設這是我們訓練階段的第一步，我們正在使用一個簡單的範例進行訓練 —— 將「merci」翻譯成「thanks」。

這意味著，我們希望輸出是一個指示「thanks」這個單詞的機率分佈。但由於這個模型尚未經過訓練，這在目前不太可能發生。

![Transformer Logits Output and Label](https://jalammar.github.io/images/t/transformer_logits_t_output_and_label.png)
![Loss Comparison](docs/svg/loss_comparison.svg)

你如何比較兩個機率分佈? 我們只需將一個減去另一個。欲了解更多細節，請參閱交叉熵 (cross-entropy) 和 Kullback–Leibler 散度 (Kullback–Leibler divergence)。

但請注意，這是一個過於簡化的範例。更現實的情況下，我們會使用比單個單詞更長的句子。例如 —— 輸入：「je suis étudiant」，預期輸出：「i am a student」。這真正的意思是，我們希望模型能夠連續輸出如下的機率分佈：

![Output Target Probability Distributions](https://jalammar.github.io/images/t/output_target_probability_distributions.png)
![Loss Comparison](docs/svg/loss_comparison.svg)

在大型數據集上經過足夠長時間的訓練後，我們希望產生的機率分佈看起來像這樣：

![Output Trained Model Probability Distributions](https://jalammar.github.io/images/t/output_trained_model_probability_distributions.png)
![Loss Comparison](docs/svg/loss_comparison.svg)

現在，因為模型一次只產生一個輸出，我們可以假設模型正在從該機率分佈中選擇機率最高的單詞，並丟棄其餘部分。這是其中一種方法（稱為貪婪解碼 greedy decoding）。另一種方法是保留，例如，前兩個單詞（例如「I」和「a」），然後在下一步中運行模型兩次：一次假設第一個輸出位置是單詞「I」，另一次假設第一個輸出位置是單詞「a」，並選擇在考慮位置 #1 和 #2 之後誤差較小的版本。我們對位置 #2 和 #3 重複此操作……以此類推。這種方法稱為束搜索 (beam search)，在我們的範例中，`beam_t_size` 為 $2$（這意味著在任何時候，記憶體中都會保留兩個部分假設（未完成的翻譯）），且 `top_beams` 也是 $2$（這意味著我們將返回兩個翻譯）。這些都是你可以進行實驗的超參數。

## 前往並轉換吧 (Go Forth And Transform)

我希望你覺得這是一個開始接觸 Transformer 主要概念的有用起點。如果你想深入研究，我建議以下後續步驟：

後續研究：

## 致謝 (Acknowledgements)

感謝 Illia Polosukhin, Jakob Uszkoreit, Llion Jones, Lukasz Kaiser, Niki Parmar, 和 Noam Shazeer 為本文的早期版本提供反饋。

如有任何更正或反饋，請在 Twitter 上聯繫我。

![CC License](https://i.creativecommons.org/l/by-nc-sa/4.0/88x31.png)
