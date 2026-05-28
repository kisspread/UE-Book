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
| 年龄标签 | 🏛️ 文物（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter) | |

## 用途

本插件是 Datasmith CAD 导入管线的核心组件，负责将工业 CAD 格式文件（如 `.wire`、`.step`、`.iges`、`.jt`、`.PLMXML`、`.3dm` 等）转换为 Unreal Engine 的 Datasmith 场景数据。

**WireInterface2022_2** 是该插件中用于导入 **Autodesk Alias** `.wire` 格式文件的特定版本适配器模块。Autodesk Alias 是汽车行业广泛使用的工业设计/A 级曲面建模软件，其 `.wire` 文件格式与 Alias 软件版本紧密耦合。为兼容不同版本的 Alias SDK，插件维护了多个版本化的 WireInterface 模块（从 WireInterface2020 到 WireInterface2026_0），每个模块链接对应版本的 Alias SDK 库。

该模块的核心工作流程：
1. 通过 Alias SDK 读取 `.wire` 文件的 DAG（有向无环图）场景树
2. 遍历节点树，提取几何体（Mesh、Surface、Shell）、材质（Shader）和图层信息
3. 将 Alias 的 BRep 曲面通过 CADKernel 或 TechSoft 两个后端之一进行细分（Tessellation）
4. 输出 Datasmith 格式的 `IDatasmithScene`，包含 Actor 层次、Mesh 和 PBR 材质

## 使用场景

- 你在汽车/工业设计流程中使用 Autodesk Alias 建模 → 用 DatasmithCADImporter 的 WireInterface 将 `.wire` 文件导入 UE
- 你需要将 Alias 的 A 级曲面数据导入 UE 做可视化评审 → 启用此插件并安装对应版本的 Alias SDK
- 你的团队使用多个版本的 Alias（如 2022、2023、2024）→ 选择对应的 WireInterface 版本模块
- 你需要导入 CATIA、NX、SolidWorks 等其他 CAD 格式 → 本插件的其他模块（CADInterfaces、CADLibrary）会处理这些格式

## 蓝图用法

本模块**不暴露任何蓝图 API**。它是 Datasmith 导入管线的内部组件，通过 Datasmith Importer 框架自动调用。用户在编辑器中通过 **File → Import** 或 Datasmith Import Actor 导入 `.wire` 文件时，引擎会自动选择匹配的 WireInterface 模块进行处理。

## C++ 用法

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
```

### 基本用法

通过 `IWireInterface` 接口进行 `.wire` 文件的加载和转换：

```cpp
// 引用: Source/WireInterface/Private/WireInterfaceImpl.h
#include "IWireInterface.h"
#include "WireInterfaceModule.h"

// 创建 Wire 翻译器实例
TUniquePtr<IWireInterface> WireTranslator = MakeUnique<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl>();

// 初始化：指定 .wire 文件路径
FString WireFilePath = TEXT("C:/Models/CarBody.wire");
bool bInitialized = WireTranslator->Initialize(*WireFilePath);

if (bInitialized)
{
    // 创建目标 Datasmith 场景
    TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("ImportedScene"));

    // 设置输出路径（用于缓存细分后的网格数据）
    WireTranslator->SetOutputPath(TEXT("C:/UEProject/Intermediate/Datasmith"));

    // 配置导入设置
    FWireSettings Settings;
    WireTranslator->SetImportSettings(Settings);

    // 执行加载，场景数据将填充到 Scene 中
    bool bLoaded = WireTranslator->Load(Scene);
}
```

### 进阶用法

获取并使用网格数据，自定义细分选项：

```cpp
// 引用: Source/WireInterface/Private/WireInterfaceImpl.h

// 加载特定 Mesh Element 的细分后网格数据
TSharedPtr<IDatasmithMeshElement> MeshElement = /* 从 Scene 中获取 */;
FDatasmithMeshElementPayload MeshPayload;
FDatasmithTessellationOptions TessOptions;
TessOptions.StitchingTechnique = EDatasmithCADStitchingTechnique::StitchingSew;
TessOptions.ChordTolerance = 0.5f;   // 弦高公差（毫米）
TessOptions.MaxEdgeLength = 10.0f;   // 最大边长
TessOptions.NormalTolerance = 10.0f; // 法线角度公差

// 使用 WireTranslatorImpl 的 LoadStaticMesh 方法
bool bGotMesh = WireTranslatorImpl->LoadStaticMesh(MeshElement, MeshPayload, TessOptions);

