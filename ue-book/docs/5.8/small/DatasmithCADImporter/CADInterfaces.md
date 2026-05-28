# Datasmith CAD Importer

> Collection of tools to work with CAD files.

| 属性 | 值 |
|---|---|
| 中文名 | CAD 文件导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `CADInterfaces` (Runtime), `CADKernelSurface` (Runtime), `CADLibrary` (Runtime), `CADTools` (Runtime), `DatasmithCADTranslator` (Runtime), `DatasmithDispatcher` (Runtime), `DatasmithOpenNurbsTranslator` (Runtime), `DatasmithPLMXMLTranslator` (Runtime), `DatasmithWireTranslator` (Runtime), `ParametricSurface` (Runtime), `ParametricSurfaceExtension` (Runtime), `WireInterface2020` (Runtime), `WireInterface2021_3` (Runtime), `WireInterface2022` (Runtime), `WireInterface2022_1` (Runtime), `WireInterface2022_2` (Runtime), `WireInterface2023_0` (Runtime), `WireInterface2023_1` (Runtime), `WireInterface2024_1` (Runtime), `WireInterface2025_0` (Runtime), `WireInterface2026_0` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2019-10-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

DatasmithCADImporter 是 Unreal Engine 的 CAD 文件导入管线核心，负责将工业 CAD 格式（STEP、CATIA V5/V6、SolidWorks、JT、IGES、Parasolid、Inventor、Rhino/3DM、PLMXML 等）解析为 UE 可用的网格数据和场景图结构。

该插件的核心价值在于：

- **B-Rep 解析**：通过 TechSoft（HOOPS Exchange）SDK 读取 CAD 文件的精确几何表示（B-Rep），包括拓扑（Shell/Face/Loop/Edge）和曲面（NURBS、平面、圆柱、旋转面等）
- **曲面细分**：支持两种细分路径——TechSoft 原生细分和 UE CADKernel 细分，可根据需要选择
- **场景图保留**：保留 CAD 装配体的层级结构（Instance/Reference/OverrideOccurrence），支持外部引用和实例化
- **缓存系统**：通过文件哈希实现导入缓存，避免重复解析相同 CAD 文件
- **材质/颜色提取**：从 CAD 图形属性中提取材质和颜色信息，映射到 UE 材质系统

此插件**默认禁用**（`EnabledByDefault: false`），需要在插件管理器中手动启用，或者通过 Datasmith 导入流程自动加载。

## 使用场景

- 你在做建筑可视化（ArchViz）→ 用 DatasmithCADImporter 导入 Revit/ArchiCAD 的 CAD 模型
- 你在做汽车/工业设计评审 → 导入 CATIA/SolidWorks/JT 的装配体到 Unreal 进行实时渲染
- 你需要在 UE 中精确呈现 CAD 几何（而非三角面片） → 使用 CADKernel 细分路径获得更好的曲面质量
- 你有大量 CAD 文件需要反复导入 → 利用缓存机制加速后续导入
- 你需要导入 Rhino 的 3DM 文件 → 使用 `DatasmithOpenNurbsTranslator` 模块
- 你需要导入 Alias/Wire 文件进行汽车 A 面设计评审 → 使用 `DatasmithWireTranslator` 和对应的 `WireInterface` 模块

## 蓝图用法

该插件主要为**底层导入管线**，不直接暴露蓝图节点。其功能通过 Datasmith 导入器统一调用。对开发者而言，主要通过 C++ API 交互。

### 模块可用性查询

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAvailability()` | 查询 CAD 接口模块是否可用 | `ICADInterfacesModule` |
| `GetLibraryVersion()` | 获取 TechSoft 库版本字符串 | `ICADInterfacesModule` |

### 使用示例（蓝图描述）

在蓝图中，CAD 文件通常通过 **Datasmith 导入工作流** 间接使用：
1. 在编辑器中选择 **File → Import → Datasmith Scene**
2. 选择支持的 CAD 文件格式（.step, .catpart, .sldprt, .jt, .3dm 等）
3. 导入器自动调用对应的 Translator 模块处理文件

如需在运行时导入，需使用 DatasmithRuntime 插件的蓝图接口。

## C++ 用法

### 头文件引入

```cpp
#include "CADInterfacesModule.h"        // 模块可用性查询
#include "TechSoftInterface.h"          // TechSoft SDK 封装
#include "CADFileReader.h"              // CAD 文件读取
#include "CADFileData.h"                // CAD 文件数据结构
#include "CADSceneGraph.h"              // 场景图结构
#include "CADFileParser.h"              // 文件解析器接口
```

### 基本用法：查询模块可用性

在使用 CAD 导入功能前，先检查 TechSoft SDK 是否可用。

```cpp
// 来源: Source/CADInterfaces/Public/CADInterfacesModule.h
#include "CADInterfacesModule.h"

