# HTN Planner

> [EXPERIMENTAL] Adds experimental support for Hierarchical Task Network (HTN) planner to the UE4's AI module

| 属性 | 值 |
|---|---|
| 分类 | AI |
| 默认启用 | false |
| 包含内容 | false |
| 模块 | HTNPlanner (Runtime), HTNTestSuite (UncookedOnly) |
| 创建时间 | 2018-04-16 |
| 年龄标签 | 👴 老古董（约8年） |
| IsBetaVersion | true |
| [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/AI/HTNPlanner) | |

## 用途

HTN（Hierarchical Task Network，层次任务网络）是一种 AI 规划方法，与行为树（Behavior Tree）互补但思路不同。行为树是"每帧从根节点评估"，而 HTN 是"预先生成一个行动计划，然后按步骤执行"。

HTNPlanner plugin 的核心功能：
1. **定义任务域（Domain）**：声明复合任务（Composite Task，可分解为子任务）和原始任务（Primitive Task，可直接执行的原子操作）
2. **基于世界状态规划**：给定当前世界状态（WorldState），HTN 规划器会递归分解复合任务，检查条件，选择满足条件的方法（Method），最终生成一个原始任务序列（Plan）
3. **自动回滚**：当某个分支的条件不满足时，规划器会回退并尝试其他方法

这个 plugin 解决的核心问题是：**当 NPC 需要做多步决策（比如"找到武器→拾取→接近敌人→攻击"）时，用声明式的方式定义任务层级，让规划器自动找到可行的行动序列**。

> ⚠️ **实验性警告**：此 plugin 标记为 `IsBetaVersion=true`，`EnabledByDefault=false`。需要手动在 .uproject 或编辑器中启用。API 可能不稳定，Epic 也没有提供官方文档。

## 使用场景

- **NPC AI 行为规划**：NPC 需要根据当前环境（是否有武器、敌人是否可见等）动态生成多步行动方案
- **复杂任务分解**：例如"攻击敌人"可以分解为"有武器→导航到敌人→使用武器"或"没武器→找到武器→导航到武器→拾取→再次攻击"
- **与行为树配合**：HTN 负责高层规划（决定做什么），行为树负责底层执行（怎么做）
- **战略/战术 AI**：RTS 游戏中的单位编队决策、任务分配等

## 蓝图用法

此 plugin 没有暴露任何 `BlueprintCallable` 函数或 `BlueprintReadWrite` 属性。所有 API 都是 C++ 层面的。`UHTNBrainComponent` 继承自 `UBrainComponent`，但自身没有额外的蓝图接口。

**唯一与蓝图相关的集成点**是通过 `UHTNBrainComponent` 挂载到 AI Controller 上，但具体的规划逻辑需要在 C++ 中编写。

## C++ 用法

### 核心概念

| 概念 | 类型 | 说明 |
|---|---|---|
| WorldState | `FHTNWorldState` | 键值对数组，表示 AI 对世界的认知（如"敌人血量"、"是否有武器"） |
| Condition | `FHTNCondition` | 条件检查（如"敌人血量 > 0"），用于方法选择 |
| Effect | `FHTNEffect` | 效果（如"设置当前位置为敌人位置"），用于规划时模拟世界状态变化 |
| Composite Task | `FHTNBuilder_CompositeTask` | 复合任务，包含多个 Method，每个 Method 有前置条件和子任务列表 |
| Primitive Task | `FHTNBuilder_PrimitiveTask` | 原始任务，可直接执行，有 Operator（动作ID + 参数）和 Effect |
| Domain | `FHTNBuilder_Domain` | 任务域，包含所有任务的定义 |
| Planner | `FHTNPlanner` | 规划器，接受 Domain + WorldState，输出 Plan |
| Result | `FHTNResult` | 规划结果，包含 TaskIDs 和 ActionsSequence |

### 头文件引入

```cpp
#include "HTNBuilder.h"    // FHTNBuilder_Domain, FHTNBuilder_CompositeTask, FHTNBuilder_PrimitiveTask
#include "HTNPlanner.h"    // FHTNPlanner, FHTNResult
#include "HTNDomain.h"     // FHTNWorldState, FHTNCondition, FHTNEffect
```

### 步骤 1：定义世界状态枚举

