# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入导出器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器自定义） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USDImporter 是 Unreal Engine 与 Pixar Universal Scene Description (USD) 之间的双向桥梁。它解决的核心问题是：如何在 UE 和其他 DCC 工具（如 Houdini、Maya、Blender、Omniverse）之间交换复杂的 3D 场景数据。

尽管名称为"Importer"，该插件实际上提供完整的 USD 工作流支持：
- **导入**：将 `.usd`/`.usda`/`.usdc` 文件导入为 UE 资产（网格、材质、动画、灯光、相机等）
- **导出**：将 UE 级别、静态/骨骼网格、动画序列、材质、几何缓存、植被等导出为 USD
- **实时 Stage 编辑**：在编辑器中直接操作 USD Stage 的 Prim 层次结构，支持引用（Reference）、负载（Payload）、变体（Variant）等 USD 合成弧
- **双向材质转换**：在 UE 材质和 UsdPreviewSurface 之间烘焙转换

**需要手动启用**：该插件默认关闭（`EnabledByDefault: false`），且标记为实验性（`IsBetaVersion: true`），在项目设置中需要手动勾选启用。

## 模块概览

该插件由 9 个模块组成，覆盖 USD 工作流的各个方面：

| 模块 | 类型 | 用途 |
|---|---|---|
| `USDStage` | Runtime | USD Stage 管理核心，提供 Stage 缓存和基本操作 |
| `USDStageImporter` | Runtime | USD 文件导入器，将 USD 资产转换为 UE 内部格式 |
| `USDExporter` | Runtime | UE 资产/级别导出为 USD，含蓝图可调用的转换工具库 |
| `USDSchemas` | Runtime | USD Schema 定义，将 USD Prim 类型映射到 UE 组件 |
| `USDStageEditor` | Runtime | USD Stage 编辑器 UI，Stage 面板和 Prim 属性面板 |
| `USDStageEditorViewModels` | Runtime | Stage 编辑器的 MVVM 视图模型层 |
| `USDClassesEditor` | Runtime | 编辑器专用的 USD 类注册和自定义 |
| `GeometryCacheUSD` | Runtime | 几何缓存的 USD 导入/导出支持 |
| `USDTests` | Runtime | 自动化测试用例 |

## 使用场景

- 你在用 Houdini/Maya 制作资产，需要导入到 UE 中 → 用 USD Importer 导入 `.usd` 文件
- 你需要将 UE 关卡导出给 Omniverse 做协作评审 → 用 Level Export to USD
- 你需要批量导出大量静态网格为 USD 格式供流水线使用 → 用 StaticMesh Exporter
- 你需要在 Python 脚本中自动化 USD 资产处理 → 用 `UUsdConversionBlueprintContext` 和 `UUsdConversionBlueprintLibrary`
- 你需要在编辑器中直接编辑 USD Stage 的 Prim 属性、添加引用/负载 → 用 USD Stage Editor 面板
- 你需要将 UE 材质烘焙为 UsdPreviewSurface 并随网格一起导出 → 用材质烘焙导出选项
- 你需要将 Level Sequence 动画导出为 USD 动画层 → 用 LevelSequence Exporter

---

## USDExporter 模块文档

> 本文档重点覆盖 `USDExporter` 模块的 API，该模块提供从 UE 导出到 USD 的全部功能和蓝图工具库。

### 模块概述

`USDExporter` 是整个导出工作流的核心模块，提供：
1. **蓝图工具库**（`UUsdConversionBlueprintLibrary`）：38000+ 行的静态工具函数，覆盖世界管理、Layer 操作、Prim 操作、元数据管理、序列化/反序列化等
2. **转换上下文**（`UUsdConversionBlueprintContext`）：实例化的 Stage 上下文对象，用于逐组件转换（灯光、相机、网格、植被、地形等）
3. **各类资产导出器**：StaticMesh、SkeletalMesh、Material、AnimSequence、GeometryCache、Level、LevelSequence 专用导出器
4. **导出选项**：每个导出器都有对应的蓝图可配置选项类

---

## 蓝图用法

