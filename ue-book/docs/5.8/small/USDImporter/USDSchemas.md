# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（内容资产） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

> ⚠️ **注意**：此插件默认未启用（`EnabledByDefault: false`），且标记为 Beta。使用前需在项目设置中手动启用。

## 文档结构

本文档为 USD Importer 插件的汇总页。该插件包含 187 个源文件，属于大型插件，建议结合子模块文档阅读。

| 子模块 | 说明 |
|---|---|
| [USDSchemas](USDSchemas.md) | USD Schema 翻译器注册表与核心翻译器实现（详细文档） |
| USDExporter | USD 导出功能 |
| USDStage | USD Stage 的运行时表示与管理 |
| USDStageImporter | USD Stage 的导入流程 |
| USDStageEditor | USD Stage 编辑器面板 |
| USDStageEditorViewModels | Stage 编辑器的视图模型层 |
| USDClassesEditor | USD 相关编辑器类 |
| GeometryCacheUSD | 几何缓存与 USD 的桥接 |
| USDTests | 自动化测试 |

## 用途

USD（Universal Scene Description）是由 Pixar 开发的开放标准场景描述格式，广泛用于影视和游戏行业的资产管线中。这个插件为 Unreal Engine 提供了完整的 USD 导入管线，能够将 USD 文件中的 Prim（场景图节点）自动翻译为 Unreal Engine 中对应的资产（StaticMesh、材质、骨骼等）和组件（SceneComponent、MeshComponent、LightComponent 等）。

插件的核心架构是 **Schema Translator 模式**：每种 USD Schema 类型（如 UsdGeomMesh、UsdGeomCamera、UsdLuxLight）都有对应的 Translator 类，负责将该类型的 Prim 创建/更新为 UE 中的对应资产和组件。插件内置了对大量 USD Schema 的支持，包括：

- **几何体**：Mesh → StaticMesh，PointInstancer → 合并网格，GeomPrimitive（BasisCurves 等）
- **动画**：SkelSkeleton → 骨骼/动画，GeometryCache
- **材质**：UsdShadeMaterial → UMaterialInterface，支持 MaterialX
- **光照**：UsdLuxLight → UE 光源组件
- **摄像机**：UsdGeomCamera → UCameraComponent
- **毛发**：Groom（基于 GeometryCacheTranslator 扩展）
- **体积**：OpenVDB 体积
- **空间音频**：UsdMediaSpatialAudio
- **Nanite 组装**：NaniteAssembly

## 使用场景

- 你的资产管线使用 USD 格式（如从 Maya、Houdini、Blender 导出 USD）→ 用此插件将 USD 文件导入 UE
- 你需要在 UE 中实时查看/编辑 USD Stage（类似 USDView）→ 使用 USDStage 编辑器面板
- 你需要将 UE 场景导出为 USD 格式供其他 DCC 工具使用 → 使用 USDExporter 模块
- 你在做虚拟制片（Virtual Production）且需要导入 USD 场景 → 启用此插件
- 你需要自定义 USD Schema 到 UE 资产的映射关系 → 通过 `FUsdSchemaTranslatorRegistry` 注册自定义 Translator

## 蓝图用法

USDSchemas 模块主要面向 C++ 扩展，提供的公开 API 集中在 Schema Translator 注册系统中。以下是关键蓝图/C++ 扩展点：

### 核心类

