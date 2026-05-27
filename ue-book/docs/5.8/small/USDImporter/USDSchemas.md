# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质模板、测试资源） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

本插件的核心功能是将通用场景描述（Universal Scene Description, USD）文件格式导入并转换为 Unreal Engine 内部的资产和场景图。它不仅仅是一个简单的文件解析器，而是一个**基于 Schema 的资产转换框架**。插件定义了一套转换器（Translator）体系，将 USD 中的各种 Schema（如 `UsdGeomMesh`, `UsdSkelSkeleton`, `UsdShadeMaterial` 等）映射为对应的 UE 资产（如 `UStaticMesh`, `USkeleton`, `UMaterialInterface`）和场景组件。它解决了从 DCC（数字内容创作）工具通过 USD 这一标准格式，高效地将复杂资产（包括几何体、材质、骨骼动画、灯光、相机等）引入 UE 并保持数据关联性的问题。

## 使用场景

-   **角色与动画流程**：从 Maya、Blender 等软件通过 USD 导入带有骨骼绑定（Skeletal Mesh）、蒙皮权重和动画剪辑的角色模型。
-   **环境与场景构建**：导入从 Houdini 或其他程序化工具生成的、包含大量实例化（Point Instancer）、LOD 和材质分配的复杂场景。
-   **虚拟制片资产交换**：在虚拟制片流水线中，使用 USD 作为交换格式，在 UE 与其它工具（如 Pixar’s Stage、NVIDIA Omniverse）之间同步灯光、相机和场景数据。
-   **程序化资产管线**：集成到自动化脚本中，批量处理并导入 USD 格式的资产，并利用其缓存和重映射系统管理资产引用。

## 蓝图用法

USD Importer 的核心功能主要通过 C++ 类和编辑器集成提供。其蓝图用法主要体现在：
1.  **资产处理器 (Asset Processor)**：导入后的 USD 资产会作为 `UUsdAssetCache` 的一部分被管理，蓝图可通过资产缓存系统查询和操作它们。
2.  **舞台编辑器 (Stage Editor)**：`USDStageEditor` 模块提供了一套编辑器UI，用于预览、配置和控制 USD 资产的导入过程，这可以视为一个可视化的“蓝图”工作台。

### 核心节点（编辑器集成）

由于翻译器主要为 C++ 运行时设计，无直接暴露的 `BlueprintCallable` 函数。其蓝图/编辑器交互主要通过 `USDStageEditor` 面板实现。

## C++ 用法

### 头文件引入

使用 USD 导入器的核心是使用其提供的翻译器框架。
```cpp
#include "USDGeomMeshTranslator.h"  // 用于导入网格
#include "USDSkelSkeletonTranslator.h" // 用于导入骨骼
#include "USDSchemaTranslator.h"     // 已废弃，请用下面的新路径
// 新路径 (5.6+):
#include "USDUtilities/Objects/USDSchemaTranslator.h"
```

### 基本用法：处理 USD 几何体

以下示例展示了如何创建一个处理 `UsdGeomMesh` 的自定义任务链，这通常用于扩展或覆盖默认的网格导入行为。
(基于 `USDGeomMeshTranslator.h` 中的 `FBaseBuildStaticMeshTaskChain` 结构)

```cpp
// 头文件: MyCustomMeshTranslator.h
#pragma once
#include "USDGeomMeshTranslator.h"
#include "MeshDescription.h"

class FMyCustomBuildStaticMeshTask : public FBaseBuildStaticMeshTaskChain
{
public:
    explicit FMyCustomBuildStaticMeshTask(
        const TSharedRef<FUsdSchemaTranslationContext>& InContext,
        const UE::FSdfPath& InPrimPath
    ) : FBaseBuildStaticMeshTaskChain(InContext, InPrimPath)
    {}

protected:
    // 重写设置任务的方法，添加自定义处理步骤
    virtual void SetupTasks() override
    {
        FBaseBuildStaticMeshTaskChain::SetupTasks();

        // 在原有的任务链之后，添加一个自定义任务（例如，应用后处理修改）
        TaskChain->AddTask<FMyCustomPostProcessMeshTask>(...)
            ->AddPrerequisites(TaskChain->GetTasks()); // 确保在原任务完成后执行
    }
};
```

### 进阶用法：注册自定义 Schema 翻译器

当导入包含自定义 USD Schema 的资产时，你可以注册自己的翻译器来处理它。
(基于 `IUsdSchemasModule` 和 `FUsdSchemaTranslatorRegistry` 的模式)

