# Gameplay Interactions

> Player and NPC interactions

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `GameplayInteractionsModule` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-05-06 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayInteractions) | |

## 用途

GameplayInteractions 是一个基于 **StateTree** 的插件，用于定义和执行 **Player/NPC 与 Smart Object 之间的交互行为**。它解决了以下核心问题：

1. **将交互逻辑数据化**：通过 StateTree 定义交互流程（如：坐在椅子上、使用工作台），而非硬编码在 C++ 中
2. **为 Smart Object 提供行为驱动**：SmartObjects 插件定义了"对象在哪里、有几个槽位"，而 GameplayInteractions 定义了"如何与槽位交互"
3. **NPC AI 行为集成**：通过 `UAITask_UseGameplayInteraction` 将 Smart Object 交互无缝集成到 AI 行为树中，支持移动到目标后再执行交互
4. **多角色同步**：通过 Slot Tag 同步机制，支持多个参与者协调执行上下文动画（Contextual Animation）

简单来说：**SmartObjects 管"是什么"，GameplayInteractions 管"怎么做"。**

## 使用场景

- 你想让 NPC 走到椅子旁坐下 → 用 GameplayInteractions 配合 SmartObjects
- 你想让两个角色执行同步的互动动画（如握手、格斗） → 用 Play Contextual Anim 任务
- 你想让 AI 角色在执行交互时自动导航到入口位置 → 用 `MoveToAndUseSmartObjectWithGameplayInteraction`
- 你想让 NPC 在 Smart Object 上执行一系列复杂操作（查找槽位 → 移动 → 播放动画 → 修改标签 → 完成） → 用 StateTree 组合多个任务

## 核心架构

```
┌─────────────────────────────────────────────────────┐
│  AITask_UseGameplayInteraction (AI 行为树任务)        │
│  ├─ MoveTo（可选：先导航到目标位置）                    │
│  └─ FGameplayInteractionContext                     │
│      ├─ Activate() → 启动 StateTree                  │
│      ├─ Tick()     → 驱动 StateTree 每帧更新          │
│      └─ Deactivate() → 停止 StateTree                │
│           │                                         │
│           ▼                                         │
│  StateTree（使用 GameplayInteractionStateTreeSchema）  │
│  ├─ 任务（Tasks）: FindSlot, PlayAnim, ModifyTag...   │
│  └─ 条件（Conditions）: MatchSlotTags, IsSlotValid... │
└─────────────────────────────────────────────────────┘
```

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UseSmartObjectWithGameplayInteraction` | 创建 AI 任务：在原地执行 Smart Object 交互 | `UAITask_UseGameplayInteraction` |
| `MoveToAndUseSmartObjectWithGameplayInteraction` | 创建 AI 任务：先移动到槽位位置，再执行交互 | `UAITask_UseGameplayInteraction` |
| `RequestAbort` | 请求中止当前交互 | `UAITask_UseGameplayInteraction` |
| `SetStateTree` | 设置行为定义引用的 StateTree 资产 | `UGameplayInteractionSmartObjectBehaviorDefinition` |
| `GetStateTree` | 获取行为定义引用的 StateTree 资产 | `UGameplayInteractionSmartObjectBehaviorDefinition` |

### 事件委托

| 委托 | 说明 |
|---|---|
| `OnFinished` | 交互完成时触发（无论成功或失败） |
| `OnSucceeded` | 交互成功完成时触发 |
| `OnFailed` | 交互失败时触发 |
| `OnMoveToFailed` | 移动到槽位失败时触发 |

### StateTree 任务节点

所有任务在 StateTree 编辑器中可见，分类为 **Gameplay Interactions|Smart Object**：

| 节点 | 说明 |
|---|---|
| **Find Slot Entrance Location** | 查找 Smart Object 槽位的入口位置，支持导航验证、碰撞检测、地面投影 |
| **Get Slot Entrance Tags** | 获取指定槽位入口处定义的 GameplayTags |
| **Find Slot** | 基于参考槽位查找另一个槽位（按 ActivityTag 或 LinkTag） |
| **Get Slot Actor** | 获取指定槽位上当前的 Actor |
| **Modify Slot Tag** | 添加/移除槽位上的 GameplayTag |
| **Send Slot Event** | 向指定槽位发送事件 |
| **Listen Slot Events** | 监听指定槽位上的所有事件并转换为 StateTree 事件 |
| **Set Slot Enabled** | 启用/禁用指定槽位 |
| **Sync Slot Tag Transition** | 监控槽位 Tag 的过渡变化，用于同步两个 StateTree 的执行 |
| **Sync Slot Tag State** | 监控槽位上 Tag 的存在状态，用于同步中断 |
| **Play Anim Montage** | 播放动画 Montage |
| **Play Contextual Anim** | 播放上下文动画，支持多角色、循环、过渡 |

### StateTree 条件

| 条件 | 说明 |
|---|---|
| **Match Slot Tags** | 检查槽位 GameplayTags 是否匹配（支持 ActivityTags 和 RuntimeTags） |
| **Query Slot Tags** | 使用 GameplayTagQuery 查询槽位标签 |
| **Is Slot Handle Valid** | 检查槽位句柄是否有效 |

### 使用示例（蓝图描述）

**场景：AI 角色走到桌旁坐下**

1. **创建 SmartObject 行为定义**：在 SmartObject 定义上添加 `UGameplayInteractionSmartObjectBehaviorDefinition`，设置一个 StateTree 资产
2. **StateTree 内容**：
   - 根状态 → Find Slot Entrance Location（查找入口位置）→ Move to Location → Play Contextual Anim（播放坐下动画）
3. **在行为树中调用**：
   - 使用 SmartObjects 插件的 `FindSmartObject` 查找可用对象
   - Claim 一个槽位得到 `FSmartObjectClaimHandle`
   - 调用 `MoveToAndUseSmartObjectWithGameplayInteraction`，连接 `OnSucceeded`/`OnFailed` 委托

## C++ 用法

### 头文件引入

```cpp
#include "GameplayInteractionContext.h"
#include "GameplayInteractionSmartObjectBehaviorDefinition.h"
#include "AITask_UseGameplayInteraction.h"
#include "GameplayInteractionsTypes.h"
```

### 基本用法：手动驱动交互

```cpp
// 来源: GameplayInteractionContext.cpp
// 需要先获取 SmartObject 的 ClaimHandle 和相关 Actor
FGameplayInteractionContext InteractionContext;

