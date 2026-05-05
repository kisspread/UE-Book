import { defineConfig } from 'vitepress'
import fs from 'node:fs'
import path from 'node:path'
import type { Plugin } from 'vite'

// ── Vite plugin: escape angle brackets in C++ code blocks to avoid Vue SFC parsing ──
function cppEscapePlugin(): Plugin {
  return {
    name: 'cpp-escape',
    enforce: 'pre',
    transform(code, id) {
      if (!id.endsWith('.md')) return

      // Escape C++ template syntax that looks like HTML tags:
      // <float>, <T>, <const float>, <UMovieSceneSection*>, etc.
      // Pattern: < followed by C++ identifiers/operators, NOT HTML tags like <div>, <script>
      code = code.replace(/<([A-Za-z_][\w:*&,\s<>]*?)>/g, (match, inner) => {
        // Skip known HTML tags and Vue directives (with optional closing slash)
        if (/^<\/?(?:div|span|p|a|img|h[1-6]|ul|ol|li|table|tr|td|th|thead|tbody|br|hr|code|pre|strong|em|b|i|u|s|script|style|template|slot|component|section|header|footer|nav|main|aside|article|form|input|button|select|option|label|textarea|link|meta|head|body|html|iframe|svg|path|circle|rect|g|video|audio|source|canvas|v-[a-z-]+)[\s>/]/i.test(match)) {
          return match
        }
        // C++ template syntax like TArray<float>, std::vector<int*>
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

// FS leftovers
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

  vite: {
    plugins: [cppEscapePlugin()]
  },

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
