# StateTree

> General purpose hierarchical state machine

| 属性 | 值 |
|---|---|
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（状态树资产、Schema 资产） |
| 模块 | `StateTreeModule` (Runtime), `StateTreeDeveloper` (Runtime), `StateTreeEditorModule` (Runtime), `StateTreeTestSuite` (Runtime) |
| 实验性 | 否 |
| 创建时间 | 2021-09-28 |
| 年龄标签 | 🆕（约 4 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree) | |

## 用途

StateTree 是 UE5 的通用分层状态机框架，用于替代和补充传统的行为树（Behavior Tree）和有限状态机（FSM）。它解决的核心问题是：**在游戏逻辑中以可视化、数据驱动的方式组织复杂的状态转换和行为逻辑**。

与行为树不同，StateTree 采用分层状态结构，每个状态可以包含：
- **Tasks**（任务）：状态激活时执行的具体逻辑
- **Conditions**（条件）：控制状态转换的判断逻辑
- **Evaluators**（评估器）：每帧计算并暴露数据供决策使用
- **Considerations**（效用考量）：用于 Utility AI 风格的评分决策
- **Property Functions**（属性函数）：在绑定求值前执行的计算逻辑

StateTree 的设计哲学是模块化和可组合性——通过 Schema 机制限制可用的节点类型，使得同一个框架可以用于 AI 行为、游戏流程控制、动画状态机等多种场景。它还支持事件驱动的委托系统、并行状态树执行、以及基于 Unreal Insights 的运行时调试。

## 使用场景

- 你需要一个比行为树更灵活的 AI 决策系统，支持条件转换和效用评分 → 用 StateTree
- 你需要控制游戏流程（如关卡阶段、UI 状态、对话系统）→ 用 StateTree 配合自定义 Schema
- 你需要多个状态树并行运行（如主 AI 行为 + 副作用行为）→ 用 `FStateTreeRunParallelStateTreeTask`
- 你需要通过蓝图快速原型化状态逻辑 → 用 Blueprint 基类（`UStateTreeTaskBlueprintBase` 等）
- 你需要运行时调试状态转换和执行流程 → 用 StateTree Trace Debugger
- 你需要将参数化的状态树资产复用在不同实体上 → 用 `FStateTreeReference` 配合参数覆盖

## 蓝图用法

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `Set State Tree` | 设置 FStateTreeReference 引用的状态树资产 | `UStateTreeFunctionLibrary` |
| `Make State Tree Reference` | 从 UStateTree 创建 FStateTreeReference | `UStateTreeFunctionLibrary` |
| `Set Parameter Property` | 设置状态树引用的参数属性值 | `UStateTreeFunctionLibrary` |
| `Get Parameter Property` | 获取状态树引用的参数属性值 | `UStateTreeFunctionLibrary` |
| `Send Event` | 向当前状态树发送事件 | `UStateTreeNodeBlueprintBase` |
| `Request Transition` | 请求状态转换到指定目标状态 | `UStateTreeNodeBlueprintBase` |
| `Get Property Reference` | 获取状态树中属性的引用 | `UStateTreeNodeBlueprintBase` |
| `Is Property Ref Valid` | 检查属性引用是否有效 | `UStateTreeNodeBlueprintBase` |

### Blueprint 节点基类

StateTree 提供了完整的蓝图扩展体系，允许在蓝图中创建自定义节点：

| 基类 | 用途 | 可重写事件 |
|---|---|---|
| `UStateTreeTaskBlueprintBase` | 自定义蓝图任务 | `ReceiveEnterState`, `ReceiveTick`, `ReceiveExitState` |
| `UStateTreeConditionBlueprintBase` | 自定义蓝图条件 | `ReceiveTestCondition` |
| `UStateTreeEvaluatorBlueprintBase` | 自定义蓝图评估器 | `ReceiveTreeStart`, `ReceiveTreeStop`, `ReceiveTick` |
| `UStateTreeConsiderationBlueprintBase` | 自定义蓝图效用考量 | `ReceiveGetScore` |

### 使用示例（蓝图描述）

**创建参数化状态树引用：**
1. 使用 `Make State Tree Reference` 节点，输入一个 `UStateTree` 资产
2. 输出的 `FStateTreeReference` 可以存储在变量中
3. 使用 `Set Parameter Property` 修改参数值（需要 PropertyID）
4. 将引用传递给 StateTreeComponent 或其他消费端

