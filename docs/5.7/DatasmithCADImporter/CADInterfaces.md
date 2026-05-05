# Datasmith CAD Importer

> Collection of tools to work with CAD files.

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

DatasmithCADImporter 是 Unreal Engine 企业版 Datasmith 生态系统的核心组件，专门用于将工业 CAD 文件（如 CATIA、NX、SolidWorks、JT、STEP、IGES 等格式）转换为 UE 可用的几何数据。

该插件解决的核心问题是：**工业 CAD 软件使用的精确 B-Rep（边界表示）几何体与游戏引擎使用的多边形网格之间存在根本性差异**。CAD 文件包含参数化曲面、NURBS 曲线、精确拓扑关系等信息，无法直接在实时渲染引擎中使用。本插件通过以下流程完成转换：

1. **解析**：使用 TechSoft/HOOPS SDK 读取原始 CAD 文件，提取几何和拓扑数据
2. **缝合（Sew）**：将独立的曲面片缝合成封闭的实体
3. **适配 B-Rep**：对边界表示进行优化，移除退化面、重复面等
4. **网格化（Mesh）**：将精确曲面转换为三角形网格，支持 SAG（弦高偏差）控制精度
5. **缓存**：将处理结果缓存为中间格式（.sg 场景图 + PRC 几何），避免重复计算

插件需要**手动启用**（`EnabledByDefault: false`），且依赖外部的 TechSoft/HOOPS SDK 库。

## 使用场景

- 你在做**建筑可视化**，需要导入 Revit、ArchiCAD 等 BIM 软件的模型 → 通过 Datasmith 导入，底层使用本插件处理 CAD 几何
- 你在做**汽车设计评审**，需要在 UE 中查看 CATIA/NX 的装配体 → 本插件处理 JT、STEP 等格式的精确几何转换
- 你在做**工业数字孪生**，需要将工厂设备的 CAD 模型导入 UE → 本插件支持多种工业 CAD 格式
- 你需要**控制导入精度**，在文件大小和几何精度之间取得平衡 → 通过 `FImportParameters` 的 SAG、缝合容差等参数调节

## 模块架构

本插件由 21 个模块组成，按功能可分为以下几层：

### 核心层

| 模块 | 职责 |
|---|---|
| `CADInterfaces` | 核心接口定义：文件解析器、TechSoft SDK 封装、场景图数据结构 |
| `CADLibrary` | CAD 数据处理工具库 |
| `CADTools` | CAD 几何处理工具（缝合、适配等） |
| `CADKernelSurface` | CAD 内核曲面处理 |

### 翻译器层

| 模块 | 职责 |
|---|---|
| `DatasmithCADTranslator` | 主翻译器，协调整个导入流程 |
| `DatasmithDispatcher` | 多进程/多线程调度器，用于并行处理 |
| `DatasmithOpenNurbsTranslator` | OpenNurbs（.3dm）格式翻译器 |
| `DatasmithPLMXMLTranslator` | PLMXML 格式翻译器 |
| `DatasmithWireTranslator` | Wire 格式翻译器入口 |

### Wire Interface 版本层

| 模块 | 对应 TechSoft/HOOPS 版本 |
|---|---|
| `WireInterface2020` | HOOPS 2020 |
| `WireInterface2021_3` | HOOPS 2021.3 |
| `WireInterface2022` ~ `WireInterface2026_0` | HOOPS 2022 ~ 2026.0 |

WireInterface 模块按年份版本化，每个版本对应特定的 TechSoft/HOOPS SDK 版本，确保兼容性。

### 曲面处理层

| 模块 | 职责 |
|---|---|
| `ParametricSurface` | 参数化曲面处理 |
| `ParametricSurfaceExtension` | 参数化曲面扩展功能 |

## 核心数据流

