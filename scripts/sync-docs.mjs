#!/usr/bin/env node

/**
 * sync-docs.mjs v2
 * 
 * 1. 读取 ue-book/manifest.json
 * 2. 将文档从 ue-book/docs/ 复制到 docs/{version}/{PluginName}/
 * 3. 解析每个 index.md 的属性表 + "## 用途" 中文描述
 * 4. 输出 docs/public/manifest.json（plugins 数组，含 name_cn 占位）
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const MANIFEST_PATH = path.join(ROOT, 'ue-book', 'manifest.json');
const SRC_DOCS = path.join(ROOT, 'ue-book', 'docs');
const DST_DOCS = path.join(ROOT, 'docs');
const OUT_MANIFEST = path.join(ROOT, 'docs', 'public', 'manifest.json');

const SIZE_DIRS = ['small', 'medium', 'large', 'xlarge'];

// ============================================================
// Source path resolution
// ============================================================
function resolveSourcePath(docPath, version) {
  const relative = docPath.replace(/^docs\//, '');

  if (version === '5.7') {
    const withoutVersion = relative.replace(/^5\.7\//, '');
    const directPath = path.join(SRC_DOCS, withoutVersion);
    if (fs.existsSync(directPath)) return directPath;

    const pluginName = withoutVersion.replace(/\/$/, '');
    if (!pluginName.includes('/')) {
      for (const sizeDir of SIZE_DIRS) {
        const probe = path.join(SRC_DOCS, sizeDir, pluginName);
        if (fs.existsSync(probe)) return probe;
      }
    }
    return directPath;
  }

  const directPath = path.join(SRC_DOCS, relative);
  if (fs.existsSync(directPath)) return directPath;

  const pluginName = relative.replace(/^5\.8\/[^/]+\//, '').replace(/\/$/, '');
  for (const sizeDir of SIZE_DIRS) {
    const probe = path.join(SRC_DOCS, version, sizeDir, pluginName);
    if (fs.existsSync(probe)) return probe;
  }

  return directPath;
}

// ============================================================
// Metadata extraction from index.md
// ============================================================
function parseAttributeTable(content) {
  const meta = {};

  const descMatch = content.match(/^> (.+)$/m);
  if (descMatch) meta.description = descMatch[1].trim();

  // Line-by-line table parsing
  const lines = content.split('\n');
  let inTable = false;
  for (const line of lines) {
    const trimmed = line.trim();
    if (trimmed === '| 属性 | 值 |') { inTable = true; continue; }
    if (trimmed === '|---|---|') continue;
    if (!inTable) continue;
    if (!trimmed.startsWith('|')) { inTable = false; continue; }

    const match = trimmed.match(/^\| ([^|]*) \| ([^|]*) \|/);
    if (match) {
      const key = match[1].trim();
      const value = match[2].trim();
      if (key && key !== '属性') meta[key] = value;
    }
  }

  return meta;
}

/**
 * Extract Chinese description from "## 用途" section.
 * Takes the first substantive paragraph (20-300 chars of Chinese-heavy text).
 */