### 核心节点 — 世界与级别管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumLevelsToExport` | 计算需要导出的关卡数量 | `UUsdConversionBlueprintLibrary` |
| `StreamInRequiredLevels` | 加载所有需要导出的子关卡 | `UUsdConversionBlueprintLibrary` |
| `StreamOutLevels` | 导出完成后卸载子关卡 | `UUsdConversionBlueprintLibrary` |
| `GetLoadedLevelNames` | 获取当前已加载的关卡名列表 | `UUsdConversionBlueprintLibrary` |
| `GetVisibleInEditorLevelNames` | 获取编辑器中可见的关卡名列表 | `UUsdConversionBlueprintLibrary` |
| `GetActorsToConvert` | 获取需要转换的 Actor 集合 | `UUsdConversionBlueprintLibrary` |
| `RevertSequencerAnimations` | 撤销 Sequencer 动画对场景的影响 | `UUsdConversionBlueprintLibrary` |
| `ReapplySequencerAnimations` | 恢复 Sequencer 动画状态 | `UUsdConversionBlueprintLibrary` |

### 核心节点 — USD Layer 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CanExportToLayer` | 检查是否可以导出到指定 Layer 路径 | `UUsdConversionBlueprintLibrary` |
| `MakePathRelativeToLayer` | 将路径转换为相对于某 Layer 的路径 | `UUsdConversionBlueprintLibrary` |
| `InsertSubLayer` | 在父 Layer 中插入子 Layer | `UUsdConversionBlueprintLibrary` |
| `AddReference` | 为 Prim 添加 Reference 合成弧 | `UUsdConversionBlueprintLibrary` |
| `AddPayload` | 为 Prim 添加 Payload 合成弧 | `UUsdConversionBlueprintLibrary` |

### 核心节点 — Prim 操作（剪贴板）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CopyPrims` | 复制 Prim 到剪贴板 Stage | `UUsdConversionBlueprintLibrary` |
| `CutPrims` | 剪切 Prim 到剪贴板 Stage | `UUsdConversionBlueprintLibrary` |
| `PastePrims` | 从剪贴板粘贴 Prim 到目标父 Prim 下 | `UUsdConversionBlueprintLibrary` |
| `CanPastePrims` | 检查剪贴板中是否有可粘贴的 Prim | `UUsdConversionBlueprintLibrary` |
| `ClearPrimClipboard` | 清空 Prim 剪贴板 | `UUsdConversionBlueprintLibrary` |
| `DuplicatePrims` | 复制 Prim（支持多种复制类型） | `UUsdConversionBlueprintLibrary` |
| `RemoveAllPrimSpecs` | 删除指定 Layer 上 Prim 的所有 Spec（包括变体内的） | `UUsdConversionBlueprintLibrary` |

### 核心节点 — 元数据管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetUsdAssetUserData` | 获取对象上的 UsdAssetUserData | `UUsdConversionBlueprintLibrary` |
| `SetUsdAssetUserData` | 设置对象的 UsdAssetUserData | `UUsdConversionBlueprintLibrary` |
| `SetMetadataField` | 设置元数据键值对（自动创建结构体） | `UUsdConversionBlueprintLibrary` |
| `GetMetadataField` | 获取元数据值 | `UUsdConversionBlueprintLibrary` |
| `HasMetadataField` | 检查元数据键是否存在 | `UUsdConversionBlueprintLibrary` |
| `ClearMetadataField` | 删除指定元数据键 | `UUsdConversionBlueprintLibrary` |

