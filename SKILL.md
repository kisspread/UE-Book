---
name: ue-book-search
description: Search UE-Book knowledge base — UE5 plugins, engine updates, open-source libraries. Use when asked about Unreal Engine plugins, features, AI/rendering/animation etc.
install: https://raw.githubusercontent.com/kisspread/UE-Book/master/install.md
---

# UE-Book Search

Search the [UE-Book](https://kisspread.github.io/UE-Book/) knowledge base, covering:

- **870+ UE5 built-in plugins** — detailed docs for every engine plugin (5.7/5.8)
- **Engine update reports** — weekly/monthly reports on ue5-main changes, AI-categorized
- **155+ community libraries** — curated Awesome UE5 tools & libraries

## Usage

When you need to search UE knowledge, call the search script:

```bash
python3 ~/.agent-skills/ue-book-search/search-ue.py "<query>" --json
```

### Example flow

1. User asks: "UE有哪些AI助手相关的内容？"
2. You break the query into Chinese + English keywords: `AI`, `助手`
3. Run search:
   ```bash
   python3 ~/.agent-skills/ue-book-search/search-ue.py "AI 助手" --json
   ```
4. Results return three sections:
   - `plugins` — matching plugins (name, name_cn, category, web_url, raw_url, _score)
   - `updates` — matching reports (title, slug, date, web_url, raw_url)
   - `libraries` — matching libraries (name, url, category, description)
5. To read a full entry, curl the `raw_url` (returns raw markdown):
   ```bash
   curl -s "<raw_url>" | head -200
   ```
6. Synthesize answer: organize by Plugins → Updates → Libraries, cite names and links.

## Script options

```
python3 search-ue.py "query" [--max 15] [--source plugins,updates,libraries] [--json] [--refresh]
```

- `--json` — machine-readable output (recommended for agents)
- `--refresh` — force re-download the index
- `--max N` — max results per source (default 15)
- `--source` — comma-separated sources to search

## Key details

- **raw_url** → GitHub raw markdown, agent-friendly, no HTML parsing
- **web_url** → VitePress rendered page, human-friendly
- **Index cached** 24 hours in `~/.cache/ue-book-search/`
- **Zero clone required** — script auto-downloads ~220KB gzipped index from GitHub Pages