| 类 | 说明 |
|---|---|
| `FUsdSchemaTranslator` | 所有 Translator 的基类，定义了 CreateAssets / CreateComponents / UpdateComponents 接口 |
| `FUsdGeomXformableTranslator` | 所有可变换（Xformable）Prim 的 Translator 基类 |
| `FUsdGeomMeshTranslator` | UsdGeomMesh → StaticMesh 的翻译器 |
| `FUsdGeomCameraTranslator` | UsdGeomCamera → CameraComponent 的翻译器 |
| `FUsdLuxLightTranslator` | UsdLuxLight → 光源组件的翻译器 |
| `FUsdShadeMaterialTranslator` | UsdShadeMaterial → UMaterialInterface 的翻译器 |
| `FUsdSkelSkeletonTranslator` | UsdSkelSkeleton → 骨骼/动画资产的翻译器 |
| `FUsdGeomPointInstancerTranslator` | UsdGeomPointInstancer → 实例化网格的翻译器 |
| `FUsdGeometryCacheTranslator` | UsdGeomMesh → GeometryCache 的翻译器 |
| `FUsdGroomTranslator` | UsdGeomMesh → Groom 资产的翻译器 |

### Translator 层次结构

```
FUsdSchemaTranslator
├── FUsdGeomXformableTranslator
│   ├── FUsdGeomMeshTranslator
│   │   ├── FUsdGeometryCacheTranslator
│   │   │   └── FUsdGroomTranslator
│   │   ├── FBuildStaticMeshTaskChain
│   │   │   ├── FGeomMeshCreateAssetsTaskChain
│   │   │   └── FUsdGeomPointInstancerCreateAssetsTaskChain
│   │   └── FBaseBuildStaticMeshTaskChain
│   ├── FUsdGeomCameraTranslator
│   ├── FUsdLuxLightTranslator
│   ├── FUsdGeomPrimitiveTranslator
│   ├── FUsdSkelSkeletonTranslator
│   ├── FUsdGeomPointInstancerTranslator
│   ├── FUsdMediaSpatialAudioTranslator
│   └── FUsdVolVolumeTranslator
├── FUsdShadeMaterialTranslator
│   └── FMaterialXUsdShadeMaterialTranslator
└── FUsdNaniteAssemblyTranslator
```

## C++ 用法

### 头文件引入

```cpp
// Schema Translator 基类与注册（已迁移到 USDUtilities，兼容头文件仍可用）
#include "USDSchemasModule.h"

// 各类型 Translator
#include "USDGeomMeshTranslator.h"
#include "USDGeomXformableTranslator.h"
#include "USDShadeMaterialTranslator.h"
```

### 注册自定义 Schema Translator

USDSchemas 模块的核心扩展能力是通过 `FUsdSchemaTranslatorRegistry` 注册自定义 Translator。以下是注册自定义 Translator 的模式：

```cpp
// 基于 USDSchemas/Public/USDGeomMeshTranslator.h 和模块接口推断的用法
#include "Objects/USDSchemaTranslator.h"  // 新的推荐路径（5.6+）
#include "USDSchemasModule.h"

// 获取 Translator 注册表（5.6+ 推荐方式）
FUsdSchemaTranslatorRegistry& Registry = FUsdSchemaTranslatorRegistry::Get();
```

### 创建自定义 Translator

以下是基于 `FUsdGeomMeshTranslator` 源码推断的自定义 Translator 模式：

```cpp
// 参考: USDSchemas/Public/USDGeomMeshTranslator.h
#if USE_USD_SDK

#include "USDGeomXformableTranslator.h"

class FMyCustomMeshTranslator : public FUsdGeomMeshTranslator
{
public:
    using Super = FUsdGeomMeshTranslator;
    using FUsdGeomMeshTranslator::FUsdGeomMeshTranslator;

    // 禁用拷贝
    FMyCustomMeshTranslator(const FMyCustomMeshTranslator&) = delete;
    FMyCustomMeshTranslator& operator=(const FMyCustomMeshTranslator&) = delete;

    // 重写核心翻译逻辑
    virtual void CreateAssets() override;
    virtual USceneComponent* CreateComponents() override;
    virtual void UpdateComponents(USceneComponent* SceneComponent) override;

    // 控制折叠行为（决定子 Prim 是否由本 Translator 统一处理）
    virtual bool CollapsesChildren(ECollapsingType CollapsingType) const override;
    virtual bool CanBeCollapsed(ECollapsingType CollapsingType) const override;
};

#endif // USE_USD_SDK
```

