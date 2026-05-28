# USD Importer

> Adds support for importing the USD file format into Unreal Engine

| 属性 | 值 |
|---|---|
| 中文名 | USD 资产交换 |
| 分类 | Importers |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `GeometryCacheUSD` (Runtime), `USDClassesEditor` (Runtime), `USDExporter` (Runtime), `USDSchemas` (Runtime), `USDStage` (Runtime), `USDStageEditor` (Runtime), `USDStageEditorViewModels` (Runtime), `USDStageImporter` (Runtime), `USDTests` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-11-19 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter) | |

## 用途

该插件为 Unreal Engine 提供了对 Pixar USD (Universal Scene Description) 文件格式的完整支持，实现了双向资产交换。其核心目标是将 USD 生态系统（包括 Maya、Houdini 等 DCC 工具）与 Unreal Engine 的资产管线无缝集成。它不仅仅是导入器，更是一个强大的场景描述交换枢纽，用于处理复杂的动画、几何体缓存、材质和舞台布局。

## 使用场景

- **大型影视或动画项目**：需要在不同 DCC 软件和 UE 之间进行复杂的场景、动画资产交换。
- **使用 USD 工作流程的团队**：需要将 Maya、Houdini 等软件中创建的 USD 资产引入 UE 进行最终渲染或实时预览。
- **跨软件资产管线**：希望利用 USD 的非破坏性、分层特性来管理资产版本和变体。
- **动画和几何体缓存**：导入 USD 格式的动画序列和几何体缓存到 UE 中播放。

## 蓝图用法

### 核心节点

由于 USDImporter 主要是一个导入/编辑器交互式插件，其核心功能通过编辑器菜单、资产操作和蓝图节点暴露。以下是从 `USDClassesEditor` 模块中提取的、可用于操作 USD 资产缓存的蓝图相关节点：

| 节点 | 说明 | 所在类 |
|---|---|---|
| `GetAssetCache` | 获取当前的 USD 资产缓存对象 (`UUsdAssetCache3`)。 | `UUsdAssetCache3` |
| `AddAsset` | 向缓存中添加一个新资产，并为其分配一个唯一的标识符 (Prim Path)。 | `UUsdAssetCache3` |
| `GetCachedAsset` | 根据给定的标识符 (Prim Path) 从缓存中获取对应的资产。 | `UUsdAssetCache3` |
| `RemoveAsset` | 从缓存中移除一个资产。 | `UUsdAssetCache3` |

**使用示例**：
你可以在蓝图中获取一个 `UUsdAssetCache3` 对象的引用。然后，使用 `AddAsset` 节点将一个从 USD 导入的纹理或材质实例添加到缓存中，并为其指定一个来自 USD Prim 的路径作为键。之后，在同一个或另一个蓝图中，你可以使用 `GetCachedAsset` 节点并传入相同的 Prim 路径，来检索之前缓存的纹理或材质实例，用于材质构建或其他逻辑。

## C++ 用法

### 头文件引入

```cpp
// 引入 USD 资产缓存类
#include "USDAssetCache.h" // UUsdAssetCache3

// 如果要在编辑器中扩展 USD 资产缓存的功能
#include "USDClassesEditorModule.h"
```

### 基本用法

以下代码展示了如何在 C++ 中访问和使用 `UUsdAssetCache3` 来管理从 USD 导入的资产。这在处理 USD 导入回调或需要程序化管理缓存时非常有用。

```cpp
// 假设你已经有一个指向 UUsdAssetCache3 的指针
UUsdAssetCache3* MyAssetCache = ...;

// 1. 添加一个资产到缓存
// (例如，在导入管线中，你收到了一个新创建的 UMaterialInstance 和它对应的 USD Prim 路径)
FString PrimPath = TEXT("/Root/MyMesh/Material");
UMaterialInstance* ImportedMaterial = ...; // 从导入过程中获得的材质实例
MyAssetCache->AddAsset(PrimPath, ImportedMaterial);

// 2. 稍后，从缓存中检索资产
UObject* CachedAsset = MyAssetCache->GetCachedAsset(PrimPath);
if (UMaterialInstance* RetrievedMaterial = Cast<UMaterialInstance>(CachedAsset))
{
    // 使用检索到的材质实例...
}

// 3. 清理时移除资产
MyAssetCache->RemoveAsset(PrimPath);
```

### 进阶用法

更复杂的用法通常涉及监听 USD 导入或场景更新的事件，并在这些事件的回调中操作缓存或场景。这通常在 `USDStage` 或 `USDStageImporter` 模块的逻辑中实现。

```cpp
// 示例：监听 USD 阶段的更新（概念性伪代码，具体事件签名需参考源码）
// 假设你有一个 IUsdStageListener 的实现
void FMyUsdStageListener::OnStageUpdated(const FUsdStageUpdateInfo& UpdateInfo)
{
    // 当 USD 阶段的 Prim 被添加或修改时，这里会被调用
    for (const FUsdPrimUpdateInfo& PrimUpdate : UpdateInfo.UpdatedPrims)
    {
        // 根据 Prim 的类型和路径，决定如何处理
        if (PrimUpdate.PrimPath == TEXT("/Root/MyAnim"))
        {
            // 可能需要重新导入或更新对应的动画缓存
            // 这里可能会调用 USDImporter 的内部 API 来更新资产
        }
    }
}
```