if (bGotMesh)
{
    // MeshPayload 中包含 FMeshDescription 可用于创建 StaticMesh
    FMeshDescription& MeshDesc = MeshPayload.GetMeshDescription();
    // ... 使用 MeshDescription 创建 UStaticMesh 资产
}
```

### 关键内部类说明

| 类名 | 作用 |
|---|---|
| `FWireTranslatorImpl` | IWireInterface 实现，负责场景遍历和 Datasmith 元素生成 |
| `FAlDagNodePtr` | Alias DAG 节点的智能指针封装，自动管理生命周期并缓存图层/类型信息 |
| `TAlObjectPtr<T>` | Alias SDK 对象的通用智能指针，带有效性检查和调试内存追踪 |
| `FPatchMesh` | 面片网格容器，聚合同图层的 Mesh 节点 |
| `FBodyNode` | 实体节点容器，管理多材质槽位分配 |
| `FAliasModelToCADKernelConverter` | Alias BRep → CADKernel 拓扑结构转换器 |
| `FAliasModelToTechSoftConverter` | Alias BRep → TechSoft 3D 数据结构转换器 |

## Demo 示例

完整的最小翻译示例——读取 `.wire` 文件并输出场景树信息：

```cpp
// WireTranslatorDemo.h
#pragma once

#include "CoreMinimal.h"
#include "IWireInterface.h"
#include "WireInterfaceModule.h"
#include "DatasmithSceneFactory.h"

class FWireTranslatorDemo
{
public:
    static bool ImportWireFile(const FString& WireFilePath, const FString& OutputDir);
};
```

```cpp
// WireTranslatorDemo.cpp
#include "WireTranslatorDemo.h"
#include "WireInterfaceImpl.h"

bool FWireTranslatorDemo::ImportWireFile(const FString& WireFilePath, const FString& OutputDir)
{
    // 检查模块可用性
    if (!UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("WireInterface 模块未加载"));
        return false;
    }

    // 创建翻译器实例
    auto Translator = MakeUnique<UE_DATASMITHWIRETRANSLATOR_NAMESPACE::FWireTranslatorImpl>();

    // 初始化
    if (!Translator->Initialize(*WireFilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("无法初始化 Wire 翻译器: %s"), *WireFilePath);
        return false;
    }

    // 配置
    Translator->SetOutputPath(OutputDir);

    FWireSettings Settings;
    Translator->SetImportSettings(Settings);

    // 创建 Datasmith 场景并执行加载
    TSharedRef<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(
        FPaths::GetBaseFilename(WireFilePath)
    );

    if (!Translator->Load(Scene))
    {
        UE_LOG(LogTemp, Error, TEXT("Wire 文件加载失败"));
        return false;
    }

    // 输出场景信息
    UE_LOG(LogTemp, Log, TEXT("场景名称: %s"), *Scene->GetName());
    UE_LOG(LogTemp, Log, TEXT("Actor 数量: %d"), Scene->GetActorsCount());

    for (int32 i = 0; i < Scene->GetActorsCount(); ++i)
    {
        TSharedPtr<IDatasmithActorElement> Actor = Scene->GetActor(i);
        if (Actor.IsValid())
        {
            UE_LOG(LogTemp, Log, TEXT("  Actor[%d]: %s (%s)"),
                i, *Actor->GetName(), *Actor->GetLabel());
        }
    }

    return true;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft 3D SDK 封装，用于 BRep 模型的细分和转换（CADInterfaces 依赖） |
| `OpenNurbs6` | OpenNurbs 库，用于 NURBS 曲面处理（DatasmithOpenNurbsTranslator 依赖） |
| `DatasmithCore` | Datasmith 核心接口（IDatasmithScene、IDatasmithMeshElement 等） |
| `DatasmithTranslator` | 翻译器框架基类和注册机制 |
| `CADKernel` | Epic 内建的 CAD 内核，用于 BRep 拓扑构建和网格细分 |
| `CADLibrary` | CAD 通用库，提供网格参数、导入参数、模型转换器接口 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 允许 Wire 翻译器在安装 Alias 2027 时仍可正常工作 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft SDK 至 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 Datasmith CAD 缓存版本号 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 使函数类型转换警告在 MSVC 和 Clang 之间可移植 |

### 维护评价

**状态：活跃维护** ✅

- 插件创建于 2019 年，已运行约 7 年，是 Epic Enterprise 工具链的成熟组件
- 最近更新集中在 2026 年 5 月，内容包括 SDK 升级（TechSoft 2026.3）、前向兼容性（Alias 2027）和编译器兼容性修复
- 多版本 WireInterface 模块的存在说明 Epic 持续跟踪 Alias SDK 的版本迭代
- 作为 **企业版插件**（`EnabledByDefault=false`），需要手动在项目设置中启用，且通常需要额外的第三方 SDK（Alias SDK、TechSoft）
- **推荐使用**：如果你的工作流涉及 Autodesk Alias 数据导入，这是官方支持的唯一途径。对于其他 CAD 格式（STEP、JT、3DM 等），本插件的其他模块同样提供支持

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Tests/Datasmith)