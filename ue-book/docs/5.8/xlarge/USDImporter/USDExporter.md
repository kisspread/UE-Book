# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD导入导出器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、编辑器工具） |
| 模块 | `USDSchemas` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime), `GeometryCacheUSD` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USDImporter 是 Unreal Engine 的 USD（Universal Scene Description）全流程支持插件。虽然 .uplugin 的 Description 只提到"导入"，但实际上该插件涵盖了 **导入、导出、编辑、预览** 四大功能：

- **导入**（USDStageImporter）：将 `.usd` / `.usda` / `.usdc` 文件加载为 UE 内容，包括网格、材质、动画、灯光、摄像机等
- **导出**（USDExporter）：将 UE 的关卡、静态网格、骨骼网格、材质、动画序列、几何缓存、关卡序列等导出为 USD 格式
- **编辑**（USDStage / USDStageEditor）：在 UE 编辑器中提供 USD Stage 窗口，支持实时查看和编辑 USD Stage 内容
- **Schema 支持**（USDSchemas）：定义 USD Prim 与 UE 组件/Actor 之间的映射规则

该插件解决的核心问题是 **影视/动画/VFX 工作流中 UE 与 DCC 工具（Maya、Houdini、Blender 等）之间的资产交换**。USD 作为 Pixar 开发的开放场景描述格式，已成为影视行业的标准，此插件让 UE 无缝融入这个生态系统。

**注意**：该插件默认未启用（`EnabledByDefault: false`），且标记为实验性（`IsBetaVersion: true`），需要在项目设置中手动启用。

## 使用场景

- 你从 Maya/Houdini 导出的 USD 资产需要导入 UE → 使用 USDStageImporter 加载 `.usd` 文件
- 你需要将 UE 关卡导出回 DCC 工具进行后期处理 → 使用 LevelExporterUSD
- 你需要将 UE 材质烘焙为 UsdPreviewSurface 标准格式 → 使用 MaterialExporterUSD
- 你需要在 UE 中预览和编辑 USD Stage 的层级结构 → 使用 USDStageEditor 窗口
- 你需要将骨骼动画导出为 USD → 使用 AnimSequenceExporterUSD
- 你需要在蓝图/Python 中批量处理 USD 导出流程 → 使用 UsdConversionBlueprintLibrary 和 UsdConversionBlueprintContext

---

## USDExporter 模块文档

USDExporter 是该插件的导出功能核心模块，负责将各种 UE 资产类型转换并写入 USD 格式文件。

### 蓝图用法

USDExporter 模块通过 `UUsdConversionBlueprintLibrary`（静态函数库）和 `UUsdConversionBlueprintContext`（实例化上下文）暴露了丰富的蓝图 API。

