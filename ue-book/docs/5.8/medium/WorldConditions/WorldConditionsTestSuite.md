# World Conditions

> General purpose cached conditions

| 属性 | 值 |
|---|---|
| 中文名 | 世界条件系统 |
| 分类 | Gameplay |
| 默认启用 | ❌ 否 |
| 包含内容 | ✅ 有（测试资产、编辑器工具） |
| 模块 | `WorldConditions` (Runtime), `WorldConditionsEditor` (Editor), `WorldConditionsTestSuite` (UncookedOnly) |
| 实验性 | ⚠️ 是 |
| 创建时间 | 2022-11-16 |
| 年龄标签 | 🆕（约 3 年） |
| [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WorldConditions) | |

## 用途

本插件提供了一个通用的、可缓存的游戏逻辑条件系统。它的核心目的是优化需要频繁评估一系列复杂条件（例如：AI 的决策、游戏任务的触发、状态机的转换判断）的性能场景。

通过将条件的评估结果进行缓存，并只在相关的上下文数据发生变化时才重新计算，避免了在每帧或每个游戏循环中重复进行不必要的条件判断，从而提升了游戏运行时的效率。它支持将多个基础条件组合成复杂的表达式进行评估。

**为什么存在？** 在复杂的游戏系统中，条件判断无处不在且可能非常消耗资源。本插件通过提供一个结构化、可复用、高性能的条件管理框架，解决了开发者自行实现此类系统时面临的重复编码、性能优化困难和维护成本高的问题。

## 使用场景

- 你正在开发一个复杂的 AI 行为树或感知系统，需要基于多个动态因素（如距离、血量、掩体状态）做出决策 → 用 WorldConditions 构建决策条件。
- 你的游戏有大型的任务或成就系统，完成条件由多个玩家行为和世界状态组合而成 → 用 WorldConditions 定义并缓存这些条件。
- 你需要实现一个状态机，其转换规则依赖于频繁变化的游戏数据（如角色状态、环境状态） → 用 WorldConditions 来高效管理转换条件。

## 蓝图用法

虽然测试代码主要展示了 C++ 实现，但该插件的核心功能是为游戏逻辑系统（如行为树、状态机）提供条件判断支持。以下是其核心的、可暴露给蓝图的功能节点。

### 核心节点

| 节点 | 说明 | 所在类 |
|---|---|---|
| `创建条件查询定义 (Create Query Definition)` | 从一组条件资产或配置创建一个可评估的条件查询定义。 | `UWorldConditionSchema` (推断) |
| `评估条件查询 (Evaluate Query)` | 使用提供的上下文数据，评估一个条件查询并返回结果。 | `UWorldConditionSchema` (推断) |
| `重置缓存 (Invalidate Cache)` | 手动使指定条件查询的缓存结果失效，促使其在下次评估时重新计算。 | `UWorldConditionSchema` (推断) |

*注：以上函数名为根据源码逻辑推断的蓝图友好名称，具体暴露名称以实际插件为准。*

### 使用示例（蓝图描述）

1.  **定义上下文数据**：首先，需要创建一个自定义的 `UWorldConditionSchema` 子类（在 C++ 中完成），它定义了条件评估所需的数据上下文（例如，一个 `AActor` 引用和一个表示“值”的结构体）。
2.  **创建条件查询**：在蓝图中（例如在游戏模式或任务管理器），根据你的 Schema 创建一个 `FWorldConditionQueryDefinition`。
3.  **评估条件**：当需要做出决策时，调用“评估条件查询”节点，传入当前的上下文数据（如当前的 Actor 和最新的“值”）。节点会返回一个结果（True/False）。
4.  **缓存与失效**：对于配置为可缓存的条件，首次评估后结果会被缓存。当上下文数据发生变化时（例如，“值”被修改），系统可以自动或手动（通过“重置缓存”节点）使缓存失效，确保下次评估时能获取最新结果。

## C++ 用法

### 头文件引入

```cpp
#include "WorldConditions/WorldConditionSchema.h"
#include "WorldConditions/WorldConditionQuery.h"
```

### 基本用法

定义你的条件 Schema 和具体条件结构体。这是构建任何条件系统的基础。