### 核心节点 — 组件转换上下文

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStageRootLayer` | 设置 Stage 根 Layer 路径 | `UUsdConversionBlueprintContext` |
| `SetEditTarget` | 设置当前编辑目标 Layer | `UUsdConversionBlueprintContext` |
| `Cleanup` | 释放 Stage 引用（脚本中必须调用） | `UUsdConversionBlueprintContext` |
| `ConvertSceneComponent` | 转换场景组件 | `UUsdConversionBlueprintContext` |
| `ConvertLightComponent` | 转换灯光组件 | `UUsdConversionBlueprintContext` |
| `ConvertCineCameraComponent` | 转换电影相机组件 | `UUsdConversionBlueprintContext` |
| `ConvertMeshComponent` | 转换网格组件 | `UUsdConversionBlueprintContext` |
| `ConvertIsmComponent` | 转换实例化静态网格组件 | `UUsdConversionBlueprintContext` |
| `ConvertInstancedFoliageActor` | 转换植被实例 Actor | `UUsdConversionBlueprintContext` |
| `ConvertLandscapeProxyActorMesh` | 转换地形网格 | `UUsdConversionBlueprintContext` |
| `ConvertMaterialOverrides` | 写入材质覆盖到 USD Prim | `UUsdConversionBlueprintContext` |
| `AuthorUnrealMaterialBinding` | 为网格 Prim 创建材质绑定 | `UUsdConversionBlueprintContext` |
| `SetPrimAssetInfo` | 设置 Prim 的 assetInfo 元数据 | `UUsdConversionBlueprintContext` |
| `GetPrimMetadata` | 从 Prim 提取元数据 | `UUsdConversionBlueprintContext` |

### 核心节点 — 导出路径管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BeginUniquePathScope` | 开启唯一路径作用域（保证路径不重复） | `UUsdConversionBlueprintLibrary` |
| `EndUniquePathScope` | 关闭唯一路径作用域并清空缓存 | `UUsdConversionBlueprintLibrary` |
| `GetUniqueFilePathForExport` | 获取保证唯一的导出文件路径 | `UUsdConversionBlueprintLibrary` |
| `GenerateObjectVersionString` | 生成对象版本标识字符串（基于 GUID + 时间戳） | `UUsdConversionBlueprintLibrary` |

### 核心节点 — 植被导出

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInstancedFoliageActorForLevel` | 获取指定关卡的植被实例 Actor | `UUsdConversionBlueprintLibrary` |
| `GetUsedFoliageTypes` | 获取植被 Actor 使用的所有 FoliageType | `UUsdConversionBlueprintLibrary` |
| `GetSource` | 获取 FoliageType 的源资产 | `UUsdConversionBlueprintLibrary` |
| `GetInstanceTransforms` | 获取指定 FoliageType 的所有实例变换 | `UUsdConversionBlueprintLibrary` |

### 核心节点 — 序列化工具

`Stringify`/`Unstringify` 系列节点用于在 UE 类型和 USD 属性字符串格式之间转换，支持所有基本类型（bool、int、float、double、half）、向量、四元数、矩阵及其数组形式。用于 Python/蓝图脚本中与 USD 属性直接交互。

### 使用示例（蓝图描述）

**示例 1：导出关卡为 USD**

1. 获取世界引用 → 调用 `GetNumLevelsToExport` 检查关卡数量
2. 调用 `StreamInRequiredLevels` 加载需要的子关卡
3. 创建 `ULevelExporterUSDOptions` 对象，设置导出选项（Stage 格式、根 Prim 名、是否导出子关卡为 Layer 等）
4. 通过导出任务 API 触发导出
5. 导出完成后调用 `StreamOutLevels` 恢复关卡状态

**示例 2：Python 脚本中将组件转换为 USD Prim**

1. 创建 `UUsdConversionBlueprintContext` 对象
2. 调用 `SetStageRootLayer` 指定目标 USD 文件路径
3. 调用 `SetEditTarget` 设置编辑目标 Layer
4. 对每个需要转换的组件调用对应的 `ConvertXxxComponent` 方法（如 `ConvertPointLightComponent`、`ConvertCineCameraComponent`）
5. **必须**调用 `Cleanup` 释放 Stage 引用

**示例 3：Prim 剪切粘贴操作**

1. 调用 `CopyPrims` 或 `CutPrims` 将选中的 Prim 复制到剪贴板
2. 调用 `CanPastePrims` 确认可以粘贴
3. 调用 `PastePrims` 指定父 Prim 路径进行粘贴
4. 操作完成后调用 `ClearPrimClipboard` 清理

---

## C++ 用法

### 头文件引入

```cpp
#include "USDConversionBlueprintLibrary.h"
#include "USDConversionBlueprintContext.h"
#include "LevelExporterUSDOptions.h"
#include "USDAssetOptions.h"
```

### 基本用法 — 检查导出权限和管理级别

```cpp
#include "USDConversionBlueprintLibrary.h"