#### 核心节点 — 世界/关卡工具

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetNumLevelsToExport` | 获取导出时会涉及的关卡总数 | `UUsdConversionBlueprintLibrary` |
| `StreamInRequiredLevels` | 将需要导出的子关卡全部流式加载 | `UUsdConversionBlueprintLibrary` |
| `StreamOutLevels` | 导出完成后卸载临时加载的子关卡 | `UUsdConversionBlueprintLibrary` |
| `GetLoadedLevelNames` | 获取当前已加载的关卡路径名列表 | `UUsdConversionBlueprintLibrary` |
| `GetVisibleInEditorLevelNames` | 获取编辑器中可见的关卡路径名列表 | `UUsdConversionBlueprintLibrary` |
| `GetActorsToConvert` | 获取需要转换导出的 Actor 集合 | `UUsdConversionBlueprintLibrary` |
| `RevertSequencerAnimations` | 导出前撤销 Sequencer 对关卡的动画影响 | `UUsdConversionBlueprintLibrary` |
| `ReapplySequencerAnimations` | 导出后恢复 Sequencer 的动画状态 | `UUsdConversionBlueprintLibrary` |
| `GenerateObjectVersionString` | 生成资产的唯一版本标识字符串，用于增量导出 | `UUsdConversionBlueprintLibrary` |
| `CanExportToLayer` | 检查是否可以向指定路径创建 USD Layer | `UUsdConversionBlueprintLibrary` |

#### 核心节点 — USD Layer 操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `MakePathRelativeToLayer` | 将绝对路径转为相对于锚定 Layer 的相对路径 | `UUsdConversionBlueprintLibrary` |
| `InsertSubLayer` | 向父 Layer 插入子 Layer 引用 | `UUsdConversionBlueprintLibrary` |
| `AddReference` | 为 Prim 添加 USD Reference 组合弧 | `UUsdConversionBlueprintLibrary` |
| `AddPayload` | 为 Prim 添加 USD Payload 组合弧 | `UUsdConversionBlueprintLibrary` |

#### 核心节点 — Prim 操作（剪贴板/复制/粘贴/删除）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `CutPrims` | 剪切 Prims 到剪贴板并删除原 Prim Spec | `UUsdConversionBlueprintLibrary` |
| `CopyPrims` | 复制 Prims 到剪贴板 | `UUsdConversionBlueprintLibrary` |
| `PastePrims` | 将剪贴板中的 Prims 粘贴为目标 Prim 的子级 | `UUsdConversionBlueprintLibrary` |
| `CanPastePrims` | 检查剪贴板中是否有可粘贴的 Prim | `UUsdConversionBlueprintLibrary` |
| `ClearPrimClipboard` | 清空 Prim 剪贴板 | `UUsdConversionBlueprintLibrary` |
| `DuplicatePrims` | 按指定方式复制 Prim（实例/引用/覆盖等） | `UUsdConversionBlueprintLibrary` |
| `RemoveAllPrimSpecs` | 从指定 Layer 移除 Prim 的所有 Spec（包括 Variant 内的） | `UUsdConversionBlueprintLibrary` |
| `GetPrimPathForObject` | 根据 UE Actor/Component 生成对应的 USD Prim 路径 | `UUsdConversionBlueprintLibrary` |
| `GetSchemaNameForComponent` | 获取 SceneComponent 对应的 USD Schema 名称 | `UUsdConversionBlueprintLibrary` |

#### 核心节点 — 植被导出

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetInstancedFoliageActorForLevel` | 获取指定关卡的 InstancedFoliageActor | `UUsdConversionBlueprintLibrary` |
| `GetUsedFoliageTypes` | 获取 FoliageActor 使用的所有 FoliageType 资产 | `UUsdConversionBlueprintLibrary` |
| `GetSource` | 获取 FoliageType 的源资产（如 UStaticMesh） | `UUsdConversionBlueprintLibrary` |
| `GetInstanceTransforms` | 获取特定 FoliageType 的所有实例变换 | `UUsdConversionBlueprintLibrary` |

#### 核心节点 — 元数据操作

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetUsdAssetUserData` | 获取对象上的 UsdAssetUserData | `UUsdConversionBlueprintLibrary` |
| `SetUsdAssetUserData` | 设置对象的 UsdAssetUserData | `UUsdConversionBlueprintLibrary` |
| `SetMetadataField` | 设置 USD 元数据键值对 | `UUsdConversionBlueprintLibrary` |
| `GetMetadataField` | 获取 USD 元数据值 | `UUsdConversionBlueprintLibrary` |
| `ClearMetadataField` | 清除指定元数据键 | `UUsdConversionBlueprintLibrary` |
| `HasMetadataField` | 检查是否存在指定元数据键 | `UUsdConversionBlueprintLibrary` |

#### 核心节点 — 导出唯一路径管理

| 节点 | 说明 | 所在类 |
|---|---|---|
| `BeginUniquePathScope` | 开始唯一路径作用域，之后生成的路径保证不重复 | `UUsdConversionBlueprintLibrary` |
| `EndUniquePathScope` | 结束唯一路径作用域并清理缓存 | `UUsdConversionBlueprintLibrary` |
| `GetUniqueFilePathForExport` | 获取全局唯一的导出文件路径 | `UUsdConversionBlueprintLibrary` |

#### 核心节点 — 分析指标

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAnalyticsAttributes` | 获取导出选项的分析属性 | `UUsdConversionBlueprintLibrary` |
| `SendAnalytics` | 发送分析事件 | `UUsdConversionBlueprintLibrary` |
| `BlockAnalyticsEvents` | 阻止分析事件发送 | `UUsdConversionBlueprintLibrary` |
| `ResumeAnalyticsEvents` | 恢复分析事件发送 | `UUsdConversionBlueprintLibrary` |

#### 核心节点 — 导出上下文（组件转换）

