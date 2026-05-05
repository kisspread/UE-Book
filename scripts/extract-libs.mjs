#!/usr/bin/env node

/**
 * extract-libs.mjs
 * 解析 notes/00.md → ue-book/docs/libraries/data.json
 * 
 * 相对图片路径自动转为 GitHub raw URL
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const SRC = process.argv[2] || '/tmp/notes-00.md';
const OUT = path.join(ROOT, 'ue-book', 'docs', 'libraries', 'data.json');

// Base URL for resolving relative image paths
// ../assets/images/xxx → https://raw.githubusercontent.com/kisspread/notes/main/docs/assets/images/xxx
const RAW_BASE = 'https://raw.githubusercontent.com/kisspread/notes/main/docs/Tools';

function resolveImageUrl(url) {
  if (url.startsWith('http://') || url.startsWith('https://')) {
    // Convert GitHub blob URLs to raw
    url = url.replace('github.com/kisspread/notes/blob/', 'raw.githubusercontent.com/kisspread/notes/');
    return url;
  }
  // Relative path: resolve against current directory
  if (url.startsWith('../')) {
    return RAW_BASE + '/' + url;
  }
  if (url.startsWith('./') || !url.startsWith('/')) {
    return RAW_BASE + '/' + url;
  }
  return url;
}

const content = fs.readFileSync(SRC, 'utf-8');
const lines = content.split('\n');

const entries = [];
let currentCategory = '';
let current = null;
let contentLines = [];

function finalizeCurrent() {
  if (current) {
    current.content = contentLines.join('\n').trim();
    entries.push(current);
    current = null;
    contentLines = [];
  }
}

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];

  // Category header
  if (line.startsWith('## ')) {
    finalizeCurrent();
    currentCategory = line.replace('## ', '').trim();
    continue;
  }

  // Entry start: "- [Name](URL) desc..."
  const entryMatch = line.match(/^- \[([^\]]+)\]\(([^)]+)\)\s*(.*)/);
  if (entryMatch) {
    finalizeCurrent();
    const desc = entryMatch[3].trim();
    current = {
      name: entryMatch[1],
      github: entryMatch[2],
      category: currentCategory,
      images: [],
      content: '',
    };
    if (desc) contentLines.push(desc);
    continue;
  }

  if (!current) continue;

  const trimmed = line.trim();

  // Collect images — resolve relative paths
  const imgMatch = trimmed.match(/^!\[([^\]]*)\]\(([^)]+)\)/);
  if (imgMatch) {
    let url = imgMatch[2].replace(/\{[^}]*\}/, '').trim(); // remove {width=...}
    // Skip private-user-images that require JWT
    if (!url.includes('private-user-images.githubusercontent.com')) {
      const resolved = resolveImageUrl(url);
      current.images.push(resolved);
      // Replace in content with resolved URL
      contentLines.push(trimmed.replace(url, resolved));
    }
    continue;
  }

  // All other lines
  contentLines.push(line.replace(/^ {2}/, ''));
}

finalizeCurrent();

// Clean up
for (const e of entries) {
  e.content = e.content.replace(/\n{3,}/g, '\n\n').trim();
  // Remove {width=...} from content
  e.content = e.content.replace(/\{width=[^}]*\}/g, '');
}

// Category stats
const cats = {};
for (const e of entries) {
  cats[e.category] = (cats[e.category] || 0) + 1;
}

fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(entries, null, 2), 'utf-8');

const withImgs = entries.filter(e => e.images.length > 0).length;
console.log(`Extracted ${entries.length} libraries (${withImgs} with images) to ${OUT}`);
console.log(`Categories:`);
for (const [c, n] of Object.entries(cats).sort((a, b) => b[1] - a[1])) {
  console.log(`  ${c}: ${n}`);
}