### 材质分配解析

以下代码展示了 USD 中材质绑定如何被解析为 UE 材质（来自 `Private/MeshTranslationImpl.h`）：

```cpp
// 参考: USDSchemas/Private/MeshTranslationImpl.h
#include "MeshTranslationImpl.h"

// 解析 USD Prim 的材质分配信息，返回每个材质槽对应的 UMaterialInterface
TMap<const UsdUtils::FUsdPrimMaterialSlot*, UMaterialInterface*> ResolvedMaterials =
    MeshTranslationImpl::ResolveMaterialAssignmentInfo(
        UsdPrim,           // USD Prim
        AssignmentInfo,    // 材质分配信息数组
        AssetCache,        // USD 资产缓存
        PrimLinkCache,     // Prim 到资产的链接缓存
        ObjectFlags,       // 资产标志
        bShareAssets       // 是否为相同 Prim 共享资产
    );
```

### Groom 绑定创建

```cpp
// 参考: USDSchemas/Private/USDGroomTranslatorUtils.h
#include "USDGroomTranslatorUtils.h"

// 为带有 GroomBindingAPI 的 Prim 创建 Groom 绑定资产
UsdGroomTranslatorUtils::CreateGroomBindingAsset(
    Prim,
    AssetCache,
    PrimLinkCache,
    ObjectFlags,
    bShareAssetsForIdenticalPrims
);

// 将 Groom 资产设置到场景组件上
UsdGroomTranslatorUtils::SetGroomFromPrim(
    Prim,
    PrimLinkCache,
    SceneComponent
);
```

### 架构分析

Translator 的生命周期遵循以下阶段（从源码中 `CreateAssets` / `CreateComponents` / `UpdateComponents` 推断）：

1. **CreateAssets()** — 创建引擎资产（StaticMesh、材质、动画等），通常通过异步任务链执行
2. **CreateComponents()** — 创建场景组件（返回 `USceneComponent*`）
3. **UpdateComponents()** — 更新已有组件的状态

任务链模式（Task Chain）用于处理复杂的异步资产构建，例如 `FBuildStaticMeshTaskChain` 会：
- 解析 Mesh LOD 描述
- 收集材质信息
- 构建 StaticMesh 资产
- 防止重建期间的渲染冲突（通过 `FStaticMeshComponentRecreateRenderStateContext`）

## 模块依赖

USD Importer 的各模块依赖以下非标准模块（基于源码文件和模块关系推断）：

| 模块 | 用途 |
|---|---|
| `USDCore` | UE 的 USD SDK 封装层（提供 `UE::FUsdStage`、`UE::FSdfPath` 等类型） |
| `USDUtilities` | USD 工具函数，包含 `FUsdSchemaTranslatorRegistry`、`FUsdPrimLinkCache`、`FUsdInfoCache` 等（5.6+ 核心迁移目标） |
| `USDClasses` | USD 相关的 UObject 类定义 |
| `GeometryCache` | 几何缓存系统（GeometryCacheTranslator 依赖） |
| `Groom` | Groom（毛发）资产系统（GroomTranslator 依赖） |
| `InterchangeCore` | Interchange 框架（USDStageImporter 依赖） |
| `MeshDescription` | Mesh 描述数据结构 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下双精度常量截断为 float 的编译警告 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 支持分配独立于蓝图的 Control Rig |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | 修复 USD 26.03 更新导致 LOD 变体切换时 AnimQuery 内部引用失效的问题 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复 32/64 位格式说明符与参数不匹配的问题 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 烘焙曝光动画轨道的所有帧 |

### 维护评价

**🟢 活跃维护中**