`UUsdConversionBlueprintContext` 是一个实例化对象，用于在蓝图/Python 中执行 UE 组件到 USD Prim 的转换。

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetStageRootLayer` | 打开或创建 USD Stage，设置根 Layer | `UUsdConversionBlueprintContext` |
| `GetStageRootLayer` | 获取当前 Stage 的根 Layer 路径 | `UUsdConversionBlueprintContext` |
| `SetEditTarget` | 设置当前编辑目标 Layer | `UUsdConversionBlueprintContext` |
| `Cleanup` | 释放 Stage 引用（脚本中必须调用） | `UUsdConversionBlueprintContext` |
| `ConvertLightComponent` | 将灯光组件转换为 USD Prim | `UUsdConversionBlueprintContext` |
| `ConvertDirectionalLightComponent` | 转换平行光 | `UUsdConversionBlueprintContext` |
| `ConvertRectLightComponent` | 转换矩形光 | `UUsdConversionBlueprintContext` |
| `ConvertPointLightComponent` | 转换点光源 | `UUsdConversionBlueprintContext` |
| `ConvertSkyLightComponent` | 转换天光 | `UUsdConversionBlueprintContext` |
| `ConvertSpotLightComponent` | 转换聚光灯 | `UUsdConversionBlueprintContext` |
| `ConvertDrawModeComponent` | 转换 USD 绘制模式组件 | `UUsdConversionBlueprintContext` |
| `ConvertAudioComponent` | 转换音频组件 | `UUsdConversionBlueprintContext` |
| `ConvertSceneComponent` | 转换场景组件（变换信息） | `UUsdConversionBlueprintContext` |
| `ConvertIsmComponent` | 转换实例化静态网格组件 | `UUsdConversionBlueprintContext` |
| `ConvertHismComponent` | 转换层次化实例静态网格组件 | `UUsdConversionBlueprintContext` |
| `ConvertMeshComponent` | 转换网格组件 | `UUsdConversionBlueprintContext` |
| `ConvertCineCameraComponent` | 转换电影摄像机组件 | `UUsdConversionBlueprintContext` |
| `ConvertInstancedFoliageActor` | 转换实例化植被 Actor | `UUsdConversionBlueprintContext` |
| `ConvertLandscapeProxyActorMesh` | 转换地形网格 | `UUsdConversionBlueprintContext` |
| `ConvertLandscapeProxyActorMaterial` | 转换地形材质（烘焙为纹理） | `UUsdConversionBlueprintContext` |
| `ConvertMaterialOverrides` | 为网格 Prim 设置材质覆盖 | `UUsdConversionBlueprintContext` |
| `AuthorUnrealMaterialBinding` | 为网格编写 Unreal 材质绑定 | `UUsdConversionBlueprintContext` |
| `ReplaceUnrealMaterialsWithBaked` | 将 Unreal 材质引用替换为烘焙后的 UsdPreviewSurface | `UUsdConversionBlueprintContext` |
| `SetPrimAssetInfo` | 设置 Prim 的 assetInfo 元数据 | `UUsdConversionBlueprintContext` |
| `GetPrimAssetInfo` | 获取 Prim 的 assetInfo 元数据 | `UUsdConversionBlueprintContext` |
| `SetPrimMetadata` | 设置 Prim 元数据 | `UUsdConversionBlueprintContext` |
| `GetPrimMetadata` | 获取 Prim 元数据 | `UUsdConversionBlueprintContext` |
| `GetUsdStageNumFrames` | 获取 Stage 的动画帧数 | `UUsdConversionBlueprintContext` |

#### Stringify / Unstringify 工具节点

`UUsdConversionBlueprintLibrary` 提供了大量类型转换工具函数，用于在蓝图/Python 中将 UE 类型转换为 USD 属性值的字符串表示，以及反向解析：

- **Stringify**：`StringifyAsBool`, `StringifyAsInt`, `StringifyAsFloat`, `StringifyAsDouble`, `StringifyAsString`, `StringifyAsToken`, `StringifyAsAssetPath`, `StringifyAsMatrix4d`, `StringifyAsQuatd`, `StringifyAsDouble3`, `StringifyAsFloat3` 等
- **Stringify 数组版**：`StringifyAsBoolArray`, `StringifyAsIntArray`, `StringifyAsFloatArray`, `StringifyAsStringArray` 等
- **Unstringify**：`UnstringifyAsBool`, `UnstringifyAsInt`, `UnstringifyAsFloat`, `UnstringifyAsDouble`, `UnstringifyAsString`, `UnstringifyAsToken` 等
- **Unstringify 数组版**：`UnstringifyAsBoolArray`, `UnstringifyAsIntArray`, `UnstringifyAsFloatArray` 等

#### 使用示例（蓝图描述）

**导出关卡到 USD 的基本蓝图流程**：

1. 创建 `UsdConversionBlueprintContext` 对象
2. 调用 `SetStageRootLayer` 打开目标 USD Stage
3. 调用 `SetEditTarget` 设置编辑目标 Layer
4. 获取需要转换的 Actor（`GetActorsToConvert`）
5. 对每个 Actor 的组件调用对应的 `Convert*Component` 函数
6. 调用 `Cleanup` 释放 Stage

**批量导出场景示例**：

1. 调用 `BeginUniquePathScope` 开始唯一路径管理
2. 调用 `StreamInRequiredLevels` 加载所有子关卡
3. 调用 `RevertSequencerAnimations` 撤销动画影响
4. 使用 `GetActorsToConvert` 获取导出对象列表
5. 循环调用各 `Convert*Component` 函数
6. 调用 `ReapplySequencerAnimations` 恢复动画
7. 调用 `StreamOutLevels` 卸载临时关卡
8. 调用 `EndUniquePathScope` 结束路径管理

### C++ 用法

#### 头文件引入

```cpp
#include "USDConversionBlueprintLibrary.h"
#include "USDConversionBlueprintContext.h"
#include "LevelExporterUSDOptions.h"
#include "USDAssetOptions.h"
```

#### 基本用法 — 检查导出可用性

```cpp
#include "StaticMeshExporterUSD.h"

