# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | 数据交换 CAD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

Datasmith CAD Importer 插件提供了一套完整的工具链，用于将工业级 CAD（计算机辅助设计）文件（如 CATIA, NX, STEP, IGES 等）高保真地导入到 Unreal Engine 中。它不仅仅是一个简单的格式转换器，而是一个深度集成的管线，负责处理复杂的 CAD 拓扑结构、曲面细分（Tessellation）以及元数据。其核心目标是将工程设计中精确的参数化几何体，转换为适用于实时渲染的多边形网格，同时尽可能保留原始模型的结构信息和元数据，服务于建筑、工程和施工（AEC）以及产品可视化领域。

该插件通过 `Datasmith` 管线工作，`DatasmithCADTranslator` 模块负责识别和处理不同的 CAD 格式，而 `CADKernelSurface` 等模块则专注于底层的几何体处理，例如拓扑修复和基于 CADKernel 库的曲面细分。

## 使用场景

- **建筑与工程可视化**：从 Revit、ArchiCAD 或 CATIA 等专业 BIM/CAD 软件导出的模型，需要在 Unreal Engine 中创建逼真的建筑漫游或施工模拟。
- **工业产品展示**：汽车、飞机、精密机械等产品的 CAD 数字模型（如来自 NX, SolidWorks）需要导入引擎进行实时交互式展示、配置器或维修培训。
- **数字孪生**：将物理世界的高精度 CAD 模型导入引擎，与实时数据结合，创建用于监控和仿真的数字孪生应用。
- **需要参数化表面支持**：当 CAD 模型包含高级参数化曲面（B-Rep）时，使用此插件进行正确的细分和转换，避免使用通用网格导入器导致的曲面失真。

## 蓝图用法

此插件主要作为 Datasmith 导入流程的底层引擎，其核心功能（如 `FCADModelToCADKernelConverterBase`）通常不直接通过蓝图节点暴露给最终用户。用户交互主要通过 Datasmith 的标准导入界面（如 `.udatasmith` 文件导入）或编辑器菜单完成。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Tessellate` | （可覆写）将存储的 CADKernel 参数化曲面数据重新细分为 `UStaticMesh` 的三角形网格。 | `UCADKernelParametricSurfaceData` |

### 使用示例（蓝图描述）

在蓝图中直接使用此插件的功能通常不常见。更常见的工作流是：
1.  使用 Datasmith 导入器导入一个包含 CAD 数据的 `.udatasmith` 文件。
2.  导入器在后台会使用 `DatasmithCADTranslator` 和 `CADKernelSurface` 等模块来处理几何体。
3.  如果导入后需要对网格进行重新细分（Retessellation），可以在编辑器中选中静态网格体，在其详细信息面板中找到 Datasmith 属性，可能会触发 `UCADKernelParametricSurfaceData::Tessellate` 的相关逻辑。

## C++ 用法

该插件的 C++ API 主要面向扩展和自定义导入流程。`CADKernelSurface` 模块提供了将 CAD 模型转换到 CADKernel 表示形式并进行细分的核心类。

### 头文件引入

```cpp
#include “CADKernelSurfaceModule.h”
#include “CADModelToCADKernelConverterBase.h”
#include “CADKernelSurfaceExtension.h”
#include “CADLibrary/ICADModelConverter.h”
#include “DatasmithContent/Public/DatasmithContentModule.h”
```

### 基本用法

以下代码展示了如何初始化一个基于 CADKernel 的模型转换器，并设置基本的细分参数。
*（来源：基于 `FCADModelToCADKernelConverterBase` 接口分析）*

```cpp
#include “CADModelToCADKernelConverterBase.h”
#include “CADLibrary/ImportParameters.h”

// 假设我们有一个导入参数对象
CADLibrary::FImportParameters ImportParams;
ImportParams.SetTesselationParameters(/* ChordTolerance */ 0.1, /* MaxEdgeLength */ 100.0, /* NormalTolerance */ 10.0, CADLibrary::EStitchingTechnique::StitchingAll);

// 创建一个具体的转换器实例（实际可能需要使用子类）
// 这里我们直接使用基类来演示接口
FCADModelToCADKernelConverterBase Converter(ImportParams);

// 初始化处理会话
Converter.InitializeProcess();

// 假设我们通过某种方式获得了 CAD 几何数据（FCADModelGeometry）
// Converter.AddGeometry(SomeGeometry);

// 修复拓扑（例如缝合）
bool bTopologyOK = Converter.RepairTopology();

// 生成网格
FMeshDescription OutMesh;
CADLibrary::FMeshParameters MeshParams; // 可能来自导入设置
bool bTessellated = Converter.Tessellate(MeshParams, OutMesh);

// 保存处理后的数据
TSharedPtr<IDatasmithMeshElement> MeshElement = MakeShared<FDatasmithMeshElement>(TEXT(“Part1”));
bool bSaved = Converter.SaveModel(TEXT(“/Game/ImportedAssets”), MeshElement);
```

### 进阶用法

结合多个模块，模拟一个简化的导入片段。
*（来源：综合 `CADKernelSurface`, `CADLibrary`, `DatasmithContent` 分析）*

```cpp
#include “CADKernelSurfaceExtension.h”
#include “DatasmithContent/Public/DatasmithMesh.h”

// 场景：需要为一个已经导入的静态网格重新生成表面数据
UStaticMesh* ExistingMesh = /* 某个已导入的网格 */;
FDatasmithRetessellationOptions RetessOptions;
RetessOptions.ChordTolerance = 0.05;
RetessOptions.MaxEdgeLength = 50.0;

