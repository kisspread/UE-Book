import { defineConfig } from 'vitepress'

export default defineConfig({
  title: 'UE-Book',
  description: 'UE5 Plugin Documentation',
  srcDir: 'docs',

  ignoreDeadLinks: true,
  markdown: { html: true },

  themeConfig: {
    nav: [
      { text: 'Home', link: '/' },
      { text: '5.8', link: '/5.8/' },
      { text: '5.7', link: '/5.7/' },
      { text: 'GitHub', link: 'https://github.com/kisspread/UE-Book' },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/kisspread/UE-Book' },
    ],
    search: { provider: 'local' },
    sidebar: false,
  },
})
