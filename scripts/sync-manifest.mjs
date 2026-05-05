#!/usr/bin/env node

/**
 * sync-manifest.mjs
 * 
 * 从 ue-book/manifest.json + markdown 文件提取元数据，
 * 生成 ue-book/docs/public/manifest.json（供前端 fetch）。
 * 
 * 不再复制文件。VitePress 通过 rewrites 直读 ue-book/docs/。
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const MANIFEST_PATH = path.join(ROOT, 'ue-book', 'manifest.json');
const SRC_DOCS = path.join(ROOT, 'ue-book', 'docs');
const OUT_MANIFEST = path.join(ROOT, 'ue-book', 'docs', 'public', 'manifest.json');

const SIZE_DIRS = ['small', 'medium', 'large', 'xlarge'];

// ── Source path resolution ──
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

// ── Metadata extraction ──
function parseAttributeTable(content) {
  const meta = {};
  const descMatch = content.match(/^> (.+)$/m);
  if (descMatch) meta.description = descMatch[1].trim();
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
      if (key && key !== '属性') meta[key] = match[2].trim();
    }
  }
  return meta;
}

function extractDescriptionCN(content) {
  const match = content.match(/## 用途\s*\n+([\s\S]{20,300}?)(?=\n\n|##|\n#)/);
  if (!match) return null;
  let text = match[1].replace(/\n/g, ' ').replace(/\s+/g, ' ').trim();
  text = text.replace(/\*\*/g, '').replace(/\[([^\]]+)\]\([^)]+\)/g, '$1').replace(/`([^`]+)`/g, '$1');
  if (text.length > 150) text = text.substring(0, 150) + '…';
  return text;
}

// ── Category normalization ──
const CATEGORY_ALIASES = {
  'Virtual Production': 'VirtualProduction',
  'Virtual Production (DMX)': 'VirtualProduction',
  'VirtualProduction (Misc)': 'VirtualProduction',
  'VirtualProduction (原 Experimental)': 'VirtualProduction',
  'Messaging (VirtualProduction)': 'VirtualProduction',
  'Animation (Experimental)': 'Animation',
  'Misc (Editor)': 'Misc', 'Other': 'Misc',
  'Online Platform': 'Online', 'Online': 'Online',
  'Developer (Examples)': 'Developer',
  'Developer (Folder) / Rendering (.uplugin Category)': 'Developer',
  'Developer (路径) / UI (.uplugin)': 'Developer',
  'Media Players': 'Media', 'Player': 'Media',
  'PCGInterops (原 Editor)': 'PCG',
  'Runtime (PacketHandlers)': 'Runtime',
  'Importers': 'Import/Export', 'Exporters': 'Import/Export',
  'Android Background Service': 'Android',
  'Gameplay Streaming': 'Gameplay',
};
function normalizeCategory(cat) { return CATEGORY_ALIASES[cat] || cat; }

// ── Build entry ──
function buildEntry(rawMeta, pluginName, version, size, content) {
  const entry = {
    name: pluginName,
    name_cn: rawMeta['中文名'] || null,
    version, size,
    link: `/${version}/${pluginName}/`,
    description: rawMeta.description || null,
    description_cn: extractDescriptionCN(content),
  };
  const cat = rawMeta['分类']; if (cat) entry.category = normalizeCategory(cat);
  if (rawMeta['默认启用']) entry.enabled_by_default = rawMeta['默认启用'].includes('是') || rawMeta['默认启用'].includes('✅');
  if (rawMeta['包含内容']) entry.has_content = rawMeta['包含内容'].includes('有') || rawMeta['包含内容'].includes('✅');
  if (rawMeta['模块']) entry.modules = rawMeta['模块'];
  if (rawMeta['实验性']) entry.experimental = rawMeta['实验性'].includes('是') || rawMeta['实验性'].includes('⚠️');
  if (rawMeta['创建时间']) entry.created_at = rawMeta['创建时间'];
  if (rawMeta['源码']) { const m = rawMeta['源码'].match(/\]\(([^)]+)\)/); if (m) entry.source_url = m[1]; }
  if (entry.created_at) {
    const year = parseInt(entry.created_at.substring(0, 4), 10);
    if (year <= 2016) entry.age_tier = 'relic';
    else if (year <= 2021) entry.age_tier = 'old';
    else entry.age_tier = 'fresh';
  }
  return entry;
}

// ── Main ──
console.log('Sync-manifest — reading manifest...');
const manifest = JSON.parse(fs.readFileSync(MANIFEST_PATH, 'utf-8'));
const plugins = manifest.plugins;
console.log(`  ${Object.keys(plugins).length} plugins in manifest`);

// Load existing translations
let existingNames = {};
if (fs.existsSync(OUT_MANIFEST)) {
  try {
    const old = JSON.parse(fs.readFileSync(OUT_MANIFEST, 'utf-8'));
    for (const p of (old.plugins || [])) {
      if (p.name_cn) existingNames[p.name] = p.name_cn;
    }
    console.log(`  Loaded ${Object.keys(existingNames).length} existing name_cn`);
  } catch (e) { /* ignore */ }
}

const allPlugins = [];
let withCN = 0, withDescCN = 0, errors = 0;

for (const [pluginName, info] of Object.entries(plugins)) {
  const { generated_in: version, size, doc_path: docPath } = info;
  const srcDir = resolveSourcePath(docPath, version);
  if (!fs.existsSync(srcDir)) { errors++; continue; }

  const indexFile = path.join(srcDir, 'index.md');
  if (fs.existsSync(indexFile)) {
    const content = fs.readFileSync(indexFile, 'utf-8');
    const entry = buildEntry(parseAttributeTable(content), pluginName, version, size, content);
    if (!entry.name_cn && existingNames[pluginName]) entry.name_cn = existingNames[pluginName];
    if (entry.name_cn) withCN++;
    if (entry.description_cn) withDescCN++;
    allPlugins.push(entry);
  } else {
    allPlugins.push({ name: pluginName, name_cn: existingNames[pluginName] || null, version, size, link: `/${version}/${pluginName}/` });
  }
}

allPlugins.sort((a, b) => a.name.localeCompare(b.name));

const output = { versions: manifest.versions, plugins: allPlugins };
fs.mkdirSync(path.dirname(OUT_MANIFEST), { recursive: true });
fs.writeFileSync(OUT_MANIFEST, JSON.stringify(output, null, 2), 'utf-8');

const tiers = { relic: 0, old: 0, fresh: 0 };
allPlugins.forEach(p => { if (p.age_tier) tiers[p.age_tier]++; });
const cats = new Set(allPlugins.map(p => p.category).filter(Boolean));

console.log(`\n=== Sync Complete ===`);
console.log(`  Total: ${allPlugins.length} plugins  Errors: ${errors}`);
console.log(`  name_cn: ${withCN}  description_cn: ${withDescCN}`);
console.log(`  Categories: ${cats.size}  Age: 🏛️${tiers.relic} 👴${tiers.old} 🥩${tiers.fresh}`);
console.log(`  Output: ${OUT_MANIFEST}`);
