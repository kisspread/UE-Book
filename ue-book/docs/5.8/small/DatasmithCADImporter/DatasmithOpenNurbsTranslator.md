# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD文件导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

此插件并非简单的“工具集合”，而是一个完整的**计算机辅助设计（CAD）文件格式转换与导入引擎**。它解决了将主流工业CAD软件（如CATIA, SolidWorks, Rhino/Grasshopper, NX, Alias等）生成的复杂参数化模型（如`.3dm`, `.step`, `.iges`, `.jt`等）导入到虚幻引擎的核心技术挑战。

其核心功能包括：
1.  **多格式解析**：支持通过各种内部翻译器（Translator）解析不同CAD格式的几何数据、拓扑结构和元数据。
2.  **几何转换**：将CAD模型中的边界表示（B-Rep）、参数化曲面等高级几何数据，转换为引擎可渲染的三角网格（Mesh）。这个过程涉及复杂的曲面细分（Tessellation）和容差控制。
3.  **进程调度**：通过`DatasmithDispatcher`管理外部进程来执行资源密集型的转换任务，避免阻塞编辑器主线程。
4.  **缓存管理**：管理转换后的中间数据缓存，优化重复导入的性能。

**为什么存在**：虚幻引擎的原生网格导入器无法处理CAD软件特有的复杂几何拓扑和参数化数据。此插件填补了这一空白，使得建筑、工程和施工（AEC）、产品设计与可视化等领域的资产能够高效地进入虚幻引擎进行实时渲染和交互。

## 使用场景

-   你正在使用**Rhino/Grasshopper**进行建筑设计或参数化设计，需要将生成的`.3dm`文件直接导入引擎，并希望控制是使用模型自带的网格还是让引擎重新进行NURBS细分。
-   你需要从**CATIA**、**SolidWorks**、**NX**等工业设计软件导入产品模型（如`.step`, `.jt`格式）进行实时可视化或虚拟评审。
-   你需要为汽车设计（如使用**Alias**）创建数字孪生或配置器，需要导入复杂的A级曲面模型。
-   你的工作流中需要**批量**或**自动化**导入大量CAD文件。

## 蓝图用法

此插件的功能主要通过Datasmith的通用导入流程和特定于格式的导入选项在蓝图中使用。搜索结果显示，公共API主要暴露了用于配置的`UCLASS`。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UDatasmithOpenNurbsImportOptions` | 用于配置Rhino（OpenNurbs）文件导入参数的选项类，可在导入设置面板中找到。 | `UDatasmithOpenNurbsImportOptions` |
| `FDatasmithOpenNurbsOptions` | 蓝图可读写的结构体，包含具体配置，如`Geometry`（几何来源）。 | `FDatasmithOpenNurbsOptions` |

### 使用示例（蓝图描述）

蓝图通常不直接调用此插件的转换逻辑。你将在“内容浏览器”中右键点击一个支持的CAD文件（如`.3dm`），选择“Datasmith导入”。在弹出的导入对话框中，会看到一个“几何与细分选项”分类，其中包含来自`UDatasmithOpenNurbsImportOptions`的配置项。你可以在这里选择：
1.  “在虚幻中细分NURBS”：由引擎的CAD内核重新生成网格。
2.  “导入Rhino网格和UV”：使用Rhino文件中预先计算好的网格数据。

这些选择会影响导入后的模型质量、UV布局和文件大小。

## C++ 用法

### 头文件引入

```cpp
// 要使用Datasmith核心接口
#include "DatasmithSceneFactory.h"
#include "DatasmithMesh.h"
#include "DatasmithImportOptions.h"

// 要使用本插件的OpenNurbs翻译器和转换器
#include "DatasmithOpenNurbsTranslatorModule.h"
#include "OpenNurbsBRepConverter.h"
#include "OpenNurbsBRepToCADKernelConverter.h"
// 或 #include "OpenNurbsBRepToTechSoftConverter.h" // 取决于底层转换引擎
```

### 基本用法

（注：以下代码示例基于提供的头文件结构推断，展示了内部转换器的直接使用逻辑，通常这会被上层翻译器封装）

```cpp
// 文件：基于 Private/OpenNurbsBRepConverter.h 和 Private/OpenNurbsBRepToCADKernelConverter.h 推断
// 场景：将一个 OpenNurbs BRep 对象（来自解析的 Rhino 文件）转换为引擎可用的网格数据

#include "CADLibrary/Public/ImportParameters.h"
#include "DatasmithImportOptions.h"
#include "OpenNurbsBRepToCADKernelConverter.h"

