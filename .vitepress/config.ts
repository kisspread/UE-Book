import { defineConfig } from 'vitepress'
import type { Plugin } from 'vite'

// Vite plugin: escape HTML-like patterns in markdown before Vue compiler sees them
function escapeUeTemplates(): Plugin {
  return {
    name: 'escape-ue-templates',
    enforce: 'pre',
    transform(code: string, id: string) {
      if (!id.endsWith('.md')) return null

      const lines = code.split('\n')
      const result: string[] = []
      let inCode = false

      for (const line of lines) {
        if (line.trimStart().startsWith('```')) {
          inCode = !inCode
          result.push(line)
          continue
        }

        if (inCode) {
          // In code blocks: escape < > that look like C++ templates
          result.push(
            line
              .replace(/&/g, '&amp;')
              .replace(/</g, '&lt;')
              .replace(/>/g, '&gt;')
          )
        } else {
          // In text: escape C++ template syntax like TArray<float>
          let l = line
          l = l.replace(/(\w)<([A-Za-z_])/g, '$1&lt;$2')
          l = l.replace(/([A-Za-z_0-9])>/g, '$1&gt;')
          result.push(l)
        }
      }

      return { code: result.join('\n'), map: null }
    },
  }
}

export default defineConfig({
  title: 'UE-Book',
  description: 'UE5 Plugin Documentation',
  srcDir: 'ue-book/docs',

  ignoreDeadLinks: true,

  vite: {
    plugins: [escapeUeTemplates()],
  },

  markdown: {
    html: true,
  },

  themeConfig: {
    nav: [
      { text: '5.8 (Latest)', link: '/5.8/' },
      { text: '5.7', link: '/small/' },
      { text: 'GitHub', link: 'https://github.com/kisspread/UE-Book' },
    ],

    socialLinks: [
      { icon: 'github', link: 'https://github.com/kisspread/UE-Book' },
    ],

    search: {
      provider: 'local',
    },
  },
})
