# MetaHuman Creator

> MetaHuman Character Asset Creator and Editor.（照抄，不翻译）

| 属性 | 值 |
|---|---|
| 分类 | MetaHuman |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（MetaHuman角色资产、编辑器工具） |
| 模块 | `MetaHumanCharacter` (Runtime), `MetaHumanCharacterEditor` (Runtime), `MetaHumanCharacterMigrationEditor` (Runtime), `MetaHumanCharacterPalette` (Runtime), `MetaHumanCharacterPaletteEditor` (Runtime), `MetaHumanDefaultEditorPipeline` (Runtime), `MetaHumanDefaultPipeline` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2025-03-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.6/Engine/Plugins/MetaHuman/MetaHumanCharacter) | |

## 用途

MetaHuman Character 插件提供了一套完整的工具链，用于在 Unreal Engine 内创建、编辑和管理 MetaHuman 角色资产。它不仅仅是导入工具，更是一个**角色资产工厂和编辑器**。其核心功能是将来自 MetaHuman Creator 的原始数据（如网格、纹理、毛发）转化为可在引擎中高效使用的资产（如骨骼网格体、材质、Groom），并允许开发者在编辑器中对角色的外观（如服装、发型）进行组合、调整和预览，最终生成可用于游戏或实时应用的完整角色蓝图和资产集合。

## 使用场景

- 你从 MetaHuman Creator 下载了一个角色，需要将其转化为 UE 中可用的、经过优化的资产 → 使用此插件的构建管线。
- 你需要为同一个 MetaHuman 角色创建多种服装或发型的变体，并快速切换预览 → 使用此插件的调色板（Palette）和实例（Instance）系统。
- 你正在开发一个需要大量高质量数字人类的游戏或应用，需要标准化的角色创建和资产管理工作流 → 使用此插件提供的编辑器管线和资产规范。
- 你需要将 MetaHuman 角色导出到 Unreal Editor for Fortnite (UEFN) 项目中 → 使用 `UMetaHumanDefaultEditorPipelineUEFN` 管线。

## 蓝图用法

本插件主要通过编辑器工具和资产操作，蓝图可直接调用的运行时节点较少。核心交互发生在编辑器中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `SetHairVisibilityState` | 设置角色毛发（头发、眉毛等）的显示状态（显示/隐藏/仅卡片） | `AMetaHumanDefaultEditorPipelineActor` |
| `SetClothingVisibilityState` | 设置角色服装的显示状态（显示/隐藏/使用替代材质） | `AMetaHumanDefaultEditorPipelineActor` |
| `TemplateClass` (属性) | 指定用于创建新蓝图的模板Actor类（用于旧版管线） | `UMetaHumanDefaultEditorPipelineLegacy` |
| `UefnProjectFilePath` (属性) | 指定用于导出组装后资产的 UEFN 项目文件路径 | `UMetaHumanDefaultEditorPipelineUEFN` |

### 使用示例（蓝图描述）

在编辑器中，你可以通过 `AMetaHumanDefaultEditorPipelineActor` 的实例来控制预览效果。例如，要隐藏角色的头发，可以在蓝图中获取该Actor的引用，然后调用 `SetHairVisibilityState` 并传入 `EMetaHumanHairVisibilityState::Hidden`。要临时用灰色材质查看服装轮廓，可以调用 `SetClothingVisibilityState` 并传入一个灰色材质实例。

## C++ 用法

本插件的 C++ 用法主要集中在扩展和自定义编辑器管线，以支持新的资产类型或构建流程。

### 头文件引入

```cpp
#include "MetaHumanDefaultEditorPipelineBase.h"
#include "MetaHumanItemEditorPipeline.h"
```

### 基本用法

创建一个自定义的编辑器管线，继承自 `UMetaHumanDefaultEditorPipelineBase` 或 `UMetaHumanItemEditorPipeline`，并重写关键虚函数。

```cpp
// 来源：MetaHumanDefaultEditorPipeline.h
// 展示如何继承并实现一个简单的编辑器管线
UCLASS(EditInlineNew)
class UMyCustomEditorPipeline : public UMetaHumanDefaultEditorPipelineBase
{
    GENERATED_BODY()

public:
    // 决定是否生成集合和实例资产
    virtual bool ShouldGenerateCollectionAndInstanceAssets() const override
    {
        return true; // 或 false，取决于你的管线逻辑
    }

    // 实现如何写入角色蓝图
    virtual UBlueprint* WriteActorBlueprint(const FWriteBlueprintSettings& InWriteBlueprintSettings) const override
    {
        // 你的自定义蓝图生成逻辑
        return nullptr;
    }

    // 实现如何更新已有的角色蓝图
    virtual bool UpdateActorBlueprint(const UMetaHumanCharacterInstance* InCharacterInstance, UBlueprint* InBlueprint) const override
    {
        // 你的自定义蓝图更新逻辑
        return false;
    }
};
```

### 进阶用法

为特定的物品类型（如服装、发型）创建编辑器管线。你需要继承 `UMetaHumanItemEditorPipeline` 并实现 `BuildItem` 函数，该函数定义了如何将原始资产（如 SkeletalMesh）构建成最终可用的资产。