首先定义你的世界状态键（World State Keys），用于标识不同的世界属性。

```cpp
// 来源: Source/HTNTestSuite/Private/MockHTN.h
enum class EMyWorldState : uint8
{
    EnemyHealth,
    EnemyActor,
    Ammo,
    HasWeapon,
    MoveDestination,
    PickupLocation,
    CurrentLocation,
    CanSeeEnemy,

    MAX
};
```

### 步骤 2：定义任务操作符枚举

定义原始任务对应的操作类型：

```cpp
// 来源: Source/HTNTestSuite/Private/MockHTN.h
enum class EMyTaskOperator : uint8
{
    DummyOperation,
    FindPatrolPoint,
    FindWeapon,
    NavigateTo,
    PickUp,
    UseWeapon,

    MAX
};
```

### 步骤 3：构建任务域（Domain）

这是最核心的部分。通过 `FHTNBuilder_Domain` 构建任务层级。

```cpp
// 来源: Source/HTNTestSuite/Private/HTNTest.cpp - FHTNTestBase::PopulateDomain()
FHTNBuilder_Domain DomainBuilder;

// 设置根任务名称
DomainBuilder.SetRootName(TEXT("Root"));

// === 定义复合任务 ===

// Root 复合任务：有两个方法
FHTNBuilder_CompositeTask& RootTask = DomainBuilder.AddCompositeTask(TEXT("Root"));

// 方法1：如果敌人血量>0 且 敌人Actor存在 → 攻击敌人
{
    FHTNBuilder_Method& Method = RootTask.AddMethod(
        TArray<FHTNCondition>({
            FHTNCondition(EMyWorldState::EnemyHealth, EHTNWorldStateCheck::Greater).SetRHSAsValue(0),
            FHTNCondition(EMyWorldState::EnemyActor, EHTNWorldStateCheck::IsTrue)
        })
    );
    Method.AddTask(TEXT("AttackEnemy"));
}

// 方法2：（无条件）→ 巡逻
{
    FHTNBuilder_Method& Method = RootTask.AddMethod();
    Method.AddTask(TEXT("FindPatrolPoint"));
    Method.AddTask(TEXT("NavigateToMoveDestination"));
}

// AttackEnemy 复合任务：有两个方法
FHTNBuilder_CompositeTask& AttackTask = DomainBuilder.AddCompositeTask(TEXT("AttackEnemy"));

// 方法1：有武器 → 导航到敌人→使用武器→(递归)继续攻击
{
    FHTNBuilder_Method& Method = AttackTask.AddMethod(
        FHTNCondition(EMyWorldState::HasWeapon, EHTNWorldStateCheck::IsTrue)
    );
    Method.AddTask(TEXT("NavigateToEnemy"));
    Method.AddTask(TEXT("UseWeapon"));
    Method.AddTask(TEXT("Root"));  // 递归！继续评估
}

// 方法2：（无条件）→ 找武器→导航→拾取→再次攻击
{
    FHTNBuilder_Method& Method = AttackTask.AddMethod();
    Method.AddTask(TEXT("FindWeapon"));
    Method.AddTask(TEXT("NavigateToWeapon"));
    Method.AddTask(TEXT("PickUp"));
    Method.AddTask(TEXT("AttackEnemy"));
}

// === 定义原始任务（带 Operator 和 Effect） ===

// FindPatrolPoint：操作符=FindPatrolPoint，参数=MoveDestination
{
    FHTNBuilder_PrimitiveTask& Task = DomainBuilder.AddPrimitiveTask(TEXT("FindPatrolPoint"));
    Task.SetOperator(EMyTaskOperator::FindPatrolPoint, EMyWorldState::MoveDestination);
}

// NavigateToMoveDestination：导航到目标位置，效果=更新当前位置
{
    FHTNBuilder_PrimitiveTask& Task = DomainBuilder.AddPrimitiveTask(TEXT("NavigateToMoveDestination"));
    Task.SetOperator(EMyTaskOperator::NavigateTo, EMyWorldState::MoveDestination);
    Task.AddEffect(FHTNEffect(EMyWorldState::CurrentLocation, EHTNWorldStateOperation::Set)
        .SetRHSAsWSKey(EMyWorldState::MoveDestination));
}

// NavigateToEnemy：导航到敌人，效果=更新当前位置 + 看到敌人
{
    FHTNBuilder_PrimitiveTask& Task = DomainBuilder.AddPrimitiveTask(TEXT("NavigateToEnemy"));
    Task.SetOperator(EMyTaskOperator::NavigateTo, EMyWorldState::EnemyActor);
    Task.AddEffect(FHTNEffect(EMyWorldState::CurrentLocation, EHTNWorldStateOperation::Set)
        .SetRHSAsWSKey(EMyWorldState::EnemyActor));
    Task.AddEffect(FHTNEffect(EMyWorldState::CanSeeEnemy, EHTNWorldStateOperation::Set)
        .SetRHSAsValue(1));
}

// PickUp：拾取武器，效果=HasWeapon=1
{
    FHTNBuilder_PrimitiveTask& Task = DomainBuilder.AddPrimitiveTask(TEXT("PickUp"));
    Task.SetOperator(EMyTaskOperator::PickUp, EMyWorldState::PickupLocation);
    Task.AddEffect(FHTNEffect(EMyWorldState::HasWeapon, EHTNWorldStateOperation::Set)
        .SetRHSAsValue(1));
}

// UseWeapon：使用武器，效果=弹药-1，敌人血量-1
{
    FHTNBuilder_PrimitiveTask& Task = DomainBuilder.AddPrimitiveTask(TEXT("UseWeapon"));
    Task.SetOperator(EMyTaskOperator::UseWeapon, EMyWorldState::EnemyActor);
    Task.AddEffect(FHTNEffect(EMyWorldState::Ammo, EHTNWorldStateOperation::Decrease).SetRHSAsValue(1));
    Task.AddEffect(FHTNEffect(EMyWorldState::EnemyHealth, EHTNWorldStateOperation::Decrease).SetRHSAsValue(1));
}

// === 编译域 ===
// 编译后不可再修改！返回 false 表示有错误（如引用了不存在的任务名）
bool bSuccess = DomainBuilder.Compile();
```

