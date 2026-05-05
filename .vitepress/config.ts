import { defineConfig } from 'vitepress'
import fs from 'node:fs'
import path from 'node:path'
import type { Plugin } from 'vite'

// ── Vite plugin: escape C++ template syntax to avoid Vue SFC parsing ──
function cppEscapePlugin(): Plugin {
  return {
    name: 'cpp-escape',
    enforce: 'pre',
    transform(code, id) {
      if (!id.endsWith('.md')) return
      code = code.replace(/<([A-Za-z_][\w:*&,\s<>]*?)>/g, (match, inner) => {
        if (/^<\/?(?:div|span|p|a|img|h[1-6]|ul|ol|li|table|tr|td|th|thead|tbody|br|hr|code|pre|strong|em|b|i|u|s|script|style|template|slot|component|section|header|footer|nav|main|aside|article|form|input|button|select|option|label|textarea|link|meta|head|body|html|iframe|svg|path|circle|rect|g|video|audio|source|canvas|v-[a-z-]+)[\s>/]/i.test(match)) {
          return match
        }
        return '&lt;' + inner + '&gt;'
      })
      return code
    }
  }
}

// ── Rewrites: file path → clean URL ──
const MANIFEST_PATH = path.resolve(__dirname, '../ue-book/manifest.json')
const SRC_DOCS = path.resolve(__dirname, '../ue-book/docs')
const rewrites: Record<string, string> = {}

// Track which names already have a 5.7 entry from manifest (to avoid FS dup)
const has5_7 = new Set<string>()

if (fs.existsSync(MANIFEST_PATH)) {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf-8'))
  const plugins = manifest.plugins || {}

  for (const [name, info] of Object.entries(plugins)) {
    const docPath = (info as any).doc_path || ''
    const version = (info as any).generated_in || ''
    let srcBase = docPath.replace(/^docs\//, '').replace(/\/$/, '')
    if (version === '5.7') {
      srcBase = srcBase.replace(/^5\.7\//, '')
      has5_7.add(name)
    }
    rewrites[`${srcBase}/:path*`] = `${version}/${name}/:path*`
  }
}

// FS leftovers: V1 dirs whose name is NOT already registered as 5.7 in manifest
const SIZE_DIRS = ['small', 'medium', 'large', 'xlarge']
for (const sd of SIZE_DIRS) {
  const dir = path.join(SRC_DOCS, sd)
  if (!fs.existsSync(dir)) continue
  for (const name of fs.readdirSync(dir)) {
    if (has5_7.has(name)) continue
    const key = `${sd}/${name}/:path*`
    if (rewrites[key]) continue
    rewrites[key] = `5.7/${name}/:path*`
  }
}

console.log(`[config] Generated ${Object.keys(rewrites).length} rewrites`)

export default defineConfig({
  title: 'UE-Book',
  description: 'Unreal Engine 开发者知识库',
  srcDir: 'ue-book/docs',

  rewrites,

  vite: {
    plugins: [cppEscapePlugin()],
    resolve: {
      preserveSymlinks: true,
    },
  },

  ignoreDeadLinks: true,
  markdown: { html: true },

  themeConfig: {
    nav: [
      { text: '内置插件', link: '/plugins/' },
      { text: '开源库', link: '/libraries/' },
      { text: '最近更新', link: '/updates/' },
      { text: 'GitHub', link: 'https://github.com/kisspread/UE-Book' },
    ],
    socialLinks: [
      { icon: 'github', link: 'https://github.com/kisspread/UE-Book' },
    ],
    search: { provider: 'local' },
    sidebar: {
      '/libraries/': 'auto',
      '/plugins/': false,
      '/updates/': false,
    },
  },
})