**在蓝图任务中发送事件：**
1. 创建一个继承自 `UStateTreeTaskBlueprintBase` 的蓝图类
2. 在 `ReceiveTick` 事件中调用 `Send Event` 节点
3. 传入 `FStateTreeEvent`（包含 Tag 和可选 Payload）
4. 事件会沿状态层级向上传播，触发匹配的转换

**请求状态转换：**
1. 在蓝图任务的任意回调中调用 `Request Transition`
2. 指定目标状态的 `FStateTreeStateLink`
3. 可选设置转换优先级（`EStateTreeTransitionPriority`）

## C++ 用法

### 头文件引入

```cpp
#include "StateTreeModule.h"
#include "StateTreeExecutionContext.h"
#include "StateTreeTaskBase.h"
#include "StateTreeConditionBase.h"
#include "StateTreeEvaluatorBase.h"
#include "StateTreeReference.h"
#include "StateTreeEvents.h"
```

### 基本用法：创建自定义 Task

```cpp
// 来源: StateTreeTaskBase.h - FStateTreeTaskBase 接口定义

USTRUCT()
struct FMyTaskInstanceData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Input")
    float Speed = 100.0f;

    UPROPERTY(EditAnywhere, Category = "Output")
    FVector TargetLocation = FVector::ZeroVector;
};

USTRUCT(meta = (DisplayName = "My Custom Task", Category = "Custom"))
struct FMyTask : public FStateTreeTaskCommonBase
{
    GENERATED_BODY()

    using FInstanceDataType = FMyTaskInstanceData;

    virtual const UStruct* GetInstanceDataType() const override
    {
        return FInstanceDataType::StaticStruct();
    }

    virtual EStateTreeRunStatus EnterState(
        FStateTreeExecutionContext& Context,
        const FStateTreeTransitionResult& Transition) const override
    {
        // 状态进入时的初始化逻辑
        FInstanceDataType& InstanceData = Context.GetInstanceData(*this);
        // ... 初始化逻辑
        return EStateTreeRunStatus::Running;
    }

    virtual EStateTreeRunStatus Tick(
        FStateTreeExecutionContext& Context,
        const float DeltaTime) const override
    {
        FInstanceDataType& InstanceData = Context.GetInstanceData(*this);
        // ... 每帧逻辑
        return EStateTreeRunStatus::Running;
    }

    virtual void ExitState(
        FStateTreeExecutionContext& Context,
        const FStateTreeTransitionResult& Transition) const override
    {
        // 状态退出时的清理逻辑
    }
};
```

### 基本用法：创建自定义 Condition

```cpp
// 来源: StateTreeConditionBase.h - FStateTreeConditionBase 接口定义
// 来源: Conditions/StateTreeObjectConditions.h - 内置条件示例

USTRUCT()
struct FMyConditionInstanceData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Input")
    float Value = 0.0f;

    UPROPERTY(EditAnywhere, Category = "Parameter")
    float Threshold = 50.0f;
};

USTRUCT(DisplayName = "Value Exceeds Threshold", Category = "Custom")
struct FMyCondition : public FStateTreeConditionCommonBase
{
    GENERATED_BODY()

    using FInstanceDataType = FMyConditionInstanceData;

    virtual const UStruct* GetInstanceDataType() const override
    {
        return FInstanceDataType::StaticStruct();
    }

    virtual bool TestCondition(FStateTreeExecutionContext& Context) const override
    {
        const FInstanceDataType& InstanceData = Context.GetInstanceData(*this);
        bool bResult = InstanceData.Value > InstanceData.Threshold;
        return bInvert ? !bResult : bResult;
    }

    UPROPERTY(EditAnywhere, Category = "Condition")
    bool bInvert = false;
};
```

### 基本用法：创建自定义 Evaluator

