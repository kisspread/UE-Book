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

HTNPlanner 为 Unreal Engine 的 AI 系统引入了**层次任务网络 (Hierarchical Task Network, HTN)** 规划算法的支持。与传统的状态机或行为树不同，HTN 是一种基于**目标和方法分解**的规划范式。它允许开发者将复杂的 AI 行为（如“攻击敌人”）定义为一系列可分解的复合任务，直到分解为可直接执行的原子动作（如“移动到位置”、“开火”）。规划器会根据当前世界状态、预先定义的任务层次结构和条件约束，自动搜索并生成一个达成目标的最优行动序列。该插件旨在为需要复杂、动态和上下文感知决策逻辑的 AI 角色提供一种强大的底层规划工具。

## 使用场景

- 你在制作一个策略游戏，需要 AI 单位根据战场形势动态制定“侦察”、“占领资源点”、“包抄敌人”等多步骤作战计划。
- 你在开发一个开放世界 RPG，NPC 需要根据自身状态（饥饿、疲惫、对话目标）和环境（时间、地点）动态生成并执行“去餐馆吃饭”、“回家休息”、“与玩家交易”等日常任务链。
- 你需要一个比行为树更灵活、更能处理复杂前置条件和任务间依赖关系的 AI 决策系统。

## 蓝图用法

该插件的核心功能（任务定义、领域构建、规划计算）主要通过 C++ 结构体和类实现，**没有直接暴露为蓝图节点**。其与蓝图系统的集成主要体现在 `UHTNBrainComponent` 这个运行时组件上，它继承自 `UBrainComponent`，可以作为 AI 控制器大脑组件的一部分，将 HTN 规划器集成到更广泛的 AI 框架中。

### 核心节点

由于核心 API 为 C++ 结构体，无直接蓝图节点。相关的 `UHTNBrainComponent` 可被添加到 `AIController` 中，但其具体蓝图调用方式取决于最终封装。

## C++ 用法

HTNPlanner 的 API 围绕着构建“领域”（Domain）和执行“规划”（Planner）展开。

### 头文件引入

```cpp
#include "HTNPlanner/Public/HTNBuilder.h"
#include "HTNPlanner/Public/HTNPlanner.h"
#include "HTNPlanner/Public/HTNDomain.h"
```

### 基本用法：构建领域并生成计划

以下示例展示了如何定义一个简单的 HTN 领域并生成一个计划。

```cpp
// 包含必要头文件
#include "HTNBuilder.h"
#include "HTNPlanner.h"
#include "HTNDomain.h"

void Example_HTNPlanning()
{
    // 1. 创建领域构建器
    FHTNBuilder_Domain DomainBuilder;
    DomainBuilder.SetRootName(TEXT("Root"));

    // 2. 定义一个复合任务 `Root`，它有一个方法
    FHTNBuilder_CompositeTask& RootTask = DomainBuilder.AddCompositeTask(TEXT("Root"));
    FHTNBuilder_Method& RootMethod = RootTask.AddMethod(); // 无条件
    RootMethod.AddTask(TEXT("Patrol"));

    // 3. 定义一个原子任务 `Patrol`，它的动作ID为0（假设对应`移动`）
    FHTNBuilder_PrimitiveTask& PatrolTask = DomainBuilder.AddPrimitiveTask(TEXT("Patrol"));
    PatrolTask.SetOperator(0); // ActionID=0, Parameter=0 (可以指定目标点ID)

    // 4. 编译领域（将构建器数据转换为运行时可规划的格式）
    if (DomainBuilder.Compile())
    {
        // 5. 创建规划器并生成计划
        FHTNPlanner Planner;
        FHTNResult PlanResult;
        FHTNWorldState InitialWorldState; // 根据游戏状态初始化

        bool bSuccess = Planner.GeneratePlan(
            *DomainBuilder.DomainInstance, // 使用编译后的领域实例
            InitialWorldState,
            PlanResult,
            TEXT("Root") // 从根任务开始规划
        );

        if (bSuccess)
        {
            // PlanResult.ActionsSequence 包含了按顺序执行的动作列表
            for (const FHTNExecutableAction& Action : PlanResult.ActionsSequence)
            {
                // 根据 Action.ActionID 和 Action.Parameter 执行具体游戏逻辑
                UE_LOG(LogTemp, Log, TEXT("Plan Action: ID=%d, Param=%d"), Action.ActionID, Action.Parameter);
            }
        }
    }
}
```
*注：此示例简化了世界状态和条件检查，实际应用中需要根据游戏逻辑设置 `FHTNWorldState` 和在方法中添加条件 (`FHTNCondition`)。*

### 进阶用法：自定义条件检查

你可以注册自定义的世界状态检查函数。

