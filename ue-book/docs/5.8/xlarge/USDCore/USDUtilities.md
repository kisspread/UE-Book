# USD Core

> Adds support for USD SDK, UE wrapper classes and USD conversion utilities

| 属性 | 值 |
|---|---|
| 中文名 | USD 核心 |
| 分类 | Other |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD SDK 库、蓝图资产） |
| 模块 | `UnrealUSDWrapper` (Runtime), `USDClasses` (Runtime), `USDUtilities` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-05-16 |
| 年龄标签 | 🆕（约 2 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/USDCore) | |

## 用途

USDCore 是 Unreal Engine 5 中 USD（Universal Scene Description）集成的基础设施插件。它为 UE 提供了以下核心能力：

1. **USD SDK 封装**：通过 `UnrealUSDWrapper` 模块封装了 Pixar 的 OpenUSD C++ SDK，提供 `pxr::` 命名空间中类型的 UE 友好包装器（如 `UE::FUsdStage`、`UE::FUsdPrim`、`UE::FSdfLayer` 等），使得其他 UE 模块可以在不直接暴露 USD SDK 头文件的情况下操作 USD 数据。

2. **双向类型转换**：提供 USD 原生类型（向量、矩阵、四元数、颜色）与 UE 类型之间的坐标空间转换，自动处理 Z-Up/Y-Up 左右手坐标系差异和单位换算（metersPerUnit）。

3. **资产转换管线**：包含将 USD 几何体（Mesh、PointInstancer、SkelRoot）、材质（UsdShadeMaterial/UsdPreviewSurface）、灯光（UsdLux 系列）、相机、动画、骨骼/蒙皮数据、Groom 毛发、稀疏体积纹理（Sparse Volume Texture）、Nanite 组装体等转换为对应 UE 资产和组件的完整工具链。

4. **可扩展的 Schema Translator 系统**：通过 `FUsdSchemaTranslatorRegistry` 提供注册机制，允许下游插件（如 USDStage、InterchangeUSD）注册自定义的 USD Schema 翻译器，从而在不修改核心代码的情况下支持新 USD Schema。

5. **USD 元数据/图层操作**：提供图层管理（子图层插入、引用/Payload 添加）、USDZ 解压、属性静默（Mute）、可见性控制、Prim 合并/折叠策略管理等底层操作工具。

**为什么存在**：此插件是 2024 年从原有的分散式 USD 代码中提取并集中管理的结果（CL 33697004），目的是将 USD SDK 集成和转换工具作为独立可维护的基础模块，供 USDStageActor、InterchangeUSD 等上层插件依赖。

## 使用场景

- 你正在构建影视/VFX 制作管线，需要在 UE 中加载和操作 USD 场景 → 用 USDCore 作为底层依赖
- 你需要将 USD Mesh 转换为 UE 的 FMeshDescription/UStaticMesh → 使用 `USDUtilities` 模块的转换函数
- 你需要为自定义 USD Schema 编写 UE 翻译器（如某个 DCC 工具导出的私有 Schema）→ 注册 `FUsdSchemaTranslator`
- 你需要在 C++ 中操作 USD Stage 的图层结构（添加引用、Payload、子图层）→ 使用 `USDLayerUtils`
- 你需要将 USD 材质（UsdPreviewSurface）转换为 UE 材质实例 → 使用 `USDShadeConversion`
- 你需要处理 USD 动画数据（骨骼动画、BlendShape 变形）→ 使用 `USDSkeletalDataConversion`

## 蓝图用法

USDCore 本身主要是 C++ 模块，提供的大部分 API 是底层的转换工具函数。其主要消费方是 USDStage 和 InterchangeUSD 等插件。USDUtilities 模块中没有 `UFUNCTION(BlueprintCallable)` 标记的公开蓝图节点——所有核心转换函数都是纯 C++ 函数（通过 `USDUTILITIES_API` 导出），不直接暴露给蓝图。

如果你需要在蓝图中使用 USD 功能，应该使用 **USDStage** 插件提供的 `AUsdStageActor` 和相关蓝图接口，它建立在 USDCore 之上。

## C++ 用法

### 头文件引入