// 检查 USD 功能是否可用（USD 运行时库是否正确加载）
bool bAvailable = UStaticMeshExporterUsd::IsUsdAvailable();
```

#### 基本用法 — 使用导出上下文转换组件

```cpp
#include "USDConversionBlueprintContext.h"

// 创建导出上下文
UUsdConversionBlueprintContext* Context = NewObject<UUsdConversionBlueprintContext>();

// 打开或创建 USD Stage
FFilePath StagePath;
StagePath.FilePath = TEXT("C:/Export/MyLevel.usda");
Context->SetStageRootLayer(StagePath);

// 设置编辑目标
FFilePath EditTarget;
EditTarget.FilePath = TEXT("C:/Export/MyLevel.usda");
Context->SetEditTarget(EditTarget);

// 转换一个点光源组件到指定 Prim 路径
UPointLightComponent* PointLight = /* 获取组件 */;
bool bSuccess = Context->ConvertPointLightComponent(PointLight, TEXT("/Root/Lights/PointLight01"));

// 转换一个网格组件
UMeshComponent* MeshComp = /* 获取组件 */;
bSuccess = Context->ConvertMeshComponent(MeshComp, TEXT("/Root/Geometry/Mesh01"));

// 使用默认时间码（省略 TimeCode 参数使用 Usd.TimeCode.Default()）
USceneComponent* SceneComp = /* 获取组件 */;
bSuccess = Context->ConvertSceneComponent(SceneComp, TEXT("/Root/Transform"));

// 完成后必须清理！
Context->Cleanup();
```

#### 基本用法 — 导出材质

```cpp
#include "MaterialExporterUSD.h"

// 导出单个材质为 UsdPreviewSurface
UMaterialInterface* Material = /* 获取材质 */;
FUsdMaterialBakingOptions BakeOptions;
BakeOptions.DefaultTextureSize = FIntPoint(512, 512);
BakeOptions.Properties = { MP_BaseColor, MP_Normal, MP_Roughness };

FUsdMetadataExportOptions MetadataOptions;
MetadataOptions.bExportAssetInfo = true;

FFilePath FilePath;
FilePath.FilePath = TEXT("C:/Export/Materials/Red.usda");

bool bSuccess = UMaterialExporterUsd::ExportMaterial(
    *Material,
    BakeOptions,
    MetadataOptions,
    FilePath,
    /* bReplaceIdentical = */ true,
    /* bReExportIdenticalAssets = */ false
);
```

#### 进阶用法 — 批量导出材质并替换引用

```cpp
#include "MaterialExporterUSD.h"

