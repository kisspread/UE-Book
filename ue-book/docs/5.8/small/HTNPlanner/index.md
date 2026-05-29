# HTN Planner

> [EXPERIMENTAL] Adds experimental support for Hierarchical Task Network (HTN) planner to the UE4's AI module

| 属性 | 值 |
|---|---|
| 中文名 | 分层任务网络规划器 |
| 分类 | AI |
| 默认启用 | ❌ 否 |
| 包含内容 | ❌ 无 |
| 模块 | `HTNPlanner` (Runtime), `HTNTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2018-04-17 |
| 年龄标签 | 👴 老古董（约 8 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/HTNPlanner) | |

## 用途

本插件为 Unreal Engine 的 AI 系统提供了一种 **分层任务网络（Hierarchical Task Network, HTN）规划器** 的实验性支持。HTN 规划器是一种更高级的 AI 决策系统，它允许 AI 代理（Agent）将一个复杂的、高层次的目标（如“搜索并消灭敌人”）分解为一系列更具体、更基础的子任务序列（如“移动到掩体”、“开火”、“寻找弹药”）。与行为树（Behavior Tree）相比，HTN 在处理动态环境和复杂任务分解方面更具灵活性。

**为什么存在？** 它为需要复杂、多层次决策逻辑的 AI 提供了一种替代或补充行为树的方案，特别适合需要动态生成或调整任务计划的场景。

## 使用场景

- 当游戏 AI 需要处理**复杂的多步骤目标**，并且这些目标的实现路径会根据环境动态变化时。
- 当 AI 的行为逻辑更偏向于**任务规划（Planning）** 而非简单的状态机或条件判断时。
- 作为对标准行为树系统的**补充或高级替代方案**，用于原型设计或研究特定的 AI 架构。

## 蓝图用法

由于本插件为实验性且默认不启用，其核心蓝图 API 集中在 `UHTNPlannerComponent` 上，用于在 Actor 上启用和驱动 HTN 规划。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `FindHTNPlan` | 为当前 Actor 寻找并生成一个 HTN 计划（Task Plan）。 | `UHTNPlannerComponent` |
| `StartHTNPlan` | 开始执行已生成的 HTN 计划。 | `UHTNPlannerComponent` |
| `StopHTNPlan` | 强制停止当前正在执行的 HTN 计划。 | `UHTNPlannerComponent` |
| `GetHTNPlanStatus` | 查询当前 HTN 计划的执行状态（如是否正在运行、是否成功等）。 | `UHTNPlannerComponent` |
| `GetHTNWorldState` | 获取用于 HTN 规划的 AI 世界状态。 | `UHTNPlannerComponent` |

### 使用示例（蓝图描述）

1. 在你的 AI 角色蓝图中，添加一个 `UHTNPlannerComponent` 组件。
2. 在需要触发 AI 决策的地方（例如 `BeginPlay` 或感知到玩家时），调用 `FindHTNPlan` 节点来生成计划。
3. 监听规划完成的事件或查询 `GetHTNPlanStatus`，在计划就绪后调用 `StartHTNPlan` 开始执行。
4. 在计划执行过程中，可以通过 `GetHTNWorldState` 修改世界状态（例如“有弹药”、“发现敌人”）来影响后续的规划。
5. 当 AI 需要中断当前行为时，调用 `StopHTNPlan`。

## C++ 用法

### 头文件引入

```cpp
#include "HTNPlanner.h"
// 需要根据具体使用的任务类型包含相应的头文件
// 例如：
#include "HTNTask.h"
```

### 基本用法

配置并启动一个简单的 HTN 规划。
*(来源: `HTNTestSuite` 模块中的测试用例)*

```cpp
// 在 AI 角色或控制器中获取 HTN 组件
UHTNPlannerComponent* HTNComponent = FindComponentByClass<UHTNPlannerComponent>();
if (HTNComponent)
{
    // 定义世界状态 (通常在一个结构体或黑板中)
    FHTNWorldState InitialWorldState;
    InitialWorldState.AddFact(TEXT("HasWeapon"), true);
    InitialWorldState.AddFact(TEXT("EnemyVisible"), true);

    // 为组件设置世界状态
    HTNComponent->SetWorldState(InitialWorldState);

    // 定义要达成的目标任务
    TArray<FHTNTask> GoalTasks;
    GoalTasks.Add(FHTNTask(TEXT("DefeatEnemy")));

    // 请求寻找计划
    HTNComponent->FindHTNPlan(GoalTasks);
}
```

### 进阶用法

自定义 HTN 任务并集成到规划器中。这通常通过继承自 `UHTNTask` 的类实现。
*(来源: 基于模块结构推断)*

```cpp
// MyHTNTask.h
#pragma once
#include "HTNTask.h"
#include "MyHTNTask.generated.h"