### 步骤 4：设置世界状态并执行规划

```cpp
// 来源: Source/HTNTestSuite/Private/HTNTest.cpp - FAITest_HTNPlanning
FHTNWorldState WorldState(128);  // 128 个键

// 初始化世界状态（可选，按需设置）
WorldState.SetValueUnsafe(FHTNPolicy::FWSKey(EMyWorldState::EnemyHealth), 1);
WorldState.SetValueUnsafe(FHTNPolicy::FWSKey(EMyWorldState::EnemyActor), 1);

// 创建规划器并生成计划
FHTNPlanner Planner;
FHTNResult Result;
Planner.GeneratePlan(*(DomainBuilder.DomainInstance), WorldState, Result);

// 读取结果
for (int32 i = 0; i < Result.TaskIDs.Num(); ++i)
{
    FHTNPolicy::FTaskID TaskID = Result.TaskIDs[i];
    FHTNExecutableAction& Action = Result.ActionsSequence[i];
    // TaskID: 任务ID，Action.ActionID: 操作符ID，Action.Parameter: 参数
}
```

### 步骤 5：动态修改世界状态并重新规划

```cpp
// 来源: Source/HTNTestSuite/Private/HTNTest.cpp - FAITest_HTNPlanning
// 修改世界状态
WorldState.ApplyEffect(FHTNEffect(EMyWorldState::EnemyHealth, EHTNWorldStateOperation::Set).SetRHSAsValue(1));
WorldState.ApplyEffect(FHTNEffect(EMyWorldState::EnemyActor, EHTNWorldStateOperation::Set).SetRHSAsValue(1));

// 重新规划
Planner.GeneratePlan(*(DomainBuilder.DomainInstance), WorldState, Result);
// 现在 Result 会包含攻击相关的任务序列
```

### 进阶用法

#### 自定义条件检查函数

当内置的比较运算（Less/Equal/Greater 等）不够用时，可以注册自定义检查函数：