// 检查该网格是否有关联的 CADKernel 参数化曲面数据
if (UCADKernelParametricSurfaceData* ParamData = ExistingMesh->GetAssetUserData<UCADKernelParametricSurfaceData>())
{
    // 使用 CADKernel 模块提供的功能重新细分
    bool bSuccess = ParamData->Tessellate(*ExistingMesh, RetessOptions);
    if (bSuccess)
    {
        // 细分成功，可能需要更新渲染状态等
        ExistingMesh->Build();
        ExistingMesh->PostEditChange();
    }
}

// 另一种场景：直接调用底层函数为网格添加表面数据（例如，自定义导入器）
FDatasmithMeshElementPayload MeshPayload;
const TCHAR* CADKernelArchivePath = TEXT(“/path/to/model.ugeom”);
CADLibrary::FImportParameters SceneParams;
CADLibrary::FMeshParameters MeshParams;
FDatasmithTessellationOptions TessOptions;

CADKernelSurface::AddSurfaceDataForMesh(
    CADKernelArchivePath,
    SceneParams,
    MeshParams,
    TessOptions,
    MeshPayload
);
// 此时 MeshPayload 中包含了可以附加到网格上的表面数据
```

## Demo 示例

以下是一个最小化的示例，展示如何创建并使用一个自定义的 `CADKernelSurface` 转换器类。

**MyCustomCADConverter.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “CADModelToCADKernelConverterBase.h”

class FMyCustomCADConverter : public FCADModelToCADKernelConverterBase
{
public:
    FMyCustomCADConverter(const CADLibrary::FImportParameters& InImportParameters)
        : FCADModelToCADKernelConverterBase(InImportParameters)
    {
    }

    // 重写添加几何体的方法，这里可以实现自定义的 CAD 数据加载逻辑
    virtual bool AddGeometry(const CADLibrary::FCADModelGeometry& Geometry) override
    {
        // 将自定义格式的几何数据解析并添加到 CADKernel 会话中
        // 此处为示意代码
        UE_LOG(LogTemp, Log, TEXT(“Adding geometry with %d faces.”), Geometry.FaceCount);
        return true; // 假设始终成功
    }

    // 可以重写其他虚函数以定制行为
    virtual void InitializeProcess() override
    {
        FCADModelToCADKernelConverterBase::InitializeProcess();
        SetTolerances(0.005, 0.005); // 使用更精确的容差
        UE_LOG(LogTemp, Log, TEXT(“Custom converter initialized.”));
    }
};
```

**MyCustomCADConverter.cpp**
```cpp
#include “MyCustomCADConverter.h”

// 使用示例
void ExampleUsage()
{
    CADLibrary::FImportParameters ImportParams;
    ImportParams.SetTesselationParameters(0.1, 100.0, 10.0, CADLibrary::EStitchingTechnique::StitchingAll);

    FMyCustomCADConverter MyConverter(ImportParams);
    MyConverter.InitializeProcess();

    // ... 加载自定义 CAD 文件并填充 CADLibrary::FCADModelGeometry ...
    // CADLibrary::FCADModelGeometry MyLoadedGeometry = LoadMyCustomCADFile(FilePath);
    // MyConverter.AddGeometry(MyLoadedGeometry);

    MyConverter.RepairTopology();

    FMeshDescription OutputMesh;
    CADLibrary::FMeshParameters MeshParams;
    MyConverter.Tessellate(MeshParams, OutputMesh);

    TSharedPtr<IDatasmithMeshElement> MeshElement = MakeShared<FDatasmithMeshElement>(TEXT(“MyCustomPart”));
    MyConverter.SaveModel(FPaths::ProjectSavedDir(), MeshElement);
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `CADLibrary` | CAD 数据模型定义、导入参数、通用 CAD 工具库。 |
| `CADInterfaces` | 定义 CAD 内核（如 TechSoft）的抽象接口。 |
| `DatasmithContent` | 提供 `UDatasmithParametricSurfaceData` 等核心内容类和接口。 |
| `CADKernel` | Epic 的 CAD 内核库，用于处理参数化几何体和拓扑。 |

*注意：此插件还依赖 `TechSoft` 和 `OpenNurbs6` 等外部 CAD 库的集成模块（如 `CADInterfaces`, `DatasmithOpenNurbsTranslator`），这些库通常需要单独获取。*

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，双精度常量截断为浮点数导致的编译警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 添加逻辑，使 Wire 转换器在安装 Alias 2027 后仍能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 Datasmith CAD 缓存的版本。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间表现一致。 |

### 维护评价

该插件创建于 **2019 年**，属于 Unreal Engine 的 **企业级 (Enterprise)** 功能，历史悠久。从近期的 Git 提交记录来看，**维护状态活跃**。更新内容包括：修复编译警告、更新外部依赖（TechSoft）、增强对第三方软件新版本（Alias 2027）的兼容性，以及改进代码的可移植性。这些都是持续维护的明确迹象。

尽管插件默认未启用 (`EnabledByDefault: false`)，且不包含内容资产 (`CanContainContent: false`)，但其作为 Datasmith 管线处理专业 CAD 格式的核心组件，对于有相关需求的用户至关重要。Epic Games 似乎仍在积极维护此插件以适配新版本的第三方 CAD 软件和引擎变化。

**结论**：推荐在需要导入工业 CAD 数据的项目中使用此插件。它仍在被积极维护，并与最新的 CAD 软件版本保持兼容。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)