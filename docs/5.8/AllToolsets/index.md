# All Toolsets

> Aggregator plugin that depends on all Toolsets plugins.

| 属性 | 值 |
|---|---|
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（.uplugin 配置文件） |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-13 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AllToolsets) | |

## 用途

AllToolsets 是一个**聚合器插件**，其本身不包含任何功能代码。它的核心作用是作为一个“开关”，通过声明对一系列其他 Toolsets 插件的依赖，实现**一键启用所有 Epic 官方提供的工具集插件**。

它解决的问题是：当开发者（尤其是 Epic 内部或需要完整工具链的团队）需要同时使用多个独立的 Toolsets 插件（如 AI 工具集、动画助手工具集、自动化测试工具集等）时，无需在项目设置中手动逐个查找并启用它们，只需启用 `AllToolsets` 这一个插件即可。

## 使用场景

- 你正在搭建一个需要完整开发工具链的项目，希望一次性获得 Epic 提供的所有官方工具集。
- 你是 Epic 内部开发者或参与需要标准化工具环境的项目，需要确保团队成员使用统一的工具集配置。
- 你想快速体验或测试所有可用的 Toolsets 插件，而不想花时间在插件管理器中逐个搜索和启用。

## 蓝图用法

此插件为纯配置聚合器，不包含任何蓝图可调用的函数或属性。其作用仅体现在插件管理器的启用状态上。

## C++ 用法

此插件不包含任何模块或源代码，因此不提供 C++ API。

## Demo 示例

不适用。此插件无功能代码，无需示例。

## 模块依赖

此插件本身无模块，但其 `.uplugin` 文件声明了对以下其他 Toolsets 插件的依赖。启用 `AllToolsets` 将自动启用这些插件：

| 模块 | 用途 |
|---|---|
| `AIModuleToolset` | AI 模块相关的工具集 |
| `AnimationAssistantToolset` | 动画助手工具集 |
| `AutomationTestToolset` | 自动化测试工具集 |
| `NiagaraToolsets` | Niagara 特效相关的工具集 |
| *(其他在 .uplugin 中声明的 Toolsets 插件)* | ... |

## 维护状态

### 近期更新

- `0cd2b3ea` 2026-04-24 — [Backout] - CL53139837
- `8dc8f3fd` 2026-04-24 — Standardize Epic toolset plugin structure
- `c868841e` 2026-04-23 — Rename NiagaraAIAssistantTools plugin to NiagaraToolsets

### 维护评价

- **创建时间**：2026年4月，非常新的插件。
- **最近更新**：最近一周内有多次提交，主要涉及结构调整和依赖项重命名，表明该插件及其关联的 Toolsets 生态系统仍在**积极开发和调整中**。
- **维护状态**：**活跃维护中**。作为 Epic 官方工具链的聚合器，其更新频率与底层 Toolsets 插件的开发进度直接相关。
- **已知限制**：这是一个实验性插件 (`IsExperimentalVersion: true`)，默认未启用 (`EnabledByDefault: false`)。其包含的 Toolsets 列表可能随版本变化。
- **推荐使用**：**推荐给需要完整 Epic 工具链的开发者**。但请注意其“实验性”状态，底层工具集可能不稳定或发生变更。对于生产项目，建议根据实际需求单独评估并启用所需的特定 Toolsets 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AllToolsets)