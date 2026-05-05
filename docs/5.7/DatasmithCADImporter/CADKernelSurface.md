# Datasmith CAD Importer

> Collection of tools to work with CAD files.（照抄，不翻译）

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

Datasmith CAD Importer 是一个企业级插件，其核心功能是将各种工业 CAD（计算机辅助设计）格式的文件（如 CATIA, NX, SolidWorks, STEP, IGES 等）导入到 Unreal Engine 中。它不仅仅是简单的文件格式转换，更是一套完整的数据处理管线，旨在解决工业设计数据在游戏引擎中使用时面临的精度、拓扑结构和材质信息保留等核心问题。

该插件通过多个模块协同工作：
1.  **格式解析**：通过 `DatasmithCADTranslator`、`DatasmithOpenNurbsTranslator` 等模块读取不同 CAD 软件的原生文件格式。
2.  **数据转换与修复**：使用 `CADLibrary` 和 `CADKernelSurface` 等模块对导入的几何体进行拓扑修复（如缝合、法线定向）、曲面细分（Tessellation）和参数化曲面数据保留。
3.  **引擎集成**：通过 `DatasmithDispatcher` 和 `ParametricSurface` 等模块将处理后的数据转换为 UE 可用的静态网格体、材质和场景层级，并支持后续的重新细分（Retessellation）操作。

其存在意义在于为建筑、工程、施工（AEC）和产品设计可视化领域提供了一条从专业 CAD 软件到实时 3D 引擎的高保真、自动化数据通道。

## 使用场景

-   **建筑可视化 (ArchViz)**：将 Revit, ArchiCAD 等 BIM 软件或 SketchUp 的模型导入 UE，用于创建交互式建筑漫游或高质量渲染。
-   **工业设计与制造**：将汽车、飞机、家电等产品的 CATIA, NX, SolidWorks 模型导入 UE，用于设计评审、虚拟装配或营销展示。
-   **数字孪生**：导入工厂产线、机械设备的精确 CAD 模型，构建用于监控和仿真的数字孪生场景。
-   **需要高精度模型的场景**：任何需要保留原始 CAD 设计意图（如参数化曲面、精确尺寸）而非仅使用多边形网格的场景。

## 蓝图用法

该插件主要通过 Datasmith 导入流程和编辑器操作使用，其核心功能（如 CAD 文件解析、曲面细分）通常不直接暴露为蓝图节点。主要的蓝图交互点在于导入后的资产管理和重新细分选项。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Tessellate` | 对包含 CADKernel 参数化曲面数据的静态网格体进行重新细分。 | `UCADKernelParametricSurfaceData` |

### 使用示例（蓝图描述）

1.  **导入 CAD 文件**：通过 Datasmith 导入器（文件 -> 导入到关卡）选择 CAD 文件（如 .CATPart, .step）。在导入选项中，可以配置细分精度（弦公差、法线公差等）。
2.  **重新细分网格体**：在内容浏览器中，右键点击一个通过 CAD 导入的静态网格体资产，选择“Datasmith” -> “重新细分网格体”。这将调用底层的 `UCADKernelParametricSurfaceData::Tessellate` 函数，根据新的参数重新生成网格体。

## C++ 用法

C++ 用法主要涉及扩展 CAD 导入管线或直接使用 CADKernel 库进行几何处理。

### 头文件引入

```cpp
#include "CADKernelSurfaceExtension.h"
#include "CADModelToCADKernelConverterBase.h"
```

### 基本用法

以下示例展示了如何创建一个自定义的 CAD 模型转换器，它继承自 `FCADModelToCADKernelConverterBase`，并重写部分方法以实现特定的处理逻辑。

```cpp
// 来源: CADModelToCADKernelConverterBase.h 的简化用法示例
#include "CADModelToCADKernelConverterBase.h"

class FMyCustomCADConverter : public FCADModelToCADKernelConverterBase
{
public:
    FMyCustomCADConverter(const CADLibrary::FImportParameters& InImportParameters)
        : FCADModelToCADKernelConverterBase(InImportParameters)
    {
        // 可以在此设置自定义的几何和缝合容差
        SetTolerances(0.001, 0.001);
    }

    // 重写拓扑修复方法，添加自定义逻辑
    virtual bool RepairTopology() override
    {
        // 先调用基类的标准修复流程（缝合、定向等）
        bool bSuccess = FCADModelToCADKernelConverterBase::RepairTopology();
        if (bSuccess)
        {
            // 在此添加额外的自定义修复逻辑
            // 例如：移除微小特征、简化特定区域等
        }
        return bSuccess;
    }

    // 重写细分方法，可以应用自定义的网格参数
    virtual bool Tessellate(const CADLibrary::FMeshParameters& InMeshParameters, FMeshDescription& OutMeshDescription) override
    {
        // 可以修改 InMeshParameters 或使用完全不同的参数
        CADLibrary::FMeshParameters CustomMeshParams = InMeshParams;
        CustomMeshParams.SetChordTolerance(0.05); // 使用更粗糙的细分以提升性能

        return FCADModelToCADKernelConverterBase::Tessellate(CustomMeshParams, OutMeshDescription);
    }
};
```

### 进阶用法

直接使用 `CADKernelSurface` 命名空间中的函数，为已有的网格体负载（Payload）添加参数化曲面数据，以便后续支持重新细分。

```cpp
// 来源: CADKernelSurfaceExtension.h
#include "CADKernelSurfaceExtension.h"
#include "CADLibrary.h" // 假设包含 FImportParameters, FMeshParameters

