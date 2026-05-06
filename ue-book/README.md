# UE5 Plugin Documentation Pipeline

批量生成 UE5 插件使用文档的自动化流水线。通过 LLM 分析源码，生成中文使用文档。

## 版本

| | V1 (本地) | V2 (GitHub Actions) |
|---|---|---|
| 源码来源 | 本地 clone | GitHub API |
| 执行方式 | `python3 run.py` | Actions workflow_dispatch |
| 版本管理 | 无 | `docs/{version}/` |
| 增量策略 | 全量 | 按版本增量（只生成新增 plugin） |

## 快速开始

### V2 (推荐)

```bash
# 1. 配置
cp v2/config_local.example.py v2/config_local.py
# 编辑 v2/config_local.py 填入 LLM 配置

# 2. 设置 GitHub Token
export GH_PAT="ghp_你的token"

# 3. 查看会生成哪些 plugin
python3 -m v2.run --version 5.8 --dry-run

# 4. 增量生成（只生成 5.8 新增的 plugin）
python3 -m v2.run --version 5.8

# 5. 强制重新生成指定 plugin
python3 -m v2.run --version 5.8 --force EnhancedInput MetaHuman

# 6. 强制全量重新生成
python3 -m v2.run --version 5.8 --force-all

# 7. 同步
node scripts/sync-manifest.mjs    # 更新 manifest + sidebar + latest.json
```



### V1 (本地模式)

需要本地 UE 源码 clone，配置 `pipeline/config_local.py`：

```bash
cp pipeline/config_local.example.py pipeline/config_local.py
export LLM_API_KEY="your-key"
python3 run.py -p PluginName
python3 run.py -c xlarge -b 4
```

## GitHub Actions

在仓库的 Actions 页面手动触发：

- **version**: UE 版本（如 `5.8`）
- **force**: 留空 = 增量生成；填 `all` = 全量；填 plugin 名（逗号分隔）= 指定 plugin

### Secrets 配置

| Secret | 说明 |
|--------|------|
| `GH_PAT` | GitHub PAT（需 `repo` scope，用于访问 EpicGames/UnrealEngine） |
| `LLM_BASE_URL` | LLM API 端点 |
| `LLM_MODEL` | 模型名称 |
| `LLM_API_KEY` | API 密钥 |

## 文件结构

```
ue-book/
├── v2/                          # V2 pipeline (GitHub API)
│   ├── config.py                # 配置
│   ├── config_local.py          # 本地配置 (git-ignored)
│   ├── scanner.py               # GitHub API 源码扫描
│   ├── manifest.py              # manifest 管理
│   ├── generator.py             # LLM 调用
│   ├── graph.py                 # LangGraph 流水线
│   ├── run.py                   # CLI 入口
│   └── requirements.txt
├── pipeline/                    # V1 pipeline (本地模式)
│   ├── config.py
│   ├── scanner.py
│   ├── generator.py
│   └── graph.py
├── run.py                       # V1 CLI
├── manifest.json                # 已生成 plugin 记录
├── harness.md                   # 文档模板 + 生成规则
├── docs/
│   ├── small/                   # V1 文档 (5.7)
│   ├── medium/
│   ├── large/
│   ├── xlarge/
│   └── {version}/               # V2 文档 (按版本)
│       └── {size}/
├── plugins-index.json           # V1 plugin 索引
└── .github/workflows/
    └── generate.yml             # GitHub Actions
```

## 增量策略

`manifest.json` 记录所有已生成的 plugin：

```json
{
  "versions": { "5.7": { "generated_at": "2026-05-01" } },
  "plugins": {
    "ADM": { "generated_in": "5.7", "size": "small", "doc_path": "docs/5.7/small/ADM/" }
  }
}
```

每次运行时：
1. 从 GitHub API 获取目标版本的 plugin 列表
2. 与 manifest 做 diff → 找出新增 plugin
3. 只生成新增的，跳过已有的

## 流水线流程

每个 plugin 经过 LangGraph StateGraph 的 5 个节点：

```
scan → generate_modules → review → generate_index → finalize
              ↑              ↓
              └── retry ─────┘ (review 不通过时，最多重试 2 次)
```

- **scan**: GitHub API 获取 .uplugin、模块列表、源码文件
- **generate_modules**: 单模块生成 index.md，多模块每个模块一个 .md
- **review**: 检查属性表、用途章节、模块完整性
- **generate_index**: 多模块 plugin 生成汇总 index.md
- **finalize**: 移动到正确的 size 目录

## 文档模板

生成规则定义在 `harness.md`，包括：
- 属性表格式
- 省略常见依赖
- 近期更新必须列出原始 commit
- 不生成 Build.cs 代码块
