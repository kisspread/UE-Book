# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD 相关资产） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

> ⚠️ **注意**：本插件默认未启用（`EnabledByDefault=false`）且标记为 Beta，需在项目设置中手动启用。需编译 USD SDK 支持（`USE_USD_SDK` 宏）。

---

## 用途

USD Importer 提供了 **Universal Scene Description (USD)** 与 Unreal Engine 之间的完整双向数据管线。它不仅是"导入器"——实际功能涵盖导入、导出和实时同步 USD 场景。

**核心架构**：插件采用 **Schema Translator（架构翻译器）** 模式，为每种 USD Schema 类型（Mesh、Material、Light、Camera、Skeleton、Groom 等）注册一个专用的 Translator 类。Translator 负责将 USD Prim 转换为 UE 的 Actor、Component 和 Asset。

**为什么要存在**：USD 是影视和视觉特效行业的标准场景描述格式（由 Pixar 开发）。随着 USD 在游戏行业（尤其是 MetaHuman、Nanite 工作流）的普及，UE 需要原生支持 USD 的读写，以实现与 DCC 工具（Maya、Houdini、Blender 等）的无缝资产交换。

**模块职责划分**：

| 模块 | 职责 |
|---|---|
| **USDSchemas** | Translator 架构核心——为每种 USD Schema 提供翻译器 |
| **USDStage** | USD Stage 管理、Stage Actor 和舞台级操作 |
| **USDStageImporter** | USD 文件的实际导入逻辑 |
| **USDStageEditor** | 编辑器 UI——USD Stage 的属性面板和操作界面 |
| **USDStageEditorViewModels** | 编辑器 UI 的 ViewModel 层 |
| **USDExporter** | 从 UE 导出为 USD 格式 |
| **GeometryCacheUSD** | GeometryCache 资产的 USD 支持 |
| **USDClassesEditor** | 编辑器专用的 USD 类和工具 |
| **USDTests** | 自动化测试 |

---

## 使用场景

- 你在使用 **MetaHuman / Houdini / Maya** 等 DCC 工具，需要将 USD 场景资产导入 UE → 使用 USD Stage Actor 导入 `.usd` / `.usda` / `.usdc` 文件
- 你需要在 UE 中**实时同步** USD 场景变更（Live Link 风格的 USD 工作流）→ 使用 USD Stage 的 Live 更新功能
- 你要将 UE 关卡**导出**为 USD 格式供影视渲染使用 → 使用 USDExporter 模块
- 你需要处理 USD 中的**骨骼动画、毛发（Groom）、几何缓存**等复杂数据 → 各专用 Translator 会自动处理
- 你要扩展 USD 导入管线，支持**自定义 USD Schema** → 注册自定义 SchemaTranslator

---

## USDSchemas 模块详解

USDSchemas 是整个插件的**翻译器核心**，定义了 USD Prim 到 UE 对象的转换规则。

### 翻译器继承体系

```
FUsdSchemaTranslator (基础接口)
├── FUsdGeomXformableTranslator (可变换的几何体基类)
│   ├── FUsdGeomMeshTranslator (网格 → StaticMesh)
│   │   └── FUsdGeometryCacheTranslator (几何缓存)
│   │       └── FUsdGroomTranslator (毛发)
│   ├── FUsdGeomCameraTranslator (摄像机)
│   ├── FUsdLuxLightTranslator (灯光)
│   ├── FUsdSkelSkeletonTranslator (骨骼)
│   ├── FUsdGeomPointInstancerTranslator (点实例化器)
│   ├── FUsdGeomPrimitiveTranslator (基础图元)
│   ├── FUsdVolVolumeTranslator (体积)
│   └── FUsdMediaSpatialAudioTranslator (空间音频)
├── FUsdShadeMaterialTranslator (材质)
│   └── FMaterialXUsdShadeMaterialTranslator (MaterialX 材质)
└── FUsdNaniteAssemblyTranslator (Nanite 装配)
```

### 核心翻译器功能表