// 检查 CAD 接口是否可用
ECADInterfaceAvailability Availability = ICADInterfacesModule::GetAvailability();

if (Availability == ECADInterfaceAvailability::Available)
{
    // 获取 TechSoft 库版本
    const TCHAR* Version = ICADInterfacesModule::GetLibraryVersion();
    UE_LOG(LogTemp, Log, TEXT("TechSoft version: %s"), Version);
}
else
{
    UE_LOG(LogTemp, Warning, TEXT("CAD interface unavailable - TechSoft SDK not linked"));
}
```

### 基本用法：初始化 TechSoft 内核

```cpp
// 来源: Source/CADInterfaces/Public/TechSoftInterface.h
#include "TechSoftInterface.h"

using namespace CADLibrary;

// 获取 TechSoft 接口单例
FTechSoftInterface& TechSoft = FTechSoftInterface::Get();

// 初始化内核（通常在模块启动时自动完成）
bool bInitialized = TechSoft.InitializeKernel();

if (bInitialized)
{
    const TCHAR* Version = TechSoft.GetVersion();
    UE_LOG(LogTemp, Log, TEXT("TechSoft kernel initialized, version: %s"), Version);
}
```

### 基本用法：读取 CAD 文件

```cpp
// 来源: Source/CADInterfaces/Public/CADFileReader.h
#include "CADFileReader.h"
#include "CADFileData.h"

using namespace CADLibrary;

// 配置导入参数
FImportParameters ImportParams;
// ... 设置导入参数（网格精度、缝合容差等）

// 创建文件描述符
FFileDescriptor FileDescription(TEXT("/path/to/model.step"));

// 创建 CAD 文件读取器
FCADFileReader Reader(ImportParams, FileDescription, EnginePluginsPath, CachePath);

// 执行导入
ECADParsingResult Result = Reader.ProcessFile();

if (Result == ECADParsingResult::Success)
{
    // 获取解析后的 CAD 数据
    const FCADFileData& CADData = Reader.GetCADFileData();
    
    // 访问场景图
    const FArchiveSceneGraph& SceneGraph = CADData.GetSceneGraphArchive();
    
    // 访问网格数据
    const TArray<FBodyMesh>& BodyMeshes = CADData.GetBodyMeshes();
    
    UE_LOG(LogTemp, Log, TEXT("Imported %d bodies, %d references, %d instances"),
        SceneGraph.Bodies.Num(),
        SceneGraph.References.Num(),
        SceneGraph.Instances.Num());
}
```

### 基本用法：遍历场景图

```cpp
// 来源: Source/CADInterfaces/Public/CADSceneGraph.h
#include "CADSceneGraph.h"

// 假设已通过 FCADFileReader 获取了 CADFileData
const FArchiveSceneGraph& SceneGraph = CADFileData.GetSceneGraphArchive();

// 遍历所有 Body（实际几何体）
for (const FArchiveBody& Body : SceneGraph.Bodies)
{
    UE_LOG(LogTemp, Log, TEXT("Body %u: Label=%s, MeshActorUId=%u"),
        Body.Id, *Body.Label, Body.MeshActorUId);
}

// 遍历实例化引用（装配结构）
for (const FArchiveInstance& Instance : SceneGraph.Instances)
{
    UE_LOG(LogTemp, Log, TEXT("Instance %u -> Reference %u, External=%s"),
        Instance.Id, Instance.ReferenceNodeId,
        Instance.bIsExternalReference ? TEXT("Yes") : TEXT("No"));
}

// 遍历外部引用文件
for (const FFileDescriptor& ExtRef : SceneGraph.ExternalReferenceFiles)
{
    UE_LOG(LogTemp, Log, TEXT("External ref: %s"), *ExtRef.GetSourcePath());
}
```

### 进阶用法：使用 TechSoft SDK 原始接口

当需要直接操作 TechSoft 数据结构时（需在 `#ifdef USE_TECHSOFT_SDK` 保护下）。

```cpp
// 来源: Source/CADInterfaces/Public/TechSoftInterface.h
#include "TechSoftInterface.h"

#ifdef USE_TECHSOFT_SDK
using namespace CADLibrary;

// 加载模型文件
A3DImport ImportParams;
A3DStatus Status;
FUniqueTechSoftModelFile ModelFile = TechSoftInterface::LoadModelFileFromFile(ImportParams, Status);

if (Status == A3D_SUCCESS && ModelFile.IsValid())
{
    // 获取模型单位
    double Unit = TechSoftInterface::GetModelFileUnit(ModelFile.Get());
    UE_LOG(LogTemp, Log, TEXT("Model unit: %f"), Unit);

    // 获取曲面 NURBS 表示
    A3DSurfNurbsData NurbsData;
    A3DStatus SurfStatus = TechSoftInterface::GetSurfaceAsNurbs(
        SomeSurfacePtr, &NurbsData, 0.01, true);

    // 在 UV 参数处求值曲面
    A3DVector2dData UVParam;
    UVParam.m_dX = 0.5;
    UVParam.m_dY = 0.5;
    A3DVector3dData PointAndDerivatives[4]; // (Derivatives+1)^2 = 4
    TechSoftInterface::Evaluate(SomeSurfacePtr, UVParam, 1, PointAndDerivatives);

    // 缝合模型（修复拓扑间隙）
    TechSoftInterface::SewModel(ModelFile.Get(), 0.1, nullptr);

    // ModelFile 超出作用域时自动释放（FUniqueTechSoftModelFile 的 RAII 行为）
}
#endif
```

