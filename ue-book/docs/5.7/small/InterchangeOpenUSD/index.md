# Interchange OpenUSD

> Allows translation of OpenUSD files via the Interchange framework

| 属性 | 值 |
|---|---|
| 中文名 | 通用USD交换插件 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容插件） |
| 模块 | `InterchangeOpenUSDEditor` (Runtime), `InterchangeOpenUSDImport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-10-02 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Extensions/OpenUSD) | |

---

## 📋 总体用途

Interchange OpenUSD 是 **Interchange 框架** 的扩展模块，专门用于支持 **OpenUSD 格式**（即通用场景描述格式 `.usd`、`.usda`、`.usdc`）的导入与编辑器配置。通过该插件，用户可以利用 Interchange 的标准化管线将 USD 资产（模型、动画、材质等）转换为 UE5 内部资源，同时支持 Nanite、Subdivision 等高级功能的导入设置。

此插件与旧的 **USD Importer** 插件（`Plugins/Experimental/USDImporter`）不同，它完全基于 Interchange 架构，提供更统一、可扩展的导入体验。

---

## 🔧 模块列表

| 模块 | 类型 | 一句话说明 | 详细文档 |
|---|---|---|---|
| `InterchangeOpenUSDEditor` | Runtime | 提供 USD 导入的编辑器设置、属性编辑 UI（如细分级别取值范围） | [InterchangeOpenUSDEditor.md](./InterchangeOpenUSDEditor.md) |
| `InterchangeOpenUSDImport` | Runtime | 核心导入逻辑：解析 USD 文件、构建 Interchange 翻译器、Nanite 装配重导入 | [InterchangeOpenUSDImport.md](./InterchangeOpenUSDImport.md) |

---

## 🎯 使用场景

- **你需要将第三方 DCC 工具（如 Maya、Houdini）导出的 USD 文件导入 UE5**，并希望利用 Interchange 的标准化导入管线（可结合其他 Interchange 扩展插件）
- **项目已启用 Interchange 框架**，需要支持 OpenUSD 格式的导入和编辑器配置
- **涉及 Nanite 几何体装配的重导入**（该插件专门修复了 Nanite Assembly 的 reimport 问题）
- **需要精确控制 USD 导入时的细分级别 Property Editor**（插件为 `SubdivisionLevel` 设置了合理的最小/最大值）

---

## 📦 依赖关系

使用本插件时，你的模块需在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `InterchangeCore` | Interchange 核心框架 |
| `InterchangeImport` | Interchange 通用导入逻辑 |
| `USD`（或 OpenUSD 相关模块） | 实际的 USD 文件解析与操作 |

> 省略常见依赖（Core、Engine、Slate 等）。

---

## 🧪 维护状态

### 近期更新（最近 5 次）

| 日期 | Hash | Commit 摘要 |
|---|---|---|
| 2025-12-18 | `3f562d0e` | 修复当 Interchange 栈名称被修改时的崩溃 |
| 2025-10-16 | `09310c6c` | [USD Interchange] Nanite Assembly 重导入修复 |
| 2025-10-03 | `24fcc14e` | 回退 CL46528816 |
| 2025-10-03 | `a8f28318` | 为细分级别属性编辑器设置最小/最大值（类似旧 USD legacy） |
| 2025-10-02 | `56e5b338` | 修复重复的 LOCTEXT 键 |

### 维护评价

- **创建时间**：2025-10-02，至今约 0.3 年
- **活跃程度**：从 2025-10 到 2025-12 持续有功能性更新（修复崩溃、优化重导入、UI 改进），维护非常活跃
- **现状评估**：该插件仍被标记为 **实验性**（`IsExperimentalVersion=true`），但更新频率高，社区反馈修复快，适合愿意跟进最新功能的项目使用
- **推荐建议**：如果你的项目已经采用 Interchange 框架且需要 USD 支持，可以直接使用。对于生产环境，建议跟踪最新版本并注意实验性 API 变化

---

## 🔗 相关链接

| 资源 | 链接 |
|---|---|
| 源码目录 | [Engine/Plugins/Interchange/Extensions/OpenUSD](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Extensions/OpenUSD) |
| Editor 模块文档 | [InterchangeOpenUSDEditor.md](./InterchangeOpenUSDEditor.md) |
| Import 模块文档 | [InterchangeOpenUSDImport.md](./InterchangeOpenUSDImport.md) |
| Interchange 框架文档（官方） | [Interchange 用户指南](https://docs.unrealengine.com/5.7/en-US/Interchange/) |