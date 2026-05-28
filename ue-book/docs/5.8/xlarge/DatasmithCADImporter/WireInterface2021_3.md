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
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

这是一个**企业级 CAD 文件翻译与导入插件**，核心功能是将多种 CAD 格式文件（如 Alias `.wire`、OpenNurbs、PLMXML 等）转换为 Unreal Engine 可用的场景资产。它通过 **Datasmith** 框架工作，提供了一套完整的工具链来解析 CAD 文件的几何结构、层级关系、材质信息和装配关系，并将其映射到 UE 的 Actor、Mesh 和 Material 系统中。

与 UE 内置的通用 FBX 导入器不同，此插件专注于处理工业 CAD 软件生成的高精度、参数化模型。它解决了以下问题：

1.  **格式兼容性**：支持多种专业 CAD 格式，这些格式通常包含复杂的曲面（NURBS）、修剪边界和装配树结构，无法通过通用导入器处理。
2.  **数据保真度**：尽可能保留 CAD 模型中的设计意图，如层（Layer）、对称性（Symmetry）、材质参数（如 Blinn、Phong 着色器）和变换信息。
3.  **性能与可扩展性**：使用模块化架构，为不同版本的 CAD 文件格式提供独立的翻译器模块（如 `WireInterface2021_3`, `WireInterface2022` 等），便于维护和扩展。
4.  **生产流水线集成**：与 Datasmith 工作流无缝集成，支持批量处理和缓存（如 `DatasmithDispatcher` 模块），适用于建筑、汽车、产品设计等领域的大规模资产导入。

## 使用场景

- **汽车行业设计评审**：需要将 Alias 等工业设计软件创建的 `.wire` 格式汽车外形模型导入 UE，进行实时渲染和虚拟展示。
- **建筑信息模型 (BIM)**：从支持 PLMXML 或其他 CAD 格式的建筑软件中导入精确的建筑构件模型，用于 VR 预览或数字孪生。
- **复杂产品可视化**：导入包含复杂曲面和装配关系的机械零件 CAD 文件，用于产品配置器或技术文档的可视化。
- **遗留资产转换**：将旧版本 CAD 软件生成的模型（通过 `WireInterface2020` 等模块）转换为现代 UE 可用的资产，避免数据丢失。

## 蓝图用法

该插件主要作为**翻译器**在引擎内部工作，不直接提供蓝图节点。资产导入过程通过 Datasmith 导入器 UI 或 `UAssetImportTask` 在 C++ 中触发。蓝图无法直接控制具体的翻译逻辑，但可以触发整个导入流程。

### 间接使用方式（通过 Datasmith 框架）

1.  在编辑器中，通过 **File > Import** 选择支持的 CAD 文件（如 `.wire`）。
2.  引擎会自动调用此插件中对应的翻译器模块（如 `DatasmithWireTranslator`）处理文件。
3.  导入设置（如曲面细分选项）通过 Datasmith 导入对话框配置。

## C++ 用法

### 核心工作流程

插件的 C++ 用法通常涉及继承和扩展其翻译器类，或直接调用其库函数进行底层模型处理。以下示例展示了如何通过 `IWireInterface` 接口加载和转换一个 `.wire` 文件。

### 头文件引入

```cpp
#include "DatasmithWireTranslator/Public/WireInterfaceModule.h"
```

### 基本用法

以下代码演示了如何初始化一个 Wire 文件翻译器并加载场景。此示例基于 `WireInterfaceModule.h` 和 `WireInterfaceImpl.h` 中的接口。

```cpp
// 文件路径：Engine/Plugins/Enterprise/DatasmithCADImporter/Source/DatasmithWireTranslator/Public/WireInterfaceModule.h
// 文件路径：Engine/Plugins/Enterprise/DatasmithCADImporter/Source/WireInterface/Private/WireInterfaceImpl.h

#include "DatasmithWireTranslator/Public/WireInterfaceModule.h"
#include "WireInterface/IWireInterface.h"

// 获取 Wire 翻译器模块
UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule& WireModule = 
    UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();

if (WireModule.IsAvailable())
{
    // 注意：IWireInterface 的实例化通常由内部工厂完成，此处为概念性演示。
    // 实际使用中，您可能通过一个工厂函数或模块提供的方法来获取实例。
    // TSharedPtr<IWireInterface> WireInterface = WireModule.CreateWireInterface(); // 假设的工厂方法

    // 示例中直接使用 FWireTranslatorImpl 的公共接口（通常不直接构造）
    TSharedPtr<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::IWireInterface> WireInterface = 
        MakeShareable(new UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl());

    // 1. 初始化翻译器，指向要导入的 .wire 文件路径
    const TCHAR* WireFilePath = TEXT("C:/Models/CarBody.wire");
    if (WireInterface->Initialize(WireFilePath))
    {
        // 2. 创建一个空的 Datasmith 场景用于接收数据
        TSharedPtr<IDatasmithScene> DatasmithScene = FDatasmithSceneFactory::CreateScene(TEXT("ImportedWireScene"));

        // 3. 加载（翻译）.wire 文件的内容到 Datasmith 场景中
        if (WireInterface->Load(DatasmithScene))
        {
            UE_LOG(LogTemp, Log, TEXT("Wire file loaded successfully. Scene has %d actors."), 
                DatasmithScene->GetActorsCount());
            
            // 此时，DatasmithScene 中已包含从 .wire 文件转换而来的 Actor 层级结构、Mesh 和 Material 数据。
            // 接下来，可以使用 Datasmith 的导入器将这些数据最终转换为 UE 的资产。
        }
        else
        {
            UE_LOG(LogTemp, Error, TEXT("Failed to load wire file."));
        }
    }
}
```

