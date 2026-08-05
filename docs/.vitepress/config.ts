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
    // Font Awesome linear icons
    ['link', { rel: 'stylesheet', href: 'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.5.1/css/all.min.css' }],
  ],

  themeConfig: {
    logo: false,
    siteTitle: false,
    nav: [],

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