# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD导入核心 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

本插件是 Unreal Engine Datasmith 生态系统中处理**计算机辅助设计（CAD）文件**的核心引擎。它并非一个独立的可视化插件，而是一个底层的、多模块的数据转换与处理框架，其核心功能是将来自 CATIA、SolidWorks、Alias、Rhino 等专业 CAD 软件创建的**精确参数化曲面和实体模型**，转换为 Unreal Engine 可导入和渲染的网格数据。

它解决的核心问题是：工业级 CAD 模型包含高精度的 NURBS 曲面、B-Spline 等数学描述几何体，而游戏引擎（如 UE5）主要基于多边形网格进行渲染。本插件通过内置的 CADKernel 库和第三方库（如 TechSoft、OpenNurbs），实现了对这些复杂几何数据的**细分（Tessellation）、拓扑修复、格式解析和转换**，是实现高质量 CAD 数据可视化的基石。

## 使用场景

-   **工业可视化与数字孪生**：你需要将整车、飞机或复杂机械设备的 CAD 设计模型导入 UE5 中，进行装配流程模拟、虚拟评审或实时配置展示。
-   **产品展示与营销**：你从 Alias 或 SolidWorks 中获得高精度的产品外观 CAD 模型，需要将其导入 UE5 制作交互式 3D 产品配置器。
-   **建筑、工程与施工（AEC）**：你需要导入来自 Revit、ArchiCAD 或其他 BIM 软件（通过 PLMXML 格式）的建筑信息模型。

## 蓝图用法

根据提供的源码（主要来自 `CADKernelSurface` 模块），本插件的核心功能主要通过 C++ API 暴露。提供的头文件中未发现 `UFUNCTION(BlueprintCallable)` 标记的函数。蓝图层面的使用通常体现在更高层级的 Datasmith 导入流程中（例如通过 Datasmith 导入器界面），而非直接在蓝图图表中调用本插件的节点。

## C++ 用法

### 头文件引入

要使用 CADKernel 的曲面细分和转换功能，需要包含对应的头文件：

```cpp
#include “CADKernelSurface/CADKernelSurfaceExtension.h”
#include “CADLibrary/ICADModelConverter.h”
```

### 基本用法

以下示例展示了如何使用 `CADKernelSurface` 命名空间下的函数，将一个 CADKernel 归档文件（`.ugeom`）转换为 Datasmith 网格元素的有效载荷。此过程通常在导入管线中发生。

```cpp
// 示例来源：基于 Public/CADKernelSurfaceExtension.h 中的 AddSurfaceDataForMesh 函数
#include “CADKernelSurface/CADKernelSurfaceExtension.h”
#include “CADLibrary/ImportParameters.h”
#include “CADLibrary/MeshParameters.h”
#include “DatasmithContent/Public/DatasmithMeshElementPayload.h”

void ConvertCADKernelArchiveToMeshPayload(
    const TCHAR* CADKernelArchivePath,
    const CADLibrary::FImportParameters& ImportParams,
    const CADLibrary::FMeshParameters& MeshParams,
    const FDatasmithTessellationOptions& TessellationOptions,
    FDatasmithMeshElementPayload& OutPayload)
{
    // 直接调用命名空间提供的静态函数进行转换
    CADKernelSurface::AddSurfaceDataForMesh(
        CADKernelArchivePath,
        ImportParams,
        MeshParams,
        TessellationOptions,
        OutPayload
    );
    // 此时 OutPayload 中已包含可用于创建 UStaticMesh 的网格数据
}
```

### 进阶用法

更高级的用法涉及通过继承 `FCADModelToCADKernelConverterBase` 来创建自定义的 CAD 模型转换器，从而完全控制从 CAD 模型到网格的转换流程。

```cpp
// 示例来源：基于 Public/CADModelToCADKernelConverterBase.h 中的类定义
#include “CADKernelSurface/CADModelToCADKernelConverterBase.h”

class FMyCustomCADConverter : public FCADModelToCADKernelConverterBase
{
public:
    FMyCustomCADConverter(const CADLibrary::FImportParameters& InImportParameters)
        : FCADModelToCADKernelConverterBase(InImportParameters)
    {
        // 设置自定义的几何和缝合公差
        SetTolerances(0.005, 0.005);
    }

    // 可以重写虚函数来定制化处理流程
    virtual bool AddGeometry(const CADLibrary::FCADModelGeometry& Geometry) override
    {
        // 实现自定义的几何数据添加逻辑
        // ...
        return true;
    }

    // 使用自定义转换器处理一个CAD模型
    void ProcessModel()
    {
        InitializeProcess();

        // ... 此处添加几何体 (AddGeometry) ...

        // 修复模型拓扑（如缝合曲面）
        RepairTopology();

        // 细分曲面
        FMeshDescription MeshDesc;
        CADLibrary::FMeshParameters MeshParams;
        Tessellate(MeshParams, MeshDesc);

        // 保存为 .ugeom 文件或直接用于创建 MeshElement
        // SaveModel(TEXT(“/Game/Meshes”), SomeMeshElement);
    }
};
```

