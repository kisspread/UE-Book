# Variant Manager Content

> Data classes and assets for the Variant Manager plugin

| 属性 | 值 |
|---|---|
| 中文名 | 变体管理器内容 |
| 分类 | Editor |
| 默认启用 | ✅ 是 |
| 包含内容 | ✅ 有（数据类资产） |
| 模块 | `VariantManagerContent` (Runtime), `VariantManagerContentEditor` (Editor) |
| 实验性 | ⚦ 是 |
| 创建时间 | 2018-09-04 |
| 年龄标签 | 👴 老古董（约 7 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent) | |

## 用途

本插件是 Datasmith 和 Variant Manager 生态系统的核心组成部分。它并不直接提供编辑器界面或工作流，而是作为 **底层数据支持**，为 `VariantManager` 插件定义了必要的数据类（如 `ULevelVariantSets`， `UVariant`， `UVariantSet`）和相关的资产类型。它与 `VariantManager` 插件紧密耦合，后者负责提供创建、管理和应用变体的实际 UI 和逻辑。因此，`VariantManagerContent` 是 `VariantManager` 插件能够运行的 **基础**。

## 使用场景

当你的项目需要使用 **Variant Manager**（变体管理器）插件时，`VariantManagerContent` 会被自动依赖并启用。典型应用场景包括：
- **产品配置器**：在汽车、家具或电子产品可视化中，快速切换不同的颜色、材质、部件或配置。
- **建筑可视化**：在同一个场景中展示不同的设计方案、光照条件或家具布局。
- **虚拟演播室或展会**：一键切换整个场景的布景、灯光或显示内容。
- **数据驱动原型**：基于导入的 CAD 数据（通过 Datasmith）或自定义数据，创建可交互的配置原型。

## 蓝图用法

此插件的核心是数据类，不直接提供大量独立的蓝图节点。蓝图的使用主要通过 `VariantManager` 插件提供的节点来创建和操控这些数据对象（如创建新的变体集或变体）。具体的操作节点和逻辑请参考 `VariantManager` 插件的文档。

## C++ 用法

### 头文件引入

要使用此插件提供的数据类，需要在模块依赖中添加 `VariantManagerContent`。

```cpp
#include "LevelVariantSets.h"
#include "Variant.h"
#include "VariantSet.h"
// 其他相关头文件...
```

### 基本用法

数据类的创建和管理通常由 `VariantManager` 编辑器插件在编辑器中处理。在运行时，主要的使用模式是**加载和应用**已配置好的变体集。

```cpp
// 假设已经有一个 ULevelVariantSets 资产的引用
ULevelVariantSets* MyVariantSets = LoadObject<ULevelVariantSets>(nullptr, TEXT("/Game/Path/To/MyLevelVariantSets"));

if (MyVariantSets)
{
    // 获取第一个变体集
    UVariantSet* VariantSet = MyVariantSets->GetVariantSet(0);
    if (VariantSet)
    {
        // 获取第一个变体并应用
        UVariant* Variant = VariantSet->GetVariant(0);
        if (Variant)
        {
            Variant->SetSwitchOn(this); // `this` 通常是拥有上下文的Actor或对象
        }
    }
}
```

## 模块列表

- **[`VariantManagerContent`](VariantManagerContent.md)** (Runtime)：核心运行时模块，定义了 `ULevelVariantSets`、`UVariant`、`UVariantSet` 等基础数据类。这些类负责存储变体的逻辑和与场景Actor的绑定关系。
- **[`VariantManagerContentEditor`](VariantManagerContentEditor.md)** (Editor)：编辑器模块，为上述数据类提供编辑器专用的功能支持，包括资产的自定义外观、缩略图渲染、资产操作（如合并）等。**注意**：虽然 `.uplugin` 中将此模块类型标记为 `Runtime`，但根据其名称和编辑器插件的典型模式，其实际作用域主要在编辑器阶段。

## 使用示例（蓝图描述）

