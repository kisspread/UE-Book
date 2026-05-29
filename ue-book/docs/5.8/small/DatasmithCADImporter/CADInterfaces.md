# Datasmith CAD Importer

> Collection of tools to work with CAD files.

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

DatasmithCADImporter 是 UE5 的核心 CAD 文件导入管线，负责将工业级 CAD 格式（STEP、JT、CATIA、SolidWorks、Rhino、IGES 等 40+ 种格式）转换为 UE 可用的网格和场景数据。

该插件解决的核心问题是：**工业 CAD 文件使用精确的 B-Rep（边界表示）几何体，而游戏引擎需要三角面片网格**。插件内部通过 TechSoft SDK 读取 CAD 原始数据，经过 B-Rep 适配、缝合（Sew）、曲面细分（Tessellation）等步骤，最终生成引擎可用的 StaticMesh。

插件架构分层清晰：
- **CADInterfaces**：底层 TechSoft SDK 封装，处理 CAD 文件读写和几何操作
- **CADLibrary**：场景图解析、缓存管理、导入参数控制
- **DatasmithCADTranslator**：Datasmith 与 CAD 数据之间的翻译层
- **各 WireInterface 模块**：对应不同版本的 CAD 内核（2020-2026），确保向前兼容
- **ParametricSurface**：将 CAD 参数化曲面转换为 NURBS 或网格

该插件默认禁用（`EnabledByDefault=false`），因为依赖商业授权的 TechSoft SDK，仅在安装了 Datasmith 相关组件后才可用。

## 使用场景

- 你在做建筑可视化（ArchViz）→ 需要从 Revit、ArchiCAD 等导入 CAD 模型
- 你在做工业产品可视化 → 需要从 CATIA、SolidWorks、NX 等导入精确几何体
- 你在做数字孪生项目 → 需要从 PLM 系统（如 Teamcenter 的 PLMXML）导入装配体
- 你需要导入 Rhino（.3dm）等 NURBS 建模软件的文件
- 你需要导入 Alias/Wire 格式的汽车 A 级曲面数据

## 蓝图用法

该插件是纯数据导入管线，不暴露任何蓝图可调用的函数（`UFUNCTION(BlueprintCallable)`）。

CAD 文件的导入通过 Datasmith Importer 的标准流程进行：

### 导入流程

1. 在编辑器中通过 **File → Import** 选择 CAD 文件
2. 或使用 **Datasmith Import** 按钮（需要 Datasmith 插件）
3. 插件自动根据文件扩展名选择对应的 Translator 模块
4. 解析、缝合、细分、生成 StaticMesh 和场景层级

### 导入参数

导入行为通过 `FImportParameters` 控制，包括：
- 缝合容差（Stitching Tolerance）
- 是否移除重复三角面
- 是否强制缝合
- 曲面细分质量（SAG - Surface Approximation Goal）
- 是否使用 JT 文件内嵌细分数据

## C++ 用法

该插件主要是内部使用，对外暴露的 C++ API 有限。以下是关键接口：

### 头文件引入

```cpp
#include "CADFileReader.h"
#include "CADFileData.h"
#include "CADInterfacesModule.h"
#include "TechSoftInterface.h"
```

### 基本用法：读取 CAD 文件

```cpp
#include "CADFileReader.h"

// 创建导入参数和文件描述符
FImportParameters ImportParams;
FFileDescriptor FileDescriptor(TEXT("/path/to/model.step"), TEXT(""), TEXT(""));

// 创建文件读取器
CADLibrary::FCADFileReader FileReader(
    ImportParams,
    FileDescriptor,
    EnginePluginsPath,  // Engine 插件路径，DWG/DGN 导入需要
    CachePath           // 缓存路径
);

// 执行导入
CADLibrary::ECADParsingResult Result = FileReader.ProcessFile();

if (Result == CADLibrary::ECADParsingResult::Success)
{
    // 获取 CAD 文件数据
    const CADLibrary::FCADFileData& CADFileData = FileReader.GetCADFileData();
    
    // 获取场景图
    const CADLibrary::FArchiveSceneGraph& SceneGraph = CADFileData.GetSceneGraphArchive();
    
    // 获取网格数据
    const TArray<CADLibrary::FBodyMesh>& BodyMeshes = CADFileData.GetBodyMeshes();
    
    // 遍历场景图中的实例
    for (const CADLibrary::FArchiveInstance& Instance : SceneGraph.Instances)
    {
        // 处理每个实例...
    }
}
```

### 检查 TechSoft SDK 可用性