## Demo 示例

以下是一个最小化的 C++ 示例，演示如何创建和使用 `UUsdAssetCache3` 对象。请注意，在实际的导入流程中，该对象通常由 USD 导入器内部创建和管理。

```cpp
// MyUsdUtils.h
#pragma once

#include "CoreMinimal.h"

class UUsdAssetCache3;
class UTexture2D;

class FMyUsdUtils
{
public:
    /** 创建一个空的 USD 资产缓存 */
    static UUsdAssetCache3* CreateEmptyAssetCache();

    /** 演示向缓存添加和检索纹理 */
    static void TestAssetCacheOperations(UUsdAssetCache3* InCache, UTexture2D* TextureToCache);
};
```

```cpp
// MyUsdUtils.cpp
#include "MyUsdUtils.h"
#include "USDAssetCache.h" // UUsdAssetCache3

UUsdAssetCache3* FMyUsdUtils::CreateEmptyAssetCache()
{
    // 在内存中创建一个新的资产缓存对象（通常由工厂处理）
    UUsdAssetCache3* NewCache = NewObject<UUsdAssetCache3>();
    return NewCache;
}

void FMyUsdUtils::TestAssetCacheOperations(UUsdAssetCache3* InCache, UTexture2D* TextureToCache)
{
    if (!InCache || !TextureToCache) return;

    const FString TexturePrimPath = TEXT("/Looks/MyMaterial/Texture");

    // 添加纹理到缓存
    InCache->AddAsset(TexturePrimPath, TextureToCache);

    // 检索纹理
    UTexture2D* RetrievedTexture = Cast<UTexture2D>(InCache->GetCachedAsset(TexturePrimPath));
    if (RetrievedTexture)
    {
        UE_LOG(LogTemp, Log, TEXT("Successfully retrieved cached texture: %s"), *RetrievedTexture->GetName());
    }

    // 可以选择移除
    // InCache->RemoveAsset(TexturePrimPath);
}
```

## 模块依赖

该插件（USDImporter）的独特之处在于它通常依赖于外部的 USD 库（如 OpenUSD 或 Pixars USD）。然而，在 UE 的构建系统中，这些依赖通常由引擎侧的 “USDCore” 等模块封装。

对于 `USDClassesEditor` 模块，其 `Build.cs` 文件显示它没有额外的特殊依赖，主要依赖常见的 `Core`、`Engine`、`Slate` 等模块。但是，要成功编译和运行整个 **USDImporter** 插件，你的项目可能需要：

| 模块 | 用途 |
|---|---|
| (无特殊模块依赖，但需要引擎级别支持) | 依赖于 Unreal Engine 内置或项目配置中启用的 USD 库 (USDCore, USDExporter 等)。这些模块通常由引擎或特定平台提供。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-13 | `852b276c` | Fixes code that produces warnings about double constant truncation to float under strict fp mode. | 修复了在严格浮点模式下双精度常量被截断为浮点数产生的编译器警告。 |
| 2026-04-29 | `bc4a1bd2` | USD: Add support for assigning BP-independent control rigs. | USD模块：新增对分配独立于蓝图的控制装置的支持。 |
| 2026-04-28 | `4fb59a1d` | USD: Work around update to 26.03 causing AnimQuery internal references to be invalidated when LOD va... | USD模块：解决升级至26.03版本导致动画查询内部引用在LOD变化时失效的问题。 |
| 2026-04-27 | `769566b4` | Fixed 32-bit format specifiers to be 64-bit when the arguments are 64-bit, and vice versa | 修正了32位格式说明符在参数为64位时应为64位的问题，反之亦然。 |
| 2026-04-09 | `fb7af182` | USD: Bake all frames of exposure animation tracks. | USD模块：烘焙曝光动画轨道的所有帧。 |

### 维护评价

**综合评价**：USD Importer 是一个**活跃维护中**但仍标记为**实验性**的核心插件。

- **创建时间**：始于 2018 年，已有约 7 年历史，属于成熟的基础设施级插件。
- **更新频率**：近期（2026年4月至5月）有密集的功能增强和 Bug 修复更新，涉及动画、控制装置集成和底层稳定性，表明 Epic 仍在积极投入开发。
- **实验性状态**：插件本身标记为 `IsBetaVersion: true` 且默认禁用，这意味着 API 和功能在版本间可能会发生重大变化，不推荐在关键生产环境中未充分测试就使用。
- **推荐度**：如果你的项目工作流**必须**依赖 Pixar USD 生态系统，那么这是唯一且必要的选择。建议在采用前，针对你的具体用例（动画、几何体缓存等）进行充分的原型测试和评估。由于其 Beta 状态，更新插件版本时需谨慎并做好回归测试。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Importers/USDImporter)
- [官方文档]() （该插件的 DocsURL 为空）
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.8/Engine/Plugins/Importers/USDImporter/Source/USDTests/)