### 进阶用法

对于需要更精细控制（如自定义细分或材质转换）的场景，可以深入使用 `FWireTranslatorImpl` 的内部方法，或扩展 `FAliasModelToCADKernelConverter` 等转换器类。

```cpp
// 文件路径：Engine/Plugins/Enterprise/DatasmithCADImporter/Source/WireInterface/Private/AliasModelToCADKernelConverter.h

#include "Private/AliasModelToCADKernelConverter.h"

// 假设已经有一个 FAlDagNodePtr 代表从 .wire 文件中遍历得到的某个几何节点
// FAlDagNodePtr GeomNode = ...;

// 创建一个转换器实例，指定细分选项
FDatasmithTessellationOptions TessOptions;
TessOptions.ChordTolerance = 0.1f; // 设置弦高公差
TessOptions.MaxEdgeLength = 10.0f; // 设置最大边长
CADLibrary::FImportParameters ImportParams;
FAliasModelToCADKernelConverter Converter(TessOptions, ImportParams);

// 将 Alias 节点添加到转换器进行处理
Converter.AddBRep(GeomNode, FColor::White, EAliasObjectReference::LocalReference);

// 执行拓扑修复（如果需要）
Converter.RepairTopology();

// 生成网格描述
FMeshDescription MeshDesc;
CADLibrary::FMeshParameters MeshParams;
if (Converter.Tessellate(MeshParams, MeshDesc))
{
    // 现在 MeshDesc 包含了转换后的网格数据，可以进一步处理或创建 UStaticMesh
}
```

## Demo 示例

一个最小化的示例，展示如何获取模块实例并检查其可用性。完整的导入流程需要集成 Datasmith 的资产管线，此处仅演示入口点。

```cpp
// MyCADImporter.h
#pragma once
#include "CoreMinimal.h"
#include "DatasmithWireTranslator/Public/WireInterfaceModule.h"

class FMyCADImporter
{
public:
    static bool CanImportWireFiles();
    static void ImportWireFile(const FString& FilePath);
};
```

```cpp
// MyCADImporter.cpp
#include "MyCADImporter.h"
#include "WireInterface/IWireInterface.h"
#include "DatasmithSceneFactory.h"

bool FMyCADImporter::CanImportWireFiles()
{
    // 检查 Wire 翻译器模块是否已加载
    return UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable();
}

void FMyCADImporter::ImportWireFile(const FString& FilePath)
{
    if (!CanImportWireFiles())
    {
        UE_LOG(LogTemp, Warning, TEXT("Datasmith CAD Importer (Wire) plugin is not available."));
        return;
    }

    // 获取模块实例
    auto& WireModule = UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::Get();

    // 注意：在实际插件中，实例通常通过模块内部管理。
    // 此处为了示例简洁，假设模块提供了一个创建翻译器实例的方法。
    // TSharedPtr<IWireInterface> Translator = WireModule.CreateTranslator();

    // 以下是概念性代码，展示了调用顺序：
    /*
    if (Translator->Initialize(*FilePath))
    {
        TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(FName("Import"));
        if (Translator->Load(Scene))
        {
            // 导入成功，Scene 包含转换后的数据
            UE_LOG(LogTemp, Log, TEXT("Successfully translated wire file: %s"), *FilePath);
            // 此处可将 Scene 传递给 Datasmith 的资产创建流程
        }
    }
    */
}
```

## 模块依赖

该插件的模块高度特化，依赖于特定的第三方 CAD 库。使用者通常**不需要**在自己的 `Build.cs` 中直接依赖这些模块，除非您正在开发自定义的 CAD 翻译器。

| 模块 | 用途 |
|---|---|
| `TechSoft` | 用于处理多种 CAD 格式的核心商业库（如 JT, STEP, IGES 等）。这是 `CADInterfaces` 模块的依赖。 |
| `OpenNurbs6` | 用于处理 Rhino 3DM (OpenNurbs) 文件格式的开源库。这是 `DatasmithOpenNurbsTranslator` 模块的依赖。 |
| `CADLibrary` | 插件内部的公共库，提供 CAD 模型数据结构、导入参数和转换基类。 |
| `DatasmithCore` | Datasmith 的核心框架，提供场景、元素（Actor, Mesh, Material）的抽象接口。 |

**注意**：`TechSoft` 是商业库，可能需要单独的许可证。这通常只对 Unreal Engine 的企业版用户可见和可用。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量被截断为浮点数时产生的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增加逻辑，使 Wire 翻译器在安装了 Alias 2027 的情况下仍能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新到 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间保持可移植性。 |

### 维护评价

**活跃维护**。该插件是 Unreal Engine 企业功能的核心组成部分，持续获得更新。

- **活跃度**：最近的提交记录显示，在 **2026年5月** 仍有密集的更新，内容涉及**新版本软件兼容性**（Alias 2027）、**第三方库升级**（TechSoft）和**编译器兼容性修复**。这表明它仍在被积极开发和维护，以支持最新的 CAD 软件生态。
- **年龄**：创建于 2019 年，是一个成熟的插件，经过多年迭代。
- **稳定性**：由于是 Epic Games 官方维护的企业插件，其稳定性和与引擎的兼容性有保障。
- **使用建议**：**强烈推荐**给需要处理专业 CAD 数据的企业用户和开发者。默认未启用 (`EnabledByDefault=false`)，使用者需在项目设置中手动启用，并确保拥有必要的第三方库许可（如 TechSoft）。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- 测试用例：通常位于 `Engine/Tests/` 目录下，与 Datasmith 相关。