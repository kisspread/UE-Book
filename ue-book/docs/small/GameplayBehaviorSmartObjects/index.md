# GameplayBehaviorSmartObjects

> Plugins for SmartObjects using GameplayBehavior as their default runtime behavior

| 属性 | 值 |
|---|---|
| 分类 | Runtime |
| 默认启用 | 是（Installed=false，需手动启用） |
| 包含内容 | true |
| 模块 | GameplayBehaviorSmartObjectsModule (Runtime, PreDefault) |
| 创建时间 | 2022-05-02 |
| 年龄标签 | 🆕（~4年） |
| 实验性 | ⚠️ IsExperimentalVersion=true |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayBehaviorSmartObjects) | |

## 用途

这个 plugin 是 **SmartObjects** 和 **GameplayBehaviors** 两个框架之间的桥梁。

- **SmartObjects** 提供了"场景中的交互点"抽象——椅子、武器架、门把手等，管理占用/释放 slot 的生命周期。
- **GameplayBehaviors** 提供了"可重复使用的行为逻辑"抽象——坐在椅子上、捡起武器、开门等具体的交互表现。

本 plugin 的核心价值是：**让 AI 通过 Behavior Tree 或 AITask 一键完成"找到 SmartObject → 移动到旁边 → 执行 GameplayBehavior"的完整流程**。没有它，你需要手动编排找到 SO、Claim slot、移动、触发 behavior、等待完成、释放 slot 这一整套逻辑。

插件很小（~5 个源文件），但它是连接两个重要子系统的关键胶水层。

## 使用场景

- 你在做一个 NPC 驱动的开放世界游戏，NPC 需要自动找到空闲的座位坐下（SmartObject = 椅子，GameplayBehavior = 坐下动画）
- 你的 AI 角色需要在巡逻时自动与场景中的可交互对象互动（拾取物品、操作机器）
- 你需要在 Behavior Tree 中用一个节点完成"查找 + 移动 + 使用" SmartObject 的完整流程
- 你想让 AI 通过 EQS（Environment Query System）找到最优的 SmartObject 并自动前往

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所属类 |
|---|---|---|
| `UseSmartObjectWithGameplayBehavior` | 使用已 Claim 的 SmartObject slot 执行 GameplayBehavior（需已在目标位置） | `UAITask_UseGameplayBehaviorSmartObject` |
| `MoveToAndUseSmartObjectWithGameplayBehavior` | 移动到 SmartObject slot 位置后执行 GameplayBehavior | `UAITask_UseGameplayBehaviorSmartObject` |
| ~~`UseGameplayBehaviorSmartObject`~~ | ⚠️ 已废弃（5.3），改用上方基于 ClaimHandle 的版本 | `UAITask_UseGameplayBehaviorSmartObject` |
| ~~`UseGameplayBehaviorSmartObject`~~ | ⚠️ 已废弃（5.3）蓝图库函数 | `UGameplayBehaviorSmartObjectsBlueprintFunctionLibrary` |

> **注意**：所有 `UAITask` 函数标记了 `BlueprintInternalUseOnly="true"`，这意味着它们主要设计为在 Behavior Tree 节点内部调用，而非直接在蓝图图表中拖拽使用。在蓝图中使用时通常通过 BT Task 间接调用。

### 蓝图中的使用方式

由于核心函数是 `BlueprintInternalUseOnly`，蓝图端最常见的用法是：

1. **配置 Behavior Tree**：在 Behavior Tree 中添加 `Find And Use Gameplay Behavior Smart Object` 节点
2. **配置 SmartObject Actor**：在场景中的 Actor 上添加 `SmartObjectComponent`，在 Definition 中添加 `GameplayBehaviorSmartObjectBehaviorDefinition`，设置 `GameplayBehaviorConfig`
3. **运行**：AI Controller 运行 Behavior Tree 时，节点自动查找、移动、执行行为

## C++ 用法

### 头文件引入

```cpp
#include "AI/AITask_UseGameplayBehaviorSmartObject.h"
#include "AI/BTTask_FindAndUseGameplayBehaviorSmartObject.h"
#include "GameplayBehaviorSmartObjectBehaviorDefinition.h"
```

### 基本用法：创建 AITask 使用已 Claim 的 SmartObject

来自 `AITask_UseGameplayBehaviorSmartObject.cpp` 的核心流程：

```cpp
// 前提：你已经通过 SmartObjectSubsystem 获取了一个 ClaimHandle
FSmartObjectClaimHandle ClaimHandle = SmartObjectSubsystem->MarkSlotAsClaimed(SlotHandle, ClaimPriority, ActorUserData);

// 方式 1：原地使用（AI 已在 SmartObject 附近）
UAITask_UseGameplayBehaviorSmartObject* Task = 
    UAITask_UseGameplayBehaviorSmartObject::UseSmartObjectWithGameplayBehavior(
        AIController, 
        ClaimHandle, 
        true  // bLockAILogic - 锁定 AI 逻辑防止被更高优先级任务抢占
    );
Task->ReadyForActivation();

// 方式 2：移动到 SmartObject 后使用
UAITask_UseGameplayBehaviorSmartObject* Task = 
    UAITask_UseGameplayBehaviorSmartObject::MoveToAndUseSmartObjectWithGameplayBehavior(
        AIController, 
        ClaimHandle, 
        true  // bLockAILogic
    );
Task->ReadyForActivation();
```

