# Gameplay Interactions

> Player and NPC interactions

| 属性 | 值 |
|---|---|
| 中文名 | 玩家交互 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayInteractionsModule` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-05-06 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayInteractions) | |

## 用途

GameplayInteractions 插件提供了一个基于 StateTree 的框架，用于标准化和管理玩家与游戏内物体（SmartObjects）以及与 AI 控制的 NPC 之间的复杂交互逻辑。它解决了在游戏开发中，如何结构化地定义、执行和同步多角色交互流程的问题，特别是当这些交互涉及状态转换、动画播放和事件驱动时。

该插件的核心是通过 `UGameplayInteractionSmartObjectBehaviorDefinition` 将一个 StateTree 与一个 SmartObject 的交互行为关联起来。`FGameplayInteractionContext` 负责管理整个交互的生命周期（激活、更新、停止），并为 StateTree 提供必要的上下文（交互的 Actor 和 SmartObject Actor）。插件内建了一系列 StateTree 任务、条件和事件，用于处理如寻找交互入口位置、播放情境动画、同步槽位状态等具体交互步骤。

## 使用场景

- **玩家与环境互动**：当玩家走近一个可交互的物体（如门、箱子、终端），并按下交互键时，需要执行一套标准化的交互逻辑（播放动画、检查条件、完成交互）。
- **AI 使用 SmartObject**：AI 角色需要寻找并使用场景中的智能物体（如桌子、武器架、治疗点），整个过程可能涉及移动、播放动画和状态同步。
- **多角色同步交互**：当两个或多个角色（如玩家与 NPC）需要同步执行一系列动作（例如共同开启一扇门、合作解谜、执行处决动画）。
- **复杂交互状态管理**：交互过程中包含多个阶段（准备、进行中、结束），并且需要根据条件在不同阶段间转换，或向其他系统发送事件。

## 蓝图用法

插件主要通过 AI 任务和 StateTree 节点在蓝图中使用。核心是创建一个与 SmartObject 关联的 `GameplayInteractionSmartObjectBehaviorDefinition` 资产，并在其中编写交互逻辑（StateTree）。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UseSmartObjectWithGameplayInteraction` | 创建一个 AI 任务，让控制器立即开始与一个已认领的 SmartObject 槽位交互。 | `UAITask_UseGameplayInteraction` |
| `MoveToAndUseSmartObjectWithGameplayInteraction` | 创建一个 AI 任务，让控制器先移动到 SmartObject 槽位位置，然后开始交互。 | `UAITask_UseGameplayInteraction` |
| `RequestAbort` | 请求中止正在执行的交互任务。 | `UAITask_UseGameplayInteraction` |
| (StateTree) Play Contextual Anim | 播放一个情境动画场景，支持开始、加入、过渡等多种模式。 | `FStateTreeTask_PlayContextualAnim` |
| (StateTree) Find Slot Entrance Location | 为指定的 SmartObject 槽位查找一个合适的交互入口位置。 | `FStateTreeTask_FindSlotEntranceLocation` |
| (StateTree) Sync Slot Tag Transition | 监控 SmartObject 槽位上的标签变化，用于在多个 StateTree 间同步交互状态。 | `FGameplayInteractionSyncSlotTagTransitionTask` |

### 使用示例（蓝图描述）

1.  **创建交互定义**：在内容浏览器中右键创建 `GameplayInteractionSmartObjectBehaviorDefinition` 资产。打开该资产，在 `State Tree` 属性中指定一个使用了 `Gameplay Interaction` Schema 的 StateTree。
2.  **配置 SmartObject**：在场景中的 SmartObject Actor 或其组件上，找到 `Behavior Definition` 列表，将你上一步创建的资产添加进去。
3.  **AI 使用交互（蓝图）**：
    *   在 AI 的行为树或黑板中，先通过 SmartObject 子系统查询并认领一个可用的 SmartObject 槽位，获得 `ClaimHandle`。
    *   在蓝图中调用 `UseSmartObjectWithGameplayInteraction` 节点，将 `ClaimHandle` 和 AI 控制器传入。该节点会返回一个 `AITask`。
    *   可以绑定该任务的 `OnSucceeded`、`OnFailed` 委托来获取结果。