```cpp
// 来源: Source/WorldConditionsTestSuite/WorldConditionsTestSuite/Public/WorldConditionTestTypes.h
// 定义上下文数据结构体
USTRUCT()
struct FMyContextData
{
    GENERATED_BODY()
    int32 Health = 100;
    bool bHasAmmo = true;
};

// 定义你的条件 Schema，描述上下文中有哪些数据
UCLASS()
class UMyWorldConditionSchema : public UWorldConditionSchema
{
    GENERATED_BODY()
public:
    explicit UMyWorldConditionSchema(const FObjectInitializer& ObjectInitializer)
        : Super(ObjectInitializer)
    {
        // 添加一个持久的 Actor 引用和一个动态的上下文数据结构体
        ActorRef = AddContextDataDesc(TEXT("Actor"), AActor::StaticClass(), EWorldConditionContextDataType::Persistent);
        MyDataRef = AddContextDataDesc(TEXT("MyData"), FMyContextData::StaticStruct(), EWorldConditionContextDataType::Dynamic);
    }

    // 允许哪些结构体作为条件使用
    virtual bool IsStructAllowed(const UScriptStruct* InScriptStruct) const override
    {
        return InScriptStruct && InScriptStruct->IsChildOf(FMyBaseCondition::StaticStruct());
    }

    FWorldConditionContextDataRef GetActorRef() const { return ActorRef; }
    FWorldConditionContextDataRef GetMyDataRef() const { return MyDataRef; }

private:
    FWorldConditionContextDataRef ActorRef;
    FWorldConditionContextDataRef MyDataRef;
};

// 定义一个具体的条件结构体
USTRUCT()
struct FHealthAboveCondition : public FWorldConditionBase
{
    GENERATED_BODY()

    UPROPERTY(EditAnywhere, Category="Condition")
    int32 HealthThreshold = 50;

    // ... 实现 Initialize, Activate, IsTrue, Deactivate, GetDescription 等虚函数
    // IsTrue 函数会从 Context 中获取 FMyContextData，比较其 Health 是否大于 HealthThreshold。
};
```

### 进阶用法：支持缓存与失效

创建一个可以监听数据变化、自动使缓存失效的条件。

```cpp
// 来源: Source/WorldConditionsTestSuite/WorldConditionsTestSuite/Public/WorldConditionTestTypes.h
// 定义运行时状态结构体，用于持有委托句柄等
USTRUCT()
struct FMyConditionState
{
    GENERATED_BODY()
    FDelegateHandle ValueChangedHandle;
};

USTRUCT()
struct FAutoInvalidateCondition : public FWorldConditionBase
{
    GENERATED_BODY()

    // 告诉系统这个条件需要运行时状态
    virtual TObjectPtr<const UStruct>* GetRuntimeStateType() const override
    {
        static TObjectPtr<const UStruct> Ptr{FMyConditionState::StaticStruct()};
        return &Ptr;
    }

    // 在激活时，绑定数据变化的委托
    virtual bool Activate(const FWorldConditionContext& Context) const override
    {
        // 获取状态对象
        FMyConditionState& State = Context.GetState(*this);
        // 获取可修改的上下文数据（例如，数据拥有者）
        if (FMyContextData* MyData = Context.GetMutableContextDataPtr<FMyContextData>(DataRef))
        {
            // 假设 FMyContextData 有一个 OnValueChanged 委托
            State.ValueChangedHandle = MyData->OnValueChanged.AddLambda(
                [InvalidationHandle = Context.GetInvalidationHandle(*this)]()
                {
                    // 当数据变化时，使此条件的缓存结果失效
                    InvalidationHandle.InvalidateResult();
                });
            return true;
        }
        return false;
    }

    // 在停用时，解绑委托
    virtual void Deactivate(const FWorldConditionContext& Context) const override
    {
        FMyConditionState& State = Context.GetState(*this);
        if (State.ValueChangedHandle.IsValid())
        {
            if (FMyContextData* MyData = Context.GetMutableContextDataPtr<FMyContextData>(DataRef))
            {
                MyData->OnValueChanged.Remove(State.ValueChangedHandle);
                State.ValueChangedHandle.Reset();
            }
        }
    }
    // ... IsTrue 等其他函数实现
private:
    FWorldConditionContextDataRef DataRef;
};
```

