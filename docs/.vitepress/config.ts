import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'MLLM安全日报',
  description: 'MLLM/VLM 多模态大模型安全学术资讯自动聚合平台',
  lang: 'zh-CN',
  base: '/',
  lastUpdated: true,
  cleanUrls: true,

  head: [
    ['link', { rel: 'icon', href: '/favicon.ico' }],
    ['meta', { name: 'theme-color', content: '#1a365d' }],
  ],

  themeConfig: {
    logo: false,
    siteTitle: '🔬 MLLM安全日报',
    nav: [
      { text: '首页', link: '/' },
      { text: '每日日报', link: '/daily' },
      { text: '月度汇总', link: '/monthly' },
      { text: '⚠️ 后门专题', link: '/backdoor' },
      { text: '数据源说明', link: '/sources' },
    ],

    socialLinks: [],

    search: {
      provider: 'local',
    },

    outline: false,
  },

  vue: {
    template: {
      compilerOptions: {
        isCustomElement: (tag) => tag.startsWith('vp-'),
      },
    },
  },
})