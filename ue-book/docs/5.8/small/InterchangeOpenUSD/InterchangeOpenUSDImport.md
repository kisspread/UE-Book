# Interchange Open USD

# Interchange Open USD Import

> Allows translation of OpenUSD files via the Interchange framework

| 属性 | 值 |
|---|---|
| 中文名 | 通用USD导入 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（翻译器设置、管线、自定义属性类型） |
| 模块 | `InterchangeOpenUSDEditor` (Runtime), `InterchangeOpenUSDImport` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-08-14 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD) | |

## 用途

本插件为 Unreal Engine 的 **Interchange 框架**提供 **OpenUSD（.usd/.usda/.usdc/.usdz）** 文件的翻译能力。它将 USD Stage 中的各种 Prim（网格、材质、灯光、相机、骨骼、Groom、Volume 等）翻译为 Interchange 通用节点图，再由 Interchange 管线和工厂系统完成最终的资产创建。

与传统的直接导入器不同，本插件采用了**可扩展的 Schema Handler 架构**：每种 USD Schema 类型（Mesh、Material、Light、Camera 等）由独立的 Handler 处理翻译逻辑，Handler 可通过注册表动态注册/注销、调整优先级和启用状态。这意味着你可以在不修改核心翻译器的情况下，为自定义 USD Schema 添加导入支持。

**核心解决的问题**：将 USD 生态系统中丰富多变的 Prim Schema 和插值方式，标准化地映射为 UE 的 Interchange 资产管线所期望的节点树和 Payload 数据。

## 使用场景

- 你在使用 DCC 工具（Maya、Houdini、Blender）通过 USD 管线导出资产 → 用本插件在 UE 端标准化导入
- 你需要导入包含动画的 USD 骨骼角色 → 骨骼动画由 `FSkeletonSchemaHandler` 处理
- 你的 USD 文件使用 MaterialX 材质系统 → 由 `FMaterialXSchemaHandler` 翻译为 UE 材质
- 你需要控制哪些 Prim 被导入（子树筛选） → 通过 `PrimsToImport` 设置
- 你需要自定义 USD 某种自定义 Schema 的导入逻辑 → 继承 `FSchemaHandler` 并注册
- 你需要控制子树折叠行为以优化导入结构 → 通过 `KindsToCollapse` 和 `bUseSchemaForCollapsing` 配置

## 蓝图用法

### 翻译器设置（UInterchangeUsdTranslatorSettings）

在导入对话框或通过 C++ 设置导入参数。

| 属性 | 说明 | 类型 |
|---|---|---|
| `GeometryPurpose` | 仅导入具有指定 Purpose 的几何 Prim（位掩码：Default/Proxy/Guide/Render） | `int32` (Bitmask) |
| `MaterialPurpose` | USD 材质绑定的 Material Purpose | `FName` |
| `InterpolationType` | 时间采样值的插值方式 | `EUsdInterpolationType` |
| `bOverrideStageOptions` | 是否覆盖 Stage 自身设置 | `bool` |
| `StageOptions` | 自定义 Stage 选项 | `FUsdStageOptions` |
| `PointInstancerCollapsing` | 遇到 PointInstancer 时的折叠行为 | `EUsdPointInstancerCollapsing` |
| `bUseSchemaForCollapsing` | 是否使用专用折叠 Schema | `bool` |
| `bUsePrimKindsForCollapsing` | 是否根据 Prim Kind 决定折叠 | `bool` |
| `KindsToCollapse` | 允许折叠的 Prim Kind 位掩码 | `int32` (Bitmask) |
| `bTranslatePrimAttributes` | 是否将 Prim 属性翻译为元数据 | `bool` |
| `AttributeRegexFilter` | Prim 属性名正则过滤器 | `FString` |
| `bTranslatePrimMetadata` | 是否翻译 Prim 元数据 | `bool` |
| `MetadataRegexFilter` | 元数据键名正则过滤器 | `FString` |
| `PrimsToImport` | 要导入的 Prim 路径列表（默认 `["/"]` 即全部） | `TArray<FString>` |
| `CustomHandlerEntries` | 自定义 Schema Handler 配置（空则使用默认） | `TArray<FSchemaHandlerEntry>` |

### 管线设置（UInterchangeUsdPipeline）