| Translator | USD Schema | UE 对应 | 功能 |
|---|---|---|---|
| `FUsdGeomMeshTranslator` | UsdGeomMesh | StaticMesh + MeshComponent | 网格几何体转换，含 LOD 和材质分配 |
| `FUsdGeomXformableTranslator` | UsdGeomXformable | USceneComponent | 变换（位移/旋转/缩放）翻译 |
| `FUsdShadeMaterialTranslator` | UsdShadeMaterial | UMaterialInterface | 材质转换 |
| `FUsdGeomCameraTranslator` | UsdGeomCamera | UCameraComponent | 摄像机参数转换 |
| `FUsdLuxLightTranslator` | UsdLuxLight | ULightComponent | 灯光转换 |
| `FUsdSkelSkeletonTranslator` | UsdSkelSkeleton | USkeleton + UAnimSequence | 骨骼和动画转换 |
| `FUsdGeomPointInstancerTranslator` | UsdGeomPointInstancer | InstancedStaticMesh | 点实例化器转换 |
| `FUsdGroomTranslator` | Groom Schema | UGroomAsset | 毛发资产转换 |
| `FUsdGeometryCacheTranslator` | GeometryCache | UGeometryCache | 几何缓存动画转换 |
| `FUsdVolVolumeTranslator` | UsdVolVolume | Volume | OpenVDB 体积转换 |
| `FUsdMediaSpatialAudioTranslator` | MediaSpatialAudio | SpatialAudio | 空间音频转换 |
| `FUsdNaniteAssemblyTranslator` | Nanite Assembly | Nanite Mesh | Nanite 装配资产创建 |
| `FMaterialXUsdShadeMaterialTranslator` | MaterialX | UMaterialInterface | MaterialX 材质管线 |

---

## 蓝图用法

USDSchemas 模块本身**不暴露 BlueprintCallable API**——它是 C++ 翻译器架构层。蓝图层面的 USD 操作（导入文件、设置 Stage Actor 参数等）主要通过 **USDStage** 和 **USDStageImporter** 模块提供。

USD 工作流的蓝图交互通常通过以下方式：

### 核心节点（来自 USDStage/USDStageImporter 模块）

| 节点 | 说明 | 所在类 |
|---|---|---|
| USD Stage Actor 属性面板 | 通过 Details 面板设置 USD 文件路径和导入选项 | `AUsdStageActor` |
| 资产缓存设置 | 配置导入时的资产缓存策略 | `UUsdAssetCache3` |

> 💡 大多数 USD 工作流通过编辑器 UI（USD Stage 面板）完成，而非蓝图节点。

---

## C++ 用法

### 翻译器注册架构

USDSchemas 的核心使用模式是**注册自定义 Schema Translator**：

### 头文件引入

```cpp
#include "USDSchemasModule.h"
// 注意：部分头文件已迁移至 USDCore 插件的 USDUtilities 模块
// 新代码应使用：
// #include "Objects/USDSchemaTranslator.h"  // from USDUtilities
// #include "Objects/USDPrimLinkCache.h"     // from USDUtilities
```

### 基本用法：实现自定义 Translator

```cpp
// MyCustomTranslator.h
#pragma once
#include "USDGeomXformableTranslator.h"

class FMyCustomSchemaTranslator : public FUsdGeomXformableTranslator
{
public:
    using FUsdGeomXformableTranslator::FUsdGeomXformableTranslator;

    // 创建 UE 资产（StaticMesh、Material 等）
    virtual void CreateAssets() override;
    
    // 创建 UE 组件（MeshComponent、LightComponent 等）
    virtual USceneComponent* CreateComponents() override;
    
    // 更新已有组件的状态
    virtual void UpdateComponents(USceneComponent* SceneComponent) override;

    // 控制子 Prim 的折叠行为
    virtual bool CollapsesChildren(ECollapsingType CollapsingType) const override;
    virtual bool CanBeCollapsed(ECollapsingType CollapsingType) const override;

    // 收集需要额外处理的辅助 Prim
    virtual TSet<UE::FSdfPath> CollectAuxiliaryPrims() const override;
};
```

### 基本用法：材质分配解析

```cpp
// 源码来源: Private/MeshTranslationImpl.h
#include "MeshTranslationImpl.h"

// 解析 USD Prim 的材质分配信息，得到每个材质槽对应的 UMaterialInterface
TMap<const UsdUtils::FUsdPrimMaterialSlot*, UMaterialInterface*> ResolvedMaterials = 
    MeshTranslationImpl::ResolveMaterialAssignmentInfo(
        UsdPrim,                    // pxr::UsdPrim
        MaterialAssignmentInfo,     // TArray<FUsdPrimMaterialAssignmentInfo>
        AssetCache,                 // UUsdAssetCache3
        PrimLinkCache,              // FUsdPrimLinkCache
        RF_NoFlags,                 // EObjectFlags
        true                        // bShareAssetsForIdenticalPrims
    );
```

### 进阶用法：异步任务链构建静态网格

```cpp
// 源码来源: Public/USDGeomMeshTranslator.h
// USD 网格导入使用任务链（TaskChain）模式实现异步处理

class FBaseBuildStaticMeshTaskChain : public FUsdSchemaTranslatorTaskChain
{
protected:
    // 输入
    UE::FSdfPath PrimPath;
    TSharedRef<FUsdSchemaTranslationContext> Context;
    TArray<FMeshDescription> LODIndexToMeshDescription;

    // 输出
    UStaticMesh* StaticMesh = nullptr;

    // 重建期间阻止渲染使用旧网格
    TSharedPtr<FStaticMeshComponentRecreateRenderStateContext> RecreateRenderStateContextPtr;

protected:
    virtual void SetupTasks();
};
```

