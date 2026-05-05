# Chaos Outfit Asset

> Outfit Asset plugin to create and assemble outfits made of Cloth Assets.

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、服装数据） |
| 模块 | `ChaosOutfitAssetDataflowNodes` (Runtime), `ChaosOutfitAssetEditor` (Runtime), `ChaosOutfitAssetEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosOutfitAsset) | |

## 用途

Chaos Outfit Asset 插件用于创建和管理基于 Chaos 布料模拟系统的服装资产。它解决的核心问题是**角色服装的尺码适配与组装**。传统上，为不同体型的角色制作服装需要为每个体型单独创建一套服装资产，工作量巨大。此插件引入了“尺码化服装”（Sized Outfit）的概念，允许美术师为一件服装（如一件夹克）创建多个尺码版本（如 S, M, L），并利用**径向基函数（RBF）插值算法**，在运行时根据角色的实际身体测量数据（如胸围、腰围）动态调整服装网格，使其适配任意体型。此外，它支持将多个服装部件（如上衣、裤子、配饰）组装成一个完整的“套装”（Outfit），并统一管理其布料模拟参数和物理资产。

## 使用场景

- **角色自定义系统**：你的游戏允许玩家自定义角色体型（如身高、胖瘦），需要服装能够实时适配这些变化，而无需为每种体型预烘焙不同的服装网格。
- **动态服装组装**：你需要将来自不同来源的服装部件（例如，来自不同 DLC 或玩家购买的物品）动态组合成一个完整的、可进行物理模拟的套装。
- **MetaHuman 或类似高保真角色工作流**：在使用 MetaHuman 等预制角色系统时，需要服装能够精确适配其合并后的身体和头部网格体，并支持布料模拟。
- **服装资产库管理**：你需要一个统一的资产格式来管理一件服装的所有尺码变体及其组成部件，简化资产管理和加载流程。

## 蓝图用法

该插件主要面向 C++ 和编辑器工具开发，直接暴露给蓝图的节点较少。核心数据结构 `FChaosSizedOutfitSource` 被标记为 `BlueprintType`，可在蓝图中作为变量使用。

### 核心结构

| 结构/类 | 说明 | 所在模块 |
|---|---|---|
| `FChaosSizedOutfitSource` | 用于定义单个尺码服装的输入结构，包含源资产、尺码名称、身体部件网格体列表和 RBF 插值点数。 | `ChaosOutfitAssetEngine` |
| `UChaosOutfitAsset` | 最终的服装资产类，继承自 `UChaosClothAssetBase`，可被骨骼网格体组件使用。 | `ChaosOutfitAssetEngine` |

### 使用示例（蓝图描述）

在蓝图中，你通常不会直接操作 `UChaosOutfitAsset`，而是通过编辑器工具或 C++ 代码来构建它。一个典型的工作流是：
1.  创建一个 `FChaosSizedOutfitSource` 变量数组。
2.  为每个目标尺码（如 “Small”, “Medium”）填充一个 `FChaosSizedOutfitSource` 结构体，指定对应的 `SourceAsset`（服装资产）和 `SourceBodyParts`（该尺码对应的身体网格体）。
3.  将这些结构体传递给 C++ 层或编辑器工具，用于构建最终的 `UChaosOutfitAsset`。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosOutfitAsset/OutfitAsset.h"
#include "ChaosOutfitAsset/Outfit.h"
#include "ChaosOutfitAsset/SizedOutfitSource.h"
```

### 基本用法

以下代码演示了如何从多个尺码的服装源资产构建一个 `UChaosOutfitAsset`。

```cpp
// 假设你已经获取了指向源服装资产和身体网格体的指针
// UChaosClothAssetBase* SmallSizeAsset;
// UChaosClothAssetBase* MediumSizeAsset;
// USkeletalMesh* SmallBodyMesh;
// USkeletalMesh* MediumBodyMesh;

// 1. 准备尺码化服装源数据
TArray<FChaosSizedOutfitSource> SizedOutfitSources;

FChaosSizedOutfitSource& SmallSource = SizedOutfitSources.AddDefaulted_GetRef();
SmallSource.SourceAsset = SmallSizeAsset;
SmallSource.SizeName = TEXT("Small");
SmallSource.SourceBodyParts.Add(SmallBodyMesh);
SmallSource.NumResizingInterpolationPoints = 1500; // 使用默认值

FChaosSizedOutfitSource& MediumSource = SizedOutfitSources.AddDefaulted_GetRef();
MediumSource.SourceAsset = MediumSizeAsset;
MediumSource.SizeName = TEXT("Medium");
MediumSource.SourceBodyParts.Add(MediumBodyMesh);

// 2. 创建一个临时的 UChaosOutfit 对象来组装这些尺码
UChaosOutfit* TempOutfit = NewObject<UChaosOutfit>();
for (const FChaosSizedOutfitSource& Source : SizedOutfitSources)
{
    TempOutfit->Add(Source);
}

// 3. 创建最终的服装资产并构建
UChaosOutfitAsset* OutfitAsset = NewObject<UChaosOutfitAsset>();
OutfitAsset->Build(TempOutfit);
// OutfitAsset 现在可以保存到磁盘或用于运行时模拟。
```

### 进阶用法

使用 `CollectionOutfitFacade` 来查询已构建服装资产的尺码信息，以实现运行时尺码匹配。