```cpp
// 类型转换
#include "USDTypesConversion.h"

// 几何体/网格转换
#include "USDGeomMeshConversion.h"

// 材质转换
#include "USDShadeConversion.h"

// Prim/组件转换
#include "USDPrimConversion.h"

// 灯光转换
#include "USDLightConversion.h"

// 骨骼/动画数据
#include "USDSkeletalDataConversion.h"

// 通用转换工具
#include "USDConversionUtils.h"

// 图层操作
#include "USDLayerUtils.h"

// 值序列化
#include "USDValueConversion.h"

// Schema Translator 注册
#include "Objects/USDSchemaTranslator.h"

// 错误/日志
#include "USDErrorUtils.h"
```

### 基本用法

**1. 坐标空间转换**

```cpp
// 来源: Public/USDTypesConversion.h
#include "USDTypesConversion.h"

// 获取 Stage 的轴向和单位信息
FUsdStageInfo StageInfo(UsdStage);
// StageInfo.UpAxis == EUsdUpAxis::YAxis (默认 USD 是 Y-Up)
// StageInfo.MetersPerUnit == 0.01 (默认 1 unit = 1cm)

// USD 空间的 FVector → UE 空间的 FVector
pxr::GfVec3f UsdPosition(1.0f, 2.0f, 3.0f);
FVector UEPosition = UsdToUnreal::ConvertVector(StageInfo, UsdPosition);

// UE 空间的 FTransform → USD 空间的变换矩阵
FTransform UETransform(FRotator(0, 90, 0), FVector(100, 200, 300));
pxr::GfMatrix4d UsdMatrix = UnrealToUsd::ConvertTransform(StageInfo, UETransform);

// 距离单位转换（UE cm → USD units）
float UEDistance = 100.0f; // cm
float UsdDistance = UnrealToUsd::ConvertDistance(StageInfo, UEDistance);
```

**2. 几何网格转换**

```cpp
// 来源: Public/USDGeomMeshConversion.h
#include "USDGeomMeshConversion.h"

// USD Mesh → FMeshDescription
FMeshDescription MeshDescription;
UsdUtils::FUsdPrimMaterialAssignmentInfo MaterialAssignments;
UsdToUnreal::FUsdMeshConversionOptions Options;
Options.TimeCode = pxr::UsdTimeCode::Default();
Options.PurposesToLoad = EUsdPurpose::Render;

bool bSuccess = UsdToUnreal::ConvertGeomMesh(
    UsdGeomMesh,        // pxr::UsdGeomMesh
    MeshDescription,
    MaterialAssignments,
    Options
);

// 合并子树中的所有 Mesh 到单个 MeshDescription
FMeshDescription CombinedMesh;
UsdUtils::FUsdPrimMaterialAssignmentInfo CombinedMats;
bool bSubtreeSuccess = UsdToUnreal::ConvertGeomMeshSubtree(
    SubtreeRootPrim,
    CombinedMesh,
    CombinedMats,
    Options,
    false,  // bSkipRootPrimTransform
    false   // bSkipRootPrimVisibility
);

// 导出 UE StaticMesh → USD
pxr::UsdPrim UsdMeshPrim = Stage->DefinePrim(...);
bool bExported = UnrealToUsd::ConvertStaticMesh(
    StaticMesh,
    UsdMeshPrim,
    pxr::UsdTimeCode::Default(),
    &MaterialStage,
    0,      // LowestMeshLOD
    INT32_MAX  // HighestMeshLOD
);
```

**3. 材质转换**

```cpp
// 来源: Public/USDShadeConversion.h
#include "USDShadeConversion.h"

// UsdShadeMaterial → UE MaterialInstance
UMaterialInstance* MaterialInstance = /* ... */;
UUsdAssetCache3* TextureCache = /* ... */;

bool bConverted = UsdToUnreal::ConvertMaterial(
    UsdShadeMaterial,
    *MaterialInstance,
    TextureCache,
    TEXT("universalRenderContext"),
    true  // bShareAssetsForIdenticalPrims
);

// 提取 UsdPreviewSurface 数据到中间结构（不依赖 UObject）
UsdToUnreal::FUsdPreviewSurfaceMaterialData MaterialData;
bool bExtracted = UsdToUnreal::ConvertMaterial(
    UsdShadeMaterialPrim,
    MaterialData,
    TEXT("unreal")
);
```

**4. 灯光转换**

```cpp
// 来源: Public/USDLightConversion.h
#include "USDLightConversion.h"

// USD 球形光 → UE PointLightComponent
UPointLightComponent* PointLight = /* ... */;
bool bLightConverted = UsdToUnreal::ConvertSphereLight(
    Prim,  // pxr::UsdPrim with UsdLuxSphereLight
    *PointLight
);

// 计算聚光灯内外锥角
float ConeAngle = 30.0f;   // USD 度数
float ConeSoftness = 0.5f; // [0, 1]
float OuterConeAngle, InnerConeAngle;
UsdToUnreal::ConvertSpotLightConeAngles(ConeAngle, ConeSoftness, OuterConeAngle, InnerConeAngle);
```

### 进阶用法

**5. Schema Translator 注册（自定义 USD Schema 翻译器）**

```cpp
// 来源: Public/Objects/USDSchemaTranslator.h
#include "Objects/USDSchemaTranslator.h"

// 定义自定义 Schema Translator
class FMyCustomSchemaTranslator : public FUsdSchemaTranslator
{
public:
    using FUsdSchemaTranslator::FUsdSchemaTranslator;

    virtual void CreateAssets() override
    {
        // 根据 USD Prim 数据创建 UE 资产
    }

    virtual USceneComponent* CreateComponents() override
    {
        // 创建对应的 UE 组件
        return nullptr;
    }

    virtual void UpdateComponents(USceneComponent* SceneComponent) override
    {
        // 更新组件状态
    }
};

// 在模块启动时注册
FRegisteredSchemaTranslatorHandle Handle;

void FMyModule::StartupModule()
{
    Handle = FUsdSchemaTranslatorRegistry::Get().Register<FMyCustomSchemaTranslator>(
        TEXT("MyCustomSchema")
    );
}

void FMyModule::ShutdownModule()
{
    FUsdSchemaTranslatorRegistry::Get().Unregister(Handle);
}
```

**6. USD 动画数据转换**

```cpp
// 来源: Public/USDSkeletalDataConversion.h + Public/USDPrimConversion.h
#include "USDSkeletalDataConversion.h"
#include "USDPrimConversion.h"

// 骨架数据转换
UsdToUnreal::FUsdSkeletonData SkeletonData;
pxr::UsdSkelSkeletonQuery SkelQuery = /* ... */;
bool bSkelConverted = UsdToUnreal::ConvertSkeleton(SkelQuery, SkeletonData, true, true);

// BlendShape 解析
UsdUtils::FBlendShapeMap BlendShapes;
UsdToUnreal::ConvertBlendShape(BlendShapePrim, StageInfo, 0, UsedNames, BlendShapes);

// 蒙皮网格转换
FSkeletalMeshImportData SkelImportData;
UsdUtils::FUsdPrimMaterialAssignmentInfo SkelMaterialAssignments;
bool bSkinned = UsdToUnreal::ConvertSkinnedMesh(
    SkinningQuery,
    SkeletonQuery,
    SkelImportData,
    SkelMaterialAssignments
);

// 关键帧动画烘焙到 Sequencer
TArray<double> TimeSamples = /* ... */;
UMovieSceneFloatTrack* FloatTrack = /* ... */;
auto ReaderFunc = [](double TimeCode) -> float { /* 采样属性 */ };
UsdToUnreal::ConvertFloatTimeSamples(Stage, TimeSamples, ReaderFunc, FloatTrack, SequenceTransform);
```

**7. USD 图层与引用操作**

```cpp
// 来源: Public/USDLayerUtils.h
#include "USDLayerUtils.h"

// 插入子图层
pxr::SdfLayerRefPtr ParentLayer = Stage->GetRootLayer();
bool bInserted = UsdUtils::InsertSubLayer(ParentLayer, TEXT("/path/to/sublayer.usda"), 0);

// 添加引用
UE::FUsdPrim Prim = Stage->GetPrimAtPath(UE::FSdfPath(TEXT("/Root/Object")));
UsdUtils::AddReference(Prim, TEXT("/path/to/asset.usd"));

// 添加 Payload
UsdUtils::AddPayload(Prim, TEXT("/path/to/heavy_asset.usd"));

// USDZ 解压
FString OutputDir, RootLayer;
UsdUtils::EUSDZDecompressResult Result = UsdUtils::DecompressUSDZFile(
    TEXT("/path/to/scene.usdz"),
    TEXT("/output/dir"),
    &RootLayer
);

// 属性静默/取消静默
UE::FUsdAttribute Attr = Prim.GetAttribute(TEXT("xformOp:translate"));
UsdUtils::MuteAttribute(Attr, Stage);      // 导入时忽略此属性的动画
UsdUtils::UnmuteAttribute(Attr, Stage);    // 恢复动画
bool bMuted = UsdUtils::IsAttributeMuted(Attr, Stage);
```

