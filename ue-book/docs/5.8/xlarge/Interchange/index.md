# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 交换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（管线、解析器、工厂节点） |
| 模块 | `InterchangeAnalytics` (Runtime), `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 未知 |
| 年龄标签 | 未知 |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime) | |

## 用途

Interchange 是一个高度模块化、可扩展的资产导入与导出框架，旨在替代并统一 UE 中散乱的导入/导出系统。它通过定义“交换节点”来抽象资产数据，然后使用“管线”和“工厂节点”将其转换为 UE 原生资产或执行逆向操作。其核心目标是让开发者能够更方便地自定义导入流程、支持新的文件格式，并简化复杂的资产转换逻辑。

## 使用场景

- **自定义资产管线**：你需要为特定的文件格式（如自定义 3D 模型格式）编写导入器。
- **批处理转换**：你需要在运行时或编辑器工具中批量处理大量资产，需要一个统一且可控的导入/导出流程。
- **深度集成**：你的工作流需要与外部 DCC 工具（如 Blender, Maya）进行深度数据交换，需要精确控制导入的细节。
- **扩展引擎功能**：你想为引擎添加对新的 3D 格式（如 glTF, FBX 的特定版本）的支持或增强现有支持。

## 模块列表

| 模块 | 简介 |
|---|---|
| **InterchangeAnalytics** | 收集导入/导出过程的性能分析数据。 |
| **InterchangeCommon** | 定义框架的核心数据结构、类型和接口。 |
| **InterchangeDispatcher** | 协调和调度异步的导入/导出任务。 |
| **InterchangeExport** | 实现将 UE 资产导出为外部格式的逻辑。 |
| **InterchangeFactoryNodes** | 定义用于创建特定 UE 资产类型（如纹理、网格体、动画）的工厂节点。 |
| **InterchangeImport** | 实现将外部文件导入为交换节点图的核心逻辑。 |
| **InterchangeMessages** | 定义框架内部使用的通用消息和通信结构。 |
| **InterchangeNodes** | 定义代表资产数据的“交换节点”，如网格体节点、材质节点等。 |
| **InterchangeCommonParser** | 提供通用的文件解析功能和辅助工具。 |
| **InterchangeFbxParser** | 解析 FBX 文件格式，并将其转换为交换节点图。 |
| **GLTFCore** | 解析 glTF 文件格式，并将其转换为交换节点图。 |
| **InterchangePipelines** | 包含一组内置的、可重用的转换管线，用于处理常见的资产类型。 |
| **Draco** | 集成 Google Draco 库，用于压缩和解压缩 glTF 中的网格体几何数据。 |

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Runtime)
- [各子模块详细文档](./InterchangeAnalytics.md)