// 导出多个材质到 Stage 旁边，并自动替换 Stage 中的 unrealMaterial 引用
TArray<UMaterialInterface*> Materials = /* 收集材质 */;

FUsdMaterialBakingOptions BakeOptions;
FUsdMetadataExportOptions MetadataOptions;

FString StageRootLayerPath = TEXT("C:/Export/MyLevel.usda");

bool bSuccess = UMaterialExporterUsd::ExportMaterialsForStage(
    Materials,
    BakeOptions,
    MetadataOptions,
    StageRootLayerPath,
    /* bIsAssetLayer = */ false,  // false = 关卡导出
    /* bUsePayload = */ false,
    /* bReplaceIdentical = */ true
);
```

#### 进阶用法 — 完整关卡导出选项配置

```cpp
#include "LevelExporterUSDOptions.h"

ULevelExporterUSDOptions* Options = NewObject<ULevelExporterUSDOptions>();

// Stage 选项
Options->StageOptions.FileFormat = EUsdFileFormat::usda;
Options->StartTimeCode = 0.0f;
Options->EndTimeCode = 120.0f;

// 导出选项
Options->Inner.RootPrimName = TEXT("Root");
Options->Inner.bSelectionOnly = false;
Options->Inner.bExportActorFolders = true;
Options->Inner.bExportSublayers = true;
Options->Inner.LevelsToIgnore.Add(TEXT("Persistent Level"));

// 资产选项
Options->Inner.AssetFolder.Path = TEXT("C:/Export/Assets");
Options->Inner.AssetOptions.bUsePayload = true;
Options->Inner.AssetOptions.bBakeMaterials = true;
Options->Inner.AssetOptions.bExportStaticMeshSourceData = true;
Options->Inner.AssetOptions.LowestMeshLOD = 0;
Options->Inner.AssetOptions.HighestMeshLOD = 2;

// 材质烘焙选项
Options->Inner.AssetOptions.MaterialBakingOptions.DefaultTextureSize = FIntPoint(1024, 1024);

// 地形选项
Options->Inner.LowestLandscapeLOD = 0;
Options->Inner.HighestLandscapeLOD = 4;
Options->Inner.LandscapeBakeResolution = FIntPoint(2048, 2048);

// 元数据选项
Options->Inner.MetadataOptions.bExportAssetInfo = true;
Options->Inner.MetadataOptions.bExportAssetMetadata = true;
```

#### 进阶用法 — 设置和获取 Prim 元数据

```cpp
#include "USDConversionBlueprintLibrary.h"

// 获取对象上的 USD 用户数据
UObject* MeshObject = /* 获取资产对象 */;
UUsdAssetUserData* UserData = UUsdConversionBlueprintLibrary::GetUsdAssetUserData(MeshObject);

if (UserData)
{
    // 设置元数据字段
    UUsdConversionBlueprintLibrary::SetMetadataField(
        UserData,
        TEXT("custom:author"),
        TEXT("John Doe"),
        TEXT("string"),
        TEXT(""),  // 自动检测 StageIdentifier
        TEXT(""),  // 自动检测 PrimPath
        /* bTriggerPropertyChangeEvents = */ true
    );

    // 读取元数据字段
    FUsdMetadataValue Value = UUsdConversionBlueprintLibrary::GetMetadataField(
        UserData,
        TEXT("custom:author")
    );

    // 检查是否存在
    bool bHasField = UUsdConversionBlueprintLibrary::HasMetadataField(
        UserData,
        TEXT("custom:author")
    );

    // 清除字段
    UUsdConversionBlueprintLibrary::ClearMetadataField(
        UserData,
        TEXT("custom:author")
    );
}
```

#### 进阶用法 — Prim 剪贴板操作

```cpp
#include "USDConversionBlueprintLibrary.h"

FString StageRootLayer = TEXT("C:/Export/MyStage.usda");

// 复制 Prim
TArray<FString> PrimPaths = { TEXT("/Root/Props/Chair"), TEXT("/Root/Props/Table") };
bool bCopied = UUsdConversionBlueprintLibrary::CopyPrims(StageRootLayer, PrimPaths);

