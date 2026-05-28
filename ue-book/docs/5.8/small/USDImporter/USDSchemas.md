# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（USD资产、配置） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD (Universal Scene Description) Importer 是 Unreal Engine 与皮克斯 USD 格式生态系统进行数据交换的核心桥梁。它远不止一个简单的文件导入器，而是一个完整的双向（导入/导出）USD 场景处理套件。其核心解决的问题是：如何将 USD 强大的场景描述、动画、材质、骨骼等复杂数据，无损或低损地转换为 Unreal Engine 内部的资产和场景结构（如 StaticMesh、 SkeletalMesh、 Level Sequence、 Material 等）。这使得 UE 能够无缝融入以 USD 为标准的影视、动画和虚拟制片流水线，允许艺术家和开发者直接在 UE 中使用在 Maya、Houdini 等 DCC 工具中创建的资产，无需繁琐的格式转换。

## 使用场景

-   你正在开发一个虚拟制片（Virtual Production）项目，需要从 Houdini 等 DCC 工具导入复杂的程序化生成的 USD 场景到 Unreal Engine 中进行实时渲染和编辑。
-   你的美术团队使用 USD 格式管理资产库，你需要将这些资产（包括复杂的材质图、骨骼动画）批量或交互式地导入到 UE 项目中。
-   你需要在 Unreal Engine 中编辑一个 USD Stage（.usda/.usdc 文件），并能够将修改后的场景属性（如变换、可见性）导出回 USD 文件，实现非破坏性编辑流程。
-   你需要处理 USD 的变体（Variants）、有效载荷（Payloads）和引用（References）等高级特性，以实现大规模场景的模块化组装。

## 蓝图用法

USDImporter 的核心功能是通过编辑器菜单（如“File > Import”）和专用的 USD Stage Actor 面板进行操作的，而非典型的蓝图节点。它主要是一个数据导入/转换框架，其 C++ API 更为强大。

尽管如此，插件的某些高级功能（如资产缓存管理、自定义翻译器注册）可能通过 C++ 模块接口暴露给蓝图。以下是基于源码推断的核心 C++ 类和概念，它们构成了插件功能的基础，通常在 C++ 插件或编辑器扩展中被调用：

### 核心概念与类

| 类/概念 | 说明 |
|---|---|
| `FUsdSchemaTranslator` | USD 原语（Prim）到 UE 对象翻译的抽象基类。所有针对特定 USD Schema（如 GeomMesh, Light, Camera）的翻译器都继承自它。 |
| `FUsdGeomMeshTranslator` | 负责将 `UsdGeomMesh` 原语翻译为 `UStaticMesh` 资产和 `UStaticMeshComponent`。 |
| `FUsdShadeMaterialTranslator` | 负责将 `UsdShadeMaterial` 原语翻译为 UE 的 `UMaterialInterface` 资产。 |
| `FUsdSkelSkeletonTranslator` | 负责处理 `UsdSkelSkeleton` 及其相关的蒙皮网格，生成骨骼网格体资产和动画。 |
| `UUsdAssetCache3` | 一个资产缓存系统，用于存储和管理导入过程中生成的 UE 资产，避免重复创建。 |
| `FUsdPrimLinkCache` | 维护 USD 原语路径（SdfPath）与其生成的 UE 资产/组件之间的链接关系。 |
| `FUsdSchemaTranslationContext` | 在整个导入/更新过程中传递上下文信息的对象，包含阶段（Stage）、缓存、标志等。 |

### 使用示例（C++ 交互）

以下示例展示了如何在 C++ 中初始化一个 USD 阶段并触发几何体的导入（概念性代码，具体实现需参考 `USDStageImporter` 或 `USDStage` 模块）：

```cpp
#include "USDStageImporter.h" // 假设的接口
#include "USDSchemasModule.h" // 用于访问 Schema 翻译器注册表

// 获取 USD 导入器模块接口
IUsdStageImporterModule* StageImporterModule = FModuleManager::GetModulePtr<IUsdStageImporterModule>(TEXT("USDStageImporter"));

if (StageImporterModule)
{
    // 配置导入选项
    FUsdStageImportOptions ImportOptions;
    ImportOptions.bImportSkeletalMesh = true;
    ImportOptions.bCreateLevelSequenceForAnimations = true;

    // 执行导入（具体路径和参数需根据实际API调整）
    UObject* ImportedRootObject = StageImporterModule->ImportUSDStage(
        TEXT("/Game/Path/To/Your/Scene.usd"),
        TEXT("/Game/ImportedAssets/"),
        ImportOptions
    );

    // ImportedRootObject 可能是包含导入子组件的 Actor 或其他根对象
}

// 示例：获取并使用 GeomMesh 翻译器（通常由框架内部调用）
FUsdSchemaTranslatorRegistry& TranslatorRegistry = FUsdSchemaTranslatorRegistry::Get();
// ... 在内部，翻译器会根据 USD 原语类型被自动查找和实例化
```

## Demo 示例

以下是一个自定义 USD Schema 翻译器的最小示例，用于将一个虚构的 `MyCustomPrim` 原语翻译为 Unreal 的 `UTextRenderComponent`。

**MyCustomTranslator.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Objects/USDSchemaTranslator.h" // 引用来自 USDUtilities 的翻译器基类

#if USE_USD_SDK
#include "USDIncludesStart.h"
#include "pxr/usd/usd/prim.h"
#include "USDIncludesEnd.h"

