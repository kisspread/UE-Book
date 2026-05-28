# Interaction Interface

> Interaction Interface

| 属性 | 值 |
|---|---|
| 中文名 | 交互接口 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（运行时模块） |
| 模块 | `InteractableInterface` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/InteractionInterface) | |

## 用途

该插件提供了一套标准化的框架，用于在游戏世界中定义、查询和触发交互。它解决的核心问题是：为游戏中常见的“玩家与物体交互”（如开门、拾取物品、与NPC对话）提供一套统一、可扩展的底层架构。开发者无需从零开始构建交互逻辑，可以直接使用该插件定义好的接口（`IInteractionTarget`、`IInteractableInstigator`）、组件（`UInteractionTargetComponent`, `UInteractionInstigatorComponent`）和工具函数库（`UInteractableInterfaceLibrary`），从而专注于游戏特定的交互逻辑实现。

## 使用场景

- 你的游戏包含大量可交互物体（宝箱、门、开关、可拾取道具等），需要一套标准化管理方式。
- 你使用 Gameplay Ability System (GAS)，并希望将交互能力（Ability）与其他游戏能力统一管理。
- 你需要在运行时动态查询玩家附近可交互的目标，并更新UI提示。

## 蓝图用法

该插件主要通过 `UInteractableInterfaceLibrary` 提供蓝图节点，以及通过 `UInteractionTargetComponent` 和 `UInteractionInstigatorComponent` 提供组件化的蓝图事件。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Interactable Targets From Actor` | 从给定的 Actor 身上获取所有实现了 `IInteractionTarget` 接口的组件或子对象。 | `UInteractableInterfaceLibrary` |
| `Append Target Configuration` | 查询一个交互目标的具体配置信息（例如名称、可用操作），并将结果添加到输出结构体中。 | `UInteractableInterfaceLibrary` |
| `Begin Interaction On Target` | 对一个交互目标触发交互。 | `UInteractableInterfaceLibrary` |
| `Attempt To Begin Interactions` | 通过交互发起组件，尝试与一组目标开始交互。 | `UInteractionInstigatorComponent` |
| `BP Append Target Configuration` | 交互目标组件上的蓝图可重写函数，用于定义该目标的配置信息。 | `UInteractionTargetComponent` |
| `BP Begin Interaction` | 交互目标组件上的蓝图可重写函数，用于定义交互发生时的具体行为。 | `UInteractionTargetComponent` |

### 使用示例（蓝图描述）

1.  **设置可交互物体**：将 `UInteractionTargetComponent` 添加到你的 Actor（如宝箱）上。在该组件的“事件图表”中，重写 `BP Append Target Configuration` 事件，设置 `TargetConfigs` 数组来定义宝箱的交互配置（如“打开”）。
2.  **设置玩家**：将 `UInteractionInstigatorComponent` 添加到玩家角色上。
3.  **发现目标**：在玩家角色的 Ability 蓝图中，添加 `UAbilityTask_GrantNearbyInteractionData` 任务。连接其 `OnAvailableInteractionTargetsChanged` 委托，当附近有可交互物体时，该委托会触发，并传入可用的目标列表。
4.  **触发交互**：在游戏逻辑（例如输入事件）中，调用玩家角色上 `UInteractionInstigatorComponent` 的 `Attempt To Begin Interactions` 节点，传入你想要交互的目标列表。这将最终触发目标物体上的 `BP Begin Interaction` 事件。

## C++ 用法

### 头文件引入

```cpp
#include "InteractableInterfaceLibrary.h"
#include "InteractableTargetInterface.h"
#include "InteractableInstigator.h"
#include "InteractionTypes.h"
#include "InteractionTargetComponent.h"
#include "InteractionInstigatorComponent.h"
```

### 基本用法：实现一个交互目标

创建一个自定义类，实现 `IInteractionTarget` 接口。

```cpp
// MyInteractableActor.h
#pragma once
#include "GameFramework/Actor.h"
#include "InteractableTargetInterface.h"
#include "MyInteractableActor.generated.h"

UCLASS()
class AMyInteractableActor : public AActor, public IInteractionTarget
{
    GENERATED_BODY()
public:
    AMyInteractableActor();

protected:
    // 实现 IInteractionTarget 接口
    virtual void AppendTargetConfiguration(const FInteractionContext& Context, FInteractionQueryResults& OutResults) const override;
    virtual void BeginInteraction(const FInteractionContext& Context) override;

    UPROPERTY(EditAnywhere, Category = "Interaction")
    FText MyDisplayName;
};
```

```cpp
// MyInteractableActor.cpp
#include "MyInteractableActor.h"
#include "InteractionTypes.h"

AMyInteractableActor::AMyInteractableActor()
{
    // 可以添加一个 UInteractionTargetComponent 来自动处理碰撞查询
    // 或者完全手动处理
}

