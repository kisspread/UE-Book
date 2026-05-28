# Datasmith CAD Importer

> Collection of tools to work with CAD files.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 中文名 | CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

这是一个企业级插件，专门用于将工业 CAD 软件（如 Autodesk Alias）创建的 `.wire` 格式文件导入到虚幻引擎中。它不仅仅是一个简单的格式转换器，而是深度集成 Datasmith 框架的解决方案，负责解析复杂的 CAD 场景结构（包括层级、几何体、材质），并将其转换为引擎可理解的 Actor、Mesh 和 Material 资产。

其存在是为了解决游戏引擎与工业设计软件之间的数据鸿沟。设计师在 Alias 等软件中创建的高精度 CAD 模型，通常包含参数化曲面、修剪曲面等高级几何信息，该插件能够理解并转换这些数据，使得工业级的资产能够被用于汽车设计、建筑可视化、产品渲染等实时 3D 项目中。

**核心子模块 WireInterface2022 分析**：该模块是处理 Alias 2022 版 `.wire` 文件的核心翻译器。它实现了 `IWireInterface` 接口，负责：
1.  **场景加载与遍历**：解析 `.wire` 文件，遍历其内部的 DAG（有向无环图）节点树。
2.  **几何转换**：将 CAD 中的 Mesh、Surface、Shell 等几何节点转换为虚幻引擎的 `FMeshDescription`。
3.  **材质处理**：将 Alias 的 Blinn、Lambert、Phong 等材质模型转换为 PBR 材质。
4.  **坐标与单位转换**：处理坐标系（从 Z-Up Right-Handed 转换）和单位（从 mm 到 cm）。

## 使用场景

-   你在使用 Autodesk Alias 进行汽车外形设计，需要将数字模型导入虚幻引擎进行实时可视化评审或虚拟样车制作。
-   你的工作流程涉及从 CAD 软件（支持 `.wire` 格式）向虚幻引擎传输资产，并需要保留原始的材质属性、层级结构和几何精度。
-   你需要处理包含复杂参数化曲面和修剪边界的 CAD 数据，并希望在引擎中保持其拓扑结构的准确性。

## 蓝图用法

根据提供的源码分析，此插件主要作为数据转换的后端运行，**没有直接暴露 `BlueprintCallable` 节点供蓝图调用**。所有导入和转换操作均由 Datasmith 框架内部的导入流程驱动。用户通过虚幻编辑器的标准 Datasmith 导入流程（如文件拖放或菜单导入）来使用该插件提供的功能。

## C++ 用法

此插件主要作为 Datasmith 框架的一个特定格式翻译器模块使用。直接操作的 API 面向需要扩展或定制 CAD 导入流程的开发者。

### 头文件引入

要使用 WireInterface2022 模块的功能，需要包含其公共头文件。

```cpp
#include "WireInterface/WireInterfaceModule.h" // 模块访问
#include "IWireInterface.h" // 核心接口
```

### 基本用法

`WireInterface2022` 模块的核心类是 `FWireTranslatorImpl`，它实现了 `IWireInterface` 接口。通常由 Datasmith 的调度器（`DatasmithDispatcher`）在后台实例化和使用。以下代码展示了其接口的基本使用模式，**这通常不由最终用户直接调用，而是集成在导入流程中**。

```cpp
// 假设已获得一个 IWireInterface 实例（通常来自模块工厂或调度器）
TSharedPtr<IWireInterface> WireTranslator = ...;

// 1. 初始化，传入 .wire 文件的完整路径
FString FilePath = TEXT("C:/Models/MyCarModel.wire");
bool bSuccess = WireTranslator->Initialize(*FilePath);

// 2. 设置导入参数
FWireSettings Settings;
// ... 配置 Settings ...
WireTranslator->SetImportSettings(Settings);

// 3. 设置输出路径（用于缓存中间文件）
FString OutputPath = FPaths::ProjectSavedDir() / TEXT("DatasmithCache");
WireTranslator->SetOutputPath(OutputPath);

// 4. 加载场景，将转换结果填充到提供的 IDatasmithScene 中
TSharedPtr<IDatasmithScene> Scene = MakeShared<FDatasmithScene>();
bSuccess = WireTranslator->Load(Scene);

// 5.（可选）加载单个网格体并获取其负载数据，用于更精细的控制
TSharedPtr<IDatasmithMeshElement> MeshElement = ...;
FDatasmithMeshElementPayload MeshPayload;
FDatasmithTessellationOptions TessOptions;
bSuccess = static_cast<FWireTranslatorImpl*>(WireTranslator.Get())->LoadStaticMesh(MeshElement, MeshPayload, TessOptions);
```

**来源**: 基于 `Private/WireInterfaceImpl.h` 中 `FWireTranslatorImpl` 类的公共接口推断。

### 进阶用法

该插件的设计允许使用不同的后端转换器来处理几何体。在 `WireInterface2022` 模块内部，存在两种转换路径：

