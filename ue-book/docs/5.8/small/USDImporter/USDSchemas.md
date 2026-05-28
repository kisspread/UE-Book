# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 导入器 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、材质、测试资源） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

USD Importer 插件为 Unreal Engine 提供了对 Universal Scene Description (USD) 文件格式的完整支持。它的核心作用是**实现 USD 与 UE 之间的双向资产与场景图交换**。这不仅包括将 USD 文件中的几何体、材质、光照、相机和动画导入为 UE 资产，还包括将 UE 场景导出为 USD 格式，以及通过一个持久化的 `USDStage` Actor 来管理、编辑和更新 USD 场景。它解决的是专业数字内容创作 (DCC) 工具（如 Maya, Houdini）与游戏引擎之间通过 USD 进行复杂资产和场景高效、无损交换的工业流程问题。

## 使用场景

- 你正在使用 Houdini 或 Maya 制作复杂的动画、特效或环境资产，并希望通过 USD 格式将其导入 UE 进行实时预览和最终集成。
- 你的团队采用 USD 作为资产管道的标准交换格式，需要将 UE 中修改后的资产（如调整后的材质或光照设置）导出回 DCC 工具进行迭代。
- 你需要管理一个由多个 USD 文件组成的大型场景，并希望在 UE 中动态加载、更新或替换其中的部分组件。
- 你需要在 UE 中实时预览 USD 场景在不同渲染上下文下的效果。

## 蓝图用法

该插件的蓝图接口主要通过 `USDStage` Actor 暴露，而非一系列独立的蓝图函数库节点。

### 核心节点（通过 USDStage Actor 属性）

| 属性 | 说明 | 所在类 |
|---|---|---|
| `StageInfo` | 获取当前 USDStage Actor 加载的 USD 文件路径和根 Prim 路径信息。 | `AUsdStageActor` |
| `RootLayer` | 设置或获取要加载的根 USD 文件（.usda/.usdc/.usdz）的路径。 | `AUsdStageActor` |
| `PurposesToLoad` | 设置加载 USD 数据时考虑的用途标签（如 `proxy`, `render`, `guide`）。 | `AUsdStageActor` |
| `RenderContext` | 设置用于材质翻译的渲染上下文（如 `unreal`, `glslfx`）。 | `AUsdStageActor` |
| `MetersPerUnit` | 设置场景的单位换算比例。 | `AUsdStageActor` |
| `TimeCode` | 设置或获取当前评估的时间码，用于播放动画。 | `AUsdStageActor` |
| `bIsAutomaticallyUpdated` | 控制 Actor 是否在编辑器或运行时自动响应底层 USD 文件的更改。 | `AUsdStageActor` |

### 使用示例（蓝图描述）
1. 在场景中放置一个 `USD Stage Actor`。
2. 在其 `Details` 面板中，设置 `Root Layer` 属性为你想要导入的 USD 文件路径（例如 `/Game/MyScene.usdz`）。
3. 根据需要调整 `Purposes To Load`、`Render Context` 等属性。
4. 运行场景或在编辑器中，USD Stage Actor 会自动根据 USD 文件内容创建对应的 UE Actor 和组件。

## C++ 用法

### 头文件引入
```cpp
#include "USDSchemas/USDSchemasModule.h" // 用于访问模块和工具函数
#include "USDStage/USDStageActor.h" // 用于操作 USDStage Actor
#include "USDCore/USDMemory.h" // 用于 USD SDK 类型 (UE::FUsdStage, UE::FSdfPath 等)
```

### 基本用法
以下代码演示如何通过 C++ 在运行时创建一个 USD Stage Actor 并加载一个 USD 文件。
```cpp
// 假设已包含相关头文件，并有一个 UWorld* WorldContext

// 1. 生成一个 USDStage Actor
AUsdStageActor* UsdStageActor = WorldContext->SpawnActor<AUsdStageActor>();

// 2. 设置要加载的 USD 文件路径
FFilePath UsdFile;
UsdFile.FilePath = TEXT("/Game/MyAssets/Props/Chair.usda");
UsdStageActor->SetRootLayer(UsdFile);

// 3. 设置加载参数（可选）
UsdStageActor->SetPurposesToLoad(EUsdPurpose::Render | EUsdPurpose::Proxy);
UsdStageActor->SetRenderContext(EUsdRenderContext::Unreal);

// 4. Actor 将在下一帧自动开始解析 USD 并创建 UE 表示
```
*来源：USDStage 模块的 Actor 创建逻辑。*