## Demo 示例

一个最小化的、可在 C++ 中使用 WorldConditions 的示例。

```cpp
// MyConditionEvaluator.h
#pragma once
#include "CoreMinimal.h"
#include "WorldConditions/WorldConditionQuery.h"
#include "MyConditionEvaluator.generated.h"

UCLASS(BlueprintType)
class UMyConditionEvaluator : public UObject
{
    GENERATED_BODY()
public:
    // 评估一个预定义的条件查询
    UFUNCTION(BlueprintCallable, Category="Conditions")
    bool EvaluateConditions(AActor* ContextActor, const FMyContextData& CurrentData);

private:
    // 存储条件查询定义
    UPROPERTY()
    FWorldConditionQueryDefinition ConditionQueryDefinition;
};

// MyConditionEvaluator.cpp
#include "MyConditionEvaluator.h"
#include "MyWorldConditionSchema.h" // 包含之前定义的 Schema 和 Condition

bool UMyConditionEvaluator::EvaluateConditions(AActor* ContextActor, const FMyContextData& CurrentData)
{
    // 1. 获取 Schema
    const UMyWorldConditionSchema* Schema = UMyWorldConditionSchema::Get();
    if (!Schema) return false;

    // 2. 创建评估上下文
    FWorldConditionContext Context(Schema, ContextActor);

    // 3. 设置上下文中的数据
    Context.SetContextData(Schema->GetMyDataRef(), &CurrentData);

    // 4. 评估查询
    FWorldConditionQueryState QueryState;
    if (!ConditionQueryDefinition.Initialize(Schema, QueryState))
    {
        return false;
    }
    FWorldConditionResult Result = ConditionQueryDefinition.Evaluate(Context, QueryState);

    // 5. 检查结果
    return Result.Value == EWorldConditionResultValue::IsTrue;
}
```

## 模块依赖

| 模块 | 用途 |
|---|---|
| `PropertyBindingUtils` | 用于支持属性绑定，这是构建条件查询表达式的基础。 |
| `EditorFramework` | 测试套件模块依赖，用于编辑器功能。 |
| `UnrealEd` | 测试套件模块依赖，用于编辑器功能。 |

## 维护状态

### 近期更新

| 日期 | Hash | 原文 | 中文解读 |
|---|---|---|---|
| 2026-04-28 | `cfaec1a0` | [WorldConditions] Build SharedDefinition before serialize so name harvest matches write | 优化序列化流程，确保共享定义的名称收集与写入一致。 |
| 2026-04-23 | `f49c6ff0` | [WorldConditions][Stability] Do not dereference Owner during GC in FWorldConditionQueryState destruc | 修复GC期间状态析构器的指针解引用问题，提升稳定性。 |
| 2026-04-14 | `35e60df1` | Migrate UE_LOG to UE_LOGF. | 将日志宏迁移到新格式，这是引擎范围内的代码现代化。 |
| 2026-03-24 | `2da4cdac` | [AI][WorldConditions] Add WorldConditionsToolset plugin for MCP inspection | 新增配套的工具集插件，用于AI行为树等上下文中的条件检查与调试。 |
| 2026-03-10 | `ba65d06d` | [WorldCondition] fixed case where world condition queries would not be properly linked when embedded | 修复条件查询在嵌入使用时链接不正确的问题。 |

### 维护评价

该插件处于**活跃维护**状态。创建时间虽不长，但自2026年3月以来更新非常频繁，内容涉及功能增强、稳定性修复和工具链完善。特别是最新添加的 `WorldConditionsToolset` 插件表明其在AI和游戏逻辑系统中的重要性正在提升。尽管仍标记为“实验性”，但从其持续的功能迭代和bug修复来看，已具备相当的成熟度和可靠性。**推荐**在项目中作为高性能条件系统的核心方案进行评估和使用。

## 相关链接

- [源码](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WorldConditions)
- [官方文档]() (暂无)
- [测试用例](https://github.com/EpicGames/UnrealEngine/tree/5.8/Engine/Plugins/Runtime/WorldConditions/Source/WorldConditionsTestSuite)