4.  **StateTree 内编辑**：在上一步的 StateTree 资产编辑器中，你可以使用插件提供的 `Gameplay Interactions` 分类下的各种任务、条件和事件节点来编排具体的交互流程。例如，在进入状态时播放动画，等待动画完成，并设置槽位标签。

## C++ 用法

### 头文件引入

```cpp
#include "GameplayInteractionContext.h"
#include "AITask_UseGameplayInteraction.h"
```

### 基本用法

以下示例展示了如何通过 C++ 代码驱动一个基于 GameplayInteractions 的交互流程。

```cpp
// 假设你已经通过 SmartObject 子系统获取了一个有效的认领句柄 FSmartObjectClaimHandle ClaimHandle
// 以及交互的参与方 AActor* MyCharacter 和 SmartObject Actor* TargetSmartObject

#include "GameplayInteractionContext.h"
#include "GameplayInteractionSmartObjectBehaviorDefinition.h"

// 1. 创建交互上下文
FGameplayInteractionContext InteractionContext;
InteractionContext.SetClaimedHandle(ClaimHandle);
InteractionContext.SetContextActor(MyCharacter); // 交互的发起者（如玩家角色）
InteractionContext.SetSmartObjectActor(TargetSmartObject); // 交互的目标 SmartObject

// 2. 获取交互行为定义
const UGameplayInteractionSmartObjectBehaviorDefinition* InteractionDefinition = /* 从 SmartObject 组件或配置中获取 */;

// 3. 激活交互
if (InteractionContext.Activate(InteractionDefinition))
{
    // 交互已成功初始化，需要在 Tick 中驱动
    bIsInteracting = true;
}

// 4. 在 Tick 中更新交互
if (bIsInteracting)
{
    bIsInteracting = InteractionContext.Tick(DeltaTime);
    if (!bIsInteracting)
    {
        // 交互结束
        EStateTreeRunStatus FinalStatus = InteractionContext.GetLastRunStatus();
        // 处理结果...
    }
}

// 5. 提前中止交互（可选）
if (NeedAbort)
{
    InteractionContext.Deactivate();
    bIsInteracting = false;
}
```

### 进阶用法：通过 AI 任务使用

对于 AI 角色，更推荐使用封装好的 `UAITask`。

```cpp
#include "AIController.h"
#include "AITask_UseGameplayInteraction.h"
#include "SmartObjectSubsystem.h"

AAIController* AIController = /* ... */;
FSmartObjectClaimHandle ClaimHandle = /* ... */;

// 创建一个 “移动并使用” 的交互任务
UAITask_UseGameplayInteraction* InteractionTask = UAITask_UseGameplayInteraction::MoveToAndUseSmartObjectWithGameplayInteraction(
    AIController,
    ClaimHandle,
    true // 锁定 AI 逻辑
);

if (InteractionTask)
{
    // 可以绑定任务委托
    InteractionTask->OnSucceeded.AddDynamic(this, &ThisClass::OnInteractionSucceeded);
    InteractionTask->OnFailed.AddDynamic(this, &ThisClass::OnInteractionFailed);
    
    // 任务将在 AI 任务系统中自动激活并执行
}
```

## Demo 示例

一个最小的可编译示例，展示如何创建一个执行简单交互的 Actor 组件。

```cpp
// MyInteractionComponent.h
#pragma once
#include "Components/ActorComponent.h"
#include "GameplayInteractionContext.h"
#include "MyInteractionComponent.generated.h"

class UGameplayInteractionSmartObjectBehaviorDefinition;

UCLASS(ClassGroup=(Custom), meta=(BlueprintSpawnableComponent))
class MYPROJECT_API UMyInteractionComponent : public UActorComponent
{
    GENERATED_BODY()
public:
    UMyInteractionComponent();

    UFUNCTION(BlueprintCallable)
    void StartInteraction(const FSmartObjectClaimHandle& ClaimHandle, UGameplayInteractionSmartObjectBehaviorDefinition* Definition);

    UFUNCTION(BlueprintCallable)
    void StopInteraction();

protected:
    virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

private:
    UPROPERTY()
    FGameplayInteractionContext InteractionContext;

    UPROPERTY()
    bool bIsInteracting = false;
};
```

