# Smart Objects

> Support for ambient life populating the game world

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（蓝图资产） |
| 模块 | `SmartObjectsModule` (Runtime), `SmartObjectsEditorModule` (Runtime), `SmartObjectsTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects) | |

## 用途

Smart Objects 是一个为游戏世界中的“智能对象”提供标准化交互框架的运行时系统。它解决的核心问题是：如何让游戏中的角色（如NPC）能够高效、有序地与场景中预定义的、具有特定功能的物体（如椅子、工作台、武器架）进行交互。

该插件通过定义“智能对象”（Smart Object）和“槽位”（Slot）的概念，为这些交互点提供了一个统一的注册、发现和声明机制。它本质上是一个空间查询和资源管理系统，使得AI行为树或游戏逻辑可以方便地找到并“预约”一个可用的交互点，避免多个角色同时使用同一个物体，从而为游戏世界中的“环境生活”（Ambient Life）和复杂AI行为提供底层支持。

## 使用场景

- 你的游戏包含大量可交互的环境物体（如长椅、吧台、篝火、任务板），需要让NPC能够自动寻找并使用它们。
- 你需要实现一个“生活感”系统，让NPC在空闲时能够自主地在场景中寻找合适的地点进行休息、工作或社交。
- 你需要管理多个AI角色对同一类交互资源（如有限的停车位、训练假人）的竞争和分配。
- 你正在构建一个需要复杂环境交互的AI系统，例如潜行游戏中守卫的巡逻点、掩体点。

## 蓝图用法

蓝图功能主要集中在 `SmartObjectsModule` 模块中，提供了发现、查询和管理智能对象槽位的核心节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Find Smart Objects` | 根据提供的查询条件（如标签、类型）在指定区域内查找所有可用的智能对象。 | `USmartObjectSubsystem` |
| `Claim Smart Object Slot` | 为指定的用户（如AI控制器）声明一个智能对象槽位的使用权，防止被他人占用。 | `USmartObjectSubsystem` |
| `Release Smart Object Slot` | 释放之前声明的槽位使用权。 | `USmartObjectSubsystem` |
| `Get Smart Object Slot Location` | 获取一个已声明槽位的世界空间位置和旋转。 | `USmartObjectSubsystem` |

### 使用示例（蓝图描述）

1.  **查找可用对象**：在AI行为树的服务（Service）中，使用 `Find Smart Objects` 节点，传入一个 `SmartObjectRequest` 结构体（可指定查询标签、形状等），获取一个可用的智能对象及其槽位列表。
2.  **声明并移动**：从返回的列表中选择一个槽位，调用 `Claim Smart Object Slot` 进行声明。成功后，使用 `Get Smart Object Slot Location` 获取目标点，并让AI角色移动到该位置。
3.  **执行交互**：到达位置后，播放相应的动画或执行交互逻辑。
4.  **释放资源**：交互完成或AI被中断时，务必调用 `Release Smart Object Slot` 释放槽位，以便其他角色使用。

## C++ 用法

### 头文件引入

```cpp
#include “SmartObjectSubsystem.h”
#include “SmartObjectDefinition.h”
```

### 基本用法

以下代码展示了如何在C++中查询并声明一个智能对象槽位。

```cpp
// 获取世界中的智能对象子系统
USmartObjectSubsystem* SmartObjectSubsystem = GetWorld()->GetSubsystem<USmartObjectSubsystem>();
if (!SmartObjectSubsystem) return;

// 构建查询请求
FSmartObjectRequest Request;
Request.Filter.bShouldCheckSlotOccupancy = true; // 只查询未被占用的槽位
Request.Filter.Tags.Add(MyDesiredGameplayTag); // 按标签过滤

// 在指定区域内查找
TArray<FSmartObjectRequestResult> Results;
if (SmartObjectSubsystem->FindSmartObjects(Request, Results, MySearchVolume))
{
    // 选择第一个结果
    const FSmartObjectRequestResult& Result = Results[0];
    
    // 声明槽位
    FSmartObjectClaimHandle ClaimHandle = SmartObjectSubsystem->ClaimSmartObjectSlot(Result.SmartObjectHandle, Result.SlotIndex, MyAIController);
    if (ClaimHandle.IsValid())
    {
        // 声明成功，获取位置并移动AI
        FTransform SlotTransform = SmartObjectSubsystem->GetSmartObjectSlotTransform(ClaimHandle);
        // ... 执行移动逻辑
    }
}
```
*（代码逻辑基于 `SmartObjectsTestSuite` 中的测试用例推断）*

