# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD导入工具集 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 6 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

此插件是 Unreal Engine 的 **企业版** Datasmith 数据导入框架的核心组成部分，专门用于处理和转换各种专业的 CAD（计算机辅助设计）软件产生的数据格式。其核心功能是将复杂的 CAD 模型（包含几何体、材质、图层、装配层级等信息）解析并转换为 Unreal Engine 原生理解的 Datasmith 场景元素（如 `IDatasmithScene`, `IDatasmithActorElement`, `IDatasmithMeshElement` 等），从而实现工业级 CAD 数据向实时 3D 应用程序的高保真导入。

与通用的 FBX 导入不同，此插件提供了对特定 CAD 格式（如 Alias `.wire` 文件、PLMXML、OpenNurbs 等）的深度解析支持，能够保留 CAD 软件中特有的数据结构（如 B-Rep 边界表示、修剪曲面、特定材质模型），并通过内部的转换器（如 `CADKernel`, `TechSoft`）将其转化为引擎可用的网格和材质数据。

**为什么存在？** 为了解决游戏引擎与工业设计、制造业 CAD 软件之间的数据交换鸿沟。它允许汽车、航空航天、工业设计等领域的设计师和工程师，直接将他们使用的专业 CAD 软件（如 Autodesk Alias）中的模型导入到 UE 中，用于产品可视化、虚拟评审、数字孪生等场景，而无需经过中间格式（如 STEP, IGES）的多次转换和数据损失。

## 使用场景

-   你是一名**汽车设计师**，使用 Autodesk Alias 进行汽车外观设计，需要将 `.wire` 格式的模型实时导入 Unreal Engine 以创建高质量的配置器或虚拟展厅。
-   你的团队使用 **PLM（产品生命周期管理）系统**，需要将 PLMXML 格式的产品结构数据批量导入 UE，用于构建数字孪生或装配指导应用。
-   你需要将基于 **NURBS 曲面** 的 CAD 模型（如 Rhino 文件）导入 UE，并希望尽可能保持曲面的精确度和拓扑信息。
-   你的项目需要处理来自**多个版本 CAD 软件**的模型数据（从 2020 到 2026+），并希望使用统一的、版本兼容的接口进行导入。

## 蓝图用法

此插件主要作为底层的 C++ 翻译器和接口库，其功能通过 Datasmith 的标准导入流程（例如通过“导入”面板或 Datasmith 导入器）被调用。**它不提供直接的、面向设计师的蓝图可调用节点**。其用户交互主要发生在编辑器内容的导入对话框中，当用户选择导入 `.wire`、`.plmxml` 等支持的格式时，此插件会作为后端引擎自动介入。

## C++ 用法

### 核心接口

插件的核心是通过 `IWireInterface` 等接口定义翻译器的功能，然后由具体的 `FWireTranslatorImpl` 类实现。使用时，通常通过 `DatasmithDispatcher` 或 `DatasmithCADTranslator` 模块来调度和管理这些翻译器。

### 基本用法（使用 WireInterface）

以下代码示例演示了如何使用 `WireInterface` 来加载一个 `.wire` 文件并获取其网格数据。这通常由 Datasmith 的导入管线内部调用，但展示了底层 API 的用法。

*来源: `Engine/Plugins/Enterprise/DatasmithCADImporter/Source/WireInterface/WireInterface2025_0/Private/WireInterfaceImpl.h`*

```cpp
#include "WireInterfaceModule.h"
// 注意：实际使用中，更多是通过 Datasmith 的高级 API 间接触发。

// 假设已有一个实现 IWireInterface 的实例（如 FWireTranslatorImpl）
TSharedPtr<IWireInterface> WireTranslator = MakeShared<FWireTranslatorImpl>();

// 1. 初始化翻译器，指向 .wire 文件路径
FString ScenePath = TEXT("C:/Models/MyCar.wire");
bool bSuccess = WireTranslator->Initialize(*ScenePath);

// 2. 配置导入选项（可选）
FWireSettings ImportSettings;
// ... 配置 ImportSettings ...
WireTranslator->SetImportSettings(ImportSettings);

// 3. 设置输出路径（用于缓存或中间文件）
FString OutputPath = FPaths::ProjectSavedDir() / TEXT("DatasmithCache");
WireTranslator->SetOutputPath(OutputPath);

// 4. 加载场景，传入一个待填充的 Datasmith 场景对象
TSharedPtr<IDatasmithScene> DatasmithScene = FDatasmithSceneFactory::CreateScene(TEXT("MyCar"));
if (WireTranslator->Load(DatasmithScene))
{
    // 此时，DatasmithScene 对象中应已填充从 .wire 文件解析出的层级、网格、材质等信息
    // 接下来可以将其传递给 Datasmith 的进一步处理或直接用于场景构建。
}

// 5. （可选）获取特定网格的负载数据
TSharedPtr<IDatasmithMeshElement> MeshElement = /* 从 DatasmithScene 中获取 */;
FDatasmithMeshElementPayload MeshPayload;
FDatasmithTessellationOptions TessOptions;
WireTranslator->LoadStaticMesh(MeshElement, MeshPayload, TessOptions);
// MeshPayload 包含了可用于创建 UStaticMesh 的网格描述数据
```

