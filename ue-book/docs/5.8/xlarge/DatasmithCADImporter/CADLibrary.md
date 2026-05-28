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
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

这个插件是一个功能强大的 CAD 文件处理工具集，其主要目的是作为 Datasmith 工作流的一部分，专门用于将来自专业 CAD 软件（如 CATIA, NX, SolidWorks, STEP, IGES, Parasolid 等）的复杂工程模型导入 Unreal Engine。

它解决了 CAD 原始数据（通常包含精确的参数化曲面、拓扑结构和装配层级）到 UE 可用的三角形网格（`FMeshDescription`）的转换问题。核心功能包括：
1.  **格式解析**：通过不同的 Translator 模块读取各种 CAD 格式。
2.  **几何内核**：利用 `CADKernel`（TechSoft）或 `OpenNurbs` 等库处理精确的几何和拓扑。
3.  **网格生成**：将参数化曲面细分为三角形网格，同时处理网格拓扑（如流形修复、法线重计算）。
4.  **材质映射**：将 CAD 文件中的材质信息转换为 Datasmith 材质元素，支持 PBR 材质。
5.  **进程调度**：`DatasmithDispatcher` 可用于管理耗时的导入任务。

**重要提示**：此插件默认禁用 (`EnabledByDefault: false`)，必须在项目设置中手动启用才能使用。

## 使用场景

-   你需要将来自汽车、航空航天、工业设备等领域的复杂 CAD 装配体导入 Unreal Engine 进行可视化、仿真或交互式评审。
-   你在使用 Datasmith 导入 `.catia`, `.nx`, `.step`, `.jt`, `.parasolid` 等格式文件时遇到问题或希望有更精细的控制，可以深入此插件提供的工具。
-   你需要将 CAD 模型中的精确曲面信息（如 A 级曲面）转换为高精度的三角形网格。
-   你需要处理导入模型的材质、拓扑（非流形几何修复）以及网格优化。

## 蓝图用法

该插件主要提供 C++ 运行时 API 和 Datasmith 翻译器接口，其核心功能（如网格细分、拓扑修复）被集成在 Datasmith 的标准导入流程中，**并未暴露直接的蓝图可调用节点**。用户通过 Datasmith Importer 面板或 Reimport 功能间接使用此插件。

因此，**本插件不提供标准的蓝图节点表**。其功能主要通过 C++ API 在底层实现。

## C++ 用法

以下是基于提供的头文件（特别是 `CADLibrary` 模块）分析的核心用法。

### 头文件引入

```cpp
#include "CADLibrary/CADKernelTools.h"
#include "CADLibrary/CADMeshDescriptionHelper.h"
```

### 基本用法

以下示例展示了如何使用 `CADKernel` 工具对一个 CAD 实体进行细分，并转换为 `FMeshDescription`。
```cpp
// 假设 `CADKernelEntity` 是一个通过 CAD 导入器解析得到的实体（例如一个 Face 或 Body）
UE::CADKernel::FTopologicalShapeEntity* CADKernelEntity = ...;

// 定义导入和网格参数
CADLibrary::FImportParameters ImportParams;
CADLibrary::FMeshParameters MeshParams;
// 可在此设置公差、网格密度等参数

// 创建网格转换上下文
CADLibrary::FMeshConversionContext ConversionContext(ImportParams, MeshParams);

// 创建目标 MeshDescription
FMeshDescription MeshDescription;

// 执行细分转换
bool bSuccess = CADLibrary::FCADKernelTools::Tessellate(*CADKernelEntity, ConversionContext, MeshDescription);

if (bSuccess)
{
    // MeshDescription 现在包含从 CAD 实体细分而来的三角形网格
    // 可以将其用于创建 Static Mesh 等
}
```

### 进阶用法

处理带有材质的 CAD 模型时，需要管理材质槽的映射。以下代码演示了使用 `FMeshDescriptionDataCache` 来保存和恢复材质槽信息。
```cpp
// 假设我们有一个原始的 MeshDescription，其中已包含正确的材质槽（PolygonGroup）分配
FMeshDescription OriginalMeshDescription;
// ... 从某个源填充 OriginalMeshDescription ...

// 创建一个缓存来保存材质槽信息
CADLibrary::FMeshDescriptionDataCache MeshCache(OriginalMeshDescription);

// ... 执行一系列网格操作（例如转换为 DynamicMesh 再转回来），这些操作可能会丢失材质槽信息 ...
// 假设 `NewOrUpdatedMeshDescription` 是操作后的结果
FMeshDescription NewOrUpdatedMeshDescription;

// 使用缓存中的信息，将材质槽名称恢复到新的 MeshDescription 中
MeshCache.RestoreMaterialSlotNames(NewOrUpdatedMeshDescription);
// 此时，`NewOrUpdatedMeshDescription` 的 PolygonGroup 拥有了与原始模型一致的材质槽名称。
```