### 进阶用法：使用 CADKernel 曲面细分路径

```cpp
// 来源: Source/CADInterfaces/Private/TechSoftFileParserCADKernelTessellator.h
// 该路径使用 UE 内置 CADKernel 进行曲面细分，而非 TechSoft 的细分器

// 当使用 CADKernel 细分时，SewModel 在 GenerateBodyMeshes 中执行，
// 而不是在 TechSoftFileParser 的标准流程中。
// 这通常能产生更高质量的三角面片。

// 具体使用方式由导入参数中的 Mesher 设置控制：
// EMesher::TechSoft - 使用 TechSoft 原生细分
// EMesher::CADKernel - 使用 UE CADKernel 细分
```

### 进阶用法：使用智能指针管理 TechSoft 对象

```cpp
// 来源: Source/CADInterfaces/Public/TUniqueTechSoftObj.h
#include "TUniqueTechSoftObj.h"

using namespace CADLibrary;

// TUniqueTSObj 是 TechSoft 数据结构的 RAII 包装
// 它自动处理 A3D_INITIALIZE_DATA / A3DGet / A3DGet(NULL) 的生命周期

// 用法一：创建空的已初始化结构
TUniqueTSObj<A3DSurfNurbsData> NurbsSurface;
// NurbsSurface 内部已通过 A3D_INITIALIZE_DATA 初始化

// 用法二：从 TechSoft 实体指针填充数据
TUniqueTSObj<A3DTopoFaceData> FaceData(A3DTopoFacePtr);
if (FaceData.IsValid())
{
    // 通过解引用访问数据
    const A3DTopoFaceData& Data = *FaceData;
    // 或通过指针访问
    const A3DTopoFaceData* DataPtr = FaceData.GetPtr();
}

// 从索引填充（如材质索引）
TUniqueTSObjFromIndex<A3DGraphMaterialData> MaterialData(MaterialIndex);

// 超出作用域时自动调用 TechSoft 的清理方法
```

## Demo 示例

以下是一个完整的、可编译的最小示例，展示如何使用 CADInterfaces 模块读取 CAD 文件并提取场景信息。

### CADImporterExample.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FCADImporterExample
{
public:
    /** 导入 CAD 文件并打印场景信息 */
    static bool ImportCADFile(const FString& FilePath, const FString& CachePath = TEXT(""));
    
    /** 检查 CAD 接口是否可用 */
    static bool IsCADAvailable();
    
    /** 获取 TechSoft 版本 */
    static FString GetVersion();
};
```

### CADImporterExample.cpp

```cpp
#include "CADImporterExample.h"
#include "CADInterfacesModule.h"
#include "TechSoftInterface.h"
#include "CADFileReader.h"
#include "CADFileData.h"
#include "CADSceneGraph.h"

using namespace CADLibrary;

bool FCADImporterExample::IsCADAvailable()
{
    return ICADInterfacesModule::GetAvailability() == ECADInterfaceAvailability::Available;
}

FString FCADImporterExample::GetVersion()
{
    if (!IsCADAvailable())
    {
        return TEXT("Unavailable");
    }
    const TCHAR* Version = ICADInterfacesModule::GetLibraryVersion();
    return FString(Version ? Version : TEXT("Unknown"));
}

