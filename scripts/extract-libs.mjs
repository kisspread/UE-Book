#!/usr/bin/env node

/**
 * extract-libs.mjs
 * 解析 notes/00.md → ue-book/docs/libraries/data.json
 * 
 * 格式：
 * ## Category
 * - [Name](URL) English desc
 *   ![alt](img)
 *   - 中文附注
 *   - 更多说明
 */

import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const __dirname = path.dirname(fileURLToPath(import.meta.url));
const ROOT = path.resolve(__dirname, '..');
const SRC = process.argv[2] || '/tmp/notes-00.md';
const OUT = path.join(ROOT, 'ue-book', 'docs', 'libraries', 'data.json');

const content = fs.readFileSync(SRC, 'utf-8');
const lines = content.split('\n');

const entries = [];
let currentCategory = '';
let current = null;

for (let i = 0; i < lines.length; i++) {
  const line = lines[i];

  // Category header
  if (line.startsWith('## ')) {
    currentCategory = line.replace('## ', '').trim();
    continue;
  }

  // Entry start: "- [Name](URL) desc..."
  const entryMatch = line.match(/^- \[([^\]]+)\]\(([^)]+)\)\s*(.*)/);
  if (entryMatch) {
    if (current) entries.push(current);
    current = {
      name: entryMatch[1],
      github: entryMatch[2],
      desc_en: entryMatch[3].trim(),
      desc_cn: '',
      category: currentCategory,
      images: [],
    };
    continue;
  }

  if (!current) continue;

  const trimmed = line.trim();

  // Image: "![alt](url)" or "![alt](url){width=...}"
  const imgMatch = trimmed.match(/^!\[([^\]]*)\]\(([^)]+)\)/);
  if (imgMatch) {
    const url = imgMatch[2];
    // Skip private-user-images that require JWT
    if (!url.includes('private-user-images.githubusercontent.com')) {
      current.images.push(url);
    }
    continue;
  }

  // Chinese notes: starts with "- " (indented)
  const noteMatch = line.match(/^\s{2,}-\s+(.*)/);
  if (noteMatch) {
    const note = noteMatch[1].trim();
    // Skip pure links/empty
    if (note && !note.startsWith('![')) {
      if (current.desc_cn) current.desc_cn += '\n';
      current.desc_cn += note;
    }
    continue;
  }

  // Continuation line (indented, not starting with -)
  if (current && /^\s{4,}/.test(line) && trimmed.length > 0) {
    // Could be extra description
    if (current.desc_cn && !current.desc_cn.endsWith('\n')) {
      current.desc_cn += ' ';
    }
  }
}

if (current) entries.push(current);

// Clean up
for (const e of entries) {
  e.desc_en = e.desc_en.replace(/\s+/g, ' ').trim();
  e.desc_cn = e.desc_cn.replace(/\n{2,}/g, '\n').trim();
  // Remove image markdown from desc_en if leaked
  e.desc_en = e.desc_en.replace(/!\[[^\]]*\]\([^)]+\)/g, '').trim();
  // Truncate long descriptions
  if (e.desc_en.length > 200) e.desc_en = e.desc_en.substring(0, 200) + '…';
  if (e.desc_cn.length > 300) e.desc_cn = e.desc_cn.substring(0, 300) + '…';
}

// Category stats
const cats = {};
for (const e of entries) {
  cats[e.category] = (cats[e.category] || 0) + 1;
}

fs.mkdirSync(path.dirname(OUT), { recursive: true });
fs.writeFileSync(OUT, JSON.stringify(entries, null, 2), 'utf-8');

console.log(`Extracted ${entries.length} libraries to ${OUT}`);
console.log(`Categories:`);
for (const [c, n] of Object.entries(cats).sort((a, b) => b[1] - a[1])) {
  console.log(`  ${c}: ${n}`);
}
