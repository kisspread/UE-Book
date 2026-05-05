# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是 Unreal Engine Datasmith 生态系统中的核心 CAD 导入插件。它并非一个独立的导入器，而是一个**完整的 CAD 文件处理工具集和翻译管线**。其主要目的是将各种工业 CAD 格式（如 CATIA, NX, SolidWorks, STEP, IGES 等）的复杂几何体、装配体结构和元数据，转换为 Unreal Engine 可用的网格（Mesh）、材质和场景图（Scene Graph）。

该插件通过集成第三方库（如 TechSoft 的 3D InterOp 和 OpenNurbs）来解析原始 CAD 文件，并通过一系列内部模块（如 `CADLibrary`, `CADInterfaces`）处理几何内核转换、曲面细分、网格优化等复杂任务。最终，由 `DatasmithCADTranslator` 等模块将处理后的数据封装成 Datasmith 场景元素，供 Datasmith 导入器使用。它解决了将高精度、参数化的工业设计数据无缝引入实时引擎进行可视化、仿真或数字孪生构建的核心问题。

## 使用场景

- **建筑、工程与施工 (AEC)**：导入来自 Revit, ArchiCAD 或其他 BIM 软件的复杂建筑模型，用于建筑可视化、虚拟漫游或施工规划。
- **汽车与交通运输**：导入来自 CATIA, NX, Alias 等软件的整车或零部件 CAD 数据，用于设计评审、虚拟展示或自动驾驶仿真。
- **工业制造与产品设计**：导入来自 SolidWorks, Creo, Inventor 的机械零件和装配体，用于创建产品配置器、维护手册或工厂布局模拟。
- **任何需要将 CAD 数据用于实时 3D 应用的场景**：当项目需要基于精确的工程数据创建交互式体验时，此插件是必经之路。

## 蓝图用法

此插件主要作为 Datasmith 导入流程的底层引擎，**不直接暴露蓝图节点**。其功能通过 Unreal Editor 的 Datasmith 导入器界面（文件 -> 导入到关卡）或通过 C++ 的 Datasmith API 间接调用。用户在使用时，主要与导入对话框中的 CAD 导入选项交互。

## C++ 用法

此插件的 API 主要面向引擎内部和高级开发者，用于扩展或定制 CAD 导入流程。以下是基于核心模块 `DatasmithCADTranslator` 的用法示例。

### 头文件引入

```cpp
#include "DatasmithMeshBuilder.h"
#include "DatasmithSceneGraphBuilder.h"
```

### 基本用法

`FDatasmithMeshBuilder` 负责将解析后的 CAD 体数据（`FBodyMesh`）转换为 Unreal 的 `FMeshDescription`。

```cpp
// 假设已通过 CAD 解析管线获得了 BodyMeshSet
TArray<CADLibrary::FBodyMesh> BodyMeshSet; // 从 CAD 文件解析得到的体网格数据
CADLibrary::FImportParameters ImportParameters; // 导入参数（如缩放、法线计算方式等）

// 创建 MeshBuilder 实例
FDatasmithMeshBuilder MeshBuilder(BodyMeshSet, ImportParameters);

// 为一个 Datasmith 网格元素获取 MeshDescription
TSharedRef<IDatasmithMeshElement> MeshElement = /* ... */;
CADLibrary::FMeshParameters MeshParameters;
TOptional<FMeshDescription> MeshDescription = MeshBuilder.GetMeshDescription(MeshElement, MeshParameters);

if (MeshDescription.IsSet())
{
    // 使用生成的 MeshDescription 创建 UStaticMesh 等资产
}
```
*来源：基于 `DatasmithMeshBuilder.h` 中的类定义推断。*

### 进阶用法

`FDatasmithSceneBaseGraphBuilder` 负责将 CAD 场景图（包含实例、引用、材质等信息）转换为 Datasmith 场景元素树。

