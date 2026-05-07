#!/usr/bin/env node

/**
 * build-search-index.mjs
 * 
 * 在 VitePress build 之后运行，生成 search-index.json 到 dist/ 目录。
 * 这个 JSON 会被部署到 GitHub Pages，供 search-ue.py 下载搜索。
 * 
 * 索引三部分：
 *   1. plugins  — 从 public manifest + 各插件 index.md 提取
 *   2. updates  — 从 updates/*.md 提取
 *   3. libraries — 从 libraries/index.md 解析
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');

const PUBLIC_MANIFEST = path.join(ROOT, 'ue-book', 'docs', 'public', 'manifest.json');
const INTERNAL_MANIFEST = path.join(ROOT, 'ue-book', 'manifest.json');
const SRC_DOCS = path.join(ROOT, 'ue-book', 'docs');
const UPDATES_DIR = path.join(SRC_DOCS, 'updates');
const LIBRARIES_MD = path.join(SRC_DOCS, 'libraries', 'index.md');
const DIST_DIR = path.join(ROOT, '.vitepress', 'dist');
const OUT_FILE = path.join(DIST_DIR, 'search-index.json');

const RAW_BASE = 'https://raw.githubusercontent.com/kisspread/UE-Book/master/ue-book/';
const SITE_BASE = '/UE-Book';

// ── Helpers ──

/** Extract frontmatter title from markdown */
function extractTitle(mdContent) {
  const m = mdContent.match(/^#\s+(.+)$/m);
  return m ? m[1].trim() : '';
}

/** Strip markdown formatting for plain-text search */
function stripMarkdown(text) {
  return text
    .replace(/^#{1,6}\s+/gm, '')          // headings
    .replace(/\*\*(.+?)\*\*/g, '$1')       // bold
    .replace(/\*(.+?)\*/g, '$1')           // italic
    .replace(/`(.+?)`/g, '$1')             // inline code
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1') // links → text
    .replace(/!\[([^\]]*)\]\([^)]+\)/g, '')  // images → remove
    .replace(/^\s*[-*+>|]\s*/gm, '')       // list bullets, blockquote, table pipes
    .replace(/\n{3,}/g, '\n\n')            // collapse blank lines
    .trim();
}

/** Extract first N chars of meaningful text (skip frontmatter, headings) */
function extractSnippet(mdContent, maxChars = 500) {
  // Remove YAML frontmatter (handles both standard and H1-then-frontmatter formats)
  let text = mdContent.replace(/---[\s\S]*?---\n*/g, '');
  // Remove HTML comments
  text = text.replace(/<!--[\s\S]*?-->/g, '');
  // Strip markdown
  text = stripMarkdown(text);
  // Remove the first H1 heading (title line)
  text = text.replace(/^.+?\n/, '');
  return text.substring(0, maxChars).trim();
}

// ── 1. Plugins ──

function buildPluginIndex() {
  const publicManifest = JSON.parse(fs.readFileSync(PUBLIC_MANIFEST, 'utf-8'));
  const internalManifest = JSON.parse(fs.readFileSync(INTERNAL_MANIFEST, 'utf-8'));
  
  // Build lookup: name → internal manifest entry (has doc_path)
  const internalLookup = {};
  for (const [name, info] of Object.entries(internalManifest.plugins || {})) {
    internalLookup[name] = info;
  }

  const plugins = [];

  for (const p of (publicManifest.plugins || [])) {
    const internal = internalLookup[p.name];
    if (!internal || !internal.doc_path) continue;

    // Read the index.md for content snippet
    const docDir = path.join(ROOT, 'ue-book', internal.doc_path);
    const indexMd = path.join(docDir, 'index.md');
    
    let textContent = '';
    if (fs.existsSync(indexMd)) {
      const mdContent = fs.readFileSync(indexMd, 'utf-8');
      textContent = extractSnippet(mdContent, 500);
    }

    // Build text blob for searching: name + name_cn + description + description_cn + category + snippet
    const text = [
      p.name,
      p.name_cn || '',
      p.description || '',
      p.description_cn || '',
      p.category || '',
      textContent,
    ].join(' ').replace(/\s+/g, ' ').trim();

    plugins.push({
      name: p.name,
      name_cn: p.name_cn || '',
      category: p.category || '',
      version: p.version || '',
      web_url: SITE_BASE + p.link,
      raw_url: RAW_BASE + internal.doc_path + 'index.md',
      text,
    });
  }

  // Deduplicate by name: prefer the one with name_cn (more complete metadata)
  const seen = new Set();
  const deduped = [];
  for (const p of plugins) {
    if (seen.has(p.name)) continue;
    seen.add(p.name);
    deduped.push(p);
  }

  console.log(`[search-index] Plugins: ${deduped.length}`);
  return deduped;
}

