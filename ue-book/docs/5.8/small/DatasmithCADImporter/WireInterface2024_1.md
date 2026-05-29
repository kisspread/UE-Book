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

DatasmithCADImporter 是 Datasmith 导入管线中负责 **CAD 文件解析与几何转换** 的核心插件。它解决的根本问题是：将工业 CAD 软件（如 Autodesk Alias、Rhino/OpenNurbs、PLMXML 等）产出的高精度 BRep（边界表示）模型，转换为 Unreal Engine 可渲染的三角网格（MeshDescription），同时保留材质、图层、变换等元数据。

本插件由多个模块组成，核心架构分为三层：

1. **格式翻译层**（DatasmithWireTranslator / DatasmithOpenNurbsTranslator / DatasmithPLMXMLTranslator）：负责读取特定 CAD 格式文件，遍历其 DAG（有向无环图）结构，提取几何体和材质信息
2. **几何处理层**（CADKernelSurface / ParametricSurface / CADLibrary）：提供 BRep → Mesh 的曲面细分（tessellation）能力，支持 CADKernel 和 TechSoft 两种后端
3. **接口适配层**（WireInterface2020 ~ WireInterface2026_0）：封装不同年份版本的 Autodesk Alias SDK，通过版本化模块实现对多版本 Alias 的兼容

其中 **WireInterface2024_1** 是适配 Alias 2024.1 版本 SDK 的模块，本文档以其为主要分析对象。

## 使用场景

- 你在汽车行业做 **外观设计可视化**，需要将 Alias 造型师交付的 `.wire` 文件导入 UE → 用 DatasmithCADImporter（WireInterface 模块）
- 你需要导入 **Rhino 3DM** 格式的 CAD 模型 → 用 DatasmithOpenNurbsTranslator 模块
- 你需要从 PLM 系统导出 **PLMXML** 产品结构 → 用 DatasmithPLMXMLTranslator 模块
- 你需要在运行时通过 **Datasmith 导入管线** 批量处理 CAD 文件 → 用 DatasmithCADTranslator（统一调度）
- 你只需要 BRep 曲面细分能力，不需要完整导入流程 → 直接使用 CADLibrary / CADKernelSurface 模块

> **注意**：本插件默认禁用（`EnabledByDefault: false`），需在 Project Settings → Plugins 中手动启用，或通过命令行 `-EnablePlugin=DatasmithCADImporter` 启用。

## 蓝图用法

本插件没有暴露 `BlueprintCallable` 接口。所有功能均在 C++ 层面通过 Datasmith 导入管线内部调用，最终由 Datasmith Import 蓝图节点间接驱动。

如果你需要通过蓝图导入 CAD 文件，请使用上层 Datasmith 插件提供的蓝图节点（如 `Datasmith Import` 节点），该插件会在后台自动调用对应的 CAD 翻译器。

## C++ 用法

### 头文件引入

```cpp
#include "WireInterfaceModule.h"
#include "IWireInterface.h"
```

### 基本用法：通过 IWireInterface 加载 .wire 文件

`IWireInterface` 是 Wire translator 的核心抽象接口。`FWireTranslatorImpl`（定义在 `Private/WireInterfaceImpl.h`）是其具体实现。

```cpp
// 引自 Private/WireInterfaceImpl.h — FWireTranslatorImpl 的接口实现
// 通常由 DatasmithWireTranslator 模块内部创建和调用，以下展示其核心流程

// 1. 创建翻译器实例并初始化
FWireTranslatorImpl Translator;
bool bInitialized = Translator.Initialize(TEXT("C:/Models/CarBody.wire"));

// 2. 配置导入选项
FWireSettings Settings;
// ... 设置细分精度、单位等参数
Translator.SetImportSettings(Settings);
Translator.SetOutputPath(TEXT("C:/Output/"));

// 3. 创建 Datasmith Scene 并加载
TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(TEXT("CarBody"));
Translator.Load(Scene);

// 4. 获取网格数据（用于 MeshElement 级别的导入）
TSharedPtr<IDatasmithMeshElement> MeshElement = /* 从场景中获取 */;
FDatasmithMeshElementPayload MeshPayload;
FDatasmithTessellationOptions TessOptions;
TessOptions.StitchingTechnique = EStitchingTechnique::StitchingTechnique_None;
Translator.LoadStaticMesh(MeshElement, MeshPayload, TessOptions);
```

### 进阶用法：理解 DAG 遍历与材质转换

Wire translator 内部通过遍历 Alias DAG 结构来提取几何和材质。关键数据类型定义在 `Private/OpenModelUtils.h`：

