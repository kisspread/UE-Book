# UE5 Plugin Documentation Pipeline

批量生成 UE5 插件使用文档的自动化流水线。

## 快速开始

```bash
# 1. 复制本地配置模板并填入你的路径和 API 信息
cp pipeline/config_local.example.py pipeline/config_local.py
vim pipeline/config_local.py

# 2. 设置 API Key（环境变量）
export LLM_API_KEY="your-api-key-here"

# 3. 生成单个 plugin
python3 run.py -p PluginName

# 批量生成指定 plugin
python3 run.py -p PluginA PluginB PluginC -b 3

# 按规模批量生成
python3 run.py -c xlarge -b 4      # 100+ 文件的 plugin
python3 run.py -c medium -n 10      # 前 10 个 medium

# 生成所有未完成的 plugin
python3 run.py
```

参数：
- `-p, --plugins` — 指定 plugin 名称（空格分隔）
- `-c, --category` — 按规模：small / medium / large / xlarge
- `-n, --limit` — 最多处理几个
- `-b, --batch-size` — 并发数（默认 3）

## 配置

### 本地配置（git-ignored）

复制 `pipeline/config_local.example.py` 为 `pipeline/config_local.py`，填入：

- `UE_SOURCE` — UE 源码根目录
- `GIT_MAIN_REPO` — Git 主仓库路径
- `LLM_BASE_URL` — LLM API 端点
- `LLM_MODEL` — 模型名称

`config_local.py` 会自动覆盖 `config.py` 中的默认值。

### 环境变量

- `LLM_API_KEY` — API 密钥（优先读取环境变量）
- `LLM_BASE_URL` — 可选，覆盖 API 端点
- `LLM_MODEL` — 可选，覆盖模型名

切换其他 OpenAI 兼容的 LLM 只需改 `config_local.py` 中的三行。

## 文件结构

```
ue-book/
├── run.py                      # CLI 入口
├── pipeline/
│   ├── config.py               # 默认配置（安全，可提交）
│   ├── config_local.py         # 本地配置（git-ignored）
│   ├── config_local.example.py # 配置模板
│   ├── graph.py                # LangGraph 流水线（scan→generate→review→index）
│   ├── scanner.py              # 源码扫描（git ls-files + Build.cs 解析）
│   └── generator.py            # LLM 调用封装
├── harness.md                  # 文档模板 + 生成规则（System Prompt）
├── plugins-index.json          # 全局 plugin 索引（509 个）
├── docs/
│   ├── small/                  # 1-20 文件（270 个）
│   ├── medium/                 # 21-50 文件（101 个）
│   ├── large/                  # 51-100 文件（54 个）
│   └── xlarge/                 # 100+ 文件（85 个）
└── scripts/
    ├── batch_doc.py            # 旧版进度管理脚本
    └── monitor_xlarge.py       # 进度监控
```

## 流水线流程

每个 plugin 经过 LangGraph StateGraph 的 5 个节点：

```
scan → generate_modules → review → generate_index → finalize
              ↑              ↓
              └── retry ─────┘ (review 不通过时，最多重试 2 次)
```

- **scan**: git ls-files 定位 plugin 路径，解析 Build.cs 提取模块列表
- **generate_modules**: 单模块生成 index.md，多模块每个模块一个 .md
- **review**: 检查属性表、用途章节、模块完整性
- **generate_index**: 多模块 plugin 生成汇总 index.md
- **finalize**: 收集结果

并发通过 `asyncio.Semaphore(batch_size)` 控制。

## 已知限制

- xlarge 中的 Avalanche 和 nDisplay 是巨型 plugin，各有 40+/7 模块，单个 plugin 需要 30-40 分钟
- 100+ 模块的 plugin 会跳过模块完整性检查（review 只检查文档质量）

## 文档模板

生成规则定义在 `harness.md`，包括：
- 属性表格式
- 省略常见依赖（Core/Engine/Slate 等只列一次）
- 近期更新必须列出原始 commit
- 不生成 Build.cs 代码块

修改 `harness.md` 后重新生成即可生效。
