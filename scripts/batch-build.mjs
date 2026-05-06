import fs from 'node:fs'
import path from 'node:path'
import { execSync } from 'node:child_process'
import { fileURLToPath } from 'node:url'

const __dirname = path.dirname(fileURLToPath(import.meta.url))
const rootDir = path.resolve(__dirname, '..')

// --- 🔥 修复这里的路径：明确指定各种目录的位置 ---
const docsDir = path.join(rootDir, 'ue-book/docs')
const outDir = path.join(rootDir, '.vitepress/dist') // 确保找的是根目录的 .vitepress
const finalOutDir = path.join(rootDir, 'dist-final')
const excludeFile = path.join(rootDir, '.batch-exclude.json')
// ------------------------------------------------

const cacheDir = path.join(rootDir, '.vitepress/cache')
if (fs.existsSync(cacheDir)) {
  console.log(`[Batch Build] 清理 Vite 缓存...`)
  fs.rmSync(cacheDir, { recursive: true, force: true })
}

function getMdFiles(dir, baseDir = '') {
  let fileList = []
  const files = fs.readdirSync(dir)
  for (const file of files) {
    const fullPath = path.join(dir, file)
    const relPath = path.join(baseDir, file)
    if (fs.statSync(fullPath).isDirectory()) {
      if (!file.startsWith('.') && file !== 'public') {
        fileList = fileList.concat(getMdFiles(fullPath, relPath))
      }
    } else if (file.endsWith('.md')) {
      fileList.push(relPath.replace(/\\/g, '/'))
    }
  }
  return fileList
}

const allMdFiles = getMdFiles(docsDir)
const docsFiles = allMdFiles.filter(f => f !== 'index.md')
const BATCH_TOTAL = 4 
const batchSize = Math.ceil(docsFiles.length / BATCH_TOTAL)

if (fs.existsSync(finalOutDir)) {
  fs.rmSync(finalOutDir, { recursive: true, force: true })
}
fs.mkdirSync(finalOutDir, { recursive: true })

for (let i = 0; i < BATCH_TOTAL; i++) {
  console.log(`\n========================================`)
  console.log(`🚀 正在执行第 ${i + 1} 批 / 共 ${BATCH_TOTAL} 批`)
  console.log(`========================================\n`)

  const start = i * batchSize
  const end = start + batchSize
  const currentBatchFiles = new Set(docsFiles.slice(start, end))
  const excludeFiles = docsFiles.filter(f => !currentBatchFiles.has(f))
  
  fs.writeFileSync(excludeFile, JSON.stringify(excludeFiles))

  try {
    execSync('npx vitepress build', {
      stdio: 'inherit',
      env: { ...process.env, NODE_OPTIONS: '--max-old-space-size=8192' }
    })
  } catch (err) {
    console.error(`❌ 第 ${i + 1} 批编译失败！`)
    process.exit(1)
  }

  console.log(`📦 [Batch Build] 合并第 ${i + 1} 批的产物...`)
  // 🔥 修复：使用 Node 原生 API 复制，告别 cp 命令的通配符报错
  if (fs.existsSync(outDir)) {
    fs.cpSync(outDir, finalOutDir, { recursive: true })
  } else {
    console.error(`❌ 找不到构建产物，检查路径: ${outDir}`)
    process.exit(1)
  }
}

if (fs.existsSync(excludeFile)) fs.rmSync(excludeFile)
console.log(`\n✅ 所有分批编译及合并完成！最终产物位于 dist-final 目录。`)