```cpp
// 引自 Private/OpenModelUtils.h — DAG 节点智能指针与几何容器

// FAlDagNodePtr 封装了 Alias AlDagNode，提供类型查询和层级访问
FAlDagNodePtr DagNode(InAlDagNode);

// 查询节点类型
if (DagNode.IsAMesh())
{
    TAlObjectPtr<AlMesh> Mesh;
    DagNode.GetMesh(Mesh);
}
else if (DagNode.IsASurface())
{
    TAlObjectPtr<AlSurface> Surface;
    DagNode.GetSurface(Surface);
}
else if (DagNode.IsAShell())
{
    TAlObjectPtr<AlShell> Shell;
    DagNode.GetShell(Shell);
}

// 获取图层信息
FString LayerName = DagNode.GetLayerName();
bool bVisible = DagNode.IsVisible();
bool bSymmetric = DagNode.HasSymmetry();

// 设置 Actor 变换（从 Alias 坐标系转换到 UE 坐标系）
IDatasmithActorElement& Actor = /* ... */;
DagNode.SetActorTransform(Actor);
// 内部将 Z-Up Right-Handed 转换为 UE 坐标系，并处理对称图层的特殊逻辑

// BRep 几何转换（通过 CADKernel 或 TechSoft 后端）
// 引自 Private/AliasModelToCADKernelConverter.h
FAliasModelToCADKernelConverter Converter(TessOptions, ImportParams);
Converter.AddBRep(DagNode, Color, EAliasObjectReference::LocalReference);

FMeshDescription OutMesh;
CADLibrary::FMeshParameters MeshParams;
Converter.Tessellate(MeshParams, OutMesh);
```

### 几何容器：BodyNode 与 PatchMesh

`FBodyNode` 和 `FPatchMesh` 是两种将多个 DAG 节点组合为单一网格的容器：

```cpp
// 引自 Private/OpenModelUtils.h

// FBodyNode：将多个 DAG 节点组合为一个 Body，支持多材质槽
FBodyNode BodyNode(TEXT("Door"), Layer, 4);
BodyNode.AddNode(DagNode1);
BodyNode.AddNode(DagNode2);

// 遍历材质槽
BodyNode.IterateOnSlotIndices([](int SlotIndex, const TAlObjectPtr<AlShader>& Shader)
{
    // 每个槽对应一个 Alias Shader
});

// 获取单内容（优化路径，避免不必要的网格合并）
FAlDagNodePtr SingleDag;
if (BodyNode.GetSingleContent(SingleDag))
{
    // 仅包含单个节点，可直接处理
}

// FPatchMesh：类似 BodyNode，但用于补丁网格
FPatchMesh PatchMesh(TEXT("Fender"), Layer, 2);
PatchMesh.AddMeshNode(MeshNode1);
```

## Demo 示例

以下展示如何在 C++ 中使用 Wire translator 接口加载 Alias 文件并提取网格：

```cpp
// WireExample.h
#pragma once

#include "CoreMinimal.h"

struct FMeshDescription;
class IDatasmithScene;

class FWireImportExample
{
public:
    /** 加载 .wire 文件并返回场景 */
    static TSharedPtr<IDatasmithScene> ImportWireFile(const FString& FilePath);

    /** 从已加载场景中提取指定 Mesh 的网格数据 */
    static bool ExtractMeshData(
        const TSharedPtr<IDatasmithScene>& Scene,
        int32 MeshIndex,
        FMeshDescription& OutMesh
    );
};
```

