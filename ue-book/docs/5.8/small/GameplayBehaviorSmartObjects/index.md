# GameplayBehaviorSmartObjects

> Plugins for SmartObjects using GameplayBehavior as their default runtime behavior

| 属性 | 值 |
|---|---|
| 中文名 | 游戏行为智能对象 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（行为定义资产） |
| 模块 | `GameplayBehaviorSmartObjectsModule` (Runtime) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-05-02 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayBehaviorSmartObjects) | |

## 用途

该插件是 `GameplayBehaviors` 和 `SmartObjects` 两个框架之间的桥梁。它解决了 AI 角色（Pawn）与场景中定义的“智能对象”（如椅子、门、可拾取物）进行交互时，如何执行预定义的复杂行为（而不仅仅是播放动画）的问题。插件通过提供一个标准化的行为定义类和专用的 AI 任务节点，让开发者能够方便地将 `GameplayBehavior` 系统配置为 `SmartObject` 的默认运行时行为，从而让 AI 在到达智能对象位置后能自动执行一套包含动画、游戏逻辑和状态转换的完整交互流程。

## 使用场景

- 你在开发一个开放世界或沉浸式模拟游戏，AI 需要能自主地与场景中的各种可交互物品（如坐在长椅上、操作控制台、拾取道具）进行互动。
- 你希望使用 `SmartObjects` 框架来高效管理和分配场景中的可交互点，同时使用 `GameplayBehaviors` 框架来定义和执行具体的交互逻辑（例如，坐下行为包含走向座椅、播放坐下动画、修改角色状态、计时、播放站起动画等一系列步骤）。
- 你需要在行为树中快速添加一个“寻找并使用附近智能对象”的通用节点，而无需为每种交互类型编写自定义任务。

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `UseSmartObjectWithGameplayBehavior` | 创建一个 AI 任务，让 AI 立即开始使用已认领的智能对象槽位，无需移动。需要 AI 已经在目标位置。 | `UAITask_UseGameplayBehaviorSmartObject` |
| `MoveToAndUseSmartObjectWithGameplayBehavior` | 创建一个 AI 任务，让 AI 移动到智能对象槽位位置，然后执行其关联的 GameplayBehavior。这是最常用的节点。 | `UAITask_UseGameplayBehaviorSmartObject` |
| `FindAndUseGameplayBehaviorSmartObject` | 一个行为树任务节点，自动查找满足条件的智能对象（通过 EQS 或半径搜索），认领槽位，并执行其 GameplayBehavior。 | `UBTTask_FindAndUseGameplayBehaviorSmartObject` |

### 使用示例（蓝图描述）

**示例 1：在行为树中直接使用（推荐）**
1. 在你的 AI 行为树中，添加一个 `UBTTask_FindAndUseGameplayBehaviorSmartObject` 节点。
2. 在节点的细节面板中，配置搜索方式：
    - 如果需要精确搜索，设置 `EQSRequest` 属性，关联一个环境查询。
    - 如果需要简单范围搜索，设置 `Radius` 属性。
3. 运行时，AI 会自动寻找附近的智能对象，认领它，移动过去，然后执行预定义的 `GameplayBehavior`。

**示例 2：通过 AI 任务蓝图手动控制**
1. 在自定义的 AI 任务蓝图中，首先使用 Smart Objects 模块的函数（如 `FindSmartObject`）获取一个 `FSmartObjectClaimHandle`。
2. 调用 `UseSmartObjectWithGameplayBehavior` 或 `MoveToAndUseSmartObjectWithGameplayBehavior` 节点，传入 `AAIController` 和获取的认领句柄。
3. 该节点会返回一个 `UAITask_UseGameplayBehaviorSmartObject` 任务实例。可以将其连接到后续任务（如等待成功/失败）。
4. 通过任务实例的 `OnSucceeded` 或 `OnFailed` 委托来监听交互结果。

## C++ 用法

### 头文件引入

```cpp
#include "AI/AITask_UseGameplayBehaviorSmartObject.h"
#include "AI/BTTask_FindAndUseGameplayBehaviorSmartObject.h"
#include "GameplayBehaviorSmartObjectBehaviorDefinition.h"
```

### 基本用法

**1. 为智能对象定义 GameplayBehavior 配置**

首先，需要在编辑器中创建一个 `UGameplayBehaviorSmartObjectBehaviorDefinition` 资产，并将其分配给 `USmartObjectComponent`。这个定义指向一个具体的 `UGameplayBehaviorConfig`。