// 粘贴为子级
if (bCopied)
{
    TArray<FString> PastedPaths = UUsdConversionBlueprintLibrary::PastePrims(
        StageRootLayer,
        TEXT("/Root/Props/Duplicated")
    );
    // PastedPaths 包含粘贴后的实际路径（可能因重命名而不同）
}

// 剪切操作（复制 + 删除原 Prim）
TArray<FString> CutPaths = { TEXT("/Root/Old/Actor1") };
bool bCut = UUsdConversionBlueprintLibrary::CutPrims(StageRootLayer, CutPaths);

// 复制 Prim（实例化/引用等模式）
TArray<FString> DupPaths = UUsdConversionBlueprintLibrary::DuplicatePrims(
    StageRootLayer,
    { TEXT("/Root/Mesh") },
    EUsdDuplicateType::DuplicateAll,  // 完整复制
    TEXT("")
);
```

#### 进阶用法 — 独一无二的文件路径管理

```cpp
#include "USDConversionBlueprintLibrary.h"

// 开始唯一路径作用域（导出前调用一次）
UUsdConversionBlueprintLibrary::BeginUniquePathScope();

// 在作用域内，每次调用都会返回不同的路径
FString Path1 = UUsdConversionBlueprintLibrary::GetUniqueFilePathForExport(TEXT("C:/Export/Mesh.usda"));
// 返回: "C:/Export/Mesh.usda"

FString Path2 = UUsdConversionBlueprintLibrary::GetUniqueFilePathForExport(TEXT("C:/Export/Mesh.usda"));
// 返回: "C:/Export/Mesh_01.usda"（自动添加后缀避免重复）

FString Path3 = UUsdConversionBlueprintLibrary::GetUniqueFilePathForExport(TEXT("C:/Export/Mesh.usda"));
// 返回: "C:/Export/Mesh_02.usda"

// 作用域结束，清空缓存
UUsdConversionBlueprintLibrary::EndUniquePathScope();

// 之后再次调用可以重用路径
FString Path4 = UUsdConversionBlueprintLibrary::GetUniqueFilePathForExport(TEXT("C:/Export/Mesh.usda"));
// 返回: "C:/Export/Mesh.usda"（缓存已清空）
```

### Demo 示例

以下是一个最小化的 C++ 示例，演示如何使用 USDExporter 模块将 UE 组件导出到 USD Stage。

#### MyUsdExporter.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "USDConversionBlueprintContext.h"
#include "USDConversionBlueprintLibrary.h"

class FMyUsdExporter
{
public:
    /** 将指定世界中的所有 Actor 导出到 USD 文件 */
    static bool ExportWorldToUsd(UWorld* World, const FString& OutputPath);

    /** 将单个 Actor 转换到已打开的 Stage */
    static bool ExportActor(UUsdConversionBlueprintContext* Context, AActor* Actor, const FString& PrimPath);
};
```

#### MyUsdExporter.cpp