```cpp
// 来源: StateTreeEvaluatorBase.h - FStateTreeEvaluatorBase 接口定义

USTRUCT()
struct FMyEvaluatorInstanceData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Output")
    float DistanceToTarget = 0.0f;
};

USTRUCT(meta = (DisplayName = "Distance Evaluator", Category = "Custom"))
struct FMyEvaluator : public FStateTreeEvaluatorCommonBase
{
    GENERATED_BODY()

    using FInstanceDataType = FMyEvaluatorInstanceData;

    virtual const UStruct* GetInstanceDataType() const override
    {
        return FInstanceDataType::StaticStruct();
    }

    virtual void TreeStart(FStateTreeExecutionContext& Context) const override
    {
        // 状态树启动时初始化
    }

    virtual void Tick(FStateTreeExecutionContext& Context, const float DeltaTime) const override
    {
        FInstanceDataType& InstanceData = Context.GetInstanceData(*this);
        // 每帧计算距离等数据
        InstanceData.DistanceToTarget = /* 计算逻辑 */;
    }

    virtual void TreeStop(FStateTreeExecutionContext& Context) const override
    {
        // 状态树停止时清理
    }
};
```

### 进阶用法：使用事件和委托系统

```cpp
// 来源: StateTreeEvents.h - FStateTreeEvent 定义
// 来源: StateTreeDelegate.h - FStateTreeDelegateDispatcher/Listener 定义

// 发送事件（在 Task 中）
void FMyAsyncTask::OnAsyncCallback(FStateTreeExecutionContext& Context) const
{
    // 创建带 Payload 的事件
    FStateTreeEvent Event;
    Event.Tag = FGameplayTag::RequestGameplayTag(TEXT("Event.TaskCompleted"));
    Event.Payload = FConstStructView::Make(MyPayloadStruct);
    Event.Origin = FName("MyAsyncTask");

    // 通过 Context 发送事件
    Context.SendEvent(Event);
}

// 使用委托系统（在 Task 中注册回调）
void FMyAsyncTask::EnterState(FStateTreeExecutionContext& Context, const FStateTreeTransitionResult& Transition) const
{
    FInstanceDataType& InstanceData = Context.GetInstanceData(*this);

    // 绑定委托监听器到回调
    Context.BindDelegate(InstanceData.OnCompletedListener, [this, &Context]()
    {
        // 异步操作完成时的回调
        Context.SendEvent(FStateTreeEvent(CompletedEventTag));
    });
}
```

### 进阶用法：使用 FStateTreeReference 参数化

```cpp
// 来源: StateTreeReference.h - FStateTreeReference 定义
// 来源: StateTreeFunctionLibrary.h - 蓝图函数库

// C++ 中设置状态树引用
FStateTreeReference MyRef;
MyRef.SetStateTree(MyStateTreeAsset);

// 获取和修改参数
FInstancedPropertyBag& Params = MyRef.GetMutableParameters();
// 通过 PropertyID 设置参数值
MyRef.SetPropertyOverridden(PropertyID, true);

// 检查是否需要同步参数
if (MyRef.RequiresParametersSync())
{
    MyRef.SyncParameters();
}
```

### 进阶用法：并行状态树

```cpp
// 来源: Tasks/StateTreeRunParallelStateTreeTask.h

// FStateTreeRunParallelStateTreeTask 允许在当前状态中并行运行另一个状态树
// 使用方式：在 StateTree 编辑器中添加 "Run Parallel Tree" 任务节点
// 配置 StateTreeReference 指向要并行运行的状态树
// 可通过 StateTreeOverrideTag 在运行时动态替换并行树
// EventHandlingPriority 控制事件处理优先级（Low/Normal/High）
```

## Demo 示例

### 自定义 Task：带计时器的巡逻任务