```cpp
// 来源: Source/HTNTestSuite/Private/HTNTest.cpp - FAITest_HTNCustomWSCheck

// 定义自定义检查函数
static bool MyCustomCheck(const FHTNPolicy::FWSValue* Values, const FHTNCondition& Condition)
{
    // 自定义逻辑，例如：检查某个复杂的游戏状态
    return true;
}

// 注册，返回一个 ID
const uint32 CustomCheckID = FHTNWorldStateOperations::RegisterCustomCheckType(
    &MyCustomCheck, TEXT("MyCustomCheck"));

// 在条件中使用
FHTNBuilder_Method& Method = CompositeTask.AddMethod(
    FHTNCondition(0, IntCastChecked<FHTNPolicy::FWSOperationID>(CustomCheckID))
);
```

#### 自定义世界状态操作函数

```cpp
// 来源: Source/HTNTestSuite/Private/HTNTest.cpp - FAITest_HTNCustomWSOperation

// 定义自定义操作函数
static uint32 Counter = 0;
static void MyCustomOperation(FHTNPolicy::FWSValue* Values, const FHTNEffect& Effect)
{
    ++Counter;
    Values[Effect.KeyLeftHand] = Counter * 1024;
}

// 注册
const uint32 CustomOpID = FHTNWorldStateOperations::RegisterCustomOperationType(
    &MyCustomOperation, TEXT("MyCustomOperation"));

// 在原始任务的效果中使用
FHTNBuilder_PrimitiveTask& Task = DomainBuilder.AddPrimitiveTask(TEXT("Task1"));
Task.AddEffect(FHTNEffect(0, IntCastChecked<FHTNPolicy::FWSOperationID>(CustomOpID)));
```

#### 读取规划后的世界状态

```cpp
// GeneratePlan 会模拟执行效果，可以通过 Planner 获取规划后的世界状态
const FHTNWorldState& FinalState = Planner.GetWorldState();
FHTNPolicy::FWSValue Value = FinalState.GetValueUnsafe(0);
```

#### 从编译后的域反编译回 Builder

```cpp
// 来源: Source/HTNTestSuite/Private/HTNTest.cpp - FAITest_HTNDecompileDomain
FHTNBuilder_Domain DomainBuilder2(DomainBuilder.DomainInstance);
DomainBuilder2.Decompile();
// DomainBuilder2 现在包含了与原始 DomainBuilder 相同的任务定义
```

#### 条件的世界状态比较操作

`EHTNWorldStateCheck` 支持以下比较操作：

| 操作 | 说明 |
|---|---|
| `Less` | < |
| `LessOrEqual` | <= |
| `Equal` | == |
| `NotEqual` | != |
| `GreaterOrEqual` | >= |
| `Greater` | > |
| `IsTrue` | != 0（布尔检查） |

Condition 的 RHS 可以是**固定值**（`SetRHSAsValue`）或**另一个世界状态键**（`SetRHSAsWSKey`），支持键到键的比较：

```cpp
// WS[EnemyHealth] > 0（固定值比较）
FHTNCondition(EMyWorldState::EnemyHealth, EHTNWorldStateCheck::Greater).SetRHSAsValue(0)

// WS[CurrentLocation] == WS[EnemyActor]（键到键比较）
FHTNCondition(EMyWorldState::CurrentLocation, EHTNWorldStateCheck::Equal).SetRHSAsWSKey(EMyWorldState::EnemyActor)
```

## Demo 示例

### 最小可运行示例

**Build.cs 依赖**：
```csharp
PublicDependencyModuleNames.AddRange(new string[] {
    "Core",
    "CoreUObject",
    "Engine",
    "HTNPlanner"
});
```

**MyHTNPlanner.h**：
```cpp
#pragma once

#include "CoreMinimal.h"

// 定义世界状态键
enum class EMyWorldState : uint8
{
    HasAmmo,
    EnemyVisible,
    MAX
};

// 定义操作符
enum class EMyOperator : uint8
{
    Shoot,
    Reload,
    MAX
};
```

