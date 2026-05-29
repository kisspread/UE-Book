# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD数据导入工具集 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

这个插件是一个功能强大的企业级 CAD 文件导入和转换框架。它不仅仅是一个简单的文件导入器，而是一个**完整的 CAD 数据处理管线**。其核心目标是将来自各种专业 CAD 软件（如 CATIA, SolidWorks, NX, Creo, Alias 等）的复杂、精确的参数化几何体，高质量地转换为虚幻引擎可用的三角形网格（`FMeshDescription`）。

它解决了以下关键问题：
1.  **格式支持**：通过模块化设计，为不同的 CAD 格式（如通用 STEP/IGES、工业软件特定的 `.wire`/`.jt` 等）提供专门的翻译器。
2.  **几何体转换**：CAD 模型通常是参数化曲面（NURBS），需要经过**曲面细分（Tessellation）** 才能在游戏引擎中渲染。`CADLibrary` 和 `CADKernelSurface` 等模块负责此核心转换过程。
3.  **拓扑与材质保持**：在转换过程中，尽力保留原始 CAD 模型的拓扑信息（如面、边、顶点关系）和材质分配。`FMeshDescriptionDataCache` 等类用于在转换过程中维护材质槽名称等元数据。
4.  **并行与分布式处理**：通过 `DatasmithDispatcher` 等模块，支持将大型装配体的处理任务分发到多个进程或计算机，以加快导入速度。
5.  **兼容性**：包含多个版本的 `WireInterface` 模块，以支持不同时期的 Alias Wire 文件格式。

**简而言之，它解决了将大型、复杂的工业 CAD 数据无缝带入实时 3D 环境（UE5）的难题，是建筑、工程、施工（AEC）和产品设计可视化的基石工具。**

## 使用场景

-  **工业产品可视化**：你需要将来自 SolidWorks 或 CATIA 的汽车、家电等产品的精确 CAD 模型导入 UE，用于创建配置器或营销渲染。
-  **建筑与施工（AEC）**：你需要导入来自 Revit 或 ArchiCAD 的建筑信息模型（BIM），用于沉浸式设计评审或虚拟施工模拟。
-  **工厂布局与仿真**：你需要将工厂的 CAD 布局导入 UE，进行物流仿真或机器人路径规划预览。
-  **影视与游戏**：你需要将概念艺术家在 Alias 中创建的高精度车辆或飞船模型导入 UE 进行最终渲染。
-  **CAD 软件互操作**：你需要在 UE 中打开并查看 `.STEP`、`.IGES`、`.JT` 等多种格式的工程数据文件。

**注意**：此插件**默认关闭**，你需要在项目设置的 `Plugins` 面板中手动启用 `Datasmith CAD Importer`。通常，你会通过 **Datasmith** 工作流（如 `Datasmith Import` 或 `Direct Link`）来间接调用它，而不是直接在蓝图中操作。

## 蓝图用法

此插件主要为运行时和数据导入服务，其核心功能通常通过 C++ 的 Datasmith 导入管线调用，或由更上层的 `Datasmith` 插件封装。在 `CADLibrary` 等模块的公共头文件中，公开的 API 主要集中在材质创建和网格转换。

### 核心节点

| 节点 | 说明 | 所在类/命名空间 |
|---|---|---|
| `CreateDefaultUEPbrMaterial` | 创建一个默认的 PBR 材质，用于无材质的 CAD 面。 | `CADLibrary` |
| `CreateUEPbrMaterialFromColor` | 根据给定的 `FColor` 创建一个 PBR 材质。 | `CADLibrary` |
| `CreateUEPbrMaterialFromMaterial` | 根据 `FCADMaterial` 对象（包含颜色、纹理等）创建一个 PBR 材质。 | `CADLibrary` |
| `ConvertBodyMeshToMeshDescription` | 将一个 `FBodyMesh`（CAD 转换后的中间网格格式）转换为虚幻的 `FMeshDescription`。 | `CADLibrary` |