```cpp
#include "CADInterfacesModule.h"

// 检查 CAD 接口是否可用
ECADInterfaceAvailability Availability = ICADInterfacesModule::GetAvailability();

if (Availability == ECADInterfaceAvailability::Available)
{
    // 获取 TechSoft SDK 版本
    const TCHAR* Version = ICADInterfacesModule::GetLibraryVersion();
    UE_LOG(LogTemp, Log, TEXT("TechSoft Version: %s"), Version);
}
```

### 使用 TechSoft 接口进行底层操作

```cpp
#include "TechSoftInterface.h"

using namespace CADLibrary;

// 获取 TechSoft 接口单例
FTechSoftInterface& TechSoft = FTechSoftInterface::Get();

// 初始化内核
bool bInitialized = TechSoft.InitializeKernel(TEXT(""));

if (bInitialized)
{
    // 加载 CAD 文件
    A3DImport Import;
    // ... 设置导入选项 ...
    
    A3DStatus Status;
    FUniqueTechSoftModelFile ModelFile = TechSoftInterface::LoadModelFileFromFile(Import, Status);
    
    if (ModelFile.IsValid())
    {
        // 获取模型单位
        double Unit = TechSoftInterface::GetModelFileUnit(ModelFile.Get());
        
        // 进行 B-Rep 适配
        int32 ErrorCount = 0;
        A3DCopyAndAdaptBrepModelData Settings;
        A3DCopyAndAdaptBrepModelErrorData* Errors = nullptr;
        TechSoftInterface::AdaptBRepInModelFile(ModelFile.Get(), Settings, ErrorCount, &Errors);
        
        // 缝合模型
        A3DSewOptionsData SewOptions;
        TechSoftInterface::SewModel(ModelFile.Get(), 0.1 /* cm */, &SewOptions);
    }
    // ModelFile 在作用域结束时自动释放
}
```

### 管理 TechSoft 对象生命周期

```cpp
#include "TUniqueTechSoftObj.h"

using namespace CADLibrary;

// 使用 RAII 方式管理 TechSoft 数据结构
// TUniqueTSObj 在析构时自动调用 TechSoft 的 Get(NULL, &data) 释放内存

// 创建并初始化数据结构
TUniqueTSObj<A3DAsmProductOccurrenceData> OccurrenceData;

// 从实体指针填充数据
A3DStatus Status = OccurrenceData.FillFrom(SomeEntityPtr);
if (Status == A3D_SUCCESS)
{
    // 通过运算符访问数据
    const A3DAsmProductOccurrenceData& Data = *OccurrenceData;
    // 或
    OccurrenceData->m_pcPrototype;
}

// 使用索引类型
TUniqueTSObjFromIndex<A3DGraphRgbColorData> ColorData;
ColorData.FillFrom(ColorIndex);
```

### 场景图操作

```cpp
#include "CADSceneGraph.h"

using namespace CADLibrary;

FArchiveSceneGraph SceneGraph;

// 预分配内存
uint32 ComponentCounts[EComponentType::LastType] = {0};
ComponentCounts[EComponentType::Instance] = 100;
ComponentCounts[EComponentType::Reference] = 50;
ComponentCounts[EComponentType::Body] = 20;
SceneGraph.Reserve(ComponentCounts);

// 添加根引用
FArchiveCADObject RootMeta;
RootMeta.Label = TEXT("Root");
FArchiveReference& RootRef = SceneGraph.AddReference(/* from unloaded ref */);

// 添加实例
FArchiveInstance& Instance = SceneGraph.AddInstance(RootMeta);
Instance.ReferenceNodeId = RootRef.Id;

// 添加 Body
FArchiveBody& Body = SceneGraph.AddBody(RootRef, EMesher::TechSoft);
Body.Label = TEXT("Part_Body");

// 序列化到文件
SceneGraph.SerializeMockUp(TEXT("/path/to/cache.sg"));
```

## Demo 示例

以下是一个完整的最小示例，展示如何使用 CADInterfaces 模块检查 SDK 可用性并读取 CAD 文件的基本信息：

### CADImportDemo.h

```cpp
#pragma once

#include "CoreMinimal.h"

class FCADImportDemo
{
public:
    /** 检查 CAD 导入是否可用，并打印版本信息 */
    static bool CheckAvailability();
    
    /** 读取 CAD 文件并打印场景统计 */
    static bool ImportAndAnalyze(const FString& CADFilePath);
};
```

### CADImportDemo.cpp