class FMyCustomTranslator : public FUsdSchemaTranslator
{
public:
    using FUsdSchemaTranslator::FUsdSchemaTranslator;

    virtual void CreateAssets() override;
    virtual USceneComponent* CreateComponents() override;
    virtual void UpdateComponents(USceneComponent* SceneComponent) override;

    virtual bool CollapsesChildren(ECollapsingType CollapsingType) const override { return false; }
    virtual bool CanBeCollapsed(ECollapsingType CollapsingType) const override { return true; }
    virtual TSet<UE::FSdfPath> CollectAuxiliaryPrims() const override { return {}; }
};

#endif // USE_USD_SDK
```

**MyCustomTranslator.cpp**
```cpp
#include "MyCustomTranslator.h"

#if USE_USD_SDK
#include "USDIncludesStart.h"
#include "pxr/usd/usdGeom/xformable.h"
#include "USDIncludesEnd.h"

#include "Components/TextRenderComponent.h"

void FMyCustomTranslator::CreateAssets()
{
    // 在此为自定义原语创建需要的资产（如字体资源），本例中无需创建资产。
}

USceneComponent* FMyCustomTranslator::CreateComponents()
{
    // 在 Context 指定的 Actor 上创建组件
    AActor* Actor = Context->GetActor();
    UTextRenderComponent* TextComp = NewObject<UTextRenderComponent>(Actor);
    Actor->AddInstanceComponent(TextComp);
    TextComp->RegisterComponent();
    return TextComp;
}

void FMyCustomTranslator::UpdateComponents(USceneComponent* SceneComponent)
{
    UTextRenderComponent* TextComp = Cast<UTextRenderComponent>(SceneComponent);
    if (!TextComp) return;

    // 从 USD 原语读取自定义属性
    pxr::UsdPrim Prim = Context->Stage.GetPrimAtPath(PrimPath);
    if (Prim)
    {
        // 假设自定义原语有一个名为 `display:text` 的属性
        pxr::UsdAttribute TextAttr = Prim.GetAttribute(pxr::TfToken("display:text"));
        std::string TextValue;
        if (TextAttr && TextAttr.Get(&TextValue))
        {
            TextComp->SetText(FString(UTF8_TO_TCHAR(TextValue.c_str())));
        }
    }

    // 更新变换
    FUsdSchemaTranslator::UpdateComponents(SceneComponent);
}

#endif // USE_USD_SDK
```

## 模块依赖

USDImporter 插件结构复杂，包含多个子模块。要使用其核心导入/翻译功能，你的项目模块通常需要依赖 `USDCore` 或更具体的子模块。由于构建文件（Build.cs）未提供，以下为基于插件结构和常见实践的推断。

| 模块 | 用途 |
|---|---|
| `USDCore` | 提供核心 USD SDK 封装、类型定义和基础工具（如 `UsdUtils`, `UsdUnreal`）。是几乎所有 USD 相关模块的基石。 |
| `USDUtilities` | 提供更高级的实用工具类，如 `FUsdSchemaTranslator`、`FUsdPrimLinkCache`、`FUsdInfoCache` 等，用于资产管理和缓存。 |
| `USDClasses` | 定义了与 USD 相关的 UE 类型和接口。 |
| `UnrealUSDWrapper` | 底层 USD C++ API 的包装器模块。 |
| `USDExporter` | 如果你需要将 UE 内容导出回 USD 格式，则依赖此模块。 |

**注意**：`USDClassesEditor`, `USDStageEditor` 等模块是编辑器专用模块，仅在编辑器环境下加载。如果你仅在运行时使用 USD 相关功能（如游戏内加载 USD 资产），则应依赖 `Runtime` 类型的模块。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下双精度常量截断为浮点数导致的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD：支持分配独立于蓝图（BP）的控制绑定。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | USD：解决更新到 26.03 版本导致的在 LOD 变体切换时 AnimQuery 内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修复格式说明符与参数位宽不匹配的问题（32/64位）。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD：烘焙曝光动画轨道的所有帧。 |

### 维护评价

-   **状态**：**活跃维护中**。尽管插件标记为实验性（IsBetaVersion=true），但其最近的提交记录显示持续有新功能添加（如BP独立控制绑定）和重要Bug修复。
-   **年龄**：创建于2018年，已有约8年历史，是一个成熟的模块。
-   **更新频率**：更新非常频繁，最近一个月内就有5次提交，涵盖了功能增强、兼容性修复和Bug修复。
-   **限制与警告**：
    1.  **手动启用**：`EnabledByDefault=false`，**必须在项目插件设置中手动启用**才能使用。
    2.  **测试版**：`IsBetaVersion=true`，表示API可能尚未完全稳定，未来版本可能发生变化，尤其是在5.6和5.8版本中已出现一些API迁移的废弃警告（如 `IUsdSchemasModule::GetTranslatorRegistry()` 被废弃）。
    3.  **复杂性**：依赖多个外部USD SDK版本，集成和版本升级可能复杂。
-   **推荐使用**：**强烈推荐**给需要进行USD集成的影视、虚拟制片和高级可视化项目。尽管标记为测试版，但它已是UE中处理USD的事实标准方案，且维护活跃。使用时请注意查阅最新文档和示例，以应对可能的API变化。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
-   [官方文档](https://docs.unrealengine.com/5.8/en-US/working-with-usd-in-unreal-engine/) (UE 官方 USD 工作流程文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests) (插件内置的测试模块)