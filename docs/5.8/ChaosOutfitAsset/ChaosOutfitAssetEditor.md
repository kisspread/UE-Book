# Chaos Outfit Asset

> Outfit Asset plugin to create and assemble outfits made of Cloth Assets.

| 属性 | 值 |
|---|---|
| 分类 | Physics |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（服装资产） |
| 模块 | `ChaosOutfitAssetDataflowNodes` (Runtime), `ChaosOutfitAssetEditor` (Runtime), `ChaosOutfitAssetEngine` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2026-04-22 |
| 年龄标签 | 🆕（约 0 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosOutfitAsset) | |

## 用途

该插件是基于 Chaos 布料系统的**服装资产编辑器**。它解决的核心问题是：在 Chaos 布料系统中，如何将多个独立的布料网格体（Cloth Assets）组合、管理并预览为一个完整的、可穿戴的服装（Outfit）。

它不仅仅是一个资产容器，更是一个编辑器工具集，允许设计师和开发者在编辑器中直观地创建、组装和编辑由多个布料部件构成的复杂服装，并支持在编辑器中实时预览布料模拟效果。这为角色换装、服装定制等需要复杂布料交互的功能提供了底层资产和工作流支持。

## 使用场景

- 你正在开发一个角色换装系统，需要将上衣、裤子、裙子等多个独立的布料部件组合成一套完整的服装，并确保它们在物理模拟时能正确交互。
- 你需要为角色创建一套复杂的、由多层布料构成的服装（如婚纱、盔甲下的内衬），并希望在编辑器中预览整体效果。
- 你的项目使用了 Chaos 布料系统，并希望有一个标准化的资产格式来管理和复用服装配置。

## 蓝图用法

该插件的核心功能主要通过编辑器界面和资产操作实现，直接暴露给蓝图的可调用函数较少。主要的交互发生在资产编辑器（Outfit Editor）中。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `OpenAssets` | 在服装资产编辑器中打开指定的服装资产进行编辑。 | `UAssetDefinition_OutfitAsset` |

### 使用示例（蓝图描述）

1.  **创建服装资产**：在内容浏览器中右键，选择 `Physics` -> `Outfit Asset` 来创建一个新的 `ChaosOutfitAsset`。
2.  **编辑服装资产**：双击创建的资产，会打开服装资产编辑器窗口。
3.  **组装服装**：在编辑器中，你可以将其他 `Cloth Asset` 拖拽到服装资产的部件列表中，完成服装的组装。
4.  **预览**：在编辑器视口中，可以实时预览组装后服装的布料模拟效果。

## C++ 用法

### 头文件引入

```cpp
#include "ChaosOutfitAsset/AssetDefinition_OutfitAsset.h"
#include "ChaosOutfitAsset/OutfitAssetFactory.h"
```

### 基本用法

以下代码展示了如何在 C++ 中以编程方式创建一个新的服装资产。这模拟了编辑器中“新建资产”的操作。

```cpp
// 来源：基于 UChaosOutfitAssetFactory::FactoryCreateNew 的逻辑推断
#include "ChaosOutfitAsset/OutfitAssetFactory.h"
#include "ChaosOutfitAssetEngine/ChaosOutfitAsset.h" // 假设的资产类头文件

void CreateNewOutfitAsset()
{
    // 获取工厂类
    UClass* FactoryClass = UChaosOutfitAssetFactory::StaticClass();
    UChaosOutfitAssetFactory* Factory = NewObject<UChaosOutfitAssetFactory>(GetTransientPackage(), FactoryClass);

    // 设置创建参数
    UClass* AssetClass = UChaosOutfitAsset::StaticClass(); // 假设的资产类
    UObject* Parent = GetTransientPackage(); // 或者指定一个有效的包路径
    FName Name = TEXT("MyNewOutfit");
    EObjectFlags Flags = RF_Public | RF_Standalone;

    // 创建资产
    UObject* NewAsset = Factory->FactoryCreateNew(AssetClass, Parent, Name, Flags, nullptr, GWarn);

    if (UChaosOutfitAsset* OutfitAsset = Cast<UChaosOutfitAsset>(NewAsset))
    {
        // 在此处对新创建的服装资产进行操作
        // 例如：保存到磁盘
        FString PackagePath = FPackageName::GetLongPackagePath(Parent->GetPathName());
        FString AssetName = Name.ToString();
        UPackage* Package = CreatePackage(*FPaths::Combine(PackagePath, AssetName));
        OutfitAsset->Rename(*AssetName, Package);
        FAssetRegistryModule::AssetCreated(OutfitAsset);
        Package->MarkPackageDirty();
        // ... 保存逻辑
    }
}
```

### 进阶用法

服装资产的核心操作是管理其包含的布料部件。虽然具体的 API 需要查看 `ChaosOutfitAssetEngine` 模块，但工作流通常如下：