// 设置交互上下文
InteractionContext.SetContextActor(MyPawn);           // 执行交互的 Actor
InteractionContext.SetSmartObjectActor(SOActor);       // Smart Object Actor
InteractionContext.SetClaimedHandle(ClaimHandle);      // 已 Claim 的槽位句柄

// 获取行为定义（通常从 SmartObjectSubsystem 获取）
const UGameplayInteractionSmartObjectBehaviorDefinition* Definition = 
    SmartObjectSubsystem->MarkSlotAsOccupied<UGameplayInteractionSmartObjectBehaviorDefinition>(ClaimHandle);

// 激活交互（启动 StateTree）
if (InteractionContext.Activate(*Definition))
{
    // 每帧 Tick 驱动 StateTree
    bool bStillRunning = InteractionContext.Tick(DeltaTime);
    if (!bStillRunning)
    {
        // 交互完成
        EStateTreeRunStatus Status = InteractionContext.GetLastRunStatus();
        InteractionContext.Deactivate();
    }
}
```

### 进阶用法：AI Task 集成

```cpp
// 来源: AITask_UseGameplayInteraction.cpp
// 最简单的方式：通过 AI Task 在行为树/StateTree 中使用

// 方式 1：直接在原地执行交互（Actor 已在目标位置）
UAITask_UseGameplayInteraction* Task = 
    UAITask_UseGameplayInteraction::UseSmartObjectWithGameplayInteraction(
        AIController, ClaimHandle, /*bLockAILogic=*/true);

// 方式 2：先移动到槽位位置，再执行交互
UAITask_UseGameplayInteraction* Task = 
    UAITask_UseGameplayInteraction::MoveToAndUseSmartObjectWithGameplayInteraction(
        AIController, ClaimHandle, /*bLockAILogic=*/true);

// 绑定回调
Task->OnSucceeded.AddDynamic(this, &AMyAI::OnInteractionSucceeded);
Task->OnFailed.AddDynamic(this, &AMyAI::OnInteractionFailed);
Task->ReadyForActivation();

// 需要中止交互时
Task->RequestAbort();
```

### 进阶用法：发送事件给 StateTree

```cpp
// 在交互过程中向 StateTree 发送自定义事件
FGameplayTag EventTag = FGameplayTag::RequestGameplayTag(FName("Event.Interaction.Custom"));
InteractionContext.SendEvent(EventTag, FConstStructView(), FName("MyOrigin"));
```

### 进阶用法：槽位失效回调

AITask 内部自动注册了槽位失效回调（`OnSlotInvalidated`）。当 Smart Object 的槽位被销毁或取消注册时，交互会自动中止并标记为 `InternalAbort`。这不需要使用者手动处理。

## Demo 示例

### 最小 C++ 示例：自定义 AI 交互任务

**Build.cs 依赖：**

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "GameplayInteractionsModule",
    "SmartObjectsModule",
    "StateTreeModule",
    "AIModule",
    "GameplayTags",
});
```

**MyAIInteractionTask.h：**