```cpp
// (概念性代码，通常在编辑器中配置，非直接C++编写)
// 1. 创建 UGameplayBehaviorConfig (例如，一个用于“坐下”的行为配置)
// 2. 创建 UGameplayBehaviorSmartObjectBehaviorDefinition 资产，将其 GameplayBehaviorConfig 属性设置为上述配置。
// 3. 将该 Definition 资产设置到场景中某个 SmartObjectComponent 的 “Behavior Definition” 属性上。
```

**2. 在C++代码中创建和使用AI任务**

```cpp
#include "AI/AITask_UseGameplayBehaviorSmartObject.h"
#include "SmartObjectSubsystem.h"

void AMyAIController::UseSmartObjectFromCpp()
{
    // 1. 获取智能对象子系统并认领一个槽位 (简化示例)
    USmartObjectSubsystem* SmartObjectSubsystem = GetWorld()->GetSubsystem<USmartObjectSubsystem>();
    FSmartObjectClaimHandle ClaimHandle = /* 通过查询获得的有效句柄 */;

    // 2. 创建并启动 AI 任务
    UAITask_UseGameplayBehaviorSmartObject* Task = UAITask_UseGameplayBehaviorSmartObject::MoveToAndUseSmartObjectWithGameplayBehavior(
        this, // AAIController*
        ClaimHandle,
        true // bLockAILogic
    );

    if (Task)
    {
        // 3. 绑定回调
        Task->OnSucceeded.AddDynamic(this, &AMyAIController::OnSmartObjectUseSucceeded);
        Task->OnFailed.AddDynamic(this, &AMyAIController::OnSmartObjectUseFailed);
        // 4. 激活任务
        Task->ReadyForActivation();
    }
}

void AMyAIController::OnSmartObjectUseSucceeded()
{
    UE_LOG(LogTemp, Log, TEXT("Successfully used smart object!"));
}

void AMyAIController::OnSmartObjectUseFailed()
{
    UE_LOG(LogTemp, Warning, TEXT("Failed to use smart object."));
}
```

### 进阶用法

**自定义行为树任务节点**

你可以继承 `UBTTask_FindAndUseGameplayBehaviorSmartObject` 来添加更复杂的查找逻辑或后处理。

```cpp
// MyBTTask_FindAndUseSpecialSmartObject.h
UCLASS()
class UMyBTTask_FindAndUseSpecialSmartObject : public UBTTask_FindAndUseGameplayBehaviorSmartObject
{
    GENERATED_BODY()

protected:
    // 重写执行任务，添加额外检查
    virtual EBTNodeResult::Type ExecuteTask(UBehaviorTreeComponent& OwnerComp, uint8* NodeMemory) override
    {
        // 例如，在执行前检查AI是否有特定物品
        AAIController* Controller = OwnerComp.GetAIOwner();
        if (Controller && /* 有特定物品 */)
        {
            return Super::ExecuteTask(OwnerComp, NodeMemory);
        }
        return EBTNodeResult::Failed;
    }

    // 重写搜索完成处理
    virtual void OnQueryFinished(TSharedPtr<FEnvQueryResult> Result) override
    {
        // 对搜索结果进行二次筛选
        Super::OnQueryFinished(Result);
    }
};
```

## Demo 示例

以下是一个最小的 C++ 示例，展示如何创建一个自定义的 AI 控制器来使用此插件。

**MySmartObjectAIController.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "AIController.h"
#include "MySmartObjectAIController.generated.h"

UCLASS()
class AMySmartObjectAIController : public AAIController
{
    GENERATED_BODY()

public:
    AMySmartObjectAIController();

protected:
    virtual void BeginPlay() override;

    UFUNCTION()
    void OnSmartObjectInteractionSucceeded();

    UFUNCTION()
    void OnSmartObjectInteractionFailed();

private:
    void FindAndUseNearbySmartObject();
};
```

**MySmartObjectAIController.cpp**
```cpp
#include "MySmartObjectAIController.h"
#include "AI/AITask_UseGameplayBehaviorSmartObject.h"
#include "BehaviorTree/BehaviorTree.h"
#include "BehaviorTree/BehaviorTreeComponent.h"
#include "BehaviorTree/BlackboardComponent.h"
#include "SmartObjectSubsystem.h"

AMySmartObjectAIController::AMySmartObjectAIController()
{
    // 如果你计划用行为树驱动，可以在这里创建组件
    // BehaviorTreeComponent = CreateDefaultSubobject<UBehaviorTreeComponent>(TEXT("BehaviorTreeComp"));
    // BlackboardComponent = CreateDefaultSubobject<UBlackboardComponent>(TEXT("BlackboardComp"));
}