**8. Nanite 组装体转换**

```cpp
// 来源: Public/USDNaniteAssemblyUtils.h
#include "USDNaniteAssemblyUtils.h"

// 检测 Nanite 组装体类型
UsdToUnreal::NaniteAssemblyUtils::ENaniteAssemblyMeshType MeshType =
    UsdToUnreal::NaniteAssemblyUtils::GetNaniteAssemblyMeshType(AssemblyRootPrim);

if (MeshType == UsdToUnreal::NaniteAssemblyUtils::ENaniteAssemblyMeshType::StaticMesh)
{
    // 构建遍历结果
    UsdToUnreal::NaniteAssemblyUtils::FNaniteAssemblyTraversalResult Result(
        MeshType, AssemblyRootPrim.GetPrimPath()
    );
    // ... 收集 mesh entries ...

    // 获取 PointInstancer 实例数据
    UsdToUnreal::NaniteAssemblyUtils::FNaniteAssemblyPointInstancerData PIData =
        UsdToUnreal::NaniteAssemblyUtils::GetPointInstancerData(
            PointInstancerPrim, Options, Result, SkelIdentifier, JointNames, PartIndexOffset
        );
}
```

## Demo 示例

以下示例演示如何使用 USDCore 的转换工具将一个 USD Mesh prim 转换为 UE 的 MeshDescription 并创建 StaticMesh：

```cpp
// MyUsdMeshConverter.h
#pragma once

#include "CoreMinimal.h"

class pxr::UsdStage;
template<typename T> class pxr::TfRefPtr;
using UsdStageRefPtr = pxr::TfRefPtr<pxr::UsdStage>;

class UStaticMesh;

class FMyUsdMeshConverter
{
public:
    /** 从 USD 文件加载 Stage 并转换第一个 Mesh prim 为 UStaticMesh */
    static UStaticMesh* ConvertFirstMeshFromUsdFile(
        const FString& UsdFilePath,
        UObject* InOuter,
        const FString& AssetName
    );
};
```

```cpp
// MyUsdMeshConverter.cpp
#include "MyUsdMeshConverter.h"

#include "USDGeomMeshConversion.h"
#include "USDConversionUtils.h"
#include "USDTypesConversion.h"
#include "Objects/USDInfoCache.h"

#include "Engine/StaticMesh.h"
#include "MeshDescription.h"
#include "StaticMeshAttributes.h"

#include "USD/USDIncludesStart.h"
#include "pxr/usd/usd/stage.h"
#include "pxr/usd/usdGeom/mesh.h"
#include "USD/USDIncludesEnd.h"

UStaticMesh* FMyUsdMeshConverter::ConvertFirstMeshFromUsdFile(
    const FString& UsdFilePath,
    UObject* InOuter,
    const FString& AssetName)
{
    // 1. 打开 USD Stage
    pxr::UsdStageRefPtr Stage = pxr::UsdStage::Open(TCHAR_TO_UTF8(*UsdFilePath));
    if (!Stage)
    {
        return nullptr;
    }

    // 2. 收集 Stage 信息（轴向、单位）
    FUsdStageInfo StageInfo(Stage);

    // 3. 查找第一个 GeomMesh
    pxr::UsdPrim MeshPrim;
    auto Range = Stage->Traverse();
    for (auto It = Range.begin(); It != Range.end(); ++It)
    {
        pxr::UsdGeomMesh GeomMesh(*It);
        if (GeomMesh)
        {
            MeshPrim = *It;
            break;
        }
    }

    if (!MeshPrim)
    {
        return nullptr;
    }

    // 4. 配置转换选项
    UsdToUnreal::FUsdMeshConversionOptions Options;
    Options.TimeCode = pxr::UsdTimeCode::Default();
    Options.PurposesToLoad = EUsdPurpose::Render;
    Options.bMergeIdenticalMaterialSlots = true;
    Options.SubdivisionLevel = 0;

    // 5. 执行转换
    FMeshDescription MeshDescription;
    FStaticMeshAttributes(MeshDescription).Register();
    UsdUtils::FUsdPrimMaterialAssignmentInfo MaterialAssignments;

    pxr::UsdGeomMesh GeomMesh(MeshPrim);
    bool bSuccess = UsdToUnreal::ConvertGeomMesh(
        GeomMesh,
        MeshDescription,
        MaterialAssignments,
        Options
    );

    if (!bSuccess || MeshDescription.VerticesNum() == 0)
    {
        return nullptr;
    }

    // 6. 创建 UStaticMesh 并填入数据
    UStaticMesh* StaticMesh = NewObject<UStaticMesh>(InOuter, FName(*AssetName), RF_Public | RF_Standalone);
    FStaticMeshSourceModel& SourceModel = StaticMesh->AddSourceModel();
    SourceModel.MeshDescription = MakeUnique<FMeshDescription>(MoveTemp(MeshDescription));
    StaticMesh->CommitMeshDescription(0);

    return StaticMesh;
}
```