### 进阶用法：监听完成事件

`UAITask_UseGameplayBehaviorSmartObject` 暴露了三个 BlueprintAssignable delegate：

```cpp
// 绑定成功回调
Task->OnSucceeded.AddDynamic(this, &AMyAI::OnSmartObjectUseSucceeded);

// 绑定失败回调（行为中断或移动失败）
Task->OnFailed.AddDynamic(this, &AMyAI::OnSmartObjectUseFailed);

// 绑定移动失败回调（仅 MoveToAndUse 模式）
Task->OnMoveToFailed.AddDynamic(this, &AMyAI::OnMoveToFailed);
```

### 进阶用法：在 Behavior Tree 中使用

`UBTTask_FindAndUseGameplayBehaviorSmartObject` 是一个现成的 BT Task 节点，内部自动完成：

1. 通过 EQS 或半径搜索找到 SmartObject
2. Claim slot
3. 创建 `UAITask_UseGameplayBehaviorSmartObject` 并移动到目标
4. 触发 GameplayBehavior

在 C++ 中也可以自定义 BT Task 来替代或扩展此行为：

```cpp
// 从 BTTask_FindAndUseGameplayBehaviorSmartObject 源码可以看到内部流程：
// ExecuteTask 中：
//   - 如果配置了 EQSRequest，通过 EQS 查询
//   - 否则，用 FSmartObjectRequest 基于半径查找
//   - 找到后 MarkSlotAsClaimed
//   - 创建 UseSOTask 并 SetShouldReachSlotLocation(true)
//   - ReadyForActivation
```

## 内部架构

本 plugin 的核心类关系如下：

```
UGameplayBehaviorSmartObjectBehaviorDefinition  (数据层)
    ├── 继承自 USmartObjectBehaviorDefinition
    └── 持有 UGameplayBehaviorConfig* - 配置要执行的行为

UAITask_UseGameplayBehaviorSmartObject  (执行层)
    ├── 继承自 UAITask
    ├── UseSmartObjectWithGameplayBehavior()     - 原地执行
    ├── MoveToAndUseSmartObjectWithGameplayBehavior() - 移动后执行
    ├── 内部使用 UAITask_MoveTo 处理移动
    └── 通过 UGameplayBehaviorSubsystem::TriggerBehavior() 触发行为

UBTTask_FindAndUseGameplayBehaviorSmartObject  (BT 集成层)
    ├── 继承自 UBTTaskNode
    ├── 支持 EQS 查询 或 半径搜索
    ├── ActivityRequirements (GameplayTagQuery) 过滤
    └── 自动创建 UAITask_UseGameplayBehaviorSmartObject
```

**执行流程**：
1. BT Task 或代码中找到 SmartObject → Claim slot
2. AITask 启动 → 如需移动，先执行 MoveTo
3. 移动完成后 → `MarkSlotAsOccupied` 获取 `GameplayBehaviorSmartObjectBehaviorDefinition`
4. 从 Definition 中取出 `GameplayBehaviorConfig` → 实例化 `GameplayBehavior`
5. 调用 `UGameplayBehaviorSubsystem::TriggerBehavior()` 执行行为
6. 行为完成后 → 释放 slot → 触发 OnSucceeded/OnFailed

## Demo 示例

### 最小示例：C++ 中直接使用 SmartObject

```cpp
// MyAIController.h
#pragma once
#include "AIController.h"
#include "MyAIController.generated.h"

UCLASS()
class AMyAIController : public AAIController
{
    GENERATED_BODY()
public:
    void UseNearbySmartObject();

private:
    UFUNCTION()
    void OnBehaviorSucceeded();

    UFUNCTION() 
    void OnBehaviorFailed();
};
```