```
CAD 文件 (CATIA/NX/JT/STEP/...)
    │
    ▼
FCADFileReader          ← CADInterfaces: 入口点
    │
    ├── ICADFileParser   ← 具体格式解析器（由 WireInterface 实现）
    │       │
    │       ▼
    │   TechSoft/HOOPS SDK 读取原始几何
    │       │
    │       ▼
    │   FCADFileData     ← 场景图 + 几何数据
    │
    ├── 场景图序列化 (.sg 文件)
    ├── PRC 几何缓存
    │
    ▼
DatasmithCADTranslator  ← 协调后续处理
    │
    ├── CADTools: 缝合、适配 B-Rep
    ├── CADKernelSurface: 曲面处理
    ├── ParametricSurface: 参数化曲面
    │
    ▼
UE 几何体 (StaticMesh)
```

## 蓝图用法

本插件主要面向**编辑器导入流程**，不提供蓝图可调用的 API。CAD 文件通过 Datasmith 导入器在编辑器中使用，无需蓝图交互。

## C++ 用法

### 头文件引入

```cpp
#include "CADInterfacesModule.h"
#include "CADFileReader.h"
#include "CADData.h"
#include "CADOptions.h"
#include "TechSoftInterface.h"
#include "TechSoftUtils.h"
```

### 基本用法：检查 TechSoft SDK 可用性

```cpp
// 检查 CADInterfaces 模块是否可用（即 TechSoft SDK 是否正确加载）
ECADInterfaceAvailability Availability = ICADInterfacesModule::GetAvailability();

if (Availability == ECADInterfaceAvailability::Available)
{
    UE_LOG(LogTemp, Log, TEXT("TechSoft SDK 版本: %s"), ICADInterfacesModule::GetLibraryVersion());
}
else
{
    UE_LOG(LogWarning, Log, TEXT("TechSoft SDK 不可用，CAD 导入功能将受限"));
}
```

### 基本用法：初始化 TechSoft 内核

```cpp
#include "TechSoftInterface.h"

using namespace CADLibrary;

// 获取 TechSoft 接口单例
FTechSoftInterface& TechSoft = FTechSoftInterface::Get();

// 初始化内核（可选传入许可证路径）
bool bSuccess = TechSoft.InitializeKernel(TEXT(""));

if (bSuccess)
{
    UE_LOG(LogTemp, Log, TEXT("TechSoft 内核初始化成功，版本: %s"), TechSoft.GetVersion());
}
```

### 基本用法：读取 CAD 文件

```cpp
#include "CADFileReader.h"
#include "CADOptions.h"

using namespace CADLibrary;

// 配置导入参数
FImportParameters ImportParams;
ImportParams.SetStitchingTechnique(EStitchingTechnique::Sew);

// 创建文件描述符
FFileDescriptor FileDescriptor;
// ... 配置文件描述符

// 创建文件读取器
FCADFileReader FileReader(
    ImportParams,
    FileDescriptor,
    FPaths::EnginePluginsDir(),  // EnginePlugins 路径
    CachePath                     // 缓存路径
);

// 执行解析
ECADParsingResult Result = FileReader.ProcessFile();

if (Result == ECADParsingResult::Success)
{
    // 获取解析后的 CAD 数据
    const FCADFileData& CADData = FileReader.GetCADFileData();
    
    // 访问场景图
    // CADData 包含实例、引用、几何体等完整场景信息
}
```

### 进阶用法：使用 TechSoftUtils 处理几何体

```cpp
#include "TechSoftUtils.h"

using namespace CADLibrary;

// 从 PRC 文件读取几何体
FBodyMesh BodyMesh;
bool bSuccess = TechSoftUtils::GetBodyFromPcrFile(
    TEXT("path/to/file.prc"),
    ImportParameters,
    BodyMesh
);

if (bSuccess)
{
    // BodyMesh 包含顶点、法线、UV、面索引等网格数据
    UE_LOG(LogTemp, Log, TEXT("顶点数: %d, 面数: %d"), 
        BodyMesh.VertexCount, BodyMesh.FaceCount);
}

// 将几何体保存为 PRC 文件
void* Bodies[] = { /* ... */ };
FUniqueTechSoftModelFile ModelFile = TechSoftUtils::SaveBodiesToPrcFile(
    Bodies,
    1,                          // Body 数量
    TEXT("output.prc"),
    TEXT("{}")                  // JSON 元数据
);
```

