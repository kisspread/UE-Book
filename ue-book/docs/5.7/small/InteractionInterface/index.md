# Interaction Interface

> Interaction Interface

| 属性 | 值 |
|---|---|
| 中文名 | 交互接口系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产、组件模板） |
| 模块 | `InteractableInterface` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2024-09-17 |
| 年龄标签 | 🆕（约 1 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InteractionInterface) | |

## 用途

**Interaction Interface** 提供了一套通用、可扩展的交互框架，用于在游戏中实现“发起者（Instigator）”与“可交互目标（Target）”之间的交互逻辑。  
该插件解决以下核心问题：

- 将“谁可以交互”和“什么可以被交互”解耦，通过接口让任何 Actor 或组件成为交互发起者或目标。
- 提供标准化的查询、配置和执行流程，方便构建 UI 提示、条件判断、交互动效等。
- 集成 SmartObjects 和 GameplayAbilities 生态，支持基于能力的交互任务和智能对象的交互规则。

## 使用场景

- **开放世界探索**：玩家靠近 NPC、宝箱、可拾取物时，自动扫描并显示可交互选项。
- **上下文相关交互**：根据不同条件（如玩家是否持有钥匙、是否完成前置任务）动态改变交互行为和反馈。
- **技能驱动的交互**：利用 GameplayAbility 实现复杂交互（如撬锁、对话、砍树），并支持能力任务轮询周围目标。
- **模块化交互组件**：为任意 Actor 添加 `UInteractionTargetComponent` 即可使其成为交互目标，无需继承特定基类。

## 蓝图用法

插件暴露了多个可蓝图调用的函数和组件，方便设计师无需 C++ 即可搭建交互系统。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Get Interactable Targets From Actor` | 从指定 Actor 上收集所有实现了 `IInteractionTarget` 接口的对象（组件或自身） | `UInteractableInterfaceLibrary` |
| `Append Target Configuration` | 获取目标交互配置（显示名称等），用于构建 UI | `UInteractableInterfaceLibrary` |
| `Begin Interaction On Target` | 执行与指定目标的交互（触发目标的 `BeginInteraction`） | `UInteractableInterfaceLibrary` |
| `Reset Query Results` | 清空交互查询结果结构体 | `UInteractableInterfaceLibrary` |
| `Attempt To Begin Interactions` | 交互发起者组件调用，向一组目标发起交互 | `UInteractionInstigatorComponent` |
| 事件 `On Begin Interaction Callback` | 当该目标被交互时触发的动态委托（可在蓝图绑定事件） | `UInteractionTargetComponent` |
| 事件 `On Available Interaction Targets Changed` | 在能力任务中，每当周围可交互目标列表变化时触发 | `UAbilityTask_GrantNearbyInteractionData` |
| 节点 `Get Target Configuration` (自定义名称) | 从目标组件获取其配置（`BP_AppendTargetConfiguration`） | `UInteractionTargetComponent` |
| 节点 `Begin Interaction` (自定义名称) | 推进该目标上的交互逻辑（`BP_BeginInteraction`） | `UInteractionTargetComponent` |

### 使用示例（蓝图描述）

**1. 检测并显示周围的交互目标**

- 在玩家角色上添加 `UInteractionInstigatorComponent`，设置 `InteractionContextData`（用继承自 `FInteractionContextData` 的自定义结构体，如包含玩家等级、物品等）。
- 在玩家控制器或 Pawn 的事件图表中，周期性（或通过 `UAbilityTask_GrantNearbyInteractionData`）使用 **Get All Actors With Interface** 或物理通道扫描得到目标列表。
- 调用 **Get Interactable Targets From Actor** 提取目标接口，再对每个目标使用 **Append Target Configuration** 获取显示名称，更新 UI。

**2. 发起交互**

- 当玩家按下交互键（如 E），从 UI 选中的目标列表中选取一个（或最近的目标），调用 `UInteractionInstigatorComponent` 的 **Attempt To Begin Interactions**。
- 该函数会遍历目标，对每个目标调用 `BeginInteraction`（目标端执行交互逻辑，如打开宝箱、播放蒙太奇等）。

**3. 自定义目标行为**

- 在目标 Actor 上添加 `UInteractionTargetComponent`（自动继承 BoxComponent 和 IInteractionTarget）。
- 设置 `TargetConfigs` 数组中的 `FInstancedStruct`（基类为 `FInteractionTargetConfiguration`），填写 `DisplayName`。
- 在 `On Begin Interaction Callback` 事件中绑定逻辑，如触发动画、生成物品、发送事件。

## C++ 用法

### 头文件引入

```cpp
#include "InteractableInterfaceLibrary.h"
#include "InteractableTargetInterface.h"
#include "InteractionInstigatorComponent.h"
#include "InteractionTargetComponent.h"
#include "InteractionTypes.h"
```

### 基本用法

**实现一个自定义交互目标（Actor 而非组件）**

```cpp
// MyInteractableActor.h
#include "InteractableTargetInterface.h"
#include "InteractionTypes.h"

