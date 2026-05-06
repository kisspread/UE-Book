# Interchange Framework

> The Interchange Framework plugin offers a customizable import and export system, with an extensible set of pipelines for handling common file types.

| 属性 | 值 |
|---|---|
| 中文名 | 交换框架 |
| 分类 | Importers |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（蓝图资产、测试资源） |
| 模块 | `InterchangeCommon` (Runtime), `InterchangeDispatcher` (Runtime), `InterchangeExport` (Runtime), `InterchangeFactoryNodes` (Runtime), `InterchangeImport` (Runtime), `InterchangeMessages` (Runtime), `InterchangeNodes` (Runtime), `InterchangeCommonParser` (Runtime), `InterchangeFbxParser` (Runtime), `GLTFCore` (Runtime), `InterchangePipelines` (Runtime), `Draco` (External) |
| 实验性 | 否 |
| 创建时间 | 2025-10-17 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime) | |

## 总体用途

Interchange Framework 是 Unreal Engine 新一代的导入/导出系统，旨在替代传统的 FBX 和 OBJ 导入器。它提供了一个高度可定制的管线架构，允许用户通过插件（Pipeline）和节点系统对导入过程进行精细化控制。核心优势在于：

- **统一数据模型**：所有文件格式（FBX、glTF、OBJ 等）先解析为统一的 `InterchangeNode` 图，再通过 Factory Nodes 转换为引擎资源（StaticMesh、SkeletalMesh、Animation、Material 等）。
- **可扩展管线**：通过 `UInterchangePipeline` 蓝图或 C++ 插件，可在导入流程中插入自定义处理步骤（如重命名、材质重定向、LOD 合并）。
- **多格式支持**：内置 FBX 和 glTF 解析器，通过 Draco 库支持网格压缩，并可通过第三方插件扩展新格式。
- **分布式处理**：借助 `InterchangeDispatcher` 支持多进程/多线程解析，提升大型场景的导入性能。

## 模块概览

| 模块 | 一句话总结 | 文档 |
|---|---|---|
| `InterchangeCommon` | 提供基础类型定义（节点、属性、消息）和共享工具类 | [InterchangeCommon.md](InterchangeCommon.md) |
| `InterchangeDispatcher` | 任务分发系统，管理工作进程间的通信与任务调度 | [InterchangeDispatcher.md](InterchangeDispatcher.md) |
| `InterchangeExport` | 导出功能的入口和核心逻辑，支持自定义导出管线 | [InterchangeExport.md](InterchangeExport.md) |
| `InterchangeFactoryNodes` | 定义各类 Factory Node（StaticMesh、SkeletalMesh、Material 等），负责将节点图转为引擎资源 | [InterchangeFactoryNodes.md](InterchangeFactoryNodes.md) |
| `InterchangeImport` | 导入功能入口，协调解析器、管线和工厂节点完成资源导入 | [InterchangeImport.md](InterchangeImport.md) |
| `InterchangeMessages` | 消息系统，统一管理导入/导出过程中的错误、警告和信息 | [InterchangeMessages.md](InterchangeMessages.md) |
| `InterchangeNodes` | 核心节点图数据结构，描述导入数据的层级、变换和属性 | [InterchangeNodes.md](InterchangeNodes.md) |
| `InterchangeCommonParser` | 通用解析器基类和辅助工具，为格式解析器提供基础 | [InterchangeCommonParser.md](InterchangeCommonParser.md) |
| `InterchangeFbxParser` | FBX 格式专用解析器，将 FBX 文件转换为 Interchange 节点图 | [InterchangeFbxParser.md](InterchangeFbxParser.md) |
| `GLTFCore` | glTF/GLB 格式核心解析器，支持 PBR 材质、动画、变形目标 | [GLTFCore.md](GLTFCore.md) |
| `InterchangePipelines` | 管道系统，允许用户通过蓝图或 C++ 自定义导入处理步骤 | [InterchangePipelines.md](InterchangePipelines.md) |
| `Draco` | 第三方 Draco 压缩库封装，用于 glTF 等格式的网格压缩/解压 | [Draco.md](Draco.md) |

## 使用场景

- **大型游戏项目**：需要批量导入大量 FBX/glTF 资产，并对每个文件执行相同的后处理（如自动生成 LOD、合并材质）。
- **自定义导入逻辑**：资产包含特殊元数据或命名规范，需要通过 `UInterchangePipeline` 编写自定义脚本进行重命名、属性映射。
- **跨格式工作流**：同时使用 FBX 和 glTF 格式，希望统一导入体验和输出质量。
- **性能敏感场景**：利用 `InterchangeDispatcher` 多进程解析加速，减少大型场景的导入等待时间。
- **资产导出**：需要将引擎资源导出为标准格式（如 glTF），供其他 DCC 工具或运行时使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Interchange/Runtime)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/interchange-framework-in-unreal-engine)（截至 UE 5.4 已发布官方文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Source/Programs/InterchangeWorker/Tests)（部分测试位于独立目录）