bool FCADImporterExample::ImportCADFile(const FString& FilePath, const FString& CachePath)
{
    if (!IsCADAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("CAD interface is not available. Ensure TechSoft SDK is linked."));
        return false;
    }

    UE_LOG(LogTemp, Log, TEXT("TechSoft version: %s"), *GetVersion());

    // 配置导入参数
    FImportParameters ImportParams;

    // 创建文件描述符
    FFileDescriptor FileDescription(FilePath);

    // 获取引擎插件路径（用于 DWG/DGN 导入的 KernelIO）
    FString EnginePluginsPath = FPaths::EnginePluginsDir();

    // 创建 CAD 文件读取器
    FCADFileReader Reader(ImportParams, FileDescription, EnginePluginsPath, CachePath);

    // 执行导入
    ECADParsingResult Result = Reader.ProcessFile();

    if (Result != ECADParsingResult::Success)
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to import CAD file: %s"), *FilePath);
        return false;
    }

    // 获取解析结果
    const FCADFileData& CADData = Reader.GetCADFileData();
    const FArchiveSceneGraph& SceneGraph = CADData.GetSceneGraphArchive();

    // 打印导入统计
    UE_LOG(LogTemp, Log, TEXT("=== CAD Import Summary ==="));
    UE_LOG(LogTemp, Log, TEXT("File: %s"), *FilePath);
    UE_LOG(LogTemp, Log, TEXT("Bodies: %d"), SceneGraph.Bodies.Num());
    UE_LOG(LogTemp, Log, TEXT("References: %d"), SceneGraph.References.Num());
    UE_LOG(LogTemp, Log, TEXT("Instances: %d"), SceneGraph.Instances.Num());
    UE_LOG(LogTemp, Log, TEXT("External References: %d"), SceneGraph.ExternalReferenceFiles.Num());
    UE_LOG(LogTemp, Log, TEXT("Colors: %d"), SceneGraph.ColorHIdToColor.Num());
    UE_LOG(LogTemp, Log, TEXT("Materials: %d"), SceneGraph.MaterialHIdToMaterial.Num());

    // 遍历所有 Body 并打印网格统计
    const TArray<FBodyMesh>& BodyMeshes = CADData.GetBodyMeshes();
    for (const FBodyMesh& BodyMesh : BodyMeshes)
    {
        UE_LOG(LogTemp, Log, TEXT("  Body Mesh UId=%u, FromCAD=%s"),
            BodyMesh.MeshActorUId,
            BodyMesh.bIsFromCad ? TEXT("Yes") : TEXT("No"));
    }

    // 打印性能记录
    const FImportRecord& Record = CADData.GetRecord();
    UE_LOG(LogTemp, Log, TEXT("Import time: %.2f ms"), Record.ImportTime);
    UE_LOG(LogTemp, Log, TEXT("Mesh time: %.2f ms"), Record.MeshTime);
    UE_LOG(LogTemp, Log, TEXT("Total load time: %.2f ms"), Record.LoadProcessTime);

    return true;
}
```

### Build.cs 依赖

```csharp
// 你的模块 Build.cs 中需要添加：
PublicDependencyModuleNames.AddRange(new string[]
{
    "CADInterfaces"
});
```

注意：实际编译还需要 TechSoft SDK 的第三方库支持。该 SDK 以预编译形式随引擎分发，需确保 `USE_TECHSOFT_SDK` 宏已定义且库文件已正确链接。

## 模块依赖

### 插件内模块依赖关系

```
DatasmithCADTranslator ──→ CADLibrary ──→ CADInterfaces
                                        ──→ CADTools
DatasmithOpenNurbsTranslator ──→ CADLibrary
DatasmithPLMXMLTranslator ──→ CADLibrary
DatasmithWireTranslator ──→ CADLibrary
                             ──→ WireInterface20xx
CADLibrary ──→ CADInterfaces
           ──→ CADKernelSurface
           ──→ ParametricSurface
```

### 外部依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | HOOPS Exchange SDK，用于解析 STEP/CATIA/SolidWorks/JT/IGES 等 CAD 格式 |
| `OpenNurbs6` | OpenNurbs 库，用于解析 Rhino 的 3DM 文件格式 |
| `DatasmithCore` | Datasmith 核心框架（DatasmithTranslator 模块使用） |
| `MeshConversion` | 网格数据转换（细分路径使用） |
| `CADKernel` | UE 内置 CAD 曲面细分引擎（CADKernelSurface 模块使用） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | Wire 转换器兼容 Alias 2027 的逻辑适配 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft SDK 到 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 CAD 缓存版本号（可能涉及缓存格式变更） |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复 MSVC 和 Clang 之间的类型转换警告可移植性 |

### 维护评价

**活跃维护** ⚡

该插件仍在被积极维护和更新：

- **创建于 2019 年**，至今约 7 年历史，属于 Enterprise（企业级）插件
- **最近 5 次提交均在 2026 年 5 月**，包括 SDK 版本升级（TechSoft 2026.3）、编译器兼容性修复、以及新版本 Alias 的支持
- TechSoft SDK 的版本持续更新（从 `WireInterface` 模块覆盖 2020-2026 全版本可看出对每个年度 Alias 版本都有适配）
- 缓存版本号也在更新，说明内部数据格式仍在演进
- 作为 Datasmith 导入管线的核心组件，与 UE 的企业级内容创作工作流深度绑定，预计会持续维护

**推荐使用**。如果你的项目需要从工业 CAD 格式导入精确几何模型，这是官方唯一的 CAD 导入方案。注意需要手动启用（`EnabledByDefault: false`），且需要 TechSoft 第三方 SDK 支持。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Tests)（如存在）