- **创建时间**：2018 年，约 7 年历史，是 UE 引擎中较成熟的插件之一
- **更新频率**：近期（2026 年 4-5 月）有多次实质性更新，包括功能增强（Control Rig 支持）、USD SDK 版本适配（26.03）和 bug 修复
- **模块成熟度**：尽管标记为 Beta，但已包含 9 个模块、187 个源文件，覆盖了 USD 导入/导出/编辑的完整管线
- **API 迁移**：5.6 版本后大量核心类（`FUsdSchemaTranslatorRegistry`、`FUsdPrimLinkCache`、`FUsdInfoCache`）已迁移到 `USDUtilities` 模块（USDCore 插件），旧头文件标记为 `UE_DEPRECATED`
- **已知限制**：`EnabledByDefault: false` 且 `IsBetaVersion: true`，但鉴于其规模和活跃度，实际功能已相当完整
- **推荐程度**：如果你的项目需要 USD 支持，强烈推荐启用。注意使用 5.6+ 版本的 API 路径（`USDUtilities` 模块）

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [USDSchemas 子模块文档](USDSchemas.md)

---

# USDSchemas

> USD Schema Translator 注册与核心翻译器实现模块

| 属性 | 值 |
|---|---|
| 模块名 | USDSchemas |
| 类型 | Runtime |
| 源文件数 | ~22（头文件可见） |
| 核心职责 | 将 USD Prim 类型映射为 UE 资产/组件 |

## 模块概述

USDSchemas 是 USD Importer 插件的核心模块之一，定义了 **Schema Translator 架构**——将 USD 文件中的各类 Prim 自动翻译为 Unreal Engine 对应资产和组件的机制。

### 核心概念

| 概念 | 说明 |
|---|---|
| **Schema Translator** | 将特定 USD Schema 类型翻译为 UE 资产/组件的类 |
| **Task Chain** | 异步资产构建任务链，用于复杂的多步骤资产创建 |
| **Collapsing** | 折叠机制，允许父 Translator 统一处理子树中的多个 Prim |
| **Translation Context** | 翻译上下文，包含 Stage、AssetCache、PrimLinkCache 等共享状态 |

## Translator 详解

### 基础层：FUsdSchemaTranslator → FUsdGeomXformableTranslator

`FUsdGeomXformableTranslator` 是所有可渲染（drawable）Prim 的 Translator 基类。除了标准的资产/组件创建，它还支持**替代绘制模式**（Alternative Draw Mode），包括 Bounds（边界框）和 Cards（贴图卡片）模式。

关键方法：

```cpp
// 核心接口
virtual void CreateAssets() override;
virtual USceneComponent* CreateComponents() override;
virtual void UpdateComponents(USceneComponent* SceneComponent) override;

// 扩展接口
USceneComponent* CreateComponentsEx(
    TOptional<TSubclassOf<USceneComponent>> ComponentType,
    TOptional<bool> bNeedsActor
);

// 替代绘制模式（Bounds/Cards）
USceneComponent* CreateAlternativeDrawModeComponents(EUsdDrawMode DrawMode);
void UpdateAlternativeDrawModeComponents(USceneComponent* SceneComponent, EUsdDrawMode DrawMode);
void CreateAlternativeDrawModeAssets(EUsdDrawMode DrawMode);
```

### 几何体翻译器

#### FUsdGeomMeshTranslator

最核心的 Translator，将 `UsdGeomMesh` 转换为 `UStaticMesh`。支持：

- 多 LOD 网格构建
- 材质分配与覆盖
- 元数据收集
- 蒙皮网格检测与跳过（避免与 `FUsdSkelSkeletonTranslator` 重复处理）
- 子树折叠控制

```cpp
// 蒙皮网格检测：避免与 SkeletonTranslator 重复
bool ShouldSkipSkinnablePrim(bool bCheckForComponent = false) const;

// 子树折叠
bool CollapsesChildren(ECollapsingType CollapsingType) const override;
bool CanBeCollapsed(ECollapsingType CollapsingType) const override;
```

#### FUsdGeomPointInstancerTranslator

将 `UsdGeomPointInstancer` 转换为实例化网格。Point Instancer 总是折叠其整个子树，嵌套情况下由最顶层的 PointInstancer 负责。