```cpp
#include "ChaosOutfitAsset/CollectionOutfitFacade.h"

// 假设 OutfitAsset 是一个已构建的 UChaosOutfitAsset
const FManagedArrayCollection& Collection = OutfitAsset->GetOutfitCollection();
UE::Chaos::OutfitAsset::FCollectionOutfitConstFacade Facade(Collection);

if (Facade.IsValid())
{
    // 获取所有可用的尺码名称
    TArray<FGuid> OutfitGuids = Facade.GetOutfitGuids();
    for (const FGuid& Guid : OutfitGuids)
    {
        TArray<int32> BodySizes = Facade.GetOutfitBodySizes(Guid);
        for (int32 SizeIndex : BodySizes)
        {
            FString SizeName = Facade.GetBodySizeName(SizeIndex);
            UE_LOG(LogTemp, Log, TEXT("Outfit has size: %s"), *SizeName);
        }
    }

    // 根据角色身体的测量数据查找最接近的尺码
    TMap<FString, float> CharacterMeasurements;
    CharacterMeasurements.Add(TEXT("chest"), 95.0f);
    CharacterMeasurements.Add(TEXT("waist"), 80.0f);
    // ... 添加其他测量值

    int32 ClosestSizeIndex = Facade.FindClosestBodySize(CharacterMeasurements);
    if (ClosestSizeIndex != INDEX_NONE)
    {
        FString ClosestSizeName = Facade.GetBodySizeName(ClosestSizeIndex);
        UE_LOG(LogTemp, Log, TEXT("Best matching size for character: %s"), *ClosestSizeName);
        // 使用此尺码索引来获取对应的服装部件或进行其他操作
    }
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何定义服装源并构建资产。

**OutfitDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "ChaosOutfitAsset/SizedOutfitSource.h"

class UChaosClothAssetBase;
class USkeletalMesh;
class UChaosOutfitAsset;

class FOutfitDemo
{
public:
    /** 创建一个包含两个尺码的示例服装资产 */
    static UChaosOutfitAsset* CreateDemoOutfitAsset(
        UChaosClothAssetBase* SmallAsset,
        USkeletalMesh* SmallBody,
        UChaosClothAssetBase* LargeAsset,
        USkeletalMesh* LargeBody);
};
```

**OutfitDemo.cpp**
```cpp
#include "OutfitDemo.h"
#include "ChaosOutfitAsset/OutfitAsset.h"
#include "ChaosOutfitAsset/Outfit.h"
#include "UObject/Package.h"

UChaosOutfitAsset* FOutfitDemo::CreateDemoOutfitAsset(
    UChaosClothAssetBase* SmallAsset,
    USkeletalMesh* SmallBody,
    UChaosClothAssetBase* LargeAsset,
    USkeletalMesh* LargeBody)
{
    // 1. 准备尺码数据
    TArray<FChaosSizedOutfitSource> Sources;

    FChaosSizedOutfitSource& Small = Sources.AddDefaulted_GetRef();
    Small.SourceAsset = SmallAsset;
    Small.SizeName = TEXT("S");
    Small.SourceBodyParts.Add(SmallBody);

    FChaosSizedOutfitSource& Large = Sources.AddDefaulted_GetRef();
    Large.SourceAsset = LargeAsset;
    Large.SizeName = TEXT("L");
    Large.SourceBodyParts.Add(LargeBody);

    // 2. 组装到临时 Outfit 对象
    UChaosOutfit* TempOutfit = NewObject<UChaosOutfit>(GetTransientPackage());
    for (const auto& Source : Sources)
    {
        TempOutfit->Add(Source);
    }

    // 3. 构建最终资产
    UChaosOutfitAsset* FinalAsset = NewObject<UChaosOutfitAsset>(GetTransientPackage(), NAME_None, RF_Public | RF_Standalone);
    FinalAsset->Build(TempOutfit);

    return FinalAsset;
}
```

## 模块依赖

要使用 `ChaosOutfitAssetEngine` 模块，你的项目模块需要在 `Build.cs` 中添加以下依赖：

| 模块 | 用途 |
|---|---|
| `ChaosClothAsset` | 核心的 Chaos 布料资产基类和模拟模型。 |
| `GeometryCollection` | 提供 `FManagedArrayCollection`，用于存储服装集合的复杂数据。 |
| `Chaos` | Chaos 物理系统核心模块。 |
| `ClothCollision` | 布料碰撞相关功能。 |

## 维护状态

### 近期更新

- 2026-04-22 `11dbcfb1` [Chaos Outfit Asset] Moved tthe ChaosOutfitAsset plugin out of Experimental and made it Beta.

### 维护评价

- **状态**：**实验性/Beta**。这是一个非常新的插件，版本号为 0.1，明确标记为实验性且默认禁用。
- **活跃度**：预计处于**活跃开发**中，因为它是 Epic Games 为支持下一代角色服装工作流（如 MetaHuman）而开发的关键组件。
- **推荐度**：**谨慎评估后使用**。适合用于原型开发或对最新技术栈有需求的项目。由于是实验性 API，未来版本可能会有重大变更。不建议用于需要长期稳定维护的生产项目，除非你有能力跟踪和适配其 API 变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosOutfitAsset)
- [官方文档]() (暂无)
- [测试用例]() (在提供的源码片段中未发现，可能位于 `Engine/Tests/` 目录下)