## Demo 示例

一个演示如何使用 `CADKernelSurface` API 进行基础转换的最小可编译示例。

**MyCADProcessor.h**
```cpp
#pragma once

#include “CoreMinimal.h”

class FDatasmithMeshElementPayload;
class UStaticMesh;

namespace CADLibrary { struct FImportParameters; struct FMeshParameters; }

class FMyCADProcessor
{
public:
    static bool ConvertArchiveToStaticMesh(
        const TCHAR* InArchivePath,
        UStaticMesh* OutStaticMesh,
        const CADLibrary::FImportParameters& InImportParams);
};
```

**MyCADProcessor.cpp**
```cpp
#include “MyCADProcessor.h”
#include “CADKernelSurface/CADKernelSurfaceExtension.h”
#include “CADLibrary/ImportParameters.h”
#include “CADLibrary/MeshParameters.h”
#include “DatasmithContent/Public/DatasmithMeshElementPayload.h”
#include “Engine/StaticMesh.h”
#include “MeshDescription.h”
#include “MeshConversion.h” // For FMeshDescriptionToDynamicMesh

bool FMyCADProcessor::ConvertArchiveToStaticMesh(
    const TCHAR* InArchivePath,
    UStaticMesh* OutStaticMesh,
    const CADLibrary::FImportParameters& InImportParams)
{
    if (!InArchivePath || !OutStaticMesh)
    {
        return false;
    }

    // 准备参数
    CADLibrary::FMeshParameters MeshParams;
    FDatasmithTessellationOptions TessOptions; // 可根据需要配置细分选项
    FDatasmithMeshElementPayload Payload;

    // 调用核心转换函数
    CADKernelSurface::AddSurfaceDataForMesh(
        InArchivePath,
        InImportParams,
        MeshParams,
        TessOptions,
        Payload
    );

    // Payload 包含网格数据，需要将其应用到 UStaticMesh
    // 注意：以下为示意，实际填充 StaticMesh 的过程更复杂，涉及 LOD、材质槽等
    if (Payload.MeshDescription.IsValid())
    {
        // 使用 MeshDescription 构建 StaticMesh
        FStaticMeshSourceModel& SourceModel = OutStaticMesh->GetSourceModel(0);
        SourceModel.MeshDescription = MakeShared<FMeshDescription>(*Payload.MeshDescription);
        OutStaticMesh->Build();
        OutStaticMesh->PostEditChange();
        return true;
    }

    return false;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | 提供对多种商业 CAD 格式（如 CATIA, NX, SolidWorks）的解析能力。这是 CADInterfaces 模块的核心依赖。 |
| `OpenNurbs6` | 提供对 Rhinoceros 3D (`.3dm`) 文件格式及 NURBS 几何体的支持。 |
| `DatasmithContent` | Datasmith 内容的核心运行时模块，提供 `FDatasmithMeshElementPayload`、`UDatasmithParametricSurfaceData` 等基础类型。 |

**注意**：`TechSoft` 和 `OpenNurbs6` 是第三方库，通常已包含在 Unreal Engine 的源代码中，但使用者通常无需直接处理它们，依赖关系已通过 Build.cs 文件配置好。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 常量到 float 的截断警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 为 Wire 转译器增加了逻辑，确保即使安装了 Alias 2027 也能工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将第三方 CAD 库 TechSoft 更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器间具有可移植性。 |

### 维护评价

-   **年龄**：插件创建于 2019 年 10 月，已超过 6 年。
-   **活跃度**：最近一次提交在 2026 年 5 月，内容以技术维护（编译器警告修复、第三方库升级）和特定兼容性（新软件版本支持）为主，表明项目仍在维护，但非功能创新阶段。
-   **状态**：作为 Unreal Engine 的官方企业（Enterprise）插件，其稳定性至关重要，更新通常以兼容性和正确性修复为主。
-   **推荐**：对于需要将专业 CAD 模型导入 UE5 进行可视化的工业和企业项目，本插件是**必需且推荐**的底层工具。但需注意，默认未启用，需要在项目中手动激活相关插件模块。由于其复杂的依赖（TechSoft, OpenNurbs）和转换逻辑，直接使用其 C++ API 需要较高的专业知识。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)