```cpp
#include "MyUsdExporter.h"
#include "USDConversionBlueprintContext.h"
#include "LevelExporterUSDOptions.h"

bool FMyUsdExporter::ExportWorldToUsd(UWorld* World, const FString& OutputPath)
{
    if (!World || OutputPath.IsEmpty())
    {
        return false;
    }

    // 创建导出上下文
    UUsdConversionBlueprintContext* Context = NewObject<UUsdConversionBlueprintContext>();

    // 打开 Stage
    FFilePath StagePath;
    StagePath.FilePath = OutputPath;
    Context->SetStageRootLayer(StagePath);
    Context->SetEditTarget(StagePath);

    // 获取需要导出的 Actor
    TSet<AActor*> Actors = UUsdConversionBlueprintLibrary::GetActorsToConvert(World);

    // 开始唯一路径作用域
    UUsdConversionBlueprintLibrary::BeginUniquePathScope();

    // 导出每个 Actor
    for (AActor* Actor : Actors)
    {
        if (!Actor)
        {
            continue;
        }

        FString PrimPath = UUsdConversionBlueprintLibrary::GetPrimPathForObject(
            Actor,
            TEXT("/Root"),
            /* bUseActorFolders = */ false,
            TEXT("Root")
        );

        ExportActor(Context, Actor, PrimPath);
    }

    // 结束唯一路径作用域
    UUsdConversionBlueprintLibrary::EndUniquePathScope();

    // 清理 Stage 引用
    Context->Cleanup();

    return true;
}

bool FMyUsdExporter::ExportActor(UUsdConversionBlueprintContext* Context, AActor* Actor, const FString& PrimPath)
{
    if (!Context || !Actor)
    {
        return false;
    }

    // 转换场景组件（根变换）
    USceneComponent* RootComp = Actor->GetRootComponent();
    if (RootComp)
    {
        Context->ConvertSceneComponent(RootComp, PrimPath);
    }

    // 转换所有子组件
    TArray<USceneComponent*> Components;
    RootComp->GetChildrenComponents(/* bIncludeAllDescendants = */ true, Components);

    for (USceneComponent* Comp : Components)
    {
        if (!Comp)
        {
            continue;
        }

        FString CompPrimPath = UUsdConversionBlueprintLibrary::GetPrimPathForObject(
            Comp,
            PrimPath,
            /* bUseActorFolders = */ false
        );

        // 根据组件类型选择转换函数
        if (UPointLightComponent* PointLight = Cast<UPointLightComponent>(Comp))
        {
            Context->ConvertPointLightComponent(PointLight, CompPrimPath);
        }
        else if (USpotLightComponent* SpotLight = Cast<USpotLightComponent>(Comp))
        {
            Context->ConvertSpotLightComponent(SpotLight, CompPrimPath);
        }
        else if (UDirectionalLightComponent* DirLight = Cast<UDirectionalLightComponent>(Comp))
        {
            Context->ConvertDirectionalLightComponent(DirLight, CompPrimPath);
        }
        else if (URectLightComponent* RectLight = Cast<URectLightComponent>(Comp))
        {
            Context->ConvertRectLightComponent(RectLight, CompPrimPath);
        }
        else if (USkyLightComponent* SkyLight = Cast<USkyLightComponent>(Comp))
        {
            Context->ConvertSkyLightComponent(SkyLight, CompPrimPath);
        }
        else if (UCineCameraComponent* CineCam = Cast<UCineCameraComponent>(Comp))
        {
            Context->ConvertCineCameraComponent(CineCam, CompPrimPath);
        }
        else if (UInstancedStaticMeshComponent* ISM = Cast<UInstancedStaticMeshComponent>(Comp))
        {
            Context->ConvertIsmComponent(ISM, CompPrimPath);
        }
        else if (UHierarchicalInstancedStaticMeshComponent* HISM = Cast<UHierarchicalInstancedStaticMeshComponent>(Comp))
        {
            Context->ConvertHismComponent(HISM, CompPrimPath);
        }
        else if (UMeshComponent* Mesh = Cast<UMeshComponent>(Comp))
        {
            Context->ConvertMeshComponent(Mesh, CompPrimPath);
        }
        else if (UAudioComponent* Audio = Cast<UAudioComponent>(Comp))
        {
            Context->ConvertAudioComponent(Audio, CompPrimPath);
        }
    }

    return true;
}
```

### 模块依赖

| 模块 | 用途 |
|---|---|
| `USDClasses` | USD 资产用户数据、Stage 选项等基础类型定义 |
| `USDUtilities` | USD 底层工具函数（Stage 管理、类型转换等） |
| `USDStage` | USD Stage 管理和 Prim 操作 |
| `Analytics` | 导出分析事件上报 |

### 维护状态

#### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的编译警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 新增支持指定不依赖蓝图的 Control Rig |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD values are being set | 修复升级到 26.03 后设置 LOD 值时 AnimQuery 内部引用失效的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数不匹配的问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 烘焙曝光动画轨道的所有帧 |

#### 维护评价

- **创建时间**：2018 年 11 月，已有约 8 年历史
- **近期活跃度**：**非常活跃**。2026 年 4-5 月有多次功能性更新，包括新的 Control Rig 支持、LOD 兼容性修复、动画烘焙改进等
- **成熟度**：尽管标记为 `IsBetaVersion: true` 且 `EnabledByDefault: false`，但该插件经过 8 年迭代，功能已经相当完善
- **已知限制**：作为实验性插件，可能在 USD 运行时版本升级时出现兼容性问题（如 26.03 升级导致的 AnimQuery 问题）
- **推荐程度**：**推荐使用**。该插件是 UE 与影视/动画行业 USD 工作流集成的官方方案，持续获得 Epic 的积极维护。如果你的项目涉及 DCC 工具交互或影视制作管线，这是必备插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)