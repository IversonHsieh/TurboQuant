import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "TurboQuant Deep Dive",
  description: "Exploring the frontiers of efficient LLM quantization",
  base: '/TurboQuant/',
  ignoreDeadLinks: true,
  markdown: {
    math: true
  },
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Introduction', link: '/chapters/01-introduction' },
      { text: 'Glossary', link: '/chapters/02-glossary' },
      { text: 'Deep Dive', link: '/chapters/03-deep-dive' }
    ],
    sidebar: [
      {
        text: '📖 章節 1：簡介',
        items: [
          { text: 'TurboQuant 簡介', link: '/chapters/01-introduction' },
        ]
      },
      {
        text: '📖 章節 2：專有名詞',
        items: [
          { text: '專有名詞總覽', link: '/chapters/02-glossary' },
          { text: '數學基礎', link: '/chapters/02-mathematical-foundations' },
          { text: '座標系統：笛卡兒與極座標', link: '/chapters/02-1-coordinate-systems' },
          { text: '前饋神經網路 (FFN)', link: '/chapters/02-3-ffn' },
          { text: 'Transformer 結構解析', link: '/chapters/02-4-transformer-analysis' },
          { text: 'KV Cache 解析', link: '/chapters/02-4-kv-cache' },
          { text: 'PolarQuant 解析', link: '/chapters/02-5-polarquant-analysis' },
        ]
      },
      {
        text: '🔬 章節 3：技術深度解析',
        items: [
          { text: 'TurboQuant 深度解析', link: '/chapters/03-deep-dive' },
          { text: 'TurboQuant 論文翻譯', link: '/chapters/03-turboquant-translation' },
          { text: 'Beta 分佈', link: '/chapters/03-beta-distribution' },
          { text: '暴力法最近鄰搜尋', link: '/chapters/03-brute-force-nn-explanation' },
          { text: 'Gersho 論文', link: '/chapters/03-gersho-paper' },
          { text: 'Hessian 矩陣', link: '/chapters/03-hessian-information' },
          { text: '內積失真', link: '/chapters/03-inner-product-distortion' },
          { text: '內積誤差', link: '/chapters/03-inner-product-errors' },
          { text: 'K-Means', link: '/chapters/03-k-means-problem' },
          { text: 'L2 範數', link: '/chapters/03-l2-norm-explanation' },
          { text: 'Lloyd-Max 量化器', link: '/chapters/03-lloyd-max-quantizer' },
          { text: 'MSE 均方誤差', link: '/chapters/03-mse-explanation' },
          { text: '最近鄰搜尋', link: '/chapters/03-nearest-neighbor-explanation' },
          { text: '乘積量化 (PQ)', link: '/chapters/03-product-quantization-explanation' },
          { text: 'QJL 詳解', link: '/chapters/03-qjl-explanation' },
          { text: 'Shannon 失真-率函數', link: '/chapters/03-shannon-distortion-rate-function' },
          { text: 'Shannon 信源編碼 (詳細)', link: '/chapters/03-shannon-source-coding-detailed' },
          { text: 'Shannon 信源編碼理論', link: '/chapters/03-shannon-source-coding-theory' },
          { text: '次佳失真界限', link: '/chapters/03-suboptimal-distortion-bounds' },
          { text: '向量量化 (VQ)', link: '/chapters/03-vector-quantization-explanation' },
        ]
      }
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/IversonHsieh/TurboQuant' }
    ]
  }
})