**MyHTNPlanner.cpp**：
```cpp
#include "MyHTNPlanner.h"
#include "HTNBuilder.h"
#include "HTNPlanner.h"

void RunHTNPlanning()
{
    // 1. 构建任务域
    FHTNBuilder_Domain DomainBuilder;
    DomainBuilder.SetRootName(TEXT("Root"));

    // Root: 有弹药→射击，无弹药→装弹
    FHTNBuilder_CompositeTask& Root = DomainBuilder.AddCompositeTask(TEXT("Root"));
    {
        FHTNBuilder_Method& Method = Root.AddMethod(
            FHTNCondition(EMyWorldState::HasAmmo, EHTNWorldStateCheck::IsTrue));
        Method.AddTask(TEXT("Shoot"));
    }
    {
        FHTNBuilder_Method& Method = Root.AddMethod();
        Method.AddTask(TEXT("Reload"));
    }

    // Shoot: 射击，效果=弹药减少
    {
        FHTNBuilder_PrimitiveTask& Task = DomainBuilder.AddPrimitiveTask(TEXT("Shoot"));
        Task.SetOperator(EMyOperator::Shoot);
        Task.AddEffect(FHTNEffect(EMyWorldState::HasAmmo, EHTNWorldStateOperation::Decrease).SetRHSAsValue(1));
    }

    // Reload: 装弹，效果=有弹药
    {
        FHTNBuilder_PrimitiveTask& Task = DomainBuilder.AddPrimitiveTask(TEXT("Reload"));
        Task.SetOperator(EMyOperator::Reload);
        Task.AddEffect(FHTNEffect(EMyWorldState::HasAmmo, EHTNWorldStateOperation::Set).SetRHSAsValue(1));
    }

    DomainBuilder.Compile();

    // 2. 设置世界状态（没有弹药）
    FHTNWorldState WorldState;
    WorldState.SetValueUnsafe(FHTNPolicy::FWSKey(EMyWorldState::HasAmmo), 0);

    // 3. 规划
    FHTNPlanner Planner;
    FHTNResult Result;
    Planner.GeneratePlan(*DomainBuilder.DomainInstance, WorldState, Result);

    // 结果：Result.TaskIDs 包含 [Reload] 的 ID
    // 因为 HasAmmo=false，所以选择"装弹"方法
}
```

### 使用 UHTNBrainComponent 集成到 AI Controller

```cpp
// UHTNBrainComponent 继承自 UBrainComponent，可以挂载到 AIController
// 来源: Source/HTNPlanner/Public/AI/HTNBrainComponent.h

UCLASS()
class UMyHTNComponent : public UHTNBrainComponent
{
    GENERATED_BODY()

public:
    // 内部已包含 FHTNPlanner Planner
    // 你可以扩展自己的规划逻辑
};
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `Core` | 基础类型、日志、容器 |
| `CoreUObject` | UObject 系统（UCLASS 等宏） |
| `Engine` | 引擎核心 |
| `GameplayTags` | GameplayTag 系统 |
| `GameplayTasks` | GameplayTask 系统 |
| `AIModule` | AI 框架（BrainComponent 等） |

> 要在你的项目中使用 HTNPlanner，Build.cs 中至少需要：`Core`, `CoreUObject`, `Engine`, `HTNPlanner`

## 维护状态

### 近期更新

| 日期 | Commit | 说明 |
|---|---|---|
| 2025-07-15 | `35e62d592f1e` | 修复/静默 V530 "未处理返回值"编译器警告 |
| 2025-06-10 | `b08804f0ef5c` | 将 AI 模块中部分 `FORCEINLINE` 替换为 `inline` |
| 2025-05-05 | `49a744bd8f3e` | [HTN] 静态分析修复，确保 HTN 域内存分配正确对齐 |

### 维护评价

- **创建时间**：2018 年 4 月，约 8 年历史
- **更新频率**：近 3 次 commit 集中在 2025 年 5-7 月，但全部是**编译器警告修复和静态分析修复**，没有任何功能性更新
- **活跃度**：**不活跃**。自创建以来一直处于实验性状态（`IsBetaVersion=true`），从未正式发布
- **API 完整度**：核心规划功能可用（域构建、规划、条件检查、效果应用），但缺少：
  - 没有蓝图接口
  - 没有官方文档
  - 没有行为树集成节点（需要自行在 BrainComponent 中桥接）
  - 部分测试标记为 `// INJECTION`（未完成）
- **推荐程度**：⚠️ **仅推荐用于学习和实验**。如果你需要在生产项目中使用 HTN 规划，建议考虑第三方方案或自行实现。此 API 随时可能被 Epic 移除或大改。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/AI/HTNPlanner)
- [测试用例](https://github.com/EpicGames/UnrealEngine/blob/5.7/Engine/Plugins/AI/HTNPlanner/Source/HTNTestSuite/Private/HTNTest.cpp)