```cpp
#include "HTNDomain.h"

// 自定义检查函数：检查两个键的值之和是否大于100
bool MyCustomCheck(const FHTNPolicy::FWSValue* Values, const FHTNCondition& Condition)
{
    FHTNPolicy::FWSValue ValA, ValB;
    // 根据Condition的左右手键从Values数组获取值（伪代码）
    ValA = Values[Condition.KeyLeftHand];
    ValB = Values[Condition.KeyRightHand]; // 假设右手是另一个键
    return (ValA + ValB) > 100;
}

void RegisterCustomCheck()
{
    // 注册自定义检查，获得一个唯一ID
    FHTNPolicy::FWSOperationID MyCheckID = FHTNWorldStateOperations::RegisterCustomCheckType(
        &MyCustomCheck, 
        FName(TEXT("SumGreater100"))
    );

    // 之后在构建领域时，可以使用这个ID创建条件
    FHTNCondition MyCondition;
    MyCondition.Operation = MyCheckID;
    // ... 设置 KeyLeftHand, KeyRightHand ...
}
```

## Demo 示例

以下是一个完整且最小的控制台应用程序示例，演示如何定义和使用 HTN 规划器。

**HTNDemo.h**
```cpp
#pragma once

#include "CoreMinimal.h"
#include "HTNBuilder.h"
#include "HTNPlanner.h"
#include "HTNDomain.h"

class FHTNDemo
{
public:
    static void RunDemo();
};
```

**HTNDemo.cpp**
```cpp
#include "HTNDemo.h"
#include "HAL/PlatformMisc.h"

void FHTNDemo::RunDemo()
{
    // --- 1. 构建领域 ---
    FHTNBuilder_Domain Builder;
    Builder.SetRootName(TEXT("AttackEnemy"));

    // 复合任务：攻击敌人
    FHTNBuilder_CompositeTask& AttackTask = Builder.AddCompositeTask(TEXT("AttackEnemy"));
    FHTNBuilder_Method& AttackMethod = AttackTask.AddMethod();
    AttackMethod.AddTask(TEXT("FindCover"));
    AttackMethod.AddTask(TEXT("ShootEnemy"));

    // 原子任务：寻找掩体 (ActionID=1)
    FHTNBuilder_PrimitiveTask& FindCoverTask = Builder.AddPrimitiveTask(TEXT("FindCover"));
    FindCoverTask.SetOperator(1);

    // 原子任务：射击敌人 (ActionID=2)
    FHTNBuilder_PrimitiveTask& ShootTask = Builder.AddPrimitiveTask(TEXT("ShootEnemy"));
    ShootTask.SetOperator(2);

    // --- 2. 编译领域 ---
    if (!Builder.Compile())
    {
        UE_LOG(LogTemp, Error, TEXT("HTN Domain compilation failed!"));
        return;
    }

    // --- 3. 规划 ---
    FHTNPlanner Planner;
    FHTNResult Result;
    FHTNWorldState InitialState; // 默认初始状态

    if (Planner.GeneratePlan(*Builder.DomainInstance, InitialState, Result, TEXT("AttackEnemy")))
    {
        UE_LOG(LogTemp, Log, TEXT("Generated HTN Plan:"));
        for (const FHTNExecutableAction& Action : Result.ActionsSequence)
        {
            UE_LOG(LogTemp, Log, TEXT("  Action ID: %d, Parameter: %d"), Action.ActionID, Action.Parameter);
        }
    }
    else
    {
        UE_LOG(LogTemp, Log, TEXT("Failed to generate a plan."));
    }
}
```

## 模块依赖

无特殊依赖（仅标准 Core/Engine/Slate 等）。

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏从 UE_LOG 迁移到 UE_LOGF，属于日志系统现代化改造。 |
| 2026-02-04 | `80b637db` | Fixed printf format specifiers. | 修复了打印格式说明符错误，提高了代码健壮性。 |
| 2025-12-16 | `7e659465` | Fixed HTNPlanner's Build.cs | 修复了构建文件，可能是依赖项或路径问题。 |
| 2025-07-15 | `35e62d59` | Fix/silence V530 unhandled return value warnings | 修复或静默了静态分析工具 V530 报告的返回值未处理警告。 |
| 2025-06-10 | `b08804f0` | Replace some usages of FORCEINLINE with inline in AI modules. | 在AI模块中将部分 `FORCEINLINE` 替换为 `inline`，属于代码规范调整。 |

### 维护评价

该插件创建于2018年，已被标记为**实验性 (IsBetaVersion=true)** 且**默认禁用 (EnabledByDefault=false)**。从近期提交历史来看，近几次更新均为编译警告修复、日志格式修正或代码规范调整，**没有实质性功能更新或增强**。这表明该插件可能已被 Epic 官方搁置或置于极低维护优先级，作为实验性特性长期存在。**不建议在生产环境中依赖此插件**，它更适合作为研究 HTN 规划算法在 UE 中实现的参考或实验基础。如果你需要成熟的 AI 解决方案，应优先考虑官方的行为树或探索社区维护的 AI 插件。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/AI/HTNPlanner)
- 官方文档: 无