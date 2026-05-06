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
      if (!id.endsWith('.md')) return null
      if (!code.includes('<')) return null
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

// ----  读取脚本生成的分批排除黑名单 ----
let srcExclude: string[] = []
const excludeFilePath = path.resolve(__dirname, '../.batch-exclude.json')
if (fs.existsSync(excludeFilePath)) {
  console.log(`[config] 读取分批排除文件: ${excludeFilePath}`)
  srcExclude = JSON.parse(fs.readFileSync(excludeFilePath, 'utf-8'))
  console.log(`[config] 分批模式启动：忽略 ${srcExclude.length} 个文件不参与此次编译`)
}



// ── Rewrites: scan filesystem for all plugin dirs ──
// docs/5.7/small/Name/:path* → 5.7/Name/:path*
// Dedup: manifest size wins when same plugin exists in multiple sizes
const DOCS_DIR = path.resolve(__dirname, '../ue-book/docs')
const MANIFEST_PATH = path.resolve(__dirname, '../ue-book/manifest.json')
const SIZE_DIRS = ['small', 'medium', 'large', 'xlarge']
const rewrites: Record<string, string> = {}

// Build (ver, name) → size priority map from raw manifest
const manifestSizeMap = new Map<string, string>()
if (fs.existsSync(MANIFEST_PATH)) {
  const rawManifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf-8'))
  const plugins = rawManifest.plugins || {}
  for (const [name, info] of Object.entries(plugins)) {
    const v = (info as any).generated_in
    const s = (info as any).size
    if (v && s) manifestSizeMap.set(v + '/' + name, s as string)
  }
}

const seenRewrite = new Set<string>()  // "ver/name"
for (const ver of ['5.7', '5.8']) {
  for (const size of SIZE_DIRS) {
    const sizeDir = path.join(DOCS_DIR, ver, size)
    if (!fs.existsSync(sizeDir)) continue
    for (const name of fs.readdirSync(sizeDir)) {
      const pluginDir = path.join(sizeDir, name)
      if (!fs.statSync(pluginDir).isDirectory()) continue
      const key = ver + '/' + name
      // Manifest-defined size wins; for others, first-seen
      const expectedSize = manifestSizeMap.get(key)
      if (expectedSize && size !== expectedSize) continue  // wrong size, skip
      if (seenRewrite.has(key)) continue  // already got this (ver,name) from a better size
      seenRewrite.add(key)
      const srcBase = [ver, size, name].join('/')
      rewrites[srcBase + '/:path*'] = key + '/:path*'
    }
  }
}

// ── Sidebar: auto-generated for multi-module plugins ──
const SIDEBAR_PATH = path.resolve(__dirname, '../ue-book/docs/public/sidebar.json')
let sidebar: any = {}
if (fs.existsSync(SIDEBAR_PATH)) {
  sidebar = JSON.parse(fs.readFileSync(SIDEBAR_PATH, 'utf-8'))
}

// ── Updates sidebar: monthly + weekly reports, grouped ──
const UPDATES_DIR = path.resolve(__dirname, '../ue-book/docs/updates')
const allUpdateFiles = fs.readdirSync(UPDATES_DIR)
  .filter(f => f.endsWith('.md'))

const monthlyFiles = allUpdateFiles
  .filter(f => /^\d{4}-\d{2}\.md$/.test(f))
  .sort().reverse()
const weeklyFiles = allUpdateFiles
  .filter(f => /^\d{4}-\d{2}-\d{2}\.md$/.test(f))
  .sort().reverse()

const updatesSidebar: any[] = []

if (monthlyFiles.length > 0) {
  updatesSidebar.push({
    text: '月报',
    collapsed: false,
    items: monthlyFiles.map(f => {
      const slug = f.replace('.md', '')
      const [y, m] = slug.split('-')
      return { text: `${y}年${m}月`, link: `/updates/${slug}` }
    }),
  })
}

if (weeklyFiles.length > 0) {
  updatesSidebar.push({
    text: '周报',
    collapsed: true,
    items: weeklyFiles.map(f => {
      const slug = f.replace('.md', '')
      const [, m, d] = slug.split('-')
      return { text: `${parseInt(m)}月${parseInt(d)}日`, link: `/updates/${slug}` }
    }),
  })
}

if (updatesSidebar.length > 0) {
  sidebar['/updates/'] = updatesSidebar
}

console.log('[config] Generated ' + Object.keys(rewrites).length + ' rewrites')
console.log('[config] Sidebar entries: ' + (typeof sidebar === 'object' ? Object.keys(sidebar).length : 0))

export default defineConfig({
  title: 'UE-Book',
  description: 'Unreal Engine 开发者知识库',
  srcDir: 'ue-book/docs',
  base: '/UE-Book/',
  srcExclude,

  head: [
    ['meta', { name: 'algolia-site-verification', content: '2A8BC67DA6BC61B3' }]
  ],

  rewrites,

  vite: {
    //plugins: [cppEscapePlugin()],
    resolve: {
      preserveSymlinks: true,
    },
  //  build: {
  //     // 降低 chunk 警告阈值，避免控制台输出过多警告占用内存
  //     chunkSizeWarningLimit: 2000,
  //     rollupOptions: {
  //       // 关键优化：关闭 Rollup 构建缓存，极大降低海量多页应用的内存峰值
  //       cache: false,
  //       // 限制并发文件操作数，缓解瞬间内存飙升
  //       maxParallelFileOps: 2, 
  //     }
  //   }
  },


  ignoreDeadLinks: true,
  markdown: {
    html: true,
    config: (md) => {
      // 定义常见的合法 HTML 标签（你之前正则里的那些）
      const htmlTags = /^\/?(?:div|span|p|a|img|h[1-6]|ul|ol|li|table|tr|td|th|thead|tbody|br|hr|code|pre|strong|em|b|i|u|s|script|style|template|slot|component|section|header|footer|nav|main|aside|article|form|input|button|select|option|label|textarea|link|meta|head|body|html|iframe|svg|path|circle|rect|g|video|audio|source|canvas|v-[a-z-]+)[\s>]/i;

      // 注册一个底层的 AST 处理规则
      md.core.ruler.push('escape_cpp_templates', (state) => {
        // 遍历所有的 AST 节点
        state.tokens.forEach((blockToken) => {
          if (blockToken.type === 'inline' && blockToken.children) {
            blockToken.children.forEach((token) => {
              // Markdown-it 会把 <FString> 误认为是 html_inline
              if (token.type === 'html_inline') {
                // 如果这个标签不是标准的 HTML 标签
                if (!htmlTags.test(token.content.replace(/^</, ''))) {
                  // 将其强制降级为纯文本，并转义尖括号
                  token.type = 'text';
                  token.content = token.content.replace(/</g, '&lt;').replace(/>/g, '&gt;');
                }
              }
            });
          }
        });
      });
    }
  },

  // 限制并发渲染，降低内存峰值（604 页）
  concurrency: 1,

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
    //search: { provider: 'local' },
    search: {
      provider: 'algolia',
      options: {
        appId: 'SG54SSJIT8',
        apiKey: '00000000000000000000000000000000',
        indexName: 'kisspread_ue_book'
      }
    },
    sidebar,
  },
})