## 模块依赖

USDCore 插件的模块依赖关系如下：

```
UnrealUSDWrapper (Runtime) ← 封装 USD SDK，依赖 Python3
       ↑
USDClasses (Runtime) ← UE 包装器类型（FUsdStage, FUsdPrim 等）
       ↑
USDUtilities (Runtime) ← 转换工具函数
```

你的项目模块如果要使用 USDCore 的 API，需要在 Build.cs 中添加：

| 模块 | 用途 |
|---|---|
| `USDUtilities` | 核心转换工具、Schema Translator、图层操作、日志系统 |
| `USDClasses` | USD 对象的 UE 包装器类型（FUsdStage, FUsdPrim, FSdfLayer 等） |
| `UnrealUSDWrapper` | 底层 USD SDK 封装（通常不需要直接依赖） |

标准 Core/Engine/Slate 依赖已被省略。**注意**：`EnabledByDefault = false`，你需要在项目设置或 .uproject 中手动启用此插件。由于 `IsBetaVersion = true`，API 可能在未来版本中发生变化。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-14 | `561d9c2d` | USD Pregen: Fix materials inside instances not being deduplicated | 修复实例内材质未被去重的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |
| 2026-04-28 | `808cb4e5` | Fixed scoped enums that are used in formatting functions that can cause garbage output | 修复格式化函数中作用域枚举导致的乱码输出 |
| 2026-04-28 | `5b5d2b22` | [USD] Harden USDZ extraction in InterchangeUSD against path traversal (Zip Slip) and unsafe archive | 加固 USDZ 解压防止路径穿越攻击（Zip Slip） |
| 2026-04-28 | `bf5d0e5b` | USD: Add Nanite/mesh build settings schemas | 添加 Nanite 和网格构建设置的 USD Schema 支持 |

### 维护评价

- **活跃维护**：最近 1 个月内有功能性更新和安全修复，处于积极开发中
- **创建时间**：2024-05-16（约 2 年前），从之前分散的 USD 代码中重组而来
- **更新频率**：高频更新，几乎每周都有改动，包括新功能（Nanite assembly schemas）、Bug 修复和安全加固
- **状态标记**：`IsBetaVersion = true`，表明 API 稳定性承诺较低，未来可能有 breaking changes
- **规模巨大**：1838 个源文件（其中大部分是 USD SDK 本身），是 UE 中最大的 Runtime 插件之一
- **推荐使用**：如果你的项目需要 USD 支持，这是必选的基础依赖。虽然是 Beta 状态，但由 Epic 直接维护，质量和稳定性有保障。注意需要手动启用（`EnabledByDefault = false`）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/USDCore)
- [官方文档](https://docs.unrealengine.com/5.8/en-US/working-with-usd-in-unreal-engine/)（UE USD 总体文档）
- [子模块文档 - USDUtilities](./USDUtilities.md)（转换工具详细文档）