```cpp
// 头文件: MyCustomSchemaTranslator.h
#pragma once
#include "USDUtilities/Objects/USDSchemaTranslator.h" // 使用新路径

class FMyCustomSchemaTranslator : public FUsdSchemaTranslator
{
public:
    FMyCustomSchemaTranslator(
        TSharedRef<FUsdSchemaTranslationContext> InContext,
        const UE::FUsdTyped& InSchema
    ) : FUsdSchemaTranslator(InContext, InSchema)
    {}

    // 实现创建资产（如UObject、UStaticMesh等）
    virtual void CreateAssets() override;

    // 实现创建对应的场景组件（如AActor、USceneComponent等）
    virtual USceneComponent* CreateComponents() override;

    // 实现更新已存在的组件
    virtual void UpdateComponents(USceneComponent* SceneComponent) override;

    // ... 其他必要的重写
};

// 注册翻译器的代码 (通常在模块 Startup 中)
FUsdSchemaTranslatorRegistry::Get().RegisterTranslator(
    TEXT("MyCustomSchemaName"), // 你的 USD Schema 类型名
    FUsdSchemaTranslatorRegistry::FTranslatorFactory::CreateLambda(
        [](const TSharedRef<FUsdSchemaTranslationContext>& Context, const UE::FUsdTyped& Schema) -> TSharedRef<FUsdSchemaTranslator>
        {
            return MakeShared<FMyCustomSchemaTranslator>(Context, Schema);
        }
    )
);
```

## Demo 示例

一个最小化的、扩展默认网格导入器的示例。

```cpp
// MyUSDImporterExtension.h
#pragma once
#include "CoreMinimal.h"
#include "USDGeomMeshTranslator.h"

class FMyGeomMeshTranslator : public FUsdGeomMeshTranslator
{
public:
    using FUsdGeomMeshTranslator::FUsdGeomMeshTranslator;

    // 覆盖创建资产，例如强制所有导入的网格启用Nanite
    virtual void CreateAssets() override
    {
        FUsdGeomMeshTranslator::CreateAssets();
        // 假设我们访问到了生成的StaticMesh
        // StaticMesh->NaniteSettings.bEnabled = true;
    }

    // 覆盖组件创建，例如将网格组件类型替换为自定义的
    virtual USceneComponent* CreateComponents() override
    {
        // 可以先调用父类创建默认组件
        USceneComponent* Component = FUsdGeomMeshTranslator::CreateComponents();
        // 然后替换或附加自定义逻辑
        // if (UStaticMeshComponent* MeshComp = Cast<UStaticMeshComponent>(Component))
        // {
        //     MeshComp->SetMaterial(0, MyDefaultMaterial);
        // }
        return Component;
    }
};
```

## 模块依赖

USD Importer 插件依赖于 Unreal Engine 内部的 USD 库和工具模块。你的项目模块若需与 USD 导入数据深度交互，可能需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `USDCore` | 提供底层的 USD SDK 封装和基础类型 (`UE::FUsdStage`, `UE::FUsdPrim` 等)。 |
| `USDUtilities` | 提供高级工具，如 `FUsdSchemaTranslator` (5.6+新位置)、`FUsdInfoCache`、`FUsdPrimLinkCache`、`USDSchemaTranslatorRegistry`。 |
| `USDSchemas` | (本插件核心模块) 提供内置 USD Schema 到 UE 资产/组件的具体翻译器实现。 |
| `USDStage` | 提供 USD Stage 的运行时表示和操作。 |
| `GeometryCacheUSD` | 专门处理几何缓存（Groom）相关的 USD 导入。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复在严格浮点模式下，代码中将双精度常量截断为浮点数而产生的警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD: 增加对独立于蓝图的 Control Rig 的分配支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | USD: 修复了升级到26.03版本后，当LOD变化时AnimQuery内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了格式说明符：当参数为64位时使用64位说明符，反之亦然，解决了32位和64位不匹配的问题。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD: 烘焙曝光动画轨道的所有帧。 |

### 维护评价

-   **创建时间**：插件于 2018 年创建，是 UE 早期对 USD 支持的核心组件之一。
-   **最近更新频率**：近期（2026年4月-5月）有持续的更新，主要集中在**编译修复、平台兼容性**和**功能细节增强**（如动画、Control Rig集成）。没有看到重大架构变更或新功能模块的添加。
-   **维护活跃度**：**维护中**。作为 Epic 官方插件且仍在持续修复问题，表明其仍在维护中。但更新内容以修复和适配为主，处于稳定期。
-   **已知问题与限制**：
    1.  **实验性**：`.uplugin` 中 `IsBetaVersion=true`，表明 API 和功能可能尚未完全稳定。
    2.  **架构重构**：代码中存在大量 `UE_DEPRECATED_HEADER` 注释（如 `USDSchemaTranslator.h`、`USDInfoCache.h`），表明核心类正在从 `USDSchemas` 模块向 `USDUtilities` 模块迁移，开发者在引用头文件时需要注意新旧路径。
    3.  **默认未启用**：需要手动在插件列表中启用。
-   **推荐使用**：**推荐，但需注意版本**。它是 UE 官方提供的、功能全面的 USD 解决方案，适合需要工业级 USD 管线集成的项目。由于是实验性状态，建议在 production 使用前进行充分测试，并关注未来版本的 API 变更。

## 相关链接

-   [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
-   [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/usd-in-unreal-engine) (Epic Games 官方 USD 文档)
-   [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests) (USDTests 模块)