### 进阶用法（转换器与几何处理）

更复杂的操作发生在转换器内部。例如，`FAliasModelToCADKernelConverter` 负责将 Alias 的几何数据（B-Rep）转换为 CADKernel 的拓扑结构，然后进行网格化。

*来源: `Engine/Plugins/Enterprise/DatasmithCADImporter/Source/WireInterface/WireInterface2025_0/Private/AliasModelToCADKernelConverter.h`*

```cpp
// 通常由翻译器内部流程调用，非直接用户代码。
// 以下展示了转换器的部分工作流程：
TSharedPtr<FAliasModelToCADKernelConverter> Converter = MakeShared<FAliasModelToCADKernelConverter>(TessellationOptions, ImportParameters);

// 添加一个 B-Rep 几何体（例如一个 DagNode）
const FAlDagNodePtr& DagNode = /* 从 .wire 文件遍历得到的节点 */;
bool bAdded = Converter->AddBRep(DagNode, Color, EAliasObjectReference::LocalReference);

// 添加完成后，进行拓扑修复（可选但推荐）
if (Converter->RepairTopology())
{
    // 进行网格剖分
    FMeshDescription OutMeshDescription;
    CADLibrary::FMeshParameters MeshParams;
    Converter->Tessellate(MeshParams, OutMeshDescription);
    // OutMeshDescription 现在包含可供 UE 使用的网格数据
}
```

## Demo 示例

一个最小的 C++ 示例，演示如何实例化并基本使用 WireInterface 模块。**请注意**：由于插件 `EnabledByDefault=false`，你需要先在项目设置或 `.uproject` 文件中手动启用它。

**MyWireLoader.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "WireInterfaceModule.h" // 引入模块头文件
#include "IWireInterface.h"      // 引入接口

class FMyWireLoader
{
public:
    bool LoadWireFile(const FString& FilePath, TSharedPtr<IDatasmithScene>& OutScene);
};
```

**MyWireLoader.cpp**
```cpp
#include "MyWireLoader.h"
#include "WireInterfaceImpl.h" // 注意：这是私有头文件，实际项目中应通过模块接口获取

bool FMyWireLoader::LoadWireFile(const FString& FilePath, TSharedPtr<IDatasmithScene>& OutScene)
{
    // 检查模块是否可用
    if (!FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("Datasmith Wire Translator module is not loaded."));
        return false;
    }

    // 创建一个翻译器实例（简化示意，实际需通过工厂或模块获取）
    TSharedPtr<IWireInterface> Translator = MakeShared<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl>();

    // 初始化
    if (!Translator->Initialize(*FilePath))
    {
        return false;
    }

    // 创建输出场景
    OutScene = FDatasmithSceneFactory::CreateScene(FName(*FPaths::GetBaseFilename(FilePath)));

    // 执行加载
    return Translator->Load(OutScene);
}
```

## 模块依赖

此插件的模块依赖了多个处理特定 CAD 格式和几何计算的外部库或内部库。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 用于解析和处理多种通用 CAD 格式（如 STEP, IGES, JT）的核心库。`CADInterfaces` 模块依赖于此。 |
| `OpenNurbs6` | 用于解析 Rhino（.3dm）等基于 NURBS 的 CAD 文件。`DatasmithOpenNurbsTranslator` 模块依赖于此。 |
| `CADKernel` | Epic 内部的几何内核库，用于 B-Rep 模型的处理、修复和曲面细分。是许多转换器的基础。 |
| `DatasmithCore` | Datasmith 的核心运行时和接口定义，是所有 Datasmith 插件的基础。 |
| `DatasmithContent` | Datasmith 的内容资产和工具，可能用于材质、资产的后处理。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下 double 常量截断为 float 产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，确保在安装了 Alias 2027 的环境下 Wire 翻译器仍能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存的版本号。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间可移植。 |

### 维护评价

**综合评价：维护中，但启用和使用门槛较高。**

- **活跃度**：插件仍在积极维护，最近一周内有多次提交，主要关注编译兼容性、第三方库更新以及对新版本 CAD 软件（Alias 2027）的适配。
- **稳定性与限制**：作为企业版功能，其稳定性经过了验证，但 **默认未启用** (`EnabledByDefault=false`)，表明它可能包含专利技术、依赖特定许可或面向高级用户。使用前需要手动启用并可能需要配置特定的第三方库（如 TechSoft）。
- **推荐度**：**推荐**给有专业 CAD 数据导入需求的企业用户或开发者。对于需要导入 Alias `.wire`、PLMXML、JT 等专业格式的项目，这是官方提供的核心解决方案。普通游戏开发者通常无需使用此插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)