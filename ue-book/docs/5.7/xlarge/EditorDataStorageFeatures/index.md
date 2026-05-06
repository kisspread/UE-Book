# TEDS: Editor Data Storage Features

> Experimental UI Features for the Editor, built on TEDS: Editor Data Storage.

| 属性 | 值 |
|---|---|
| 中文名 | TEDS 功能集 |
| 分类 | Editor |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（编辑器扩展资产、配置） |
| 模块 | `TedsActorCompatibility` (Runtime), `TedsAlerts` (Runtime), `TedsAssetData` (Runtime), `TedsContentBrowser` (Runtime), `TedsDebugger` (Runtime), `TedsEditorCompatibility` (Runtime), `TedsEverythingPicker` (Runtime), `TedsOutliner` (Runtime), `TedsPropertyEditor` (Runtime), `TedsQueryStack` (Runtime), `TedsRevisionControl` (Runtime), `TedsSettings` (Runtime), `TedsTableViewer` (Runtime), `TedsTypeInfo` (Runtime), `TedsTypedElementBridge` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-09-25 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures) | |

## 总体用途

TEDS（Editor Data Storage）是一个基于 ECS（实体组件系统）的编辑器数据存储框架。`EditorDataStorageFeatures` 插件是 TEDS 的**高级特性层**，它封装了一系列开箱即用的编辑器 UI 和工具模块，让开发者能够快速利用 TEDS 构建模块化、高性能的编辑器界面。

该插件解决了传统编辑器 UI 耦合紧密、难以扩展的问题，通过 TEDS 的数据驱动模式，提供统一的数据管理、查询、展示和交互能力。它包含内容浏览器、大纲视图、属性面板、资产数据、警报系统、调试器、版本控制集成等功能模块，是 TEDS 生态的核心组件。

## 模块列表

| 模块 | 一句话总结 |
|---|---|
| **TedsActorCompatibility** | 在 TEDS 中维护 Actor 与场景元素的兼容性映射，支持 Actor 的查找和转化。 |
| **TedsAlerts** | 提供基于 TEDS 的编辑器警报系统，可显示、过滤和管理警告/错误消息。 |
| **TedsAssetData** | 将资产注册表数据以表格形式导入 TEDS，支持资产的查询、排序和过滤。 |
| **TedsContentBrowser** | 使用 TEDS 作为数据源的新一代内容浏览器，提供更灵活的视图和搜索。 |
| **TedsDebugger** | 可视化调试 TEDS 数据存储的运行状态，包括实体、组件和查询的实时监控。 |
| **TedsEditorCompatibility** | 确保 TEDS 与现有编辑器基础设施（如菜单、命令绑定）兼容。 |
| **TedsEverythingPicker** | 一个通用的拾取器组件，可基于 TEDS 数据搜索任意类型的内容。 |
| **TedsOutliner** | 基于 TEDS 的世界大纲视图，支持按自定义列排序、过滤和层级展示。 |
| **TedsPropertyEditor** | 将 TEDS 实体的属性映射到标准属性面板，支持编辑和查看。 |
| **TedsQueryStack** | 管理 TEDS 查询的堆栈和组合，支持复杂过滤逻辑的构建与复用。 |
| **TedsRevisionControl** | 集成版本控制系统（如 Perforce），在 TEDS 中展示文件的变更状态。 |
| **TedsSettings** | 提供基于 TEDS 的编辑器设置管理器，允许按实体存储和编辑配置。 |
| **TedsTableViewer** | 一个通用表格视图组件，以表格形式展示 TEDS 查询结果，支持排序、过滤和列定制。 |
| **TedsTypeInfo** | 维护 TEDS 中注册的类型信息，支持运行时类型发现和反射。 |
| **TedsTypedElementBridge** | 将 TEDS 实体桥接到 Typed Element 框架，使 TEDS 数据能参与标准元素交互。 |

## 使用场景

- **构建自定义编辑器面板**：利用 `TedsTableViewer`、`TedsOutliner` 等模块快速创建数据驱动的表格、树形视图，无需从头实现 UI 逻辑。
- **增强内容浏览器**：通过 `TedsContentBrowser` 和 `TedsAssetData` 获得更强大的搜索、过滤和排序功能，且数据由 TEDS 统一管理。
- **调试 TEDS 数据**：使用 `TedsDebugger` 实时查看实体、组件和查询结果，便于开发阶段排查问题。
- **集成现有编辑器功能**：借助 `TedsActorCompatibility`、`TedsEditorCompatibility`、`TedsTypedElementBridge` 等模块，使 TEDS 能与 Actor、TypedElement 等现有系统协同工作。
- **实现属性面板扩展**：在 `TedsPropertyEditor` 基础上，为自定义 TEDS 组件添加标准属性编辑能力。
- **数据分析与筛选**：组合 `TedsQueryStack` 和 `TedsTableViewer`，搭建复杂的查询条件，并以表格形式展示结果（如资产列表、事件日志）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/EditorDataStorageFeatures)
- 模块文档：
  - [TedsActorCompatibility](docs/large/EditorDataStorageFeatures/TedsActorCompatibility.md)
  - [TedsAlerts](docs/large/EditorDataStorageFeatures/TedsAlerts.md)
  - [TedsAssetData](docs/large/EditorDataStorageFeatures/TedsAssetData.md)
  - [TedsContentBrowser](docs/large/EditorDataStorageFeatures/TedsContentBrowser.md)
  - [TedsDebugger](docs/large/EditorDataStorageFeatures/TedsDebugger.md)
  - [TedsEditorCompatibility](docs/large/EditorDataStorageFeatures/TedsEditorCompatibility.md)
  - [TedsEverythingPicker](docs/large/EditorDataStorageFeatures/TedsEverythingPicker.md)
  - [TedsOutliner](docs/large/EditorDataStorageFeatures/TedsOutliner.md)
  - [TedsPropertyEditor](docs/large/EditorDataStorageFeatures/TedsPropertyEditor.md)
  - [TedsQueryStack](docs/large/EditorDataStorageFeatures/TedsQueryStack.md)
  - [TedsRevisionControl](docs/large/EditorDataStorageFeatures/TedsRevisionControl.md)
  - [TedsSettings](docs/large/EditorDataStorageFeatures/TedsSettings.md)
  - [TedsTableViewer](docs/large/EditorDataStorageFeatures/TedsTableViewer.md)
  - [TedsTypeInfo](docs/large/EditorDataStorageFeatures/TedsTypeInfo.md)
  - [TedsTypedElementBridge](docs/large/EditorDataStorageFeatures/TedsTypedElementBridge.md)

> **说明**：本插件为实验性功能，默认未启用。需要在插件管理器中手动启用，并确保 TEDS 核心功能（`EditorDataStorage` 插件）已加载。完整 API 及用法请参考各子模块文档。