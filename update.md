# Update UE-Book Search

> 帮我更新 UE-Book 搜索：https://raw.githubusercontent.com/kisspread/UE-Book/master/update.md

---

```bash
# 1. Download latest search script
curl -fsSL -o ~/.agent-skills/ue-book-search/search-ue.py \
  https://raw.githubusercontent.com/kisspread/UE-Book/master/scripts/search-ue.py

# 2. Refresh search index
python3 ~/.agent-skills/ue-book-search/search-ue.py --refresh

# 3. Verify
python3 ~/.agent-skills/ue-book-search/search-ue.py --cache-status
```