```cpp
// WireExample.cpp
#include "WireExample.h"

#include "WireInterfaceModule.h"
#include "IWireInterface.h"
#include "DatasmithSceneFactory.h"
#include "DatasmithMesh.h"

using namespace UE_DATASMITHWIRETRANSLATOR_NAMESPACE;

TSharedPtr<IDatasmithScene> FWireImportExample::ImportWireFile(const FString& FilePath)
{
    // 检查模块是否可用
    if (!FDatasmithWireTranslatorModule::IsAvailable())
    {
        UE_LOG(LogTemp, Error, TEXT("WireInterface module is not loaded"));
        return nullptr;
    }

    // 创建翻译器实例
    FWireTranslatorImpl Translator;

    // 初始化：传入 .wire 文件的完整路径
    if (!Translator.Initialize(*FilePath))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to initialize Wire translator for: %s"), *FilePath);
        return nullptr;
    }

    // 配置导入参数
    FWireSettings Settings;
    Translator.SetImportSettings(Settings);

    // 设置输出缓存目录
    FString TempDir = FDatasmithWireTranslatorModule::Get().GetTempDir();
    Translator.SetOutputPath(TempDir);

    // 创建 Datasmith 场景并执行加载
    // 加载过程会遍历 Alias DAG，提取几何体和材质
    TSharedPtr<IDatasmithScene> Scene = FDatasmithSceneFactory::CreateScene(
        FPaths::GetBaseFilename(FilePath)
    );

    if (!Translator.Load(Scene))
    {
        UE_LOG(LogTemp, Error, TEXT("Failed to load Wire file: %s"), *FilePath);
        return nullptr;
    }

    UE_LOG(LogTemp, Log, TEXT("Successfully imported Wire file with %d meshes"),
        Scene->GetMeshesCount());

    return Scene;
}

bool FWireImportExample::ExtractMeshData(
    const TSharedPtr<IDatasmithScene>& Scene,
    int32 MeshIndex,
    FMeshDescription& OutMesh)
{
    if (!Scene.IsValid() || MeshIndex < 0 || MeshIndex >= Scene->GetMeshesCount())
    {
        return false;
    }

    // 通过 Datasmith 标准管线获取网格数据
    TSharedPtr<IDatasmithMeshElement> MeshElement = Scene->GetMesh(MeshIndex);

    // 使用 Datasmith 的运行时网格加载器
    FDatasmithMeshElementPayload MeshPayload;
    FDatasmithTessellationOptions TessOptions;
    TessOptions.StitchingTechnique = EStitchingTechnique::StitchingTechnique_None;

    // 加载网格到 MeshDescription
    FDatasmithMeshUtils::LoadStaticMesh(MeshElement, OutMesh, TessOptions);

    UE_LOG(LogTemp, Log, TEXT("Mesh '%s': %d vertices, %d triangles"),
        *MeshElement->GetName(),
        OutMesh.Vertices().Num(),
        OutMesh.Triangles().Num());

    return true;
}
```

## 模块依赖

本插件的依赖关系通过各子模块的 Build.cs 管理。以下是 **非标准** 的独特依赖：

| 模块 | 用途 |
|---|---|
| `TechSoft` | TechSoft A3D 内核，用于 BRep → Mesh 的高精度曲面细分 |
| `OpenNurbs6` | OpenNurbs 库，用于读取 Rhino 3DM 格式文件 |
| `DatasmithContent` | Datasmith 内容类型定义（IDatasmithScene / IDatasmithMeshElement 等） |
| `CADLibrary` | CAD 几何处理公共库（FMeshParameters、ICADModelConverter 等） |
| `MeshConversion` | MeshDescription 构建与转换工具 |

> WireInterface 系列模块还依赖外部 **Autodesk Alias SDK**（通过 CADInterfaces 模块桥接），该 SDK 随引擎以预编译库形式提供。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 截断为 float 的编译警告 |
| 2026-05-13 | `889b1ce2` | Added logic to allow Wire translator to work even if Alias 2027 is installed | 新增 Alias 2027 兼容逻辑 |
| 2026-05-13 | `52c91865` | Updated TechSoft to 2026.3 | 升级 TechSoft 库至 2026.3 版本 |
| 2026-05-12 | `f8fbdc1f` | Updated version of DatasmithCAD cache | 更新 DatasmithCAD 缓存版本号 |
| 2026-05-12 | `3e657fb3` | Make function type cast warnings portable between MSVC and Clang. | 修复 MSVC/Clang 间的函数类型转换警告可移植性 |

### 维护评价

**活跃维护** — 推荐使用（企业级场景）。

本插件持续获得 Epic 团队的维护更新，最近一次提交距今不到 1 周（2026-05-13）。维护内容涵盖：

- **兼容性扩展**：持续添加新版 Alias SDK 支持（WireInterface 模块从 2020 到 2026_0 共 10 个版本），并前瞻支持 Alias 2027
- **依赖库更新**：TechSoft 内核定期升级
- **编译质量改进**：跨编译器（MSVC/Clang）的警告修复和浮点精度处理

**已知限制**：
- 默认禁用（`EnabledByDefault: false`），需手动启用
- 依赖 Autodesk Alias SDK，仅在安装了 Alias 的工作站上可用
- 纯 Runtime 模块，无编辑器内预览 UI，完全通过 Datasmith 导入管线驱动
- 每个 WireInterface 版本模块绑定特定 Alias SDK 版本，不支持跨版本混用

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [WireInterface2024_1 源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/DatasmithCADImporter/Source/WireInterface)