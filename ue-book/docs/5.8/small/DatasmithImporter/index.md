# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 中文名 | 数据导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

本插件是用于导入 **Datasmith** 格式文件的核心生态系统。它不仅仅是一个简单的文件导入器，而是一个完整的**工业数据转换与同步框架**。其核心价值在于将来自 CAD、BIM、DCC 等专业软件的复杂模型、场景和元数据，高保真地转换并导入到 Unreal Engine 中。

通过模块化设计，该插件支持通过不同的“翻译器”处理各种原生格式（如 .udatasmith），并通过 **DirectLink** 协议实现与某些源软件（如 CATIA、3ds Max）的实时双向数据同步。它解决了工业数据在转换过程中丢失元数据、破坏层级结构等痛点，是进行建筑可视化、工业设计和数字孪生等项目的关键工具。

**注意**：此插件默认未启用。您需要在项目设置中手动启用它才能使用。

## 使用场景

- **建筑可视化 (ArchViz)**：将 Revit、Bentley、ArchiCAD 等 BIM 软件创建的建筑模型导入 Unreal Engine 进行实时渲染和交互式演示。
- **工业设计与数字孪生**：导入 SolidWorks、CATIA、NX 等 CAD 软件设计的复杂装配体，用于产品配置器、虚拟装配培训或工厂数字孪生。
- **实时设计协同 (DirectLink)**：在源 DCC 软件（如 3ds Max）中修改设计后，通过 DirectLink 将变更实时同步到 Unreal Engine 场景中，实现快速迭代。

## 模块列表

| 模块 | 类型 | 说明 |
|---|---|---|
| **DatasmithExternalSource** | Runtime | 管理和处理 Datasmith 特有的外部数据源。 |
| **DatasmithImporter** | Runtime | 核心导入模块，负责协调整个导入流程、资产转换和场景构建。 |
| **DatasmithNativeTranslator** | Runtime | 处理 Datasmith 原生格式 (.udatasmith) 的读取和解析。 |
| **DatasmithTranslator** | Runtime | 所有 Datasmith “翻译器”的基类模块，定义转换接口。 |
| **DirectLinkExtension** | Runtime | 提供 DirectLink 协议的核心基础功能和 API 扩展。 |
| **DirectLinkExtensionEditor** | Runtime | 将 DirectLink 功能集成到 Unreal Editor 中（如工具、UI）。 |
| **DirectLinkTest** | Runtime | DirectLink 功能的测试和调试工具集。 |
| **ExternalSource** | Runtime | 通用外部数据源框架，DatasmithExternalSource 基于此构建。 |

*(每个子模块的详细 API 和用法，请参见对应的模块文档。)*

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithImporter/Tests)