UCLASS()
class UMyHTNTask : public UHTNTask
{
    GENERATED_BODY()
public:
    // 重写此方法以定义任务的执行逻辑
    virtual EHTNTaskStatus ExecuteTask(AHTNPlannerComponent& PlannerComp) override;

    // 定义此任务的前提条件 (Preconditions) 和效果 (Effects)
    virtual void GetPreconditions(const FHTNWorldState& WorldState, FHTNPrecondition& OutPreconditions) const override;
    virtual void GetEffects(const FHTNWorldState& WorldState, FHTNWorldState& OutEffects) const override;
};
```

```cpp
// MyHTNTask.cpp
#include "MyHTNTask.h"

EHTNTaskStatus UMyHTNTask::ExecuteTask(AHTNPlannerComponent& PlannerComp)
{
    // 执行具体的游戏逻辑，例如移动、播放动画等
    // ...
    
    // 根据执行结果返回状态
    return EHTNTaskStatus::Succeeded; // 或 Failed, InProgress
}

void UMyHTNTask::GetPreconditions(const FHTNWorldState& WorldState, FHTNPrecondition& OutPreconditions) const
{
    // 定义执行此任务前需要满足的条件
    // 例如：要求世界状态中 “HasWeapon” 为 true
    OutPreconditions.AddRequirement(TEXT("HasWeapon"), true);
}

void UMyHTNTask::GetEffects(const FHTNWorldState& WorldState, FHTNWorldState& OutEffects) const
{
    // 定义此任务执行成功后会改变的世界状态
    // 例如：任务完成后 “EnemyDefeated” 变为 true
    OutEffects.AddFact(TEXT("EnemyDefeated"), true);
}
```

## Demo 示例

由于此插件为底层规划器框架，无独立运行时 Demo。**其功能和使用方式主要体现在 `HTNTestSuite` 模块的单元测试中**，这些测试用例是最直接、可编译的参考示例。测试内容涵盖了从规划器初始化、任务定义、计划生成到执行的完整流程。

## 模块依赖

| 模块 | 用途 |
|---|---|
| `EditorFramework` | 提供编辑器框架支持，HTN 规划器的编辑器集成可能需要。 |
| `UnrealEd` | 提供 Unreal 编辑器核心功能，用于插件的编辑器部分（如可视化调试工具）。 |

**注意**: 要使用 `HTNPlanner` 模块，你的 `Build.cs` 文件需要添加对以上模块的依赖。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 迁移日志宏到新版 UE_LOGF 格式。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了 printf 格式说明符的编译警告。 |
| 2025-12-16 | `7e659465` | Fixed HTNPlanner's Build.cs | 修复了 HTNPlanner 模块的构建配置。 |
| 2025-07-15 | `35e62d59` | Fix/silence V530 unhandled return value warnings | 修复或静默了未处理返回值的编译警告。 |
| 2025-06-10 | `b08804f0` | Replace some usages of FORCEINLINE with inline in AI modules. | 将 AI 模块中部分 FORCEINLINE 用法替换为 inline。 |

### 维护评价

- **创建时间**：2018年，历史悠久。
- **近期更新频率**：最近一年有零星更新（2025年6月，2026年4月），**但全部是编译警告修复、构建修复和日志宏迁移等维护性工作，没有任何新功能或实质性改进**。
- **活跃度**：**维护不活跃**。自创建以来的绝大部分时间（2018-2025）似乎没有实质性更新，最近的更新也表明它处于“维护模式”而非开发模式。
- **已知问题/限制**：插件自身标记为 `[EXPERIMENTAL]` 和 `IsBetaVersion=true`，且 `EnabledByDefault=false`。这意味着它不被视为稳定或生产就绪的功能。
- **推荐使用**：**不推荐用于正式项目**。可作为**学习、研究或高级原型开发**的参考。如果要在生产中使用 HTN 规划，可能需要自行维护或寻找更成熟稳定的第三方实现。

**⚠️ 警告：此插件虽有近期更新，但仅限于基础维护，长期处于实验性状态，无活跃功能开发迹象。**

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/HTNPlanner)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/HTNPlanner/Source/HTNTestSuite)