```cpp
#pragma once

#include "CoreMinimal.h"
#include "GameplayInteractionSmartObjectBehaviorDefinition.h"
#include "SmartObjectSubsystem.h"

class FMyInteractionHelper
{
public:
    static void ExecuteInteraction(UWorld* World, AActor* ContextActor, const FSmartObjectClaimHandle& ClaimHandle)
    {
        USmartObjectSubsystem* SOSubsystem = USmartObjectSubsystem::GetCurrent(World);
        if (!SOSubsystem || !ClaimHandle.IsValid())
        {
            return;
        }

        // 标记槽位为已占用，获取行为定义
        const UGameplayInteractionSmartObjectBehaviorDefinition* Definition = 
            SOSubsystem->MarkSlotAsOccupied<UGameplayInteractionSmartObjectBehaviorDefinition>(ClaimHandle);
        
        if (!Definition)
        {
            return;
        }

        // 获取 SmartObject Actor
        const USmartObjectComponent* SOComponent = SOSubsystem->GetSmartObjectComponent(ClaimHandle);
        
        // 设置并激活交互
        FGameplayInteractionContext& Context = InteractionContext;
        Context.SetContextActor(ContextActor);
        Context.SetSmartObjectActor(SOComponent ? SOComponent->GetOwner() : nullptr);
        Context.SetClaimedHandle(ClaimHandle);
        Context.Activate(*Definition);
    }

    // 在 Tick 中调用
    static void TickInteraction(FGameplayInteractionContext& Context, float DeltaTime)
    {
        if (!Context.Tick(DeltaTime))
        {
            // 交互完成
            Context.Deactivate();
        }
    }

private:
    static FGameplayInteractionContext InteractionContext;
};
```

### StateTree 编辑器配置示例

在 StateTree 编辑器中，使用 **Gameplay Interactions** Schema 创建一个交互流程：

```
[Root]
  └─ Sequence
      ├─ [Task] Find Slot Entrance Location
      │     Input:  ReferenceSlot (绑定到 Context ClaimedHandle)
      │     Output: EntryTransform, EntranceTags
      │
      ├─ [Task] Move To (StateTreeAI 通用任务)
      │     Input:  目标位置 (绑定到上一步 EntryTransform)
      │
      ├─ [Task] Modify Slot Tag
      │     参数: Tag = "State.Occupied", Operation = Add
      │     Modify = OnEnterStateUndoOnExitState
      │
      ├─ [Task] Play Contextual Anim
      │     参数: PrimaryActor = Context Actor
      │            SceneAsset = SitDownScene
      │
      └─ [Task] Modify Slot Tag
            参数: Tag = "State.Occupied", Operation = Remove
            Modify = OnExitStateSucceeded
```

## 模块依赖

从 Build.cs 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `AIModule` | AI Controller、AI Task 基础设施 |
| `ContextualAnimation` | 上下文动画系统（多角色同步动画） |
| `Core` | UE 核心基础 |
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、World 等） |
| `GameplayStateTreeModule` | Gameplay 层的 StateTree 集成 |
| `GameplayTags` | GameplayTag 系统 |
| `GameplayTasks` | GameplayTask 基础设施（AITask 基类） |
| `NavCorridor` | 导航走廊（用于路径验证） |
| `NavigationSystem` | 导航系统（寻路、路径查询） |
| `SmartObjectsModule` | Smart Objects 系统（槽位管理、Claim 机制） |
| `StateTreeModule` | StateTree 状态机引擎 |

**插件依赖**（.uplugin 中声明）：

| 插件 | 用途 |
|---|---|
| `StateTree` | StateTree 状态机 |
| `SmartObjects` | Smart Object 框架 |
| `ContextualAnimation` | 上下文动画 |
| `NavCorridor` | 导航走廊 |
| `GameplayStateTree` | Gameplay 层 StateTree 集成 |

## 维护状态

### 近期更新

1. **2025-08-25** `8156363` — `[State Tree] only log error when the previous tree is still running in GameplayInteractionContext`
   - 解读：修复了当之前的 StateTree 仍在运行时错误日志级别过高的问题，从 fatal 降为 error

2. **2025-08-22** `e45861b` — `[State Tree] - Prevent reentrant call into StartTree and Tick for StateTreeComponent and GameplayInteractionsContext`
   - 解读：**重要修复**。防止了 `Activate()` 和 `Tick()` 的重入调用，这在复杂交互场景中可能导致崩溃。同时修复了 StopTree 在重入时的上下文使用问题

3. **2025-07-11** `1bb7cec` — `Ran update script to removed null initializers when creating TSubclassOf<T>`
   - 解读：代码清理，移除不必要的 `nullptr` 初始化器，属于批量自动化维护

### 维护评价

- **状态**：⚠️ 实验性插件（`IsExperimentalVersion=true`），默认不启用
- **创建时间**：2022 年 5 月（约 4 年前）
- **活跃度**：**活跃维护中**。最近 3 次提交集中在 2025 年 7-8 月，都是实质性修复（防止重入崩溃等），说明 Epic 在持续使用和改进此插件
- **注意事项**：
  - 因为是实验性 API，接口可能在后续版本中发生变化
  - 默认不启用，需要在项目设置中手动启用
  - 强依赖 SmartObjects、StateTree、ContextualAnimation 等实验性/较新系统
- **推荐度**：如果你的项目使用 SmartObjects + StateTree 做 AI 交互，**推荐使用**。它是 Epic 官方推荐的 Smart Object 交互执行方案。但要注意 API 可能变化。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayInteractions)
- 官方文档（无，.uplugin 中 DocsURL 为空）
- 相关插件：[SmartObjects](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects)、[StateTree](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Editor/StateTree)、[ContextualAnimation](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Animation/ContextualAnimation)