| 属性 | 说明 |
|---|---|
| `ImportPrimvars` | 如何处理 Primvar 附加到 MeshDescription |
| `SubdivisionLevel` | 细分网格的细分级别（0=不细分，最大6） |
| `bImportPseudoRoot` | 是否导入 Stage 伪根场景节点 |
| `bGeneratePrimvarCompatibleMaterials` | 是否生成与网格 Primvar UV 映射兼容的材质实例 |

### UsdContext 蓝图函数（UInterchangeUsdContext）

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetStageId` | 获取当前 USD Stage 在 StageCache 中的 ID | `UInterchangeUsdContext` |
| `SetStageId` | 通过 StageCache ID 设置要导入的 USD Stage（支持 Python 传入的 Stage） | `UInterchangeUsdContext` |

### 使用示例（蓝图描述）

典型的蓝图导入流程：
1. 使用 **Interchange Import Asset** 节点，Source 指向 `.usd`/`.usdz` 文件
2. 选择 **UInterchangeUsdPipeline** 作为导入管线
3. 通过管线的属性面板配置细分级别、Primvar 处理等
4. 如果需要仅导入特定子树，通过 `UInterchangeUsdTranslatorSettings` 的 `PrimsToImport` 指定 Prim 路径

## C++ 用法

### 头文件引入

```cpp
#include "InterchangeUsdTranslator.h"
#include "InterchangeUsdContext.h"
#include "SchemaHandlers/SchemaHandler.h"
#include "SchemaHandlers/SchemaHandlerRegistry.h"
#include "SchemaHandlers/SchemaHandlerEntry.h"
#include "InterchangeUSDPipeline.h"
#include "InterchangeOpenUSDImportModule.h"
```

### 注册自定义 Schema Handler

如果你想为自定义 USD Schema 添加导入支持，需要：
1. 继承 `FSchemaHandler`
2. 注册到全局注册表

```cpp
// MyCustomSchemaHandler.h
#pragma once
#include "SchemaHandlers/SchemaHandler.h"

namespace UE::Interchange::USD
{
    class FMyCustomSchemaHandler : public FSchemaHandler
    {
    public:
        virtual const FString& GetHandlerName() const override
        {
            static FString Name = TEXT("MyCustomSchemaHandler");
            return Name;
        }

        virtual const FString& GetTargetSchemaName() const override
        {
            static FString SchemaName = TEXT("MyCustomSchema");
            return SchemaName;
        }

        virtual bool OnTranslate(
            const UE::FUsdPrim& Prim,
            FTraversalInfo& TraversalInfo,
            FHandlerAccumulatedInfo& AccumulatedInfo,
            UInterchangeUsdContext& UsdContext
        ) override
        {
            // 获取或创建主场景节点
            UInterchangeBaseNode* SceneNode = AccumulatedInfo.GetOrCreateMainSceneNode(
                Prim, TraversalInfo, UsdContext
            );
            if (!SceneNode)
            {
                return false;
            }

            // 在此处理你的自定义 Schema 翻译逻辑...
            return true;
        }

        // 可选：提供 Mesh Payload 数据
        virtual bool OnGetMeshPayloadData(
            const FInterchangeMeshPayLoadKey& PayLoadKey,
            const UE::Interchange::FAttributeStorage& PayloadAttributes,
            UInterchangeUsdContext& UsdContext,
            TOptional<UE::Interchange::FMeshPayloadData>& InOutPayloadData
        ) override
        {
            // 生成网格数据...
            return InOutPayloadData.IsSet();
        }
    };
}
```

```cpp
// MyModule.cpp - 模块启动时注册
#include "SchemaHandlers/SchemaHandlerRegistry.h"
#include "MyCustomSchemaHandler.h"

void FMyModule::StartupModule()
{
    FString HandlerName = FSchemaHandlerRegistry::Register<FMyCustomSchemaHandler>();
    UE_LOG(LogTemp, Log, TEXT("Registered custom USD handler: %s"), *HandlerName);
}

void FMyModule::ShutdownModule()
{
    FSchemaHandlerRegistry::Unregister(TEXT("MyCustomSchemaHandler"));
}
```

### 自定义材质 Handler（带渲染上下文）

```cpp
namespace UE::Interchange::USD
{
    class FMyMaterialSchemaHandler : public FMaterialSchemaHandler
    {
    public:
        virtual const FString& GetHandlerName() const override
        {
            static FString Name = TEXT("MyMaterialHandler");
            return Name;
        }