### 使用示例（蓝图描述）

由于这些函数主要在数据导入管线中使用，典型的蓝图用法可能不多。一个可能的场景是，你在自定义导入工具中，需要手动创建材质：
1.  使用 `Make Literal Color` 节点创建一个颜色（例如，红色）。
2.  将其连接到 `CreateUEPbrMaterialFromColor` 节点，得到一个材质对象引用。
3.  你可以将此材质应用到网格体上。`ConvertBodyMeshToMeshDescription` 节点通常会在 Datasmith 导入过程中被底层代码调用，不建议在常规蓝图中直接使用。

## C++ 用法

此插件的 C++ 用法通常涉及扩展导入器或编写自定义的 CAD 处理工具。以下示例基于公共头文件中暴露的 API。

### 头文件引入

```cpp
#include "CADMeshDescriptionHelper.h" // 包含材质创建、网格转换等核心函数
#include "CADKernelTools.h"           // 包含与 CADKernel 交互的工具函数
```

### 基本用法

以下代码展示了如何使用 `CADLibrary` 提供的公共函数来创建材质。来源文件: `CADLibrary/Public/CADMeshDescriptionHelper.h`。

```cpp
// 假设我们有一个 CAD 材质对象
FCADMaterial MyCADMaterial;
MyCADMaterial.Color = FColor(255, 0, 0, 255); // 红色

// 创建一个用于存储 Datasmith 场景元素的共享引用
TSharedRef<IDatasmithScene> DatasmithScene = FDatasmithSceneFactory::CreateScene(TEXT("MyScene"));

// 使用 CAD 材质创建对应的 UE PBR 材质
TSharedPtr<IDatasmithUEPbrMaterialElement> UEMaterial = CADLibrary::CreateUEPbrMaterialFromMaterial(MyCADMaterial, DatasmithScene);

if (UEMaterial.IsValid())
{
    // 材质创建成功，可以将其应用到 Datasmith 网格元素上
    // ...
}
```

### 进阶用法

结合 `FCADKernelTools` 进行 CAD 内核级别的曲面细分。这通常发生在更底层的导入代码中。来源文件: `CADLibrary/Public/CADKernelTools.h`。

```cpp
// 假设已经通过某种方式得到了一个 CADKernel 的拓扑实体（例如，一个面）
UE::CADKernel::FTopologicalShapeEntity* MyCADKernelEntity = /* ... */;

// 准备转换上下文
CADLibrary::FImportParameters ImportParams;
ImportParams.ScaleFactor = 1.0f; // 单位缩放
CADLibrary::FMeshParameters MeshParams;
// 设置网格质量参数...
CADLibrary::FMeshConversionContext ConversionContext(ImportParams, MeshParams);

// 准备输出的网格描述
FMeshDescription OutputMeshDescription;

// 使用 CADKernel 工具进行曲面细分并直接输出到 MeshDescription
bool bSuccess = CADLibrary::FCADKernelTools::Tessellate(*MyCADKernelEntity, ConversionContext, OutputMeshDescription);

if (bSuccess)
{
    // OutputMeshDescription 中现在包含了从 CAD 曲面细分得到的三角形网格数据
    // 可以将其用于创建 StaticMesh 资产等后续步骤
}
```

## Demo 示例

由于此插件是底层框架，直接构建一个完整的可编译示例需要大量的 CAD 数据加载代码。以下是一个概念性的类片段，演示如何集成 `CADLibrary` 的功能。