// 假设已经有一个 CADKernel 归档文件路径和导入参数
FString CADKernelArchivePath = TEXT("/Path/To/Model.ugeom");
CADLibrary::FImportParameters SceneParams;
CADLibrary::FMeshParameters MeshParams;
FDatasmithTessellationOptions TessOptions;
FDatasmithMeshElementPayload MeshPayload;

// 为网格体负载添加 CADKernel 曲面数据
CADKernelSurface::AddSurfaceDataForMesh(
    *CADKernelArchivePath,
    SceneParams,
    MeshParams,
    TessOptions,
    MeshPayload
);

// 之后，可以将 MeshPayload 用于创建或更新静态网格体资产
```

## Demo 示例

一个最小化的示例，展示如何在 C++ 中实例化一个 CAD 模型转换器并执行基本的处理流程。

```cpp
// MyCADProcessor.h
#pragma once

#include "CoreMinimal.h"
#include "CADModelToCADKernelConverterBase.h"

class FMyCADProcessor
{
public:
    void ProcessCADModel(const FString& CADFilePath);
};
```

```cpp
// MyCADProcessor.cpp
#include "MyCADProcessor.h"
#include "CADLibrary.h" // 包含 FImportParameters 等

void FMyCADProcessor::ProcessCADModel(const FString& CADFilePath)
{
    // 1. 配置导入参数
    CADLibrary::FImportParameters ImportParams;
    ImportParams.SetTesselationParameters(0.1, 10.0, 10.0, CADLibrary::EStitchingTechnique::StitchingSew); // 示例参数

    // 2. 创建转换器实例
    FMyCustomCADConverter Converter(ImportParams);

    // 3. 初始化处理会话
    Converter.InitializeProcess();

    // 4. 模拟添加几何体（实际中由 CAD 解析器调用）
    // Converter.AddGeometry(...);

    // 5. 执行拓扑修复
    Converter.RepairTopology();

    // 6. 细分并获取网格描述
    FMeshDescription MeshDesc;
    CADLibrary::FMeshParameters MeshParams;
    Converter.Tessellate(MeshParams, MeshDesc);

    // 7. 保存处理后的模型（可选）
    // TSharedPtr<IDatasmithMeshElement> MeshElement = ...;
    // Converter.SaveModel(TEXT("/Game/ProcessedModels/"), MeshElement);

    // 此时 MeshDesc 包含了细分后的网格数据，可用于创建 UStaticMesh
}
```

## 模块依赖

该插件的模块依赖较为复杂，且部分依赖于特定的第三方库。以下列出其**独特**的、不常见的依赖项。

| 模块 | 用途 |
|---|---|
| `DatasmithCore` | Datasmith 核心框架，提供场景元素、导入选项等基础类型。 |
| `CADLibrary` | 本插件内部的 CAD 处理核心库，提供导入参数、网格参数、模型转换器接口等。 |
| `CADKernel` | Epic 自研的 CAD 内核库，用于参数化曲面表示、拓扑修复和细分。 |
| `TechSoft` | 第三方库，用于读取多种原生 CAD 格式（如 CATIA, NX）。 |
| `OpenNurbs6` | 第三方库，用于读写 Rhino 的 .3dm 文件格式。 |
| `Interchange` | UE 的通用数据交换框架，Datasmith 可能通过它进行部分数据传递。 |

## 维护状态

### 近期更新

-   `af690b62c96d` Renamed FMeshConversionContext to FCADMeshConversionContext
    *解读：重构，将内部类名从 `FMeshConversionContext` 重命名为 `FCADMeshConversionContext`，可能为了更清晰的命名或避免冲突。*
-   `a42d940b5e71` Added retessellation action for meshes imported through Datasmith Interchange from CAD files.
    *解读：功能更新，为通过 Datasmith Interchange 流程导入的 CAD 网格体添加了“重新细分”操作支持。*
-   `c4e44debb7f7` Moved CADKernel library code from /Engine/Source/Runtime/Datasmith/CADKernel to /Engine/Source/Runtime/Datasmith/CADKernel/Base This is in preparation of the creation of a CADKernelEngine module
    *解读：架构调整，将 CADKernel 库代码移动到新目录，为即将创建的 CADKernelEngine 模块做准备，表明该库仍在积极演进。*

### 维护评价

**活跃维护**。该插件创建于 2019 年，属于 Epic 的企业级产品线，持续获得更新。从近期提交记录看，不仅有常规的代码重构和重命名，还有明确的功能增强（如支持 Interchange 流程的重新细分）和架构演进（为 CADKernelEngine 模块做准备）。这表明该插件仍在积极开发中，以适应新的引擎功能（如 Interchange）并优化其底层架构。作为企业版功能，其稳定性和长期支持有较高保障。

**推荐使用**：对于有 CAD 数据导入需求的项目，特别是建筑、工业设计和数字孪生领域，该插件是官方推荐且功能完善的解决方案。需要注意的是，它默认未启用，需要在插件管理器中手动开启。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
-   [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests) (如果存在)