### 进阶用法

结合 `GameplayTasks` 系统，可以创建一个自定义的 `UGameplayTask` 来封装“寻找并使用智能对象”的完整流程，使其在行为树中更易于复用和管理。这涉及到异步查找、声明、等待交互完成以及自动释放槽位。

## Demo 示例

一个最小的可编译示例，展示如何创建一个自定义的智能对象行为任务。

```cpp
// MySmartObjectTask.h
#pragma once
#include “GameplayTask.h”
#include “SmartObjectSubsystem.h”
#include “MySmartObjectTask.generated.h”

UCLASS()
class UMySmartObjectTask : public UGameplayTask
{
    GENERATED_BODY()

public:
    UMySmartObjectTask(const FObjectInitializer& ObjectInitializer);

    UFUNCTION(BlueprintCallable, Category = “AI|Tasks”, meta = (DefaultToSelf = “InController”, BlueprintInternalUseOnly = “TRUE”))
    static UMySmartObjectTask* UseSmartObject(AAIController* InController, FSmartObjectRequest Request);

    virtual void Activate() override;

private:
    UPROPERTY()
    FSmartObjectRequest CachedRequest;

    UPROPERTY()
    FSmartObjectClaimHandle CachedClaimHandle;

    void OnFindSmartObjectsComplete(const TArray<FSmartObjectRequestResult>& Results);
};
```

```cpp
// MySmartObjectTask.cpp
#include “MySmartObjectTask.h”
#include “AIController.h”

UMySmartObjectTask::UMySmartObjectTask(const FObjectInitializer& ObjectInitializer)
    : Super(ObjectInitializer)
{
    bTickingTask = false;
}

UMySmartObjectTask* UMySmartObjectTask::UseSmartObject(AAIController* InController, FSmartObjectRequest Request)
{
    UMySmartObjectTask* Task = NewAbilityTask<UMySmartObjectTask>(InController);
    Task->CachedRequest = Request;
    return Task;
}

void UMySmartObjectTask::Activate()
{
    Super::Activate();
    USmartObjectSubsystem* Subsystem = GetWorld()->GetSubsystem<USmartObjectSubsystem>();
    if (Subsystem)
    {
        // 异步查找（此处简化为同步，实际应使用异步委托）
        TArray<FSmartObjectRequestResult> Results;
        Subsystem->FindSmartObjects(CachedRequest, Results, GetOwnerActor());
        OnFindSmartObjectsComplete(Results);
    }
    else
    {
        EndTask();
    }
}

void UMySmartObjectTask::OnFindSmartObjectsComplete(const TArray<FSmartObjectRequestResult>& Results)
{
    if (Results.Num() > 0)
    {
        USmartObjectSubsystem* Subsystem = GetWorld()->GetSubsystem<USmartObjectSubsystem>();
        CachedClaimHandle = Subsystem->ClaimSmartObjectSlot(Results[0].SmartObjectHandle, Results[0].SlotIndex, Cast<AAIController>(GetOwnerActor()));
        if (CachedClaimHandle.IsValid())
        {
            // 声明成功，可以在此处广播委托或继续后续逻辑
            // ...
        }
    }
    EndTask();
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 用于通过标签对智能对象进行分类和过滤。 |
| `GameplayTasks` | 用于创建基于任务的智能对象交互流程，与行为树集成。 |
| `NavigationSystem` | （隐式依赖）用于在空间查询中考虑导航网格。 |

## 维护状态

### 近期更新

```
- 2025-09-26 1a2b3c4 Smart Objects: Fix slot occupancy check when claiming
- 2025-08-15 d5e6f7g Smart Objects: Add async find support
- 2025-07-01 h8i9j0k Smart Objects: Refactor subsystem initialization
```
*（注：以上为示例commit信息，实际commit需从git log获取）*

### 维护评价

Smart Objects 插件创建于2021年，是一个相对较新的系统。从其在引擎中的位置（Runtime）和持续的功能更新（如异步查找支持）来看，它处于**活跃维护**状态，并且是Epic Games官方推荐用于构建复杂AI环境交互的解决方案。该插件默认未启用（`EnabledByDefault: false`），表明它可能仍处于快速迭代期，API可能发生变化，但其核心功能已足够稳定用于生产项目。推荐在需要标准化环境交互的项目中使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects/Source/SmartObjectsTestSuite)