        // 声明此 Handler 默认解析的渲染上下文
        virtual const TArray<FString>& GetDefaultRenderContexts() const override
        {
            static TArray<FString> Contexts = { TEXT("myRenderer") };
            return Contexts;
        }

        // 允许用户在 UI 中自定义渲染上下文
        virtual bool AllowCustomRenderContexts() const override { return true; }

        virtual bool OnTranslate(
            const UE::FUsdPrim& Prim,
            FTraversalInfo& TraversalInfo,
            FHandlerAccumulatedInfo& AccumulatedInfo,
            UInterchangeUsdContext& UsdContext
        ) override
        {
            // 处理材质翻译...
            return true;
        }
    };
}
```

### 自定义 Handler 配置（通过 TranslatorSettings）

```cpp
// 在导入前，通过 TranslatorSettings 自定义 Handler 行为
UInterchangeUsdTranslatorSettings* Settings = Translator->GetSettings();

// 获取默认 Handler 配置并调整
TArray<FSchemaHandlerEntry>& Entries = Settings->CustomHandlerEntries;

// 禁用某个 Handler
for (FSchemaHandlerEntry& Entry : Entries)
{
    if (Entry.HandlerName == TEXT("UnrealMaterial"))
    {
        Entry.bEnabled = false;
    }

    // 修改材质 Handler 的自定义渲染上下文
    if (Entry.HandlerName == TEXT("UniversalMaterial"))
    {
        Entry.bAllowCustomRenderContexts = true;
        Entry.CustomRenderContexts = { TEXT("unreal"), TEXT("myCustomContext") };
    }
}
```

### 使用 UsdContext 管理 Stage

```cpp
#include "InterchangeUsdContext.h"

// 通过 StageCache 获取/设置 Stage（适合 Python 管线集成）
UInterchangeUsdContext* UsdContext = Translator->UsdContext;

// 获取当前 Stage
UE::FUsdStage Stage = UsdContext->GetUsdStage();

// 通过 ID 设置（适用于 Python 传入的 Stage）
int64 StageId = UsdUtils::... // 获取 Python 创建的 Stage ID
UsdContext->SetStageId(StageId);
```

## Demo 示例

### 完整自定义 Handler 示例

```cpp
// FVolumeVariantSchemaHandler.h
#pragma once
#include "SchemaHandlers/SchemaHandler.h"
#include "SchemaHandlers/SchemaHandlerRegistry.h"

namespace UE::Interchange::USD
{
    /**
     * 示例：自定义 Handler，为特定 Volume Prim 添加额外的元数据标签。
     * 在模块启动时通过 FSchemaHandlerRegistry::Register 注册。
     */
    class FVolumeVariantSchemaHandler : public FSchemaHandler
    {
    public:
        virtual const FString& GetHandlerName() const override
        {
            static FString Name = TEXT("VolumeVariantHandler");
            return Name;
        }

        virtual const FString& GetTargetSchemaName() const override
        {
            static FString Schema = TEXT("Volume");
            return Schema;
        }

        virtual bool OnTranslate(
            const UE::FUsdPrim& Prim,
            FTraversalInfo& TraversalInfo,
            FHandlerAccumulatedInfo& AccumulatedInfo,
            UInterchangeUsdContext& UsdContext
        ) override
        {
            // 获取场景节点（Volume handler 可能已创建）
            UInterchangeBaseNode* SceneNode = AccumulatedInfo.GetMainSceneNode();
            if (!SceneNode)
            {
                return false;
            }

            // 在场景节点上添加自定义元数据
            // 例如：标记为需要特殊处理的 Volume
            static const FString Key = TEXT("VolumeVariant");
            static const FString Value = TEXT("AtmosphericFog");
            SceneNode->AddUserAttributeFromString(
                Key, Value
            );

            return true;
        }
    };
}
```

```cpp
// MyUSDExtensionModule.cpp
#include "MyUSDExtensionModule.h"
#include "FVolumeVariantSchemaHandler.h"

void FMyUSDExtensionModule::StartupModule()
{
    FString Name = FSchemaHandlerRegistry::Register<FVolumeVariantSchemaHandler>();
    UE_LOG(LogTemp, Log, TEXT("Registered: %s"), *Name);
}