void ConvertRhinoBrepToMesh(ON_Brep* RhinoBrep)
{
    if (!RhinoBrep)
    {
        return;
    }

    // 1. 准备导入参数
    CADLibrary::FImportParameters ImportParams;
    ImportParams.ScaleFactor = 1.0; // 设置缩放因子

    // 2. 准备细分选项
    FDatasmithTessellationOptions TessOptions;
    TessOptions.SetGeometricTolerance(0.1f); // 设置几何容差
    TessOptions.SetStitchingTolerance(0.05f); // 设置接合容差

    // 3. 实例化 CADKernel 转换器（这是内部实现之一）
    FOpenNurbsBRepToCADKernelConverter Converter(ImportParams, TessOptions);

    // 4. 执行转换。Offset 用于偏移网格，常将原点置于包围盒中心。
    ON_3dVector Offset(0.0, 0.0, 0.0);
    bool bSuccess = Converter.AddBRep(*RhinoBrep, Offset);

    if (bSuccess)
    {
        // 转换完成后，数据存储在 CADKernel 的拓扑面（FTopologicalFace）中。
        // 这些数据将被后续流程（如 FParametricSurfaceTranslator）进一步处理并生成 FDatasmithMesh。
        UE_LOG(LogTemp, Log, TEXT("OpenNurbs BRep to CADKernel conversion successful."));
    }
}
```

### 进阶用法

更复杂的用法是**注册自定义翻译器**或**理解翻译器生命周期**。以下基于`Private/DatasmithOpenNurbsTranslator.h`推断。

```cpp
// 文件：基于 Private/DatasmithOpenNurbsTranslator.h 推断
// 场景：理解一个完整的 Datasmith 翻译器如何运作

#include "DatasmithTranslator.h"
#include "DatasmithOpenNurbsTranslator.h" // 假设的头文件路径

class FMyCustomTranslator : public FDatasmithOpenNurbsTranslator
{
public:
    virtual FName GetFName() const override { return "MyCustomOpenNurbsTranslator"; }

    // 翻译器初始化时声明它能处理什么文件
    virtual void Initialize(FDatasmithTranslatorCapabilities& OutCapabilities) override
    {
        FDatasmithOpenNurbsTranslator::Initialize(OutCapabilities);
        // 可以在这里添加或修改支持的扩展名
        OutCapabilities.SupportedFileFormats.Add(TEXT("3dm"));
    }

    // 载入场景，解析文件结构
    virtual bool LoadScene(TSharedRef<IDatasmithScene> OutScene) override
    {
        // 调用父类实现来解析 Rhino 文件，获取图层、组等场景结构
        bool bLoaded = FDatasmithOpenNurbsTranslator::LoadScene(OutScene);
        if (bLoaded)
        {
            UE_LOG(LogTemp, Log, TEXT("Custom translator loaded scene successfully."));
        }
        return bLoaded;
    }

    // 载入具体的静态网格资产
    virtual bool LoadStaticMesh(const TSharedRef<IDatasmithMeshElement> MeshElement,
                                FDatasmithMeshElementPayload& OutMeshPayload) override
    {
        // 父类实现内部会调用 FOpenNurbsBRepToCADKernelConverter 等转换器
        return FDatasmithOpenNurbsTranslator::LoadStaticMesh(MeshElement, OutMeshPayload);
    }
};
```

## Demo 示例

一个展示如何在代码中触发OpenNurbs格式文件导入的最小示例。**注意**：实际使用中，通常通过编辑器的GUI或`UDatasmithImportFactory`触发，直接调用`LoadScene`和`LoadStaticMesh`需要完整的上下文（如已解析的文件句柄）。

```cpp
// MyOpenNurbsDemo.h
#pragma once

#include "CoreMinimal.h"
#include "DatasmithScene.h"

class FMyOpenNurbsDemo
{
public:
    /** 演示加载一个Rhino文件并获取其场景数据 */
    static TSharedPtr<IDatasmithScene> LoadRhinoFileDemo(const FString& FilePath);

    /** 演示如何为已加载场景中的第一个网格元素获取网格数据 */
    static FDatasmithMeshElementPayload GetMeshPayloadDemo(
        const TSharedPtr<IDatasmithScene>& Scene,
        const TSharedPtr<IDatasmithMeshElement>& MeshElement
    );
};
```

```cpp
// MyOpenNurbsDemo.cpp
#include "MyOpenNurbsDemo.h"
#include "DatasmithOpenNurbsTranslator.h"
#include "DatasmithSceneFactory.h"