### 进阶用法：创建 TechSoft 几何对象

```cpp
#include "TechSoftUtils.h"

using namespace CADLibrary;

// 创建拓扑面
A3DSurfBase* Surface = /* ... */;
A3DTopoFace* TopoFace = TechSoftUtils::CreateTopoFaceWithNaturalLoop(Surface);

// 创建拓扑边
A3DTopoEdge* TopoEdge = TechSoftUtils::CreateTopoEdge();

// 创建 NURBS 裁剪曲线
A3DCrvNurbs* TrimCurve = TechSoftUtils::CreateTrimNurbsCurve(
    CurveNurbsPtr,
    UMin, UMax,
    bIs2D  // 是否为 2D 曲线
);

// 创建表示项
A3DTopoShell* TopoShell = /* ... */;
A3DRiRepresentationItem* RIRep = TechSoftUtils::CreateRIBRep(TopoShell);

// 创建零件定义
TArray<A3DRiRepresentationItem*> RepItems = { RIRep };
A3DAsmPartDefinition* Part = TechSoftUtils::CreatePart(RepItems);
```

### 进阶用法：使用 TUniqueTSObj 管理 TechSoft 对象生命周期

```cpp
#include "TUniqueTechSoftObj.h"

// TUniqueTSObj 是 TechSoft 对象的 RAII 包装器
// 自动管理 A3D_INITIALIZE_DATA 和 A3DXXXXXXGet 的生命周期

// 示例：获取曲面的 NURBS 表示
TUniqueTSObj<A3DSurfNurbsData> NurbsData;
A3DStatus Status = NurbsData.FillFrom(SurfacePtr);

if (Status == A3D_SUCCESS)
{
    // NurbsData.Data 包含 NURBS 曲面数据
    // 离开作用域时自动调用 A3DSurfNurbsGet(NULL, &Data) 释放内存
}
```

## 场景图数据结构

插件使用层次化的场景图结构表示 CAD 装配体：

```cpp
// 场景图核心类层次
FArchiveCADObject           // 基类：ID、标签、元数据、变换矩阵、单位
├── FArchiveWithOverridenChildren   // 带覆盖子项的 CAD 对象
│   ├── FArchiveOverrideOccurrence  // 覆盖出现（如隐藏某个实例）
│   └── FArchiveInstance            // 实例（链接到引用）
├── FArchiveReference       // 引用（可被多个实例共享）
├── FArchiveBody            // 几何体
└── FArchiveUnloadedReference  // 未加载的外部引用
```

**关键概念**：
- **Reference（引用）**：CAD 中的零件定义，可被多个实例共享
- **Instance（实例）**：引用在装配体中的出现，有自己的变换矩阵
- **Override（覆盖）**：允许对特定实例进行属性覆盖（如隐藏第 4 个实例）

## Demo 示例

### 最小 CAD 文件读取示例

```cpp
// MyCADImporter.h
#pragma once

#include "CoreMinimal.h"
#include "CADFileReader.h"
#include "CADOptions.h"

class FMyCADImporter
{
public:
    bool ImportCADFile(const FString& FilePath, const FString& CachePath);
    
private:
    void ProcessSceneGraph(const CADLibrary::FCADFileData& FileData);
};
```