### 进阶用法
扩展自定义 Schema Translator 以支持自定义的 USD Schema。这允许你在导入过程中将特定的 USD Prim 类型转换为你自定义的 UE 组件或资产。
```cpp
// 假设你定义了一个自定义的 USD Schema `MyCustomSchema`。
// 1. 创建 Translator 类
class FMyCustomSchemaTranslator : public FUsdSchemaTranslator
{
public:
    using FUsdSchemaTranslator::FUsdSchemaTranslator;
    
    virtual void CreateAssets() override
    {
        // 在这里将 USD Prim 数据转换为 UStaticMesh 或其他资产
        // 可以使用 AssetCache 和 PrimLinkCache 来缓存和链接资产
    }
    
    virtual USceneComponent* CreateComponents() override
    {
        // 在这里创建并返回自定义的 USceneComponent 子类实例
        return NewObject<UMyCustomComponent>();
    }
    
    virtual void UpdateComponents(USceneComponent* SceneComponent) override
    {
        // 在这里根据 USD Prim 的当前状态更新组件属性
    }
};

// 2. 在模块启动时注册 Translator
IUsdSchemasModule& SchemasModule = FModuleManager::GetModuleChecked<IUsdSchemasModule>(TEXT("USDSchemas"));
SchemasModule.GetTranslatorRegistry().RegisterTranslator<FMyCustomSchemaTranslator>(
    TEXT("MyCustomSchema") // 你的 USD Schema 类型名称
);
```
*来源：基于 `FUsdGeomMeshTranslator` 等翻译器的结构设计。*

## Demo 示例

一个最小化的自定义 USD Schema Translator 示例，用于将包含 `CustomData` 属性的 USD Prim 转换为带标签的 Static Mesh Actor。

### CustomDataTranslator.h
```cpp
#pragma once
#include "USDSchemas/USDSchemaTranslator.h"

#if USE_USD_SDK
class UStaticMesh;

class FCustomDataTranslator : public FUsdSchemaTranslator
{
public:
    using FUsdSchemaTranslator::FUsdSchemaTranslator;

    // 重写核心翻译函数
    virtual void CreateAssets() override;
    virtual USceneComponent* CreateComponents() override;
    virtual void UpdateComponents(USceneComponent* SceneComponent) override;

    // 定义此 Translator 是否处理其子 Prim
    virtual bool CollapsesChildren(ECollapsingType CollapsingType) const override { return false; }
    virtual bool CanBeCollapsed(ECollapsingType CollapsingType) const override { return false; }
    virtual TSet<UE::FSdfPath> CollectAuxiliaryPrims() const override { return {}; }
};

#endif // USE_USD_SDK
```

### CustomDataTranslator.cpp
```cpp
#include "CustomDataTranslator.h"

#if USE_USD_SDK
#include "Components/StaticMeshComponent.h"
#include "USDConversionUtils.h"

void FCustomDataTranslator::CreateAssets()
{
    // 示例：此处可从 Prim 中读取自定义数据并创建 UStaticMesh
    // 通常会使用 AssetCache 来缓存资产
}

USceneComponent* FCustomDataTranslator::CreateComponents()
{
    // 创建一个基础的静态网格组件
    return NewObject<UStaticMeshComponent>();
}

void FCustomDataTranslator::UpdateComponents(USceneComponent* SceneComponent)
{
    if (UStaticMeshComponent* MeshComp = Cast<UStaticMeshComponent>(SceneComponent))
    {
        // 从 USD Prim 中读取自定义数据，例如一个标签
        pxr::VtValue LabelValue;
        if (GetPrim().GetCustomDataByKey(pxr::TfToken("ueLabel"), &LabelValue))
        {
            FString Label = UsdToUnreal::ConvertString(LabelValue.Get<std::string>());
            MeshComp->SetTag(FName(*Label));
        }
        // 更新网格等其他属性...
    }
}
#endif // USE_USD_SDK
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `USDCore` | 提供对底层 USD SDK (`pxr`) 的 C++ 封装和基础工具类（如 `FUsdStage`, `FUsdPrim`, `FSdfPath`）。 |
| `USDUtilities` | 提供高级工具类，如 `FUsdSchemaTranslatorRegistry`, `FUsdPrimLinkCache`, `FUsdInfoCache`，是扩展和使用该插件的主要接口。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了严格浮点模式下双精度常量被截断为单精度的编译警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | 为USD动画添加了支持蓝图无关的控制重定向功能。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va | 修复了USD SDK 26.03更新导致动画查询在LOD变化时内部引用失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了32位格式说明符与64位参数不匹配的代码，提升了数值精度。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | 优化了曝光动画轨道的烘焙，现在支持烘焙所有帧。 |

### 维护评价
该插件于 **2018 年** 创建，历史较长。从近期的 git 日志可以看出，它在 **2026 年 4 月至 5 月期间仍有频繁且实质性的更新**，修复了多项编译、兼容性和功能问题（如动画、LOD、数值精度）。这表明该插件虽然标记为实验性 (`IsBetaVersion: true`) 且默认禁用，但 **仍在积极维护和开发中**，是 Epic 为影视和虚拟制片行业提供的核心工具之一。鉴于其活跃的维护状态和强大的功能集，对于有专业 USD 管道需求的项目是**推荐使用**的，但需注意其实验性状态可能意味着 API 可能会发生变化。

## 相关链接
- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- 官方文档：无
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests)