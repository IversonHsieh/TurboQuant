import { defineConfig } from 'vitepress'

export default defineConfig({
  title: "TurboQuant Deep Dive",
  description: "Exploring the frontiers of efficient LLM quantization",
  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: 'Introduction', link: '/chapters/01-introduction' },
      { text: 'Glossary', link: '/chapters/02-glossary' },
      { text: 'Deep Dive', link: '/chapters/03-deep-dive' }
    ],
    sidebar: [
      {
        text: 'Chapters',
        items: [
          { text: 'Introduction', link: '/chapters/01-introduction' },
          { text: 'Glossary', link: '/chapters/02-glossary' },
          { text: 'Deep Dive', link: '/chapters/03-deep-dive' },
        ]
      }
    ],
    socialLinks: [
      { icon: 'github', link: '#' }
    ]
  }
})