```cpp
// 假设的进阶用法，需要 ChaosOutfitAssetEngine 模块的具体 API
#include "ChaosOutfitAssetEngine/ChaosOutfitAsset.h"
#include "ChaosClothAsset/ClothAsset.h"

void AssembleOutfit(UChaosOutfitAsset* OutfitAsset, const TArray<UClothAsset*>& ClothParts)
{
    if (!OutfitAsset) return;

    // 清空现有部件（假设的 API）
    // OutfitAsset->ClearClothParts();

    // 添加新的布料部件
    for (UClothAsset* ClothPart : ClothParts)
    {
        if (ClothPart)
        {
            // 假设的 API：将布料资产添加到服装中
            // OutfitAsset->AddClothPart(ClothPart);
        }
    }

    // 重新构建或更新服装的物理表示（假设的 API）
    // OutfitAsset->RebuildOutfit();
}
```

## Demo 示例

一个最小化的 C++ 示例，展示如何创建服装资产并为其添加一个布料部件。

**OutfitDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "Subsystems/GameInstanceSubsystem.h"
#include "OutfitDemo.generated.h"

class UChaosOutfitAsset;
class UClothAsset;

UCLASS()
class UOutfitDemoSubsystem : public UGameInstanceSubsystem
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintCallable, Category = "Outfit Demo")
    void CreateAndPopulateOutfit();

private:
    UPROPERTY()
    TObjectPtr<UChaosOutfitAsset> DemoOutfitAsset;
};
```

**OutfitDemo.cpp**
```cpp
#include "OutfitDemo.h"
#include "ChaosOutfitAssetEngine/ChaosOutfitAsset.h"
#include "ChaosClothAsset/ClothAsset.h"
#include "AssetRegistry/AssetRegistryModule.h"
#include "UObject/SavePackage.h"

void UOutfitDemoSubsystem::CreateAndPopulateOutfit()
{
    // 1. 创建服装资产包
    UPackage* Package = CreatePackage(TEXT("/Game/Demo/MyOutfit"));
    DemoOutfitAsset = NewObject<UChaosOutfitAsset>(Package, TEXT("MyOutfit"), RF_Public | RF_Standalone);

    // 2. 假设我们已经有一个布料资产
    // UClothAsset* ShirtCloth = LoadObject<UClothAsset>(nullptr, TEXT("/Game/ClothAssets/Shirt_Cloth"));

    // 3. 将布料部件添加到服装中 (API 为假设)
    // if (ShirtCloth && DemoOutfitAsset)
    // {
    //     DemoOutfitAsset->AddClothPart(ShirtCloth);
    // }

    // 4. 标记资产为已修改并保存
    if (DemoOutfitAsset)
    {
        FAssetRegistryModule::AssetCreated(DemoOutfitAsset);
        Package->MarkPackageDirty();

        // 保存包
        FString PackageFileName = FPackageName::LongPackageNameToFilename(
            Package->GetName(), FPackageName::GetAssetPackageExtension());
        FSavePackageArgs SaveArgs;
        SaveArgs.TopLevelFlags = RF_Public | RF_Standalone;
        UPackage::SavePackage(Package, DemoOutfitAsset, *PackageFileName, SaveArgs);
    }
}
```

## 模块依赖

要使用此插件，你的模块需要依赖以下**独特**模块（已在 `Build.cs` 的 `PublicDependencyModuleNames` 或 `PrivateDependencyModuleNames` 中声明）：

| 模块 | 用途 |
|---|---|
| `ChaosOutfitAssetEngine` | 服装资产的核心运行时逻辑和数据结构。 |
| `ChaosClothAsset` | Chaos 布料资产系统，服装由其构成。 |
| `ChaosOutfitAssetDataflowNodes` | 提供用于服装资产处理的 Dataflow 节点（如果使用 Dataflow）。 |
| `CharacterFXEditor` | 编辑器模块依赖，用于构建服装资产编辑器界面。 |

## 维护状态

### 近期更新

- 2026-04-22 `11dbcfb1` [Chaos Outfit Asset] Moved tthe ChaosOutfitAsset plugin out of Experimental and made it Beta.

### 维护评价

- **状态**：**实验性/Beta**。这是一个非常新的插件，标记为 Beta 版本且默认未启用。
- **活跃度**：预计处于**活跃开发**中，因为它是 Chaos 布料系统的重要扩展。
- **推荐度**：**谨慎使用**。适合用于原型开发和功能预览。由于是实验性功能，API 和资产格式可能在后续版本中发生重大变更。不建议在需要长期稳定性的生产项目中作为核心依赖。
- **已知限制**：作为 Beta 产品，可能存在功能不完整、性能问题或未文档化的边界情况。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/ChaosOutfitAsset)
- 官方文档：暂无
- 测试用例：暂未发现公开的测试用例路径。