```cpp
// 假设已加载 CAD 场景图归档
CADLibrary::FArchiveSceneGraph* SceneGraphArchive = /* ... */;
FString CachePath = FPaths::ProjectSavedDir() / TEXT("CADCache");
TSharedRef<IDatasmithScene> DatasmithScene = /* ... */;
FDatasmithSceneSource SceneSource;
CADLibrary::FImportParameters ImportParameters;

// 创建场景图构建器
FDatasmithSceneBaseGraphBuilder SceneGraphBuilder(
    SceneGraphArchive,
    CachePath,
    DatasmithScene,
    SceneSource,
    ImportParameters
);

// 执行构建，将 CAD 场景图转换为 Datasmith 场景
bool bSuccess = SceneGraphBuilder.Build();

if (bSuccess)
{
    // DatasmithScene 现在包含了从 CAD 数据转换而来的 Actor、Mesh、Material 等元素
    // 可以将其传递给 Datasmith 导入器进行最终资产创建
}
```
*来源：基于 `DatasmithSceneGraphBuilder.h` 中的类定义推断。*

## Demo 示例

由于此插件是引擎内部管线，通常不直接实例化。以下是一个概念性的 C++ 示例，展示如何利用 Datasmith API 触发 CAD 文件导入。

```cpp
// MyCADImporter.h
#pragma once
#include "CoreMinimal.h"

class FMyCADImporter
{
public:
    static bool ImportCADFile(const FString& FilePath, const FString& DestinationPath);
};
```

```cpp
// MyCADImporter.cpp
#include "MyCADImporter.h"
#include "DatasmithImportFactory.h"
#include "DatasmithSceneFactory.h"
#include "IDatasmithSceneElements.h"

bool FMyCADImporter::ImportCADFile(const FString& FilePath, const FString& DestinationPath)
{
    // 1. 创建 Datasmith 场景
    TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("ImportedCADScene"));

    // 2. 创建导入上下文和选项 (此处可配置 CAD 特定选项)
    FDatasmithImportContext ImportContext;
    // ... 配置 ImportContext.Options，其中包含 CAD 导入器的参数 ...

    // 3. 使用 Datasmith 导入工厂处理文件
    // 内部会调用 DatasmithCADTranslator 等模块
    UDatasmithImportFactory* ImportFactory = GetMutableDefault<UDatasmithImportFactory>();
    bool bImportSuccess = ImportFactory->ImportDatasmithScene(FilePath, Scene, ImportContext);

    if (bImportSuccess)
    {
        // 4. 将场景中的资产保存到磁盘
        // 此步骤会触发网格构建、材质创建等
        FDatasmithSceneExporter::ExportScene(Scene, DestinationPath);
        return true;
    }
    return false;
}
```

## 模块依赖

要使用此插件的功能（通常通过 Datasmith 导入器间接使用），你的项目需要依赖以下独特的模块：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对主流 CAD 格式（如 CATIA, NX, STEP, IGES）的解析能力，是 CADInterfaces 模块的底层依赖。 |
| `OpenNurbs6` | 用于解析 Rhino 的 .3dm 文件格式，是 DatasmithOpenNurbsTranslator 模块的底层依赖。 |

**注意**：作为使用者，你通常不需要直接在项目的 `.Build.cs` 中添加这些依赖。当你启用 `DatasmithCADImporter` 插件并使用 Datasmith 导入器时，引擎会自动处理这些依赖关系。

## 维护状态

### 近期更新

```
- 70cdacc72d5f Upgraded TechSoft SDK from 2025.3.0 to 2025.6.1
- 72a038a471b6 [In Progress] InterchangeCADImporter plugin - Added skeleton translated nodes for meshes - Added skeleton CAD pipelines for mesh, actor and level and a composite one - Miscellaneous changes on the Wire parser
- 4e58d19c78bc Fixed crash importing CAD scene with root node(and below) hidden
```

- **TechSoft SDK 升级**：保持对最新 CAD 格式和标准的支持，是持续维护的积极信号。
- **InterchangeCADImporter 开发**：表明 Epic 正在基于此插件开发下一代的 CAD 导入框架（Interchange），预示着未来架构的演进。
- **Bug 修复**：修复了特定场景下的崩溃问题，说明插件仍在被积极使用和维护。

### 维护评价

**活跃维护**。该插件创建于2019年，作为 Epic Games 官方支持的 Enterprise 级功能，一直是 Datasmith 工具链的核心组成部分。从近期提交记录看，它不仅在进行常规的 SDK 升级和 Bug 修复，还在被用于开发新的 Interchange 框架，这证明了其代码库的活跃度和重要性。对于需要导入 CAD 数据的项目，这是一个**可靠且推荐使用**的官方解决方案。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (如果存在)