```cpp
// MyCADImporter.cpp
#include "MyCADImporter.h"
#include "CADInterfacesModule.h"
#include "TechSoftInterface.h"

bool FMyCADImporter::ImportCADFile(const FString& FilePath, const FString& CachePath)
{
    // 1. 检查 SDK 可用性
    if (ICADInterfacesModule::GetAvailability() != ECADInterfaceAvailability::Available)
    {
        UE_LOG(LogTemp, Error, TEXT("TechSoft SDK 不可用"));
        return false;
    }

    // 2. 初始化 TechSoft 内核
    CADLibrary::FTechSoftInterface::Get().InitializeKernel();

    // 3. 配置导入参数
    CADLibrary::FImportParameters ImportParams;
    // ImportParams 可配置 SAG、缝合容差等参数

    // 4. 创建文件描述符
    CADLibrary::FFileDescriptor FileDescriptor;
    FileDescriptor.SetSourcePath(FilePath);

    // 5. 创建并执行文件读取器
    CADLibrary::FCADFileReader FileReader(
        ImportParams,
        FileDescriptor,
        FPaths::EnginePluginsDir(),
        CachePath
    );

    CADLibrary::ECADParsingResult Result = FileReader.ProcessFile();
    
    if (Result != CADLibrary::ECADParsingResult::Success)
    {
        UE_LOG(LogTemp, Error, TEXT("CAD 文件解析失败"));
        return false;
    }

    // 6. 处理解析结果
    const CADLibrary::FCADFileData& FileData = FileReader.GetCADFileData();
    ProcessSceneGraph(FileData);

    return true;
}

void FMyCADImporter::ProcessSceneGraph(const CADLibrary::FCADFileData& FileData)
{
    // 访问场景图中的实例、引用、几何体等
    // FileData 包含完整的 CAD 场景层次结构
    UE_LOG(LogTemp, Log, TEXT("CAD 文件导入成功"));
}
```

## 模块依赖

### 外部依赖

| 依赖 | 用途 |
|---|---|
| `TechSoft` (HOOPS SDK) | CAD 文件解析核心库，支持 CATIA、NX、JT、STEP、IGES 等格式 |
| `OpenNurbs6` | OpenNurbs 库，用于 .3dm 文件格式支持 |

### 内部模块依赖

本插件的模块间依赖关系：

```
DatasmithCADTranslator
├── CADInterfaces (核心接口)
├── CADLibrary (工具库)
├── CADTools (几何处理)
├── CADKernelSurface (曲面处理)
├── ParametricSurface (参数化曲面)
├── ParamasmithDispatcher (调度器)
└── WireInterface* (格式翻译器)

CADInterfaces
└── TechSoft (外部 SDK)

DatasmithOpenNurbsTranslator
└── OpenNurbs6 (外部库)
```

**注意**：使用本插件时，你的模块通常不需要直接依赖这些内部模块。CAD 导入通过 Datasmith 框架自动调用。

## 维护状态

### 近期更新

```
- 5dd34d99e6dc Updated HOOPS version from 2024.6.0 to 2025.3.0
- 3fb1655bff06 Fixed crash when loading specific CATProduct file - Temporarily worked around the bug from TechSoft - Updated worker and plugin to use the newly added TechSoft binaries.
- cee46b9a1e73 Restored include files for Linux build - Restored back the header files from previous TechSoft drop since Linux binaries have not been upgraded - Modified techSoft.Build.cs to account for the change in header files - Modified the CADInterface.Build.cs to temporarily work around a problem with build on Linux. Will be investigated for next release - Updated license header to use license from previous TechSoft SDK version on Linux Note: The TechSoft SDK for Linux will be updated in next release alongside the Win64 one. All those changes will be gone.
```

**解读**：
- HOOPS SDK 版本从 2024.6.0 升级到 2025.3.0，表明持续跟进上游 SDK 更新
- 修复了特定 CATProduct 文件加载崩溃的问题，说明有实际用户在使用
- Linux 构建存在临时 workaround，Linux 平台支持可能不如 Windows 完善

### 维护评价

**活跃维护** ✅

- **创建时间**：2019 年，约 6 年历史
- **更新频率**：近期有实质性更新（SDK 升级、bug 修复）
- **维护状态**：持续维护中，跟随 TechSoft/HOOPS SDK 版本更新
- **已知限制**：
  - Linux 平台支持可能不完整（从 commit 信息推断）
  - 依赖外部 TechSoft SDK，需要有效的许可证
  - `EnabledByDefault: false`，需要手动启用
- **推荐使用**：如果你需要在 UE 中导入工业 CAD 文件，这是官方推荐的解决方案。作为企业版 Datasmith 生态的一部分，有 Epic Games 持续维护。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [Datasmith 官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/DatasmithOverview/)