// 检查是否可以导出到指定路径
bool bCanExport = UUsdConversionBlueprintLibrary::CanExportToLayer(TEXT("C:/Exports/MyLevel.usda"));

// 获取需要导出的关卡数量（排除某些关卡）
TSet<FString> LevelsToIgnore;
LevelsToIgnore.Add(TEXT("Persistent Level"));
int32 NumLevels = UUsdConversionBlueprintLibrary::GetNumLevelsToExport(World, LevelsToIgnore);

// 加载需要导出的子关卡
UUsdConversionBlueprintLibrary::StreamInRequiredLevels(World, LevelsToIgnore);

// 导出完成后恢复状态
TArray<FString> LoadedLevels = UUsdConversionBlueprintLibrary::GetLoadedLevelNames(World);
TArray<FString> VisibleLevels = UUsdConversionBlueprintLibrary::GetVisibleInEditorLevelNames(World);
UUsdConversionBlueprintLibrary::StreamOutLevels(World, LoadedLevels, VisibleLevels);
```

### 基本用法 — Layer 操作和引用

```cpp
// 插入子 Layer
UUsdConversionBlueprintLibrary::InsertSubLayer(
    TEXT("C:/Stage/Root.usda"),
    TEXT("C:/Stage/Child.usda"),
    0  // 插入索引
);

// 添加 Reference
UUsdConversionBlueprintLibrary::AddReference(
    TEXT("C:/Stage/Root.usda"),         // ReferencingStagePath
    TEXT("/Root/MyPrim"),                // ReferencingPrimPath
    TEXT("C:/Assets/Cube.usda"),         // TargetStagePath
    TEXT(""),                            // TargetPrimPath（空=整个文件）
    0.0,                                 // TimeCodeOffset
    1.0,                                 // TimeCodeScale
    false,                               // bUseProjectDefaultTypeHandling
    EReferencerTypeHandling::MatchReferencedType  // 类型处理方式
);

// 添加 Payload（按需加载）
UUsdConversionBlueprintLibrary::AddPayload(
    TEXT("C:/Stage/Root.usda"),
    TEXT("/Root/HeavyAsset"),
    TEXT("C:/Assets/HeavyAsset.usdc"),
    TEXT("/HeavyAsset/Geometry")
);
```

### 进阶用法 — 组件转换上下文

```cpp
#include "USDConversionBlueprintContext.h"

// 创建转换上下文
UUsdConversionBlueprintContext* Context = NewObject<UUsdConversionBlueprintContext>();

// 设置 Stage 根层
Context->SetStageRootLayer(FFilePath{TEXT("C:/Exports/MyScene.usda")});
Context->SetEditTarget(FFilePath{TEXT("C:/Exports/MyScene.usda")});

// 转换各种组件到 USD Prim
// 对于时序相关的组件，可传入 TimeCode
Context->ConvertPointLightComponent(PointLightComp, TEXT("/Root/Lights/PointLight"), UsdTimeCode);
Context->ConvertCineCameraComponent(CameraComp, TEXT("/Root/Cameras/MainCam"), UsdTimeCode);
Context->ConvertSceneComponent(SceneComp, TEXT("/Root/Transforms/Node"));

// 转换实例化网格
Context->ConvertIsmComponent(ISMComp, TEXT("/Root/Meshes/Instances"), UsdTimeCode);

// 转换植被
Context->ConvertInstancedFoliageActor(FoliageActor, TEXT("/Root/Foliage/Trees"));

// 转换地形（指定 LOD 范围）
Context->ConvertLandscapeProxyActorMesh(
    LandscapeActor,
    TEXT("/Root/Landscape/Main"),
    0,    // LowestLOD
    4,    // HighestLOD
    UsdTimeCode
);

// 设置材质覆盖
TArray<UMaterialInterface*> MaterialOverrides;
MaterialOverrides.Add(MyMaterial);
Context->ConvertMaterialOverrides(
    MeshAsset,
    MaterialOverrides,
    TEXT("/Root/Meshes/MyMesh"),
    0,     // LowestLOD
    4,     // HighestLOD
    true   // bCheckAssetUserData
);