UCLASS()
class AMyInteractableActor : public AActor, public IInteractionTarget
{
    GENERATED_BODY()
public:
    // IInteractionTarget interface
    virtual void AppendTargetConfiguration(const FInteractionContext& Context, FInteractionQueryResults& OutResults) const override;
    virtual void BeginInteraction(const FInteractionContext& Context) override;
};
```

```cpp
// MyInteractableActor.cpp
void AMyInteractableActor::AppendTargetConfiguration(const FInteractionContext& Context, FInteractionQueryResults& OutResults) const
{
    // 设置显示名称
    FInteractionTargetConfiguration Config;
    Config.DisplayName = NSLOCTEXT("Interaction", "OpenChest", "Open Chest");
    OutResults.TargetConfigs.Add(FInstancedStruct::Make(Config));
}

void AMyInteractableActor::BeginInteraction(const FInteractionContext& Context)
{
    // 处理交互：打开宝箱动画，更改状态等
    UE_LOG(LogInteractions, Log, TEXT("Chest opened by instigator: %s"), *Context.InstigatorContext.Instigator.GetObject()->GetName());
}
```

**从重叠结果中收集交互目标**

```cpp
#include "InteractableInterfaceLibrary.h"
#include "Engine/OverlapResult.h"

// 在角色组件中
TArray<FOverlapResult> OverlapResults;
GetWorld()->OverlapMultiByChannel(OverlapResults, GetActorLocation(), FQuat::Identity, ECollisionChannel::ECC_GameTraceChannel1, FCollisionShape::MakeSphere(500.0f));

TArray<TScriptInterface<IInteractionTarget>> Targets;
UInteractableInterfaceLibrary::AppendInteractableTargetsFromOverlapResults(OverlapResults, Targets);
```

**使用能力任务扫描目标（C++ 实现）**

```cpp
#include "InteractionTask_WaitForTargets.h"

// 在 GameplayAbility 中创建任务
UAbilityTask_GrantNearbyInteractionData* Task = UAbilityTask_GrantNearbyInteractionData::GrantAbilitiesForNearbyInteractionData(
    this, ECollisionChannel::ECC_GameTraceChannel1, 500.0f, 0.5f);
Task->OnAvailableInteractionTargetsChanged.AddDynamic(this, &UMyAbility::OnTargetsChanged);
Task->ReadyForActivation();
```

### 进阶用法

**扩展交互上下文数据**

继承 `FInteractionContextData` 添加自定义字段：

```cpp
USTRUCT(BlueprintType)
struct FMyInteractionContextData : public FInteractionContextData
{
    GENERATED_BODY()
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    bool bRequiresLockpick = false;
    