#### FUsdGeomPrimitiveTranslator

处理 `UsdGeomBasisCurves` 等几何图元类型。

#### FUsdGeomCameraTranslator

将 `UsdGeomCamera` 转换为 `UCameraComponent`。

### 材质翻译器

#### FUsdShadeMaterialTranslator

将 `UsdShadeMaterial` 转换为 `UMaterialInterface`。支持导入后自定义处理：

```cpp
virtual void PostImportMaterial(const FString& PrefixedMaterialHash, UMaterialInterface* ImportedMaterial);
```

#### FMaterialXUsdShadeMaterialTranslator

继承自 `FUsdShadeMaterialTranslator`，专门处理 MaterialX 格式的材质描述。

### 动画与骨骼翻译器

#### FUsdSkelSkeletonTranslator

将 `UsdSkelSkeleton` 转换为 UE 的骨骼和动画资产。注释中说明了从已废弃的 `SkelRootTranslator` 到基于 Skeleton 的架构迁移——SkeletonTranslator 能自行查找关联的蒙皮网格。

#### FUsdGeometryCacheTranslator

将 `UsdGeomMesh` 转换为 `GeometryCache` 资产（用于缓存的顶点动画）。

### 特殊用途翻译器

| Translator | USD Schema | UE 对应 |
|---|---|---|
| `FUsdLuxLightTranslator` | UsdLuxLight | UE 光源组件 |
| `FUsdGroomTranslator` | UsdGeomMesh (with Groom) | Groom 资产 + GroomComponent |
| `FUsdMediaSpatialAudioTranslator` | UsdMediaSpatialAudio | 空间音频组件 |
| `FUsdVolVolumeTranslator` | OpenVDB Volume | 体积组件 |
| `FUsdNaniteAssemblyTranslator` | Nanite Assembly | Nanite 组装资产（仅编辑器） |

### MeshTranslationImpl 工具命名空间

提供 Skeleton Translator 和 GeomMesh Translator 共享的实现：

```cpp
namespace MeshTranslationImpl
{
    // 解析材质分配
    TMap<const UsdUtils::FUsdPrimMaterialSlot*, UMaterialInterface*> ResolveMaterialAssignmentInfo(...);

    // 设置材质覆盖（注意：非线程安全，会临时切换 LOD 变体）
    void SetMaterialOverrides(...);

    // 记录材质槽的源 Prim 信息
    void RecordSourcePrimsForMaterialSlots(...);
}
```

## 废弃的 API

以下头文件在 5.6+ 版本中已标记为废弃，使用请迁移到 `USDUtilities` 模块：

| 旧路径 | 新路径 |
|---|---|
| `USDSchemasModule.h` 中的 `GetTranslatorRegistry()` | `FUsdSchemaTranslatorRegistry::Get()` from `Objects/USDSchemaTranslator.h` (USDUtilities) |
| `USDSchemaTranslator.h` | `Objects/USDSchemaTranslator.h` (USDUtilities) |
| `USDPrimLinkCache.h` | `Objects/USDPrimLinkCache.h` (USDUtilities) |
| `USDInfoCache.h` | `Objects/USDInfoCache.h` (USDUtilities) |
| `USDSkelRootTranslator.h` | `USDSkelSkeletonTranslator.h` |

## 模块依赖

| 模块 | 用途 |
|---|---|
| `USDCore` | USD SDK 封装（`UE::FUsdStage`、`UE::FSdfPath`、`UE::FUsdPrim` 等） |
| `USDUtilities` | Translator 注册表、资产缓存、Prim 链接缓存、Info 缓存 |
| `USDClasses` | USD 相关 UObject 类 |
| `GeometryCache` | 几何缓存资产（GeometryCacheTranslator 依赖） |
| `Groom` | 毛发资产系统（GroomTranslator 依赖） |
| `MeshDescription` | 网格描述数据结构 |