### 进阶用法：统计 Schema 使用情况

```cpp
// 源码来源: Public/USDSchemasModule.h
#include "USDSchemasModule.h"

// 收集场景中的 Schema 使用分析数据
// 统计自定义 schema、不支持的原生 schema、已注册的 schema translator 数量
UsdUnreal::Analytics::CollectSchemaAnalytics(
    Stage,              // const UE::FUsdStage&
    TEXT("OnImport")    // const FString& EventName
);
```

---

## Demo 示例

### 自定义 USD Schema Translator（最小示例）

```cpp
// MyCustomUSDTranslator.h
#pragma once

#if USE_USD_SDK

#include "USDGeomXformableTranslator.h"

/// 将自定义 USD Schema "MyApp:InteractivePrim" 翻译为 UE Actor
class FMyCustomUSDTranslator : public FUsdGeomXformableTranslator
{
public:
    using Super = FUsdGeomXformableTranslator;
    using FUsdGeomXformableTranslator::FUsdGeomXformableTranslator;

    virtual void CreateAssets() override;
    virtual USceneComponent* CreateComponents() override;
    virtual void UpdateComponents(USceneComponent* SceneComponent) override;
};

#endif // USE_USD_SDK
```

```cpp
// MyCustomUSDTranslator.cpp
#include "MyCustomUSDTranslator.h"

#if USE_USD_SDK

#include "Components/StaticMeshComponent.h"
#include "USDConversionUtils.h"
#include "UsdWrappers/UsdStage.h"

void FMyCustomUSDTranslator::CreateAssets()
{
    // 自定义资产创建逻辑
    // 例如：读取 USD Prim 上的自定义属性，创建对应的 UE 资产
    Super::CreateAssets();
}

USceneComponent* FMyCustomUSDTranslator::CreateComponents()
{
    // 使用基类的组件创建逻辑，自动处理 Xform 变换
    USceneComponent* Component = Super::CreateComponents();
    
    if (Component)
    {
        // 读取自定义 USD 属性并应用到组件
        UE::FUsdPrim Prim = Context->Stage.GetPrimAtPath(PrimPath);
        // ... 自定义逻辑
    }
    
    return Component;
}

void FMyCustomUSDTranslator::UpdateComponents(USceneComponent* SceneComponent)
{
    Super::UpdateComponents(SceneComponent);
    // 更新逻辑
}

#endif // USE_USD_SDK
```

---

## 模块依赖

从源码分析推断的依赖关系（USDSchemas 模块）：

| 模块 | 用途 |
|---|---|
| `USDCore` | USD SDK 封装（UsdWrappers）、InfoCache、PrimLinkCache 等核心工具 |
| `USDUtilities` | SchemaTranslator 基类、翻译工具函数（部分从 USDSchemas 迁移而来） |
| `HairStrandsCore` | Groom 毛发资产支持 |
| `GeometryCache` | 几何缓存资产支持 |
| `NaniteCore` / `MeshConversion` | Nanite 网格和网格转换 |

> ⚠️ 从 UE 5.6 起，`FUsdSchemaTranslatorRegistry`、`FUsdPrimLinkCache`、`FUsdInfoCache` 等核心类型已从 USDSchemas 迁移至 **USDCore** 插件的 **USDUtilities** 模块。USDSchemas 中的对应头文件已标记为 `UE_DEPRECATED`。

---

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度截断警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 支持独立于蓝图的 Control Rig 分配 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | 修复 26.03 更新导致 LOD 变体切换时动画查询失效 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符不匹配 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 修复曝光动画轨道仅烘培单帧的问题 |

### 维护评价

**✅ 活跃维护中**

- **年龄**：约 7 年（2018 年创建），属于核心基础设施类插件
- **更新频率**：近期（2026 年 4-5 月）有持续的功能增强和 Bug 修复，更新频率约每周 1-2 次
- **活跃度**：非常高——作为 MetaHuman、影视管线等关键工作流的核心依赖，Epic 持续投入开发
- **已知限制**：
  - 默认未启用（`EnabledByDefault=false`），需手动启用
  - 标记为 Beta（`IsBetaVersion=true`），API 可能变更
  - 需要编译 USD SDK 支持
  - 部分 API 从 UE 5.6 起已迁移至 USDUtilities 模块，旧头文件已废弃
- **推荐使用**：✅ 强烈推荐——这是 UE 中 USD 支持的唯一官方实现，活跃维护且功能持续完善

---

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [USDSchemas 模块源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDSchemas)
- [USDTests 测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)
- [Pixar USD 官方文档](https://openusd.org/release/index.html)