    UPROPERTY(EditAnywhere, BlueprintReadWrite)
    int32 MinLevel = 1;
};
```

在 `UInteractionInstigatorComponent` 中设置 `InteractionContextData` 为 `FInstancedStruct` 包含此类型。

**结合 SmartObjects 使用**

插件默认依赖 SmartObjects，你可以将 `UInteractionTargetComponent` 或其接口实现放在 SmartObject 行为上，利用 SmartObject 的查询和选择机制驱动交互。

## Demo 示例

以下演示创建一个简单的交互角色和可拾取物品。

### MyInteractableWidget.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "InteractionTypes.h"
#include "MyInteractableWidget.generated.h"

UCLASS()
class UMyInteractableWidget : public UUserWidget
{
    GENERATED_BODY()

public:
    UFUNCTION(BlueprintImplementableEvent, Category="Interaction")
    void UpdateInteractables(const TArray<FInteractionTargetConfiguration>& Configs);
};
```

### MyInteractionPlayer.h

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "InteractableInstigator.h"
#include "MyInteractionPlayer.generated.h"

UCLASS()
class AMyInteractionPlayer : public ACharacter, public IInteractableInstigator
{
    GENERATED_BODY()

public:
    virtual void Tick(float DeltaTime) override;

protected:
    virtual void OnAttemptToBeginInteractions(const TArray<TScriptInterface<IInteractionTarget>>& TargetsToInteractWith) override;

private:
    UPROPERTY()
    TArray<TScriptInterface<IInteractionTarget>> CurrentTargets;
};
```

### MyInteractionPlayer.cpp

```cpp
#include "MyInteractionPlayer.h"
#include "InteractableInterfaceLibrary.h"

void AMyInteractionPlayer::Tick(float DeltaTime)
{
    Super::Tick(DeltaTime);
    
    // 每帧扫描重叠（简化示例）
    TArray<FOverlapResult> Overlaps;
    GetWorld()->OverlapMultiByChannel(Overlaps, GetActorLocation(), FQuat::Identity, ECC_Visibility, FCollisionShape::MakeSphere(300.0f));
    
    TArray<TScriptInterface<IInteractionTarget>> NewTargets;
    UInteractableInterfaceLibrary::AppendInteractableTargetsFromOverlapResults(Overlaps, NewTargets);
    CurrentTargets = MoveTemp(NewTargets);
}

void AMyInteractionPlayer::OnAttemptToBeginInteractions(const TArray<TScriptInterface<IInteractionTarget>>& TargetsToInteractWith)
{
    // 只与第一个目标交互
    if (TargetsToInteractWith.Num() > 0)
    {
        FInteractionContext Context;
        Context.Target = TargetsToInteractWith[0];
        // 填充其他上下文...
        TargetsToInteractWith[0]->BeginInteraction(Context);
    }
}
```

## 模块依赖

插件自身使用了以下模块，你在自己的模块中使用时需添加这些依赖（省略标准模块）：

| 模块 | 用途 |
|---|---|
| `SmartObjects` | 提供智能对象查询和选择框架，允许交互目标与智能对象集成 |
| `GameplayAbilities` | 提供 GameplayAbility 系统，能力任务 `UAbilityTask_GrantNearbyInteractionData` 依赖该模块 |
| `StructUtils` | 提供 `FInstancedStruct` 支持，用于存储可配置的结构体（交互上下文、目标配置等） |

> **注意**：SmartObjects 和 GameplayAbilities 为必需依赖，且均为实验性模块，需要你的项目已启用它们。

## 维护状态

### 近期更新

- 2024-09-17 `f4537894` Enter the beginning phase of the Interactable Interface plugin. Still in active development!

### 维护评价

该插件创建于 2024 年 9 月，属于全新实验性内容。自首次提交后无后续更新，处于早期开发阶段。由于缺少后续提交记录和实质性功能迭代，建议谨慎用于生产项目。插件文档和 API 可能不稳定，后续版本可能发生较大变化。推荐在原型验证或学习研究时使用，避免直接依赖。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InteractionInterface)
- [官方文档](https://dev.epicgames.com/documentation/unreal-engine/interaction-system)（未提供，可参考官方文档搜索“Interaction”）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Experimental/InteractionInterface/Tests)（暂无公开用例）