```cpp
// 来源：MetaHumanOutfitEditorPipeline.h
// 展示如何为服装创建编辑器管线
UCLASS(EditInlineNew)
class UMyOutfitEditorPipeline : public UMetaHumanItemEditorPipeline
{
    GENERATED_BODY()

public:
    UMyOutfitEditorPipeline();

    // 核心构建函数，处理服装资产的生成
    virtual void BuildItem(
        const FMetaHumanPaletteItemPath& ItemPath,
        TNotNull<const UMetaHumanWardrobeItem*> WardrobeItem,
        const FInstancedStruct& BuildInput,
        TArrayView<const FMetaHumanPinnedSlotSelection> SortedPinnedSlotSelections,
        TArrayView<const FMetaHumanPaletteItemPath> SortedItemsToExclude,
        FMetaHumanPaletteBuildCacheEntry& BuildCache,
        EMetaHumanCharacterPaletteBuildQuality Quality,
        ITargetPlatform* TargetPlatform,
        TNotNull<UObject*> OuterForGeneratedObjects,
        const FOnBuildComplete& OnComplete) const override;

    // 返回此管线的规范说明
    virtual TNotNull<const UMetaHumanCharacterEditorPipelineSpecification*> GetSpecification() const override;

    // 服装特有的属性，用于处理头部和身体的几何体遮挡
    UPROPERTY(EditAnywhere, Category = "Outfit")
    UE::MetaHuman::GeometryRemoval::FHiddenFaceMapTexture HeadHiddenFaceMapTexture;

    UPROPERTY(EditAnywhere, Category = "Outfit")
    UE::MetaHuman::GeometryRemoval::FHiddenFaceMapTexture BodyHiddenFaceMapTexture;
};
```

## Demo 示例

以下示例展示如何创建一个最简单的自定义编辑器管线，它继承自遗留管线，并重写了蓝图生成逻辑。

```cpp
// MySimplePipeline.h
#pragma once

#include "MetaHumanDefaultEditorPipelineLegacy.h"
#include "MySimplePipeline.generated.h"

UCLASS(EditInlineNew)
class UMySimplePipeline : public UMetaHumanDefaultEditorPipelineLegacy
{
    GENERATED_BODY()

public:
    UMySimplePipeline();

    // 重写蓝图生成，使用一个简单的模板
    virtual UBlueprint* WriteActorBlueprint(const FWriteBlueprintSettings& InWriteBlueprintSettings) const override;

    // 重写蓝图更新，添加自定义逻辑
    virtual bool UpdateActorBlueprint(const UMetaHumanCharacterInstance* InCharacterInstance, UBlueprint* InBlueprint) const override;
};
```

```cpp
// MySimplePipeline.cpp
#include "MySimplePipeline.h"
#include "Engine/Blueprint.h"

UMySimplePipeline::UMySimplePipeline()
{
    // 设置一个默认的模板类
    TemplateClass = AActor::StaticClass();
}

UBlueprint* UMySimplePipeline::WriteActorBlueprint(const FWriteBlueprintSettings& InWriteBlueprintSettings) const
{
    // 简单的实现：调用父类逻辑，或返回一个基于TemplateClass的新蓝图
    // 这里仅为演示，实际逻辑会更复杂
    if (TemplateClass)
    {
        // 创建蓝图的逻辑...
        // return NewBlueprint;
    }
    return nullptr;
}

bool UMySimplePipeline::UpdateActorBlueprint(const UMetaHumanCharacterInstance* InCharacterInstance, UBlueprint* InBlueprint) const
{
    // 在蓝图更新时执行自定义操作，例如添加组件或修改变量
    // ...
    return Super::UpdateActorBlueprint(InCharacterInstance, InBlueprint);
}
```

## 模块依赖

从头文件依赖关系推断，使用本插件的模块通常需要依赖以下独特模块：

| 模块 | 用途 |
|---|---|
| `MetaHumanCharacter` | 核心运行时模块，定义角色、实例等基础数据类型 |
| `MetaHumanCharacterPalette` | 管理角色资产的调色板（Palette）和衣柜（Wardrobe）系统 |
| `MetaHumanCollectionEditorPipeline` | 提供编辑器管线的基类和规范 |
| `ControlRig` | 用于驱动 MetaHuman 面部和身体的动画控制系统 |
| `Dataflow` | 用于处理纹理烘焙等数据流操作 |
| `TextureGraph` | 用于程序化生成和烘焙纹理 |

## 维护状态

### 近期更新

- 2025-10-03 a7ffdedc5b23 [UEMHC] Release any live MID/MIC when replacing newly assembled MIs
- 2025-10-03 5eb1962481de [UEMHC] Re-enabled baked grooms by baking them to a separate texture ahead of the skin material bake. This saves 2 SRVs in the skin material and gets it back below the limit.
- 2025-10-03 c608384cda0b [UEMHC] Fixed crash when groom already has decimation settings applied

### 维护评价

- **创建时间**：2025年3月，非常新的插件。
- **最近更新**：最近一次更新在2025年10月，且提交信息显示是针对具体功能（毛发烘焙、材质实例管理、崩溃修复）的实质性改进，表明处于**活跃开发**阶段。
- **实验性**：插件标记为 `IsBetaVersion: true`，且默认未启用，说明它仍处于测试和完善阶段，API和功能可能会发生变化。
- **推荐使用**：如果你正在使用 MetaHuman 工作流，并且愿意跟进 Beta 版本的更新和潜在问题，那么强烈推荐使用此插件，它是 Epic 官方提供的、功能最完整的 MetaHuman 集成方案。对于生产环境，建议密切关注其版本更新和已知问题。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.6/Engine/Plugins/MetaHuman/MetaHumanCharacter)
- [官方文档]() (暂无)
- [测试用例]() (未在提供的路径中发现)