1.  **CADKernel 路径** (`FAliasModelToCADKernelConverter`)：将 Alias 的 B-Rep（边界表示）几何体转换为 UE 自研的 CADKernel 内存表示，然后进行曲面细分。
2.  **TechSoft 路径** (`FAliasModelToTechSoftConverter`)：使用第三方的 TechSoft 库来处理 B-Rep 几何体。

转换器的选择和配置依赖于 `ImportParameters`。开发者可以根据需求扩展或替换这些转换逻辑。

```cpp
// 示例：创建一个基于 CADKernel 的转换器
// 注意：这是一个底层操作，通常集成在 FWireTranslatorImpl 的实现内部
FDatasmithTessellationOptions TessOptions;
CADLibrary::FImportParameters ImportParams;

// 创建转换器实例
auto Converter = MakeShared<FAliasModelToCADKernelConverter>(TessOptions, ImportParams);

// 假设我们有一个表示几何体的 FDagNodeGeometry
FDagNodeGeometry Geometry(...);
// 将几何体添加到转换器进行处理
bool bAdded = Converter->AddGeometry(Geometry);

// 执行拓扑修复和曲面细分
Converter->RepairTopology();
FMeshDescription OutMesh;
CADLibrary::FMeshParameters MeshParams;
bool bTessellated = Converter->Tessellate(MeshParams, OutMesh);
```

**来源**: 基于 `Private/AliasModelToCADKernelConverter.h` 的接口和 `WireInterfaceImpl.h` 中 `GetModelConverter()` 方法推断。

## Demo 示例

由于此插件是 Datasmith 框架的内部模块，没有独立的“最小可运行示例”。其使用完全集成在 Datasmith 的 `.wire` 文件导入流程中。

一个概念性的 C++ 使用示例如下，展示了如何在引擎内手动触发一次 `.wire` 文件的解析（**注意：实际环境中此操作由导入器自动完成**）：

```cpp
// MyWireImporter.h
#pragma once

#include "CoreMinimal.h"
#include "WireInterfaceModule.h"
#include "IWireInterface.h"

class FMyWireImporter
{
public:
    static bool ImportWireFile(const FString& InFilePath, TSharedPtr<IDatasmithScene>& OutScene);
};

// MyWireImporter.cpp
#include "MyWireImporter.h"

bool FMyWireImporter::ImportWireFile(const FString& InFilePath, TSharedPtr<IDatasmithScene>& OutScene)
{
    // 检查 WireTranslator 模块是否可用
    if (!UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("WireTranslator module is not loaded."));
        return false;
    }

    // 通常，具体的 IWireInterface 实例由模块根据文件版本（如2022, 2023）创建
    // 这里我们假设通过模块工厂或直接实例化特定版本的翻译器
    // 实际代码中，您会使用类似 FWireInterface2022Factory::Create() 的方式
    TSharedPtr<IWireInterface> Translator = MakeShared<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl>();
    if (!Translator.IsValid())
    {
        return false;
    }

    // 初始化
    if (!Translator->Initialize(*InFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize translator for file: %s"), *InFilePath);
        return false;
    }

    // 配置
    FWireSettings Settings;
    Translator->SetImportSettings(Settings);
    Translator->SetOutputPath(FPaths::ProjectSavedDir() / TEXT("MyImportCache"));

    // 创建输出场景
    OutScene = MakeShared<FDatasmithScene>();

    // 执行加载/转换
    bool bLoaded = Translator->Load(OutScene);
    if (!bLoaded)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load scene from wire file."));
    }

    return bLoaded;
}
```

## 模块依赖

要使用此插件（特别是 `WireInterface2022` 模块），您的项目或模块需要链接以下特定依赖：

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对 `.wire` 等 CAD 格式进行解析的底层库。 |
| `CADKernel` | Epic 自研的 CAD 内核库，用于进行 B-Rep 几何体的内存表示和拓扑操作。 |
| `DatasmithCore` | Datasmith 框架的核心接口和数据结构（如 `IDatasmithScene`, `IDatasmithMeshElement`）。 |
| `DatasmithContent` | Datasmith 的内容类型资产和材质转换逻辑。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数产生的警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加逻辑，允许 Wire 翻译器在安装了 Alias 2027 的情况下仍能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间可移植。 |

### 维护评价

该插件作为 Unreal Engine 企业版的一部分，由 Epic Games 维护，用于支持其重要客户（如汽车制造商）的工作流。从提交历史看，**维护活跃但频率不高**。最近的更新集中在编译兼容性修复（`852b276c`, `3e657fb3`）、第三方库更新（`52c91865`）以及对新版本 CAD 软件的支持（`889b1ce2`，针对 Alias 2027）。

尽管它创建于约 7 年前，但仍在持续迭代以保持与最新工业软件版本的兼容性并修复问题。对于需要处理 `.wire` 格式 CAD 文件的企业级用户，这是一个**推荐使用**的官方解决方案。对于个人或小型项目，考虑到其启用状态（默认禁用）和复杂性，需评估是否有实际需求。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例]（在提供的源码文件列表中未发现明确的测试文件，可能位于 Engine 的其他测试目录中。）