// 写入元数据
FUsdCombinedPrimMetadata Metadata;
Context->SetPrimMetadata(
    TEXT("/Root/MyPrim"),
    Metadata,
    {},      // BlockedPrefixFilter
    false    // bInvertFilter
);

// !! 必须释放 Stage 引用 !!
Context->Cleanup();
```

### 进阶用法 — Prim 剪贴板操作

```cpp
// 复制 Prim
TArray<FString> PrimsToCopy = {TEXT("/Root/Object1"), TEXT("/Root/Object2")};
bool bCopied = UUsdConversionBlueprintLibrary::CopyPrims(
    TEXT("C:/Stage/Root.usda"),
    PrimsToCopy
);

// 粘贴到新父 Prim 下
if (UUsdConversionBlueprintLibrary::CanPastePrims())
{
    TArray<FString> PastedPaths = UUsdConversionBlueprintLibrary::PastePrims(
        TEXT("C:/Stage/Root.usda"),
        TEXT("/Root/NewParent")
    );
    // PastedPaths 包含实际粘贴后的路径（可能被重命名）
}

// 复制 Prim（支持不同复制类型）
TArray<FString> DuplicatedPaths = UUsdConversionBlueprintLibrary::DuplicatePrims(
    TEXT("C:/Stage/Root.usda"),
    PrimsToCopy,
    EUsdDuplicateType::FlatCopy,  // 平面复制
    TEXT("")                        // TargetLayer（空=当前 Layer）
);

// 清理
UUsdConversionBlueprintLibrary::ClearPrimClipboard();
```

### 进阶用法 — 版本追踪与唯一路径

```cpp
// 开启唯一路径作用域，防止导出路径冲突
UUsdConversionBlueprintLibrary::BeginUniquePathScope();

FString Path1 = UUsdConversionBlueprintLibrary::GetUniqueFilePathForExport(
    TEXT("C:/Exports/Mesh.usda")
);
// 返回 "C:/Exports/Mesh.usda"

FString Path2 = UUsdConversionBlueprintLibrary::GetUniqueFilePathForExport(
    TEXT("C:/Exports/Mesh.usda")
);
// 返回 "C:/Exports/Mesh_1.usda"（自动加后缀避免冲突）

UUsdConversionBlueprintLibrary::EndUniquePathScope();

// 生成对象版本字符串（用于增量导出判断）
FString VersionHash = UUsdConversionBlueprintLibrary::GenerateObjectVersionString(
    MyAsset,
    ExportOptions  // 可选，包含导出选项的哈希
);
```

---

## Demo 示例

### 完整的 C++ 导出示例 — 将关卡导出为 USD

```cpp
// MyUSDEExporter.h
#pragma once

#include "CoreMinimal.h"
#include "UObject/NoExportTypes.h"
#include "USDConversionBlueprintContext.h"
#include "USDConversionBlueprintLibrary.h"
#include "LevelExporterUSDOptions.h"

class FMyUSDExporter
{
public:
    static bool ExportWorldToUSD(UWorld* World, const FString& OutputPath);
    static void ExportActorToStage(UUsdConversionBlueprintContext* Context, AActor* Actor, const FString& PrimPath);
};
```

```cpp
// MyUSDExporter.cpp
#include "MyUSDExporter.h"
#include "USDConversionBlueprintLibrary.h"
#include "USDConversionBlueprintContext.h"
#include "LevelExporterUSDOptions.h"

bool FMyUSDExporter::ExportWorldToUSD(UWorld* World, const FString& OutputPath)
{
    if (!World || !UUsdConversionBlueprintLibrary::CanExportToLayer(OutputPath))
    {
        return false;
    }

    // 1. 加载需要导出的子关卡
    TSet<FString> LevelsToIgnore;
    UUsdConversionBlueprintLibrary::StreamInRequiredLevels(World, LevelsToIgnore);

    // 2. 创建转换上下文
    UUsdConversionBlueprintContext* Context = NewObject<UUsdConversionBlueprintContext>();
    Context->SetStageRootLayer(FFilePath{OutputPath});
    Context->SetEditTarget(FFilePath{OutputPath});

    // 3. 获取需要导出的 Actor 并逐个转换
    TSet<AActor*> Actors = UUsdConversionBlueprintLibrary::GetActorsToConvert(World);
    for (AActor* Actor : Actors)
    {
        FString PrimPath = UUsdConversionBlueprintLibrary::GetPrimPathForObject(
            Actor, TEXT(""), false, TEXT("Root")
        );
        ExportActorToStage(Context, Actor, PrimPath);
    }

    // 4. 清理
    Context->Cleanup();

    // 5. 恢复关卡状态
    TArray<FString> Loaded = UUsdConversionBlueprintLibrary::GetLoadedLevelNames(World);
    TArray<FString> Visible = UUsdConversionBlueprintLibrary::GetVisibleInEditorLevelNames(World);
    UUsdConversionBlueprintLibrary::StreamOutLevels(World, Loaded, Visible);

    return true;
}