void AMyInteractableActor::AppendTargetConfiguration(const FInteractionContext& Context, FInteractionQueryResults& OutResults) const
{
    // 创建一个基础配置结构体
    FInteractionTargetConfiguration Config;
    Config.DisplayName = MyDisplayName;
    
    // 将配置添加到输出结果中
    OutResults.AvailableInteractions.Add(FInstancedStruct::Make(Config));
}

void AMyInteractableActor::BeginInteraction(const FInteractionContext& Context)
{
    // 实现你的交互逻辑，例如播放动画、销毁自身等
    UE_LOG(LogTemp, Log, TEXT("Interaction began on %s"), *GetName());
}
```

### 进阶用法：查询与触发交互

```cpp
// 在某个 Ability 或游戏逻辑中查询并触发交互
void SomeGameplayClass::QueryAndTriggerInteraction(AActor* InstigatorActor)
{
    // 1. 获取 Actor 上的交互目标
    TArray<TScriptInterface<IInteractionTarget>> Targets;
    UInteractableInterfaceLibrary::GetInteractableTargetsFromActor(SomeTargetActor, Targets);

    if (Targets.Num() > 0)
    {
        // 2. 查询第一个目标的配置
        FInteractionQueryResults Results;
        FInteractionContext Context;
        Context.Instigator = InstigatorActor->FindComponentByClass<UInteractionInstigatorComponent>(); // 需要一个发起者接口
        UInteractableInterfaceLibrary::AppendTargetConfiguration(Targets[0], Context, Results);

        // 3. 检查配置并决定是否交互
        if (Results.AvailableInteractions.Num() > 0)
        {
            // 4. 触发交互
            UInteractableInterfaceLibrary::BeginInteractionOnTarget(Targets[0], Context);
        }
    }
}
```

## Demo 示例

一个简单的可交互宝箱 Actor。

```cpp
// TreasureChest.h
#pragma once
#include "GameFramework/Actor.h"
#include "InteractableTargetInterface.h"
#include "TreasureChest.generated.h"

UCLASS()
class ATreasureChest : public AActor, public IInteractionTarget
{
    GENERATED_BODY()
public:
    ATreasureChest();

    // 实现接口
    virtual void AppendTargetConfiguration(const FInteractionContext& Context, FInteractionQueryResults& OutResults) const override;
    virtual void BeginInteraction(const FInteractionContext& Context) override;

protected:
    UPROPERTY(VisibleAnywhere, Category = "Interaction")
    class UInteractionTargetComponent* InteractionTargetComponent;

    UPROPERTY(EditAnywhere, Category = "Interaction")
    int32 GoldAmount = 100;

    bool bIsOpened = false;
};
```

```cpp
// TreasureChest.cpp
#include "TreasureChest.h"
#include "InteractionTargetComponent.h"
#include "InteractionTypes.h"

ATreasureChest::ATreasureChest()
{
    InteractionTargetComponent = CreateDefaultSubobject<UInteractionTargetComponent>(TEXT("InteractionTarget"));
    RootComponent = InteractionTargetComponent;
}

void ATreasureChest::AppendTargetConfiguration(const FInteractionContext& Context, FInteractionQueryResults& OutResults) const
{
    if (bIsOpened) return; // 已打开则不添加配置

    FInteractionTargetConfiguration Config;
    Config.DisplayName = FText::FromString(TEXT("打开宝箱"));
    OutResults.AvailableInteractions.Add(FInstancedStruct::Make(Config));
}

void ATreasureChest::BeginInteraction(const FInteractionContext& Context)
{
    if (bIsOpened) return;

    bIsOpened = true;
    UE_LOG(LogTemp, Log, TEXT("宝箱被打开，获得 %d 金币！"), GoldAmount);
    // 这里可以添加金币添加到玩家背包、播放开箱动画等逻辑
}
```

## 模块依赖

该插件依赖于其他特定插件和模块，使用时需在项目的 `.uproject` 或模块的 `Build.cs` 中进行声明。

| 模块 | 用途 |
|---|---|
| `GameplayAbilities` | 插件中的 Ability 任务和 Gameplay Ability 类依赖此模块。 |
| `SmartObjects` | 插件的依赖项之一，表明其设计可能与智能对象系统有关联或未来会集成。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到新的 UE_LOGF 格式。 |
| 2024-09-17 | `f4537894` | Enter the beginning phase of the Interactable Interface plugin. Still in active development! | 插件初始创建，进入开发初期阶段。 |

### 维护评价

该插件于 2024 年 9 月创建，目前仍标记为 **实验性** (`IsExperimentalVersion: true`) 且默认未启用 (`EnabledByDefault: false`)。从 Git 历史看，仅有一次初始提交和一次日志迁移更新，表明其仍处于**早期开发阶段**，API 和功能可能不稳定，会有变动。

**不推荐**在正式生产项目中依赖此插件。适用于对 UE5 新功能进行原型开发、技术验证，或愿意接受未来 API 变更风险的开发者。建议持续关注 Epic 的更新日志以了解其成熟度变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Experimental/InteractionInterface)
- 测试用例：暂无（插件目录内未发现标准测试文件）