```cpp
// MyCADProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "CADMeshDescriptionHelper.h"

class FMyCADProcessor
{
public:
    void ProcessCADModelToMesh(const FString& CADModelPath, FMeshDescription& OutMeshDescription);

private:
    // 此函数模拟加载一个 CAD 模型并返回其中间网格格式
    // 在实际应用中，这里会调用 DatasmithCADTranslator 等模块
    TSharedPtr<CADLibrary::FBodyMesh> LoadCADModelAsBodyMesh(const FString& Path);
};

// MyCADProcessor.cpp
#include "MyCADProcessor.h"

void FMyCADProcessor::ProcessCADModelToMesh(const FString& CADModelPath, FMeshDescription& OutMeshDescription)
{
    // 1. 加载 CAD 模型并转换为中间格式 (FBodyMesh)
    TSharedPtr<CADLibrary::FBodyMesh> BodyMesh = LoadCADModelAsBodyMesh(CADModelPath);
    if (!BodyMesh.IsValid()) return;

    // 2. 准备转换参数
    CADLibrary::FImportParameters ImportParams;
    CADLibrary::FMeshParameters MeshParams;
    CADLibrary::FMeshConversionContext Context(ImportParams, MeshParams);

    // 3. 调用 CADLibrary 的核心转换函数
    bool bConverted = CADLibrary::ConvertBodyMeshToMeshDescription(Context, *BodyMesh, OutMeshDescription);
    if (bConverted)
    {
        UE_LOG(LogTemp, Log, TEXT("CAD model converted to MeshDescription successfully. Vertices: %d"), OutMeshDescription.GetNumVertices());
    }
}

TSharedPtr<CADLibrary::FBodyMesh> FMyCADProcessor::LoadCADModelAsBodyMesh(const FString& Path)
{
    // 实际实现会非常复杂，涉及文件解析和几何内核转换。
    // 通常由 DatasmithCADTranslator 模块内部处理。
    return nullptr; // 占位
}
```

## 模块依赖

`DatasmithCADImporter` 插件包含多个模块，每个模块依赖于特定的第三方库。以下是用户需要注意的核心依赖：

| 模块 | 用途 |
|---|---|
| `TechSoft` | （通过 CADInterfaces）提供对多种工业 CAD 格式（如 IGES, STEP, JT, CATIA V5/V6, NX, SolidWorks 等）的读取和转换能力。这是 CAD 数据接入的关键第三方库。 |
| `OpenNurbs6` | （通过 DatasmithOpenNurbsTranslator）提供对 Rhino 3DM 文件的读取支持。 |
| `UE::CADKernel` | （内部依赖）Epic 自研的 CAD 几何内核，用于处理参数化曲面和进行高质量的曲面细分。 |

**注意**：这些依赖（特别是 `TechSoft` 和 `OpenNurbs6`）通常作为预编译的二进制库（`.lib`, `.dll`）随插件提供。在开发环境中，你需要确保这些库的二进制文件在正确的位置（通常在 `Binaries` 目录下），插件才能正确链接。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量截断为浮点数导致的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 更新了 Wire 文件翻译器逻辑，以兼容新版的 Alias 2027 软件。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将核心的 TechSoft CAD 库更新到了 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本，可能改进了缓存兼容性或性能。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复了函数类型转换警告，增强了代码在不同编译器（MSVC 和 Clang）间的可移植性。 |

### 维护评价

-   **活跃维护**：插件**仍在积极维护中**。从最近的提交记录看，更新非常频繁（最新的提交在 2026 年 5 月），内容包括**第三方库升级（TechSoft）、新软件版本支持（Alias 2027）、编译兼容性修复和性能优化**。
-   **企业级支持**：作为 Epic Games 官方的企业级插件（`Enterprise` 类别），其目标是保持与专业 CAD 软件生态系统的同步，服务于商业客户。
-   **复杂性高**：包含 21 个运行时模块，架构复杂，是大型工程代码。维护和调试需要深厚的 CAD 领域知识。
-   **推荐使用**：如果你需要将工业 CAD 数据导入虚幻引擎，并且你的目标是企业级应用、AEC 或产品设计，那么**强烈推荐使用此插件**。它是目前 UE 中处理此类数据的官方和最完整的解决方案。注意它默认关闭，需要手动启用。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例] (此插件的测试用例可能分散在 `Engine/Tests/` 目录或集成在 Datasmith 相关的测试中，未在此插件目录下发现独立的测试文件。)