void FMyUSDExporter::ExportActorToStage(
    UUsdConversionBlueprintContext* Context,
    AActor* Actor,
    const FString& PrimPath)
{
    // 遍历 Actor 的组件并转换
    for (UActorComponent* Comp : Actor->GetComponents())
    {
        FString CompPrimPath = PrimPath + TEXT("/") + Comp->GetName();

        if (UPointLightComponent* PointLight = Cast<UPointLightComponent>(Comp))
        {
            Context->ConvertPointLightComponent(PointLight, CompPrimPath);
        }
        else if (USpotLightComponent* SpotLight = Cast<USpotLightComponent>(Comp))
        {
            Context->ConvertSpotLightComponent(SpotLight, CompPrimPath);
        }
        else if (UCineCameraComponent* Camera = Cast<UCineCameraComponent>(Comp))
        {
            Context->ConvertCineCameraComponent(Camera, CompPrimPath);
        }
        else if (UMeshComponent* MeshComp = Cast<UMeshComponent>(Comp))
        {
            Context->ConvertMeshComponent(MeshComp, CompPrimPath);
        }
        else if (USceneComponent* SceneComp = Cast<USceneComponent>(Comp))
        {
            Context->ConvertSceneComponent(SceneComp, CompPrimPath);
        }
    }
}
```

---

## 模块依赖

从 USDExporter 模块的 Build.cs 提取的独特依赖（省略 Core/Engine/Slate 等通用依赖）：

| 模块 | 用途 |
|---|---|
| `USDClasses` | USD 基础类定义（USDAssetUserData、StageOptions 等） |
| `USDUtilities` | USD 底层工具函数（Stage 操作、类型转换） |
| `USDStage` | USD Stage 管理和缓存 |
| `Landscape` | 地形导出支持 |
| `Foliage` | 植被实例导出支持 |
| `MaterialBaking` | 材质烘焙为纹理（用于 UsdPreviewSurface 转换） |
| `Analytics` | 导出分析事件上报 |
| `RenderCore` | 渲染核心（材质烘焙需要） |
| `MeshDescription` | 网格描述（网格导出） |
| `StaticMeshDescription` | 静态网格描述 |
| `SkeletalMeshDescription` | 骨骼网格描述 |

> **注意**：该插件还依赖第三方 USD 库（OpenUSD），由 UE 构建系统提供。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 新增独立于蓝图的 Control Rig 分配支持 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD values change. | 修复 USD 26.03 升级导致 LOD 值变化时 AnimQuery 内部引用失效的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式化说明符的 32/64 位匹配问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 烘焙曝光动画轨道的所有帧 |

### 维护评价

- **活跃维护**：最近一次更新为 2026 年 5 月，近一个月内有 5 次提交，包括功能增强（Control Rig 支持）、Bug 修复（USD 26.03 兼容性、浮点警告、格式化说明符）和行为改进（动画烘焙）
- **长期项目**：创建于 2018 年 11 月，已持续维护约 7 年，从早期的实验性插件逐步发展为成熟的全功能 USD 工作流
- **实验性状态**：尽管维护活跃，仍标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，API 可能在未来版本发生变化
- **推荐使用**：对于需要 USD 互操作的项目，该插件是官方推荐方案。功能全面覆盖导入、导出、实时编辑等场景。建议关注后续版本的 API 变更，做好升级适配准备

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档](https://docs.unrealengine.com/en-US/working-with-content/usd-in-unreal-engine/)（UE 官方 USD 文档）