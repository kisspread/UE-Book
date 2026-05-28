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

DatasmithCADImporter 是 Unreal Engine 企业版中处理 CAD 数据的核心工具链。它解决的根本问题是：如何将来自各种工业 CAD 软件（如 CATIA、SolidWorks、NX、JT、STEP、IGES 等）的高精度、参数化 CAD 模型，高效、准确地转换为 Unreal Engine 可用的网格（Mesh）数据，同时尽可能保留原始的材质、颜色、结构层次（装配树）和几何拓扑信息。

这个插件存在是因为直接导入 CAD 文件（尤其是 B-Rep 数据）非常复杂，且 UE 原生支持有限。它通过集成 **TechSoft** 等专业 CAD 内核库，提供了从解析、几何修复（如缝合）、曲面细分（Tessellation）到最终生成 UE 可用资产（如 Static Mesh）的完整流水线。

## 使用场景

- **建筑与工程 (AEC)**: 将 Revit、ArchiCAD 或其他 BIM 软件导出的 CAD 模型（如 IFC、PLMXML 格式）导入 UE，用于建筑可视化、施工模拟或数字孪生。
- **制造业与产品设计**: 将 SolidWorks、CATIA、NX、Creo 等机械 CAD 软件生成的精密零件和装配体（STEP、JT 格式）导入 UE，用于产品展示、虚拟装配、维修手册生成或数字样机评审。
- **工业仿真与培训**: 在 UE 中构建复杂的工业设备模型（可能由多个 CAD 软件生成），用于操作培训、安全流程模拟或实时仿真。
- **跨软件协作**: 当团队使用不同的 CAD 工具时，UE 可以作为统一的可视化和交互平台，此插件负责处理来自不同源头的 CAD 数据。

## 蓝图用法

本插件的核心功能主要通过 Datasmith 工作流（如 Datasmith Import 工具栏按钮）或 C++ API 进行调用。从提供的源码分析，其公共 API 主要为 C++ 接口，**未发现直接暴露给蓝图的 `UFUNCTION(BlueprintCallable)` 或 `UPROPERTY(BlueprintReadWrite)`**。因此，蓝图中主要通过 Datasmith 的标准导入流程间接使用此插件。

### 使用示例（蓝图描述）
在编辑器中，用户通常通过“Datasmith”工具栏或内容浏览器的“导入”功能，选择一个 CAD 文件（如 .step, .catpart, .sldprt）。插件在后台自动执行解析、转换和网格生成。整个过程对蓝图是透明的，用户最终获得的是导入后的 Actor 和 Static Mesh 资产。

## C++ 用法

本插件为 C++ 模块，主要提供底层的文件解析和数据转换接口。典型的使用流程是创建一个文件读取器，处理 CAD 文件，并获取生成的网格数据。

### 头文件引入

```cpp
#include “CADInterfaces/CADFileReader.h”
#include “CADInterfaces/TechSoftInterface.h”
#include “CADLibrary/CADFileData.h”
```

### 基本用法

从 `CADFileReader.h` 和相关头文件推断，基本流程是初始化 TechSoft 内核，然后使用 `FCADFileReader` 读取文件。

```cpp
// 基于 Public/CADFileReader.h 和 Public/TechSoftInterface.h
// 初始化 TechSoft 内核（通常由插件内部管理，但有时需要手动检查或初始化）
CADLibrary::FTechSoftInterface& TechSoft = CADLibrary::FTechSoftInterface::Get();
if (!TechSoft.InitializeKernel())
{
    // 错误处理：TechSoft 内核初始化失败，可能缺少许可或库文件
    return;
}

// 准备导入参数和文件描述符
CADLibrary::FImportParameters ImportParams;
CADLibrary::FFileDescriptor FileDesc(TEXT(“C:/Models/Engine.step”));

// 创建文件读取器，传入参数、文件描述、引擎插件路径和缓存路径
CADLibrary::FCADFileReader FileReader(ImportParams, FileDesc, FPaths::EnginePluginsDir(), CachePath);

// 执行文件解析和处理
CADLibrary::ECADParsingResult Result = FileReader.ProcessFile();
if (Result != CADLibrary::ECADParsingResult::Succeed)
{
    // 处理错误
    return;
}

// 获取处理结果，其中包含了场景图和网格数据
const CADLibrary::FCADFileData& CADData = FileReader.GetCADFileData();
// CADData 内部持有 FArchiveSceneGraph (结构/材质信息) 和 TArray<FBodyMesh> (网格数据)
```

### 进阶用法

更复杂的用法涉及直接管理 TechSoft 模型文件（`FUniqueTechSoftModelFile`）并进行操作，例如从 PRC 文件加载或缝合（Sew）模型。这通常发生在翻译器模块内部。