TSharedPtr<IDatasmithScene> FMyOpenNurbsDemo::LoadRhinoFileDemo(const FString& FilePath)
{
    // 1. 创建翻译器实例
    TSharedPtr<FDatasmithOpenNurbsTranslator> Translator = MakeShareable(new FDatasmithOpenNurbsTranslator());

    // 2. 初始化翻译器能力（检查是否可用）
    FDatasmithTranslatorCapabilities Capabilities;
    Translator->Initialize(Capabilities);

    if (!Capabilities.bIsEnabled)
    {
        UE_LOG(LogTemp, Warning, TEXT("OpenNurbs translator is not available. Check if the plugin is enabled and dependencies are present."));
        return nullptr;
    }

    // 3. 设置文件路径并加载场景结构
    Translator->SetSourceFilePath(FilePath);
    TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("MyRhinoImport"));

    if (!Translator->LoadScene(Scene))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load Rhino scene: %s"), *FilePath);
        return nullptr;
    }

    UE_LOG(LogTemp, Log, TEXT("Successfully loaded Rhino scene structure. Found %d elements."),
        Scene->GetMeshesCount());

    return Scene;
}

FDatasmithMeshElementPayload FMyOpenNurbsDemo::GetMeshPayloadDemo(
    const TSharedPtr<IDatasmithScene>& Scene,
    const TSharedPtr<IDatasmithMeshElement>& MeshElement)
{
    FDatasmithMeshElementPayload Payload;
    if (!Scene || !MeshElement)
    {
        return Payload;
    }

    // 重新创建翻译器（在实际应用中，可能需要保持与LoadScene时相同的实例和配置）
    TSharedPtr<FDatasmithOpenNurbsTranslator> Translator = MakeShareable(new FDatasmithOpenNurbsTranslator());
    FDatasmithTranslatorCapabilities Capabilities;
    Translator->Initialize(Capabilities);

    // 设置导入选项（可选）
    TArray<TObjectPtr<UDatasmithOptionsBase>> Options;
    Translator->GetSceneImportOptions(Options);
    // ... 可以修改 Options 中的 FDatasmithOpenNurbsOptions ...
    Translator->SetSceneImportOptions(Options);

    // 加载特定网格的几何数据
    if (Translator->LoadStaticMesh(MeshElement.ToSharedRef(), Payload))
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully loaded static mesh payload."));
    }
    else
    {
        UE_LOG(LogTemp, Warning, TEXT("Failed to load mesh payload for element: %s"),
            *MeshElement->GetName());
    }

    return Payload;
}
```

## 模块依赖

要使用此插件，你的项目或模块无需直接依赖其内部模块。通过 Datasmith 的通用框架进行交互。

如果要在**C++中扩展或集成**此插件的功能，你可能需要依赖以下**独特**的模块：

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | 提供 `IDatasmithScene`, `IDatasmithMeshElement` 等核心Datasmith接口。 |
| `CADLibrary` | 提供 `FImportParameters`, 网格操作工具等基础CAD数据结构和函数。 |
| `CADKernel` | 提供参数化曲面内核（`FTopologicalFace`, `FSurface` 等），用于高级几何转换。 |
| `TechSoft` | 提供商业CAD转换SDK（A3DSDK）的封装，是部分转换器（如`FOpenNurbsBRepToTechSoftConverter`）的底层依赖。 |

**注**：`OpenNurbs6` 是开源库，已包含在 `DatasmithOpenNurbsTranslator` 模块内部，使用者无需额外配置。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed. | 增加逻辑，确保线框翻译器在安装了Alias 2027的环境下仍能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3. | 将TechSoft库更新至2026.3版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache. | 更新了DatasmithCAD缓存文件的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在MSVC和Clang编译器之间可移植，增强跨平台兼容性。 |

### 维护评价

-   **活跃维护**：作为 Epic 的 **Enterprise（企业版）** 级插件，Datasmith CAD Importer 受到持续维护和更新。从近期的 git 历史可以看出，在过去的几天内仍有密集的提交，内容包括底层依赖升级（TechSoft）、新版本软件适配（Alias 2027）、跨编译器兼容性修复以及性能/缓存优化。
-   **推荐使用**：**强烈推荐**。对于需要导入工业CAD资产的用户来说，这是官方支持的最强大和可靠的解决方案。插件虽然模块众多、架构复杂，但作为整体产品，其稳定性和功能完整性很高。
-   **注意事项**：默认设置为**未启用** (`EnabledByDefault: false`)。用户必须在“编辑”->“插件”中手动启用“Datasmith CAD Importer”，否则相关的导入功能将不可用。这是因为该插件可能需要额外的许可（部分格式）且体积较大。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) （路径已根据典型UE插件结构推断）