function extractDescriptionCN(content) {
  // Find "## 用途" and grab the next paragraph
  const match = content.match(/## 用途\s*\n+([\s\S]{20,300}?)(?=\n\n|##|\n#)/);
  if (!match) return null;
  let text = match[1].replace(/\n/g, ' ').replace(/\s+/g, ' ').trim();
  // Remove markdown bold markers
  text = text.replace(/\*\*/g, '');
  // Remove markdown links
  text = text.replace(/\[([^\]]+)\]\([^)]+\)/g, '$1');
  // Remove backtick code
  text = text.replace(/`([^`]+)`/g, '$1');
  if (text.length > 150) text = text.substring(0, 150) + '…';
  return text;
}

// ============================================================
// Category normalization
// ============================================================
const CATEGORY_ALIASES = {
  'Virtual Production': 'VirtualProduction',
  'Virtual Production (DMX)': 'VirtualProduction',
  'VirtualProduction (Misc)': 'VirtualProduction',
  'VirtualProduction (原 Experimental)': 'VirtualProduction',
  'Messaging (VirtualProduction)': 'VirtualProduction',
  'Animation (Experimental)': 'Animation',
  'Misc (Editor)': 'Misc',
  'Other': 'Misc',
  'Online Platform': 'Online',
  'Online': 'Online',
  'Developer (Examples)': 'Developer',
  'Developer (Folder) / Rendering (.uplugin Category)': 'Developer',
  'Developer (路径) / UI (.uplugin)': 'Developer',
  'Media Players': 'Media',
  'Player': 'Media',
  'PCGInterops (原 Editor)': 'PCG',
  'Runtime (PacketHandlers)': 'Runtime',
  'Importers': 'Import/Export',
  'Exporters': 'Import/Export',
  'Android Background Service': 'Android',
  'Gameplay Streaming': 'Gameplay',
};

function normalizeCategory(cat) {
  return CATEGORY_ALIASES[cat] || cat;
}

// ============================================================
// Build plugin entry from raw md metadata
// ============================================================
function buildPluginEntry(rawMeta, pluginName, version, size, content) {
  const entry = {
    name: pluginName,
    name_cn: null,              // to be filled by translation script
    version,
    size,
    link: `/${version}/${pluginName}/`,
    description: rawMeta.description || null,
    description_cn: extractDescriptionCN(content),
  };

  // Attribute table fields
  const cnName = rawMeta['中文名'];
  if (cnName) entry.name_cn = cnName;  // priority: from md (pipeline-generated)

  const cat = rawMeta['分类'];
  if (cat) entry.category = normalizeCategory(cat);

  const enabled = rawMeta['默认启用'];
  if (enabled) entry.enabled_by_default = enabled.includes('是') || enabled.includes('✅');

  const hasContent = rawMeta['包含内容'];
  if (hasContent) entry.has_content = hasContent.includes('有') || hasContent.includes('✅');

  const modules = rawMeta['模块'];
  if (modules) entry.modules = modules;

  const experimental = rawMeta['实验性'];
  if (experimental) entry.experimental = experimental.includes('是') || experimental.includes('⚠️');

  const createdAt = rawMeta['创建时间'];
  if (createdAt) entry.created_at = createdAt;

  const sourceUrl = rawMeta['源码'];
  if (sourceUrl) {
    const urlMatch = sourceUrl.match(/\]\(([^)]+)\)/);
    entry.source_url = urlMatch ? urlMatch[1] : sourceUrl;
  }

  // Age tier from created_at
  if (entry.created_at) {
    const year = parseInt(entry.created_at.substring(0, 4), 10);
    if (year <= 2016) entry.age_tier = 'relic';
    else if (year <= 2021) entry.age_tier = 'old';
    else entry.age_tier = 'fresh';
  }

  return entry;
}

// ============================================================
// Main
// ============================================================
console.log('Sync-docs v2 — reading manifest...');

const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf-8'));
const plugins = manifest.plugins;
console.log(`  ${Object.keys(plugins).length} plugins in manifest`);

// 不覆盖已有翻译：从旧 manifest.json 读取已有的 name_cn
let existingNames = {};
const oldManifest = path.join(ROOT, 'docs', 'public', 'manifest.json');
if (fs.existsSync(oldManifest)) {
  try {
    const old = JSON.parse(fs.readFileSync(oldManifest, 'utf-8'));
    for (const p of (old.plugins || [])) {
      if (p.name_cn) existingNames[p.name] = p.name_cn;
    }
    console.log(`  Loaded ${Object.keys(existingNames).length} existing name_cn from previous run`);
  } catch (e) { /* ignore */ }
}

const allPlugins = [];
let copied = 0, errors = 0, withCN = 0;

// Clear version dirs
for (const ver of ['5.7', '5.8']) {
  const d = path.join(DST_DOCS, ver);
  if (fs.existsSync(d)) fs.rmSync(d, { recursive: true });
}

for (const [pluginName, info] of Object.entries(plugins)) {
  const { generated_in: version, size, doc_path: docPath } = info;

  const srcDir = resolveSourcePath(docPath, version);
  if (!fs.existsSync(srcDir)) { errors++; continue; }

  const dstDir = path.join(DST_DOCS, version, pluginName);
  fs.cpSync(srcDir, dstDir, { recursive: true });
  copied++;

  const indexFile = path.join(dstDir, 'index.md');
  if (fs.existsSync(indexFile)) {
    const content = fs.readFileSync(indexFile, 'utf-8');
    const rawMeta = parseAttributeTable(content);
    const entry = buildPluginEntry(rawMeta, pluginName, version, size, content);

    // Preserve existing translations (fallback when md has no 中文名)
    if (!entry.name_cn && existingNames[pluginName]) {
      entry.name_cn = existingNames[pluginName];
      withCN++;
    } else if (entry.name_cn) {
      withCN++;
    }

    allPlugins.push(entry);
  } else {
    allPlugins.push({ name: pluginName, name_cn: null, version, size, link: `/${version}/${pluginName}/` });
  }
}

// Sort alphabetically by name
allPlugins.sort((a, b) => a.name.localeCompare(b.name));

// Write output
const output = {
  versions: manifest.versions,
  plugins: allPlugins,
};

fs.mkdirSync(path.dirname(OUT_MANIFEST), { recursive: true });
fs.writeFileSync(OUT_MANIFEST, JSON.stringify(output, null, 2), 'utf-8');

// Summary
const cats = new Set(allPlugins.map(p => p.category).filter(Boolean));
const tiers = { relic: 0, old: 0, fresh: 0 };
let withDescCN = 0;
allPlugins.forEach(p => {
  if (p.age_tier) tiers[p.age_tier]++;
  if (p.description_cn) withDescCN++;
});

console.log(`\n=== Sync Complete ===`);
console.log(`  Copied: ${copied}  Errors: ${errors}`);
console.log(`  Total plugins: ${allPlugins.length}`);
console.log(`  Has description_cn: ${withDescCN}`);
console.log(`  Has name_cn: ${withCN} / ${allPlugins.length} remaining`);
console.log(`  Categories: ${cats.size}`);
console.log(`  Age: 🏛️${tiers.relic} 👴${tiers.old} 🥩${tiers.fresh}`);
