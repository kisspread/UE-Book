# All Toolsets

> Aggregator plugin that depends on all Toolsets plugins.

| 属性 | 值 |
|---|---|
| 中文名 | 工具箱聚合器 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | 无（纯内容插件） |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-01 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AllToolsets) | |

## 用途

这个插件本身不包含任何功能代码。它是一个“聚合器”或“伞形”插件，其唯一作用是在 .uplugin 文件中声明对一系列其他“Toolset”（工具箱）插件的依赖。启用 AllToolsets 插件相当于一键启用所有它依赖的工具箱插件，为开发者提供了一种批量启用相关实验性工具箱的便捷方式。它解决了需要同时使用多个分散的工具箱插件时，手动逐一启用的麻烦。

## 使用场景

- 你想要快速体验或测试 Epic 提供的所有实验性“Toolset”（如 AI 工具箱、动画助手工具箱等），无需在插件列表中逐个查找和启用。
- 你的项目或功能开发需要依赖多个工具箱插件，希望有一个统一的入口进行管理。

## 蓝图用法

此插件为纯配置聚合插件，不提供任何蓝图节点。

### 核心节点

无。

### 使用示例

无。

## C++ 用法

此插件为纯配置聚合插件，不包含任何源码或 API。

### 头文件引入

无。

### 基本用法

无。

### 进阶用法

无。

## Demo 示例

无。此插件不包含任何可演示的功能。

## 模块依赖

此插件作为聚合器，其依赖关系体现在对其他插件的引用上。启用此插件会自动启用以下插件（摘自 .uplugin 配置）：

| 插件 | 说明 |
|---|---|
| `AIModuleToolset` | AI 模块相关工具箱 |
| `AnimationAssistantToolset` | 动画助手工具箱 |
| `AutomationTestToolset` | 自动化测试工具箱 |
| `ConfigSettingsToolset` | 配置设置工具箱（2026-05-12 新增） |
| `PluginToolset` | 插件管理工具箱（2026-05-12 新增） |
| `PCGToolset` | PCG 相关工具箱 |
| 以及 `.uplugin` 中列出的其他 Toolset 插件 | |

**注意**：依赖的具体工具箱列表可能随版本更新而变化。使用此插件时，你的项目将加载所有上述依赖插件的模块和内容。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `c7baaf9c` | Migrated EditorApp and Logs toolsets from ToolsetRegistry to new EditorToolset plugin. | 将编辑器应用和日志工具箱迁移到新的 EditorToolset 插件中。 |
| 2026-05-12 | `b0a44cc5` | Add ConfigSettingsToolset plugin | 新增配置设置工具箱插件。 |
| 2026-05-12 | `d93da640` | Added new PluginToolset AI Toolset for managing plugins. | 新增用于管理插件的 PluginToolset 工具箱。 |
| 2026-04-28 | `ffe59a83` | Added toolsets for data registries. Current implemented commands include: | 新增数据注册表相关的工具箱。 |
| 2026-04-27 | `1fa8f2b1` | Move PCGToolset from Restricted/NFL/Plugins to Plugins/Experimental/Toolsets | 将 PCGToolset 从受限路径迁移到实验性工具箱目录。 |

### 维护评价

- **创建时间**：2026年4月创建，是一个非常新的插件。
- **更新频率**：近期更新活跃，每月都有提交，主要用于添加新的工具箱插件依赖或调整其组织结构。
- **维护状态**：处于**活跃维护**中，是 Epic 实验性工具箱体系的一部分。
- **推荐使用**：**推荐在实验性功能开发中使用**。它作为入口点，可以方便地获取 Epic 提供的一整套实验性开发工具。由于其 `IsExperimentalVersion` 和 `EnabledByDefault=false` 的特性，建议仅在明确需要这些实验性工具的项目中启用，并注意其可能随 UE 版本升级而发生的变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/Toolsets/AllToolsets)
- 官方文档：无
- 测试用例：无