```cpp
// MyAIController.cpp
#include "MyAIController.h"
#include "AI/AITask_UseGameplayBehaviorSmartObject.h"
#include "SmartObjectSubsystem.h"
#include "SmartObjectComponent.h"
#include "GameplayBehaviorSmartObjectBehaviorDefinition.h"

void AMyAIController::UseNearbySmartObject()
{
    APawn* MyPawn = GetPawn();
    if (!MyPawn) return;

    USmartObjectSubsystem* SOSubsystem = USmartObjectSubsystem::GetCurrent(GetWorld());
    if (!SOSubsystem) return;

    // 1. 搜索附近的 SmartObject
    FSmartObjectRequestFilter Filter;
    Filter.BehaviorDefinitionClasses = { UGameplayBehaviorSmartObjectBehaviorDefinition::StaticClass() };

    FSmartObjectRequest Request(FBox(MyPawn->GetActorLocation(), MyPawn->GetActorLocation()).ExpandBy(FVector(500.f)), Filter);
    TArray<FSmartObjectRequestResult> Results;
    const FSmartObjectActorUserData UserData(MyPawn);
    const FConstStructView UserDataView(FConstStructView::Make(UserData));

    if (!SOSubsystem->FindSmartObjects(Request, Results, UserDataView) || Results.IsEmpty())
    {
        return;
    }

    // 2. Claim 第一个可用 slot
    FSmartObjectClaimHandle ClaimHandle = SOSubsystem->MarkSlotAsClaimed(
        Results[0].SlotHandle, ESmartObjectClaimPriority::Normal, UserDataView);
    if (!ClaimHandle.IsValid()) return;

    // 3. 创建 AITask 移动到目标并使用
    UAITask_UseGameplayBehaviorSmartObject* Task = 
        UAITask_UseGameplayBehaviorSmartObject::MoveToAndUseSmartObjectWithGameplayBehavior(
            this, ClaimHandle, true);
    
    if (Task)
    {
        Task->OnSucceeded.AddDynamic(this, &AMyAIController::OnBehaviorSucceeded);
        Task->OnFailed.AddDynamic(this, &AMyAIController::OnBehaviorFailed);
        Task->ReadyForActivation();
    }
}

void AMyAIController::OnBehaviorSucceeded()
{
    UE_LOG(LogTemp, Log, TEXT("SmartObject behavior completed successfully!"));
}

void AMyAIController::OnBehaviorFailed()
{
    UE_LOG(LogTemp, Warning, TEXT("SmartObject behavior failed or was interrupted."));
}
```

**Build.cs 依赖**：

```csharp
PublicDependencyModuleNames.AddRange(new string[]
{
    "AIModule",
    "GameplayBehaviorsModule",   // GameplayBehavior 框架
    "GameplayTags",
    "GameplayTasks",
    "SmartObjectsModule"         // SmartObject 框架
});
```

## 模块依赖

从 Build.cs 的 `PublicDependencyModuleNames` 提取：

| 模块 | 用途 |
|---|---|
| `AIModule` | AIController、AITask 基础设施 |
| `Core` | UE 核心基础库 |
| `GameplayBehaviorsModule` | GameplayBehavior 框架（行为定义和执行） |
| `GameplayTags` | GameplayTag 系统（用于 ActivityRequirements 过滤） |
| `GameplayTasks` | GameplayTask 基础设施（AITask 的基类） |
| `SmartObjectsModule` | SmartObject 框架（slot 管理、subsystem） |

Private 依赖：

| 模块 | 用途 |
|---|---|
| `CoreUObject` | UObject 系统 |
| `Engine` | 引擎核心（Actor、World 等） |

## 维护状态

### 近期更新

| 日期 | Hash | 说明 | 解读 |
|---|---|---|---|
| 2025-07-18 | `462ec4ed` | Fix warning V623: Consider inspecting the '?:' operator | 静态分析警告修复，三元运算符临时对象问题 |
| 2025-06-26 | `ec900998` | Added UE_INLINE_GENERATED_CPP_BY_NAME | 批量添加内联生成宏，编译优化，非功能性改动 |
| 2025-06-19 | `38224d46` | PR #13135: Fix Smart Objects Crash | 修复 SmartObject 崩溃 bug，实质性修复 |

### 维护评价

- **创建时间**：2022 年 5 月，约 4 年历史
- **实验性状态**：`IsExperimentalVersion=true`，虽然 `IsBetaVersion=false`，但 Epic 官方仍标记为实验性
- **近期活跃度**：2025 年 6-7 月有 3 次更新，包含 bug 修复，属于活跃维护
- **API 稳定性**：5.3 版本经历了一次重大 API 重构（旧接口标记废弃，迁移到 ClaimHandle 机制），Config 中有大量 CoreRedirects 证明这一点
- **代码质量**：代码量小（~600 行有效代码），结构清晰，有 VisualLogger 支持
- **已知限制**：依赖 `GameplayBehaviors` plugin（同样是实验性），两个实验性 plugin 的叠加使用需要谨慎
- **推荐程度**：如果你的项目已经使用了 SmartObjects + GameplayBehaviors，这个 bridge plugin 是必需的。但要注意它仍标记为实验性，未来可能有 API 变动

⚠️ **警告**：此 plugin 标记为 `IsExperimentalVersion=true`，在生产环境中使用需评估风险。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayBehaviorSmartObjects)
- 官方文档：无（.uplugin 中 DocsURL 为空）
- 依赖插件：[GameplayBehaviors](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/GameplayBehaviors)、[SmartObjects](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/SmartObjects)
- 测试用例：未在 Engine/Tests 目录下发现独立测试文件
