#!/usr/bin/env python3
"""
search-ue.py — UE-Book 知识库搜索脚本

用法:
    python search-ue.py "AI assistant 助手"
    python search-ue.py "AI assistant 助手" --max 20 --source plugins,updates
    python search-ue.py "AI assistant 助手" --json    # JSON 输出

从 GitHub Pages 下载 search-index.json，缓存到 /tmp，模糊搜索。
"""

import json
import os
import re
import sys
import time
import hashlib
from pathlib import Path
from urllib.request import urlopen, Request
from urllib.error import URLError

INDEX_URL = "https://kisspread.github.io/UE-Book/search-index.json"
CACHE_DIR = Path.home() / ".cache" / "ue-book-search"
CACHE_MAX_AGE = 3600 * 24  # 24 hours

# ── Tokenization ──

def tokenize_query(query):
    """拆分查询为搜索词元：中文双字及以上短语 / 英文逐词"""
    tokens = []
    # Extract English words / acronyms
    en_words = re.findall(r'[a-zA-Z0-9]{2,}', query)
    tokens.extend(w.lower() for w in en_words)
    # Extract Chinese phrases (2+ chars only — single chars are too noisy)
    cn_phrases = re.findall(r'[\u4e00-\u9fff]{2,}', query)
    tokens.extend(cn_phrases)
    return list(set(tokens))

def match_score(text, tokens):
    """计算匹配分数"""
    text_lower = text.lower()
    score = 0
    matched = []
    for tok in tokens:
        if tok in text_lower:
            score += 1
            matched.append(tok)
    return score, matched

def name_bonus(entry, tokens):
    """名称匹配加分（英文名 + 中文名）"""
    name = (entry.get("name", "") + " " + entry.get("name_cn", "")).lower()
    bonus = 0
    for tok in tokens:
        if tok in name:
            bonus += 2
    return bonus

# ── Index loading ──

def load_index(force_refresh=False):
    """下载或加载缓存索引"""
    CACHE_DIR.mkdir(parents=True, exist_ok=True)
    cache_file = CACHE_DIR / "search-index.json"
    
    # Check cache
    if not force_refresh and cache_file.exists():
        age = time.time() - cache_file.stat().st_mtime
        if age < CACHE_MAX_AGE:
            with open(cache_file) as f:
                return json.load(f)
    
    # Download
    try:
        req = Request(INDEX_URL, headers={"User-Agent": "ue-book-search/1.0"})
        with urlopen(req, timeout=15) as resp:
            data = json.loads(resp.read().decode())
        with open(cache_file, "w") as f:
            json.dump(data, f, ensure_ascii=False)
        return data
    except (URLError, ValueError) as e:
        # Fall back to stale cache
        if cache_file.exists():
            return json.loads(open(cache_file).read())
        raise RuntimeError(f"Failed to download index: {e}")

# ── Search ──

def search(query, sources=None, max_results=15):
    """
    搜索知识库
    
    Args:
        query: 搜索关键词（中英文混合）
        sources: 搜索源列表，默认 ['plugins', 'updates', 'libraries']
        max_results: 每个源最多返回条数
    
    Returns:
        {"plugins": [...], "updates": [...], "libraries": [...]}
    """
    if sources is None:
        sources = ["plugins", "updates", "libraries"]
    
    index = load_index()
    tokens = tokenize_query(query)
    
    if not tokens:
        return {"plugins": [], "updates": [], "libraries": []}
    
    results = {}
    
    for source in sources:
        entries = index.get(source, [])
        scored = []
        for entry in entries:
            score, matched = match_score(entry.get("text", ""), tokens)
            # Bonus: name match (English + Chinese)
            score += name_bonus(entry, tokens)
            if score > 0:
                scored.append((score, matched, entry))
        
        # Sort by score descending
        scored.sort(key=lambda x: x[0], reverse=True)
        results[source] = [
            {**entry, "_score": score, "_matched": matched}
            for score, matched, entry in scored[:max_results]
        ]
    
    return results


# ── CLI ──

def format_output(results):
    """人类可读输出"""
    sections = [
        ("🔌 插件 (Plugins)", "plugins"),
        ("📰 更新 (Updates)", "updates"),
        ("📚 开源库 (Libraries)", "libraries"),
    ]
    
    total = sum(len(v) for v in results.values())
    if total == 0:
        print("❌ 未找到相关结果。")
        return
    
    print(f"🔍 共找到 {total} 个相关结果：\n")
    
    for title, key in sections:
        items = results.get(key, [])
        if not items:
            continue
        print(f"## {title} ({len(items)})")
        print()
        for item in items:
            name = item.get("name") or item.get("title", "")
            name_cn = item.get("name_cn", "")
            cat = item.get("category", "")
            url = item.get("web_url", "")
            
            line = f"  • {name}"
            if name_cn:
                line += f" ({name_cn})"
            if cat:
                line += f"  [{cat}]"
            print(line)
            # Snippet (first 120 chars of text, skip name/name_cn)
            text = item.get("text", "")
            # Remove the leading name part from text for cleaner snippet
            snippet = text.replace(name, "").strip()
            if name_cn:
                snippet = snippet.replace(name_cn, "").strip()
            if snippet:
                print(f"    {snippet[:120]}...")
            if url:
                print(f"    → {url}")
            print()
        print()

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Search UE-Book knowledge base")
    parser.add_argument("query", nargs="?", help="Search query")
    parser.add_argument("--max", type=int, default=15, help="Max results per source")
    parser.add_argument("--source", type=str, default="plugins,updates,libraries",
                        help="Sources to search (comma-separated)")
    parser.add_argument("--json", action="store_true", help="Output raw JSON")
    parser.add_argument("--refresh", action="store_true", help="Force refresh index cache")
    parser.add_argument("--cache-status", action="store_true", help="Show cache status")
    
    args = parser.parse_args()
    
    # Cache status
    if args.cache_status:
        cache_file = CACHE_DIR / "search-index.json"
        if cache_file.exists():
            age_hrs = (time.time() - cache_file.stat().st_mtime) / 3600
            with open(cache_file) as f:
                idx = json.load(f)
            total = len(idx.get("plugins",[])) + len(idx.get("updates",[])) + len(idx.get("libraries",[]))
            print(f"Cache: {cache_file} ({cache_file.stat().st_size/1024:.0f} KB, {age_hrs:.1f}h old)")
            print(f"Entries: {len(idx.get('plugins',[]))} plugins + {len(idx.get('updates',[]))} updates + {len(idx.get('libraries',[]))} libraries = {total}")
        else:
            print("No cache found.")
        return
    
    if not args.query:
        parser.print_help()
        return
    
    sources = [s.strip() for s in args.source.split(",")]
    results = search(args.query, sources=sources, max_results=args.max)
    
    if args.json:
        print(json.dumps(results, ensure_ascii=False, indent=2))
    else:
        format_output(results)


if __name__ == "__main__":
    main()