```cpp
// 基于 Public/TechSoftInterface.h 和 Public/TechSoftUtils.h
#ifdef USE_TECHSOFT_SDK
using namespace CADLibrary::TechSoftInterface;

// 从 PRC 文件加载模型
A3DStatus Status;
FUniqueTechSoftModelFile ModelFile = LoadModelFileFromPrcFile(PrcFileName, nullptr);
if (!ModelFile.IsValid())
{
    // 加载失败处理
    return;
}

// 对加载的模型进行缝合（Sew），修复小的几何间隙
double ToleranceCM = 0.01; // 容差1厘米
A3DSewOptionsData SewOptions;
A3D_INITIALIZE_DATA(A3DSewOptionsData, SewOptions);
A3DStatus SewStatus = SewModel(ModelFile.Get(), ToleranceCM, &SewOptions);

// 将模型文件导出为 PRC 文件
const TCHAR* OutputFile = TEXT(“Processed.prc”);
A3DRWParamsExportPrcData ExportParams;
A3D_INITIALIZE_DATA(A3DRWParamsExportPrcData, ExportParams);
ExportModelFileToPrcFile(ModelFile.Get(), &ExportParams, OutputFile, nullptr);

// ModelFile 将在作用域结束时自动调用 DeleteModelFile 进行清理
#endif
```

## Demo 示例

一个最小的示例，展示如何使用 `FCADFileReader` 导入一个 CAD 文件并遍历其结果。请注意，实际生成 UE Static Mesh Actor 需要更复杂的资产工厂代码，此示例仅展示数据获取。

**MyCADImporter.h**
```cpp
#pragma once

#include “CoreMinimal.h”
#include “CADInterfaces/CADFileReader.h”

class FMyCADImporter
{
public:
    bool ImportCADFile(const FString& FilePath);

private:
    void ProcessCADData(const CADLibrary::FCADFileData& CADData);
};
```

**MyCADImporter.cpp**
```cpp
#include “MyCADImporter.h”
#include “CADInterfaces/CADFileReader.h”
#include “CADLibrary/CADFileData.h”

bool FMyCADImporter::ImportCADFile(const FString& FilePath)
{
    // 准备参数
    CADLibrary::FImportParameters ImportParams;
    CADLibrary::FFileDescriptor FileDesc(FilePath);

    // 使用临时缓存目录
    FString CachePath = FPaths::ProjectSavedDir() / TEXT(“TempCADCaches”);

    // 创建读取器并处理
    CADLibrary::FCADFileReader Reader(ImportParams, FileDesc, FPaths::EnginePluginsDir(), CachePath);
    CADLibrary::ECADParsingResult Result = Reader.ProcessFile();

    if (Result == CADLibrary::ECADParsingResult::Succeed)
    {
        const CADLibrary::FCADFileData& CADData = Reader.GetCADFileData();
        ProcessCADData(CADData);
        return true;
    }
    UE_LOG(LogTemp, Error, TEXT(“Failed to import CAD file: %s”), *FilePath);
    return false;
}

void FMyCADImporter::ProcessCADData(const CADLibrary::FCADFileData& CADData)
{
    // 获取场景图，里面包含了零件的层次结构、材质和颜色信息
    const CADLibrary::FArchiveSceneGraph& SceneGraph = CADData.GetSceneGraphArchive();
    UE_LOG(LogTemp, Log, TEXT(“Imported scene graph with %d references, %d instances, and %d bodies.”),
        SceneGraph.References.Num(),
        SceneGraph.Instances.Num(),
        SceneGraph.Bodies.Num());

    // 获取网格数据数组，每个元素对应一个可渲染的物体（Body）
    const TArray<CADLibrary::FBodyMesh>& BodyMeshes = CADData.GetBodyMeshes();
    for (const CADLibrary::FBodyMesh& Body : BodyMeshes)
    {
        UE_LOG(LogTemp, Log, TEXT(“Body %u has %d vertices and %d triangles.”),
            Body.MeshActorUId,
            Body.Vertices.Num(),
            Body.Triangles.Num());
        // 这里，Body.Vertices 和 Body.Triangles 包含了创建 Static Mesh 所需的原始数据
    }
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | 核心第三方 CAD 内核库，用于解析多种 CAD 文件格式和进行高级几何操作（如缝合）。 |
| `CADKernel` | UE 内部的 CAD 几何内核，用于参数化曲面处理、细分和网格生成，常作为 TechSoft 的补充或替代细分器。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下 double 常量被截断为 float 的警告。 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 为 Wire 翻译器添加逻辑，确保即使安装了 Alias 2027 也能正常工作。 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 将 TechSoft 库更新至 2026.3 版本。 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新了 DatasmithCAD 缓存的版本格式。 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 编译器之间具有可移植性。 |

### 维护评价

- **创建时间**：2019 年 10 月，至今约 7 年。
- **活跃度**：**非常活跃**。最近一次更新在 2026 年 5 月（文档编写时间），内容包括依赖库升级（TechSoft）、兼容性修复（Alias 2027）和编译警告修复。
- **状态**：这是 UE **企业版**的核心组件之一，为多个行业解决方案提供基础支持，因此处于**持续维护和更新**状态。
- **推荐度**：**强烈推荐**。对于需要处理专业 CAD 数据的 UE 项目，这是必不可少的插件。它功能强大且维护良好，但需注意其属于企业功能，可能需要相应的订阅或许可。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests) (注意：大型插件的测试可能位于 Engine/Tests/ 或独立的测试项目中)