在蓝图中，你通常不直接操作 `VariantManagerContent` 的类，而是使用 `VariantManager` 插件提供的节点：
1.  使用“Get Level Variant Sets”节点从资产引用中获取一个 `ULevelVariantSets` 对象。
2.  使用“Get Variant Set”节点获取特定的变体集。
3.  使用“Get Variant”或“Get Variants”节点获取变体。
4.  使用“Switch On”或“Switch Off”节点来应用或取消应用变体的效果。
5.  在事件图表中，通过这些节点构建配置选择逻辑。

## Demo 示例

一个完整的示例通常涉及 `VariantManager` 插件。在 C++ 中，你可能会在游戏逻辑中读取并应用配置：

**MyActor.h**
```cpp
#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MyActor.generated.h"

class ULevelVariantSets;

UCLASS()
class AMyActor : public AActor
{
    GENERATED_BODY()

public:
    AMyActor();

    virtual void BeginPlay() override;

    UPROPERTY(EditAnywhere, Category = "Variants")
    TSoftObjectPtr<ULevelVariantSets> LevelVariantSetsAsset;

    UPROPERTY(EditAnywhere, Category = "Variants")
    FString VariantSetToActivate;

    UPROPERTY(EditAnywhere, Category = "Variants")
    FString VariantToActivate;

    UFUNCTION(BlueprintCallable, Category = "Variants")
    void ActivateSelectedVariant();
};
```

**MyActor.cpp**
```cpp
#include "MyActor.h"
#include "LevelVariantSets.h"
#include "VariantSet.h"
#include "Variant.h"

AMyActor::AMyActor()
{
    PrimaryActorTick.bCanEverTick = false;
}

void AMyActor::BeginPlay()
{
    Super::BeginPlay();
}

void AMyActor::ActivateSelectedVariant()
{
    ULevelVariantSets* LVS = LevelVariantSetsAsset.LoadSynchronous();
    if (!LVS) return;

    UVariantSet* VS = LVS->GetVariantSet(FName(*VariantSetToActivate));
    if (!VS) return;

    UVariant* V = VS->GetVariant(FName(*VariantToActivate));
    if (V)
    {
        // 应用变体，传递当前 Actor 作为上下文
        V->SetSwitchOn(this);
    }
}
```

## 模块依赖

此插件本身依赖较少，主要是 `VariantManager` 和 `Datasmith` 的核心模块。要使用它提供的类，你的项目需要依赖以下模块：

| 模块 | 用途 |
|---|---|
| `VariantManager` | 变体管理器核心逻辑模块，提供操作变体的主要蓝图和 C++ API |
| `DatasmithContent` | 如果变体是基于导入的 Datasmith CAD 数据，则需要此模块 |
| `PropertyPath` | 用于解析和操作属性路径（如 `UVariant` 如何绑定到 Actor 属性） |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-05-12 | `0a77223b` | Fixed crash in LevelVariantSet.cpp | 修复了 LevelVariantSet 中的崩溃问题 |
| 2026-04-16 | `0b4d09a4` | [ContentBrowser] New Add Menu Data Menu | 内容浏览器中新增了数据菜单 |
| 2026-04-14 | `50042443` | TLazyObjectPtr Deprecation: | 对 TLazyObjectPtr 进行了废弃标记 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将旧版日志宏 UE_LOG 迁移为 UE_LOGF |
| 2026-03-20 | `c5bb9adf` | [AutoViz] Minor updates to Variant Manager | 对变体管理器进行了小的更新 |

### 维护评价

- **实验性警告**：此插件的 `.uplugin` 文件中 `IsBetaVersion` 设置为 `true`，表明其 API 和功能可能仍处于测试阶段，未来版本可能发生不兼容的更改。
- **活跃维护**：从 git 历史看，近几个月仍有功能更新和重要的崩溃修复，表明它仍在 **积极维护** 中。
- **核心依赖**：它是 `VariantManager` 插件不可或缺的组成部分。如果你的项目使用了 `VariantManager`，则必然会加载此插件。
- **推荐使用**：对于需要使用变体管理功能的项目（尤其是企业级可视化、产品配置器），推荐使用。但需注意其 **Beta** 状态，并关注官方文档和更新日志。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent)
- [官方文档](https://docs.unrealengine.com/en-US/WorkingWithContent/Importing/Datasmith/)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Enterprise/VariantManagerContent/Tests) (如果存在)