## Demo 示例

下面是一个最小的 C++ 示例，演示如何集成 CADLibrary 的功能来处理一个假设的 CAD 网格体。

### `MyCADProcessor.h`
```cpp
#pragma once
#include "CoreMinimal.h"

// 前置声明
namespace CADLibrary
{
    struct FMeshConversionContext;
    struct FImportParameters;
    struct FMeshParameters;
    class FBodyMesh;
}

class FMeshDescription;

class FMyCADProcessor
{
public:
    static bool ProcessCADBodyToUE4Mesh(CADLibrary::FBodyMesh& InCADBody, FMeshDescription& OutUE4Mesh);
};
```

### `MyCADProcessor.cpp`
```cpp
#include "MyCADProcessor.h"
#include "CADLibrary/CADMeshDescriptionHelper.h"
#include "CADLibrary/CADKernelTools.h"
#include "MeshDescription.h"

bool FMyCADProcessor::ProcessCADBodyToUE4Mesh(CADLibrary::FBodyMesh& InCADBody, FMeshDescription& OutUE4Mesh)
{
    // 1. 准备转换参数
    CADLibrary::FImportParameters ImportParams;
    CADLibrary::FMeshParameters MeshParams;
    double GeometricTolerance = 0.001; // 根据模型精度调整

    CADLibrary::FMeshConversionContext Context(ImportParams, MeshParams, GeometricTolerance);

    // 2. 执行从 CAD 体网格到 UE MeshDescription 的转换
    // 注意：此函数内部可能涉及网格修复、法线计算等操作。
    bool bConverted = CADLibrary::ConvertBodyMeshToMeshDescription(Context, InCADBody, OutUE4Mesh);

    if (!bConverted)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to convert CAD body mesh to MeshDescription."));
        return false;
    }

    // 3. （可选）启用 CAD 补丁信息，以便后续按面（Patch）设置材质或进行其他操作
    TPolygonAttributesRef<int32> PatchGroupRef = CADLibrary::EnableCADPatchGroups(OutUE4Mesh);

    // ... 可以在此基于 PatchGroupRef 为不同面分配材质 ...

    UE_LOG(LogTemp, Log, TEXT("Successfully processed CAD body. Mesh has %d vertices and %d polygons."),
           OutUE4Mesh.Vertices().Num(), OutUE4Mesh.Polygons().Num());

    return true;
}
```

## 模块依赖

你的模块需要依赖以下库才能使用 `CADLibrary` 的核心功能。这些是该插件特有的依赖项。

| 模块 | 用途 |
|---|---|
| `CADKernel` | Epic 自研的 CAD 几何内核，用于处理参数化曲面和拓扑 |
| `DatasmithCore` | Datasmith 框架核心，用于创建材质、场景元素等 |
| `MeshDescription` | UE 的网格数据结构，这是转换的目标格式 |
| `MeshConversion` | 提供网格数据格式转换工具 |

**注意**：如果你想使用 `DatasmithOpenNurbsTranslator` 或 `WireInterface` 模块，可能需要额外的第三方库（如 `OpenNurbs6`， `TechSoft`）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量截断为浮点数的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 增强了线框翻译器兼容性，支持新版本的 Alias 软件。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 更新了核心的 TechSoft CAD 内核库至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本，可能影响数据持久化。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 提升了代码的跨编译器（MSVC/Clang）可移植性，修复类型转换警告。 |

### 维护评价

**维护状态：不活跃**。

-   **年龄**：该插件已存在约 7 年，是一个成熟的工具。
-   **近期更新频率**：最近的更新集中在 2026 年 5 月，但内容主要是编译修复、第三方库更新和兼容性改进，**没有添加新功能或架构调整**。
-   **活跃度**：作为 Enterprise（企业）插件，它随引擎版本进行维护性更新，但开发重心可能不在活跃的功能迭代上。其核心依赖库（TechSoft）的更新表明它仍在维护范围内。
-   **已知问题/限制**：插件默认禁用，需要用户显式启用。依赖于特定的第三方库版本。
-   **推荐使用**：**推荐**，但仅适用于有明确 CAD 导入需求的项目。对于简单的工业模型导入，Datasmith 标准流程可能已足够。当需要深度控制 CAD 几何转换、处理复杂拓扑或使用最新版本的 CAD 内核时，此插件是必要的。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Enterprise/DatasmithCADImporterTests)