```cpp
#include "CADImportDemo.h"
#include "CADInterfacesModule.h"
#include "CADFileReader.h"
#include "CADFileData.h"
#include "TechSoftInterface.h"

bool FCADImportDemo::CheckAvailability()
{
    // 检查 TechSoft SDK 是否加载
    ECADInterfaceAvailability Availability = ICADInterfacesModule::GetAvailability();
    
    if (Availability == ECADInterfaceAvailability::Unavailable)
    {
        UE_LOG(LogTemp, Warning, TEXT("CAD 接口不可用，请确保安装了 Datasmith 和 TechSoft SDK"));
        return false;
    }
    
    if (Availability == ECADInterfaceAvailability::Unknown)
    {
        // 触发模块加载
        ICADInterfacesModule::Get();
        Availability = ICADInterfacesModule::GetAvailability();
    }
    
    const TCHAR* Version = ICADInterfacesModule::GetLibraryVersion();
    UE_LOG(LogTemp, Log, TEXT("TechSoft SDK 版本: %s"), Version);
    
    return Availability == ECADInterfaceAvailability::Available;
}

bool FCADImportDemo::ImportAndAnalyze(const FString& CADFilePath)
{
    using namespace CADLibrary;
    
    if (!CheckAvailability())
    {
        return false;
    }
    
    // 设置导入参数
    FImportParameters ImportParams;
    FFileDescriptor FileDescriptor(CADFilePath, TEXT(""), TEXT(""));
    
    // 创建读取器
    FCADFileReader Reader(ImportParams, FileDescriptor);
    
    // 执行导入
    ECADParsingResult Result = Reader.ProcessFile();
    
    if (Result != ECADParsingResult::Success)
    {
        UE_LOG(LogTemp, Error, TEXT("CAD 文件导入失败: %s"), *CADFilePath);
        return false;
    }
    
    // 分析结果
    const FCADFileData& Data = Reader.GetCADFileData();
    const FArchiveSceneGraph& SceneGraph = Data.GetSceneGraphArchive();
    
    UE_LOG(LogTemp, Log, TEXT("=== CAD 导入统计 ==="));
    UE_LOG(LogTemp, Log, TEXT("文件: %s"), *CADFilePath);
    UE_LOG(LogTemp, Log, TEXT("引用数量: %d"), SceneGraph.References.Num());
    UE_LOG(LogTemp, Log, TEXT("实例数量: %d"), SceneGraph.Instances.Num());
    UE_LOG(LogTemp, Log, TEXT("Body 数量: %d"), SceneGraph.Bodies.Num());
    UE_LOG(LogTemp, Log, TEXT("外部引用: %d"), SceneGraph.ExternalReferenceFiles.Num());
    UE_LOG(LogTemp, Log, TEXT("颜色数量: %d"), SceneGraph.ColorHIdToColor.Num());
    UE_LOG(LogTemp, Log, TEXT("材质数量: %d"), SceneGraph.MaterialHIdToMaterial.Num());
    
    // 遍历 Body 网格统计
    const TArray<FBodyMesh>& BodyMeshes = Data.GetBodyMeshes();
    int32 TotalVertices = 0;
    int32 TotalFaces = 0;
    
    for (const FBodyMesh& BodyMesh : BodyMeshes)
    {
        for (const auto& [MeshKey, TessData] : BodyMesh.Meshes)
        {
            TotalVertices += TessData.PositionArray.Num();
            TotalFaces += TessData.PositionIndices.Num() / 3;
        }
    }
    
    UE_LOG(LogTemp, Log, TEXT("总顶点数: %d"), TotalVertices);
    UE_LOG(LogTemp, Log, TEXT("总面数: %d"), TotalFaces);
    
    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | 商业 CAD 内核 SDK，提供 40+ 种 CAD 格式的读写能力 |
| `OpenNurbs6` | Rhino 的开源 NURBS 库，用于 .3dm 文件解析 |
| `CADKernel` | UE 自有的 CAD 内核，用于参数化曲面处理和网格生成 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 转 float 的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 使 Wire 翻译器兼容 Alias 2027 版本 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft SDK 至 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 DatasmithCAD 缓存版本 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使类型转换警告在 MSVC 和 Clang 之间可移植 |

### 维护评价

**活跃维护** — 该插件仍在积极维护中。

- **创建时间**：2019 年 10 月，已有约 7 年历史
- **最近更新**：2026 年 5 月仍有实质性更新（TechSoft SDK 升级、新 Alias 版本兼容）
- **维护状态**：高度活跃，定期更新 CAD SDK 版本和添加新格式支持
- **WireInterface 模块**：包含 2020-2026 共 11 个版本的翻译器模块，表明持续跟进 CAD 内核版本
- **注意事项**：
  - 依赖商业授权的 TechSoft SDK，需要单独获取许可
  - 默认禁用（`EnabledByDefault=false`），需手动启用
  - 大型装配体导入可能消耗大量内存和时间
  - 缓存机制（`.sg`/`.gm` 文件）可显著加速重复导入

**推荐使用**：如果你的项目需要导入工业 CAD 文件，这是 UE5 官方推荐的方案。确保正确配置 TechSoft SDK 许可证。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)