```cpp
// MyInteractionComponent.cpp
#include "MyInteractionComponent.h"
#include "GameplayInteractionSmartObjectBehaviorDefinition.h"

UMyInteractionComponent::UMyInteractionComponent()
{
    PrimaryComponentTick.bCanEverTick = true;
}

void UMyInteractionComponent::StartInteraction(const FSmartObjectClaimHandle& ClaimHandle, UGameplayInteractionSmartObjectBehaviorDefinition* Definition)
{
    if (!Definition)
    {
        UE_LOG(LogTemp, Warning, TEXT("StartInteraction: Definition is null."));
        return;
    }

    InteractionContext.SetClaimedHandle(ClaimHandle);
    InteractionContext.SetContextActor(GetOwner());
    // SmartObjectActor 可以从 ClaimHandle 或 Definition 的上下文中推断
    // 这里假设您有办法获取它，例如：InteractionContext.SetSmartObjectActor(...);

    bIsInteracting = InteractionContext.Activate(Definition);
    SetComponentTickEnabled(bIsInteracting);
}

void UMyInteractionComponent::StopInteraction()
{
    if (bIsInteracting)
    {
        InteractionContext.Deactivate();
        bIsInteracting = false;
        SetComponentTickEnabled(false);
    }
}

void UMyInteractionComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
    Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

    if (bIsInteracting)
    {
        bIsInteracting = InteractionContext.Tick(DeltaTime);
        if (!bIsInteracting)
        {
            // 交互自然结束
            UE_LOG(LogTemp, Log, TEXT("Interaction finished with status: %d"), static_cast<int32>(InteractionContext.GetLastRunStatus()));
            SetComponentTickEnabled(false);
        }
    }
}
```

## 模块依赖

该插件本身依赖多个其他插件，要使用它，你的项目或模块需要启用这些插件。

| 模块/插件 | 用途 |
|---|---|
| `StateTree` | 交互逻辑的核心状态机框架。 |
| `SmartObjects` | 提供可交互物体、槽位和认领系统的底层支持。 |
| `ContextualAnimation` | 用于执行 `Play Contextual Anim` 任务，处理多角色同步动画。 |
| `NavCorridor` | 在 `Find Slot Entrance Location` 等任务中，用于导航路径验证。 |
| `GameplayStateTree` | 为 StateTree 提供游戏玩法相关的集成和功能扩展。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于引擎日志系统更新。 |
| 2026-04-13 | `6f1ea925` | State Tree: Updated state tree reference struct details to show the display name of the struct rather than the type name. | 更新了状态树引用结构的详细信息显示，现在会显示结构体的显示名称而非类型名。 |
| 2025-11-17 | `0c9f3796` | [StateTree] Execution context uses a view instead of the property bag. Deprecated the property bag version. | [状态树] 执行上下文改用视图而非属性包，并废弃了属性包版本。 |
| 2025-10-08 | `e166d56b` | Contextual Anim - Moved SectionIdx and AnimSetIdx to individuals Bindings to be able to support actor change during transitions. | [情境动画] 将段索引和动画集索引移至单独的绑定，以支持过渡期间的Actor变更。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 将插件的 `Base<Plugin>.ini` 配置文件重命名为 `Default<Plugin>.ini`。 |

### 维护评价

- **创建时间**：该插件于 2022 年 5 月创建，相对年轻。
- **最近更新**：最近一次提交（2026-04-14）距今不到 1 个月，更新内容主要是跟随引擎核心系统（StateTree、日志）的演进。这表明该插件仍在被 Epic Games 内部使用和维护。
- **状态**：插件 `.uplugin` 中明确标记 `IsExperimentalVersion: true` 且 `EnabledByDefault: false`，这表明它仍处于**实验性**阶段。其 API 和功能在未来版本中可能发生变化。
- **推荐**：适用于愿意接受实验性 API 变化、并需要高级 StateTree 驱动交互框架的项目。对于生产环境中的关键功能，需谨慎评估其稳定性。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayInteractions)
- [官方文档]() （未提供）
- [测试用例]() （插件目录内未发现独立测试文件，测试可能位于 `Engine/Tests` 下）