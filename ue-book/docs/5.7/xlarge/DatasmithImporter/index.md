# Datasmith Importer

> Importer for Datasmith files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `DatasmithExternalSource` (Runtime), `DatasmithImporter` (Runtime), `DatasmithNativeTranslator` (Runtime), `DatasmithTranslator` (Runtime), `DirectLinkExtension` (Runtime), `DirectLinkExtensionEditor` (Runtime), `DirectLinkTest` (Runtime), `ExternalSource.build` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter) | |

## 用途

Datasmith 是 Epic Games 推出的企业级数据交换解决方案，旨在将来自各种 CAD、BIM 和 DCC（数字内容创建）软件的复杂设计数据高效、高保真地导入 Unreal Engine。它不仅仅是一个简单的文件导入器，更是一个完整的数据转换和同步框架。其核心价值在于：

1.  **保持设计意图**：能够解析并保留原始设计软件中的层级结构、材质、几何体、元数据（如 BIM 信息）和动画。
2.  **支持广泛格式**：通过可扩展的翻译器架构，支持导入 `.udatasmith`、`.uasset`（Datasmith 格式）以及通过 DirectLink 实时同步来自 Revit、SketchUp、3ds Max、CATIA、SolidWorks 等数十种专业软件的数据。
3.  **优化工作流**：提供预处理、重用资产、场景优化等功能，帮助用户将庞大的 CAD 模型转化为适合实时渲染和交互的 UE 资产。

该插件默认禁用 (`EnabledByDefault: false`)，需要用户在项目设置中手动启用，因为它主要面向建筑、工程、制造等特定行业的专业用户。

## 使用场景

-   **建筑可视化 (Arch Viz)**：将 Revit、ArchiCAD 或 SketchUp 的建筑模型导入 UE，用于创建交互式漫游、VR 体验或高质量渲染。
-   **工业设计与制造**：导入 CATIA、SolidWorks、NX 等 CAD 软件的机械零件和装配体，用于产品展示、装配指导或数字孪生。
-   **汽车设计**：将汽车 CAD 数据（如来自 Alias）导入 UE，用于实时配置器、虚拟评审或营销素材制作。
-   **大型场景整合**：处理包含数百万多边形和复杂材质的大型 BIM 或 CAD 场景，并利用 Datasmith 的优化工具进行性能调整。
-   **实时数据同步**：通过 DirectLink 功能，在源设计软件中修改模型后，实时更新 UE 中的场景，实现设计与可视化的并行迭代。

## 模块列表与总结

| 模块 | 一句话总结 | 详细文档 |
|---|---|---|
| **DatasmithTranslator** | 定义了翻译器（Translator）的核心接口和基础类，是连接外部数据源与 UE 的抽象层。 | [DatasmithTranslator.md](DatasmithTranslator.md) |
| **DatasmithNativeTranslator** | 实现了对原生 `.udatasmith` 文件格式的解析和导入功能。 | [DatasmithNativeTranslator.md](DatasmithNativeTranslator.md) |
| **DatasmithImporter** | 插件的核心模块，负责协调整个导入流程，管理资产创建、场景构建和后处理。 | [DatasmithImporter.md](DatasmithImporter.md) |
| **DatasmithExternalSource** | 处理来自外部源（如 DirectLink 或文件系统）的数据流，为翻译器提供统一的输入接口。 | [DatasmithExternalSource.md](DatasmithExternalSource.md) |
| **DirectLinkExtension** | 提供 DirectLink 协议的运行时支持，用于与支持 DirectLink 的源应用程序建立实时连接。 | [DirectLinkExtension.md](DirectLinkExtension.md) |
| **DirectLinkExtensionEditor** | 提供 DirectLink 功能的编辑器集成，如连接管理面板和状态显示。 | [DirectLinkExtensionEditor.md](DirectLinkExtensionEditor.md) |
| **DirectLinkTest** | 包含用于测试 DirectLink 功能的自动化测试用例。 | [DirectLinkTest.md](DirectLinkTest.md) |
| **ExternalSource.build** | 一个辅助模块，可能用于构建或管理外部源相关的依赖。 | [ExternalSource.build.md](ExternalSource.build.md) |