void FMyUSDExtensionModule::ShutdownModule()
{
    FSchemaHandlerRegistry::Unregister(TEXT("VolumeVariantHandler"));
}

IMPLEMENT_MODULE(FMyUSDExtensionModule, MyUSDExtension)
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等以及 UnrealUSDWrapper/InterchangeCore）

| 模块 | 用途 |
|---|---|
| `UnrealUSDWrapper` | USD SDK 封装层（FUsdPrim、FUsdStage 等） |
| `InterchangeCore` / `InterchangeNodes` | Interchange 框架核心（节点容器、Payload 接口等） |
| `UsdUtils` | USD 工具集（材质分配、网格转换选项等） |

## 默认注册的 Schema Handler

本插件在模块启动时注册以下 Handler，按优先级顺序执行：

| Handler | 目标 Schema | 功能 |
|---|---|---|
| `FCollapsingSchemaHandler` | 多种 | 处理子树折叠逻辑 |
| `FNaniteAssemblySchemaHandler` | 多种 | 处理 Nanite 装配数据 |
| `FXformableSchemaHandler` | Xformable | 翻译变换（Transform） |
| `FImageableSchemaHandler` | Imageable | 处理可视属性（Purpose、Visibility） |
| `FGprimSchemaHandler` | Gprim | 处理几何基元（网格+材质槽+骨骼） |
| `FUniversalMaterialSchemaHandler` | Material | 翻译 UsdPreviewSurface 材质（渲染上下文：unreal） |
| `FMaterialXSchemaHandler` | Material | 翻译 MaterialX 材质（渲染上下文：mtlx） |
| `FUnrealMaterialSchemaHandler` | Material | 处理 Unreal 特有材质上下文 |
| `FLightSchemaHandler` | 多种灯光 | 翻译灯光参数 |
| `FCameraSchemaHandler` | 多种相机 | 翻译相机参数 |
| `FSkeletonSchemaHandler` | Skeleton/SkelRoot | 翻译骨骼和动画 |
| `FGroomSchemaHandler` | Groom | 翻译毛发数据 |
| `FGroomBindingSchemaHandler` | GroomBinding | 翻译毛发绑定 |
| `FVolumeSchemaHandler` | Volume/OpenVDB | 翻译体积数据（OpenVDB） |
| `FSpatialAudioSchemaHandler` | SpatialAudio | 翻译空间音频 |
| `FGeometryCacheSchemaHandler` | 多种 | 翻译几何缓存 |
| `FPointInstancerSchemaHandler` | PointInstancer | 翻译点实例器 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-25 | `61d0e791` | USD Pregen: Implement tracking of Skeleton and PhysicsAssets | 实现骨骼和物理资产的预生成跟踪 |
| 2026-05-22 | `e55b6ad4` | USD Pregen: Fix handling of USDZ files. | 修复 USDZ 文件的预生成处理 |
| 2026-05-19 | `fd496b57` | USD Pregen: Properly tag nodes produced by MaterialX translator with corresponding prim path so that | 正确标记 MaterialX 翻译器生成的节点的 Prim 路径 |
| 2026-05-14 | `561d9c2d` | USD Pregen: Fix materials inside instances not being deduplicated; | 修复实例内部材质未去重的问题 |
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复严格浮点模式下 double 常量截断为 float 的警告 |

### 维护评价

- **状态**：**活跃维护中**。最近数周内持续有实质性功能更新（Pregen 功能开发）和 bug 修复
- **实验性**：标记为 `IsExperimentalVersion=true` 且 `EnabledByDefault=false`，需要在插件设置中手动启用
- **风险**：作为实验性插件，API 可能在版本间发生变化；部分功能（如 FUsdInfoCache 相关 API）已在 5.8 版本中标记为 `UE_DEPRECATED`
- **推荐**：如果你的项目依赖 USD 管线，这是 UE5 原生的 Interchange 方案，处于快速迭代阶段，适合积极关注但需注意版本升级时的 API 变更

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD)
- [官方文档](https://docs.unrealengine.com)（插件本身 DocsURL 为空，参见 UE 官方 Interchange 文档）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Interchange/Extensions/OpenUSD)（需确认具体测试目录）