// ── 2. Updates ──

function buildUpdatesIndex() {
  const updates = [];

  if (!fs.existsSync(UPDATES_DIR)) {
    console.log('[search-index] Updates: 0 (no updates dir)');
    return updates;
  }

  const files = fs.readdirSync(UPDATES_DIR)
    .filter(f => f.endsWith('.md') && f !== 'index.md')
    .sort();

  for (const file of files) {
    const mdContent = fs.readFileSync(path.join(UPDATES_DIR, file), 'utf-8');
    const title = extractTitle(mdContent);
    const snippet = extractSnippet(mdContent, 1000);
    const slug = file.replace('.md', '');

    updates.push({
      title,
      slug,
      web_url: `${SITE_BASE}/updates/${slug}.html`,
      raw_url: `${RAW_BASE}docs/updates/${file}`,
      text: snippet,
    });
  }

  console.log(`[search-index] Updates: ${updates.length}`);
  return updates;
}

// ── 3. Libraries ──

function buildLibrariesIndex() {
  const libraries = [];

  if (!fs.existsSync(LIBRARIES_MD)) {
    console.log('[search-index] Libraries: 0 (no libraries/index.md)');
    return libraries;
  }

  const content = fs.readFileSync(LIBRARIES_MD, 'utf-8');
  
  // Parse library entries: lines starting with "- [Name](url) ..."
  // Some entries have sub-bullets (indented with "  - ")
  const lines = content.split('\n');
  let currentLib = null;
  let currentCategory = '';

  for (const line of lines) {
    // Track H2 categories
    const catMatch = line.match(/^##\s+(.+)$/);
    if (catMatch) {
      currentCategory = catMatch[1].trim();
      continue;
    }

    // New library entry
    const libMatch = line.match(/^-\s+\[([^\]]+)\]\(([^)]+)\)\s*(.*)$/);
    if (libMatch) {
      // Save previous
      if (currentLib) {
        libraries.push(currentLib);
      }

      const name = libMatch[1].trim();
      const url = libMatch[2].trim();
      const desc = libMatch[3].trim();

      currentLib = {
        name,
        url,
        category: currentCategory,
        text: `${name} ${desc}`,
      };
      continue;
    }

    // Sub-bullet (description continuation)
    if (currentLib && line.match(/^\s{2,}-\s+(.+)/)) {
      const subText = line.replace(/^\s{2,}-\s+/, '').trim();
      // Strip image references
      const cleaned = subText.replace(/!\[.*?\]\(.*?\)/g, '').trim();
      if (cleaned) {
        currentLib.text += ' ' + cleaned;
      }
      // Also strip image-only lines from text
      currentLib.text = currentLib.text.replace(/!\[.*?\]\(.*?\)/g, '').replace(/\s+/g, ' ').trim();
    }
  }

  // Save last entry
  if (currentLib) {
    libraries.push(currentLib);
  }

  console.log(`[search-index] Libraries: ${libraries.length}`);
  return libraries;
}

// ── Main ──

console.log('[search-index] Building search index...');

const index = {
  generated_at: new Date().toISOString(),
  plugins: buildPluginIndex(),
  updates: buildUpdatesIndex(),
  libraries: buildLibrariesIndex(),
};

// Ensure dist directory exists
if (!fs.existsSync(DIST_DIR)) {
  fs.mkdirSync(DIST_DIR, { recursive: true });
}

fs.writeFileSync(OUT_FILE, JSON.stringify(index));
const stats = fs.statSync(OUT_FILE);
console.log(`[search-index] Written to ${OUT_FILE} (${(stats.size / 1024).toFixed(1)} KB)`);

// Also write gzip size estimate (rough)
const compressed = JSON.stringify(index);
console.log(`[search-index] Total entries: ${index.plugins.length + index.updates.length + index.libraries.length}`);
console.log(`[search-index] Raw size: ${(compressed.length / 1024).toFixed(1)} KB (gzip ~${(compressed.length / 1024 / 4).toFixed(0)} KB estimated)`);