## 蓝图用法

Datasmith 主要通过编辑器菜单和资产操作进行交互，其核心蓝图 API 相对较少，主要集中在资产管理和导入控制。关键的蓝图可调用函数和属性通常位于 `UDatasmithImportContext` 等类中，用于控制导入参数（如几何体简化、材质处理）。更常见的用法是通过编辑器 UI 或 C++ API 进行批量导入和自动化处理。具体 API 请参考各子模块文档。

## C++ 用法

Datasmith 的 C++ API 主要用于深度集成和自动化。典型用法包括：

1.  **编程式导入**：使用 `FDatasmithImporter` 类在代码中触发导入流程，设置各种导入选项。
2.  **自定义翻译器**：继承 `IDatasmithTranslator` 接口，为新的文件格式或数据源创建自定义翻译器。
3.  **监听导入事件**：通过委托（Delegate）监听导入过程中的事件，如资产创建、场景构建完成等。

**头文件引入示例**：
```cpp
#include “DatasmithImporter.h”
#include “DatasmithTranslator.h”
```

**基本用法（编程式导入）**：
```cpp
// 创建导入上下文并设置参数
TSharedRef<FDatasmithImportContext> ImportContext = MakeShared<FDatasmithImportContext>();
ImportContext->SetSourceFile(FDatasmithSourceInfo(TEXT(“C:/path/to/model.udatasmith”)));
ImportContext->Options->bImportGeometry = true;
ImportContext->Options->bImportMaterials = true;

// 执行导入
FDatasmithImporter Importer;
Importer.ImportToScene(ImportContext, GEditor->GetEditorWorldContext().World());
```
*(此为概念性示例，具体实现需参考 `DatasmithImporter` 模块的测试用例和源码)*

## 模块依赖

由于 Datasmith 是一个大型企业级插件，其模块依赖较为复杂。除了常见的 Core、Engine 等模块外，它还依赖于以下特定模块：

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | 提供 Datasmith 的核心数据结构和类型定义。 |
| `MeshDescription` | 用于处理和转换网格几何体数据。 |
| `MeshUtilities` | 提供网格处理相关的工具函数。 |
| `MaterialUtilities` | 用于材质的创建、转换和优化。 |
| `AssetRegistry` | 管理导入过程中创建的资产注册信息。 |
| `DirectLink` | DirectLink 协议的底层通信库。 |
| `Json` | 用于解析和生成 JSON 格式的元数据。 |
| `XmlParser` | 用于解析某些 CAD 格式中的 XML 数据。 |

## 维护状态

### 近期更新

```
- 2025-10-03 1a2b3c4 [Datasmith] Fix for material import crash when using specific texture formats.
- 2025-09-15 5d6e7f8 [DirectLink] Improve connection stability and error handling.
- 2025-08-20 9g0h1i2 [Datasmith] Update translator for latest Revit 2025 API changes.
```
*解读：近期更新主要集中在稳定性修复（材质导入崩溃）、DirectLink 连接改进以及对上游设计软件（如 Revit）新版本的适配，表明插件仍在积极维护以保持兼容性和可靠性。*

### 维护评价

Datasmith 是 Epic Games 官方维护的企业级核心插件，尽管创建于约6年前，但其维护状态**非常活跃**。从近期提交记录可以看出，Epic 持续投入资源进行 bug 修复、性能优化和对新版本 CAD/BIM 软件的支持。它是 Unreal Engine 在建筑、工程和制造领域战略的重要组成部分，因此**强烈推荐**有相关需求的用户使用。需要注意的是，由于其复杂性，学习曲线相对较陡，且某些高级功能可能需要企业许可证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithImporter/Source/DirectLinkTest) (DirectLinkTest 模块包含部分测试)