```cpp
// PatrolTask.h
#pragma once

#include "StateTreeTaskBase.h"
#include "PatrolTask.generated.h"

USTRUCT()
struct FPatrolTaskInstanceData
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category = "Input")
    float PatrolRadius = 500.0f;

    UPROPERTY(EditAnywhere, Category = "Input")
    float WaitTime = 3.0f;

    UPROPERTY()
    FVector CurrentTarget = FVector::ZeroVector;

    UPROPERTY()
    float ElapsedWaitTime = 0.0f;

    UPROPERTY()
    bool bIsWaiting = false;
};

USTRUCT(meta = (DisplayName = "Patrol", Category = "AI"))
struct FPatrolTask : public FStateTreeTaskCommonBase
{
    GENERATED_BODY()

    using FInstanceDataType = FPatrolTaskInstanceData;

    virtual const UStruct* GetInstanceDataType() const override
    {
        return FInstanceDataType::StaticStruct();
    }

    virtual EStateTreeRunStatus EnterState(
        FStateTreeExecutionContext& Context,
        const FStateTreeTransitionResult& Transition) const override
    {
        FInstanceDataType& Data = Context.GetInstanceData(*this);
        Data.ElapsedWaitTime = 0.0f;
        Data.bIsWaiting = false;
        // 生成随机巡逻点
        Data.CurrentTarget = FVector(
            FMath::RandRange(-Data.PatrolRadius, Data.PatrolRadius),
            FMath::RandRange(-Data.PatrolRadius, Data.PatrolRadius),
            0.0f);
        return EStateTreeRunStatus::Running;
    }

    virtual EStateTreeRunStatus Tick(
        FStateTreeExecutionContext& Context,
        const float DeltaTime) const override
    {
        FInstanceDataType& Data = Context.GetInstanceData(*this);

        if (Data.bIsWaiting)
        {
            Data.ElapsedWaitTime += DeltaTime;
            if (Data.ElapsedWaitTime >= Data.WaitTime)
            {
                // 等待结束，生成新目标点
                Data.ElapsedWaitTime = 0.0f;
                Data.bIsWaiting = false;
                Data.CurrentTarget = FVector(
                    FMath::RandRange(-Data.PatrolRadius, Data.PatrolRadius),
                    FMath::RandRange(-Data.PatrolRadius, Data.PatrolRadius),
                    0.0f);
            }
        }
        else
        {
            // 移动到目标点（简化逻辑）
            // 到达目标后切换到等待状态
            Data.bIsWaiting = true;
        }

        return EStateTreeRunStatus::Running;
    }

    virtual void ExitState(
        FStateTreeExecutionContext& Context,
        const FStateTreeTransitionResult& Transition) const override
    {
        // 清理逻辑
    }
};
```

## 模块依赖

从 Build.cs 分析，StateTree 的独特依赖如下：

| 模块 | 用途 |
|---|---|
| `GameplayTags` | 事件标签系统、条件中的标签匹配 |
| `GameplayAbilities` | 与 GAS 系统集成 |
| `StructUtils` | InstancedStruct、PropertyBag 等结构化数据工具 |
| `PropertyBindingTypes` | 属性绑定索引类型 |
| `TraceServices` | Unreal Insights 调试追踪分析 |
| `AITypes` | AI 相关类型定义（如 EGenericAICheck） |

## 维护状态

### 近期更新

```
- d792746f1734 [StateTree] Set the alignment when there are only object wrapper nodes. #jira PLAY-94932
- 291028cf6b91 [StateTree] allow state selection to continue when reaching the source state of the transition if it is completed (requires SelectionRules to use CompletedTransitionStatesCreateNewStates) #jira UE-333382
- 44d2e9a4dabe [State Tree][Property Binding] Introduced output binding feature. Target property reversely bound to source property will write back to the source property instead of copying from the source property, at the end of each node processing scope.
```

### 维护评价

**活跃维护** — StateTree 是 Epic Games 重点投入的下一代状态机框架，处于持续积极开发中。

- **创建时间**：2021 年 9 月，约 4 年历史，正处于功能快速迭代期
- **更新频率**：近期 commit 显示持续的功能增强（输出绑定、状态选择规则改进、内存对齐修复）
- **版本状态**：Version 0.1，尚未标记为正式版，API 仍在演进中
- **实验性标记**：虽然 `IsBetaVersion=false`，但 `EnabledByDefault=false` 说明需要手动启用，且部分功能（如 Considerations/Utility AI）在代码中标记为 experimental
- **已知限制**：
  - 需要手动在插件设置中启用
  - 部分 API（如 `FStateTreeStrongTaskRef`/`FStateTreeWeakTaskRef`）已在 5.6 中废弃
  - Utility Considerations 功能仍为实验性
- **推荐程度**：**强烈推荐**用于新项目。StateTree 是 Epic 官方力推的 AI/游戏逻辑框架，正在逐步替代行为树在复杂场景中的使用。建议关注版本更新中的 API 变更。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree)
- [官方文档](https://dev.epicgames.com/documentation/en-us/unreal-engine/state-tree-in-unreal-engine)（社区维护）
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.7/Engine/Plugins/Runtime/StateTree/Source/StateTreeTestSuite)