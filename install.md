# Install UE-Book Search

A one-command install for agents. Copy this URL to your agent:

> 帮我安装 UE-Book 搜索：https://raw.githubusercontent.com/kisspread/UE-Book/master/install.md

---

## What your agent will do

```bash
# 1. Create directory
mkdir -p ~/.agent-skills/ue-book-search/

# 2. Download the search script (single file, ~7KB)
curl -fsSL -o ~/.agent-skills/ue-book-search/search-ue.py \
  https://raw.githubusercontent.com/kisspread/UE-Book/master/scripts/search-ue.py

# 3. Make executable
chmod +x ~/.agent-skills/ue-book-search/search-ue.py

# 4. Download the search index from GitHub Pages
python3 ~/.agent-skills/ue-book-search/search-ue.py --cache-status
```

## Verify

```bash
python3 ~/.agent-skills/ue-book-search/search-ue.py "AI助手 Niagara" --json
```

Should return JSON with `plugins`, `updates`, `libraries` results.

## Optional: full offline install

If you want to search the raw markdown files directly (no network after install):

```bash
# Sparse clone — only pulls docs, not the full repo
git clone --depth 1 --filter=blob:none --sparse \
  https://github.com/kisspread/UE-Book.git ~/ue-book-offline

cd ~/ue-book-offline
git sparse-checkout set ue-book/docs scripts/search-ue.py

# Then use --local flag to search local files instead of the index
python3 scripts/search-ue.py "AI" --local ~/ue-book-offline/ue-book/docs
```

## Uninstall

```bash
rm -rf ~/.agent-skills/ue-book-search/
```