void AMySmartObjectAIController::BeginPlay()
{
    Super::BeginPlay();
    // 简单示例：游戏开始后尝试寻找智能对象
    FindAndUseNearbySmartObject();
}

void AMySmartObjectAIController::FindAndUseNearbySmartObject()
{
    USmartObjectSubsystem* SOSubsystem = GetWorld()->GetSubsystem<USmartObjectSubsystem>();
    if (!SOSubsystem) return;

    // 这里简化：假设通过某种方式（如EQS）已经找到了一个有效的 ClaimHandle
    FSmartObjectClaimHandle ClaimHandle; // = ... 获取有效句柄的逻辑

    if (ClaimHandle.IsValid())
    {
        // 创建移动并使用的任务
        UAITask_UseGameplayBehaviorSmartObject* Task =
            UAITask_UseGameplayBehaviorSmartObject::MoveToAndUseSmartObjectWithGameplayBehavior(
                this,
                ClaimHandle,
                true
            );

        if (Task)
        {
            Task->OnSucceeded.AddDynamic(this, &AMySmartObjectAIController::OnSmartObjectInteractionSucceeded);
            Task->OnFailed.AddDynamic(this, &AMySmartObjectAIController::OnSmartObjectInteractionFailed);
            Task->ReadyForActivation();
        }
    }
}

void AMySmartObjectAIController::OnSmartObjectInteractionSucceeded()
{
    UE_LOG(LogTemp, Log, TEXT("AI 成功与智能对象交互！"));
}

void AMySmartObjectAIController::OnSmartObjectInteractionFailed()
{
    UE_LOG(LogTemp, Warning, TEXT("AI 与智能对象交互失败。"));
}
```

## 模块依赖

该插件本身依赖 `GameplayBehaviors` 和 `SmartObjects` 插件。你的游戏模块要使用此插件的功能，需要在 `.Build.cs` 文件中添加依赖：

```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "GameplayBehaviors",
    "SmartObjects",
    "GameplayBehaviorSmartObjectsModule" // 如果你需要直接引用该模块的类
});
```

| 模块 | 用途 |
|---|---|
| `GameplayBehaviors` | 提供 GameplayBehavior 系统的基础框架，用于定义可中断、可组合的复杂行为。 |
| `SmartObjects` | 提供智能对象系统，用于管理场景中可交互点的创建、查询、认领和生命周期。 |
| `GameplayBehaviorSmartObjectsModule` | 本插件的核心模块，提供连接两个系统的行为定义类和 AI 任务。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 日志宏迁移，代码规范化更新。 |
| 2025-10-07 | `96352708` | - Renaming Base<Plugin>.ini to Default<Plugin>.ini | 配置文件命名规范变更，影响插件默认设置。 |
| 2025-07-18 | `462ec4ed` | Fix warning V623: Consider inspecting the '?:' operator. A temporary object is being created and sub | 修复三元运算符可能产生临时对象的编译警告。 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME to source files that has corresponding .gen.cpp files. (Applie | 优化编译，为生成的 .cpp 文件添加内联宏。 |
| 2025-06-19 | `38224d46` | PR #13135: Fix Smart Objects Crash | 修复智能对象相关的崩溃问题。 |

### 维护评价

该插件自 **2022 年创建**，距今约 **4 年**。从 Git 历史看，它**仍处于维护中**，最近的提交集中在 2025 年和 2026 年。更新内容主要是**编译警告修复、日志系统迁移、命名规范调整和关键崩溃修复**，而非新功能开发。

需要注意的是，该插件在 `.uplugin` 中明确标记为 **`IsExperimentalVersion: true`**，并且 **`Installed: false`**。这意味着：
1.  **实验性**：API 和功能在未来版本中可能发生变化或被重构，不建议用于需要高度稳定性的生产环境。
2.  **非默认安装**：需要在项目设置中手动启用。

**综合评价**：这是一个功能明确、仍在维护的**实验性插件**。它解决了 AI 与智能对象交互的常见需求，并与 UE5 的官方 AI 框架（行为树、EQS）集成良好。如果你的项目需要快速实现 AI 环境交互，并且可以接受实验性 API 可能带来的未来变更风险，那么可以尝试使用。建议密切关注引擎版本更新时的兼容性说明。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayBehaviorSmartObjects)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/GameplayBehaviorSmartObjects/Tests) (如果存在)