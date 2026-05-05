import { defineConfig } from 'vitepress'
import fs from 'node:fs'
import path from 'node:path'

const MANIFEST_PATH = path.resolve(__dirname, '../ue-book/manifest.json')
const SRC_DOCS = path.resolve(__dirname, '../ue-book/docs')
const rewrites: Record<string, string> = {}

// ── From manifest ──
const manifestPlugins = new Set<string>()

if (fs.existsSync(MANIFEST_PATH)) {
  const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf-8'))
  const plugins = manifest.plugins || {}

  for (const [name, info] of Object.entries(plugins)) {
    const docPath = (info as any).doc_path || ''
    const version = (info as any).generated_in || ''

    let srcBase = docPath.replace(/^docs\//, '').replace(/\/$/, '')
    if (version === '5.7') srcBase = srcBase.replace(/^5\.7\//, '')
    rewrites[`${srcBase}/:path*`] = `${version}/${name}/:path*`
    manifestPlugins.add(name)
  }
}

// ── From filesystem: V1 leftovers not in manifest (e.g. small/ADM/) ──
const SIZE_DIRS = ['small', 'medium', 'large', 'xlarge']
for (const sd of SIZE_DIRS) {
  const dir = path.join(SRC_DOCS, sd)
  if (!fs.existsSync(dir)) continue
  for (const name of fs.readdirSync(dir)) {
    if (manifestPlugins.has(name)) continue
    const key = `${sd}/${name}/:path*`
    if (rewrites[key]) continue
    rewrites[key] = `5.7/${name}/:path*`
  }
}

console.log(`[config] Generated ${Object.keys(rewrites).length} rewrites`)

export default defineConfig({
  title: 'UE-Book',
  description: 'UE5 Plugin Documentation',
  srcDir: 'ue-book/docs',

  rewrites,

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
